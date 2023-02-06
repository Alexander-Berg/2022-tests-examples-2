from taxi_pyml.mediaservices_support import postprocess
from taxi_pyml.mediaservices_support.types import Request
from taxi_pyml.mediaservices_support.model import Model
import pytest


@pytest.fixture
def resources_path(get_directory_path):
    return get_directory_path('resources')


@pytest.fixture
def postprocessor(resources_path):
    return postprocess.Postprocessor.from_resources_path(resources_path)


def test_ok_request(postprocessor, load_json):
    topics_probabilities = [1, 0, 0]
    data = Request.from_dict(load_json('ok_request.json'))

    result = postprocessor(topics_probabilities, data)

    assert result.topic == 'mbilling_refund'
    assert result.line == 'mbilling_refund_new'
    assert set(result.tags) == {
        'experiment3_experiment',
        'music_model_v1',
        'music_checked',
        'music_model_topic_mbilling_refund',
        'music_model_routing_done',
    }


def test_other_class_request(postprocessor, load_json):
    topics_probabilities = [0, 0, 1]
    data = Request.from_dict(load_json('ok_request.json'))

    result = postprocessor(topics_probabilities, data)

    assert result.topic == 'other__classes'
    assert result.line is None
    assert set(result.tags) == {
        'experiment3_experiment',
        'ml_fail_absent_topic',
        'ml_fail_absent_topic_other__classes',
        'music_model_v1',
        'music_checked',
        'music_model_topic_other__classes',
    }


def test_not_sure_in_line_request(postprocessor, load_json):
    topics_probabilities = [0.1, 0.8, 0.1]
    data = Request.from_dict(load_json('ok_request.json'))

    result = postprocessor(topics_probabilities, data)

    assert result.topic is None
    assert result.line is None
    assert set(result.tags) == {
        'experiment3_experiment',
        'music_model_v1',
        'music_checked',
        'ml_fail_not_sure_in_topic',
        'ml_fail_not_sure_in_topic_mbilling_cancel',
    }


def test_end_to_end(postprocessor, resources_path, load_json, monkeypatch):
    def mock_model_creation(*args, **kwargs):
        return None

    monkeypatch.setattr(Model, 'create_bert_model', mock_model_creation)

    def mock_probabilities(*args, **kwargs):
        return [0.1, 0.8, 0.1]

    monkeypatch.setattr(Model, 'get_probabilities', mock_probabilities)

    model = Model.from_resources_path(resources_path)
    request = Request.from_dict(load_json('ok_request.json'))
    response = model(request, postprocessor)
    assert response.line is None
    assert set(response.tags) == {
        'experiment3_experiment',
        'music_model_v1',
        'music_checked',
        'ml_fail_not_sure_in_topic',
        'ml_fail_not_sure_in_topic_mbilling_cancel',
    }
