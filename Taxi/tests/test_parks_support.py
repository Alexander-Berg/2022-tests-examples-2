from taxi_pyml.parks_support import postprocess
from taxi_pyml.parks_support.types import Request

import pytest


@pytest.fixture
def postprocessor(get_directory_path):
    return postprocess.Postprocessor.from_resources_path(
        get_directory_path('resources'),
    )


def test_feedback_about_rider_general(postprocessor, load_json):
    topics_probabilities = load_json('probs_feedback_about_rider.json')[
        'topics_probabilities'
    ]
    data = Request.fill_data_with_fields(
        load_json('feedback_about_rider.json'),
    )
    assert data.extra['comment_lowercased'] == data.comment.lower()

    response = postprocessor(topics_probabilities, data)
    assert response['parent_confidence'] >= response['confidence']
    assert response == {
        'topic': 'dr_trips_feedback_about_rider',
        'most_probable_topic': 'dr_trips_feedback_about_rider_kids',
        'confidence': 0.55,
        'parent_confidence': 0.75,
        'topics_probabilities': topics_probabilities,
        'macro_id': 182239,
        'status': 'ok',
        'line': 'complaint',
        'line_confidence': 0.75,
        'tags': [
            'ar_checked',
            'ar_done',
            'ar_parks_v1',
            'experiment3_ml_top_macros_choose_not_available',
            'ml_topic_dr_trips_feedback_about_rider',
        ],
        'top_probable_macros': [182239, 182241, 182240, 182309, 182306],
    }


def test_driver_rating(postprocessor, load_json):
    topics_probabilities = load_json('probs_drivers_rating.json')[
        'topics_probabilities'
    ]
    data = Request.fill_data_with_fields(load_json('drivers_rating.json'))

    response = postprocessor(topics_probabilities, data)
    assert response['parent_confidence'] >= response['confidence']
    assert response == {
        'topic': 'dr_driver_rating',
        'most_probable_topic': 'dr_driver_rating',
        'confidence': 0.8,
        'parent_confidence': 0.8,
        'topics_probabilities': topics_probabilities,
        'macro_id': 182306,
        'status': 'ok',
        'line': 'account_other',
        'line_confidence': 0.8,
        'tags': [
            'ar_checked',
            'ar_done',
            'ar_parks_v1',
            'experiment3_ml_top_macros_choose_not_available',
            'ml_topic_dr_driver_rating',
        ],
        'top_probable_macros': [182306, 182309, 182239, 182241, 182240],
    }


def test_feedback_about_rider_general_ml_control(postprocessor, load_json):
    topics_probabilities = load_json('probs_feedback_about_rider.json')[
        'topics_probabilities'
    ]
    request_data = load_json('feedback_about_rider.json')
    request_data['control_tag'] = 'ml_fail_control'
    data = Request.fill_data_with_fields(request_data)

    response = postprocessor(topics_probabilities, data)
    assert response['parent_confidence'] >= response['confidence']
    assert response == {
        'topic': 'dr_trips_feedback_about_rider',
        'most_probable_topic': 'dr_trips_feedback_about_rider_kids',
        'confidence': 0.55,
        'parent_confidence': 0.75,
        'topics_probabilities': topics_probabilities,
        'macro_id': 182239,
        'status': 'nope',
        'line': 'complaint',
        'line_confidence': 0.75,
        'tags': [
            'ar_checked',
            'ar_parks_v1',
            'experiment3_ml_top_macros_choose_not_available',
            'ml_fail_control',
            'ml_topic_dr_trips_feedback_about_rider',
        ],
        'top_probable_macros': [],
    }


def test_feedback_about_rider_general_ml_top_macros_control(
        postprocessor, load_json,
):
    topics_probabilities = load_json('probs_feedback_about_rider.json')[
        'topics_probabilities'
    ]
    request_data = load_json('feedback_about_rider.json')
    request_data['control_ml_top_macros_tag'] = 'ml_top_macros_control'
    data = Request.fill_data_with_fields(request_data)

    response = postprocessor(topics_probabilities, data)
    assert response['parent_confidence'] >= response['confidence']
    assert response == {
        'topic': 'dr_trips_feedback_about_rider',
        'most_probable_topic': 'dr_trips_feedback_about_rider_kids',
        'confidence': 0.55,
        'parent_confidence': 0.75,
        'topics_probabilities': topics_probabilities,
        'macro_id': 182239,
        'status': 'ok',
        'line': 'complaint',
        'line_confidence': 0.75,
        'tags': [
            'ar_checked',
            'ar_done',
            'ar_parks_v1',
            'ml_top_macros_control',
            'ml_topic_dr_trips_feedback_about_rider',
        ],
        'top_probable_macros': [],
    }
