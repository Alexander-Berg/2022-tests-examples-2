from taxi_pyml.autoreply_general import postprocess
from taxi_pyml.autoreply_general.types import Request

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


@pytest.fixture
def postprocessor_top_macros(get_directory_path):
    return postprocess.Postprocessor.from_resources_path(
        get_directory_path('resources_top_macros'),
    )


def test_ok_request(postprocessor, load_json):
    topics_probabilities = [0.59, 0.18, 0.12, 0, 0, 0, 0.11]
    data = Request.fill_data_with_fields(load_json('ok_request.json'))
    assert data.extra['comment_lowercased'] == data.comment.lower()

    result = postprocessor(topics_probabilities, data)

    assert result['macro_id'] == 139897
    assert result['topic'] == 'rd_fare_cancel_driver_canceled'
    assert result['top_probable_macros'] == [
        139897,
        122992,
        124933,
        195021,
        195022,
    ]
    assert result['status'] == 'ok'
    assert set(result['tags']) == {
        'ar_checked',
        'ar_model3',
        'ar_done',
        'ml_top_macros_experiment',
        'ml_topic_rd_fare_cancel_driver_canceled',
    }


def test_no_change_request(postprocessor, load_json):
    topics_probabilities = [0.11, 0.12, 0.16, 0, 0.04, 0.4, 0.17]
    data = Request.fill_data_with_fields(load_json('no_change_request.json'))

    result = postprocessor(topics_probabilities, data)

    assert (
        result['topic']
        == 'rd_feedback_professionalism_payment_fraud_not_change'
    )
    assert result['status'] == 'ok'
    assert result['predicted_change'] == 17
    assert result['predicted_promo_value'] == 20
    assert result['top_probable_macros'] == [
        195000,
        195021,
        195022,
        124933,
        122992,
    ]
    assert set(result['tags']) == {
        'ar_checked',
        'ar_model3',
        'ar_done',
        'ml_topic_rd_feedback_professionalism_payment_fraud_not_change',
        'ml_top_macros_experiment',
    }
    assert result['macro_id'] == 195000


def test_waiting_request(postprocessor, load_json):
    topics_probabilities = [0.2, 0.4, 0.16, 0, 0, 0.14, 0.1]
    data = Request.fill_data_with_fields(load_json('waiting_request.json'))

    result = postprocessor(topics_probabilities, data)

    assert (
        result['top_probable_macros']
        == [122992, 139897, 124933, 195000, 195021]
        or result['top_probable_macros']
        == [122992, 139897, 124933, 195000, 195022]
    )
    assert result['macro_id'] == 122992
    assert result['topic'] == 'rd_fare_extra_cash_driver_error_not_change'
    assert result['status'] == 'waiting'
    assert set(result['tags']) == {
        'ar_checked',
        'ar_model3',
        'ar_done',
        'ml_topic_rd_fare_extra_cash_driver_error_not_change',
        'ml_top_macros_experiment',
    }


def test_black_list_request(postprocessor, load_json):
    topics_probabilities = [0, 0, 1, 0, 0, 0, 0]
    data = Request.fill_data_with_fields(load_json('black_list_request.json'))

    result = postprocessor(topics_probabilities, data)

    assert result.get('macro_id') is None
    assert result['topic'] == 'rd_fare_cancellation_policy'
    assert len(result['top_probable_macros']) == 5
    assert result['top_probable_macros'][0] == 124933
    assert result['status'] == 'nope'
    assert set(result['tags']) == {
        'ar_checked',
        'ar_model3',
        'ml_topic_rd_fare_cancellation_policy',
        'ml_fail_blacklist_rd_fare_cancellation_policy',
        'ml_fail_blacklist',
        'ml_top_macros_experiment',
    }


def test_defer_request(postprocessor, load_json):
    topics_probabilities = [0, 0, 0, 1, 0, 0, 0]
    data = Request.fill_data_with_fields(load_json('defer_request.json'))

    result = postprocessor(topics_probabilities, data)

    assert result.get('macro_id') is None
    assert result['time'] == 5
    assert result['topic'] == 'rd_fare_cancellation'
    assert len(result['top_probable_macros']) == 5
    assert result['status'] == 'defer'
    assert set(result['tags']) == {
        'ar_checked',
        'ar_model3',
        'ml_topic_rd_fare_cancellation',
        'ml_top_macros_experiment',
    }


def test_topic_not_in_rules_request(postprocessor, load_json):
    topics_probabilities = [0.1, 0, 0, 0, 1, 0, 0]
    data = Request.fill_data_with_fields(
        load_json('topic_not_in_rules_request.json'),
    )

    result = postprocessor(topics_probabilities, data)

    assert result.get('macro_id') is None
    assert result.get('topic') == 'no_tag'
    assert len(result['top_probable_macros']) == 5
    assert result['top_probable_macros'][0] == 139897
    assert result['status'] == 'nope'
    assert set(result['tags']) == {
        'ar_checked',
        'ar_model3',
        'ml_topic_no_tag',
        'ml_fail_absent_topic_no_tag',
        'ml_fail_absent_topic',
        'ml_top_macros_experiment',
    }


def test_content_experiment(postprocessor_with_content_exp, load_json):
    topics_probabilities = [1, 0, 0, 0, 0, 0, 0]
    data = Request.fill_data_with_fields(load_json('ok_request.json'))

    result = postprocessor_with_content_exp(topics_probabilities, data)

    assert result['macro_id'] == 139898
    assert result['topic'] == 'rd_fare_cancel_driver_canceled'
    assert result['status'] == 'ok'
    assert set(result['tags']) == {
        'ar_checked',
        'ar_model3',
        'ar_done',
        'ml_topic_rd_fare_cancel_driver_canceled',
        'promocodes_experiment',
        'promocodes_experiment_changed',
        'promocodes_experiment_rd_fare_cancel_driver_canceled',
        'ml_top_macros_experiment',
    }


def test_content_experiment_empty_topic(
        postprocessor_with_content_exp, load_json,
):
    topics_probabilities = [0, 0.2, 0, 0, 0, 0, 0.8]
    data = Request.fill_data_with_fields(load_json('ok_request.json'))

    result = postprocessor_with_content_exp(topics_probabilities, data)

    assert result['macro_id'] is None
    assert result['topic'] == 'rd_feedback_empty_topic'
    assert result['top_probable_macros'][0] == 122992
    assert result['status'] == 'nope'
    assert set(result['tags']) == {
        'ar_checked',
        'ar_model3',
        'ml_fail_rules_evaluate_error',
        'ml_fail_rules_evaluate_error_rd_feedback_empty_topic',
        'ml_topic_rd_feedback_empty_topic',
        'ml_top_macros_experiment',
    }


def test_control_request(postprocessor, load_json):
    topics_probabilities = [0.59, 0.18, 0.12, 0, 0, 0, 0.11]
    data = Request.fill_data_with_fields(load_json('control_request.json'))

    result = postprocessor(topics_probabilities, data)

    assert result['macro_id'] == 139897
    assert result['topic'] == 'rd_fare_cancel_driver_canceled'
    assert result['top_probable_macros'] == []
    assert result['status'] == 'nope'
    assert set(result['tags']) == {
        'ar_checked',
        'ar_model3',
        'ml_fail_control',
        'ml_topic_rd_fare_cancel_driver_canceled',
        'ml_top_macros_experiment',
    }


def test_control_ml_top_macros_request(postprocessor, load_json):
    topics_probabilities = [0.59, 0.18, 0.12, 0, 0, 0, 0.11]
    data = Request.fill_data_with_fields(
        load_json('control_ml_top_macros_request.json'),
    )

    result = postprocessor(topics_probabilities, data)

    assert result['macro_id'] == 139897
    assert result['topic'] == 'rd_fare_cancel_driver_canceled'
    assert result['top_probable_macros'] == []
    assert result['status'] == 'ok'
    assert set(result['tags']) == {
        'ar_checked',
        'ar_model3',
        'ar_done',
        'ml_top_macros_control',
        'ml_topic_rd_fare_cancel_driver_canceled',
        'experiment3_experiment',
    }


def test_top_macros_range_request(postprocessor_top_macros, load_json):
    topics_probabilities = [0.59, 0.18, 0.12, 0, 0, 0, 0.11]
    data = Request.fill_data_with_fields(load_json('ok_request.json'))

    result = postprocessor_top_macros(topics_probabilities, data)

    assert result['macro_id'] is None
    assert result['topic'] == 'rd_fare_cancel_driver_canceled'
    assert result['top_probable_macros'] == [4, 1, 2]
    assert result['status'] == 'nope'
    assert set(result['tags']) == {
        'ar_checked',
        'ar_model3',
        'ml_fail_rules',
        'ml_fail_rules_rd_fare_cancel_driver_canceled',
        'ml_topic_rd_fare_cancel_driver_canceled',
        'ml_top_macros_experiment',
    }


def test_top_macros_range_several_topics_request(
        postprocessor_top_macros, load_json,
):
    topics_probabilities = [0, 0, 0.7, 0, 0, 0.1, 0.2]
    data = Request.fill_data_with_fields(load_json('ok_request.json'))

    result = postprocessor_top_macros(topics_probabilities, data)

    assert result['macro_id'] is None
    assert result['topic'] == 'rd_fare_cancellation_policy'
    assert result['top_probable_macros'] == [124933, 124934, 195022]
    assert result['status'] == 'nope'
    assert set(result['tags']) == {
        'ar_checked',
        'ar_model3',
        'ml_fail_blacklist',
        'ml_fail_blacklist_rd_fare_cancellation_policy',
        'ml_topic_rd_fare_cancellation_policy',
        'ml_top_macros_experiment',
    }
