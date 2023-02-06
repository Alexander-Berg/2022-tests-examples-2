# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.core import db
from taxi_stq.tasks import calc_fulfilled_subventions_notify as cfs

_TRANSLATIONS = [
    (
        'taximeter_messages',
        'subventions_done_feed.daily_guarantee.fulfilled_text',
        'ru',
        (
            'full cost of your orders %(in_zone)s for %(date)s '
            'is %(income)s. guarantee for %(num_orders)s is '
            '%(guarantee)s. %(bonus)s will be added to balance'
        ),
    ),
    (
        'taximeter_messages',
        'subventions_done_feed.daily_guarantee.n_orders',
        'ru',
        '%(count)s orders'
    ),
    (
        'taximeter_messages',
        'subventions_feed.rule_sum',
        'ru',
        '%(sum)s %(currency)s'
    ),
    (
        'taximeter_messages',
        'subventions_feed.in_zone.moscow',
        'ru',
        'in moscow'
    ),
    (
        'taximeter_messages',
        'subventions_feed.in_zone_default',
        'ru',
        'in your zone'
    ),
    (
        'tariff',
        'currency.rub',
        'ru',
        'rub',
    ),
    (
        'taximeter_messages',
        'subventions_done_feed.daily_guarantee.bonus_title',
        'ru',
        'YOU DID IT!',
    ),
    (
        'taximeter_messages',
        'subventions_done_feed.daily_guarantee.fulfilled_text',
        'en',
        (
            'EN: full cost of your orders %(in_zone)s for %(date)s '
            'is %(income)s. guarantee for %(num_orders)s is '
            '%(guarantee)s. %(bonus)s will be added to balance'
        ),
    ),
    (
        'taximeter_messages',
        'subventions_done_feed.daily_guarantee.n_orders',
        'en',
        '%(count)s orders'
    ),
    (
        'taximeter_messages',
        'subventions_feed.rule_sum',
        'en',
        '%(sum)s %(currency)s'
    ),
    (
        'taximeter_messages',
        'subventions_feed.in_zone.moscow',
        'en',
        'in moscow'
    ),
    (
        'taximeter_messages',
        'subventions_feed.in_zone_default',
        'en',
        'in your zone'
    ),
    (
        'tariff',
        'currency.rub',
        'en',
        'rub',
    ),
    (
        'taximeter_messages',
        'subventions_done_feed.daily_guarantee.bonus_title',
        'en',
        'YOU DID IT!',
    ),
    (
        'taximeter_messages',
        'subventions_done_feed.daily_guarantee.bonus_title',
        'kk',
        'YOU DID IT!',
    ),
    (
        'taximeter_messages',
        'subventions_done_feed.daily_guarantee.exceeded_title',
        'ru',
        'Your income',
    ),
    (
        'taximeter_messages',
        'subventions_done_feed.daily_guarantee.exceeded_title',
        'en',
        'Your income',
    ),
    (
        'taximeter_messages',
        'subventions_done_feed.daily_guarantee.exceeded_text',
        'ru',
        (
            'full cost of your orders %(in_zone)s for %(date)s '
            'before Yandex.Taxi and park taxes is %(income)s. '
            'It exceeded guarantee for %(num_orders)s,'
            'thus bonus will not be added to balance. Have a nice day'
        ),
    ),
    (
        'taximeter_messages',
        'subventions_done_feed.daily_guarantee.exceeded_text',
        'en',
        (
            'full cost of your orders %(in_zone)s for %(date)s '
            'before Yandex.Taxi and park taxes is %(income)s. '
            'It exceeded guarantee for %(num_orders)s,'
            'thus bonus will not be added to balance. Have a nice day'
        ),
    ),
    (
        'taximeter_messages',
        'subventions_done_feed.daily_guarantee.exceeded_text_net',
        'ru',
        (
            'full cost of your orders %(in_zone)s for %(date)s '
            'before park taxes is %(income)s. '
            'It exceeded guarantee for %(num_orders)s,'
            'thus bonus will not be added to balance. Have a nice day'
        ),
    ),
    (
        'taximeter_messages',
        'subventions_done_feed.daily_guarantee.fulfilled_text_net',
        'ru',
        (
            'full cost of your orders %(in_zone)s for %(date)s '
            'before park taxes is %(income)s. guarantee for %(num_orders)s is '
            '%(guarantee)s. %(bonus)s will be added to balance'
        ),
    ),
    (
        'taximeter_messages',
        'subventions_done_feed.geobooking.bonus_text',
        'ru',
        (
            'income is %(income)s. bonus %(bonus)s.'
        ),
    ),
    (
        'taximeter_messages',
        'subventions_done_feed.geobooking.bonus_title',
        'ru',
        (
            'Geobooking title'
        ),
    ),
    (
        'taximeter_messages',
        'subventions_done_feed.geobooking.bonus_text',
        'en',
        (
            'income is %(income)s. bonus %(bonus)s.'
        ),
    ),
    (
        'taximeter_messages',
        'subventions_done_feed.geobooking.bonus_title',
        'en',
        (
            'Geobooking title'
        ),
    ),
    (
        'tariff',
        'currency.kzt',
        'ru',
        'kzt',
    ),
]


@pytest.mark.asyncenv('blocking')
@pytest.mark.translations(_TRANSLATIONS)
@pytest.mark.filldb(
    dbdrivers='for_test_calc_daily_guarantees',
    dbparks='for_test_calc_daily_guarantees',
    fulfilled_subventions_notify='for_test_calc_daily_guarantees',
    tariff_settings='for_test_calc_daily_guarantees',
)
@pytest.mark.parametrize(('zone_name', 'date', 'expected_notify_drivers_calls'), [
(
    'moscow',
    datetime.datetime(2018, 8, 16).date(),
    3
)
])
@pytest.inline_callbacks
def test_fulfilled_notify_taximeter(
        patch, zone_name, date, expected_notify_drivers_calls):
    notify_drivers = _patch_notify_drivers(patch)

    yield cfs.task(
        task_id='task_id',
        zone_name=zone_name,
        date=date.isoformat(),
        notify_id='notify_id'
    )

    assert len(notify_drivers.calls) == expected_notify_drivers_calls


@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(
    fulfilled_subventions_notify='for_test_calc_daily_guarantees',
)
@pytest.mark.parametrize(('zone_name', 'date', 'expected_notify_calls', 'chunk_size'), [
    (
        'moscow',
        datetime.datetime(2018, 8, 16).date(),
        3,
        5,
    )
    ])
@pytest.inline_callbacks
def test_stq_fulfilled_notify_chunks(patch, zone_name, date, expected_notify_calls, chunk_size):
    notify_mock = _patch_notify(patch, zone_name, date, chunk_size)
    yield cfs.task(
        task_id='task_id',
        zone_name=zone_name,
        date=date.isoformat(),
        notify_id='notify_id'
    )
    assert len(notify_mock.calls) == expected_notify_calls


@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(
    fulfilled_subventions_notify='for_test_calc_daily_guarantees',
)
@pytest.inline_callbacks
def test_stq_fulfilled_notify_checks_count(patch):
    zone_name = 'moscow'
    date = datetime.datetime(2018, 8, 16).date()
    notify_mock = _patch_notify(patch, zone_name, date, 10000)

    yield cfs.task(
        task_id='task_id',
        zone_name=zone_name,
        date=date.isoformat(),
        notify_id='notify_id'
    )
    assert len(notify_mock.calls) == 1

    yield db.fulfilled_subventions_notify.insert({
        'zone': zone_name,
        'date': date.isoformat(),
        'notify_id': 'notify_id',
        'order': {},
        'fulfilled': {},
        'key': 'some_key'
    })

    yield cfs.task(
        task_id='task_id',
        zone_name=zone_name,
        date=date.isoformat(),
        notify_id='notify_id'
    )
    assert len(notify_mock.calls) == 0


def _patch_notify(patch, zone_name, date, chunk_size):
    @patch('taxi.internal.subvention_kit.fulfilled_notify.notify_taximeter')
    @pytest.inline_callbacks
    def notify_taximeter(*args, **kwargs):
        assert kwargs['zone_name'] == zone_name
        assert kwargs['date'] == date
        yield
    cfs._NOTIFY_CHUNK_SIZE = chunk_size
    return notify_taximeter


def _patch_notify_drivers(patch):
    @patch('taxi.external.communications.notify_drivers')
    @async.inline_callbacks
    def notify_drivers(request_id, title, drivers, text=None, texts=None,
                       expires_at=None, alert=False, important=False,
                       tvm_src_service=None, log_extra=None):
        assert tvm_src_service == settings.STQ_TVM_SERVICE_NAME
        assert title == 'YOU DID IT!' or title == 'Your income'
        assert not alert
        assert not important
        assert '0' in request_id
        data = zip(drivers, texts)
        if title == 'YOU DID IT!':
            if request_id.endswith('/ru'):
                assert (
                           ('some_db_id', 'another'),
                           (
                               'full cost of your orders in moscow for 16.08 '
                               'is 2 rub. guarantee for 2 orders is '
                               '8002 rub. 8000 rub will be added to balance'
                           ),
                       ) in data

                assert (
                           ('some_db_id', 'billed'),
                           (
                               'full cost of your orders in your zone for 16.08 '
                               'is 3 rub. guarantee for 20 orders is '
                               '9003 rub. 9000 rub will be added to balance'
                           ),
                       ) in data
                assert (
                           ('some_db_id', 'no-bonus'),
                           (
                               'full cost of your orders in moscow for 16.08 '
                               'before park taxes is 1500 rub. guarantee for 2 orders is '
                               '2001 rub. 501 rub will be added to balance'
                           ),
                       ) in data
                # here comes `not in` check!
                assert (
                           ('some_db_id', 'different'),
                           (
                               'full cost of your orders in moscow for 16.08 '
                               'is 2000 rub. guarantee for 2 orders is '
                               '2001 rub. 0 rub will be added to balance'
                           ),
                       ) not in data
                assert len(data) == 7
            else:
                assert request_id.endswith('/en')
                assert (
                           ('some_db_id', 'some'),
                           (
                               'EN: full cost of your orders in moscow for 16.08 '
                               'is 1 rub. guarantee for 2 orders is '
                               '6001 rub. 6000 rub will be added to balance'
                           ),
                       ) in data
                assert len(data) == 1
        elif title == 'Your income':
            assert (
                   ('some_db_id', 'no-bonus'),
                   (
                       'full cost of your orders in moscow for 16.08 '
                       'before Yandex.Taxi and park taxes is 2500 rub. '
                       'It exceeded guarantee for 2 orders,'
                       'thus bonus will not be added to balance. Have a nice day'
                   ),
               ) in data
            assert (
                   ('some_db_id', 'no-bonus'),
                   (
                       'full cost of your orders in moscow for 16.08 '
                       'before park taxes is 2500 rub. '
                       'It exceeded guarantee for 2 orders,'
                       'thus bonus will not be added to balance. Have a nice day'
                   ),
               ) in data
            assert len(data) == 2
        yield

    return notify_drivers


def _patch_notify_drivers_geo(patch):
    @patch('taxi.external.communications.notify_drivers')
    @async.inline_callbacks
    def notify_drivers(request_id, title, drivers, text=None, texts=None,
                       expires_at=None, alert=False, important=False,
                       tvm_src_service=None, log_extra=None):
        assert tvm_src_service == settings.STQ_TVM_SERVICE_NAME
        assert title == 'Geobooking title'
        assert not alert
        assert not important
        assert '0' in request_id
        data = zip(drivers, texts)
        if request_id.startswith('moscow'):
            if request_id.endswith('/en'):
                assert (
                           ('some_db_id', 'some'), 'income is 1 rub. bonus 6000 rub.'
                       ) in data
                assert len(data) == 1
            elif request_id.endswith('/ru'):
                assert (
                           ('some_db_id', 'another'), 'income is 2 rub. bonus 8000 rub.'
                       ) in data
                assert (
                           ('some_db_id', 'billed'), 'income is 3 rub. bonus 9000 rub.'
                       ) in data
                assert (
                           ('some_db_id', 'different'), 'income is 2000 rub. bonus 0 rub.'
                       ) in data

                assert (
                           ('some_db_id', 'no-bonus'), 'income is 2500 rub. bonus 0 rub.'
                       ) in data
                # aggregated
                assert (
                            ('some_db_id', 'two-rules'), 'income is 11 rub. bonus 21000 rub.'
                       ) in data
                assert (
                            ('some_db_id', 'no-subvention-reasons'), 'income is 7 rub. bonus 12000 rub.'
                       ) in data
                assert (
                            ('some_db_id', 'holded'), 'income is 9 rub. bonus 14000 rub.'
                       ) in data
                assert len(data) == 7
        elif request_id.startswith('astana'):
            assert (
                       ('some_db_id', 'no-bonus'), 'income is 2500 kzt. bonus 0 kzt.'
                   ) in data
            assert len(data) == 1
        yield

    return notify_drivers
