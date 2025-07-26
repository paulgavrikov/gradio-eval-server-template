import gradio as gr
import json, os, time, uuid
from eval_utils import evaluate_submission, clean_submission
import pandas as pd
from rate_limiter import RateLimiter, RateLimitConfig
from config import *


def login_check(profile: gr.OAuthProfile | None):
    visible = profile is not None
    welcome = (
        f"## 👋 Welcome, {profile.username}! Ready to submit?"
        if visible
        else "🔒 Please sign in to submit."
    )

    quota_details = quoata_check(profile)

    return (
        welcome,
        gr.Markdown(visible=visible),
        gr.Markdown(value=quota_details, visible=visible),
        gr.Textbox(visible=visible & SAVE_SUBMISSIONS),
        gr.File(visible=visible),
        gr.Checkbox(visible=visible),
        gr.Checkbox(visible=visible & SAVE_SUBMISSIONS),
        gr.Button(visible=visible),
    )


def quoata_check(profile: gr.OAuthProfile | None):
    quota_details = None
    if profile and (
        MAX_SUBMISSIONS_PER_USER_PER_DAY > 0 or MAX_TOTAL_SUBMISSIONS_PER_USER > 0
    ):
        quota = limiter.get_status(profile.username)
        quota_details = (
            f"### Remaining quota  \n"
            + (
                f"**Daily Used:** {quota['daily_used']} / {MAX_SUBMISSIONS_PER_USER_PER_DAY}  \n"
                if MAX_SUBMISSIONS_PER_USER_PER_DAY
                else ""
            )
            + (
                f"**Total Used:** {quota['total_used']} / {MAX_TOTAL_SUBMISSIONS_PER_USER}  \n"
                if MAX_TOTAL_SUBMISSIONS_PER_USER
                else ""
            )
        )
    return quota_details


def submit(
    submission_id: str,
    submission_file: str,
    is_cleaning: bool,
    is_private: bool,
    profile: gr.OAuthProfile | None,
):
    if not profile:
        raise gr.Error("🔒 Please sign in first.")

    if not submission_file:
        raise gr.Error("❌ Please upload a submission file.")

    username = profile.username
    now = time.time()

    with open(submission_file, "rb") as file:
        try:
            prediction_json = json.load(file)
        except json.JSONDecodeError:
            raise gr.Error("❌ Submission file is invalid JSON.")

    with open(GROUND_TRUTH, "rb") as file:
        ground_truth_json = json.load(file)

    try:
        if is_cleaning:
            prediction_json = clean_submission(prediction_json)
        score_dict = evaluate_submission(prediction_json, ground_truth_json)
    except Exception as e:
        print(e)
        raise gr.Error(f"❌ Invalid submission format.")

    allowed, allowed_reason = limiter.is_allowed(username)
    status = limiter.get_status(username)

    if not allowed:
        if allowed_reason == "min_interval_seconds":
            raise gr.Error(
                f"❌ You must wait at least {RATE_LIMIT_MIN_INT_SEC} seconds between submissions."
            )
        elif allowed_reason == "max_per_day":
            raise gr.Error(
                f"❌ You have reached your daily submission limit of {MAX_SUBMISSIONS_PER_USER_PER_DAY}."
            )
        elif allowed_reason == "max_total":
            raise gr.Error(
                f"❌ You have reached your total submission limit of {MAX_TOTAL_SUBMISSIONS_PER_USER}."
            )

    if not is_private and SAVE_SUBMISSIONS:
        sid = str(uuid.uuid4())
        submission_record = f"{sid}"

        # TODO: it is probably a good idea to sanitize the prediction_json here, e.g. remove any user-provided fields to avoid memory attacks.

        data = {
            "username": username,
            "identifier": submission_id,
            "timestamp": now,
            "scores": score_dict,
        }
        if SAVE_SUBMISSION_PREDICTIONS:
            data["predictions"] = prediction_json

        json.dump(data, open(os.path.join(SUB_DIR, submission_record + ".json"), "w"))

    score_response = f"{score_dict}"

    return gr.Text(score_response, visible=True)


def get_leaderboard() -> pd.DataFrame | str:

    # TODO: Implement your leaderboard logic here, there are many ways to do this.
    # If you want to show a hardcoded leaderboard, you can return a DataFrame directly.
    # return pd.DataFrame(columns=["Rank", "ID", "Score", "Reported by"], data=[1, "test", 100, "test_user"])
    # Or you can read from the SUB_DIR and return a DataFrame with the top submissions. Note, that this may allows users to inject arbitrary data.
    records = []
    for fn in os.listdir(SUB_DIR):
        r = json.load(open(os.path.join(SUB_DIR, fn)))
        records.append(
            {
                "ID": r[
                    "identifier"
                ],  # This field is user-provided, so be careful with how you display it.
                **r["scores"],
                # "Reported by": r["username"],
                # "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r["timestamp"]))
            }
        )
    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)

    # TODO: Define your sorting logic here
    df = df.sort_values(by="accuracy/partition1", ascending=False)

    df["#"] = range(1, len(df) + 1)  # Add a rank column based on the sorted order
    df = df[
        [df.columns[-1]] + df.columns[:-1].tolist()
    ]  # Move the Rank column to the front
    return df


def get_quota(profile: gr.OAuthProfile | None = None):
    return limiter.get_status(profile.username)


with gr.Blocks() as app:

    with gr.Tab("🏆 Public Leaderboard"):
        leaderboard_heading_md = gr.Markdown(
            "TODO: Introduction to the benchmark and leaderboard"
        )
        leaderboard_table = gr.Dataframe(get_leaderboard())
        leaderboard_footer_md = gr.Markdown(
            "TODO: Add instructions for the leaderboard, e.g. how to submit, evaluation criteria, etc."
        )

    with gr.Tab("🚀 Evaluation"):
        login_button = gr.LoginButton()
        welcome_md = gr.Markdown("🔒 Please sign in to submit.")
        welcome_details_md = gr.Markdown(
            "TODO: add instructions for submission format and evaluation criteria.",
            visible=False,
        )
        submission_file = gr.File(
            label="Prediction (.json)", visible=False, file_types=[".json"]
        )
        submission_id = gr.Textbox(
            label="(Optional) Submission identifier", visible=False
        )
        clean_flag = gr.Checkbox(
            label="Attempt to clean my submission (Recommended for raw responses)",
            value=True,
            visible=False,
        )
        private_flag = gr.Checkbox(
            label="Do not save my submission", value=False, visible=False
        )
        quota_details = gr.Markdown(visible=False)
        submit_btn = gr.Button("Submit", visible=False)
        result = gr.Textbox(label="✅ Submission processed", visible=False)

    copyright = gr.Markdown(
        "Based on the [gradio-eval-server-template](https://github.com/paulgavrikov/gradio-eval-server-template) by Paul Gavrikov."
    )

    # Load login state → show/hide components
    app.load(
        fn=login_check,
        inputs=[],
        outputs=[
            welcome_md,
            welcome_details_md,
            quota_details,
            submission_id,
            submission_file,
            clean_flag,
            private_flag,
            submit_btn,
        ],
    )

    # Submit button only shown post-login
    submit_btn.click(
        fn=submit,
        inputs=[submission_id, submission_file, clean_flag, private_flag],
        outputs=[result],
    ).then(
        get_leaderboard,
        outputs=[leaderboard_table],
    ).then(
        quoata_check, outputs=[quota_details]
    )


if __name__ == "__main__":

    config = RateLimitConfig(
        max_per_day=MAX_SUBMISSIONS_PER_USER_PER_DAY,
        max_total=MAX_TOTAL_SUBMISSIONS_PER_USER,
        min_interval_seconds=RATE_LIMIT_MIN_INT_SEC,
    )
    limiter = RateLimiter(config)

    app.launch()
