import pytest

from tests_fleet_offers import utils

ENDPOINT = '/fleet/offers/v1/signers/by-id/offers/list'


def build_params(signer_id):
    return {'id': signer_id}


def build_payload(cursor=None, limit=None):
    payload = {}
    if cursor is not None:
        payload['cursor'] = cursor
    if limit is not None:
        payload['limit'] = limit
    return payload


OK_PARAMS = [
    (
        'driver1',
        None,
        None,
        {
            'offers': [
                {
                    'id': '00000000-0000-0000-0000-000000000003',
                    'kind': 'offer',
                    'name': 'offer3',
                    'number': 10,
                    'rev': 1,
                    'signed_at': '2020-02-29T21:00:00+00:00',
                },
                {
                    'id': '00000000-0000-0000-0000-000000000002',
                    'kind': 'offer',
                    'name': 'offer2',
                    'number': 10,
                    'rev': 0,
                    'signed_at': '2020-01-31T21:00:00+00:00',
                },
                {
                    'id': '00000000-0000-0000-0000-000000000001',
                    'kind': 'offer',
                    'name': 'offer1',
                    'number': 10,
                    'rev': 0,
                    'signed_at': '2019-12-31T21:00:00+00:00',
                },
            ],
        },
    ),
    (
        'driver1',
        None,
        1,
        {
            'offers': [
                {
                    'id': '00000000-0000-0000-0000-000000000003',
                    'kind': 'offer',
                    'name': 'offer3',
                    'number': 10,
                    'rev': 1,
                    'signed_at': '2020-02-29T21:00:00+00:00',
                },
            ],
            'cursor': (
                'eyJzaWduZWRfYXQiOiIyMDIwLTAxLTMxVDIxOjAwOj'
                'AwKzAwOjAwIiwib2ZmZXJfaWQiOiIwMDAwMDAwMC0w'
                'MDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDIifQ=='
            ),
        },
    ),
    (
        'driver1',
        'eyJzaWduZWRfYXQiOiIyMDIwLTAxLTMxVDIxOjAwOj'
        'AwKzAwOjAwIiwib2ZmZXJfaWQiOiIwMDAwMDAwMC0w'
        'MDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDIifQ==',
        10,
        {
            'offers': [
                {
                    'id': '00000000-0000-0000-0000-000000000002',
                    'kind': 'offer',
                    'name': 'offer2',
                    'number': 10,
                    'rev': 0,
                    'signed_at': '2020-01-31T21:00:00+00:00',
                },
                {
                    'id': '00000000-0000-0000-0000-000000000001',
                    'kind': 'offer',
                    'name': 'offer1',
                    'number': 10,
                    'rev': 0,
                    'signed_at': '2019-12-31T21:00:00+00:00',
                },
            ],
        },
    ),
    ('driver99', None, None, {'offers': []}),
]


@pytest.mark.parametrize(
    'client_id, cursor, limit, expected_response', OK_PARAMS,
)
async def test_ok(
        taxi_fleet_offers, client_id, cursor, limit, expected_response,
):

    response = await taxi_fleet_offers.post(
        ENDPOINT,
        headers=utils.build_fleet_headers(park_id='park1'),
        params=build_params(client_id),
        json=build_payload(cursor, limit),
    )

    assert response.status_code == 200, response.text
    assert response.json() == expected_response
