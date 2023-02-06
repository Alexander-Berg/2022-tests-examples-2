import os

import pandas as pd

from supportai_ml.train.intent_detectors import configs
from supportai_ml.train.intent_detectors import holistic_evaluation
from supportai_ml.train.intent_detectors import metrics


def test_default_configs_are_correct() -> None:
    root_folder = "supportai_ml/train/intent_detectors/default_configs"
    for filename in os.listdir(root_folder):
        path = os.path.join(root_folder, filename)
        configs.PipelineConfig.from_file(path)


def test_indomain_accuracy() -> None:
    assert (
        metrics.calculate_indomain_accuracy(
            pd.Series(["a", "b", "a", "b"]),
            pd.Series(["a", "b", "other__classes", "other__classes"]),
        )
        == 1
    )
    assert (
        metrics.calculate_indomain_accuracy(
            pd.Series(["a", "b", "c", "c"]),
            pd.Series(["a", "b", "a", "b"]),
        )
        == 0.5
    )

    assert (
        metrics.calculate_indomain_accuracy(
            pd.Series(["a", "b", "c", "c"]),
            pd.Series(
                ["b", "other__classes", "other__classes", "other__classes"]
            ),
        )
        == 0.0
    )


def test_true_num_samples_grid() -> None:
    assert holistic_evaluation.SAMPLES_PER_TOPIC_SPACE == [
        5,
        10,
        15,
        20,
        25,
        30,
        35,
        40,
        45,
        50,
    ]
