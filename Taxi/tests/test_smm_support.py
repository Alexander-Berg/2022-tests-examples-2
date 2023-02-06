from taxi_pyml.smm_support import postprocess
from taxi_pyml.smm_support.types import Request

import pytest


@pytest.fixture
def eats_postprocessor(get_directory_path):
    return postprocess.Postprocessor.from_resources_path(
        get_directory_path('eats_resources'),
    )


@pytest.fixture
def taxi_postprocessor(get_directory_path):
    return postprocess.Postprocessor.from_resources_path(
        get_directory_path('taxi_resources'),
    )


def test_taxi_spam_request(taxi_postprocessor, load_json):
    topics_probabilities = [0.8, 0.1, 0.1]
    data = Request.from_dict(load_json('taxi_spam_request.json'))

    assert taxi_postprocessor(topics_probabilities, data) == {
        'topic': 'spam',
        'most_probable_topic': 'spam',
        'topics_probabilities': topics_probabilities,
        'macro_id': None,
        'status': 'not_reply',
        'tags': [
            'checked',
            'ml_not_reply',
            'ml_topic_spam',
            'smm_topic_taxi',
            'smmtaxi_v1',
        ],
    }


def test_taxi_not_reply_request(taxi_postprocessor, load_json):
    topics_probabilities = [0.05, 0.9, 0.05]
    data = Request.from_dict(load_json('taxi_not_reply_request.json'))

    assert taxi_postprocessor(topics_probabilities, data) == {
        'topic': 'not_reply',
        'most_probable_topic': 'not_reply',
        'topics_probabilities': topics_probabilities,
        'macro_id': None,
        'status': 'not_reply',
        'tags': [
            'checked',
            'ml_not_reply',
            'ml_topic_not_reply',
            'smm_topic_taxi',
            'smmtaxi_v1',
        ],
    }


def test_taxi_reply_request(taxi_postprocessor, load_json):
    topics_probabilities = [0.05, 0.1, 0.85]
    data = Request.from_dict(load_json('taxi_reply_request.json'))

    assert taxi_postprocessor(topics_probabilities, data) == {
        'topic': 'reply',
        'most_probable_topic': 'reply',
        'topics_probabilities': topics_probabilities,
        'macro_id': None,
        'status': 'nope',
        'tags': [
            'checked',
            'ml_fail_rules',
            'ml_topic_reply',
            'smm_topic_taxi',
            'smmtaxi_v1',
        ],
    }


def test_taxi_reply_because_empty_field_request(taxi_postprocessor, load_json):
    topics_probabilities = [0.05, 0.9, 0.05]
    data = Request.from_dict(
        load_json('taxi_reply_because_empty_field_request.json'),
    )

    assert taxi_postprocessor(topics_probabilities, data) == {
        'topic': 'not_reply',
        'most_probable_topic': 'not_reply',
        'topics_probabilities': topics_probabilities,
        'macro_id': None,
        'status': 'nope',
        'tags': [
            'checked',
            'ml_fail_rules',
            'ml_topic_not_reply',
            'smm_topic_Yandex.Taxi_Водители',
            'smmtaxi_v1',
        ],
    }


def test_taxi_reply_because_rules_request(taxi_postprocessor, load_json):
    topics_probabilities = [0.05, 0.9, 0.05]
    data = Request.from_dict(
        load_json('taxi_reply_because_rules_request.json'),
    )

    assert taxi_postprocessor(topics_probabilities, data) == {
        'topic': 'not_reply',
        'most_probable_topic': 'not_reply',
        'topics_probabilities': topics_probabilities,
        'macro_id': None,
        'status': 'nope',
        'tags': [
            'checked',
            'ml_fail_rules',
            'ml_topic_not_reply',
            'smm_topic_taxi',
            'smmtaxi_v1',
        ],
    }


def test_eats_reply_request(eats_postprocessor, load_json):
    topics_probabilities = [0.05, 0.05, 0.85, 0.05]
    data = Request.from_dict(load_json('eats_reply_request.json'))

    assert eats_postprocessor(topics_probabilities, data) == {
        'topic': 'reply',
        'most_probable_topic': 'reply',
        'topics_probabilities': topics_probabilities,
        'macro_id': None,
        'status': 'nope',
        'tags': [
            'checked',
            'ml_fail_rules',
            'ml_topic_reply',
            'smm_topic_eats',
            'smmeats_v1',
        ],
    }


def test_eats_hiring_request(eats_postprocessor, load_json):
    topics_probabilities = [0.05, 0.05, 0.05, 0.85]
    data = Request.from_dict(load_json('eats_hiring_request.json'))

    assert eats_postprocessor(topics_probabilities, data) == {
        'topic': 'hiring',
        'most_probable_topic': 'hiring',
        'topics_probabilities': topics_probabilities,
        'macro_id': None,
        'status': 'not_reply',
        'tags': [
            'checked',
            'ml_not_reply',
            'ml_topic_hiring',
            'smm_topic_eats',
            'smmeats_v1',
        ],
    }
