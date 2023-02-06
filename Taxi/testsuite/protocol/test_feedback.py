import json

import pytest

from replica_dbusers_switch_parametrize import (
    PROTOCOL_SWITCH_TO_REPLICA_DBUSERS,
)
from user_api_switch_parametrize import PROTOCOL_SWITCH_TO_USER_API


def call_feedback_save(
        mockserver,
        taxi_protocol,
        request,
        feedback_called=True,
        passenger_feedback_called=False,
        passenger_feedback_failed=False,
        passenger_feedback_retries=3,
):
    feedback_data = {
        'order_finished_for_client': False,
        'rating': request['rating'],
        'call_me': False,
        'order_id': request['orderid'],
        'order_cancelled': False,
        'phone_id': '5714f45e98956f06baaae3d4',
        'choices': [
            {'type': key, 'value': value[0]}
            for key, value in request['choices'].items()
        ],
        'badges': [],
        'driver_license': 'AB0254',
        'app_comment': False,
        'order_completed': False,
        'allow_overwrite': True,
        'order_zone': 'moscow',
        'id': request['id'],
        'msg': request['msg'],
    }

    passenger_feedback_data = dict(feedback_data)
    passenger_feedback_data.pop('allow_overwrite')
    passenger_feedback_data[
        'driver_license_pd_id'
    ] = '62cdd404a88947cca670f32b87b90518'

    @mockserver.json_handler('/feedback/1.0/save')
    def mock_feedback_save(request):
        assert request.headers['YaTaxi-Api-Key'] == 'feedback_apikey'
        data = json.loads(request.get_data())
        assert 'created_time' in data
        assert 'order_created_time' in data
        data.pop('created_time')
        data.pop('order_created_time')
        assert data == feedback_data
        return {}

    @mockserver.json_handler(
        '/passenger_feedback/passenger-feedback/v1/feedback',
    )
    def mock_passenger_feedback_save(request):
        data = json.loads(request.get_data())
        assert 'created_time' in data
        assert 'order_created_time' in data
        data.pop('created_time')
        data.pop('order_created_time')
        assert data == passenger_feedback_data
        if passenger_feedback_failed:
            return mockserver.make_response({}, 500)
        else:
            return {}

    response = taxi_protocol.post(
        '/3.0/feedback', request, bearer='test_token',
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {}

    if passenger_feedback_called:
        if passenger_feedback_failed:
            assert (
                mock_passenger_feedback_save.times_called
                == passenger_feedback_retries
            )
        else:
            assert mock_passenger_feedback_save.times_called == 1
    else:
        assert mock_passenger_feedback_save.times_called == 0

    if feedback_called:
        assert mock_feedback_save.times_called == 1
    else:
        assert mock_feedback_save.times_called == 0


@PROTOCOL_SWITCH_TO_USER_API
@pytest.mark.parametrize(
    'tips_type, tips_value', [('flat', 10), ('percent', 15)],
)
@pytest.mark.parametrize(
    'passenger_feedback_failed, passenger_feedback_called, feedback_called',
    [
        pytest.param(False, False, True),
        pytest.param(
            False,
            True,
            False,
            marks=pytest.mark.experiments3(
                filename='exp3_use_passenger_feedback.json',
            ),
        ),
        pytest.param(
            True,
            True,
            True,
            marks=pytest.mark.experiments3(
                filename='exp3_use_passenger_feedback.json',
            ),
        ),
    ],
)
@pytest.mark.now('2018-08-17T10:43:38+0000')
def test_feedback_tips_nochoice_city_default(
        taxi_protocol,
        blackbox_service,
        db,
        mockserver,
        tips_type,
        tips_value,
        passenger_feedback_failed,
        passenger_feedback_called,
        feedback_called,
        user_api_switch_on,
):
    """
    Checks writing tips in db 'order' & 'order_proc'
    Empty 'tips' field checked in test_feedback_no_tips
    """

    @mockserver.json_handler('/user-api/users/get')
    def mock_user_api_user_get(request):
        return {
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'phone_id': '5714f45e98956f06baaae3d4',
            'yandex_uid': '4003514353',
        }

    call_feedback_save(
        mockserver,
        taxi_protocol,
        {
            'call_me': False,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'tips': {'type': tips_type, 'value': tips_value},
            'choices': {'low_rating_reason': ['rudedriver']},
            'orderid': '8c83b49edb274ce0992f337061047375',
            'rating': 4,
            'msg': 'hello world',
        },
        passenger_feedback_failed=passenger_feedback_failed,
        passenger_feedback_called=passenger_feedback_called,
        feedback_called=feedback_called,
    )

    proc = db.order_proc.find_one({'_id': '8c83b49edb274ce0992f337061047375'})
    if tips_type == 'flat':
        tips_perc = 0
    else:
        tips_perc = tips_value
    assert proc['order']['creditcard']['tips']['type'] == tips_type
    assert proc['order']['creditcard']['tips']['value'] == tips_value
    assert proc['order']['creditcard']['tips_perc_default'] == tips_perc
    order = db.orders.find_one({'_id': '8c83b49edb274ce0992f337061047375'})
    assert order['creditcard']['tips']['type'] == tips_type
    assert order['creditcard']['tips']['value'] == tips_value
    assert order['creditcard']['tips_perc_default'] == tips_perc

    if user_api_switch_on:
        assert mock_user_api_user_get.times_called == 1
    else:
        assert mock_user_api_user_get.times_called == 0


@pytest.mark.experiments3(filename='exp3_use_passenger_feedback.json')
@pytest.mark.parametrize(
    'passenger_feedback_retries',
    [
        pytest.param(
            2,
            marks=pytest.mark.config(
                PASSENGER_FEEDBACK_CLIENT_QOS={
                    '__default__': {'attempts': 2, 'timeout-ms': 200},
                },
            ),
        ),
        pytest.param(
            4,
            marks=pytest.mark.config(
                PASSENGER_FEEDBACK_CLIENT_QOS={
                    '__default__': {'attempts': 2, 'timeout-ms': 200},
                    '/passenger_feedback/passenger-feedback/v1/feedback': {
                        'attempts': 4,
                        'timeout-ms': 200,
                    },
                },
            ),
        ),
    ],
)
@pytest.mark.now('2018-08-17T10:43:38+0000')
def test_passenger_feedback_retries(
        taxi_protocol,
        blackbox_service,
        mockserver,
        passenger_feedback_retries,
):
    call_feedback_save(
        mockserver,
        taxi_protocol,
        {
            'call_me': False,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'tips': {'type': 'flat', 'value': 10},
            'choices': {'low_rating_reason': ['rudedriver']},
            'orderid': '8c83b49edb274ce0992f337061047375',
            'rating': 4,
            'msg': 'hello world',
        },
        passenger_feedback_failed=True,
        passenger_feedback_called=True,
        feedback_called=True,
        passenger_feedback_retries=passenger_feedback_retries,
    )


@pytest.mark.now('2018-08-17T10:43:38+0000')
@pytest.mark.filldb(users='crossdevice')
@pytest.mark.parametrize(
    'user_id',
    ['b300bda7d41b4bae8d58dfa93221ef16', 'crossdeviceuser00000000000000000'],
)
def test_feedback_no_tips(
        taxi_protocol, blackbox_service, db, mockserver, user_id,
):
    """
    When request doesn't contain the field 'tips',
    shouldn't change 'tips' in 'creditcard' field in dbs
    order & order_proc
    'order' already contains "creditcard.tips_perc_default" = 5
    """

    @mockserver.json_handler('/feedback/1.0/save')
    def mock_service_save(request):
        assert request.headers['YaTaxi-Api-Key'] == 'feedback_apikey'
        data = json.loads(request.get_data())
        assert data == {
            'order_finished_for_client': False,
            'rating': 4,
            'call_me': False,
            'order_id': '8c83b49edb274ce0992f337061047375',
            'order_cancelled': False,
            'phone_id': '5714f45e98956f06baaae3d4',
            'choices': [{'type': 'low_rating_reason', 'value': 'rudedriver'}],
            'created_time': '2018-08-17T10:43:38+0000',
            'order_created_time': '2018-08-17T10:42:54+0000',
            'driver_license': 'AB0254',
            'app_comment': False,
            'order_completed': False,
            'allow_overwrite': True,
            'order_zone': 'moscow',
            'id': user_id,
            'badges': [],
            'msg': 'hello world',
        }
        return {}

    response = taxi_protocol.post(
        '/3.0/feedback',
        {
            'call_me': False,
            'id': user_id,
            'choices': {'low_rating_reason': ['rudedriver']},
            'orderid': '8c83b49edb274ce0992f337061047375',
            'rating': 4,
            'msg': 'hello world',
        },
        bearer='test_token',
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {}
    proc = db.order_proc.find_one({'_id': '8c83b49edb274ce0992f337061047375'})
    assert proc.get('creditcard') is None
    order = db.orders.find_one({'_id': '8c83b49edb274ce0992f337061047375'})
    assert order['creditcard'].get('tips') is None
    assert order['creditcard']['tips_perc_default'] == 5


@pytest.mark.now('2018-08-17T10:43:38+0000')
def test_feedback_nochoice_city_nodefault_external(
        taxi_protocol, blackbox_service, mockserver,
):
    @mockserver.json_handler('/feedback/1.0/save')
    def mock_service_save(request):
        assert request.headers['YaTaxi-Api-Key'] == 'feedback_apikey'
        data = json.loads(request.get_data())
        assert data == {
            'order_finished_for_client': False,
            'rating': 4,
            'call_me': False,
            'order_id': '8c83b49edb274ce0992f337061047375',
            'order_cancelled': False,
            'order_created_time': '2018-08-17T10:42:54+0000',
            'phone_id': '5714f45e98956f06baaae3d4',
            'choices': [{'type': 'low_rating_reason', 'value': 'rudedriver'}],
            'created_time': '2018-08-17T10:43:38+0000',
            'driver_license': 'AB0254',
            'app_comment': False,
            'order_completed': False,
            'allow_overwrite': True,
            'order_zone': 'moscow',
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'badges': [],
            'msg': 'hello world',
        }
        return mockserver.make_response(status=404)

    response = taxi_protocol.post(
        '/3.0/feedback',
        {
            'call_me': False,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'tips': {'type': 'percent', 'value': 0},
            'choices': {'low_rating_reason': ['rudedriver']},
            'orderid': '8c83b49edb274ce0992f337061047375',
            'rating': 4,
            'msg': 'hello world',
        },
        bearer='test_token',
    )
    assert response.status_code == 404


@pytest.mark.now('2018-08-17T10:43:38+0000')
def test_feedback_cancel_reason_on_non_cancelled_order_external(
        taxi_protocol, blackbox_service, mockserver,
):
    @mockserver.json_handler('/feedback/1.0/save')
    def mock_service_save(request):
        assert request.headers['YaTaxi-Api-Key'] == 'feedback_apikey'
        data = json.loads(request.get_data())
        assert data == {
            'order_finished_for_client': False,
            'rating': 4,
            'call_me': False,
            'order_id': '8c83b49edb274ce0992f337061047375',
            'order_created_time': '2018-08-17T10:42:54+0000',
            'order_cancelled': False,
            'phone_id': '5714f45e98956f06baaae3d4',
            'choices': [{'type': 'cancelled_reason', 'value': 'longwait'}],
            'created_time': '2018-08-17T10:43:38+0000',
            'driver_license': 'AB0254',
            'app_comment': False,
            'order_completed': False,
            'allow_overwrite': True,
            'order_zone': 'moscow',
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'badges': [],
            'msg': 'hello world',
        }
        return mockserver.make_response(status=400)

    response = taxi_protocol.post(
        '/3.0/feedback',
        {
            'call_me': False,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'tips': {'type': 'percent', 'value': 0},
            'choices': {'cancelled_reason': ['longwait']},
            'orderid': '8c83b49edb274ce0992f337061047375',
            'rating': 4,
            'msg': 'hello world',
        },
        bearer='test_token',
    )
    assert response.status_code == 400


@pytest.mark.filldb(orders='archive', order_proc='archive')
def test_feedback_archive_order_proc_external(
        taxi_protocol, blackbox_service, db,
):
    response = taxi_protocol.post(
        '/3.0/feedback',
        {
            'call_me': False,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'tips': {'type': 'percent', 'value': 0},
            'choices': {'low_rating_reason': ['rudedriver']},
            'orderid': '8c83b49edb274ce0992f337061047375',
            'rating': 4,
            'msg': 'hello world',
        },
        bearer='test_token',
    )
    assert response.status_code == 404


@pytest.mark.now('2018-08-16T23:03:32+0000')
@pytest.mark.filldb(tariff_settings='disable_ban_category')
def test_ext_feedback_dont_exclude_driver_with_low_rating_sdc(
        taxi_protocol, blackbox_service, db, mockserver,
):
    @mockserver.json_handler('/feedback/1.0/save')
    def mock_service_save(request):
        assert request.headers['YaTaxi-Api-Key'] == 'feedback_apikey'
        data = json.loads(request.get_data())
        assert data == {
            'order_finished_for_client': False,
            'rating': 2,
            'call_me': False,
            'order_id': '8c83b49edb274ce0992f337061047476',
            'order_cancelled': False,
            'phone_id': '5714f45e98956f06baaae3d4',
            'choices': [{'type': 'low_rating_reason', 'value': 'rudedriver'}],
            'created_time': '2018-08-16T23:03:32+0000',
            'order_created_time': '2018-08-16T23:02:48+0000',
            'app_comment': False,
            'order_completed': False,
            'allow_overwrite': True,
            'order_zone': 'moscow',
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'badges': [],
            'msg': 'hello world 2',
        }
        return {}

    response = taxi_protocol.post(
        '/3.0/feedback',
        {
            'call_me': False,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'tips': {'type': 'percent', 'value': 0},
            'choices': {'low_rating_reason': ['rudedriver']},
            'orderid': '8c83b49edb274ce0992f337061047476',
            'rating': 2,
            'msg': 'hello world 2',
        },
        bearer='test_token',
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {}
    bad_order = db.excluded_drivers.find_one(
        {'o': '8c83b49edb274ce0992f337061047476'},
    )
    assert bad_order is None


@pytest.mark.now('2018-08-16T23:03:32+0000')
@pytest.mark.filldb(tariff_settings='enable_ban_category')
def test_ext_feedback_exclude_driver_with_low_rating_sdc(
        taxi_protocol, blackbox_service, db, mockserver,
):
    @mockserver.json_handler('/feedback/1.0/save')
    def mock_service_save(request):
        assert request.headers['YaTaxi-Api-Key'] == 'feedback_apikey'
        data = json.loads(request.get_data())
        assert data == {
            'order_finished_for_client': False,
            'rating': 2,
            'call_me': False,
            'driver_license': 'AB0254',
            'order_id': '8c83b49edb274ce0992f337061047476',
            'order_cancelled': False,
            'phone_id': '5714f45e98956f06baaae3d4',
            'choices': [{'type': 'low_rating_reason', 'value': 'rudedriver'}],
            'created_time': '2018-08-16T23:03:32+0000',
            'order_created_time': '2018-08-16T23:02:48+0000',
            'app_comment': False,
            'order_completed': False,
            'allow_overwrite': True,
            'order_zone': 'moscow',
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'badges': [],
            'msg': 'hello world 2',
        }
        return {}

    response = taxi_protocol.post(
        '/3.0/feedback',
        {
            'call_me': False,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'tips': {'type': 'percent', 'value': 0},
            'choices': {'low_rating_reason': ['rudedriver']},
            'orderid': '8c83b49edb274ce0992f337061047476',
            'rating': 2,
            'msg': 'hello world 2',
        },
        bearer='test_token',
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {}


@pytest.mark.now('2018-08-16T23:03:32+0000')
@pytest.mark.filldb(orders='reorder', order_proc='reorder')
def test_feedback_reorder(taxi_protocol, blackbox_service, mockserver, db):
    @mockserver.json_handler('/feedback/1.0/save')
    def mock_service_save(request):
        assert request.headers['YaTaxi-Api-Key'] == 'feedback_apikey'
        data = json.loads(request.get_data())
        assert data == {
            'order_finished_for_client': False,
            'rating': 4,
            'call_me': True,
            'order_id': '8c83b49edb274ce0992f337061047375',
            'reorder_id': 'ab064115e41d435eac5de389fcb205d3',
            'order_created_time': '2018-08-16T23:02:48+0000',
            'order_cancelled': False,
            'phone_id': '5714f45e98956f06baaae3d4',
            'choices': [{'type': 'low_rating_reason', 'value': 'rudedriver'}],
            'created_time': '2018-08-16T23:03:32+0000',
            'driver_license': 'AB0254',
            'app_comment': False,
            'order_completed': False,
            'allow_overwrite': True,
            'order_zone': 'moscow',
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'badges': [],
            'msg': 'hello world',
        }
        return {}

    response = taxi_protocol.post(
        '/3.0/feedback',
        {
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'tips': {'type': 'flat', 'value': 15},
            'choices': {
                'low_rating_reason': ['rudedriver'],
                'rating_reason': ['pong', 'other'],
            },
            'created_time': '2018-08-16T23:03:32+0000',
            'orderid': 'ab064115e41d435eac5de389fcb205d3',
            'rating': 4,
            'msg': 'hello world',
            'call_me': True,
        },
        headers={'Cookie': 'Session_id=test_session'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {}
    proc = db.order_proc.find_one({'_id': '8c83b49edb274ce0992f337061047375'})
    assert proc['order']['creditcard']['tips']['type'] == 'flat'
    assert proc['order']['creditcard']['tips']['value'] == 15
    assert proc['order']['creditcard']['tips_perc_default'] == 0

    order = db.orders.find_one({'_id': '8c83b49edb274ce0992f337061047375'})
    assert order['creditcard']['tips']['type'] == 'flat'
    assert order['creditcard']['tips']['value'] == 15

    assert mock_service_save.times_called == 1


@pytest.mark.config(MAX_TIPS_BY_CURRENCY={'RUB': 100.0})
def test_overtips(taxi_protocol):
    response = taxi_protocol.post(
        '/3.0/feedback',
        {
            'call_me': False,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'tips': {'type': 'flat', 'value': 101.0, 'currency': 'RUB'},
            'choices': {'low_rating_reason': ['rudedriver']},
            'orderid': '8c83b49edb274ce0992f337061047375',
            'rating': 4,
            'msg': 'hello world',
        },
        bearer='test_token',
    )
    assert response.status_code == 400


@pytest.mark.now('2018-08-17T10:43:38+0000')
@pytest.mark.parametrize(
    'tips,expected_code,expected_tips',
    [
        (
            {'type': 'percent', 'value': 0},
            200,
            {'type': 'percent', 'value': 0},
        ),
        (
            {'type': 'percent', 'decimal_value': '0'},
            200,
            {'type': 'percent', 'value': 0},
        ),
        ({'type': 'flat', 'value': 0}, 200, {'type': 'flat', 'value': 0}),
        (
            {'type': 'flat', 'decimal_value': '0'},
            200,
            {'type': 'flat', 'value': 0},
        ),
        ({'type': 'percent', 'value': 150}, 400, None),
        ({'type': 'percent', 'decimal_value': '150'}, 400, None),
        (
            {'type': 'flat', 'value': 150.23},
            200,
            {'type': 'flat', 'value': 150.23},
        ),
        (
            {'type': 'flat', 'decimal_value': '150.23'},
            200,
            {'type': 'flat', 'value': 150.23},
        ),
        ({'type': 'flat', 'decimal_value': '!!!'}, 400, None),
    ],
)
def test_feedback_tips_parsing(
        taxi_protocol,
        blackbox_service,
        db,
        mockserver,
        tips,
        expected_code,
        expected_tips,
):
    @mockserver.json_handler('/feedback/1.0/save')
    def mock_service_save(request):
        return {}

    response = taxi_protocol.post(
        '/3.0/feedback',
        {
            'call_me': False,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'tips': tips,
            'choices': {'low_rating_reason': ['rudedriver']},
            'orderid': '8c83b49edb274ce0992f337061047375',
            'rating': 4,
            'msg': 'hello world',
        },
        bearer='test_token',
    )
    assert response.status_code == expected_code

    if expected_code == 200:
        order = db.orders.find_one({'_id': '8c83b49edb274ce0992f337061047375'})
        assert order['creditcard']['tips'] == expected_tips


@PROTOCOL_SWITCH_TO_REPLICA_DBUSERS
def test_read_user_from_secondary(
        taxi_protocol, mockserver, db, testpoint, read_from_replica_dbusers,
):
    @testpoint('UserExperimentsHelper::GetById')
    def replica_dbusers_test_point(data):
        assert read_from_replica_dbusers == data['replica']

    @mockserver.json_handler('/feedback/1.0/save')
    def mock_service_save(request):
        return {}

    response = taxi_protocol.post(
        '/3.0/feedback',
        {
            'call_me': False,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'tips': {'type': 'percent', 'value': 0},
            'choices': {'low_rating_reason': ['rudedriver']},
            'orderid': '8c83b49edb274ce0992f337061047476',
            'rating': 2,
            'msg': 'hello world 2',
        },
        bearer='test_token',
    )

    assert response.status_code == 200
    assert replica_dbusers_test_point.wait_call()
