import datetime
import json

import pytest
import pytz

DEFAULT_PARAMS = {'param_1': 'value_1', 'param_2': 'value_2'}
DEFAULT_TTL = datetime.timedelta(hours=1)
DEFAULT_OFFER_ID = 'default-offer-id'
DEFAULT_PAYLOAD = {'some_arg': 'some_value'}
DEFAULT_TAG = 'grocery:catalog'


@pytest.mark.parametrize(
    'sleep_time, params, offer_id, expected_matched, expected_reason',
    [
        (
            DEFAULT_TTL.seconds // 2,
            DEFAULT_PARAMS,
            DEFAULT_OFFER_ID,
            True,
            None,
        ),
        (DEFAULT_TTL.seconds // 2, DEFAULT_PARAMS, None, True, None),
        (
            DEFAULT_TTL.seconds // 2,
            {'other_param': 'other_value'},
            DEFAULT_OFFER_ID,
            False,
            'PARAMS_NOT_MATCHING',
        ),
        (
            DEFAULT_TTL.seconds + 1,
            DEFAULT_PARAMS,
            DEFAULT_OFFER_ID,
            False,
            'OFFER_EXPIRED',
        ),
        (
            DEFAULT_TTL.seconds // 2,
            DEFAULT_PARAMS,
            'offer-id-not-found',
            False,
            'OFFER_NOT_FOUND',
        ),
    ],
)
async def test_match_create(
        taxi_grocery_offers,
        sleep_time,
        params,
        offer_id,
        expected_matched,
        expected_reason,
        now,
        pgsql,
        mocked_time,
):
    """
    Test /internal/v1/offers/v1/match-create should match offer
    by id or by param. If match fails - new offer should be created
    """
    now = now.replace(tzinfo=pytz.UTC)
    due = now + DEFAULT_TTL
    _insert_offer(pgsql, now, due)

    mocked_time.sleep(sleep_time)

    new_due = now + DEFAULT_TTL
    new_payload = {'some_other_arg': 'some_other_value'}
    request = {
        'tag': DEFAULT_TAG,
        'params': params,
        'payload': new_payload,
        'due': new_due.isoformat(),
    }
    if offer_id is not None:
        request['current_id'] = offer_id

    response = await taxi_grocery_offers.post(
        '/internal/v1/offers/v1/match-create', json=request,
    )

    expected_response = {'matched': expected_matched, 'params': params}

    if expected_matched:
        expected_response['id'] = DEFAULT_OFFER_ID
        expected_response['payload'] = DEFAULT_PAYLOAD
    else:
        expected_response['payload'] = new_payload
        expected_response['not_matched_reason'] = expected_reason

        cursor = pgsql['grocery_offers'].cursor()
        cursor.execute(
            f"""SELECT offer_id, created, due, tag, params, payload
            FROM offers.offers WHERE offer_id <> '{DEFAULT_OFFER_ID}'""",
        )
        offers = list(cursor)
        assert len(offers) == 1
        offer = offers[0]
        assert offer[1] >= now
        assert offer[2] == new_due
        assert offer[3] == DEFAULT_TAG
        assert offer[4] == params
        assert offer[5] == new_payload

        expected_response['id'] = offer[0]

    assert response.status_code == 200
    assert response.json() == expected_response


def _insert_offer(pgsql, now, due):
    cursor = pgsql['grocery_offers'].cursor()
    cursor.execute(
        f"""INSERT INTO offers.offers (offer_id, created, due, tag, params, payload)
        VALUES ('{DEFAULT_OFFER_ID}', '{now.isoformat()}', '{due.isoformat()}',
        '{DEFAULT_TAG}', '{json.dumps(DEFAULT_PARAMS)}',
        '{json.dumps(DEFAULT_PAYLOAD)}' );
        """,
    )
