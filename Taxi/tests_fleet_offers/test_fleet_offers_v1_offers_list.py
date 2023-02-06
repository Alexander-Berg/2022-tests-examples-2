import pytest

from tests_fleet_offers import utils

ENDPOINT = '/fleet/offers/v1/offers/list'


def build_payload(cursor=None, limit=None):
    payload = {}
    if cursor is not None:
        payload['cursor'] = cursor
    if limit is not None:
        payload['limit'] = limit
    return payload


OK_PARAMS = [
    (
        'park1',
        None,
        None,
        {
            'offers': [
                {
                    'created_at': '2020-01-04T21:00:00+00:00',
                    'id': '00000000-0000-0000-0000-000000000005',
                    'is_enabled': True,
                    'kind': 'custom',
                    'name': 'offer5',
                    'rev': 0,
                    'signers_count': 0,
                },
                {
                    'created_at': '2020-01-03T21:00:00+00:00',
                    'id': '00000000-0000-0000-0000-000000000004',
                    'is_enabled': True,
                    'kind': 'offer',
                    'name': 'offer4',
                    'rev': 1,
                    'signers_count': 0,
                },
                {
                    'created_at': '2020-01-01T21:00:00+00:00',
                    'id': '00000000-0000-0000-0000-000000000002',
                    'is_enabled': True,
                    'kind': 'offer',
                    'name': 'offer2',
                    'rev': 2,
                    'signers_count': 1,
                },
                {
                    'created_at': '2019-12-31T21:00:00+00:00',
                    'id': '00000000-0000-0000-0000-000000000001',
                    'is_enabled': True,
                    'kind': 'offer',
                    'name': 'offer1',
                    'rev': 0,
                    'signers_count': 1,
                },
                {
                    'created_at': '2020-01-02T21:00:00+00:00',
                    'id': '00000000-0000-0000-0000-000000000003',
                    'is_enabled': False,
                    'kind': 'offer',
                    'name': 'offer3',
                    'rev': 0,
                    'signers_count': 0,
                },
            ],
        },
    ),
    (
        'park1',
        None,
        1,
        {
            'cursor': (
                'eyJpc19lbmFibGVkIjp0cnVlLCJwdWJsaXNoZWR'
                'fYXQiOiIyMDIwLTAxLTAzVDIxOjAwOjAwKzAwOjAwIn0='
            ),
            'offers': [
                {
                    'created_at': '2020-01-04T21:00:00+00:00',
                    'id': '00000000-0000-0000-0000-000000000005',
                    'is_enabled': True,
                    'kind': 'custom',
                    'name': 'offer5',
                    'rev': 0,
                    'signers_count': 0,
                },
            ],
        },
    ),
    (
        'park1',
        'eyJpc19lbmFibGVkIjp0cnVlLCJwdWJsaXNoZWRfYXQ'
        'iOiIyMDIwLTAxLTAzVDIxOjAwOjAwKzAwOjAwIn0=',
        None,
        {
            'offers': [
                {
                    'created_at': '2020-01-03T21:00:00+00:00',
                    'id': '00000000-0000-0000-0000-000000000004',
                    'is_enabled': True,
                    'kind': 'offer',
                    'name': 'offer4',
                    'rev': 1,
                    'signers_count': 0,
                },
                {
                    'created_at': '2020-01-01T21:00:00+00:00',
                    'id': '00000000-0000-0000-0000-000000000002',
                    'is_enabled': True,
                    'kind': 'offer',
                    'name': 'offer2',
                    'rev': 2,
                    'signers_count': 1,
                },
                {
                    'created_at': '2019-12-31T21:00:00+00:00',
                    'id': '00000000-0000-0000-0000-000000000001',
                    'is_enabled': True,
                    'kind': 'offer',
                    'name': 'offer1',
                    'rev': 0,
                    'signers_count': 1,
                },
                {
                    'created_at': '2020-01-02T21:00:00+00:00',
                    'id': '00000000-0000-0000-0000-000000000003',
                    'is_enabled': False,
                    'kind': 'offer',
                    'name': 'offer3',
                    'rev': 0,
                    'signers_count': 0,
                },
            ],
        },
    ),
    (
        'park1',
        'eyJpc19lbmFibGVkIjp0cnVlLCJwdWJsaXNoZWRfYX'
        'QiOiIyMDIwLTAxLTAzVDIxOjAwOjAwKzAwOjAwIn0=',
        1,
        {
            'cursor': (
                'eyJpc19lbmFibGVkIjp0cnVlLCJwdWJsaXNoZWRfYXQiOi'
                'IyMDIwLTAxLTAxVDIxOjAwOjAwKzAwOjAwIn0='
            ),
            'offers': [
                {
                    'created_at': '2020-01-03T21:00:00+00:00',
                    'id': '00000000-0000-0000-0000-000000000004',
                    'is_enabled': True,
                    'kind': 'offer',
                    'name': 'offer4',
                    'rev': 1,
                    'signers_count': 0,
                },
            ],
        },
    ),
    ('park2', None, None, {'offers': []}),
]


@pytest.mark.parametrize(
    'park_id, cursor, limit, expected_response', OK_PARAMS,
)
async def test_ok(
        taxi_fleet_offers, park_id, cursor, limit, expected_response,
):
    response = await taxi_fleet_offers.post(
        ENDPOINT,
        headers=utils.build_fleet_headers(park_id=park_id),
        json=build_payload(cursor, limit),
    )

    assert response.status_code == 200, response.text
    assert response.json() == expected_response
