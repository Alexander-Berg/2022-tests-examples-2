import pytest

from tests_fleet_offers import utils

ENDPOINT = '/fleet/offers/v1/offers/by-id/signers/list'

MOCK_RESPONSE = {
    'profiles': [
        {
            'data': {
                'full_name': {
                    'first_name': 'Александр',
                    'middle_name': 'Александрович',
                    'last_name': 'Александров',
                },
                'uuid': 'driver1',
            },
            'park_driver_profile_id': 'park1_driver1',
        },
        {
            'data': {
                'full_name': {
                    'first_name': 'Борис',
                    'middle_name': 'Борисович',
                    'last_name': 'Борисов',
                },
                'uuid': 'driver2',
            },
            'park_driver_profile_id': 'park1_driver2',
        },
        {
            'data': {
                'full_name': {'first_name': 'John', 'last_name': 'Smith'},
                'uuid': 'driver3',
            },
            'park_driver_profile_id': 'park1_driver3',
        },
        {
            'data': {'uuid': 'driver4'},
            'park_driver_profile_id': 'park1_driver4',
        },
    ],
}


def build_params(offer_id):
    return {'id': offer_id}


def build_payload(cursor=None, limit=None):
    payload = {}
    if cursor is not None:
        payload['cursor'] = cursor
    if limit is not None:
        payload['limit'] = limit
    return payload


OK_PARAMS = [
    (
        '00000000-0000-0000-0000-000000000001',
        None,
        None,
        1,
        {
            'signers': [
                {
                    'signed_at': '2020-04-30T21:00:00+00:00',
                    'id': 'driver5',
                    'name': {'first': '', 'last': '', 'middle': ''},
                    'number': 5,
                },
                {
                    'signed_at': '2020-03-31T21:00:00+00:00',
                    'id': 'driver4',
                    'name': {'first': '', 'last': '', 'middle': ''},
                    'number': 4,
                },
                {
                    'signed_at': '2020-02-29T21:00:00+00:00',
                    'id': 'driver3',
                    'name': {'first': 'John', 'last': 'Smith', 'middle': ''},
                    'number': 3,
                },
                {
                    'signed_at': '2020-01-31T21:00:00+00:00',
                    'id': 'driver2',
                    'name': {
                        'first': 'Борис',
                        'last': 'Борисов',
                        'middle': 'Борисович',
                    },
                    'number': 2,
                },
                {
                    'signed_at': '2019-12-31T21:00:00+00:00',
                    'id': 'driver1',
                    'name': {
                        'first': 'Александр',
                        'last': 'Александров',
                        'middle': 'Александрович',
                    },
                    'number': 1,
                },
            ],
        },
    ),
    (
        '00000000-0000-0000-0000-000000000001',
        None,
        1,
        1,
        {
            'signers': [
                {
                    'signed_at': '2020-04-30T21:00:00+00:00',
                    'id': 'driver5',
                    'name': {'first': '', 'last': '', 'middle': ''},
                    'number': 5,
                },
            ],
            'cursor': (
                'eyJzaWduZWRfYXQiOiIyMDIwLTAzLTMxVDIxOjAwOj'
                'AwKzAwOjAwIiwic2lnbmVyX2lkIjoiZHJpdmVyNCJ9'
            ),
        },
    ),
    (
        '00000000-0000-0000-0000-000000000001',
        'eyJzaWduZWRfYXQiOiIyMDIwLTAzLTMxVDIxOjAwOj'
        'AwKzAwOjAwIiwic2lnbmVyX2lkIjoiZHJpdmVyNCJ9',
        4,
        1,
        {
            'signers': [
                {
                    'signed_at': '2020-03-31T21:00:00+00:00',
                    'id': 'driver4',
                    'name': {'first': '', 'last': '', 'middle': ''},
                    'number': 4,
                },
                {
                    'signed_at': '2020-02-29T21:00:00+00:00',
                    'id': 'driver3',
                    'name': {'first': 'John', 'last': 'Smith', 'middle': ''},
                    'number': 3,
                },
                {
                    'signed_at': '2020-01-31T21:00:00+00:00',
                    'id': 'driver2',
                    'name': {
                        'first': 'Борис',
                        'last': 'Борисов',
                        'middle': 'Борисович',
                    },
                    'number': 2,
                },
                {
                    'signed_at': '2019-12-31T21:00:00+00:00',
                    'id': 'driver1',
                    'name': {
                        'first': 'Александр',
                        'last': 'Александров',
                        'middle': 'Александрович',
                    },
                    'number': 1,
                },
            ],
        },
    ),
    ('00000000-0000-0000-0000-000000000002', None, None, 0, {'signers': []}),
]


@pytest.mark.parametrize(
    'offer_id, cursor, limit, mock_calls, expected_response', OK_PARAMS,
)
async def test_ok(
        taxi_fleet_offers,
        mockserver,
        offer_id,
        cursor,
        limit,
        mock_calls,
        expected_response,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def mock_driver_profiles(request):
        return MOCK_RESPONSE

    response = await taxi_fleet_offers.post(
        ENDPOINT,
        headers=utils.build_fleet_headers(park_id='park1'),
        params=build_params(offer_id),
        json=build_payload(cursor, limit),
    )

    assert response.status_code == 200, response.text
    assert response.json() == expected_response

    assert mock_driver_profiles.times_called == mock_calls
