import json
import pytest
import typing as tp

import numpy as np
import pandas as pd

from nile.api.v1 import Record

from projects.supportai.thresholds import thresholds_data_preparation
from taxi_pyml.supportai.common import model_topics


@pytest.fixture
def sample_request_response_topic():
    return [
        (
            {
                'dialog': {
                    'messages': [
                        {
                            'text': (
                                'Добрый день! 24 февраля сделали заказ, '
                                'привезли ряженку с истёкшим сроком годности'
                            ),
                            'author': 'user',
                            'language': 'ru',
                        },
                        {
                            'text': 'Только сейчас увидела',
                            'author': 'user',
                            'language': 'ru',
                        },
                        {
                            'text': (
                                'Здравствуйте, Анастасия!\n'
                                'Простите, пожалуйста, за эту ситуацию.'
                            ),
                            'author': 'support',
                            'language': 'ru',
                        },
                        {
                            'text': 'Пытаюсь прогрузить',
                            'author': 'user',
                            'language': 'ru',
                        },
                        {
                            'text': (
                                'Простите, что привезли несвежую ряженку :('
                            ),
                            'author': 'support',
                            'language': 'ru',
                        },
                        {
                            'text': 'Можете привезти новые',
                            'author': 'user',
                            'language': 'ru',
                        },
                        {
                            'text': 'Отправил заказ из позиций',
                            'author': 'support',
                            'language': 'ru',
                        },
                        {
                            'text': (
                                'Прислали опять ряженку со '
                                'сроком годности 23 февраля!!!'
                            ),
                            'author': 'user',
                            'language': 'ru',
                        },
                        {
                            'text': 'Капец, ребята!',
                            'author': 'user',
                            'language': 'ru',
                        },
                    ],
                },
                'control_tag': 'experiment3_experiment',
                'features': [],
            },
            {
                'tag': {
                    'add': [
                        'ml_topic_FOODTECH_product_quality__product_spoiled',
                        'ml_topic_net_FOODTECH_product_'
                        'quality__product_spoiled',
                    ],
                },
                'features': {
                    'most_probable_topic': (
                        'FOODTECH_product_quality__product_spoiled'
                    ),
                    'sure_topic': 'FOODTECH_product_quality__product_spoiled',
                    'probabilities': [
                        {
                            'topic_name': 'FOODTECH_Missing_dish_or_product',
                            'probability': 0.0049065593630075455,
                        },
                        {
                            'topic_name': (
                                'FOODTECH_product_quality__product_expired'
                            ),
                            'probability': 0.2576819360256195,
                        },
                        {
                            'topic_name': 'other__classes',
                            'probability': 0.14093896746635437,
                        },
                    ],
                },
            },
            b'FOODTECH_product_quality__product_expired',
        ),
    ]


@pytest.fixture
def sample_dataframe(sample_request_response_topic) -> pd.DataFrame:
    output = {'topic': [], 'request_body': [], 'response_body': []}
    for request, response, topic in sample_request_response_topic:
        output['topic'].append(topic)
        output['request_body'].append(json.dumps(request))
        output['response_body'].append(json.dumps(response))
    return pd.DataFrame(output)


@pytest.fixture
def sample_model_topics_config() -> tp.List[model_topics.Topic]:
    return [
        model_topics.Topic.deserialize(
            {
                'slug': 'FOODTECH_Missing_dish_or_product',
                'thresholds': [
                    {'threshold_based_on_precision': 0.008187716826796532},
                    {'threshold_based_on_precision': 0.03544704616069794},
                ],
                'rule_value': None,
                'parent_slug': None,
            },
        ),
        model_topics.Topic.deserialize(
            {
                'slug': 'FOODTECH_product_quality__product_expired',
                'thresholds': [
                    {'threshold_based_on_precision': 0.03526797890663147},
                    {'threshold_based_on_precision': 0.0672706663608551},
                ],
                'rule_value': None,
                'parent_slug': None,
            },
        ),
        model_topics.Topic.deserialize(
            {
                'slug': 'other__classes',
                'thresholds': [
                    {'threshold_based_on_precision': 0.26248475909233093},
                    {'threshold_based_on_precision': 0.3782869279384613},
                ],
                'rule_value': None,
                'parent_slug': None,
            },
        ),
    ]


def test_thresholds(sample_dataframe, sample_model_topics_config):
    output = list(
        thresholds_data_preparation.calculate_thresholds_data(
            table=sample_dataframe,
            model_topics_config=sample_model_topics_config,
            request_column_name='request_body',
            response_column_name='response_body',
            topic_column_name='topic',
        ),
    )
    assert len(output) == 1
    assert isinstance(output[0], Record)
    assert output[0].iteration == 4
    assert np.allclose(
        output[0].probabilities,
        [0.0049065593630075455, 0.2576819360256195, 0.14093896746635437],
    )
    assert output[0].topic == 'FOODTECH_product_quality__product_expired'
