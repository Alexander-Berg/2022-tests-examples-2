from taxi_pyml.eats.support import postprocess
from taxi_pyml.eats.support.types import Request

import pytest


@pytest.fixture
def postprocessor(get_directory_path):
    return postprocess.Postprocessor.from_resources_path(
        get_directory_path('resources'),
    )


def test_time_problem_request(postprocessor, load_json):
    topics_probabilities = [0.1, 0.8, 0.1, 0, 0, 0, 0, 0, 0]
    data = Request.from_dict(load_json('time_problem.json'))

    assert postprocessor(topics_probabilities, data) == {
        'topic': 'Время',
        'most_probable_topic': 'Время',
        'topics_probabilities': [0.1, 0.8, 0.1, 0, 0, 0, 0, 0, 0],
        'macro_id': 2,
        'status': 'ok',
        'tags': ['ar_checked', 'ar_done', 'ar_eatsmodel_v1'],
    }


def test_taste_not_reply_request(postprocessor, load_json):
    topics_probabilities = [0.8, 0, 0.1, 0, 0, 0, 0, 0, 0.1]
    data = Request.from_dict(load_json('taste_not_reply.json'))

    assert postprocessor(topics_probabilities, data) == {
        'topic': 'Вкус',
        'most_probable_topic': 'Вкус',
        'topics_probabilities': [0.8, 0, 0.1, 0, 0, 0, 0, 0, 0.1],
        'macro_id': None,
        'status': 'not_reply',
        'tags': ['ar_checked', 'ar_done', 'ar_eatsmodel_v1'],
    }


def test_unknown_comment_request(postprocessor, load_json):
    topics_probabilities = None
    data = Request.from_dict(load_json('unknown_comment.json'))

    assert postprocessor(topics_probabilities, data) == {
        'topic': None,
        'most_probable_topic': None,
        'topics_probabilities': None,
        'macro_id': None,
        'status': 'nope',
        'tags': ['ar_checked', 'ar_eatsmodel_v1'],
    }
