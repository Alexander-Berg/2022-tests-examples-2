from taxi_pyml.eats_courier_hiring_by_phone import postprocess
from taxi_pyml.eats_courier_hiring_by_phone.types import Request

import pytest


@pytest.fixture
def postprocessor(get_directory_path):
    return postprocess.Postprocessor.from_resources_path(
        get_directory_path('resources'),
    )


@pytest.fixture
def postprocessor_with_content_exp(get_directory_path):
    return postprocess.Postprocessor.from_resources_path(
        get_directory_path('resources_with_content_exp'),
    )


def test_ok_request(postprocessor, load_json):
    topics_probabilities = None
    data = Request.from_dict(load_json('ok_request.json'))

    result = postprocessor(topics_probabilities, data)

    assert result['macro_id'] == 10
    assert result['topic'] == 'not_sure_topic'
    assert set(result['tags']) == {
        'experiment3_experiment',
        'ar_eats_courier_hiring_by_phone',
        'ar_done',
        'ar_checked',
    }


def test_forward_request(postprocessor, load_json):
    topics_probabilities = None
    data = Request.from_dict(load_json('forward_request.json'))

    result = postprocessor(topics_probabilities, data)

    assert result['forward'] == 'line1'
    assert result['topic'] == 'not_sure_topic'


def test_ask_again_request(postprocessor, load_json):
    topics_probabilities = None
    data = Request.from_dict(load_json('ask_again_request_first.json'))

    result = postprocessor(topics_probabilities, data)

    assert result['macro_id'] == postprocess.ASK_AGAIN_INDEX
    assert result['topic'] == 'not_sure_topic'
    assert set(result['tags']) == {
        'ar_checked',
        'ar_eats_courier_hiring_by_phone',
        'experiment3_experiment',
        'ml_fail_rules',
        'ml_fail_rules_not_sure_topic',
    }

    topics_probabilities = None
    data = Request.from_dict(load_json('ask_again_request_second.json'))

    result = postprocessor(topics_probabilities, data)

    assert result['macro_id'] == postprocess.ASK_AGAIN_INDEX
    assert result['topic'] == 'not_sure_topic'
    assert set(result['tags']) == {
        'ar_checked',
        'ar_eats_courier_hiring_by_phone',
        'experiment3_experiment',
        'ml_fail_rules',
        'ml_fail_rules_not_sure_topic',
    }


def test_no_ask_again_request(postprocessor, load_json):
    topics_probabilities = None
    data = Request.from_dict(load_json('no_ask_again_request.json'))

    result = postprocessor(topics_probabilities, data)

    assert result['macro_id'] == postprocess.SEND_TO_OPERATOR_INDEX


def test_empty_request(postprocessor, load_json):
    topics_probabilities = None
    data = Request.from_dict(load_json('empty_request.json'))

    result = postprocessor(topics_probabilities, data)

    assert result['macro_id'] == 139897
    assert result['topic'] == 'empty_message_topic'
    assert set(result['tags']) == {
        'experiment3_experiment',
        'ar_eats_courier_hiring_by_phone',
        'ar_checked',
        'ar_done',
        'ar_last_empty_message',
    }


def test_control_request(postprocessor, load_json):
    topics_probabilities = None
    data = Request.from_dict(load_json('control_request.json'))

    result = postprocessor(topics_probabilities, data)

    assert result['macro_id'] == postprocess.SEND_TO_OPERATOR_INDEX
    assert result['topic'] == 'not_sure_topic'
    assert set(result['tags']) == {
        'ml_fail_control',
        'ar_eats_courier_hiring_by_phone',
        'ar_checked',
    }


def test_empty_broken_model_topics_config_request(postprocessor, load_json):
    topics_probabilities = None
    data = Request.from_dict(load_json('empty_request.json'))
    postprocessor._model_topics_config[0]['empty_message_topic'] = False

    result = postprocessor(topics_probabilities, data)

    assert result['macro_id'] == postprocess.SEND_TO_OPERATOR_INDEX
    assert result['topic'] == 'operator_topic'
    assert set(result['tags']) == {
        'experiment3_experiment',
        'ar_eats_courier_hiring_by_phone',
        'ar_checked',
        'ml_fail_no_empty_message_topic',
    }


def test_first_message_from_system_request(postprocessor, load_json):
    topics_probabilities = None
    data = Request.from_dict(
        load_json('first_message_from_system_request.json'),
    )

    result = postprocessor(topics_probabilities, data)

    assert result['macro_id'] == postprocess.ASK_AGAIN_INDEX
    assert result['topic'] == 'not_sure_topic'
    assert set(result['tags']) == {
        'ar_checked',
        'ar_eats_courier_hiring_by_phone',
        'experiment3_experiment',
        'ml_fail_rules',
        'ml_fail_rules_not_sure_topic',
    }
