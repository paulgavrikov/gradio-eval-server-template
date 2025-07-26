from collections import defaultdict


class AverageMeter(object):
    """Computes and stores the average and current value"""

    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


def clean_submission(preds):
    cleaned_preds = preds

    # TODO: Implement your cleaning logic here

    return cleaned_preds


def evaluate_submission(preds, ground_truth) -> dict:
    # TODO: Implement your evaluation logic

    accuracy_meter = defaultdict(AverageMeter)

    accuracy_meter["partition1"].update(0.43)
    accuracy_meter["partition2"].update(0.42)
    accuracy_meter["partition3"].update(0.99)

    return dict([(f"accuracy/{k}", 100 * v.avg) for k, v in accuracy_meter.items()])
