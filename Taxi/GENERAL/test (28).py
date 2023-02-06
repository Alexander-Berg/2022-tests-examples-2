import json
import os
import typing as tp

import pandas as pd
import torch

from supportai_ml.inference.intent_detectors import (
    applier_factory as applier_factory,
)
from supportai_ml.inference.intent_detectors import thresholds
from supportai_ml.train.intent_detectors import configs
from supportai_ml.train.intent_detectors import constants
from supportai_ml.train.intent_detectors import io_utils
from supportai_ml.train.intent_detectors import logging_utils
from supportai_ml.train.intent_detectors import metrics


def create_test_applied(
    test_table: pd.DataFrame,
    responses: tp.List[thresholds.Response],
    output_folder: str,
) -> pd.DataFrame:
    test_table[constants.PREDICTED_INTENT_COLUMN_NAME] = [
        json.dumps(response.serialize(), ensure_ascii=False)
        for response in responses
    ]
    test_table.to_csv(os.path.join(output_folder, "test_applied.csv"))
    return test_table


def run(config: configs.PipelineConfig) -> None:
    torch.set_num_threads(4)  # TODO nkpalchikov make this configurable
    test_table = io_utils.load_raw_dataframe(
        config.data_folder,
        constants.TEST_FILENAME,
    )
    applier = applier_factory.load_applier(
        config.applier_slug,
        config.test_io.input_folder,
    )
    applier.to_device("cuda:0")  # TODO nkpalchikov make this configurable
    model_topics_config = thresholds.Config.from_config_filepath(
        os.path.join(
            config.test_io.input_folder,
            constants.MODEL_TOPICS_CONFIG_FILENAME,
        ),
    )
    responses, times = applier.apply_to_test(
        test_table["request_body"],
        model_topics_config,
    )
    create_test_applied(
        test_table,
        responses,
        config.test_io.output_folder,
    )
    metrics_result = metrics.calculate_all_metrics(
        responses,
        test_table["topic"],
        times,
    )
    with open(
        os.path.join(
            config.test_io.output_folder,
            "metrics.json",
        ),
        "w",
    ) as fout:
        json.dump(metrics_result, fout, ensure_ascii=False, indent=2)
    logging_utils.print_metrics(metrics_result)
