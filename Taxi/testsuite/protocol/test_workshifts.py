import datetime
import json

import pytest


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.translations(geoareas={'moscow': {'en': 'Москва'}})
@pytest.mark.config(WORKSHIFTS_BUY_USING_OFFERS_ALLOWED=True)
def test_workshifts(taxi_protocol, db):
    response = taxi_protocol.get(
        '/utils/1.0/workshifts',
        params={
            'clid': '999012',
            'uuid': 'uuidx',
            'db': 'dbidx',
            'version': '8.58 (850)',
            'latitude': '55.733863',
            'longitude': '37.590533',
        },
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )
    assert response.status_code == 200
    content = response.json()

    offer_id = content['offer_id']
    content.pop('offer_id')

    assert content == {
        'available_workshifts': [
            {
                'begin': '2016-02-09T10:35:00+0000',
                'title': 'Москва',
                'currency': 'RUB',
                'duration_hours': 10,
                'home_zone': 'moscow',
                'zones': [{'name': 'moscow', 'title': 'Москва'}],
                'tariffs': [],
                'id': 'shift1',
                'price': '100',
            },
        ],
        'active_workshifts': [
            {
                'id': 'shift2',
                'begin': '2016-12-15T09:35:00+0000',
                'end': '2016-12-16T09:35:00+0000',
                'title': 'Москва',
                'home_zone': 'moscow',
                'zones': [{'name': 'moscow', 'title': 'Москва'}],
                'tariffs': [],
                'price': '1000',
                'currency': 'RUB',
            },
        ],
    }

    workshift_offer = db.workshift_offers.find_one({'_id': offer_id})
    assert workshift_offer == {
        '_id': offer_id,
        'driver_id': '999012_uuidx',
        'home_zone': 'moscow',
        'created': datetime.datetime(2016, 12, 15, 8, 30),
        'due': datetime.datetime(2016, 12, 15, 8, 45),
        'workshifts': [
            {
                'id': 'shift1',
                'price': '100',
                'duration_hours': 10,
                'zones': ['moscow'],
                'tariffs': [],
            },
        ],
    }


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.driver_experiments(
    'workshifts_ab_testing', 'workshifts_ab_testing1',
)
@pytest.mark.filldb(workshift_rules='experiment')
@pytest.mark.translations(geoareas={'moscow': {'en': 'Москва'}})
@pytest.mark.config(WORKSHIFTS_BUY_USING_OFFERS_ALLOWED=True)
def test_workshifts_price_testing(taxi_protocol, db):
    response = taxi_protocol.get(
        '/utils/1.0/workshifts',
        params={
            'clid': '999012',
            'db': 'dbidx',
            'uuid': 'uuid3',
            'version': '8.58 (850)',
            'latitude': '55.733863',
            'longitude': '37.590533',
        },
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )
    assert response.status_code == 200
    content = response.json()

    offer_id = content['offer_id']
    content.pop('offer_id')

    content['available_workshifts'] = sorted(
        content['available_workshifts'], key=lambda x: x['id'],
    )

    expected_content = {
        'available_workshifts': [
            {
                'begin': '2016-02-09T10:35:00+0000',
                'title': 'Москва',
                'currency': 'RUB',
                'duration_hours': 12,
                'home_zone': 'moscow',
                'id': 'shift0',
                'price': '120',
                'zones': [{'name': 'moscow', 'title': 'Москва'}],
                'tariffs': [],
            },
            {
                'begin': '2016-02-09T10:35:00+0000',
                'title': 'Москва',
                'currency': 'RUB',
                'duration_hours': 10,
                'home_zone': 'moscow',
                'id': 'shift1',
                'price': '100',
                'zones': [{'name': 'moscow', 'title': 'Москва'}],
                'tariffs': [],
            },
            {
                'begin': '2016-02-09T10:35:00+0000',
                'title': 'Москва',
                'currency': 'RUB',
                'duration_hours': 20,
                'home_zone': 'moscow',
                'id': 'shift2',
                'price': '200',
                'show_discount_badge': True,
                'discount_conditions': [{'discount_price': '150'}],
                'zones': [{'name': 'moscow', 'title': 'Москва'}],
                'tariffs': [],
            },
            {
                'begin': '2016-02-09T10:35:00+0000',
                'title': 'Москва',
                'currency': 'RUB',
                'duration_hours': 30,
                'home_zone': 'moscow',
                'id': 'shift3',
                'price': '300',
                'show_discount_badge': True,
                'discount_conditions': [{'discount_price': '200'}],
                'zones': [{'name': 'moscow', 'title': 'Москва'}],
                'tariffs': [],
            },
        ],
        'active_workshifts': [
            {
                'id': 'shift3',
                'begin': '2016-12-15T09:35:00+0000',
                'end': '2016-12-16T09:35:00+0000',
                'title': 'Москва',
                'home_zone': 'moscow',
                'price': '1000',
                'currency': 'USD',
                'zones': [{'name': 'moscow', 'title': 'Москва'}],
                'tariffs': [],
            },
        ],
    }
    expected_content['available_workshifts'].sort(key=lambda x: x['id'])

    assert content == expected_content

    workshift_offer = db.workshift_offers.find_one({'_id': offer_id})
    workshift_offer['workshifts'].sort(key=lambda x: x['id'])

    expected_workshift_offer = {
        '_id': offer_id,
        'driver_id': '999012_uuid3',
        'home_zone': 'moscow',
        'created': datetime.datetime(2016, 12, 15, 8, 30),
        'due': datetime.datetime(2016, 12, 15, 8, 45),
        'workshifts': [
            {
                'id': 'shift0',
                'price': '120',
                'duration_hours': 12,
                'zones': ['moscow'],
                'tariffs': [],
            },
            {
                'id': 'shift1',
                'price': '100',
                'duration_hours': 10,
                'zones': ['moscow'],
                'tariffs': [],
            },
            {
                'duration_hours': 20,
                'id': 'shift2',
                'price': '200',
                'zones': ['moscow'],
                'tariffs': [],
            },
            {
                'duration_hours': 30,
                'id': 'shift3',
                'price': '300',
                'zones': ['moscow'],
                'tariffs': [],
            },
        ],
    }
    expected_workshift_offer['workshifts'].sort(key=lambda x: x['id'])
    assert workshift_offer == expected_workshift_offer


@pytest.mark.filldb(workshift_rules='with_title_and_zones')
@pytest.mark.filldb(driver_workshifts='with_title_and_zones')
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.translations(
    taximeter_messages={
        'workshift_rule_title.almaty_moscow': {'en': 'Москва и Алматы'},
    },
    geoareas={'almaty': {'en': 'Алматы'}, 'moscow': {'en': 'Москва'}},
)
@pytest.mark.config(WORKSHIFTS_BUY_USING_OFFERS_ALLOWED=True)
def test_workshifts_with_title_and_zones(taxi_protocol, db):
    # call
    response = taxi_protocol.get(
        '/utils/1.0/workshifts',
        params={
            'clid': '999012',
            'db': 'dbidx',
            'uuid': 'uuidx',
            'version': '8.58 (850)',
            'latitude': '55.733863',
            'longitude': '37.590533',
        },
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )

    # check response
    assert response.status_code == 200
    content = response.json()

    offer_id = content['offer_id']
    content.pop('offer_id')

    assert content == {
        'available_workshifts': [
            {
                'begin': '2016-02-09T10:35:00+0000',
                'title': 'Москва и Алматы',
                'currency': 'RUB',
                'duration_hours': 10,
                'home_zone': 'moscow',
                'zones': [
                    {'name': 'almaty', 'title': 'Алматы'},
                    {'name': 'moscow', 'title': 'Москва'},
                ],
                'tariffs': [],
                'id': 'shift1',
                'price': '100',
            },
        ],
        'active_workshifts': [
            {
                'id': 'shift2',
                'begin': '2016-12-15T09:35:00+0000',
                'end': '2016-12-16T09:35:00+0000',
                'title': 'Москва и Алматы',
                'home_zone': 'moscow',
                'zones': [
                    {'name': 'almaty', 'title': 'Алматы'},
                    {'name': 'moscow', 'title': 'Москва'},
                ],
                'tariffs': [],
                'price': '1000',
                'currency': 'RUB',
            },
        ],
    }

    workshift_offer = db.workshift_offers.find_one({'_id': offer_id})
    assert workshift_offer == {
        '_id': offer_id,
        'driver_id': '999012_uuidx',
        'home_zone': 'moscow',
        'created': datetime.datetime(2016, 12, 15, 8, 30),
        'due': datetime.datetime(2016, 12, 15, 8, 45),
        'workshifts': [
            {
                'id': 'shift1',
                'price': '100',
                'title_key': 'almaty_moscow',
                'duration_hours': 10,
                'zones': ['almaty', 'moscow'],
                'tariffs': [],
            },
        ],
    }


@pytest.mark.filldb(workshift_rules='with_title')
@pytest.mark.filldb(driver_workshifts='with_title')
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.translations(
    taximeter_messages={
        'workshift_rule_title.almaty_moscow': {'en': 'Москва и Алматы'},
    },
    geoareas={'almaty': {'en': 'Алматы'}, 'moscow': {'en': 'Москва'}},
)
@pytest.mark.config(WORKSHIFTS_BUY_USING_OFFERS_ALLOWED=True)
def test_workshifts_with_title(taxi_protocol, db):
    # call
    response = taxi_protocol.get(
        '/utils/1.0/workshifts',
        params={
            'clid': '999012',
            'db': 'dbidx',
            'uuid': 'uuidx',
            'version': '8.58 (850)',
            'latitude': '55.733863',
            'longitude': '37.590533',
        },
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )

    # check response
    assert response.status_code == 200
    content = response.json()

    offer_id = content['offer_id']
    content.pop('offer_id')

    assert content == {
        'available_workshifts': [
            {
                'begin': '2016-02-09T10:35:00+0000',
                'title': 'Москва и Алматы',
                'currency': 'RUB',
                'duration_hours': 10,
                'home_zone': 'moscow',
                'zones': [{'name': 'moscow', 'title': 'Москва'}],
                'tariffs': [],
                'id': 'shift1',
                'price': '100',
            },
        ],
        'active_workshifts': [
            {
                'id': 'shift2',
                'begin': '2016-12-15T09:35:00+0000',
                'end': '2016-12-16T09:35:00+0000',
                'title': 'Москва и Алматы',
                'home_zone': 'moscow',
                'zones': [{'name': 'moscow', 'title': 'Москва'}],
                'tariffs': [],
                'price': '1000',
                'currency': 'RUB',
            },
        ],
    }

    workshift_offer = db.workshift_offers.find_one({'_id': offer_id})
    assert workshift_offer == {
        '_id': offer_id,
        'driver_id': '999012_uuidx',
        'home_zone': 'moscow',
        'created': datetime.datetime(2016, 12, 15, 8, 30),
        'due': datetime.datetime(2016, 12, 15, 8, 45),
        'workshifts': [
            {
                'id': 'shift1',
                'price': '100',
                'title_key': 'almaty_moscow',
                'duration_hours': 10,
                'zones': ['moscow'],
                'tariffs': [],
            },
        ],
    }


@pytest.mark.filldb(workshift_rules='with_zones')
@pytest.mark.filldb(driver_workshifts='with_zones')
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.translations(
    taximeter_messages={
        'workshift_rule_title.almaty_moscow': {'en': 'Москва и Алматы'},
    },
    geoareas={'almaty': {'en': 'Алматы'}, 'moscow': {'en': 'Москва'}},
)
@pytest.mark.config(WORKSHIFTS_BUY_USING_OFFERS_ALLOWED=True)
def test_workshifts_with_zones(taxi_protocol, db):
    # call
    response = taxi_protocol.get(
        '/utils/1.0/workshifts',
        params={
            'clid': '999012',
            'db': 'dbidx',
            'uuid': 'uuidx',
            'version': '8.58 (850)',
            'latitude': '55.733863',
            'longitude': '37.590533',
        },
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )

    # check response
    assert response.status_code == 200
    content = response.json()

    offer_id = content['offer_id']
    content.pop('offer_id')

    assert content == {
        'available_workshifts': [
            {
                'begin': '2016-02-09T10:35:00+0000',
                'title': 'Алматы, Москва',
                'currency': 'RUB',
                'duration_hours': 10,
                'home_zone': 'moscow',
                'zones': [
                    {'name': 'almaty', 'title': 'Алматы'},
                    {'name': 'moscow', 'title': 'Москва'},
                ],
                'tariffs': [],
                'id': 'shift1',
                'price': '100',
            },
        ],
        'active_workshifts': [
            {
                'id': 'shift2',
                'begin': '2016-12-15T09:35:00+0000',
                'end': '2016-12-16T09:35:00+0000',
                'title': 'Алматы, Москва',
                'home_zone': 'moscow',
                'zones': [
                    {'name': 'almaty', 'title': 'Алматы'},
                    {'name': 'moscow', 'title': 'Москва'},
                ],
                'tariffs': [],
                'price': '1000',
                'currency': 'RUB',
            },
        ],
    }

    workshift_offer = db.workshift_offers.find_one({'_id': offer_id})
    assert workshift_offer == {
        '_id': offer_id,
        'driver_id': '999012_uuidx',
        'home_zone': 'moscow',
        'created': datetime.datetime(2016, 12, 15, 8, 30),
        'due': datetime.datetime(2016, 12, 15, 8, 45),
        'workshifts': [
            {
                'id': 'shift1',
                'price': '100',
                'duration_hours': 10,
                'zones': ['almaty', 'moscow'],
                'tariffs': [],
            },
        ],
    }


@pytest.mark.filldb(workshift_rules='with_zone')
@pytest.mark.filldb(driver_workshifts='with_zone')
@pytest.mark.filldb(cities='with_almaty')
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.translations(
    taximeter_messages={
        'workshift_rule_title.almaty_moscow': {'en': 'Москва и Алматы'},
    },
    geoareas={'almaty': {'en': 'Алматы'}, 'moscow': {'en': 'Москва'}},
)
@pytest.mark.config(WORKSHIFTS_BUY_USING_OFFERS_ALLOWED=True)
def test_workshifts_with_zone(taxi_protocol, db):
    # call
    response = taxi_protocol.get(
        '/utils/1.0/workshifts',
        params={
            'clid': '999012',
            'db': 'dbidx',
            'uuid': 'uuidx',
            'version': '8.58 (850)',
            'latitude': '55.733863',
            'longitude': '37.590533',
        },
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )

    # check response
    assert response.status_code == 200
    content = response.json()

    offer_id = content['offer_id']
    content.pop('offer_id')

    assert content == {
        'available_workshifts': [
            {
                'begin': '2016-02-09T10:35:00+0000',
                'title': 'Москва',
                'currency': 'RUB',
                'duration_hours': 10,
                'home_zone': 'almaty',
                'zones': [{'name': 'moscow', 'title': 'Москва'}],
                'tariffs': [],
                'id': 'shift1',
                'price': '100',
            },
        ],
        'active_workshifts': [
            {
                'id': 'shift2',
                'begin': '2016-12-15T09:35:00+0000',
                'end': '2016-12-16T09:35:00+0000',
                'title': 'Алматы',
                'home_zone': 'moscow',
                'zones': [{'name': 'almaty', 'title': 'Алматы'}],
                'tariffs': [],
                'price': '1000',
                'currency': 'RUB',
            },
        ],
    }

    workshift_offer = db.workshift_offers.find_one({'_id': offer_id})
    assert workshift_offer == {
        '_id': offer_id,
        'driver_id': '999012_uuidx',
        'home_zone': 'moscow',
        'created': datetime.datetime(2016, 12, 15, 8, 30),
        'due': datetime.datetime(2016, 12, 15, 8, 45),
        'workshifts': [
            {
                'id': 'shift1',
                'price': '100',
                'duration_hours': 10,
                'zones': ['moscow'],
                'tariffs': [],
            },
        ],
    }


@pytest.mark.filldb(workshift_rules='with_zones')
@pytest.mark.filldb(driver_workshifts='with_zones')
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.translations(geoareas={'almaty': {'en': 'Алматы'}})
@pytest.mark.config(WORKSHIFTS_BUY_USING_OFFERS_ALLOWED=True)
def test_workshifts_with_zones_missed_translations(taxi_protocol, db):
    # call
    response = taxi_protocol.get(
        '/utils/1.0/workshifts',
        params={
            'clid': '999012',
            'db': 'dbidx',
            'uuid': 'uuidx',
            'version': '8.58 (850)',
            'latitude': '55.733863',
            'longitude': '37.590533',
        },
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )

    # check response
    assert response.status_code == 200
    content = response.json()

    offer_id = content['offer_id']
    content.pop('offer_id')

    assert content == {
        'available_workshifts': [
            {
                'begin': '2016-02-09T10:35:00+0000',
                'title': 'moscow, Алматы',
                'currency': 'RUB',
                'duration_hours': 10,
                'home_zone': 'moscow',
                'zones': [
                    {'name': 'almaty', 'title': 'Алматы'},
                    {'name': 'moscow', 'title': 'moscow'},
                ],
                'tariffs': [],
                'id': 'shift1',
                'price': '100',
            },
        ],
        'active_workshifts': [
            {
                'id': 'shift2',
                'begin': '2016-12-15T09:35:00+0000',
                'end': '2016-12-16T09:35:00+0000',
                'title': 'moscow, Алматы',
                'home_zone': 'moscow',
                'zones': [
                    {'name': 'almaty', 'title': 'Алматы'},
                    {'name': 'moscow', 'title': 'moscow'},
                ],
                'tariffs': [],
                'price': '1000',
                'currency': 'RUB',
            },
        ],
    }

    workshift_offer = db.workshift_offers.find_one({'_id': offer_id})
    assert workshift_offer == {
        '_id': offer_id,
        'driver_id': '999012_uuidx',
        'home_zone': 'moscow',
        'created': datetime.datetime(2016, 12, 15, 8, 30),
        'due': datetime.datetime(2016, 12, 15, 8, 45),
        'workshifts': [
            {
                'id': 'shift1',
                'price': '100',
                'duration_hours': 10,
                'zones': ['almaty', 'moscow'],
                'tariffs': [],
            },
        ],
    }


@pytest.mark.filldb(workshift_rules='with_zones')
@pytest.mark.filldb(driver_workshifts='with_zones')
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.translations(geoareas={'moscow': {'en': 'Москва'}})
def test_workshifts_with_zones_missed_translations_emplace_mode(
        taxi_protocol, db,
):
    # call
    response = taxi_protocol.get(
        '/utils/1.0/workshifts',
        params={
            'clid': '999012',
            'db': 'dbidx',
            'uuid': 'uuidx',
            'version': '8.58 (850)',
            'latitude': '55.733863',
            'longitude': '37.590533',
        },
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )

    # check response
    assert response.status_code == 200
    content = response.json()

    assert content == {
        'available_workshifts': [
            {
                'begin': '2016-02-09T10:35:00+0000',
                'title': 'almaty, Москва',
                'currency': 'RUB',
                'duration_hours': 10,
                'home_zone': 'moscow',
                'zones': [
                    {'name': 'almaty', 'title': 'almaty'},
                    {'name': 'moscow', 'title': 'Москва'},
                ],
                'tariffs': [],
                'id': 'shift1',
                'price': '100',
            },
        ],
        'active_workshifts': [
            {
                'id': 'shift2',
                'begin': '2016-12-15T09:35:00+0000',
                'end': '2016-12-16T09:35:00+0000',
                'title': 'almaty, Москва',
                'home_zone': 'moscow',
                'zones': [
                    {'name': 'almaty', 'title': 'almaty'},
                    {'name': 'moscow', 'title': 'Москва'},
                ],
                'tariffs': [],
                'price': '1000',
                'currency': 'RUB',
            },
        ],
    }


@pytest.mark.filldb(workshift_rules='match_multizone_by_not_a_homezone')
@pytest.mark.filldb(driver_workshifts='empty')
@pytest.mark.filldb(cities='with_almaty')
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.translations(
    taximeter_messages={
        'workshift_rule_title.almaty_moscow': {'en': 'Москва и Алматы'},
    },
    geoareas={'almaty': {'en': 'Алматы'}, 'moscow': {'en': 'Москва'}},
)
@pytest.mark.config(WORKSHIFTS_BUY_USING_OFFERS_ALLOWED=True)
def test_workshifts_match_multizone_by_not_a_homezone(taxi_protocol, db):
    # call
    response = taxi_protocol.get(
        '/utils/1.0/workshifts',
        params={
            'clid': '999012',
            'db': 'dbidx',
            'uuid': 'uuidx',
            'version': '8.58 (850)',
            'latitude': '55.733863',
            'longitude': '37.590533',
        },
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )

    # check response
    assert response.status_code == 200
    content = response.json()

    offer_id = content['offer_id']
    content.pop('offer_id')

    assert content == {
        'available_workshifts': [
            {
                'begin': '2016-02-09T10:35:00+0000',
                'title': 'Алматы, Москва',
                'currency': 'RUB',
                'duration_hours': 10,
                'home_zone': 'almaty',
                'zones': [
                    {'name': 'almaty', 'title': 'Алматы'},
                    {'name': 'moscow', 'title': 'Москва'},
                ],
                'tariffs': [],
                'id': 'shift1',
                'price': '100',
            },
        ],
        'active_workshifts': [],
    }

    workshift_offer = db.workshift_offers.find_one({'_id': offer_id})
    assert workshift_offer == {
        '_id': offer_id,
        'driver_id': '999012_uuidx',
        'home_zone': 'moscow',
        'created': datetime.datetime(2016, 12, 15, 8, 30),
        'due': datetime.datetime(2016, 12, 15, 8, 45),
        'workshifts': [
            {
                'id': 'shift1',
                'price': '100',
                'duration_hours': 10,
                'zones': ['almaty', 'moscow'],
                'tariffs': [],
            },
        ],
    }


OLD_TYPE_WORKSHIFT = {
    'begin': '2016-02-09T10:35:00+0000',
    'title': 'Москва',
    'currency': 'RUB',
    'duration_hours': 10,
    'home_zone': 'moscow',
    'id': 'shift1',
    'price': '100',
    'zones': [{'name': 'moscow', 'title': 'Москва'}],
    'tariffs': [],
}


NEW_TYPE_WORKSHIFT_EXP1 = {
    'begin': '2016-02-09T10:35:00+0000',
    'currency': 'RUB',
    'duration_hours': 48,
    'home_zone': 'moscow',
    'id': 'shift2',
    'discount_conditions': [{'discount_price': '1329'}],
    'show_discount_badge': True,
    'price': '1130',
    'title': 'New workshifts',
    'zones': [{'name': 'moscow', 'title': 'Москва'}],
    'tariffs': [],
}


NEW_TYPE_WORKSHIFT_EXP2 = {
    'begin': '2016-02-09T10:35:00+0000',
    'currency': 'RUB',
    'duration_hours': 48,
    'home_zone': 'moscow',
    'id': 'shift2',
    'price': '1130',
    'discount_conditions': [{'discount_price': '1329'}],
    'show_discount_badge': True,
    'title': 'New workshifts',
    'zones': [{'name': 'moscow', 'title': 'Москва'}],
    'tariffs': [],
}


OLD_TYPE_OFFER = {
    'id': 'shift1',
    'price': '100',
    'duration_hours': 10,
    'zones': ['moscow'],
    'tariffs': [],
}


NEW_TYPE_OFFER_EXP1 = {
    'id': 'shift2',
    'price': '1130',
    'title_key': 'with_schedule',
    'hiring_extra_percent': '0.12',
    'duration_hours': 48,
    'zones': ['moscow'],
    'tariffs': [],
}


NEW_TYPE_OFFER_EXP2 = {
    'id': 'shift2',
    'price': '1130',
    'title_key': 'with_schedule',
    'hiring_extra_percent': '0.12',
    'duration_hours': 48,
    'zones': ['moscow'],
    'tariffs': [],
}


@pytest.mark.config(
    FETCH_DRIVER_TAGS_BY_LICENSES_FROM_SERVICE=True,
    WORKSHIFTS_TAGS_ENABLED=True,
    WORKSHIFTS_BUY_USING_OFFERS_ALLOWED=True,
)
@pytest.mark.now('2018-08-20T11:30:00+0300')
@pytest.mark.filldb(workshift_rules='schedule')
@pytest.mark.translations(
    taximeter_messages={
        'workshift_rule_title.with_schedule': {'en': 'New workshifts'},
    },
    geoareas={'moscow': {'en': 'Москва'}},
)
@pytest.mark.parametrize(
    'available,offer,workshifts_with_schedule',
    [
        (
            [OLD_TYPE_WORKSHIFT, NEW_TYPE_WORKSHIFT_EXP1],
            [OLD_TYPE_OFFER, NEW_TYPE_OFFER_EXP1],
            True,
        ),
        ([OLD_TYPE_WORKSHIFT], [OLD_TYPE_OFFER], False),
        (
            [OLD_TYPE_WORKSHIFT, NEW_TYPE_WORKSHIFT_EXP2],
            [OLD_TYPE_OFFER, NEW_TYPE_OFFER_EXP2],
            True,
        ),
    ],
    ids=[
        'with new workshifts',
        'new workshifts is disabled',
        'new workshift with discount',
    ],
)
@pytest.mark.driver_tags_match(
    dbid='dbidx', uuid='uuid4', tags=['show_workshift1', 'show_workshift2'],
)
@pytest.mark.driver_tags_match(
    dbid='test', uuid='tets', tags=['show_workshift-2', 'show_workshift32'],
)
def test_workshifts_price_schedule(
        taxi_protocol, config, db, available, offer, workshifts_with_schedule,
):
    config.set_values(
        dict(WORKSHIFTS_ENABLED_SHIFTS_WITH_SCHEDULE=workshifts_with_schedule),
    )

    response = taxi_protocol.get(
        '/utils/1.0/workshifts',
        params={
            'clid': '999012',
            'db': 'dbidx',
            'uuid': 'uuid4',
            'version': '8.58 (850)',
            'latitude': '55.733863',
            'longitude': '37.590533',
        },
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )
    assert response.status_code == 200
    content = response.json()

    offer_id = content['offer_id']
    content.pop('offer_id')

    content['available_workshifts'] = sorted(
        content['available_workshifts'], key=lambda x: x['id'],
    )

    expected_content = {
        'available_workshifts': available,
        'active_workshifts': [],
    }
    expected_content['available_workshifts'] = sorted(
        expected_content['available_workshifts'], key=lambda x: x['id'],
    )
    assert content == expected_content

    workshift_offer = db.workshift_offers.find_one({'_id': offer_id})
    workshift_offer['workshifts'] = sorted(
        workshift_offer['workshifts'], key=lambda x: x['id'],
    )
    expected_workshift_offer = {
        '_id': offer_id,
        'driver_id': '999012_uuid4',
        'home_zone': 'moscow',
        'created': datetime.datetime(2018, 8, 20, 8, 30),
        'due': datetime.datetime(2018, 8, 20, 8, 45),
        'workshifts': offer,
    }
    expected_workshift_offer['workshifts'] = sorted(
        expected_workshift_offer['workshifts'], key=lambda x: x['id'],
    )
    assert workshift_offer == expected_workshift_offer


@pytest.mark.config(
    FETCH_DRIVER_TAGS_BY_LICENSES_FROM_SERVICE=True,
    WORKSHIFTS_TAGS_ENABLED=True,
    WORKSHIFTS_ENABLED_SHIFTS_WITH_SCHEDULE=True,
    WORKSHIFTS_MIN_TAXIMETER_VERSION_FOR_SHIFTS_WITH_SCHEDULE='8.57',
    WORKSHIFTS_BUY_USING_OFFERS_ALLOWED=True,
)
@pytest.mark.now('2018-08-20T09:30:00+0300')
@pytest.mark.filldb(workshift_rules='schedule')
@pytest.mark.translations(
    taximeter_messages={
        'workshift_rule_title.with_schedule': {'en': 'New workshifts'},
    },
    geoareas={'moscow': {'en': 'Москва'}},
)
@pytest.mark.driver_tags_match(
    dbid='dbidx', uuid='uuid4', tags=['show_workshift0', 'show_workshift1'],
)
def test_workshifts_shcedule_zero_price(taxi_protocol, mockserver, db):
    response = taxi_protocol.get(
        '/utils/1.0/workshifts',
        params={
            'clid': '999012',
            'db': 'dbidx',
            'uuid': 'uuid4',
            'version': '8.58 (850)',
            'latitude': '55.733863',
            'longitude': '37.590533',
        },
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )
    assert response.status_code == 200
    content = response.json()

    offer_id = content['offer_id']
    content.pop('offer_id')

    assert content == {
        'available_workshifts': [OLD_TYPE_WORKSHIFT],
        'active_workshifts': [],
    }

    workshift_offer = db.workshift_offers.find_one({'_id': offer_id})
    assert workshift_offer == {
        '_id': offer_id,
        'driver_id': '999012_uuid4',
        'home_zone': 'moscow',
        'created': datetime.datetime(2018, 8, 20, 6, 30),
        'due': datetime.datetime(2018, 8, 20, 6, 45),
        'workshifts': [OLD_TYPE_OFFER],
    }


@pytest.mark.config(
    FETCH_DRIVER_TAGS_BY_LICENSES_FROM_SERVICE=True,
    WORKSHIFTS_TAGS_ENABLED=True,
    WORKSHIFTS_ENABLED_SHIFTS_WITH_SCHEDULE=True,
    WORKSHIFTS_MIN_TAXIMETER_VERSION_FOR_SHIFTS_WITH_SCHEDULE='8.57',
    WORKSHIFTS_BUY_USING_OFFERS_ALLOWED=True,
    WORKSHIFTS_ENABLED_SHIFTS_WITH_TARIFFS=True,
    WORKSHIFTS_PREFERRED_TARIFFS_ORDER=['econom', 'comfort', 'comfortplus'],
    WORKSHIFTS_MIN_TAXIMETER_VERSION_FOR_SHIFTS_WITH_TARIFFS='8.58',
)
@pytest.mark.now('2018-09-10T09:30:00+0300')
@pytest.mark.filldb(workshift_rules='equal')
@pytest.mark.translations(
    taximeter_messages={
        'workshift_rule_title.with_schedule': {'en': 'New workshifts'},
    },
    geoareas={'moscow': {'en': 'Москва'}, 'minsk': {'en': 'Минск'}},
)
@pytest.mark.driver_tags_match(dbid='dbidx', uuid='uuid4', tags=[])
def test_equal_workshifts(taxi_protocol):
    response = taxi_protocol.get(
        '/utils/1.0/workshifts',
        params={
            'clid': '999012',
            'db': 'dbidx',
            'uuid': 'uuid4',
            'version': '8.58 (850)',
            'latitude': '55.733863',
            'longitude': '37.590533',
        },
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )
    assert response.status_code == 200
    content = response.json()

    content.pop('offer_id')
    content['available_workshifts'] = sorted(
        content['available_workshifts'], key=lambda x: x['id'],
    )

    expected_response = {
        'available_workshifts': [
            {
                'begin': '2018-09-01T10:35:00+0000',
                'end': '2018-10-01T10:35:00+0000',
                'title': 'Москва',
                'currency': 'RUB',
                'duration_hours': 10,
                'home_zone': 'moscow',
                'id': 'shift2',
                'price': '1100',
                'zones': [{'name': 'moscow', 'title': 'Москва'}],
                'tariffs': [],
            },
            {
                'begin': '2018-09-01T10:35:00+0000',
                'end': '2018-10-01T10:35:00+0000',
                'title': 'Минск, Москва',
                'currency': 'RUB',
                'duration_hours': 10,
                'home_zone': 'moscow',
                'id': 'shift4',
                'price': '5.4',
                'zones': [
                    {'name': 'minsk', 'title': 'Минск'},
                    {'name': 'moscow', 'title': 'Москва'},
                ],
                'tariffs': [
                    {'name': 'econom', 'title': 'Econom'},
                    {'name': 'comfortplus', 'title': 'Comfort+'},
                ],
            },
        ],
        'active_workshifts': [],
    }

    expected_response['available_workshifts'] = sorted(
        expected_response['available_workshifts'], key=lambda x: x['id'],
    )
    assert content == expected_response


@pytest.mark.config(
    FETCH_DRIVER_TAGS_BY_LICENSES_FROM_SERVICE=True,
    WORKSHIFTS_TAGS_ENABLED=True,
    WORKSHIFTS_BUY_USING_OFFERS_ALLOWED=True,
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(workshift_rules='match_tags')
@pytest.mark.translations(geoareas={'moscow': {'en': 'Москва'}})
@pytest.mark.parametrize(
    'tags_enabled,clid,db_id,uuid,' 'expected_response,offer',
    [
        (
            True,
            '999012',
            'dbidx',
            'uuid5',
            {
                'available_workshifts': [
                    {
                        'begin': '2016-02-09T10:35:00+0000',
                        'title': 'Москва',
                        'currency': 'RUB',
                        'duration_hours': 30,
                        'home_zone': 'moscow',
                        'id': 'shift0',
                        'price': '300',
                        'zones': [{'name': 'moscow', 'title': 'Москва'}],
                        'tariffs': [],
                    },
                    {
                        'begin': '2016-02-09T10:35:00+0000',
                        'title': 'Москва',
                        'currency': 'RUB',
                        'duration_hours': 24,
                        'home_zone': 'moscow',
                        'id': 'shift1',
                        'price': '250',
                        'zones': [{'name': 'moscow', 'title': 'Москва'}],
                        'tariffs': [],
                    },
                ],
                'active_workshifts': [],
            },
            {
                'driver_id': '999012_uuid5',
                'home_zone': 'moscow',
                'created': datetime.datetime(2016, 12, 15, 8, 30),
                'due': datetime.datetime(2016, 12, 15, 8, 45),
                'workshifts': [
                    {
                        'id': 'shift0',
                        'price': '300',
                        'duration_hours': 30,
                        'zones': ['moscow'],
                        'tariffs': [],
                    },
                    {
                        'id': 'shift1',
                        'price': '250',
                        'duration_hours': 24,
                        'zones': ['moscow'],
                        'tariffs': [],
                    },
                ],
            },
        ),
        (
            False,
            '999012',
            'dbidx',
            'uuid5',
            {
                'available_workshifts': [
                    {
                        'begin': '2016-02-09T10:35:00+0000',
                        'title': 'Москва',
                        'currency': 'RUB',
                        'duration_hours': 24,
                        'home_zone': 'moscow',
                        'id': 'shift1',
                        'price': '250',
                        'zones': [{'name': 'moscow', 'title': 'Москва'}],
                        'tariffs': [],
                    },
                ],
                'active_workshifts': [],
            },
            {
                'driver_id': '999012_uuid5',
                'home_zone': 'moscow',
                'created': datetime.datetime(2016, 12, 15, 8, 30),
                'due': datetime.datetime(2016, 12, 15, 8, 45),
                'workshifts': [
                    {
                        'id': 'shift1',
                        'price': '250',
                        'duration_hours': 24,
                        'zones': ['moscow'],
                        'tariffs': [],
                    },
                ],
            },
        ),
        (
            True,
            '999012',
            'dbidx',
            'uuid6',
            {
                'available_workshifts': [
                    {
                        'begin': '2016-02-09T10:35:00+0000',
                        'title': 'Москва',
                        'currency': 'RUB',
                        'duration_hours': 24,
                        'home_zone': 'moscow',
                        'id': 'shift1',
                        'price': '250',
                        'zones': [{'name': 'moscow', 'title': 'Москва'}],
                        'tariffs': [],
                    },
                ],
                'active_workshifts': [],
            },
            {
                'driver_id': '999012_uuid6',
                'home_zone': 'moscow',
                'created': datetime.datetime(2016, 12, 15, 8, 30),
                'due': datetime.datetime(2016, 12, 15, 8, 45),
                'workshifts': [
                    {
                        'id': 'shift1',
                        'price': '250',
                        'duration_hours': 24,
                        'zones': ['moscow'],
                        'tariffs': [],
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.driver_tags_match(
    dbid='dbidx', uuid='uuid5', tags=['show_workshift0', 'show_workshift1'],
)
def test_workshifts_tags_service(
        taxi_protocol,
        db,
        db_id,
        config,
        tags_enabled,
        clid,
        uuid,
        expected_response,
        offer,
):
    config.set_values(dict(WORKSHIFTS_TAGS_ENABLED=tags_enabled))

    response = taxi_protocol.get(
        '/utils/1.0/workshifts',
        params={
            'clid': clid,
            'db': db_id,
            'uuid': uuid,
            'version': '8.58 (850)',
            'latitude': '55.733863',
            'longitude': '37.590533',
        },
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )
    assert response.status_code == 200
    content = response.json()

    offer_id = content['offer_id']
    content.pop('offer_id')

    content['available_workshifts'] = sorted(
        content['available_workshifts'], key=lambda x: x['id'],
    )
    expected_response['available_workshifts'] = sorted(
        expected_response['available_workshifts'], key=lambda x: x['id'],
    )

    assert content == expected_response

    workshift_offer = db.workshift_offers.find_one({'_id': offer_id})
    workshift_offer.pop('_id')
    workshift_offer['workshifts'] = sorted(
        workshift_offer['workshifts'], key=lambda x: x['id'],
    )
    assert workshift_offer == offer


OFFER_WITH_TARIFF = {
    'id': 'shift0',
    'price': '300',
    'duration_hours': 30,
    'zones': ['moscow'],
    'tariffs': ['econom', 'comfortplus'],
}

OFFER = {
    'id': 'shift1',
    'price': '250',
    'duration_hours': 24,
    'zones': ['moscow'],
    'tariffs': [],
}

OFFER_FOR_OLD_VERSION = {
    'id': 'shift2',
    'price': '350',
    'duration_hours': 48,
    'zones': ['moscow'],
    'tariffs': ['econom'],
}


@pytest.mark.filldb(driver_workshifts='with_tariffs')
@pytest.mark.filldb(workshift_rules='with_tariffs')
@pytest.mark.config(
    WORKSHIFTS_BUY_USING_OFFERS_ALLOWED=True,
    WORKSHIFTS_PREFERRED_TARIFFS_ORDER=['econom', 'comfort', 'comfortplus'],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.translations(geoareas={'moscow': {'en': 'Москва'}})
@pytest.mark.parametrize(
    'clid,db_id,uuid,version,tariffs_enabled,old_tariffs,'
    'expected_response,offer',
    [
        (
            '999012',
            'dbidx',
            'uuid6',
            '8.55',
            True,
            [],
            'expected_response1.json',
            {
                'driver_id': '999012_uuid6',
                'home_zone': 'moscow',
                'created': datetime.datetime(2016, 12, 15, 8, 30),
                'due': datetime.datetime(2016, 12, 15, 8, 45),
                'workshifts': [
                    OFFER_WITH_TARIFF,
                    OFFER,
                    OFFER_FOR_OLD_VERSION,
                ],
            },
        ),
        (
            '999012',
            'dbidx',
            'uuid6',
            '8.55',
            False,
            ['econom'],
            'expected_response2.json',
            {
                'driver_id': '999012_uuid6',
                'home_zone': 'moscow',
                'created': datetime.datetime(2016, 12, 15, 8, 30),
                'due': datetime.datetime(2016, 12, 15, 8, 45),
                'workshifts': [OFFER, OFFER_FOR_OLD_VERSION],
            },
        ),
        (
            '999012',
            'dbidx',
            'uuid6',
            '9.00',
            True,
            ['econom'],
            'expected_response2.json',
            {
                'driver_id': '999012_uuid6',
                'home_zone': 'moscow',
                'created': datetime.datetime(2016, 12, 15, 8, 30),
                'due': datetime.datetime(2016, 12, 15, 8, 45),
                'workshifts': [OFFER, OFFER_FOR_OLD_VERSION],
            },
        ),
        (
            '999012',
            'dbidx',
            'uuid5',
            '8.55',
            True,
            [],
            'expected_response3.json',
            {
                'driver_id': '999012_uuid5',
                'home_zone': 'moscow',
                'created': datetime.datetime(2016, 12, 15, 8, 30),
                'due': datetime.datetime(2016, 12, 15, 8, 45),
                'workshifts': [
                    OFFER_WITH_TARIFF,
                    OFFER,
                    OFFER_FOR_OLD_VERSION,
                ],
            },
        ),
    ],
)
def test_workshifts_with_tariffs(
        taxi_protocol,
        db,
        config,
        load_json,
        clid,
        uuid,
        version,
        tariffs_enabled,
        db_id,
        old_tariffs,
        expected_response,
        offer,
):
    config.set_values(
        dict(
            WORKSHIFTS_MIN_TAXIMETER_VERSION_FOR_SHIFTS_WITH_TARIFFS=version,
            WORKSHIFTS_ENABLED_SHIFTS_WITH_TARIFFS=tariffs_enabled,
            WORKSHIFTS_TARIFFS_FOR_OLD_VERSION=old_tariffs,
        ),
    )

    response = taxi_protocol.get(
        '/utils/1.0/workshifts',
        params={
            'clid': clid,
            'uuid': uuid,
            'db': db_id,
            'version': '8.58 (850)',
            'latitude': '55.733863',
            'longitude': '37.590533',
        },
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )
    assert response.status_code == 200
    content = response.json()

    offer_id = content['offer_id']
    content.pop('offer_id')

    expected_response = load_json('tariffs/' + expected_response)
    content['available_workshifts'] = sorted(
        content['available_workshifts'], key=lambda x: x['id'],
    )
    expected_response['available_workshifts'] = sorted(
        expected_response['available_workshifts'], key=lambda x: x['id'],
    )

    assert content == expected_response

    workshift_offer = db.workshift_offers.find_one({'_id': offer_id})
    workshift_offer.pop('_id')
    workshift_offer['workshifts'] = sorted(
        workshift_offer['workshifts'], key=lambda x: x['id'],
    )
    assert workshift_offer == offer


@pytest.mark.filldb(workshift_rules='skip_tariffs')
@pytest.mark.config(
    WORKSHIFTS_BUY_USING_OFFERS_ALLOWED=True,
    WORKSHIFTS_PREFERRED_TARIFFS_ORDER=[
        'child_tariff',
        'econom',
        'comfort',
        'comfortplus',
        'vip',
    ],
    WORKSHIFTS_MIN_TAXIMETER_VERSION_FOR_SHIFTS_WITH_TARIFFS='8.55',
    WORKSHIFTS_ENABLED_SHIFTS_WITH_TARIFFS=True,
    WORKSHIFTS_TARIFFS_FOR_OLD_VERSION=['econom'],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.translations(geoareas={'moscow': {'en': 'Москва'}})
@pytest.mark.parametrize(
    'clid,db_id,uuid,expected_response,candidates_enabled',
    [
        ('999011', 'dbidx', 'uuid11', 'expected_response4.json', True),
        ('999011', 'dbidx', 'uuid11', 'expected_response5.json', False),
    ],
)
def test_workshifts_skip_tariffs(
        taxi_protocol,
        mockserver,
        load_json,
        config,
        clid,
        uuid,
        expected_response,
        db_id,
        candidates_enabled,
):
    config.set_values(dict(WORKSHIFTS_CANDIDATES_ENABLED=candidates_enabled))

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_tracker_profile(request):
        return load_json('mock_tracker/expected_response.json')

    @mockserver.json_handler('/candidates/profiles')
    def mock_candidates(request):
        request_data = json.loads(request.get_data())
        driver = request_data['driver_ids'][0]
        return {
            'drivers': [
                {
                    'dbid': driver['dbid'],
                    'uuid': driver['uuid'],
                    'position': [37.590533, 55.733863],
                    'classes': ['econom', 'vip'],
                },
            ],
        }

    response = taxi_protocol.get(
        '/utils/1.0/workshifts',
        params={
            'clid': clid,
            'db': db_id,
            'uuid': uuid,
            'version': '8.58 (850)',
            'latitude': '55.733863',
            'longitude': '37.590533',
        },
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )
    assert response.status_code == 200
    content = response.json()

    content.pop('offer_id')

    expected_response = load_json('tariffs/' + expected_response)
    content['available_workshifts'] = sorted(
        content['available_workshifts'], key=lambda x: x['id'],
    )
    expected_response['available_workshifts'] = sorted(
        expected_response['available_workshifts'], key=lambda x: x['id'],
    )

    assert content == expected_response
