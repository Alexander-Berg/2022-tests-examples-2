# -*- coding: utf-8 -*-
import datetime

import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.core import db
from taxi.external import adjust
from taxi.internal import adjust_manager
from taxi.internal import dbh
from taxi.util import dates


NOW = datetime.datetime(2016, 2, 9, 12, 35, 55)
CREATED = datetime.datetime(2016, 2, 9, 9, 35, 34)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(ADJUST_CONFIG={'__default__': False, 'enabled': True})
@pytest.mark.parametrize(
    'user_id, revenue, currency, adjust_exception, expected_tasks, '
    'success, not_sent, not_patched',
    [
        (
            'b64c2572a40f4abca870380754538441',
            None,
            None,
            None,
            [],
            1,
            0,
            0,
        ),
        (
            '2a9a63e31a024f01995744cbc4f723c9',
            None,
            None,
            None,
            [
                {
                    'u': '2a9a63e31a024f01995744cbc4f723c9',
                    'e': 'order_attempt',
                    'a': 'android',
                    'c': CREATED,
                    'updated': CREATED,
                    'n': (NOW + datetime.timedelta(
                        hours=settings.ADJUST_PATCH_DELAY)),
                    'tz': 'Europe/Moscow',
                }
            ],
            0,
            0,
            1,
        ),
        (
            'b64c2572a40f4abca870380754538441',
            None,
            None,
            adjust.AdjustRequestError(''),
            [
                {
                    'u': 'b64c2572a40f4abca870380754538441',
                    'e': 'order_attempt',
                    'a': 'android',
                    'c': CREATED,
                    'updated': CREATED,
                    'n': (NOW + datetime.timedelta(
                        hours=settings.ADJUST_SEND_DELAY)),
                    'tz': 'Europe/Moscow',
                    'k': 'android_id',
                    't': 'android',
                    'i': '89f9ebe64a7b4aee93205008812cb0e8',
                }
            ],
            0,
            1,
            0,
        ),
        (
            '0627ffc183d74cd882311eed6e8584eb',
            None,
            None,
            None,
            [
                {
                    'u': '0627ffc183d74cd882311eed6e8584eb',
                    'e': 'order_attempt',
                    'a': 'android',
                    'c': CREATED,
                    'updated': CREATED,
                    'n': (NOW + datetime.timedelta(
                        hours=settings.ADJUST_PATCH_DELAY)),
                    'tz': 'Europe/Moscow',
                }
            ],
            0,
            0,
            1,
        ),
        (
            '2a9a63e31a024f01995744cbc4f723c9',
            600,
            settings.DEFAULT_CURRENCY,
            adjust.AdjustRequestError(''),
            [
                {
                    'u': '2a9a63e31a024f01995744cbc4f723c9',
                    'e': 'order_attempt',
                    'a': 'android',
                    'c': CREATED,
                    'updated': CREATED,
                    'n': (NOW + datetime.timedelta(
                        hours=settings.ADJUST_PATCH_DELAY)),
                    'tz': 'Europe/Moscow',
                    'co': 600,
                    'cu': settings.DEFAULT_CURRENCY,
                }
            ],
            0,
            0,
            1,
        ),
        (
            '2a9a63e31a024f01995744cbc4f723c9',
            600,
            settings.DEFAULT_CURRENCY,
            adjust.InvalidAdjustUserError(''),
            [
                {
                    'u': '2a9a63e31a024f01995744cbc4f723c9',
                    'e': 'order_attempt',
                    'a': 'android',
                    'c': CREATED,
                    'updated': CREATED,
                    'n': (NOW + datetime.timedelta(
                        hours=settings.ADJUST_PATCH_DELAY)),
                    'tz': 'Europe/Moscow',
                    'co': 600,
                    'cu': settings.DEFAULT_CURRENCY,
                }
            ],
            0,
            0,
            1,
        )
    ]
)
@pytest.inline_callbacks
def test_process_event_success(
        patch,
        user_id, revenue, currency, adjust_exception, expected_tasks,
        success, not_sent, not_patched):

    @patch('taxi.external.experiments3.get_values')
    def experiments3_mock(consumer, experiments_args, **kwargs):
        assert False  # this experiment must not be checked

    @patch('taxi.external.adjust.request')
    @async.inline_callbacks
    def adjust_request(*args, **kwargs):
        date_localized = dates.localize(
            CREATED,
            'Europe/Moscow'
        )

        expected = {
            'event_token': 'tr7d7e',
            'app_token': '55ug2ntb3uzf',
            'device_id_key': 'android_id',
            'device_id_value': '89f9ebe64a7b4aee93205008812cb0e8',
            'created_at': date_localized,
            'revenue': revenue,
            'currency': currency,
            'log_extra': None
        }
        yield
        assert kwargs == expected
        assert args == ()
        if adjust_exception is not None:
            raise adjust_exception

    yield adjust_manager._process_event(
        user_id=user_id,
        created_at=CREATED,
        city_id=u'Москва',
        event_type='order_attempt',
        revenue=revenue,
        application='android',
        currency=currency,
    )

    tasks = yield dbh.adjust_tasks.Doc._find({}, {'_id': 0}).run()
    assert tasks == expected_tasks

    entry = yield db.adjust_stats.find_one({'_id': 'requests'})
    assert entry[adjust_manager.SUCCESS] == success
    assert entry[adjust_manager.NOT_SENT] == not_sent
    assert entry[adjust_manager.NOT_PATCHED] == not_patched
