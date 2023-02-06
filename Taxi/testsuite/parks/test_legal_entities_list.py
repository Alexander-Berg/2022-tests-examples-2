import json

import pytest


ALL_LEGAL_ENTITIES = [
    {
        'id': '5b5984fdfefe3d7ba0ac1234',
        'park_id': '123',
        'registration_number': '1',
        'name': 'Ivanov',
        'address': 'Msk',
        'work_hours': '11-13',
        'type': 'carrier_permit_owner',
        'legal_type': 'legal',
    },
    {
        'id': '5b5984fdfefe3d7ba0ac1235',
        'park_id': '123',
        'registration_number': '10',
        'name': 'Ivanov2',
        'address': 'Msk2',
        'work_hours': '11-14',
        'type': 'carrier_permit_owner',
        'legal_type': 'legal',
    },
    {
        'id': '5b5984fdfefe3d7ba0ac1236',
        'park_id': '123',
        'registration_number': '20',
        'name': 'Ivanov3',
        'address': 'Msk3',
        'work_hours': '11-14',
        'type': 'carrier_permit_owner',
        'legal_type': 'legal',
    },
    {
        'id': '5b5984fdfefe3d7ba0ac1237',
        'park_id': '456',
        'registration_number': '20',
        'name': 'Ivanov3',
        'address': 'Msk3',
        'work_hours': '11-14',
        'type': 'carrier_permit_owner',
        'legal_type': 'legal',
    },
]


def make_response(ids, has_more=False):
    return {
        'legal_entities': [
            prop for prop in ALL_LEGAL_ENTITIES if prop['id'] in ids
        ],
        'has_more': has_more,
    }


@pytest.mark.parametrize(
    'list_request,expected_response',
    [
        ({'query': {'park': {'id': ['net_takogo']}}}, make_response([])),
        (
            {'query': {'park': {'id': ['123']}, 'legal_entity': {'id': []}}},
            make_response(
                [
                    '5b5984fdfefe3d7ba0ac1234',
                    '5b5984fdfefe3d7ba0ac1235',
                    '5b5984fdfefe3d7ba0ac1236',
                ],
            ),
        ),
        (
            {
                'query': {
                    'park': {'id': ['123']},
                    'legal_entity': {
                        'id': ['5b5984fdfefe3d7ba0ac1234'],
                        'registration_number': ['10'],
                    },
                },
            },
            make_response([]),
        ),
        (
            {'query': {'park': {'id': ['456']}}},
            make_response(['5b5984fdfefe3d7ba0ac1237']),
        ),
        (
            {'query': {'park': {'id': ['123', '456']}}},
            make_response(
                [
                    '5b5984fdfefe3d7ba0ac1234',
                    '5b5984fdfefe3d7ba0ac1235',
                    '5b5984fdfefe3d7ba0ac1236',
                    '5b5984fdfefe3d7ba0ac1237',
                ],
            ),
        ),
        (
            {
                'query': {
                    'legal_entity': {
                        'id': [
                            '5b5984fdfefe3d7ba0ac1234',
                            '5b5984fdfefe3d7ba0ac1237',
                        ],
                    },
                },
            },
            make_response(
                ['5b5984fdfefe3d7ba0ac1234', '5b5984fdfefe3d7ba0ac1237'],
            ),
        ),
        (
            {
                'query': {
                    'park': {'id': ['123', '456']},
                    'legal_entity': {
                        'id': [
                            '5b5984fdfefe3d7ba0ac1234',
                            '5b5984fdfefe3d7ba0ac1237',
                        ],
                    },
                },
            },
            make_response(
                ['5b5984fdfefe3d7ba0ac1234', '5b5984fdfefe3d7ba0ac1237'],
            ),
        ),
        (
            {'query': {'legal_entity': {'registration_number': ['20']}}},
            make_response(
                ['5b5984fdfefe3d7ba0ac1236', '5b5984fdfefe3d7ba0ac1237'],
            ),
        ),
        (
            {'offset': 3, 'query': {'park': {'id': ['123', '456']}}},
            make_response(['5b5984fdfefe3d7ba0ac1237']),
        ),
        (
            {
                'limit': 1,
                'offset': 2,
                'query': {'park': {'id': ['123', '456']}},
            },
            make_response(['5b5984fdfefe3d7ba0ac1236'], True),
        ),
        (
            {
                'limit': 10,
                'offset': 0,
                'query': {'park': {'id': ['123', '456']}},
            },
            make_response(
                [
                    '5b5984fdfefe3d7ba0ac1234',
                    '5b5984fdfefe3d7ba0ac1235',
                    '5b5984fdfefe3d7ba0ac1236',
                    '5b5984fdfefe3d7ba0ac1237',
                ],
            ),
        ),
        (
            {
                'limit': 1,
                'offset': 4,
                'query': {'park': {'id': ['123', '456']}},
            },
            make_response([]),
        ),
        (
            {
                'query': {
                    'park': {'id': ['123']},
                    'legal_entity': {'id': ['invalid_id']},
                },
            },
            make_response([]),
        ),
    ],
)
def test_ok(taxi_parks, list_request, expected_response):
    response = taxi_parks.post(
        '/legal-entities/list', data=json.dumps(list_request),
    )

    assert response.status_code == 200, response.text
    if 'limit' not in list_request:
        expected_response.pop('has_more', None)

    # response is sorted in order of creation
    assert response.json() == expected_response


def test_empty_request(taxi_parks):
    response = taxi_parks.post(
        '/legal-entities/list', data=json.dumps({'query': {}}),
    )

    assert response.status_code == 400
    assert response.json() == {
        'error': {
            'text': (
                'at least one of park.id, legal_entity.id, '
                'legal_entity.registration_number must be '
                'present in query'
            ),
        },
    }
