from taxi_pyml.b2b_support.sunlight import postprocess
from taxi_pyml.b2b_support.sunlight.types import Request

import pytest


@pytest.fixture
def postprocessor(get_directory_path):
    return postprocess.Postprocessor.from_resources_path(
        get_directory_path('resources'),
    )


def test_ok_request(postprocessor, load_json):
    topics_probabilities = [0, 1, 0, 0]
    data = Request.from_dict(load_json('ok_request.json'))

    result = postprocessor(topics_probabilities, data).serialize()

    assert result['send_text'] == 'Пожалуйста, уточните Ваш вопрос.'
    assert not result['route_to_employee']
    assert result['topic'] == 'general.clarify_question'
    assert set(result['tags']) == {
        'ar_done',
        'ar_checked',
        'sunlight_model_v1',
        'experiment3_experiment',
    }


def test_black_list_request(postprocessor, load_json):
    topics_probabilities = [0, 0, 1, 0]
    data = Request.from_dict(load_json('black_list_request.json'))

    result = postprocessor(topics_probabilities, data).serialize()

    assert result['send_text'] == ''
    assert result['route_to_employee']
    assert result['topic'] == 'general.info_bonus'
    assert set(result['tags']) == {
        'ar_checked',
        'sunlight_model_v1',
        'experiment3_experiment',
        'ml_fail_blacklist',
        'ml_fail_blacklist_general.info_bonus',
    }


def test_not_sure_in_topic_request(postprocessor, load_json):
    topics_probabilities = [0.27, 0.25, 0.25, 0.23]
    data = Request.from_dict(load_json('not_sure_in_topic_request.json'))

    result = postprocessor(topics_probabilities, data).serialize()
    assert result['send_text'] == ''
    assert result['route_to_employee']
    assert result['topic'] is None
    assert result['most_probable_topic'] == 'general.thanks'
    assert set(result['tags']) == {
        'ar_checked',
        'sunlight_model_v1',
        'experiment3_experiment',
        'ml_fail_not_sure_in_topic',
        'ml_fail_not_sure_in_topic_general.thanks',
    }


def test_control_experiment(postprocessor, load_json):
    topics_probabilities = [0, 1, 0, 0]
    data = Request.from_dict(load_json('control_request.json'))

    result = postprocessor(topics_probabilities, data).serialize()

    assert result['send_text'] == ''
    assert result['route_to_employee']
    assert result['topic'] == 'general.clarify_question'
    assert set(result['tags']) == {
        'ar_checked',
        'sunlight_model_v1',
        'ml_fail_control',
    }
