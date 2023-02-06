# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from taxi.core import db
from taxi_maintenance.stuff import send_promocode_notification


@pytest.mark.now("2018-10-10T13:01:00+0300")
@pytest.mark.config(
    DRIVER_PROMOCODES_NOTIFICATIONS_ENABLED=True,
    DRIVER_PROMOCODES_MIN_COMMISSION={
        'RUB': 1,
        'BYN': 0.1,
        '__default__': 1
    }
)
@pytest.mark.translations([
    (
        'taximeter_driver_messages',
        'driver_promocode.created',
        'ru',
        'Промокод создан: %(code)s, продолжительность %(duration)s часов.'
    ),
    (
        'taximeter_driver_messages',
        'driver_promocode.finished',
        'ru',
        'Промокод закончился: код %(code)s'
    )
])
@pytest.inline_callbacks
def test_send_promocode_notification(patch, areq_request):
    db_id_1, db_id_3 = ('dbid1', 'dbid3')
    driver_ids = {
        db_id_1: 'driver1',
        db_id_3: 'driver3'
    }
    msgs = {
        db_id_1: 'Промокод создан: 11111111, продолжительность 12 часов.',
        db_id_3: 'Промокод закончился: код 33333333'
    }

    @areq_request
    def mock_request(method, url, params, json, *args, **kwargs):
        assert method == 'POST'
        assert url == (
            'http://driver-protocol.taxi.tst.yandex.net/service/chat/add'
        )
        assert params['db'] in (db_id_1, db_id_3)
        assert json == {
            'msg': msgs[params['db']],
            'driver': driver_ids[params['db']],
            'channel': 'PRIVATE',
            'user_login': 'YANDEX',
            'user_name': 'YANDEX',
            'yandex': True
        }
        return areq_request.response(200)

    yield send_promocode_notification.do_stuff()

    assert len(mock_request.calls) == 2

    doc = yield db.driver_promocodes.find_one({'_id': 'promocode_1'})
    assert doc['send_notification'] == 'finished'
    doc = yield db.driver_promocodes.find_one({'_id': 'promocode_3'})
    assert doc.get('send_notification') is None


@pytest.mark.now("2018-10-10T13:00:00+0300")
@pytest.mark.config(DRIVER_PROMOCODES_NOTIFICATIONS_ENABLED=False)
@pytest.inline_callbacks
def test_send_promocode_notification_disabled(patch, areq_request):
    @areq_request
    def mock_request(method, url, params, json, *args, **kwargs):
        assert False, 'should not be called'

    yield send_promocode_notification.do_stuff()

    assert len(mock_request.calls) == 0
