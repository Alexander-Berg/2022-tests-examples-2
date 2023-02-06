from taxi_pyml.drivers_support import postprocess
from taxi_pyml.drivers_support.types import Request

import pytest


@pytest.fixture
def postprocessor(get_directory_path):
    return postprocess.Postprocessor.from_resources_path(
        get_directory_path('resources'),
    )


def test_feedback_rider_alcohol_request(postprocessor, load_json):
    topics_probabilities = load_json('probs_feedback_rider_alcohol.json')[
        'topics_probabilities'
    ]
    data = Request.fill_data_with_fields(
        load_json('feedback_rider_alcohol_request.json'),
    )
    assert data.extra['comment_lowercased'] == data.comment.lower()
    assert data.extra['number_of_characters'] == len(data.comment)

    response = postprocessor(topics_probabilities, data)
    assert (
        data.extra['top1_most_probable_topic']
        == 'dr_trips_feedback_about_rider_alcohol_or_drug_intoxication'
    )
    assert (
        data.extra['top2_most_probable_topic']
        == 'dr_trips_feedback_about_rider_minor_altercation'
    )

    assert response['parent_confidence'] >= response['confidence']
    assert response == {
        'topic': 'dr_trips_feedback_about_rider_alcohol_or_drug_intoxication',
        'most_probable_topic': (
            'dr_trips_feedback_about_rider_alcohol_or_drug_intoxication'
        ),
        'confidence': max(topics_probabilities),
        'parent_confidence': max(topics_probabilities),
        'topics_probabilities': topics_probabilities,
        'macro_id': 146172,
        'status': 'ok',
        'line': 'complaint',
        'line_confidence': 0.93,
        'tags': [
            'ar_checked',
            'ar_done',
            'ar_drivers_v1',
            'experiment3_ml_top_macros_choose_not_available',
            f'ml_topic_{response["topic"]}',
        ],
        'top_probable_macros': [146172, 146176, 146000, 139162, 139163],
    }


def test_feedback_rider_minor_altercation(postprocessor, load_json):
    topics_probabilities = load_json(
        'probs_feedback_rider_minor_altercation.json',
    )['topics_probabilities']
    data = Request.fill_data_with_fields(
        load_json('feedback_rider_minor_altercation_request.json'),
    )

    response = postprocessor(topics_probabilities, data)
    assert response['parent_confidence'] > response['confidence']
    assert response == {
        'topic': 'dr_trips_feedback_about_rider',
        'most_probable_topic': (
            'dr_trips_feedback_about_rider_minor_altercation'
        ),
        'confidence': max(topics_probabilities),
        'parent_confidence': 0.93,
        'topics_probabilities': topics_probabilities,
        'macro_id': 146000,
        'status': 'ok',
        'line': 'complaint',
        'line_confidence': 0.93,
        'tags': [
            'ar_checked',
            'ar_done',
            'ar_drivers_v1',
            'experiment3_ml_top_macros_choose_not_available',
            'ml_topic_dr_trips_feedback_about_rider',
        ],
        'top_probable_macros': [146176, 146172, 146000, 139162, 139163],
    }


def test_account_inactive(postprocessor, load_json):
    topics_probabilities = load_json('probs_account_inactive.json')[
        'topics_probabilities'
    ]
    data = Request.fill_data_with_fields(
        load_json('account_inactive_request.json'),
    )

    response = postprocessor(topics_probabilities, data)
    assert response['parent_confidence'] >= response['confidence']
    assert response == {
        'topic': 'dr_account_inactive',
        'most_probable_topic': 'dr_account_inactive',
        'confidence': max(topics_probabilities),
        'parent_confidence': max(topics_probabilities),
        'topics_probabilities': topics_probabilities,
        'macro_id': 139163,
        'status': 'ok',
        'line': 'account',
        'line_confidence': 0.99,
        'tags': [
            'ar_checked',
            'ar_done',
            'ar_drivers_v1',
            'experiment3_ml_top_macros_choose_not_available',
            'ml_topic_dr_account_inactive',
        ],
        'top_probable_macros': [139163, 139162, 139164, 146176, 146172],
    }


def test_account_inactive_failed_line(postprocessor, load_json):
    topics_probabilities = load_json(
        'probs_account_inactive_failed_line.json',
    )['topics_probabilities']
    data = Request.fill_data_with_fields(
        load_json('account_inactive_request.json'),
    )

    response = postprocessor(topics_probabilities, data)
    assert response['parent_confidence'] >= response['confidence']
    assert response == {
        'topic': None,
        'most_probable_topic': 'dr_account_inactive',
        'confidence': max(topics_probabilities),
        'parent_confidence': max(topics_probabilities),
        'topics_probabilities': topics_probabilities,
        'macro_id': None,
        'status': 'nope',
        'line': 'other',
        'line_confidence': 0.0,
        'tags': [
            'ar_checked',
            'ar_drivers_v1',
            'experiment3_ml_top_macros_choose_not_available',
            'ml_fail_not_sure_in_topic',
            'ml_fail_not_sure_in_topic_dr_account_inactive',
        ],
        'top_probable_macros': [139163, 139162, 139164, 146176, 146172],
    }


def test_feedback_rider_vehicle_damage(postprocessor, load_json):
    topics_probabilities = load_json(
        'probs_feedback_rider_vehicle_damage.json',
    )['topics_probabilities']
    data = Request.fill_data_with_fields(
        load_json('feedback_rider_vehicle_damage_request.json'),
    )

    response = postprocessor(topics_probabilities, data)
    assert response['parent_confidence'] >= response['confidence']
    assert response == {
        'topic': 'dr_trips_feedback_about_rider_vehicle_interior_damage',
        'most_probable_topic': (
            'dr_trips_feedback_about_rider_vehicle_interior_damage'
        ),
        'confidence': max(topics_probabilities),
        'parent_confidence': max(topics_probabilities),
        'topics_probabilities': topics_probabilities,
        'macro_id': 146174,
        'status': 'ok',
        'line': 'complaint',
        'line_confidence': 0.96,
        'tags': [
            'ar_checked',
            'ar_done',
            'ar_drivers_v1',
            'experiment3_ml_top_macros_choose_not_available',
            'ml_topic_dr_trips_feedback_about_rider_vehicle_interior_damage',
        ],
        'top_probable_macros': [146174, 146000, 146176, 146172, 139162],
    }


def test_feedback_rider_urgent_keywords(postprocessor, load_json):
    topics_probabilities = load_json('probs_feedback_urgent_keywords.json')[
        'topics_probabilities'
    ]
    data = Request.fill_data_with_fields(
        load_json('feedback_rider_urgent_keywords.json'),
    )

    response = postprocessor(topics_probabilities, data)
    assert response['parent_confidence'] > response['confidence']
    assert response == {
        'topic': 'dr_trips_feedback_about_rider',
        'most_probable_topic': (
            'dr_trips_feedback_about_rider_minor_altercation'
        ),
        'confidence': max(topics_probabilities),
        'parent_confidence': 0.93,
        'topics_probabilities': topics_probabilities,
        'macro_id': 146000,
        'status': 'nope',
        'line': 'urgent',
        'line_confidence': 0.0,
        'tags': [
            'ar_checked',
            'ar_drivers_v1',
            'experiment3_ml_top_macros_choose_not_available',
            'ml_fail_urgent_keywords',
            'ml_topic_dr_trips_feedback_about_rider',
        ],
        'top_probable_macros': [146176, 146172, 146000, 139162, 139163],
    }


def test_feedback_rider_keywords(postprocessor, load_json):
    topics_probabilities = load_json('probs_feedback_rider_keywords.json')[
        'topics_probabilities'
    ]
    data = Request.fill_data_with_fields(
        load_json('feedback_rider_keywords.json'),
    )

    response = postprocessor(topics_probabilities, data)
    assert response['parent_confidence'] >= response['confidence']
    assert response == {
        'topic': 'dr_trips_feedback_about_rider_vehicle_interior_damage',
        'most_probable_topic': (
            'dr_trips_feedback_about_rider_vehicle_interior_damage'
        ),
        'confidence': max(topics_probabilities),
        'parent_confidence': max(topics_probabilities),
        'topics_probabilities': topics_probabilities,
        'macro_id': 146174,
        'status': 'nope',
        'line': 'complaint',
        'line_confidence': 0.96,
        'tags': [
            'ar_checked',
            'ar_drivers_v1',
            'experiment3_ml_top_macros_choose_not_available',
            'ml_fail_keywords',
            'ml_topic_dr_trips_feedback_about_rider_vehicle_interior_damage',
        ],
        'top_probable_macros': [146174, 146000, 146176, 146172, 139162],
    }


def test_feedback_rider_alcohol_request_ml_control(postprocessor, load_json):
    topics_probabilities = load_json('probs_feedback_rider_alcohol.json')[
        'topics_probabilities'
    ]
    request_data = load_json('feedback_rider_alcohol_request.json')
    request_data['control_tag'] = 'ml_fail_control'
    data = Request.fill_data_with_fields(request_data)
    assert data.extra['comment_lowercased'] == data.comment.lower()
    assert data.extra['number_of_characters'] == len(data.comment)

    response = postprocessor(topics_probabilities, data)
    assert (
        data.extra['top1_most_probable_topic']
        == 'dr_trips_feedback_about_rider_alcohol_or_drug_intoxication'
    )
    assert (
        data.extra['top2_most_probable_topic']
        == 'dr_trips_feedback_about_rider_minor_altercation'
    )

    assert response['parent_confidence'] >= response['confidence']
    assert response == {
        'topic': 'dr_trips_feedback_about_rider_alcohol_or_drug_intoxication',
        'most_probable_topic': (
            'dr_trips_feedback_about_rider_alcohol_or_drug_intoxication'
        ),
        'confidence': max(topics_probabilities),
        'parent_confidence': max(topics_probabilities),
        'topics_probabilities': topics_probabilities,
        'macro_id': 146172,
        'status': 'nope',
        'line': 'complaint',
        'line_confidence': 0.93,
        'tags': [
            'ar_checked',
            'ar_drivers_v1',
            'experiment3_ml_top_macros_choose_not_available',
            'ml_fail_control',
            f'ml_topic_{response["topic"]}',
        ],
        'top_probable_macros': [],
    }


def test_feedback_rider_alcohol_request_ml_top_macros_control(
        postprocessor, load_json,
):
    topics_probabilities = load_json('probs_feedback_rider_alcohol.json')[
        'topics_probabilities'
    ]
    request_data = load_json('feedback_rider_alcohol_request.json')
    request_data['control_ml_top_macros_tag'] = 'ml_top_macros_control'
    data = Request.fill_data_with_fields(request_data)
    assert data.extra['comment_lowercased'] == data.comment.lower()
    assert data.extra['number_of_characters'] == len(data.comment)

    response = postprocessor(topics_probabilities, data)
    assert (
        data.extra['top1_most_probable_topic']
        == 'dr_trips_feedback_about_rider_alcohol_or_drug_intoxication'
    )
    assert (
        data.extra['top2_most_probable_topic']
        == 'dr_trips_feedback_about_rider_minor_altercation'
    )

    assert response['parent_confidence'] >= response['confidence']
    assert response == {
        'topic': 'dr_trips_feedback_about_rider_alcohol_or_drug_intoxication',
        'most_probable_topic': (
            'dr_trips_feedback_about_rider_alcohol_or_drug_intoxication'
        ),
        'confidence': max(topics_probabilities),
        'parent_confidence': max(topics_probabilities),
        'topics_probabilities': topics_probabilities,
        'macro_id': 146172,
        'status': 'ok',
        'line': 'complaint',
        'line_confidence': 0.93,
        'tags': [
            'ar_checked',
            'ar_done',
            'ar_drivers_v1',
            'ml_top_macros_control',
            f'ml_topic_{response["topic"]}',
        ],
        'top_probable_macros': [],
    }
