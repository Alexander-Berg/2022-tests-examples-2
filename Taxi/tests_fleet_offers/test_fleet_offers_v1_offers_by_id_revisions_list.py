import pytest

from tests_fleet_offers import utils

ENDPOINT = '/fleet/offers/v1/offers/by-id/revisions/list'


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
        {
            'revisions': [
                {'published_at': '2020-03-01T09:00:00+00:00', 'rev': 2},
                {
                    'published_at': '2020-02-01T09:00:00+00:00',
                    'published_till': '2020-03-01T09:00:00+00:00',
                    'rev': 1,
                },
                {
                    'published_at': '2020-01-01T09:00:00+00:00',
                    'published_till': '2020-02-01T09:00:00+00:00',
                    'rev': 0,
                },
            ],
        },
    ),
    (
        '00000000-0000-0000-0000-000000000001',
        None,
        1,
        {
            'cursor': '2',
            'revisions': [
                {'published_at': '2020-03-01T09:00:00+00:00', 'rev': 2},
            ],
        },
    ),
    (
        '00000000-0000-0000-0000-000000000001',
        '2',
        None,
        {
            'revisions': [
                {
                    'published_at': '2020-02-01T09:00:00+00:00',
                    'published_till': '2020-03-01T09:00:00+00:00',
                    'rev': 1,
                },
                {
                    'published_at': '2020-01-01T09:00:00+00:00',
                    'published_till': '2020-02-01T09:00:00+00:00',
                    'rev': 0,
                },
            ],
        },
    ),
    (
        '00000000-0000-0000-0000-000000000001',
        '2',
        1,
        {
            'cursor': '1',
            'revisions': [
                {
                    'published_at': '2020-02-01T09:00:00+00:00',
                    'published_till': '2020-03-01T09:00:00+00:00',
                    'rev': 1,
                },
            ],
        },
    ),
    ('00000000-0000-0000-0000-100000000001', None, None, {'revisions': []}),
]


@pytest.mark.parametrize(
    'offer_id, cursor, limit, expected_response', OK_PARAMS,
)
async def test_ok(
        taxi_fleet_offers, offer_id, cursor, limit, expected_response,
):
    response = await taxi_fleet_offers.post(
        ENDPOINT,
        headers=utils.build_fleet_headers(park_id='park1'),
        params=build_params(offer_id),
        json=build_payload(cursor=cursor, limit=limit),
    )

    assert response.status_code == 200, response.text
    assert response.json() == expected_response
