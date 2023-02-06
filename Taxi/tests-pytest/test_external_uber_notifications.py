# coding: utf-8
from __future__ import unicode_literals

import datetime
from collections import namedtuple

import pytest

from taxi.internal import dbh
from taxi.internal.notifications import order as notify
from taxi.internal.order_kit.plg import order_fsm
from taxi_stq.tasks.notify import task


NOW = datetime.datetime(2017, 6, 23)


def _notify_on_moved_to_cash(order_state, log_extra):
    return notify.notify_on_moved_to_cash(order_state, False, log_extra)


@pytest.mark.config(UBER_STATUS_NOTIFICATION_ENABLED=True)
@pytest.mark.parametrize('event, notify_method', [
    (
        'driver_arriving',
        notify.notify_on_waiting,
    ),
    (
        'driver_assigned',
        notify.notify_on_assigned,
    ),
    (
        'no_drivers_available',
        notify.notify_on_search_expired,
    ),
    (
        'payment_invalid',
        _notify_on_moved_to_cash,
    ),
])
@pytest.mark.filldb()
@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations([
    ('client_messages', 'time', 'fr', 'time'),
    ('notify', 'apns.moved_to_cash', 'fr', 'apns.text'),
    ('notify', 'time', 'fr', 'time'),
])
@pytest.inline_callbacks
def test_notify_uber(patch, event, notify_method):

    @patch('taxi.internal.notifications.order._send_notification_internal')
    def _try_send_sms(*args, **kwargs):
        pass

    @patch('taxi.internal.notifications.order._send_notification')
    def _send_notification(*args, **kwargs):
        pass

    @patch('taxi.internal.notifications.order.text_formatter.performer_info')
    def performer_info(*args, **kwargs):
        pass

    @patch('taxi.internal.notifications.order._make_common_payload')
    def _make_common_payload(*args, **kwargs):
        return {}

    @patch('taxi.internal.notifications.order._arrival_interval')
    def _arrival_interval(*args, **kwargs):
        return 10, 10

    @patch('taxi.external.geotracks.get_driver_track')
    def _get_driver_track(*args, **kwargs):
        class TrackResp():
            def json(self):
                return {'track': [
                    {
                        'point': [0, 0],
                        'timestamp': 0,
                    }
                ]}
        return TrackResp()

    @patch('taxi.internal.notifications.order.'
           '_uber_finish_order_notifications')
    def _uber_finish_order_notifs(*args, **kwargs):
        pass

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_ = namedtuple('uuid4', 'hex')
        return uuid4_('2830227ea6944f95b894d27df5f9ace4')

    @patch('taxi.core.arequests.post')
    def post(*args, **kwargs):
        class DummyResp:
            status_code = 0
        return DummyResp()

    order_id = 'order_id3'
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order.request.due = NOW + datetime.timedelta(minutes=10)
    state = order_fsm.OrderFsm(proc=proc)
    state._candidate_index = 0

    yield notify_method(state, None)

    yield task(order_id, None)

    calls = post.calls

    assert len(calls) == 1

    assert calls[0]['args'][0] == 'https://api.some-uber-host.com/providers' \
                                  '/trips/order_id3/notifications'

    assert calls[0]['kwargs'] == _get_expected_uber_send_kwargs(event)

    assert len(_send_notification.calls) == 0


@pytest.mark.config(UBER_STATUS_NOTIFICATION_ENABLED=False)
@pytest.mark.filldb()
@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations([
    ('client_messages', 'time', 'ru', 'time'),
    ('notify', 'apns.moved_to_cash', 'ru', 'apns.text'),
    ('notify', 'time', 'ru', 'time'),
])
@pytest.inline_callbacks
def test_notify_uber_disabled(patch):
    @patch('taxi.external.uber_notifications.send')
    def send(*args, **kwargs):
        pass

    @patch('taxi.internal.notifications.order._send_notification_internal')
    def _try_send_sms(*args, **kwargs):
        pass

    @patch('taxi.internal.notifications.order._send_notification')
    def _send_notification(*args, **kwargs):
        pass

    @patch('taxi.internal.notifications.order.text_formatter.performer_info')
    def performer_info(*args, **kwargs):
        pass

    @patch('taxi.internal.notifications.order._make_common_payload')
    def _make_common_payload(*args, **kwargs):
        return {}

    @patch('taxi.internal.notifications.order._arrival_interval')
    def _arrival_interval(*args, **kwargs):
        return 10, 10

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_ = namedtuple('uuid4', 'hex')
        return uuid4_('2830227ea6944f95b894d27df5f9ace4')

    order_id = 'order_id3'
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order.request.due = NOW + datetime.timedelta(minutes=10)
    state = order_fsm.OrderFsm(proc=proc)

    yield notify.notify_on_waiting(state, None)

    yield task(order_id, None)

    calls = send.calls

    assert len(calls) == 0


@pytest.mark.config(UBER_STATUS_NOTIFICATION_ENABLED=True)
@pytest.mark.parametrize('event, notify_method', [
    (
        'completed',
        notify.notify_on_complete,
    ),
    (
        'driver_canceled',
        notify.notify_on_autoreordering,
    ),
])
@pytest.mark.filldb()
@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations([
    ('client_messages', 'time', 'ru', 'time'),
    ('notify', 'apns.moved_to_cash', 'ru', 'apns.text'),
    ('notify', 'time', 'ru', 'time'),
])
@pytest.inline_callbacks
def test_notify_complete_uber(patch, event, notify_method):

    @patch('taxi.internal.notifications.order._send_notification_internal')
    def _try_send_sms(*args, **kwargs):
        pass

    @patch('taxi.internal.notifications.order._send_notification')
    def _send_notification(*args, **kwargs):
        pass

    @patch('taxi.internal.notifications.order.text_formatter.performer_info')
    def performer_info(*args, **kwargs):
        pass

    @patch('taxi.internal.notifications.order._make_common_payload')
    def _make_common_payload(*args, **kwargs):
        return {}

    @patch('taxi.internal.notifications.order._arrival_interval')
    def _arrival_interval(*args, **kwargs):
        return 10, 10

    @patch('taxi.external.geotracks.get_driver_track')
    def _get_driver_track(*args, **kwargs):
        class TrackResp():
            def json(self):
                return {'track': [
                    {
                        'point': [0, 0],
                        'timestamp': 0,
                    }
                ]}

        return TrackResp()

    @patch('taxi.internal.notifications.order.'
           '_uber_notifications')
    def _uber_notifs(*args, **kwargs):
        pass

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_ = namedtuple('uuid4', 'hex')
        return uuid4_('2830227ea6944f95b894d27df5f9ace4')

    @patch('taxi.core.arequests.post')
    def post(*args, **kwargs):
        class DummyResp:
            status_code = 204

            def json(self):
                return {}
        return DummyResp()

    order_id = 'order_id3'
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order.request.due = NOW + datetime.timedelta(minutes=10)
    state = order_fsm.OrderFsm(proc=proc)
    state._candidate_index = 0

    yield notify_method(state, None)

    yield task(order_id, None)

    calls = post.calls

    assert len(calls) == 1

    assert calls[0]['args'][0] == 'https://api.some-uber-host.com' \
                                  '/providers/trips'

    assert calls[0]['kwargs'] == {
        'headers': {
            'Accept-Language': 'fr',
            'Authorization': 'Bearer '
        },
        'json': {
            'all_points': '...',
            'calculated_fare': {
                'currency_code': 'руб.',
                'total': '100',
            },
            'state_changes': [
                {
                    'latitude': 1,
                    'longitude': 1,
                    'state': 'accepted',
                    'timestamp': 1494372265000
                },
                {
                    'latitude': 2,
                    'longitude': 2,
                    'state': 'begintrip',
                    'timestamp': 1494373425000
                },
                {
                    'latitude': 3,
                    'longitude': 3,
                    'state': 'completed',
                    'timestamp': 1494374625000
                }
            ],
            'trip_id': 'order_id3',
            'trip_source': 'yandex',
            'trip_status': event,
            'user_id': 'uber_id3',
            'vehicle': {
                'license_number': 'Q666QQ777',
                'make': u'\ufeff',
                'model': 'vehicle model',
            },
            'city_name': 'moscow'
        },
        'log_extra': {'extdict': {}},
        'timeout': 500,
    }

    assert len(_send_notification.calls) == 0


def _get_expected_uber_send_kwargs(event):
    kwargs = {
        'headers': {
            'Authorization':
                'Bearer ',
            'Accept-Language': 'fr'
        },
        'json': {
            'trip_id': 'order_id3',
            'event_time': 1494374625,
            'event_name': event,
            'user_id': 'uber_id3',
            'location': {
                'city_name': 'moscow',
                'latitude': 55.7,
                'longitude': 37.5,
            },
            'vehicle': {
                'license_number': "Q666QQ777",
                'make': u'\ufeff',
                'model': 'vehicle model',
            },
        },
        'log_extra': {'extdict': {}},
        'timeout': 500,
    }

    if event == 'driver_assigned':
        kwargs['json']['driver_arrival_eta'] = 1

    return kwargs
