# coding: utf-8

import copy
import json
import pytest

from taxi.core import async
from taxi.internal import dbh
from taxi.internal import geo_position
from taxi_stq.tasks import arrival_push


DEFAULT_PROC_PATCH = {
    '$push': {
        dbh.order_proc.Doc.order.experiments: {
            '$each': [
                'send_notification_on_driver_arriving'
            ]
        }
    }
}


@async.inline_callbacks
def _check_send_push_on_driver_arriving(
        patch, order_id, order_proc_patch, arriving_time,
        expected_car_info, sent_state, changed_proc, areq_request):
    @patch('taxi.internal.driver_manager._set_brand_model')
    def _set_brand_model(brand, model, car_doc):
        assert model == 'Hyundai Equus'
        car_doc['model'] = model

    @patch('taxi.internal.import_drivers_utils.get_car_display_model')
    def _get_car_display_model(car_doc):
        assert car_doc['model'] == 'Hyundai Equus'
        return 'EquusMINE'

    @patch('taxi.internal.driver_manager._set_color')
    def _set_color(color, car_doc):
        assert color == u'оранжевый'
        car_doc['color'] = u'оранжевый'
        car_doc['color_code'] = 'FF8649'

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    @patch('taxi.internal.tracker.get_driver_position')
    @async.inline_callbacks
    def get_driver_position(*args, **kwargs):
        data = yield {'lon': 37.0, 'lat': 55.0, 'geotime': None}
        async.return_value(geo_position.DriverTrackPoint(**data))

    @patch('taxi.internal.tracker.get_smoothed_route')
    @async.inline_callbacks
    def get_smoothed_route(*args, **kwargs):
        assert 'router_yamaps' in args[0]['user_experiments']
        data = yield {'smooth_duration': arriving_time}
        async.return_value(data)

    @patch('taxi.external.driver_route_responder.timeleft')
    @async.inline_callbacks
    def timeleft(*args, **kwargs):
        data = yield {
            'time_left': arriving_time,
        }
        async.return_value(data)

    @patch('taxi.internal.router.route_info')
    @async.inline_callbacks
    def route_info(*args, **kwargs):
        if arriving_time:
            eta = yield arriving_time
        if (dbh.order_proc.Doc.order.experiments in order_proc_patch and
            'use_smooth_routing_in_push_on_driver_arriving' in
                order_proc_patch[dbh.order_proc.Doc.order.experiments]):
            assert False
        async.return_value(([], eta))

    @patch('taxi.internal.city_kit.country_manager.get_doc_by_zone_name')
    @async.inline_callbacks
    def get_countries(*args, **kwargs):
        rules = yield {
            'car_number_formatting_rules':
                {
                    'delimiter': ' ',
                    'regexps': [
                        '^(\\D)(\\d{3})(\\D{2})(\\d{2,3})$',
                        '^(\\D{2})(\\d{3})(\\d{2,3})$'
                    ],
                    'to_lower_case': False
                },
        }
        async.return_value(rules)

    @patch('taxi.internal.notifications.order._get_user')
    @async.inline_callbacks
    def get_user(*args, **kwargs):
        user = yield {}
        async.return_value(user)

    @patch('taxi.internal.notifications.order._send_push')
    @async.inline_callbacks
    def send_push(user, order_state, message_key, payload, log_extra):
        assert payload.get('car_info') == expected_car_info
        r = yield None
        async.return_value(r)

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    query = {
        dbh.order_proc.Doc._id: order_id,
    }

    proc = yield dbh.order_proc.Doc._find_and_modify(query,
                                                     order_proc_patch,
                                                     new=True)

    yield arrival_push._try_send_push_on_driver_arriving(order_id)

    new_proc = yield dbh.order_proc.Doc.find_one_by_exact_id(order_id)

    assert new_proc is not None

    if changed_proc:
        assert proc != new_proc
    else:
        assert proc == new_proc

    if new_proc.performer.candidate_index is not None:
        assert new_proc.candidates[
                   new_proc.performer.candidate_index
               ].push_on_driver_arriving_sent == sent_state


@pytest.mark.parametrize(
    'order_id,arriving_time,'
    'expected_car_info,sent_state,proc_changed',
    [
        (
            'send_push',
            60,
            None,
            'sent',
            True
        ),
        (
            'send_push',
            60,
            None,
            'sent',
            True
        ),
    ]
)
@pytest.mark.config(
    ADD_CAR_INFO_TO_NOTIFICATION='no_info',
    MIN_ETA_TO_SEND_DRIVER_ARRIVING=150,
    SEND_PUSH_IF_ETA_UNKNOWN=False,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING=True,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING_BY_ZONES=['moscow'],
    NOTIFICATION_ON_DRIVER_ARRIVING_SETTINGS={
        '__default__': {
            '__default__': {
                'hide_waiting_if_longer_than_mins': 30,
                'send_free_waiting': True,
                'send_notification_timings': [
                    {
                        'from': 0,
                        'send_eta': 90
                    }
                ]
            }
        }
    },
    RETRY_GET_ETA_PERIOD=10,
    NOTIFICATION_TYPES_FOR_DRIVER_ARRIVING=['push'],
    DELAY_PART_NEXT_CALL_ETA=0.2,
    MIN_SERVING_TIME_TO_SEND_NOTIFICATION=300
)
@pytest.mark.translations([
    ('notify', 'time', 'ru', '%H:%M'),
    ('color', 'FF8649', 'ru', 'orange'),
    ('notify', 'notifications.color', 'ru', '%(color)s %(info)s')
])
@pytest.inline_callbacks
def test_send_push_on_driver_arriving_no_car_info(
        patch, order_id, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request):

    yield _check_send_push_on_driver_arriving(
        patch, order_id, DEFAULT_PROC_PATCH, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request)


@pytest.mark.parametrize(
    'order_id,arriving_time,'
    'expected_car_info,sent_state,proc_changed',
    [
        (
            'send_push',
            60,
            u' \u041c\u0410 909 77',
            'sent',
            True
        ),
        (
            'send_push',
            60,
            u' \u041c\u0410 909 77',
            'sent',
            True
        )
    ]
)
@pytest.mark.config(
    ADD_CAR_INFO_TO_NOTIFICATION='car_number',
    MIN_ETA_TO_SEND_DRIVER_ARRIVING=150,
    SEND_PUSH_IF_ETA_UNKNOWN=False,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING=True,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING_BY_ZONES=['moscow'],
    NOTIFICATION_ON_DRIVER_ARRIVING_SETTINGS={
        '__default__': {
            '__default__': {
                'hide_waiting_if_longer_than_mins': 30,
                'send_free_waiting': True,
                'send_notification_timings': [
                    {
                        'from': 0,
                        'send_eta': 90
                    }
                ]
            }
        }
    },
    RETRY_GET_ETA_PERIOD=10,
    NOTIFICATION_TYPES_FOR_DRIVER_ARRIVING=['push'],
    DELAY_PART_NEXT_CALL_ETA=0.2,
    MIN_SERVING_TIME_TO_SEND_NOTIFICATION=300
)
@pytest.mark.translations([
    ('notify', 'time', 'ru', '%H:%M'),
    ('color', 'FF8649', 'ru', 'orange'),
    ('notify', 'notifications.color', 'ru', '%(color)s %(info)s')
])
@pytest.inline_callbacks
def test_send_push_on_driver_arriving_car_number(
        patch, order_id, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request):

    yield _check_send_push_on_driver_arriving(
        patch, order_id, DEFAULT_PROC_PATCH, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request)


@pytest.mark.parametrize(
    'order_id,arriving_time,'
    'expected_car_info,sent_state,proc_changed',
    [
        (
            'send_push',
            60,
            u'Orange EquusMINE \u041c\u0410 909 77',
            'sent',
            True
        ),
        (
            'send_push',
            60,
            u'Orange EquusMINE \u041c\u0410 909 77',
            'sent',
            True
        )
    ]
)
@pytest.mark.config(
    ADD_CAR_INFO_TO_NOTIFICATION='car_number_with_color_and_model',
    MIN_ETA_TO_SEND_DRIVER_ARRIVING=150,
    SEND_PUSH_IF_ETA_UNKNOWN=False,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING=True,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING_BY_ZONES=['moscow'],
    NOTIFICATION_ON_DRIVER_ARRIVING_SETTINGS={
        '__default__': {
            '__default__': {
                'hide_waiting_if_longer_than_mins': 30,
                'send_free_waiting': True,
                'send_notification_timings': [
                    {
                        'from': 0,
                        'send_eta': 90
                    }
                ]
            }
        }
    },
    RETRY_GET_ETA_PERIOD=10,
    NOTIFICATION_TYPES_FOR_DRIVER_ARRIVING=['push'],
    DELAY_PART_NEXT_CALL_ETA=0.2,
    MIN_SERVING_TIME_TO_SEND_NOTIFICATION=300
)
@pytest.mark.translations([
    ('notify', 'time', 'ru', '%H:%M'),
    ('color', 'FF8649', 'ru', 'orange'),
    ('notify', 'notifications.color', 'ru', '%(color)s %(info)s')
])
@pytest.inline_callbacks
def test_send_push_on_driver_arriving_car_number_and_color(
        patch, order_id, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request):

    yield _check_send_push_on_driver_arriving(
        patch, order_id, DEFAULT_PROC_PATCH, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request)


@pytest.mark.parametrize(
    'order_id,arriving_time,'
    'expected_car_info,sent_state,proc_changed',
    [
        (
            'send_push_nonsoon',
            60,
            None,
            None,
            False
        ),
        (
            'send_push',
            60,
            None,
            'sent',
            True
        )
    ]
)
@pytest.mark.config(
    SEND_PUSH_IF_ETA_UNKNOWN=True,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING=True,
    SEND_PUSH_FOR_NONSOON_ORDERS=False,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING_BY_ZONES=['moscow'],
    MIN_SERVING_TIME_TO_SEND_NOTIFICATION=300,
    NOTIFICATION_ON_DRIVER_ARRIVING_SETTINGS={
        '__default__': {
            '__default__': {
                'hide_waiting_if_longer_than_mins': 30,
                'send_free_waiting': True,
                'send_notification_timings': [
                    {
                        'from': 0,
                        'send_eta': 90
                    }
                ]
            }
        }
    }
)
@pytest.mark.translations([
    ('notify', 'time', 'ru', '%H:%M'),
    ('color', 'FF8649', 'ru', 'orange'),
    ('notify', 'notifications.color', 'ru', '%(color)s %(info)s')
])
@pytest.inline_callbacks
def test_send_push_on_driver_arriving_nonsoon_no_push(
        patch, order_id, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request):

    yield _check_send_push_on_driver_arriving(
        patch, order_id, DEFAULT_PROC_PATCH, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request)


@pytest.mark.parametrize(
    'order_id,arriving_time,'
    'expected_car_info,sent_state,proc_changed',
    [
        (
            'send_push_nonsoon',
            60,
            None,
            'sent',
            True
        ),
        (
            'send_push',
            60,
            None,
            'sent',
            True
        )
    ]
)
@pytest.mark.config(
    SEND_PUSH_IF_ETA_UNKNOWN=True,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING=True,
    SEND_PUSH_FOR_NONSOON_ORDERS=True,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING_BY_ZONES=['moscow'],
    MIN_SERVING_TIME_TO_SEND_NOTIFICATION=300,
    NOTIFICATION_ON_DRIVER_ARRIVING_SETTINGS={
        '__default__': {
            '__default__': {
                'hide_waiting_if_longer_than_mins': 30,
                'send_free_waiting': True,
                'send_notification_timings': [
                    {
                        'from': 0,
                        'send_eta': 90
                    }
                ]
            }
        }
    }
)
@pytest.mark.translations([
    ('notify', 'time', 'ru', '%H:%M'),
    ('color', 'FF8649', 'ru', 'orange'),
    ('notify', 'notifications.color', 'ru', '%(color)s %(info)s')
])
@pytest.inline_callbacks
def test_send_push_on_driver_arriving_nonsoon_send_push(
        patch, order_id, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request):

    yield _check_send_push_on_driver_arriving(
        patch, order_id, DEFAULT_PROC_PATCH, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request)


@pytest.mark.parametrize(
    'order_id,arriving_time,'
    'expected_car_info,sent_state,proc_changed',
    [
        (
            'send_push',
            60,
            None,
            'sent',
            True
        ),
        (
            'send_push',
            None,
            None,
            'sending',
            True
        )
    ]
)
@pytest.mark.config(
    SEND_PUSH_IF_ETA_UNKNOWN=True,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING=True,
    SEND_PUSH_FOR_NONSOON_ORDERS=True,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING_BY_ZONES=['moscow'],
    MIN_SERVING_TIME_TO_SEND_NOTIFICATION=300,
    USE_SMOOTH_ROUTING=True,
    NOTIFICATION_ON_DRIVER_ARRIVING_SETTINGS={
        '__default__': {
            '__default__': {
                'hide_waiting_if_longer_than_mins': 30,
                'send_free_waiting': True,
                'send_notification_timings': [
                    {
                        'from': 0,
                        'send_eta': 90
                    }
                ]
            }
        }
    }
)
@pytest.mark.translations([
    ('notify', 'time', 'ru', '%H:%M'),
    ('color', 'FF8649', 'ru', 'orange'),
    ('notify', 'notifications.color', 'ru', '%(color)s %(info)s')
])
@pytest.inline_callbacks
def test_send_push_on_driver_arriving_smooth_routing(
        patch, order_id, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request):
    proc_patch = copy.deepcopy(DEFAULT_PROC_PATCH)
    proc_patch['$push'][dbh.order_proc.Doc.order.experiments]['$each'] = [
        'use_smooth_routing_in_push_on_driver_arriving',
        'send_notification_on_driver_arriving'
    ]
    yield _check_send_push_on_driver_arriving(
        patch, order_id, proc_patch, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request)


@pytest.mark.parametrize(
    'order_id,arriving_time,'
    'expected_car_info,sent_state,proc_changed',
    [
        (
            'send_push',
            60,
            None,
            'sent',
            True
        ),
        (
            'send_push',
            None,
            None,
            'sending',
            True
        )
    ]
)
@pytest.mark.config(
    SEND_PUSH_IF_ETA_UNKNOWN=True,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING=True,
    SEND_PUSH_FOR_NONSOON_ORDERS=True,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING_BY_ZONES=['moscow'],
    MIN_SERVING_TIME_TO_SEND_NOTIFICATION=300,
    USE_SMOOTH_ROUTING=True,
    NOTIFICATION_ON_DRIVER_ARRIVING_SETTINGS={
        '__default__': {
            '__default__': {
                'hide_waiting_if_longer_than_mins': 30,
                'send_free_waiting': True,
                'send_notification_timings': [
                    {
                        'from': 0,
                        'send_eta': 90
                    }
                ]
            }
        }
    }
)
@pytest.mark.translations([
    ('notify', 'time', 'ru', '%H:%M'),
    ('color', 'FF8649', 'ru', 'orange'),
    ('notify', 'notifications.color', 'ru', '%(color)s %(info)s')
])
@pytest.inline_callbacks
def test_send_push_on_driver_arriving_uber_experiment(
        patch, order_id, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request):
    proc_patch = copy.deepcopy(DEFAULT_PROC_PATCH)
    proc_patch['$push'][dbh.order_proc.Doc.order.experiments]['$each'] = [
        'use_smooth_routing_in_push_on_driver_arriving',
        'send_notification_on_driver_arriving_uber'
    ]
    yield _check_send_push_on_driver_arriving(
        patch, order_id, proc_patch, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request)


@pytest.mark.parametrize(
    'order_id,arriving_time,'
    'expected_car_info,sent_state,proc_changed',
    [
        (
            'send_push_second_iteration',
            90,
            None,
            'sending',
            True
        ),
    ]
)
@pytest.mark.config(
    SEND_PUSH_IF_ETA_UNKNOWN=True,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING=True,
    SEND_PUSH_FOR_NONSOON_ORDERS=True,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING_BY_ZONES=['moscow'],
    MIN_SERVING_TIME_TO_SEND_NOTIFICATION=300,
    USE_SMOOTH_ROUTING=True,
    NOTIFICATION_ON_DRIVER_ARRIVING_SETTINGS={
        '__default__': {
            '__default__': {
                'hide_waiting_if_longer_than_mins': 30,
                'send_free_waiting': True,
                'send_notification_timings': [
                    {
                        'from': 0,
                        'send_eta': 90
                    }
                ]
            }
        }
    }
)
@pytest.mark.translations([
    ('notify', 'time', 'ru', '%H:%M'),
    ('color', 'FF8649', 'ru', 'orange'),
    ('notify', 'notifications.color', 'ru', '%(color)s %(info)s')
])
@pytest.inline_callbacks
def test_send_push_on_driver_arriving_second_iteration(
        patch, order_id, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request):
    proc_patch = copy.deepcopy(DEFAULT_PROC_PATCH)
    proc_patch['$push'][dbh.order_proc.Doc.order.experiments]['$each'] = [
        'use_smooth_routing_in_push_on_driver_arriving',
        'send_notification_on_driver_arriving_uber'
    ]
    yield _check_send_push_on_driver_arriving(
        patch, order_id, proc_patch, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request)


@pytest.mark.parametrize(
    'order_id,arriving_time,'
    'expected_car_info,sent_state,proc_changed',
    [
        (
            'send_push_autoreorder',
            90,
            None,
            'sending',
            False
        ),
    ]
)
@pytest.mark.config(
    SEND_PUSH_IF_ETA_UNKNOWN=True,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING=True,
    SEND_PUSH_FOR_NONSOON_ORDERS=True,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING_BY_ZONES=['moscow'],
    MIN_SERVING_TIME_TO_SEND_NOTIFICATION=300,
    USE_SMOOTH_ROUTING=True,
    NOTIFICATION_ON_DRIVER_ARRIVING_SETTINGS={
        '__default__': {
            '__default__': {
                'hide_waiting_if_longer_than_mins': 30,
                'send_free_waiting': True,
                'send_notification_timings': [
                    {
                        'from': 0,
                        'send_eta': 90
                    }
                ]
            }
        }
    }
)
@pytest.mark.translations([
    ('notify', 'time', 'ru', '%H:%M'),
    ('color', 'FF8649', 'ru', 'orange'),
    ('notify', 'notifications.color', 'ru', '%(color)s %(info)s')
])
@pytest.inline_callbacks
def test_send_push_on_driver_arriving_autoreorder(
        patch, order_id, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request):
    proc_patch = copy.deepcopy(DEFAULT_PROC_PATCH)
    proc_patch['$push'][dbh.order_proc.Doc.order.experiments]['$each'] = [
        'use_smooth_routing_in_push_on_driver_arriving',
        'send_notification_on_driver_arriving_uber'
    ]
    proc_patch['$set'] = {
        dbh.order_proc.Doc.performer.candidate_index: None
    }

    yield _check_send_push_on_driver_arriving(
        patch, order_id, proc_patch, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request)


@pytest.mark.parametrize(
    'order_id,arriving_time,'
    'expected_car_info,sent_state,proc_changed',
    [
        (
            'send_push',
            60,
            None,
            'sent',
            True
        ),
        (
            'send_push',
            None,
            None,
            'sending',
            True
        )
    ]
)
@pytest.mark.config(
    SEND_PUSH_IF_ETA_UNKNOWN=True,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING=True,
    SEND_PUSH_FOR_NONSOON_ORDERS=True,
    SEND_NOTIFICATION_ON_DRIVER_ARRIVING_BY_ZONES=['moscow'],
    MIN_SERVING_TIME_TO_SEND_NOTIFICATION=300,
    USE_SMOOTH_ROUTING=True,
    ARRIVAL_PUSH_USE_DRW=True,
    NOTIFICATION_ON_DRIVER_ARRIVING_SETTINGS={
        '__default__': {
            '__default__': {
                'hide_waiting_if_longer_than_mins': 30,
                'send_free_waiting': True,
                'send_notification_timings': [
                    {
                        'from': 0,
                        'send_eta': 90
                    }
                ]
            }
        }
    }
)
@pytest.mark.translations([
    ('notify', 'time', 'ru', '%H:%M'),
    ('color', 'FF8649', 'ru', 'orange'),
    ('notify', 'notifications.color', 'ru', '%(color)s %(info)s')
])
@pytest.inline_callbacks
def test_send_push_on_driver_arriving_smooth_routing_via_drw(
        patch, order_id, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request):
    # Test smooth eta via driver-route-watcher
    proc_patch = copy.deepcopy(DEFAULT_PROC_PATCH)
    proc_patch['$push'][dbh.order_proc.Doc.order.experiments]['$each'] = [
        'use_smooth_routing_in_push_on_driver_arriving',
        'send_notification_on_driver_arriving'
    ]
    yield _check_send_push_on_driver_arriving(
        patch, order_id, proc_patch, arriving_time,
        expected_car_info, sent_state, proc_changed, areq_request)
