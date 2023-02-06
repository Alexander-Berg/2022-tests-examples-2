from taxi_pyml.yadrive_support import postprocess
from taxi_pyml.yadrive_support.types import Request

import pytest


@pytest.fixture
def postprocessor(get_directory_path):
    return postprocess.Postprocessor.from_resources_path(
        get_directory_path('resources'),
    )


def test_feedback_ok_request(postprocessor, load_json):
    topics_probabilities = load_json(
        'probs_feedback_ok_and_control_requests.json',
    )['topics_probabilities']
    data = Request.from_dict(load_json('feedback_ok_request.json'))
    response = postprocessor(topics_probabilities, data)
    assert response['top5_most_probable_topic'] == [
        {'topic': '1', 'probability': 0.4},
        {'topic': '8', 'probability': 0.154},
        {'topic': '3', 'probability': 0.153},
        {'topic': '2', 'probability': 0.152},
        {'topic': '0', 'probability': 0.151},
    ]

    assert set(response['tags']) == {
        'experiment3_experiment',
        'ar_yadrivemodel_v1',
        'ar_checked',
        'ar_done',
    }


def test_feedback_control_request(postprocessor, load_json):
    topics_probabilities = load_json(
        'probs_feedback_ok_and_control_requests.json',
    )['topics_probabilities']
    data = Request.from_dict(load_json('feedback_control_request.json'))
    response = postprocessor(topics_probabilities, data)
    assert response['top5_most_probable_topic'] == [
        {'topic': '1', 'probability': 0.4},
        {'topic': '8', 'probability': 0.154},
        {'topic': '3', 'probability': 0.153},
        {'topic': '2', 'probability': 0.152},
        {'topic': '0', 'probability': 0.151},
    ]
    assert set(response['tags']) == {
        'ml_fail_control',
        'ar_yadrivemodel_v1',
        'ar_checked',
    }


def test_feedback_ok_several_messages_request(postprocessor, load_json):
    topics_probabilities = load_json(
        'probs_feedback_ok_and_control_requests.json',
    )['topics_probabilities']
    data = Request.from_dict(load_json('feedback_ok_several_messages.json'))
    response = postprocessor(topics_probabilities, data)
    assert response['top5_most_probable_topic'] == [
        {'topic': '1', 'probability': 0.4},
        {'topic': '8', 'probability': 0.154},
        {'topic': '3', 'probability': 0.153},
        {'topic': '2', 'probability': 0.152},
        {'topic': '0', 'probability': 0.151},
    ]

    assert set(response['tags']) == {
        'experiment3_experiment',
        'ar_yadrivemodel_v1',
        'ar_checked',
        'ar_done',
    }
