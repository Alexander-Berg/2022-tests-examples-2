import datetime

import pytest
import pytz

from tests_grocery_offers import tests_headers


_DEFAULT_TTL = datetime.timedelta(minutes=10)
_SHORT_TTL = datetime.timedelta(minutes=5)


@pytest.mark.parametrize(
    'ttl, check_params, good_offer_id, expected_matched, expected_reason,'
    'expect_body',
    [
        (
            _DEFAULT_TTL,
            {'position': '35;57', 'depot_id': '1'},
            True,
            True,
            None,
            True,
        ),
        (
            _DEFAULT_TTL,
            {'depot_id': '1', 'position': '35;57'},
            True,
            True,
            None,
            True,
        ),
        (
            _DEFAULT_TTL,
            {'position': '57;35', 'depot_id': '1'},
            True,
            False,
            'PARAMS_NOT_MATCHING',
            True,
        ),
        (
            _SHORT_TTL,
            {'position': '35;57', 'depot_id': '1'},
            True,
            False,
            'OFFER_EXPIRED',
            True,
        ),
        (
            _SHORT_TTL,
            {'position': '57;35', 'depot_id': '1'},
            True,
            False,
            'PARAMS_NOT_MATCHING',
            True,
        ),
        (
            _DEFAULT_TTL,
            {'position': '35;57', 'depot_id': '1'},
            False,
            False,
            'OFFER_NOT_FOUND',
            False,
        ),
    ],
)
async def test_basic(
        taxi_grocery_offers,
        ttl,
        check_params,
        good_offer_id,
        expected_matched,
        expected_reason,
        expect_body,
        now,
        pgsql,
        mocked_time,
):
    tag = 'lavka:0x33ed'
    now = now.replace(tzinfo=pytz.UTC)
    create_params = {'depot_id': '1', 'position': '35;57'}
    create_payload = {'surge': 3.5}
    create_response = await taxi_grocery_offers.post(
        '/v1/create',
        headers=tests_headers.HEADERS,
        json={
            'tag': tag,
            'due': (now + ttl).isoformat(),
            'params': create_params,
            'payload': create_payload,
        },
    )
    assert create_response.status_code == 200
    if good_offer_id:
        offer_id = create_response.json()['id']

        cursor = pgsql['grocery_offers'].cursor()
        cursor.execute(
            'SELECT due FROM offers.offers where offer_id = %s', [offer_id],
        )
        offers = list(cursor)
        offer = offers[0]
        assert offer[0] >= now, offer[0]

    else:
        offer_id = create_response.json()['id'] + '111'

    mocked_time.sleep(7 * 60)
    await taxi_grocery_offers.invalidate_caches()

    match_response = await taxi_grocery_offers.post(
        '/v1/match',
        headers={**{'Date': now.isoformat()}, **tests_headers.HEADERS},
        json={'tag': tag, 'id': offer_id, 'params': check_params},
    )
    assert match_response.status_code == 200
    match_response = match_response.json()
    assert match_response['matched'] is expected_matched, match_response
    if expected_reason is not None:
        assert match_response['not_matched_reason'] == expected_reason
    else:
        assert 'not_matched_reason' not in match_response

    if expect_body:
        assert match_response['offer_params'] == create_params
        assert match_response['payload'] == create_payload
    else:
        assert 'offer_params' not in match_response
        assert 'payload' not in match_response


@pytest.mark.parametrize(
    'ttl, check_params, expected_matched, expected_reason,' 'expect_body',
    [
        (_DEFAULT_TTL, {'point': [35, 57], 'lavka': 1}, True, None, True),
        (_DEFAULT_TTL, {'lavka': 1, 'point': [35, 57]}, True, None, True),
        (
            _DEFAULT_TTL,
            {'point': [57, 35], 'lavka': 1},
            False,
            'OFFER_NOT_FOUND',
            False,
        ),
        (
            _SHORT_TTL,
            {'point': [35, 57], 'lavka': 1},
            False,
            'OFFER_EXPIRED',
            True,
        ),
        (
            _SHORT_TTL,
            {'point': [57, 35], 'lavka': 1},
            False,
            'OFFER_NOT_FOUND',
            False,
        ),
    ],
)
async def test_match_by_params(
        taxi_grocery_offers,
        ttl,
        check_params,
        expected_matched,
        expected_reason,
        expect_body,
        now,
        pgsql,
        mocked_time,
):
    tag = 'lavka:0x33ed'
    now = now.replace(tzinfo=pytz.UTC)
    create_params = {'lavka': 1, 'point': [35, 57]}
    create_payload = {'surge': 3.5}
    create_response = await taxi_grocery_offers.post(
        '/v1/create',
        headers=tests_headers.HEADERS,
        json={
            'tag': tag,
            'due': (now + ttl).isoformat(),
            'params': create_params,
            'payload': create_payload,
        },
    )
    assert create_response.status_code == 200
    offer_id = create_response.json()['id']

    cursor = pgsql['grocery_offers'].cursor()
    cursor.execute(
        'SELECT due FROM offers.offers where offer_id = %s', [offer_id],
    )
    offers = list(cursor)
    offer = offers[0]
    assert offer[0] >= now, offer[0]

    mocked_time.sleep(7 * 60)
    await taxi_grocery_offers.invalidate_caches()

    match_response = await taxi_grocery_offers.post(
        '/v1/match',
        headers={**{'Date': now.isoformat()}, **tests_headers.HEADERS},
        json={'tag': tag, 'params': check_params},
    )
    assert match_response.status_code == 200
    match_response = match_response.json()
    assert match_response['matched'] is expected_matched, match_response
    if expected_reason is not None:
        assert match_response['not_matched_reason'] == expected_reason
    else:
        assert 'not_matched_reason' not in match_response

    if expect_body:
        assert match_response['offer_params'] == create_params
        assert match_response['payload'] == create_payload
    else:
        assert 'offer_params' not in match_response
        assert 'payload' not in match_response
