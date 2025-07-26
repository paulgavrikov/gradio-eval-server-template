import datetime
import time
from collections import defaultdict
import threading
import json
import os

PERSISTENT_FILE = ".rate_limiter.json"


def _json_dumper(obj):
    try:
        return obj.to_dict()
    except:
        return obj


class RateLimitConfig:
    def __init__(self, max_per_day=None, max_total=None, min_interval_seconds=None):
        self.max_per_day = max_per_day
        self.max_total = max_total
        self.min_interval_seconds = min_interval_seconds


class RateLimitState:
    def __init__(self):
        self.daily_count = 0
        self.total_count = 0
        self.last_access_time = None
        self.last_access_date = datetime.date.today()

    def to_dict(self):
        return {
            "daily_count": self.daily_count,
            "total_count": self.total_count,
            "last_access_time": self.last_access_time,
            "last_access_date": str(self.last_access_date),
        }

    def from_dict(data):
        state = RateLimitState()
        state.daily_count = data.get("daily_count", 0)
        state.total_count = data.get("total_count", 0)
        state.last_access_time = data.get("last_access_time")
        state.last_access_date = datetime.datetime.strptime(
            data.get("last_access_date"), "%Y-%m-%d"
        ).date()
        return state


class RateLimiter:
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.user_log = defaultdict(RateLimitState)
        self.load_state()
        self.lock = threading.Lock()

    def _today(self):
        return datetime.date.today()

    def _reset_daily_count_if_needed(self, state: RateLimitState):
        today = self._today()
        if state.last_access_date != today:
            state.daily_count = 0
            state.last_access_date = today

    def is_allowed(self, user_id: str) -> bool:
        now = time.time()
        with self.lock:
            state = self.user_log[user_id]
            self._reset_daily_count_if_needed(state)

            # Check min time between accesses
            if self.config.min_interval_seconds and state.last_access_time is not None:
                if now - state.last_access_time < self.config.min_interval_seconds:
                    return False, "min_interval_seconds"

            # Check daily limit
            if self.config.max_per_day and state.daily_count >= self.config.max_per_day:
                return False, "max_per_day"

            # Check total limit
            if self.config.max_total and state.total_count >= self.config.max_total:
                return False, "max_total"

            # All checks passed, update counters
            state.last_access_time = now
            state.daily_count += 1
            state.total_count += 1

            self.save_state()

            return True, "allowed"

    def load_state(self):
        self.user_log.clear()
        if os.path.exists(PERSISTENT_FILE):
            with open(PERSISTENT_FILE, "r") as f:
                try:
                    self.user_log = json.load(f)
                    for user_id, state_data in self.user_log.items():
                        self.user_log[user_id] = RateLimitState.from_dict(state_data)
                except json.JSONDecodeError:
                    print("Error loading rate limiter state from file. Starting fresh.")

    def save_state(self):
        with open(PERSISTENT_FILE, "w") as f:
            json.dump(self.user_log, f, default=_json_dumper)

    def get_status(self, user_id: str) -> dict:
        now = time.time()
        with self.lock:
            if user_id not in self.user_log:
                return {
                    "daily_used": 0,
                    "daily_remaining": self.config.max_per_day,
                    "total_used": 0,
                    "total_remaining": self.config.max_total,
                    "wait_seconds": 0,
                }
            state = self.user_log[user_id]
            self._reset_daily_count_if_needed(state)

            remaining_daily = (
                None
                if self.config.max_per_day is None
                else max(0, self.config.max_per_day - state.daily_count)
            )
            remaining_total = (
                None
                if self.config.max_total is None
                else max(0, self.config.max_total - state.total_count)
            )
            wait_time = (
                0
                if self.config.min_interval_seconds is None
                or state.last_access_time is None
                else max(
                    0, self.config.min_interval_seconds - (now - state.last_access_time)
                )
            )

            return {
                "daily_used": state.daily_count,
                "daily_remaining": remaining_daily,
                "total_used": state.total_count,
                "total_remaining": remaining_total,
                "wait_seconds": round(wait_time, 2),
            }
