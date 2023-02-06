from taxi_pyml.taxi_client_chat_support import postprocess
from taxi_pyml.taxi_client_chat_support import types

import pytest


@pytest.fixture
def postprocessor(get_directory_path):
    return postprocess.Postprocessor.from_resources_path(
        get_directory_path('resources'),
    )


def test_ok_request(postprocessor, load_json):
    topics_probabilities = [0, 0.1, 0.9, 0, 0, 0]
    data = types.Request.fill_data_with_fields(load_json('ok_request.json'))

    result = postprocessor(topics_probabilities, data)

    assert result.macro_id == 124000
    assert result.topic == 'rd_feedback_professionalism_cancel_before_trip'
    assert result.status == 'ok'
    assert set(result.top_probable_macros) <= {
        124000,
        125000,
        139897,
        139898,
        139899,
        139900,
    }


def test_keywords_request(postprocessor, load_json):
    topics_probabilities = [0, 0.1, 0.9, 0, 0, 0]
    data = types.Request.fill_data_with_fields(
        load_json('keyword_request.json'),
    )

    result = postprocessor(topics_probabilities, data)
    assert result.macro_id is None
    assert result.status == 'nope'
    assert 'ml_fail_keywords' in result.tags

    data = types.Request.fill_data_with_fields(
        load_json('urgent_keyword_request.json'),
    )
    result = postprocessor(topics_probabilities, data)
    assert result.macro_id is None
    assert result.status == 'nope'
    assert result.line == 'urgent'
    assert 'ml_fail_urgent_keywords' in result.tags


def test_similarity_request(postprocessor, load_json):
    topics_probabilities = [0, 0, 1, 0, 0, 0]
    data = types.Request.fill_data_with_fields(
        load_json('similarity_request.json'),
    )

    result = postprocessor(topics_probabilities, data)

    assert result.macro_id == 125000
    assert result.topic == 'rd_feedback_professionalism_cancel_before_trip'
    assert result.status == 'waiting'
    assert set(result.top_probable_macros) <= {
        124000,
        125000,
        139897,
        139898,
        139899,
        139900,
    }
