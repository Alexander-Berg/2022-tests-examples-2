import datetime

import pytz

from tests_grocery_offers import tests_headers


async def test_basic(taxi_grocery_offers, now, pgsql):
    due = now + datetime.timedelta(hours=1)
    tag = 'lavka:0x324236'
    params = {'a': [37, 56], 'lavka': 'chamovniki'}
    payload = {'moloko': {'price': '100', 'currency': 'RUB'}}
    response = await taxi_grocery_offers.post(
        '/v1/create',
        headers=tests_headers.HEADERS,
        json={
            'params': params,
            'payload': payload,
            'tag': tag,
            'due': f'{due.isoformat()}+00:00',
        },
    )
    offer_id = response.json()['id']
    cursor = pgsql['grocery_offers'].cursor()
    cursor.execute(
        """SELECT offer_id, created, due, tag, params, payload
        FROM offers.offers""",
    )
    offers = list(cursor)
    assert len(offers) == 1, offers
    offer = offers[0]
    assert offer[0] == offer_id
    assert _to_utc(offer[1]) >= now, offer[1]
    assert _to_utc(offer[2]) == due, offer[2]
    assert offer[3] == tag
    assert offer[4] == params
    assert offer[5] == payload


async def test_create_multi(taxi_grocery_offers, now, pgsql):
    dues = [
        now + datetime.timedelta(hours=1),
        now + datetime.timedelta(hours=2),
    ]
    offers = [
        {
            'params': {'a': [37, 56], 'lavka': 'chamovniki'},
            'payload': {'moloko': {'price': '100', 'currency': 'RUB'}},
            'tag': 'lavka:0x324236',
            'due': f'{dues[0].isoformat()}+00:00',
        },
        {
            'params': {'b': [1, 1], 'lavka': 'volkova'},
            'payload': {'nemoloko': {'price': '150', 'currency': 'RUB'}},
            'tag': 'lavka:0x123',
            'due': f'{dues[1].isoformat()}+00:00',
        },
    ]

    response = await taxi_grocery_offers.post(
        '/v1/create/multi',
        headers=tests_headers.HEADERS,
        json={'offers': offers},
    )
    offer_ids = response.json()['ids']
    cursor = pgsql['grocery_offers'].cursor()
    cursor.execute(
        """SELECT offer_id, created, due, tag, params, payload
        FROM offers.offers""",
    )
    pg_offers = list(cursor)
    assert len(offers) == len(pg_offers)

    for pg_offer, offer, offer_id, due in zip(
            pg_offers, offers, offer_ids, dues,
    ):
        assert pg_offer[0] == offer_id
        assert _to_utc(pg_offer[1]) >= now
        assert _to_utc(pg_offer[2]) == due
        assert pg_offer[3] == offer['tag']
        assert pg_offer[4] == offer['params']
        assert pg_offer[5] == offer['payload']


def _to_utc(stamp):
    if stamp.tzinfo is not None:
        stamp = stamp.astimezone(pytz.UTC).replace(tzinfo=None)
    return stamp
