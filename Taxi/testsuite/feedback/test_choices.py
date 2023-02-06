import pytest


def call_choices(taxi_feedback, zone_id=None):
    body = {}

    if zone_id is not None:
        body['zone_id'] = zone_id

    return taxi_feedback.post(
        '1.0/retrieve_choices',
        body,
        headers={'YaTaxi-Api-Key': 'feedback_apikey'},
    )


DEFAULT_CHOICES_OBJ = {
    'low_rating_reason': [
        'smellycar',
        'rudedriver',
        'carcondition',
        'nochange',
        'notrip',
        'badroute',
        'driverlate',
    ],
    'cancelled_reason': [
        'usererror',
        'longwait',
        'othertaxi',
        'driverrequest',
        'droveaway',
    ],
}


DEFAULT_CHOICES_RESPONSE = {
    'low_rating_reason': [
        {
            'type': 'low_rating_reason',
            'value': 'notrip',
            'image_tag': '',
            'applicable_rating_values': [1, 2, 3],
            'match': {'guilt': ['driver'], 'status': ['transporting']},
        },
        {
            'type': 'low_rating_reason',
            'value': 'driverlate',
            'image_tag': '',
            'applicable_rating_values': [],
            'match': {},
        },
        {
            'type': 'low_rating_reason',
            'value': 'rudedriver',
            'image_tag': '',
            'applicable_rating_values': [],
            'match': {},
        },
        {
            'type': 'low_rating_reason',
            'value': 'smellycar',
            'image_tag': '',
            'applicable_rating_values': [],
            'match': {},
        },
        {
            'type': 'low_rating_reason',
            'value': 'carcondition',
            'image_tag': '',
            'applicable_rating_values': [],
            'match': {},
        },
        {
            'type': 'low_rating_reason',
            'value': 'badroute',
            'image_tag': '',
            'applicable_rating_values': [],
            'match': {},
        },
        {
            'type': 'low_rating_reason',
            'value': 'nochange',
            'image_tag': '',
            'applicable_rating_values': [],
            'match': {},
        },
    ],
    'cancelled_reason': [
        {
            'type': 'cancelled_reason',
            'value': 'usererror',
            'image_tag': '',
            'applicable_rating_values': [],
            'match': {},
        },
        {
            'type': 'cancelled_reason',
            'value': 'driverrequest',
            'image_tag': '',
            'applicable_rating_values': [],
            'match': {},
        },
        {
            'type': 'cancelled_reason',
            'value': 'longwait',
            'image_tag': '',
            'applicable_rating_values': [],
            'match': {},
        },
        {
            'type': 'cancelled_reason',
            'value': 'othertaxi',
            'image_tag': '',
            'applicable_rating_values': [],
            'match': {},
        },
        {
            'type': 'cancelled_reason',
            'value': 'droveaway',
            'image_tag': '',
            'applicable_rating_values': [],
            'match': {},
        },
    ],
}


MOSCOW_CHOICES_RESPONSE = {
    'low_rating_reason': [
        {
            'type': 'low_rating_reason',
            'value': 'rudedriver',
            'image_tag': '',
            'applicable_rating_values': [],
            'match': {},
        },
    ],
    'cancelled_reason': [
        {
            'type': 'cancelled_reason',
            'value': 'longwait',
            'image_tag': '',
            'applicable_rating_values': [],
            'match': {},
        },
    ],
}

EMPTY_CHOICES_RESPONSE: dict = {
    'low_rating_reason': [],
    'cancelled_reason': [],
}

DEFAULT_CHOICES = {
    '__default__': DEFAULT_CHOICES_OBJ,
    'moscow': {
        'low_rating_reason': ['rudedriver'],
        'cancelled_reason': ['longwait'],
    },
    'skolkovo': {'low_rating_reason': [], 'cancelled_reason': []},
}


def test_choices_bad_method(taxi_feedback):
    response = taxi_feedback.get(
        '1.0/retrieve_choices', headers={'YaTaxi-Api-Key': 'feedback_apikey'},
    )

    assert response.status_code == 405


@pytest.mark.config(SUPPORTED_FEEDBACK_CHOICES=DEFAULT_CHOICES)
@pytest.mark.parametrize(
    'zone,expected_choices',
    [
        (None, DEFAULT_CHOICES_RESPONSE),
        ('moscow', MOSCOW_CHOICES_RESPONSE),
        ('skolkovo', EMPTY_CHOICES_RESPONSE),
    ],
)
def test_choices(taxi_feedback, db, zone, expected_choices):
    response = call_choices(taxi_feedback, zone)
    assert response.status_code == 200
    data = response.json()
    assert data == expected_choices


@pytest.mark.config(SUPPORTED_FEEDBACK_CHOICES=DEFAULT_CHOICES)
def test_choices_unknown_zone(taxi_feedback):
    response = call_choices(taxi_feedback, 'unknown')
    assert response.status_code == 200
    assert response.json() == DEFAULT_CHOICES_RESPONSE
