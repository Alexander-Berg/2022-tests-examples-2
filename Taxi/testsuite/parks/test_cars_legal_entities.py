import pytest

from taxi_tests.utils import ordered_object

from . import error


ENDPOINT_URL = '/cars/legal-entities'


@pytest.mark.config(PARKS_LEGAL_ENTITY_SUPPORTED_COUNTRIES=['rus'])
@pytest.mark.parametrize(
    'params, default_work_hours, expected_response',
    [
        (
            {'park_id': 'ok', 'car_id': '1'},
            False,
            {
                'legal_entities': [
                    {
                        'registration_number': '1',
                        'name': 'Ivanov',
                        'address': 'Msk',
                        'work_hours': '11-13',
                        'entity_id': '5b5984fdfefe3d7ba0ac1234',
                        'type': 'carrier_permit_owner',
                        'legal_type': 'legal',
                    },
                    {
                        'registration_number': '1234-ab-45',
                        'name': 'Organization',
                        'address': 'Street',
                        'work_hours': '9-18',
                        'entity_id': 'ok',
                        'type': 'park',
                    },
                ],
            },
        ),
        (
            {'park_id': 'ok', 'car_id': '1'},
            True,
            {
                'legal_entities': [
                    {
                        'registration_number': '1',
                        'name': 'Ivanov',
                        'address': 'Msk',
                        'work_hours': '9-18',
                        'entity_id': '5b5984fdfefe3d7ba0ac1234',
                        'type': 'carrier_permit_owner',
                        'legal_type': 'legal',
                    },
                    {
                        'registration_number': '1234-ab-45',
                        'name': 'Organization',
                        'address': 'Street',
                        'work_hours': '9-18',
                        'entity_id': 'ok',
                        'type': 'park',
                    },
                ],
            },
        ),
        (
            {'park_id': 'ok', 'car_id': '2'},
            False,
            {
                'legal_entities': [
                    {
                        'registration_number': '1234-ab-45',
                        'name': 'Organization',
                        'address': 'Street',
                        'work_hours': '9-18',
                        'entity_id': 'ok',
                        'type': 'park',
                    },
                ],
            },
        ),
        (
            {'park_id': 'ok', 'car_id': 'net_takogo'},
            False,
            {
                'legal_entities': [
                    {
                        'registration_number': '1234-ab-45',
                        'name': 'Organization',
                        'address': 'Street',
                        'work_hours': '9-18',
                        'entity_id': 'ok',
                        'type': 'park',
                    },
                ],
            },
        ),
        (
            {'park_id': 'not_all_fields', 'car_id': '2'},
            False,
            {
                'legal_entities': [
                    {
                        'registration_number': '1234-ab-45',
                        'address': 'Street',
                        'work_hours': '9-18',
                        'entity_id': 'not_all_fields',
                        'type': 'park',
                    },
                ],
            },
        ),
        (
            {'park_id': 'net_clid', 'car_id': '5'},
            False,
            {'legal_entities': []},
        ),
        (
            {'park_id': 'empty_clid', 'car_id': '6'},
            False,
            {'legal_entities': []},
        ),
        (
            {'park_id': 'no_such_clid', 'car_id': '11'},
            False,
            {'legal_entities': []},
        ),
        (
            {'park_id': 'ok', 'car_id': 'no_such_legal_entity'},
            False,
            {
                'legal_entities': [
                    {
                        'registration_number': '1234-ab-45',
                        'name': 'Organization',
                        'address': 'Street',
                        'work_hours': '9-18',
                        'entity_id': 'ok',
                        'type': 'park',
                    },
                ],
            },
        ),
        (
            {'park_id': 'no_account', 'car_id': '8'},
            False,
            {
                'legal_entities': [
                    {
                        'work_hours': '9-18',
                        'entity_id': 'no_account',
                        'type': 'park',
                    },
                ],
            },
        ),
        (
            {'park_id': 'no_account_details', 'car_id': '9'},
            False,
            {
                'legal_entities': [
                    {
                        'work_hours': '9-18',
                        'entity_id': 'no_account_details',
                        'type': 'park',
                    },
                ],
            },
        ),
        (
            {'park_id': 'no_such_clid', 'car_id': 'with_carrier'},
            False,
            {
                'legal_entities': [
                    {
                        'registration_number': '1',
                        'name': 'Ivanov',
                        'address': 'Msk',
                        'work_hours': '11-13',
                        'entity_id': '5b5984fdfefe3d7ba0ac1235',
                        'type': 'carrier_permit_owner',
                        'legal_type': 'legal',
                    },
                ],
            },
        ),
    ],
)
def test_ok(taxi_parks, config, params, default_work_hours, expected_response):
    config.set_values(
        dict(PARKS_USE_PARK_DEFAULT_WORK_HOURS=default_work_hours),
    )

    response = taxi_parks.post(ENDPOINT_URL, params=params)

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(), expected_response, ['legal_entities'],
    )


def test_bad_request(taxi_parks):
    response = taxi_parks.post(
        ENDPOINT_URL, params={'park_id': 'net_takogo', 'car_id': '4'},
    )

    assert response.status_code == 404, response.text
    assert response.json() == error.make_error_response(
        'park with id `net_takogo` not found',
    )
