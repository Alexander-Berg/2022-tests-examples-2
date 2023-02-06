import argparse
import json
import logging
import os
import typing as tp

from sklearn import metrics
from tqdm import tqdm
import pandas as pd

import nile.api.v1 as nile_api

from projects.supportai.sentence_bert_one_message_training import data_utils
from taxi_pyml.supportai.common import model_topics
from taxi_pyml.supportai.common import types
from taxi_pyml.supportai.models.sentence_bert_one_message import (
    model as model_module,
)


REQUEST_BODIES_COLUMN = 'request_body'
TOPIC_COLUMN = 'topic'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--yt_test_path', help='yt path to test')
    parser.add_argument(
        '--yt_output_test_applied', help='output yt path to test applied',
    )
    parser.add_argument(
        '--resources_path', help='path to model weights and etc',
    )
    parser.add_argument('--yt_proxy', help='yt_proxy')
    return parser.parse_args()


def apply_model(
        model: model_module.Model,
        config: model_topics.Config,
        test_data: tp.Iterable[nile_api.Record],
) -> pd.DataFrame:
    request_bodies: tp.List[str] = []
    response_bodies: tp.List[str] = []
    predicted_topics: tp.List[str] = []
    true_topics: tp.List[str] = []

    logging.info('Applying model')
    for data_item in tqdm(test_data):
        request_bodies.append(data_item.request_body)
        request_for_model = types.Request.deserialize(
            json.loads(data_item.request_body),
        )
        model_response = model(request_for_model, config)
        response_bodies.append(data_utils.serialize_response(model_response))
        predicted_topics.append(
            model_response.sure_topic
            if model_response.sure_topic is not None
            else 'not_sure',
        )
        true_topics.append(data_item.topic)

    logging.info(metrics.classification_report(true_topics, predicted_topics))

    test_applied_df = pd.DataFrame(
        {
            'topic': true_topics,
            'request_body': request_bodies,
            'response_body': response_bodies,
        },
    )
    return test_applied_df


def main():
    logging.basicConfig(
        format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO,
    )
    args = parse_args()

    logging.info('Loading model from resources_path')
    model = model_module.Model.from_resources_path(args.resources_path)
    config = model_topics.Config.from_config_filepath(
        os.path.join(args.resources_path, 'model_topics_config.json'),
    )

    cluster = data_utils.get_cluster(args.yt_proxy)
    test_data = cluster.read(args.yt_test_path, bytes_decode_mode='strict')

    test_applied_df = apply_model(model, config, test_data)

    logging.info('Uploading results to yt')
    data_utils.save_table_to_yt(
        args.yt_proxy, test_applied_df, args.yt_output_test_applied,
    )


if __name__ == '__main__':
    main()
