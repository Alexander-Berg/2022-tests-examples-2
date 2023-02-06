import copy
import datetime
import json

import bson
from bson import ObjectId
import bson.json_util
import pytest

from taxi_tests import utils

from individual_tariffs_switch_parametrize import (
    PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS,
)
from order_core_switch_parametrize import PROTOCOL_SWITCH_TO_ORDER_CORE
from protocol.ordercommit import order_commit_common
from replica_dbusers_switch_parametrize import (
    PROTOCOL_SWITCH_TO_REPLICA_DBUSERS,
)

API_OVER_DATA_WORK_MODE = {
    '__default__': {'__default__': 'oldway'},
    'parks-activation-client': {'protocol': 'newway'},
}

DRIVERTAG = 'c457f916dad5ed96dcc05e150df711ad5fdf0f7239a355531b07c45cabff7ef9'


def update_mongo(db, collection_name, query, update):
    collection = getattr(db, collection_name)
    collection.update(query, {'$set': update})


def update_destinations_statuses(db, order_id, destinations_statuses):
    db.order_proc.update(
        {'_id': order_id},
        {
            '$set': {
                'destinations_statuses': [
                    {'passed': x, 'updated': datetime.datetime.utcnow()}
                    for x in destinations_statuses
                ],
            },
        },
    )


def make_taxiontheway_request(taxi_protocol, user_id, order_id):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {'format_currency': True, 'id': user_id, 'orderid': order_id},
    )
    return response


@pytest.fixture
def default_driver_position(tracker, now):
    tracker.set_position(
        '999012_a5709ce56c2740d9a536650f5390de0b',
        now,
        55.73341076871702,
        37.58917997300821,
    )


def check_points_statuses(response, destinations_statuses):
    assert 'request' in response
    assert 'route' in response['request']
    route = response['request']['route']

    # check number of points
    assert len(route) == len(destinations_statuses) + 1

    # only intermediate points should have 'passed' flag
    assert 'passed' not in route[0]
    assert 'passed' not in route[-1]

    # check that 'passed' values were changed
    for i in range(0, len(destinations_statuses) - 1):
        assert 'passed' in route[i + 1]
        assert route[i + 1]['passed'] == destinations_statuses[i]


@pytest.mark.parametrize(
    'destinations_statuses,expected_path',
    [
        ([], [(1, 2), (2, 3), (3, 4)]),
        ([False, False, False], [(1, 2), (2, 3), (3, 4)]),
        ([True, False, False], [(2, 3), (3, 4)]),
        ([True, True, False], [(3, 4)]),
        ([True, True, True], [(3, 4)]),
        ([False, False, True], [(3, 4)]),
        ([False, True, False], [(3, 4)]),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(orders='eta_transporting', order_proc='eta_transporting')
@pytest.mark.fixture_now(datetime.timedelta(minutes=10))
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_tow_transporting_eta(
        destinations_statuses,
        expected_path,
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        load_binary,
        mock_order_core,
        order_core_switch_on,
):
    order_id = '8c83b49edb274ce0992f337061047375'
    user_id = 'b300bda7d41b4bae8d58dfa93221ef16'

    @mockserver.json_handler('/maps-router/route_jams/')
    def route_jams(request):
        return mockserver.make_response(
            load_binary('route_jams.protobuf'),
            content_type='application/x-protobuf',
        )

    update_destinations_statuses(db, order_id, destinations_statuses)
    tracker.set_position('999012_a5709ce56c2740d9a536650f5390de0b', now, 1, 0)

    response = make_taxiontheway_request(taxi_protocol, user_id, order_id)

    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'transporting'
    assert mock_order_core.get_fields_times_called == int(order_core_switch_on)


@pytest.mark.parametrize(
    'destinations_statuses,expected_path',
    [
        ([], [(1, 2), (2, 3), (3, 4)]),
        ([False, False, False], [(1, 2), (2, 3), (3, 4)]),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(orders='eta_driving', order_proc='eta_driving')
@pytest.mark.fixture_now(datetime.timedelta(minutes=10))
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_tow_driving_eta(
        destinations_statuses,
        expected_path,
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        load,
        mock_order_core,
        order_core_switch_on,
):
    order_id = '8c83b49edb274ce0992f337061047375'
    user_id = 'b300bda7d41b4bae8d58dfa93221ef16'

    update_destinations_statuses(db, order_id, destinations_statuses)
    tracker.set_position('999012_a5709ce56c2740d9a536650f5390de0b', now, 1, 0)

    response = make_taxiontheway_request(taxi_protocol, user_id, order_id)

    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'driving'
    assert content.get('routeinfo') is not None
    assert mock_order_core.get_fields_times_called == int(order_core_switch_on)


@pytest.mark.config(TAXIONTHEWAY_ENABLE_ETA=False)
@pytest.mark.parametrize(
    'destinations_statuses,expected_path',
    [
        ([], [(1, 2), (2, 3), (3, 4)]),
        ([False, False, False], [(1, 2), (2, 3), (3, 4)]),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(orders='eta_driving', order_proc='eta_driving')
@pytest.mark.fixture_now(datetime.timedelta(minutes=10))
def test_tow_driving_eta_disabled_routeinfo(
        destinations_statuses,
        expected_path,
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        load,
):
    # same as test_tow_driving_eta but disable routeinfo
    order_id = '8c83b49edb274ce0992f337061047375'
    user_id = 'b300bda7d41b4bae8d58dfa93221ef16'

    update_destinations_statuses(db, order_id, destinations_statuses)
    tracker.set_position('999012_a5709ce56c2740d9a536650f5390de0b', now, 1, 0)

    response = make_taxiontheway_request(taxi_protocol, user_id, order_id)

    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'driving'
    assert content.get('routeinfo') is None


@pytest.mark.now('2016-12-15T11:30:00+0300')
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_tow_regular(
        taxi_protocol,
        mockserver,
        default_driver_position,
        mock_order_core,
        order_core_switch_on,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'waiting'
    assert content['tariff']['class'] == 'econom'
    assert content['driver'] == {
        'car': [37.58917997300821, 55.73341076871702],
        'color': 'фиолетовый',
        'color_code': '4A2197',
        'model': 'Skoda Fabia',
        'name': 'Бородач Исак Арнольдович',
        'overdue': False,
        'phone': '+79321259615',
        'need_request_driver_phone': True,
        'plates': 'Х492НК77',
        'way_time': 0,
        'yellow_car_number': False,
        'photo_url': (
            'https://tc.mobile.yandex.net/static/images/'
            '41007/54630f09-1f14-4bf3-8c24-04fdd7059107'
        ),
        'tag': DRIVERTAG,
    }
    assert mock_order_core.get_fields_times_called == int(order_core_switch_on)


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.config(USE_DRIVER_TRACKSTORY_PERCENT=100)
def test_tow_regular_driver_trackstory(taxi_protocol, mockserver, now):
    @mockserver.json_handler('/driver_trackstory/position')
    def get_position(request):
        return {
            'position': {
                'direction': 328,
                'lat': 55.73341076871702,
                'lon': 37.58917997300821,
                'speed': 30,
                'timestamp': utils.timestamp(now),
            },
            'type': 'raw',
        }

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'waiting'
    assert content['tariff']['class'] == 'econom'
    assert content['driver'] == {
        'car': [37.58917997300821, 55.73341076871702],
        'color': 'фиолетовый',
        'color_code': '4A2197',
        'model': 'Skoda Fabia',
        'name': 'Бородач Исак Арнольдович',
        'overdue': False,
        'phone': '+79321259615',
        'need_request_driver_phone': True,
        'plates': 'Х492НК77',
        'way_time': 0,
        'yellow_car_number': False,
        'photo_url': (
            'https://tc.mobile.yandex.net/static/images/'
            '41007/54630f09-1f14-4bf3-8c24-04fdd7059107'
        ),
        'tag': DRIVERTAG,
    }


@pytest.mark.filldb(tariff_settings='selfdriving')
@pytest.mark.experiments3(filename='cfg3_sdc_phone.json')
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.translations(
    client_messages={'taxiontheway.selfdriving.model': {'ru': 'беспилотник'}},
)
@pytest.mark.config(
    TAXIONTHEWAY_DRIVER_FIELDS_BY_TARIFF={
        'selfdriving': {
            'model_template_key': 'taxiontheway.selfdriving.model',
        },
    },
)
def test_tow_regular_sdc(taxi_protocol, mockserver, default_driver_position):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047476',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'waiting'
    assert content['tariff']['class'] == 'selfdriving'
    content['driver'].pop('tag')
    assert content['driver'] == {
        'car': [37.58917997300821, 55.73341076871702],
        'color': 'фиолетовый',
        'color_code': '4A2197',
        'model': 'беспилотник',
        'name': 'Бородач Исак Арнольдович',
        'overdue': False,
        'phone': '+71233141592',
        'plates': 'Х492НК77',
        'way_time': 0,
        'yellow_car_number': False,
        'photo_url': (
            'https://tc.mobile.yandex.net/static/images/'
            '41007/54630f09-1f14-4bf3-8c24-04fdd7059107'
        ),
    }


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(order_proc='uncommited')
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_tow_uncommited(
        taxi_protocol,
        mockserver,
        default_driver_position,
        mock_order_core,
        order_core_switch_on,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '46b7c9021bceaf5ec0086a12288b7a38',
        },
    )
    assert response.status_code == 404
    assert mock_order_core.get_fields_times_called == int(order_core_switch_on)


def _free_waiting_until(
        taxi_protocol,
        mockserver,
        default_driver_position,
        status_info,
        config,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    # 999012_a5709ce56c2740d9a536650f5390de0b is waiting since
    # 2016-12-15T11:29:38+0300.
    assert response.json().get('status_info') == status_info


@pytest.mark.parametrize(
    'status_info, due_diff, surge',
    [
        pytest.param(
            {
                'free_waiting_until': '2016-12-15T08:31:40+0000',
                'title_color': '#000000',
                'translations': {'card': {'title_template': 'Вас ожидает'}},
            },
            100,
            1,
            id='free waiting',
        ),
        pytest.param(
            {
                'free_waiting_until': '2016-12-15T08:30:10+0000',
                'title_color': '#FF0000',
                'translations': {'card': {'title_template': 'Пора ехать'}},
            },
            10,
            1,
            id='expiring free waiting',
        ),
        pytest.param(
            {
                'free_waiting_until': '2016-12-15T08:29:49+0000',
                'title_color': '#FF0000',
                'translations': {
                    'card': {'title_template': 'Платное ожидание'},
                },
                'waiting_price': 11.0,
            },
            -11,
            1,
            id='paid waiting',
        ),
        pytest.param(
            {
                'free_waiting_until': '2016-12-15T08:29:49+0000',
                'title_color': '#FF0000',
                'translations': {
                    'card': {
                        'title_template': (
                            'Платное ожидание 11\xa0$SIGN$$CURRENCY$'
                        ),
                    },
                },
                'waiting_price': 11.0,
            },
            -11,
            1,
            marks=pytest.mark.translations(
                client_messages={
                    'taxiontheway.card.waiting.paid': {
                        'ru': 'Платное ожидание %(value)s',
                    },
                },
            ),
            id='paid waiting with value',
        ),
        pytest.param(
            {
                'free_waiting_until': '2016-12-15T08:29:49+0000',
                'title_color': '#FF0000',
                'translations': {
                    'card': {'title_template': 'Платное ожидание'},
                },
                'waiting_price': 22.0,
            },
            -11,
            2,
            id='paid waiting with surge',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'taxiontheway.card.waiting.free': {'ru': 'Вас ожидает'},
        'taxiontheway.card.waiting.paid': {'ru': 'Платное ожидание'},
        'taxiontheway.card.waiting.expiring_free': {'ru': 'Пора ехать'},
    },
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.experiments3(filename='exp3_paid_waiting_timer.json')
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_tow_free_waiting_until_experiment_enabled(
        taxi_protocol,
        mockserver,
        db,
        default_driver_position,
        now,
        status_info,
        due_diff,
        surge,
        config,
        individual_tariffs_switch_on,
):
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$set': {
                'order.request.due': now + datetime.timedelta(
                    seconds=due_diff,
                ),
                'order.request.sp': surge,
            },
        },
    )
    _free_waiting_until(
        taxi_protocol,
        mockserver,
        default_driver_position,
        status_info,
        config,
    )


@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_tow_free_waiting_until_experiment_disabled(
        taxi_protocol, mockserver, default_driver_position, config,
):
    _free_waiting_until(
        taxi_protocol, mockserver, default_driver_position, None, config,
    )


@pytest.mark.parametrize(
    'version,expected_invocations,expected_version',
    [
        (None, ['master'], 'DAAAAAAABgAMAAQABgAAAB/jmQFZAQAA'),
        ('search', ['master'], 'DAAAAAAABgAMAAQABgAAAB/jmQFZAQAA'),
        (
            'DAAAAAAABgAMAAQABgAAAB/jmQFZAQAA',
            ['secondary'],
            'DAAAAAAABgAMAAQABgAAAB/jmQFZAQAA',
        ),
        (
            'DAAAAAAABgAMAAQABgAAACDlmQFZAQAA',
            ['secondary', 'master'],
            'DAAAAAAABgAMAAQABgAAAB/jmQFZAQAA',
        ),
        (
            'DAAAAAAABgAMAAQABgAAAFDdmQFZAQAA',
            ['secondary'],
            'DAAAAAAABgAMAAQABgAAAB/jmQFZAQAA',
        ),
    ],
    ids=[
        'no version',
        'invalid version',
        'same version',
        'laggy secondary',
        'advanced secondary',
    ],
)
@pytest.mark.now('2016-12-15T11:30:00.487+0300')
@pytest.mark.config(TAXIONTHEWAY_ALLOW_SECONDARY=True)
@PROTOCOL_SWITCH_TO_ORDER_CORE
@PROTOCOL_SWITCH_TO_REPLICA_DBUSERS
def test_tow_version(
        taxi_protocol,
        mockserver,
        default_driver_position,
        testpoint,
        mock_order_core,
        order_core_switch_on,
        read_from_replica_dbusers,
        version,
        expected_invocations,
        expected_version,
):
    pended_invocations = expected_invocations.copy()

    @testpoint('taxiontheway::Data::FetchProc')
    def handle_test_point(data):
        assert pended_invocations
        assert pended_invocations[0] == data['replica']
        del pended_invocations[0]

    @testpoint('taxiontheway::Data::FetchUser')
    def replica_dbusers_test_point(data):
        assert read_from_replica_dbusers == data['replica']

    request = {
        'format_currency': True,
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '8c83b49edb274ce0992f337061047375',
    }

    if version:
        request.update({'version': version})

    response = taxi_protocol.post('3.0/taxiontheway', request)
    assert response.status_code == 200
    content = response.json()
    assert content['version'] == expected_version
    assert not pended_invocations

    assert handle_test_point.wait_call()
    if order_core_switch_on:
        assert mock_order_core.get_fields_times_called == len(
            expected_invocations,
        )
    else:
        assert mock_order_core.get_fields_times_called == 0


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.experiments3(filename='experiments3_01.json')
def test_tow_regular_with_exp(
        taxi_protocol, default_driver_position, load_json,
):
    user_agent = (
        'ru.yandex.taxi.inhouse/3.98.8966 '
        '(iPhone; iPhone7,1; iOS 10.3.3; Darwin)'
    )
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
        headers={'User-Agent': user_agent},
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'waiting'
    assert content['tariff']['class'] == 'econom'
    assert content['driver'] == {
        'car': [37.58917997300821, 55.73341076871702],
        'color': 'фиолетовый',
        'color_code': '4A2197',
        'model': 'Skoda Fabia',
        'name': 'Бородач Исак Арнольдович',
        'overdue': False,
        'phone': '+79321259615',
        'need_request_driver_phone': True,
        'plates': 'Х492НК77',
        'way_time': 0,
        'yellow_car_number': False,
        'photo_url': (
            'https://tc.mobile.yandex.net/static/images/'
            '41007/54630f09-1f14-4bf3-8c24-04fdd7059107'
        ),
        'tag': DRIVERTAG,
    }
    assert len(content['typed_experiments']['items']) == 2
    print(content['typed_experiments'])


@pytest.mark.parametrize('exp_enabled', [True, False])
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_tow_plates_exp(
        taxi_protocol,
        default_driver_position,
        load_json,
        experiments3,
        exp_enabled,
):
    user_agent = (
        'ru.yandex.taxi.inhouse/3.98.8966 '
        '(iPhone; iPhone7,1; iOS 10.3.3; Darwin)'
    )
    if exp_enabled:
        experiments3.add_experiments_json(
            load_json('experiments3_plates.json'),
        )
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
        headers={'User-Agent': user_agent},
    )
    assert response.status_code == 200
    content = response.json()
    assert content['driver']['plates'] == 'Х492НК77'
    assert len(content['typed_experiments']['items']) == (
        1 if exp_enabled else 0
    )


@pytest.mark.config(
    SHOW_DRIVER_PHOTO_ZONES={'moscow': True, '__default__': False},
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_tow_regular_show_photo(
        taxi_protocol, mockserver, default_driver_position, mock_personal,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()

    assert content['status'] == 'waiting'
    assert content['tariff']['class'] == 'econom'
    assert content['driver'] == {
        'car': [37.58917997300821, 55.73341076871702],
        'color': 'фиолетовый',
        'color_code': '4A2197',
        'model': 'Skoda Fabia',
        'name': 'Бородач Исак Арнольдович',
        'overdue': False,
        'phone': '+79321259615',
        'need_request_driver_phone': True,
        'plates': 'Х492НК77',
        'way_time': 0,
        'yellow_car_number': False,
        'photo_url': mockserver.url('static/images/test/AB0254'),
        'tag': DRIVERTAG,
    }


@pytest.mark.config(
    SHOW_DRIVER_PHOTO_ZONES={'ekb': True, '__default__': False},
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_tow_regular_dont_show_photo(
        taxi_protocol, mockserver, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'waiting'
    assert content['tariff']['class'] == 'econom'
    assert content['driver'] == {
        'car': [37.58917997300821, 55.73341076871702],
        'color': 'фиолетовый',
        'color_code': '4A2197',
        'model': 'Skoda Fabia',
        'name': 'Бородач Исак Арнольдович',
        'overdue': False,
        'phone': '+79321259615',
        'need_request_driver_phone': True,
        'plates': 'Х492НК77',
        'way_time': 0,
        'yellow_car_number': False,
        'photo_url': (
            'https://tc.mobile.yandex.net/static/images/41007/'
            '54630f09-1f14-4bf3-8c24-04fdd7059107'
        ),
        'tag': DRIVERTAG,
    }


@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_tow_bad_user(taxi_protocol, mockserver, default_driver_position):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef17',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 404
    content = response.json()
    assert content['error']['text'] == 'User not found'


@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_tow_bad_user2(taxi_protocol, mockserver, default_driver_position):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': '7c5cea02692a49a5b5e277e4582af45b',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 401


@pytest.mark.now('2016-12-15T11:30:00+0300')
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_tow_404(
        taxi_protocol,
        mockserver,
        default_driver_position,
        mock_order_core,
        order_core_switch_on,
):
    @mockserver.json_handler('/order-archive/v1/order_proc/retrieve')
    def archive_api_handler(request):
        return mockserver.make_response(status=404)

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047379',
        },
    )
    assert response.status_code == 404
    assert mock_order_core.get_fields_times_called == int(order_core_switch_on)


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.config(
    HIDE_DRIVER_INFO={
        '__default__': {
            'driver_phone': True,
            'park_phone': True,
            'car_number': True,
            'fio': True,
        },
    },
)
def test_tow_hide_driver_info(
        taxi_protocol, mockserver, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['driver']['name'] == 'Исак'
    assert 'phone' not in content['driver']
    assert content['driver']['plates'] == '**92НК**'
    assert content['driver']['yellow_car_number'] is False
    assert 'phone' not in content['park']


@pytest.mark.config(ALLOW_CHANGE_TO_CASH_IF_UNSUCCESSFUL_PAYMENT=True)
@pytest.mark.filldb(orders='transporting_pool', order_proc='transporting_pool')
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_tow_available_cash(
        taxi_protocol, db, mockserver, default_driver_position,
):
    db.orders.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'payment_tech.unsuccessful_payment': True}},
    )
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )

    assert response.status_code == 200
    content = response.json()

    payment = list(
        filter(lambda x: x['name'] == 'payment', content['allowed_changes']),
    )[0]
    assert 'cash' in payment['available_methods']


@pytest.mark.parametrize(
    'use_order_core',
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    PROCESSING_BACKEND_CPP_SWITCH=[
                        'cancel-order-from-protocol',
                    ],
                ),
            ],
        ),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_tow_cancel_free(
        db,
        taxi_protocol,
        mockserver,
        default_driver_position,
        use_order_core,
        mock_order_core,
        order_core_switch_on,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'break': 'user',
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'cancelled'
    assert 'cost' not in content
    proc = db.order_proc.find_one({'_id': '8c83b49edb274ce0992f337061047375'})
    assert proc['order']['status'] == 'cancelled'
    assert (
        proc['order_info']['statistics']['status_updates'][-1]['s']
        == 'cancelled'
    )
    order_commit_common.check_current_prices(proc, 'final_cost', 0)
    assert mock_order_core.post_event_times_called == int(use_order_core)
    assert mock_order_core.get_fields_times_called == int(order_core_switch_on)


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.config(USE_DRIVER_TRACKSTORY_PERCENT=100)
def test_tow_cancel_free_driver_trackstory(db, taxi_protocol, mockserver):
    @mockserver.json_handler('/driver_trackstory/position')
    def get_position(request):
        return mockserver.make_response('{"message": "123"}', status=404)

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'break': 'user',
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'cancelled'
    assert 'cost' not in content
    proc = db.order_proc.find_one({'_id': '8c83b49edb274ce0992f337061047375'})
    order_commit_common.check_current_prices(proc, 'final_cost', 0)


@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_double_cancel(db, taxi_protocol, mockserver, default_driver_position):
    order_id = '8c83b49edb274ce0992f337061047375'
    user_id = 'b300bda7d41b4bae8d58dfa93221ef16'
    request = {
        'break': 'user',
        'format_currency': True,
        'id': user_id,
        'orderid': order_id,
    }
    response = taxi_protocol.post('3.0/taxiontheway', request)
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'cancelled'
    query = {'_id': order_id, 'order.user_id': user_id}
    proc = db.order_proc.find_one(query)

    response = taxi_protocol.post('3.0/taxiontheway', request)
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'cancelled'
    second_proc = db.order_proc.find_one(query)

    assert proc == second_proc


@pytest.mark.parametrize(
    'add_minimal, paid_cancel_fix, price_modifiers, expected_cost',
    [
        # minimal = 99, ride_price = 22
        (False, 200, 1.0, 222),  # paid_cancel_fix + ride_price
        (True, 0, 1.0, 121),  # minimal + ride_price
        (False, 200, 0.9, 220),  # paid_cancel_fix + ride_price * 0.9
        (True, 0, 0.9, 109),  # (minimal + ride_price) * 0.9
        (True, 100, 0.9, 209),  # paid_cancel_fix + (
        # minimal + ride_price) * 0.9
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=9))
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
def test_tow_cancel_paid(
        taxi_protocol,
        mockserver,
        recalc_order,
        default_driver_position,
        now,
        db,
        add_minimal,
        paid_cancel_fix,
        expected_cost,
        price_modifiers,
):
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$set': {
                'price_modifiers': {
                    'items': [
                        {
                            'pay_subventions': False,
                            'reason': 'ya_plus',
                            'tariff_categories': ['econom'],
                            'type': 'multiplier',
                            'value': str(price_modifiers),
                        },
                    ],
                },
            },
        },
    )

    db.tariffs.update(
        {
            'categories': {
                '$elemMatch': {
                    'category_type': 'application',
                    'id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                },
            },
        },
        {
            '$set': {
                'categories.$.add_minimal_to_paid_cancel': add_minimal,
                'categories.$.paid_cancel_fix': paid_cancel_fix,
            },
        },
    )
    taxi_protocol.tests_control(now, invalidate_caches=True)

    recalc_order.set_driver_recalc_result(expected_cost, expected_cost)
    recalc_order.set_user_recalc_result(expected_cost, expected_cost)

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'break': 'user',
            'format_currency': True,
            'cancel_state': 'paid',
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'cancelled'
    assert content['cost'] == expected_cost
    proc = db.order_proc.find_one({'_id': '8c83b49edb274ce0992f337061047375'})
    assert abs(proc['order']['cost'] - expected_cost) < 1e-6
    order_commit_common.check_current_prices(proc, 'final_cost', expected_cost)


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=9))
@pytest.mark.filldb(orders='cost_details', order_proc='cost_details')
def test_tow_cost_details(taxi_protocol, default_driver_position, maps_router):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047376',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'complete'
    assert content['cost'] == 300
    assert content['cost_message_details'] == {
        'cost_breakdown': [
            {
                'display_name': 'Ride',
                'display_amount': '255\u00a0$SIGN$$CURRENCY$',
            },
            {
                'display_name': '9 min of waiting',
                'display_amount': '45\u00a0$SIGN$$CURRENCY$',
            },
            {
                'display_name': 'Discount',
                'display_amount': '150\u00a0$SIGN$$CURRENCY$',
            },
        ],
    }

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '01729d2f89654a83b9ec47fafe55c379',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'complete'
    assert content['cost'] == 797
    assert 'cost_message' not in content
    assert 'cost_message_details' not in content


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=9))
@pytest.mark.filldb(
    orders='cost_details', order_proc='cost_details_new_pricing',
)
def test_tow_cost_details_new_pricing(
        taxi_protocol, default_driver_position, maps_router,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047376',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'transporting'
    assert content['final_cost'] == 42


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(orders='driving', order_proc='driving')
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
def test_tow_driving(
        taxi_protocol, mockserver, default_driver_position, db, maps_router,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'driving'
    # NOTE: in really routing of test case is 0 (routing between same point)
    assert content['cancel_rules'] == {
        'message_key': 'free.driving',
        'state': 'free',
        'state_change_estimate': 227,
    }
    assert content['tariff']['class'] == 'econom'
    assert content['exact_pickup_point'] == [40.454257, 56.152082]


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.config(COUNTRIES_DATA_SOURCE='database')
@pytest.mark.filldb(orders='driving', order_proc='driving')
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
def test_tow_driving_with_countries_data_source_database(
        taxi_protocol, mockserver, default_driver_position, db, maps_router,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'driving'
    # NOTE: in really routing of test case is 0 (routing between same point)
    assert content['cancel_rules'] == {
        'message_key': 'free.driving',
        'state': 'free',
        'state_change_estimate': 227,
    }
    assert content['tariff']['class'] == 'econom'
    assert content['exact_pickup_point'] == [40.454257, 56.152082]


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(orders='combo_order', order_proc='combo_order')
@pytest.mark.parametrize(
    ['order_id', 'expected_can_change_destinations'],
    [
        ('8c83b49edb274ce0992f337061000000', True),  # no altrernative type
        ('8c83b49edb274ce0992f337061000001', True),  # altpin alt type
        ('8c83b49edb274ce0992f337061000002', False),  # combo_outer alt type
        ('8c83b49edb274ce0992f337061000003', False),  # combo_inner alt type
    ],
)
def test_tow_combo_change_destinations(
        taxi_protocol,
        mockserver,
        default_driver_position,
        order_id,
        expected_can_change_destinations,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def mock_personal(request):
        request_json = json.loads(request.get_data())
        assert request_json == {'id': '1fab75363700481a9adf5e31c3b6e673'}
        return {
            'id': '1fab75363700481a9adf5e31c3b6e673',
            'value': '+79031520355',
        }

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': order_id,
        },
    )
    assert response.status_code == 200
    raw_allowed_changes = response.json()['allowed_changes']
    allowed_changes = {change['name'] for change in raw_allowed_changes}
    can_change_destinations = 'destinations' in allowed_changes
    assert can_change_destinations == expected_can_change_destinations


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(orders='transporting', order_proc='transporting')
@pytest.mark.translations(
    client_messages={
        'taxiontheway.time_calc_message': {
            'en': 'about %(final_cost_with_currency)s for %(estimate)d min',
        },
    },
)
def test_tow_transporting(
        taxi_protocol, mockserver, default_driver_position, db,
):
    """
    Although user_experiment 'tips_flat' and
    order_experiment 'tips_flat' (see db.order_proc) is active,
    shouldn't be field 'tips_suggestions' in response.
    It's existence are checked in test_tow_transporting_fixed
    """
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'transporting'
    assert content['cost_message'] == 'about 230 $SIGN$$CURRENCY$ for 16 min'
    assert content.get('tips_suggestions') is None


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(orders='transporting', order_proc='transporting')
@pytest.mark.translations(
    tariff={'routestats_description_taximeter_price': {'en': 'rub/km'}},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='taximeter_ride_price_for_user',
    consumers=['protocol/taxiontheway'],
    clauses=[],
    default_value={'enabled': True},
)
def test_totw_exp_ride_price(taxi_protocol, default_driver_position, db):
    db.tariff_settings.update(
        {'hz': 'moscow'}, {'$set': {'s.$[].fixed_price_enabled': False}},
    )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'transporting'
    assert content['cost_message'] == 'rub/km'


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(
    orders='fixed_transporting', order_proc='fixed_transporting',
)
@pytest.mark.fixture_now(datetime.timedelta(minutes=10))
def test_tow_transporting_fixed(
        taxi_protocol, mockserver, default_driver_position, db,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'transporting'
    assert content['cost_message'] == '151 $SIGN$$CURRENCY$ for the ride'
    assert 'cost_message_details' not in content
    assert content['tariff']['fixed']

    # Fixed price from taximeter
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'order_info.cc': 601}},
    )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'transporting'
    assert content['cost_message'] == '601 $SIGN$$CURRENCY$ for the ride'
    assert content['tariff']['fixed']


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(
    orders='fixed_transporting', order_proc='fixed_transporting',
)
@pytest.mark.fixture_now(datetime.timedelta(minutes=10))
@pytest.mark.user_experiments('tips_flat')
@pytest.mark.config(
    FLAT_TIPS_SETTINGS_V3={
        'countries': {
            'rus': {
                '__default__': {
                    'log_base': 14,
                    'percents': [5, 10, 15],
                    'manual_entry_allowed': True,
                    'decimal_digits': 0,
                    'min_tips_value': 10,
                    'tips_limit': {'max_tips': 100},
                    'base_numerator': 10,
                    'base_denominator': 10,
                    'additional_constant': 1,
                },
            },
        },
        'zones': {},
    },
    CURRENCY_FORMATTING_RULES={'__default__': {'__default__': 2}},
)
@pytest.mark.parametrize('has_disabled_flag', [True, False])
@pytest.mark.parametrize(
    ['payment_type', 'is_tips_payment_type_enabled'],
    [
        pytest.param('card', True),
        pytest.param('applepay', False),
        pytest.param(
            'applepay',
            True,
            marks=[
                pytest.mark.experiments3(
                    name='extra_tips_payment_methods',
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    consumers=['protocol/taxiontheway'],
                    clauses=[
                        {
                            'title': 'test_clause',
                            'value': {
                                'enabled': True,
                                'payment_types': ['card', 'applepay'],
                            },
                            'predicate': {'type': 'true'},
                        },
                    ],
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'ride_price,tips_choices',
    [
        (-100, None),
        (0, None),
        (
            99,
            [
                {'type': 'flat', 'value': 0, 'decimal_value': '0'},
                {'type': 'flat', 'value': 5, 'decimal_value': '5'},
                {'type': 'flat', 'value': 10, 'decimal_value': '10'},
                {'type': 'flat', 'value': 15, 'decimal_value': '15'},
            ],
        ),
        (
            101,
            [
                {'type': 'flat', 'value': 0, 'decimal_value': '0'},
                {'type': 'flat', 'value': 6, 'decimal_value': '6'},
                {'type': 'flat', 'value': 11, 'decimal_value': '11'},
                {'type': 'flat', 'value': 16, 'decimal_value': '16'},
            ],
        ),
        (
            231,
            [
                {'type': 'flat', 'value': 0, 'decimal_value': '0'},
                {'type': 'flat', 'value': 20, 'decimal_value': '20'},
                {'type': 'flat', 'value': 30, 'decimal_value': '30'},
                {'type': 'flat', 'value': 40, 'decimal_value': '40'},
            ],
        ),
        (
            431,
            [
                {'type': 'flat', 'value': 0, 'decimal_value': '0'},
                {'type': 'flat', 'value': 30, 'decimal_value': '30'},
                {'type': 'flat', 'value': 50, 'decimal_value': '50'},
                {'type': 'flat', 'value': 70, 'decimal_value': '70'},
            ],
        ),
        (
            631,
            [
                {'type': 'flat', 'value': 0, 'decimal_value': '0'},
                {'type': 'flat', 'value': 40, 'decimal_value': '40'},
                {'type': 'flat', 'value': 70, 'decimal_value': '70'},
                {'type': 'flat', 'value': 100, 'decimal_value': '100'},
            ],
        ),
        (
            2499,
            [
                {'type': 'flat', 'value': 0, 'decimal_value': '0'},
                {'type': 'flat', 'value': 130, 'decimal_value': '130'},
                {'type': 'flat', 'value': 250, 'decimal_value': '250'},
                {'type': 'flat', 'value': 380, 'decimal_value': '380'},
            ],
        ),
        (
            2600,
            [
                {'type': 'flat', 'value': 0, 'decimal_value': '0'},
                {'type': 'flat', 'value': 140, 'decimal_value': '140'},
                {'type': 'flat', 'value': 270, 'decimal_value': '270'},
                {'type': 'flat', 'value': 400, 'decimal_value': '400'},
            ],
        ),
    ],
)
def test_tow_tips(
        taxi_protocol,
        mockserver,
        default_driver_position,
        db,
        ride_price,
        tips_choices,
        has_disabled_flag,
        config,
        payment_type,
        is_tips_payment_type_enabled,
):
    """
    # Initial fixed price taken from order.fixed_price.price

    Also checks not obligatory field 'tips_suggestions'.
    It should be in response, when:
    1) active user_experiment 'tips_flat'
    2) active order_experiment 'tips_flat' (see db.order_proc)
    3) at the beginnings was fixed price (it may drop by change pt B)
    4) tips isn't percent or percent = 0 (see credit_card.tips in db.orders)
    Otherwise shouldn't exist


    When ride price < 101, should be used 101
    When ride price > 2499, should be used 2499

    When disabled flag == False, method behaves like
    it was without disabled flag
    """
    are_tips_expected = ride_price > 0 and is_tips_payment_type_enabled
    if has_disabled_flag:
        tariff_config = config.get('FLAT_TIPS_SETTINGS_V3')
        tariff_config['countries']['rus']['__default__']['disabled'] = False
        config.set_values(dict(FLAT_TIPS_SETTINGS_V3=tariff_config))

    order_id = '8c83b49edb274ce0992f337061047375'
    db.orders.update(
        {'_id': order_id}, {'$set': {'payment_tech.type': payment_type}},
    )
    db.order_proc.update(
        {'_id': order_id},
        {'$set': {'order.fixed_price.price_original': ride_price}},
    )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': order_id,
        },
    )
    assert response.status_code == 200
    content = response.json()
    tips_type = content['tips'].pop('type')
    assert content['tips'] == {
        'available': are_tips_expected,
        'value': 0,
        'decimal_value': '0',
    }
    if are_tips_expected:
        assert tips_type == 'flat'

    tips_suggestion_answer = {
        'variants': [
            {
                'choices': tips_choices,
                'customize_options': {
                    'decimal_digits': 0,
                    'manual_entry_allowed': True,
                    'max_value': '100',
                    'min_value': '10',
                },
                'match': {'max_rating': 5, 'min_rating': 4},
            },
        ],
    }
    if are_tips_expected:
        assert content['tips_suggestions'] == tips_suggestion_answer
    else:
        assert 'tips_suggestions' not in content


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(tariff_settings='selfdriving')
@pytest.mark.translations(
    client_messages={'taxiontheway.selfdriving.model': {'ru': 'беспилотник'}},
)
@pytest.mark.fixture_now(datetime.timedelta(minutes=10))
@pytest.mark.user_experiments('tips_flat')
@pytest.mark.config(
    FLAT_TIPS_SETTINGS_V3={
        'countries': {
            'rus': {
                '__default__': {
                    'log_base': 14,
                    'percents': [5, 10, 15],
                    'manual_entry_allowed': True,
                    'decimal_digits': 0,
                    'min_tips_value': 10,
                    'tips_limit': {'max_tips': 100},
                    'base_numerator': 10,
                    'base_denominator': 10,
                    'additional_constant': 1,
                },
            },
        },
        'zones': {},
    },
    CURRENCY_FORMATTING_RULES={'__default__': {'__default__': 2}},
)
def test_sdc_tips_disabled(taxi_protocol, mockserver, default_driver_position):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047476',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert not content.get('tips', {}).get('available')


def _mark_tips_config(
        max_tips_limit,
        min_tips_limit=None,
        min_tips_percent_limit=None,
        step=None,
):
    tips_limit = {'max_tips': max_tips_limit}
    if min_tips_limit is not None:
        tips_limit['min_tips'] = min_tips_limit
    if min_tips_percent_limit is not None:
        tips_limit['min_tips_percent'] = min_tips_percent_limit
    if step is not None:
        tips_limit['step'] = step
    configs = dict(
        FLAT_TIPS_SETTINGS_V3={
            'countries': {
                'rus': {
                    '__default__': {
                        'log_base': 14,
                        'percents': [5, 10, 15],
                        'manual_entry_allowed': True,
                        'decimal_digits': 0,
                        'min_tips_value': 10,
                        'tips_limit': tips_limit,
                        'base_numerator': 10,
                        'base_denominator': 10,
                        'additional_constant': 1,
                    },
                },
            },
            'zones': {},
        },
    )

    mark = pytest.mark.config(**configs)
    return [mark]


@pytest.mark.filldb(
    orders='fixed_transporting', order_proc='fixed_transporting',
)
@pytest.mark.user_experiments('tips_flat')
@pytest.mark.config(
    CURRENCY_FORMATTING_RULES={'__default__': {'__default__': 2}},
)
@pytest.mark.parametrize(
    ['ride_price', 'expected_max_value'],
    [
        # only max tips
        pytest.param(100, 1500, marks=_mark_tips_config(1500)),
        # no min_tips_percent_limit specified
        pytest.param(100, 1500, marks=_mark_tips_config(1500, 100)),
        pytest.param(100, 1500, marks=_mark_tips_config(1500, 100, None, 37)),
        pytest.param(100, 1500, marks=_mark_tips_config(1500, None, None, 37)),
        # min percent & no min tips
        pytest.param(100, 50, marks=_mark_tips_config(1500, None, 50)),
        pytest.param(100, 50, marks=_mark_tips_config(1500, 0, 50)),
        pytest.param(100, 50, marks=_mark_tips_config(1500, None, 50, 1)),
        pytest.param(100, 50, marks=_mark_tips_config(1500, 0, 50, 5)),
        # different step
        pytest.param(99, 50, marks=_mark_tips_config(1500, 0, 50, 10)),
        pytest.param(100, 50, marks=_mark_tips_config(1500, 0, 50, 50)),
        pytest.param(101, 100, marks=_mark_tips_config(1500, 0, 50, 50)),
        pytest.param(100, 50, marks=_mark_tips_config(1500, 0, 50, 10)),
        pytest.param(101, 60, marks=_mark_tips_config(1500, 0, 50, 10)),
        pytest.param(3.14, 10, marks=_mark_tips_config(1500, 0, 100, 10)),
        pytest.param(3.14, 4, marks=_mark_tips_config(1500, 0, 100, 1)),
        # set_precision rounding
        pytest.param(3.14, 3.14, marks=_mark_tips_config(1500, 0, 100)),
        pytest.param(3.54, 3.54, marks=_mark_tips_config(1500, 0, 100)),
        # min tips used
        pytest.param(100, 75, marks=_mark_tips_config(1500, 75, 50)),
        # max tips used
        pytest.param(9999, 100, marks=_mark_tips_config(100, 75, 50)),
    ],
)
def test_tow_max_tips(taxi_protocol, db, ride_price, expected_max_value):
    order_id = '8c83b49edb274ce0992f337061047375'
    db.order_proc.update(
        {'_id': order_id},
        {'$set': {'order.fixed_price.price_original': ride_price}},
    )
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': order_id,
        },
    )
    assert response.status_code == 200
    content = response.json()
    tips_suggestions_variant = content['tips_suggestions']['variants'][0]
    max_value = tips_suggestions_variant['customize_options']['max_value']
    assert max_value == str(expected_max_value)


HIGHER_TIPS_EXP_MARKS = [
    pytest.mark.experiments3(
        name='bigger_tips_suggestions_choices',
        match={'predicate': {'type': 'true'}, 'enabled': True},
        consumers=['protocol/taxiontheway'],
        clauses=[
            {
                'title': 'test_clause',
                'value': {
                    'ranges': [
                        {
                            'from': 99,
                            'to': 400,
                            'replace': [
                                # position 0 cant replace 'no tip option'
                                {'position': 0, 'percent': 100, 'ceil': 500},
                                {'position': 2, 'percent': 25, 'ceil': 50},
                                {'position': 3, 'percent': 50, 'ceil': 50},
                                # position 4 is out of range
                                {'position': 4, 'percent': 100, 'ceil': 500},
                            ],
                        },
                    ],
                },
                'predicate': {'type': 'true'},
            },
        ],
    ),
]


@pytest.mark.filldb(
    orders='fixed_transporting', order_proc='fixed_transporting',
)
@pytest.mark.config(
    FLAT_TIPS_SETTINGS_V3={
        'countries': {
            'rus': {
                '__default__': {
                    'log_base': 14,
                    'percents': [5, 10, 15],
                    'manual_entry_allowed': True,
                    'decimal_digits': 0,
                    'min_tips_value': 10,
                    'tips_limit': {'max_tips': 100},
                    'base_numerator': 10,
                    'base_denominator': 10,
                    'additional_constant': 1,
                },
            },
        },
        'zones': {},
    },
)
@pytest.mark.user_experiments('tips_flat')
@pytest.mark.parametrize(
    ['ride_price', 'expected_tips_choices'],
    [
        pytest.param(98, [0, 5, 10, 15]),
        pytest.param(100, [0, 6, 11, 16]),
        pytest.param(231, [0, 20, 30, 40]),
        pytest.param(431, [0, 30, 50, 70]),
        pytest.param(98, [0, 5, 10, 15], marks=HIGHER_TIPS_EXP_MARKS),
        pytest.param(99, [0, 5, 50, 50], marks=HIGHER_TIPS_EXP_MARKS),
        pytest.param(100, [0, 6, 50, 50], marks=HIGHER_TIPS_EXP_MARKS),
        pytest.param(101, [0, 6, 50, 100], marks=HIGHER_TIPS_EXP_MARKS),
        pytest.param(231, [0, 20, 100, 150], marks=HIGHER_TIPS_EXP_MARKS),
        pytest.param(399, [0, 20, 100, 200], marks=HIGHER_TIPS_EXP_MARKS),
        pytest.param(400, [0, 30, 50, 70], marks=HIGHER_TIPS_EXP_MARKS),
        pytest.param(431, [0, 30, 50, 70], marks=HIGHER_TIPS_EXP_MARKS),
    ],
)
def test_tow_higher_tips_suggestions_choices_exp(
        taxi_protocol, db, ride_price, expected_tips_choices,
):
    order_id = '8c83b49edb274ce0992f337061047375'
    db.order_proc.update(
        {'_id': order_id},
        {'$set': {'order.fixed_price.price_original': ride_price}},
    )
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': order_id,
        },
    )
    assert response.status_code == 200
    content = response.json()
    tips_suggestions_variant = content['tips_suggestions']['variants'][0]
    tips_choices = [c['value'] for c in tips_suggestions_variant['choices']]
    assert tips_choices == expected_tips_choices


_DEFAULT_TIPS_CONFIG = {
    '__default__': {
        'log_base': 14,
        'percents': [5, 10, 15],
        'manual_entry_allowed': True,
        'decimal_digits': 0,
        'min_tips_value': 10,
        'tips_limit': {'max_tips': 100},
        'base_numerator': 10,
        'base_denominator': 10,
        'additional_constant': 1,
    },
}


@pytest.mark.filldb(
    orders='fixed_transporting', order_proc='fixed_transporting',
)
@pytest.mark.user_experiments('tips_flat')
@pytest.mark.parametrize(
    ['is_tips_suggestions_expected'],
    [
        # by country
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    FLAT_TIPS_SETTINGS_V3={
                        'countries': {'rus': _DEFAULT_TIPS_CONFIG},
                        'zones': {},
                    },
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    FLAT_TIPS_SETTINGS_V3={
                        'countries': {'wrong': _DEFAULT_TIPS_CONFIG},
                        'zones': {},
                    },
                ),
            ],
        ),
        # by zone
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    FLAT_TIPS_SETTINGS_V3={
                        'countries': {},
                        'zones': {'moscow': _DEFAULT_TIPS_CONFIG},
                    },
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    FLAT_TIPS_SETTINGS_V3={
                        'countries': {},
                        'zones': {'wrong': _DEFAULT_TIPS_CONFIG},
                    },
                ),
            ],
        ),
        # fallback to country
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    FLAT_TIPS_SETTINGS_V3={
                        'countries': {'rus': _DEFAULT_TIPS_CONFIG},
                        'zones': {'wrong': _DEFAULT_TIPS_CONFIG},
                    },
                ),
            ],
        ),
    ],
)
def test_tow_tips_config(taxi_protocol, is_tips_suggestions_expected):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    if is_tips_suggestions_expected:
        assert 'tips_suggestions' in content
    else:
        assert 'tips_suggestions' not in content


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(
    orders='fixed_transporting_no_card', order_proc='fixed_transporting',
)
@pytest.mark.fixture_now(datetime.timedelta(minutes=10))
def test_tow_tips_no_card(
        taxi_protocol, mockserver, default_driver_position, db, config,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['tips'] == {
        'type': '',
        'available': False,
        'value': 0,
        'decimal_value': '0',
    }


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(
    orders='fixed_transporting', order_proc='fixed_transporting',
)
@pytest.mark.fixture_now(datetime.timedelta(minutes=10))
@pytest.mark.user_experiments('tips_flat')
@pytest.mark.config(
    FLAT_TIPS_SETTINGS_V3={
        'countries': {
            'rus': {
                '__default__': {
                    'log_base': 14,
                    'percents': [5, 10, 15],
                    'manual_entry_allowed': True,
                    'decimal_digits': 0,
                    'min_tips_value': 10,
                    'tips_limit': {'max_tips': 100},
                    'base_numerator': 10,
                    'base_denominator': 10,
                    'additional_constant': 1,
                    'disabled': True,
                },
            },
        },
        'zones': {},
    },
)
@pytest.mark.parametrize(
    'ride_price',
    [
        -100,  # Чаевых и так не должно быть
        0,  # Не должно быть, но 0
        99,  # Чаевые должны быть, но мы их отключаем
    ],
)
def test_totw_tips_tariff_disabled_true(
        taxi_protocol, default_driver_position, db, ride_price,
):
    """
    Ride_price list has prices when tips may or may not exist.
    In this test they must be disabled and suggestions list must absent.
    """
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'order.fixed_price.price_original': ride_price}},
    )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()

    assert content['tips'] == {
        'available': False,
        'type': 'flat',
        'value': 0,
        'decimal_value': '0',
    }

    assert 'tips_suggestions' not in content


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(
    orders='fixed_transporting', order_proc='fixed_transporting',
)
@pytest.mark.fixture_now(datetime.timedelta(minutes=10))
@pytest.mark.user_experiments('tips_flat')
@pytest.mark.config(
    FLAT_TIPS_SETTINGS_V3={
        'countries': {
            'rus': {
                '__default__': {
                    'log_base': 14,
                    'percents': [5, 10, 15],
                    'manual_entry_allowed': True,
                    'decimal_digits': 0,
                    'min_tips_value': 10,
                    'tips_limit': {'max_tips': 100},
                    'base_numerator': 10,
                    'base_denominator': 10,
                    'additional_constant': 1,
                    'disabled': True,
                },
            },
        },
        'zones': {},
    },
)
@pytest.mark.parametrize(
    'order_tips,active_order_exp',
    [
        ({'type': 'percent', 'value': 5.0}, True),
        ({'type': 'percent', 'value': 0.0}, True),
        ({'type': 'flat', 'value': 5.0}, True),
        ({'type': 'flat', 'value': 0.0}, True),
        ({'type': 'percent', 'value': 5.0}, False),
        ({'type': 'percent', 'value': 0.0}, False),
        ({'type': 'flat', 'value': 5.0}, False),
        ({'type': 'flat', 'value': 0.0}, False),
    ],
)
def test_totw_tips_tariff_disabled_nonzero_tips(
        taxi_protocol,
        default_driver_position,
        db,
        order_tips,
        active_order_exp,
):
    order_id = '8c83b49edb274ce0992f337061047375'
    order_experiments = []
    if active_order_exp:
        order_experiments.append('tips_flat')

    db.orders.update(
        {'_id': order_id},
        {
            '$set': {
                'creditcard.tips': order_tips,
                'experiments': order_experiments,
            },
        },
    )
    db.order_proc.update(
        {'_id': order_id},
        {
            '$set': {
                'order.creditcard.tips': order_tips,
                'order.experiments': order_experiments,
            },
        },
    )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': order_id,
        },
    )
    assert response.status_code == 200
    content = response.json()

    assert content['tips']['value'] == 0
    assert content['tips']['decimal_value'] == '0'
    assert not content['tips']['available']

    assert 'tips_suggestions' not in content


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(
    orders='fixed_transporting', order_proc='fixed_transporting',
)
@pytest.mark.fixture_now(datetime.timedelta(minutes=10))
@pytest.mark.user_experiments('tips_flat')
@pytest.mark.config(
    FLAT_TIPS_SETTINGS_V3={
        'countries': {
            'rus': {
                '__default__': {
                    'log_base': 14,
                    'percents': [5, 10, 15],
                    'manual_entry_allowed': True,
                    'decimal_digits': 0,
                    'min_tips_value': 10,
                    'tips_limit': {'max_tips': 100},
                    'base_numerator': 10,
                    'base_denominator': 10,
                    'additional_constant': 1,
                },
            },
        },
        'zones': {},
    },
)
@pytest.mark.parametrize(
    'order_tips,active_order_exp,contains_suggestions',
    [
        ({'type': 'percent', 'value': 5.0}, True, True),
        ({'type': 'percent', 'value': 0.0}, True, True),
        ({'type': 'flat', 'value': 5.0}, True, True),
        ({'type': 'flat', 'value': 0.0}, True, True),
        ({'type': 'percent', 'value': 5.0}, False, False),
        ({'type': 'percent', 'value': 0.0}, False, False),
        ({'type': 'flat', 'value': 5.0}, False, True),
        ({'type': 'flat', 'value': 0.0}, False, True),
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_tow_tips_suggestion(
        taxi_protocol,
        default_driver_position,
        db,
        order_tips,
        active_order_exp,
        contains_suggestions,
        mock_order_core,
        order_core_switch_on,
):
    order_id = '8c83b49edb274ce0992f337061047375'
    order_experiments = []
    if active_order_exp:
        order_experiments.append('tips_flat')

    db.orders.update(
        {'_id': order_id},
        {
            '$set': {
                'creditcard.tips': order_tips,
                'experiments': order_experiments,
            },
        },
    )
    db.order_proc.update(
        {'_id': order_id},
        {
            '$set': {
                'order.creditcard.tips': order_tips,
                'order.experiments': order_experiments,
            },
        },
    )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': order_id,
        },
    )
    assert response.status_code == 200
    content = response.json()

    assert ('tips_suggestions' in content) == contains_suggestions
    assert mock_order_core.get_fields_times_called == int(order_core_switch_on)


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(
    orders='fixed_transporting', order_proc='fixed_transporting',
)
@pytest.mark.fixture_now(datetime.timedelta(minutes=10))
@pytest.mark.user_experiments('tips_flat')
@pytest.mark.config(
    FLAT_TIPS_SETTINGS_V3={
        'countries': {
            'rus': {
                '__default__': {
                    'log_base': 14,
                    'percents': [15, 5, 10],
                    'manual_entry_allowed': True,
                    'decimal_digits': 0,
                    'min_tips_value': 10,
                    'tips_limit': {'max_tips': 100},
                    'base_numerator': 10,
                    'base_denominator': 10,
                    'additional_constant': 1,
                },
            },
        },
        'zones': {},
    },
    CURRENCY_FORMATTING_RULES={'__default__': {'__default__': 2}},
)
@pytest.mark.parametrize(
    'ride_price,tips_choices',
    [
        (
            431,
            [
                {'type': 'flat', 'value': 0, 'decimal_value': '0'},
                {'type': 'flat', 'value': 30, 'decimal_value': '30'},
                {'type': 'flat', 'value': 50, 'decimal_value': '50'},
                {'type': 'flat', 'value': 70, 'decimal_value': '70'},
            ],
        ),
    ],
)
def test_totw_tips_order(
        taxi_protocol, default_driver_position, db, ride_price, tips_choices,
):
    """
    Because now config has jsonschema validation there is no
    percents order rule.
    """
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'order.fixed_price.price_original': ride_price}},
    )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()

    expected_answer = {
        'variants': [
            {
                'choices': tips_choices,
                'customize_options': {
                    'decimal_digits': 0,
                    'manual_entry_allowed': True,
                    'max_value': '100',
                    'min_value': '10',
                },
                'match': {'max_rating': 5, 'min_rating': 4},
            },
        ],
    }

    assert content['tips_suggestions'] == expected_answer


@pytest.mark.parametrize(
    'payment_events,payment_changes,updated_reqs',
    [
        ([], [], []),
        (
            [
                {
                    'c': datetime.datetime(2017, 8, 2, 14, 56, 46, 964000),
                    'data': {
                        'from': {'type': 'card'},
                        'reason': {'code': 'NEED_CVN'},
                        'to': {'type': 'cash'},
                    },
                    'status': 'success',
                    'type': 'moved_to_cash_by_antifraud',
                },
            ],
            [
                {
                    'from': {'payment_method_id': '', 'type': 'card'},
                    'reason': {
                        'code': 'NEED_CVN',
                        'text': (
                            'Need 3-digit credit card '
                            'security code (CVN) to continue'
                        ),
                    },
                    'to': {'type': 'cash'},
                },
            ],
            [
                {
                    'reason': {
                        'text': (
                            'Need 3-digit credit card '
                            'security code (CVN) to continue'
                        ),
                        'code': 'NEED_CVN',
                    },
                    'requirement': 'creditcard',
                    'value': False,
                },
            ],
        ),
        (
            [
                {
                    'c': datetime.datetime(2017, 8, 2, 14, 56, 46, 964000),
                    'data': {
                        'from': {'type': 'card'},
                        'reason': {'code': 'SILENT'},
                        'to': {'type': 'cash'},
                    },
                    'status': 'success',
                    'type': 'moved_to_cash_by_antifraud',
                },
            ],
            [
                {
                    'from': {'payment_method_id': '', 'type': 'card'},
                    'reason': {'code': 'SILENT'},
                    'to': {'type': 'cash'},
                },
            ],
            [
                {
                    'reason': {'code': 'SILENT'},
                    'requirement': 'creditcard',
                    'value': False,
                },
            ],
        ),
        (
            [
                {
                    'c': datetime.datetime(2017, 8, 2, 15, 4, 9, 190000),
                    'data': {
                        'push_id': '55161821475a2fe2f71b3e3ae0200519f7269bfd',
                        'trust_payment_id': '5981e9db795be205036ac8e3',
                        'url': (
                            'https://tmongo1f.fin.yandex.ru/pchecks/0a0453fd7'
                            '36be975643f658a2dc75f1b/receipts/0a0453fd736be97'
                            '5643f658a2dc75f1b?mode=mobile'
                        ),
                    },
                    'status': 'success',
                    'type': 'receipt_sent',
                },
            ],
            [],
            [],
        ),
        (
            [
                {
                    'c': datetime.datetime(2017, 8, 2, 15, 3, 53, 404000),
                    'data': {
                        'from': {'type': 'cash'},
                        'reason': {'code': 'INITIATED_BY_USER'},
                        'to': {'type': 'card'},
                    },
                    'status': 'success',
                    'type': 'paid_by_user',
                },
            ],
            [],
            [],
        ),
        (
            [
                {
                    'c': datetime.datetime(2017, 8, 2, 14, 56, 46, 964000),
                    'data': {
                        'from': {'type': 'card'},
                        'reason': {'code': 'NEED_CVN'},
                        'to': {'type': 'cash'},
                    },
                    'status': 'success',
                    'type': 'moved_to_cash_by_check_card',
                },
            ],
            [
                {
                    'to': {'type': 'cash'},
                    'reason': {
                        'text': (
                            'Need 3-digit credit card '
                            'security code (CVN) to continue'
                        ),
                        'code': 'NEED_CVN',
                    },
                    'from': {'type': 'card', 'payment_method_id': ''},
                },
            ],
            [
                {
                    'reason': {
                        'text': (
                            'Need 3-digit credit card '
                            'security code (CVN) to continue'
                        ),
                        'code': 'NEED_CVN',
                    },
                    'requirement': 'creditcard',
                    'value': False,
                },
            ],
        ),
        (
            [
                {
                    'c': datetime.datetime(2017, 8, 2, 14, 56, 46, 964000),
                    'data': {
                        'from': {'type': 'card'},
                        'reason': {'code': 'NEED_CVN'},
                        'to': {'type': 'cash'},
                    },
                    'status': 'success',
                    'type': 'moved_to_cash_by_update_transactions',
                },
            ],
            [
                {
                    'to': {'type': 'cash'},
                    'reason': {
                        'text': (
                            'Need 3-digit credit card '
                            'security code (CVN) to continue'
                        ),
                        'code': 'NEED_CVN',
                    },
                    'from': {'type': 'card', 'payment_method_id': ''},
                },
            ],
            [
                {
                    'reason': {
                        'text': (
                            'Need 3-digit credit card '
                            'security code (CVN) to continue'
                        ),
                        'code': 'NEED_CVN',
                    },
                    'requirement': 'creditcard',
                    'value': False,
                },
            ],
        ),
        (
            [
                {
                    'c': datetime.datetime(2017, 8, 2, 14, 56, 46, 964000),
                    'data': {
                        'from': {'type': 'card'},
                        'reason': {'code': 'ORDER_EXPIRED'},
                        'to': {'type': 'cash'},
                    },
                    'status': 'success',
                    'type': 'closed_with_cash',
                },
            ],
            [
                {
                    'to': {'type': 'cash'},
                    'reason': {
                        'text': 'Order status is unknown',
                        'code': 'ORDER_EXPIRED',
                    },
                    'from': {'type': 'card', 'payment_method_id': ''},
                },
            ],
            [
                {
                    'reason': {
                        'text': 'Order status is unknown',
                        'code': 'ORDER_EXPIRED',
                    },
                    'requirement': 'creditcard',
                    'value': False,
                },
            ],
        ),
        (
            [
                {
                    'c': datetime.datetime(2017, 8, 2, 14, 56, 46, 964000),
                    'data': {
                        'from': {'type': 'card'},
                        'reason': {'code': 'ORDER_CANCELLED'},
                        'to': {'type': 'cash'},
                    },
                    'status': 'success',
                    'type': 'closed_with_cash',
                },
            ],
            [
                {
                    'to': {'type': 'cash'},
                    'reason': {
                        'text': 'Your order has been cancelled',
                        'code': 'ORDER_CANCELLED',
                    },
                    'from': {'type': 'card', 'payment_method_id': ''},
                },
            ],
            [
                {
                    'reason': {
                        'text': 'Your order has been cancelled',
                        'code': 'ORDER_CANCELLED',
                    },
                    'requirement': 'creditcard',
                    'value': False,
                },
            ],
        ),
        (
            [
                {
                    'c': datetime.datetime(2017, 8, 2, 14, 56, 46, 964000),
                    'data': {
                        'from': {'type': 'card'},
                        'reason': {'code': 'UNUSABLE_CARD'},
                        'to': {'type': 'cash'},
                    },
                    'status': 'success',
                    'type': 'remembered_cvn',
                },
            ],
            [
                {
                    'to': {'type': 'cash'},
                    'reason': {
                        'text': 'Unable to complete payment',
                        'code': 'UNUSABLE_CARD',
                    },
                    'from': {'type': 'card', 'payment_method_id': ''},
                },
            ],
            [
                {
                    'reason': {
                        'text': 'Unable to complete payment',
                        'code': 'UNUSABLE_CARD',
                    },
                    'requirement': 'creditcard',
                    'value': False,
                },
            ],
        ),
        (
            [
                {
                    'c': datetime.datetime(2017, 8, 2, 14, 56, 46, 964000),
                    'data': {
                        'from': {'type': 'card'},
                        'reason': {'code': 'NEED_CVN'},
                        'to': {'type': 'cash'},
                    },
                    'status': 'success',
                    'type': 'remembered_cvn',
                },
            ],
            [
                {
                    'to': {'type': 'cash'},
                    'reason': {
                        'text': (
                            'Need 3-digit credit card '
                            'security code (CVN) to continue'
                        ),
                        'code': 'NEED_CVN',
                    },
                    'from': {'type': 'card', 'payment_method_id': ''},
                },
            ],
            [
                {
                    'reason': {
                        'text': (
                            'Need 3-digit credit card '
                            'security code (CVN) to continue'
                        ),
                        'code': 'NEED_CVN',
                    },
                    'requirement': 'creditcard',
                    'value': False,
                },
            ],
        ),
        (
            [
                {
                    'c': datetime.datetime(2017, 8, 2, 14, 56, 46, 964000),
                    'data': {
                        'from': {'type': 'card'},
                        'reason': {'code': 'DEBT_ALLOWED'},
                        'to': {'type': 'card'},
                    },
                    'status': 'success',
                    'type': 'debt_allowed_by_antifraud',
                },
            ],
            [
                {
                    'to': {'type': 'card', 'payment_method_id': ''},
                    'reason': {
                        'text': (
                            'The order can not be paid by card, '
                            'you go in debt'
                        ),
                        'code': 'DEBT_ALLOWED',
                    },
                    'from': {'type': 'card', 'payment_method_id': ''},
                },
            ],
            [
                {
                    'reason': {
                        'text': (
                            'The order can not be paid by card, '
                            'you go in debt'
                        ),
                        'code': 'DEBT_ALLOWED',
                    },
                    'requirement': 'creditcard',
                    'value': True,
                },
            ],
        ),
    ],
)
@pytest.mark.filldb(orders='payment_events')
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_tow_payment_events(
        payment_events,
        payment_changes,
        updated_reqs,
        taxi_protocol,
        default_driver_position,
        db,
):
    db.orders.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'payment_events': payment_events}},
    )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )

    result = response.json()
    assert result['payment_changes'] == payment_changes
    assert result['request'].get('updated_requirements', []) == updated_reqs


@pytest.mark.filldb(order_proc='driver_phone_without_forwarding')
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_driver_phone_totw_without_forwarding(
        taxi_protocol, mockserver, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'waiting'
    assert content['tariff']['class'] == 'econom'
    assert content['driver'] == {
        'car': [37.58917997300821, 55.73341076871702],
        'color': 'фиолетовый',
        'color_code': '4A2197',
        'model': 'Skoda Fabia',
        'name': 'Бородач Исак Арнольдович',
        'overdue': False,
        'phone': '+79321259615',
        'need_request_driver_phone': True,
        'plates': 'Х492НК77',
        'way_time': 0,
        'yellow_car_number': False,
        'photo_url': (
            'https://tc.mobile.yandex.net/static/images/'
            '41007/54630f09-1f14-4bf3-8c24-04fdd7059107'
        ),
        'tag': DRIVERTAG,
    }


@pytest.mark.filldb(order_proc='driver_phone_forwarding')
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_driver_phone_totw_forwarding(
        taxi_protocol, mockserver, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'waiting'
    assert content['tariff']['class'] == 'econom'
    assert content['driver'] == {
        'car': [37.58917997300821, 55.73341076871702],
        'color': 'фиолетовый',
        'color_code': '4A2197',
        'model': 'Skoda Fabia',
        'name': 'Бородач Исак Арнольдович',
        'overdue': False,
        'phone': '+7123456789,,007',
        'forwarding': {'ext': '007', 'phone': '+7123456789'},
        'plates': 'Х492НК77',
        'way_time': 0,
        'yellow_car_number': False,
        'photo_url': (
            'https://tc.mobile.yandex.net/static/images/'
            '41007/54630f09-1f14-4bf3-8c24-04fdd7059107'
        ),
        'tag': DRIVERTAG,
    }


@pytest.mark.filldb(order_proc='driver_phone_forwarding_no_gate')
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_driver_phone_totw_forwarding_no_gate(
        taxi_protocol, mockserver, default_driver_position,
):
    """
    Possible case when totw is called before gateway was set,
    backend never sends any phone number (prod solution)
    """
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'waiting'
    assert content['tariff']['class'] == 'econom'
    assert content['driver'] == {
        'car': [37.58917997300821, 55.73341076871702],
        'color': 'фиолетовый',
        'color_code': '4A2197',
        'model': 'Skoda Fabia',
        'name': 'Бородач Исак Арнольдович',
        'overdue': False,
        'plates': 'Х492НК77',
        'way_time': 0,
        'yellow_car_number': False,
        'photo_url': (
            'https://tc.mobile.yandex.net/static/images/'
            '41007/54630f09-1f14-4bf3-8c24-04fdd7059107'
        ),
        'tag': DRIVERTAG,
    }


@pytest.mark.filldb(order_proc='driver_phone_forwarding')
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.config(
    HIDE_DRIVER_INFO={
        '__default__': {
            'car_number': False,
            'driver_phone': True,
            'fio': False,
            'park_phone': False,
        },
    },
)
def test_driver_phone_totw_with_forwarding_hide_driver_phone(
        taxi_protocol, mockserver, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'waiting'
    assert content['tariff']['class'] == 'econom'
    assert content['driver'] == {
        'car': [37.58917997300821, 55.73341076871702],
        'color': 'фиолетовый',
        'color_code': '4A2197',
        'model': 'Skoda Fabia',
        'name': 'Бородач Исак Арнольдович',
        'overdue': False,
        'phone': '+7123456789,,007',
        'forwarding': {'ext': '007', 'phone': '+7123456789'},
        'plates': 'Х492НК77',
        'way_time': 0,
        'yellow_car_number': False,
        'photo_url': (
            'https://tc.mobile.yandex.net/static/images/'
            '41007/54630f09-1f14-4bf3-8c24-04fdd7059107'
        ),
        'tag': DRIVERTAG,
    }


@pytest.mark.filldb(order_proc='driver_phone_forwarding_failed')
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_driver_phone_totw_forwarding_failed(
        taxi_protocol, mockserver, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'waiting'
    assert content['tariff']['class'] == 'econom'
    assert content['driver'] == {
        'car': [37.58917997300821, 55.73341076871702],
        'color': 'фиолетовый',
        'color_code': '4A2197',
        'model': 'Skoda Fabia',
        'name': 'Бородач Исак Арнольдович',
        'overdue': False,
        'plates': 'Х492НК77',
        'phone': '+79321259615',
        'need_request_driver_phone': True,
        'way_time': 0,
        'yellow_car_number': False,
        'photo_url': (
            'https://tc.mobile.yandex.net/static/images/'
            '41007/54630f09-1f14-4bf3-8c24-04fdd7059107'
        ),
        'tag': DRIVERTAG,
    }


@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_tow_with_chat(taxi_protocol, mockserver, default_driver_position, db):
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'chat_id': 'test_chat_id', 'chat_visible': True}},
    )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['driverclientchat_enabled'] is True


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.translations(
    geoareas={'moscow': {'en': 'Москва'}},
    tariff={
        'old_category_name.econom': {'en': 'Econom'},
        'old_category_name.cargo': {'en': 'Cargo'},
    },
)
@pytest.mark.filldb(orders='transporting', order_proc='transporting')
@pytest.mark.config(
    TAXIONTHEWAY_DRIVERCALL_TRANSPORTING_CATEGORIES=[
        'cargo',
        'express',
        'personal_driver',
    ],
)
@pytest.mark.parametrize(
    'tariff,call_enabled', [('cargo', True), ('econom', False)],
)
def test_tow_call_in_transporting(
        taxi_protocol,
        mockserver,
        default_driver_position,
        db,
        tariff,
        call_enabled,
):
    for status, isenabled in [
            ('driving', True),
            ('waiting', True),
            ('transporting', call_enabled),
            ('complete', False),
    ]:
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {
                '$set': {
                    'order.performer.tariff.class': tariff,
                    'order.status': status,
                    'order.taxi_status': status,
                },
            },
        )

        response = taxi_protocol.post(
            '3.0/taxiontheway',
            {
                'format_currency': True,
                'id': 'b300bda7d41b4bae8d58dfa93221ef16',
                'orderid': '8c83b49edb274ce0992f337061047375',
            },
        )
        assert response.status_code == 200
        content = response.json()
        assert content['drivercall_enabled'] is isenabled


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(orders='driving', order_proc='driving')
@pytest.mark.config(
    TAXIONTHEWAY_CARD_SWITCH_MINVERSION={
        'iphone': {'version': (3, 98, 0)},
        'android': {'version': (3, 52, 0)},
    },
)
@pytest.mark.parametrize(
    'ua,allowed',
    [
        (
            'ru.yandex.taxi.inhouse/3.98.8966 '
            '(iPhone; iPhone7,1; iOS 10.3.3; Darwin)',
            True,
        ),
        (
            'ru.yandex.taxi.inhouse/3.97.3456 '
            '(iPhone; iPhone7,1; iOS 10.3.3; Darwin)',
            False,
        ),
        (
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:53.0) '
            'Gecko/20100101 Firefox/53.0',
            False,
        ),
        ('yandex-taxi/3.29.0.8857 Android/7.0 (samsung; SM-G930F)', False),
        ('yandex-taxi/3.52.0.0000 Android/7.0 (samsung; SM-G930F)', True),
        ('yandex-taxi/3.52.0.0001 Android/7.0 (samsung; SM-G930F)', True),
        ('yandex-taxi/3.52.1.0000 Android/7.0 (samsung; SM-G930F)', True),
        ('yandex-taxi/3.51.9.9999 Android/7.0 (samsung; SM-G930F)', False),
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='yandex_card',
    consumers=['protocol/taxiontheway'],
    clauses=[
        {
            'title': '1',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
def test_tow_ua(
        taxi_protocol,
        mockserver,
        default_driver_position,
        maps_router,
        db,
        ua,
        allowed,
):
    db.orders.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'payment_tech.type': 'card'}},
    )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
        headers={'User-Agent': ua},
    )
    assert response.status_code == 200
    content = response.json()

    assert 'allowed_changes' in content
    payment_change = list(
        filter(lambda i: i['name'] == 'payment', content['allowed_changes']),
    )
    if allowed:
        assert len(payment_change) == 1
        assert 'card' in payment_change[0]['available_methods']
        assert 'applepay' in payment_change[0]['available_methods']
        assert 'yandex_card' in payment_change[0]['available_methods']
    else:
        assert len(payment_change) == 0


@pytest.mark.config(CURRENCY_FORMATTING_RULES={'RUB': {'__default__': 1}})
@pytest.mark.parametrize(
    'ride_cost,price,overpay',
    [(2010000, 151, '50'), (2001500, 200, '0.2'), (2000100, 200, None)],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(orders='with_hold', order_proc='with_hold')
@pytest.mark.translations(
    client_messages={
        'taxiontheway.paid_too_much': {
            'en': 'Reserverd %(cost)s more. Will be refunded',
        },
    },
)
def test_with_hold(
        taxi_protocol,
        mockserver,
        default_driver_position,
        maps_router,
        ride_cost,
        price,
        overpay,
        db,
):
    db.orders.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$set': {
                'payment_tech.type': 'card',
                'fixed_price.price': price,
                'billing_tech.transactions.0.sum.ride': ride_cost,
            },
        },
    )
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$set': {
                'order.fixed_price.price': price,
                'payment_tech.paid_amount.ride': ride_cost,
            },
        },
    )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    if overpay:
        assert content['cost_message_details']['extra_info'] == [
            {
                'type': 'paid_too_much',
                'text': (
                    'Reserverd %s $SIGN$$CURRENCY$ more. Will be refunded'
                    % (overpay,)
                ),
            },
        ]
    else:
        assert 'cost_message_details' not in content


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(
    users='no_due',
    user_phones='no_due',
    cities='no_due',
    tariff_settings='no_due',
)
@pytest.mark.fixture_now(datetime.timedelta(minutes=10))
def test_tow_no_due(taxi_protocol, mockserver, tracker, now, db, load):
    @mockserver.json_handler('/order-archive/v1/order_proc/retrieve')
    def archive_api_handler(request):
        order_proc = bson.json_util.loads(
            load('archive_order_proc_no_due.json'),
        )
        response_json = {'doc': order_proc}
        response = bson.BSON.encode(response_json)
        return mockserver.make_response(response)

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': '20c8eb68e4824feca23b8401a19d0856',
            'orderid': 'e7b3130e5e9c4edd8cfd2ae754c58600',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'complete'
    assert content['cost_message_details'] == {
        'extra_info': [
            {
                'text': (
                    'The cost of the ride was modified, as the order was not '
                    'closed in the location that had been specified earlier.'
                ),
                'type': 'taximeter_cost_message',
            },
        ],
    }
    assert content['tips'] == {
        'type': '',
        'value': 0,
        'available': False,
        'decimal_value': '0',
    }


@pytest.mark.config(
    TRACKER_ADJUST_EXPERIMENTS_PARAMETRS={
        'adjust_additional_options_1': {
            'part_count': 1,
            'part_distance': 1,
            'part_time': 1,
        },
    },
)
@pytest.mark.filldb(orders='transporting', order_proc='transporting')
@pytest.mark.driver_experiments('adjust_additional_options_1')
def test_experiment_position_request(taxi_protocol, mockserver):
    testcase = {'called': 0}

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        testcase['called'] += 1
        testcase['query_string'] = request.query_string
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )

    query = dict(
        map(
            lambda x: x.split('='),
            testcase['query_string'].decode().split('&'),
        ),
    )

    assert query == {'id': '999012_a5709ce56c2740d9a536650f5390de0b'}

    assert response.status_code == 200
    assert 'brandings' not in response.json()


@pytest.mark.config(
    TRACKER_ADJUST_EXPERIMENTS_PARAMETRS={
        'adjust_additional_options_1': {
            'part_count': 1,
            'part_distance': 1,
            'part_time': 1,
        },
    },
)
@pytest.mark.filldb(orders='transporting', order_proc='transporting')
def test_position_request(taxi_protocol, mockserver):
    testcase = {'called': 0}

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        testcase['called'] += 1
        testcase['query_string'] = request.query_string
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )

    query = dict(
        map(
            lambda x: x.split('='),
            testcase['query_string'].decode().split('&'),
        ),
    )

    assert query == {'id': '999012_a5709ce56c2740d9a536650f5390de0b'}

    assert response.status_code == 200


promo_stories_views = ['ask_feedback', 'transporting', 'main']


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='higher_class_congratulation_settings',
    consumers=['protocol/taxiontheway'],
    clauses=[
        {
            'title': '',
            'value': {
                'higher_class_congratulation_settings': {
                    'moscow': {
                        'econom': [
                            {'to_class': 'comfortplus', 'probability': 1.0},
                            {'to_class': 'business', 'probability': 1.0},
                        ],
                    },
                },
                'enabled': True,
            },
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.translations(
    client_messages={
        'taxiontheway.highest_tariff.title_v2': {
            'ru': 'Заголовок поздравления',
        },
        'taxiontheway.highest_tariff.text_v2': {
            'ru': (
                'Вы поедете по тарифу «%(original)s» '
                'на машине из «%(highest)sа»'
            ),
        },
    },
    tariff={
        'old_category_name.econom': {'ru': 'Эконом'},
        'old_category_name.comfortplus': {'ru': 'Комфортплюс'},
    },
)
def test_tow_congratulation_1(
        taxi_protocol, mockserver, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
        headers={'Accept-Language': 'ru-RU'},
    )
    assert response.status_code == 200
    content = response.json()
    assert content['higher_class_dialog'] == {
        'image': 'class_comfortplus_car',
        'title': 'Заголовок поздравления',
        'text': 'Вы поедете по тарифу «Эконом» на машине из «Комфортплюса»',
        'class_after_upgrade': 'comfortplus',
        'class_name_after_upgrade': 'Комфортплюс',
    }


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='quality_question',
    consumers=['client_protocol/taxiontheway'],
    clauses=[
        {
            'title': '',
            'value': {
                'link': 'https://forms.yandex.ru/surveys/10015306/',
                'enabled': True,
            },
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'driver_classes',
                                'set_elem_type': 'string',
                                'value': 'comfortplus',
                            },
                            'type': 'contains',
                        },
                        {
                            'init': {
                                'arg_name': 'tariff_class',
                                'arg_type': 'string',
                                'value': 'econom',
                            },
                            'type': 'eq',
                        },
                    ],
                },
                'type': 'all_of',
            },
        },
    ],
)
def test_secret_buyer_survey_select_by_class(
        taxi_protocol, mockserver, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
        headers={'Accept-Language': 'ru-RU'},
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content['typed_experiments']['items']) == 1
    assert (
        content['typed_experiments']['items'][0]['name'] == 'quality_question'
    )
    assert (
        content['typed_experiments']['items'][0]['value']['link']
        == 'https://forms.yandex.ru/surveys/10015306/'
    )


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='higher_class_congratulation_settings',
    consumers=['protocol/taxiontheway'],
    clauses=[
        {
            'title': '',
            'value': {
                'higher_class_congratulation_settings': {
                    'moscow': {
                        'econom': [
                            {'to_class': 'business', 'probability': 1.0},
                            {'to_class': 'comfortplus', 'probability': 1.0},
                        ],
                    },
                },
                'enabled': True,
            },
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.translations(
    client_messages={
        'taxiontheway.highest_tariff.title_v2': {
            'ru': 'Заголовок поздравления',
        },
        'taxiontheway.highest_tariff.text_v2': {
            'ru': (
                'Вы поедете по тарифу «%(original)s» '
                'на машине из «%(highest)sа»'
            ),
        },
    },
    tariff={
        'old_category_name.econom': {'ru': 'Эконом'},
        'old_category_name.business': {'ru': 'Комфорт'},
    },
)
def test_tow_congratulation_2(
        taxi_protocol, mockserver, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
        headers={'Accept-Language': 'ru-RU'},
    )
    assert response.status_code == 200
    content = response.json()
    assert content['higher_class_dialog'] == {
        'image': 'class_business_car',
        'title': 'Заголовок поздравления',
        'text': 'Вы поедете по тарифу «Эконом» на машине из «Комфорта»',
        'class_after_upgrade': 'business',
        'class_name_after_upgrade': 'Комфорт',
    }


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='higher_class_congratulation_settings',
    consumers=['protocol/taxiontheway'],
    clauses=[
        {
            'title': '',
            'value': {
                'higher_class_congratulation_settings': {
                    '__default__': {
                        '__default__': [
                            {'to_class': 'business', 'probability': 1.0},
                            {'to_class': 'comfortplus', 'probability': 1.0},
                        ],
                    },
                },
                'enabled': True,
            },
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.translations(
    client_messages={
        'taxiontheway.highest_tariff.title_v2': {
            'ru': 'Заголовок поздравления',
        },
        'taxiontheway.highest_tariff.text_v2': {
            'ru': (
                'Вы поедете по тарифу «%(original)s» '
                'на машине из «%(highest)sа»'
            ),
        },
    },
    tariff={
        'old_category_name.econom': {'ru': 'Эконом'},
        'old_category_name.business': {'ru': 'Комфорт'},
    },
)
def test_tow_congratulation_defaults(
        taxi_protocol, mockserver, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
        headers={'Accept-Language': 'ru-RU'},
    )
    assert response.status_code == 200
    content = response.json()
    assert content['higher_class_dialog'] == {
        'image': 'class_business_car',
        'title': 'Заголовок поздравления',
        'text': 'Вы поедете по тарифу «Эконом» на машине из «Комфорта»',
        'class_after_upgrade': 'business',
        'class_name_after_upgrade': 'Комфорт',
    }


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': False},
    name='higher_class_congratulation_settings',
    consumers=['protocol/taxiontheway'],
    clauses=[],
)
def test_tow_congratulation_none_1(
        taxi_protocol, mockserver, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
        headers={'Accept-Language': 'ru-RU'},
    )
    assert response.status_code == 200
    content = response.json()
    assert content.get('higher_class_dialog') is None


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='higher_class_congratulation_settings',
    consumers=['protocol/taxiontheway'],
    clauses=[
        {
            'title': '',
            'value': {
                'higher_class_congratulation_settings': {
                    'moscow': {
                        'econom': [{'to_class': 'vip', 'probability': 1.0}],
                    },
                },
                'enable': True,
            },
            'predicate': {'type': 'true'},
        },
    ],
)
def test_tow_congratulation_none_2(
        taxi_protocol, mockserver, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
        headers={'Accept-Language': 'ru-RU'},
    )
    assert response.status_code == 200
    content = response.json()
    assert content.get('higher_class_dialog') is None


def _check_can_make_more_orders(
        expected,
        taxi_protocol,
        load_json,
        expected_after_cancel=None,
        **http_kwargs,
):
    commit_resp = make_order(taxi_protocol, load_json, **http_kwargs)
    assert commit_resp.get('can_make_more_orders') == expected
    order_id = commit_resp['orderid']

    req_body = {'id': 'f4eb6aaa29ad4a6eb53f8a7620793561', 'orderid': order_id}

    # check totw doesn't return valuable field for non-terminal order status
    tow_resp = taxi_protocol.post('3.0/taxiontheway', req_body, **http_kwargs)
    assert tow_resp.status_code == 200
    assert tow_resp.json().get('can_make_more_orders') == 'not_modified'

    # cancel order
    if expected_after_cancel is None:
        expected_after_cancel = expected
    cancel_resp = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'break': 'user',
            'id': 'f4eb6aaa29ad4a6eb53f8a7620793561',
            'orderid': order_id,
        },
        **http_kwargs,
    )
    assert cancel_resp.status_code == 200
    can_make_more = cancel_resp.json().get('can_make_more_orders')
    assert can_make_more == expected_after_cancel

    # check totw returns field for terminal order status
    tow_resp = taxi_protocol.post('3.0/taxiontheway', req_body, **http_kwargs)
    assert tow_resp.status_code == 200
    assert tow_resp.json().get('can_make_more_orders') == expected_after_cancel


@pytest.mark.filldb(users='make_more_orders', user_phones='make_more_orders')
@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=1,
    MAX_CONCURRENT_ORDERS=1,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
)
def test_tow_no_can_make_more_orders(
        taxi_protocol, load_json, pricing_data_preparer,
):
    # disabled by parameter 'multiorder_calc_can_make_more_orders',
    # expect no field in response
    _check_can_make_more_orders('allowed', taxi_protocol, load_json)


@pytest.mark.filldb(users='make_more_orders', user_phones='make_more_orders')
@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
)
def test_tow_multiorder_can_make_more_orders(
        taxi_protocol, load_json, pricing_data_preparer,
):
    for i in range(2):
        commit_resp = make_order(taxi_protocol, load_json)
        assert commit_resp.get('can_make_more_orders') == 'allowed'

    _check_can_make_more_orders(
        'disallowed',
        taxi_protocol,
        load_json,
        expected_after_cancel='allowed',
    )


@pytest.mark.filldb(users='make_more_orders', user_phones='make_more_orders')
@pytest.mark.config(
    MAX_CONCURRENT_ORDERS=1,
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
)
def test_tow_can_make_more_orders(
        taxi_protocol, load_json, pricing_data_preparer,
):
    _check_can_make_more_orders(
        'disallowed',
        taxi_protocol,
        load_json,
        expected_after_cancel='allowed',
    )


USER_PHONE_ID = ObjectId('59246c5b6195542e9b084206')


@pytest.mark.config(
    MULTIORDER_ENABLING_MIN_COMPLETE_ORDERS_N=2,
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS_CHECK_COMPLETE_ORDERS=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi', 'android': 'yataxi'},
)
@pytest.mark.filldb(users='make_more_orders', user_phones='make_more_orders')
@pytest.mark.parametrize(
    'complete,can_make_more',
    [(1, 'disallowed'), (2, 'allowed'), (3, 'allowed')],
)
def test_tow_can_make_more_antifraud(
        taxi_protocol,
        db,
        load_json,
        complete,
        can_make_more,
        pricing_data_preparer,
):
    db.user_phones.find_and_modify(
        {'_id': USER_PHONE_ID}, {'$set': {'stat.complete': complete}},
    )
    _check_can_make_more_orders(
        can_make_more,
        taxi_protocol,
        load_json,
        expected_after_cancel='allowed',
    )


FRANCE_IP = '89.185.38.136'


@pytest.mark.filldb(users='make_more_orders', user_phones='make_more_orders')
@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=2,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
)
@pytest.mark.parametrize(
    'remote_ip,allowed_countries,expected_res',
    [
        (FRANCE_IP, None, 'allowed'),
        (FRANCE_IP, ['ru', 'us'], 'disallowed'),
        (FRANCE_IP, ['fr'], 'allowed'),
    ],
)
def test_multiorder_by_country(
        remote_ip,
        allowed_countries,
        expected_res,
        taxi_protocol,
        load_json,
        config,
        pricing_data_preparer,
):
    use_by_country_check = allowed_countries is not None
    config.set_values(dict(MULTIORDER_ENABLE_BY_COUNTRY=use_by_country_check))
    config.set_values(dict(MULTIORDER_ENABLED_COUNTRIES=allowed_countries))

    _check_can_make_more_orders(
        expected_res, taxi_protocol, load_json, x_real_ip=remote_ip,
    )


def make_order(taxi_protocol, load_json, **http_kwargs):
    request = load_json('basic_request.json')
    draft_resp = taxi_protocol.post('3.0/orderdraft', request, **http_kwargs)
    assert draft_resp.status_code == 200
    order_id = draft_resp.json()['orderid']

    commit_request = {'id': request['id'], 'orderid': order_id}

    resp = taxi_protocol.post('3.0/ordercommit', commit_request, **http_kwargs)
    assert resp.status_code == 200
    return resp.json()


@pytest.mark.filldb(users='make_more_orders', user_phones='make_more_orders')
@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=2,
    MULTIORDER_NUMERAL_THRESHOLD_COUNT=0,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_PROCESS_FOR_MULTIORDER_ON_ORDER_COMMIT=True,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi', 'android': 'yataxi'},
)
def test_tow_multiorder_order_name(
        taxi_protocol, load_json, pricing_data_preparer,
):
    # create the 1-st order
    commit_resp1 = make_order(taxi_protocol, load_json)

    # no order name: no multiorder yet
    assert _get_tow_order_name(taxi_protocol, commit_resp1['orderid']) is None

    # create the 2-nd order
    commit_resp2 = make_order(taxi_protocol, load_json)

    assert (
        _get_tow_order_name(taxi_protocol, commit_resp1['orderid'])
        == 'Заказ №1'
    )
    assert (
        _get_tow_order_name(taxi_protocol, commit_resp2['orderid'])
        == 'Заказ №2'
    )


def _get_tow_order_name(protocol, orderid):
    req_body = {'id': 'f4eb6aaa29ad4a6eb53f8a7620793561', 'orderid': orderid}
    tow_resp = protocol.post('3.0/taxiontheway', req_body)
    assert tow_resp.status_code == 200
    return tow_resp.json().get('order_name')


@pytest.mark.filldb(users='make_more_orders', user_phones='make_more_orders')
@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=2,
    MULTIORDER_NUMERAL_THRESHOLD_COUNT=1,
    MULTIORDER_PROCESS_FOR_MULTIORDER_ON_ORDER_COMMIT=True,
    MULTIORDER_LIMITS_ENABLED=True,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi', 'android': 'yataxi'},
)
@pytest.mark.translations(
    client_messages={'multiorder.order_name.n1': {'ru': 'order_name_1'}},
)
def test_tow_multiorder_numeral_order_name(
        taxi_protocol, load_json, pricing_data_preparer,
):
    """Checks if tow returns correct numeral order name."""
    # create the 1-st order
    commit_resp1 = make_order(taxi_protocol, load_json)

    # no order name: no multiorder yet
    assert _get_tow_order_name(taxi_protocol, commit_resp1['orderid']) is None

    # create the 2-nd order
    commit_resp2 = make_order(taxi_protocol, load_json)

    assert (
        _get_tow_order_name(taxi_protocol, commit_resp1['orderid'])
        == 'order_name_1'
    )
    assert (
        _get_tow_order_name(taxi_protocol, commit_resp2['orderid'])
        == 'Заказ №2'
    )


@pytest.mark.config(
    FEEDBACK_BADGES_MAPPING={
        'feedback_badges': [
            {
                'name': 'pleasantmusic',
                'label': 'feedback_badges.pleasantmusic',
                'filters': {'tariffs': ['default']},
            },
            {
                'name': 'pong',
                'label': 'feedback_badges.pong',
                'filters': {'tariffs': ['default']},
            },
            {
                'name': 'other',
                'label': 'feedback_badges.other',
                'images': {
                    'active_image_tag': 'tag.other',
                    'inactive_image_tag': 'tag.inother',
                },
                'filters': {'tariffs': ['default']},
            },
        ],
        'feedback_rating_mapping': [
            {'rating': 1, 'badges': []},
            {'rating': 2, 'badges': []},
            {'rating': 3, 'badges': []},
            {
                'rating': 4,
                'choice_title': 'feedback_badges.rating_title_4',
                'badges': ['pong'],
            },
            {
                'rating': 5,
                'choice_title': 'feedback_badges.rating_title_5',
                'badges': ['pleasantmusic', 'other'],
            },
        ],
    },
)
def test_tow_feedback_badges_user_without_expr(
        taxi_protocol, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
        headers={'Accept-Language': 'en-EN'},
    )
    assert response.status_code == 200
    content = response.json()
    assert content['supported_feedback_choices'].get('feedback_badges') is None
    assert (
        content['supported_feedback_choices'].get('feedback_rating_mapping')
        is None
    )


@pytest.mark.user_experiments('five_stars')
@pytest.mark.config(
    FEEDBACK_BADGES_MAPPING={
        'feedback_badges': [
            {
                'name': 'pleasantmusic',
                'label': 'feedback_badges.pleasantmusic',
                'filters': {'tariffs': ['default']},
            },
            {
                'name': 'pong',
                'label': 'feedback_badges.pong',
                'filters': {'tariffs': ['default']},
            },
            {
                'name': 'other',
                'label': 'feedback_badges.other',
                'images': {
                    'active_image_tag': 'tag.other',
                    'inactive_image_tag': 'tag.inother',
                },
                'filters': {'tariffs': ['default']},
            },
        ],
        'feedback_rating_mapping': [
            {'rating': 1, 'badges': []},
            {'rating': 2, 'badges': []},
            {'rating': 3, 'badges': []},
            {
                'rating': 4,
                'choice_title': 'feedback_badges.rating_title_4',
                'badges': ['pong'],
            },
            {
                'rating': 5,
                'choice_title': 'feedback_badges.rating_title_5',
                'badges': ['pleasantmusic', 'other'],
            },
        ],
    },
)
def test_tow_feedback_badges_user_with_expr(
        taxi_protocol, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
        headers={'Accept-Language': 'en-EN'},
    )
    assert response.status_code == 200
    content = response.json()
    expected_result = {
        'feedback_badges': [
            {'name': 'pleasantmusic', 'label': 'GOOD MUSIC'},
            {'name': 'pong', 'label': 'PONG'},
            {
                'name': 'other',
                'label': 'OTHER',
                'images': {
                    'active_image_tag': 'tag.other',
                    'inactive_image_tag': 'tag.inother',
                },
            },
        ],
        'feedback_rating_mapping': [
            {'rating': 1, 'badges': []},
            {'rating': 2, 'badges': []},
            {'rating': 3, 'badges': []},
            {'rating': 4, 'choice_title': 'RATING 4', 'badges': ['pong']},
            {
                'rating': 5,
                'choice_title': 'RATING 5',
                'badges': ['pleasantmusic', 'other'],
            },
        ],
    }

    assert (
        sorted(expected_result['feedback_badges'], key=lambda k: k['name'])
        == sorted(
            content['supported_feedback_choices']['feedback_badges'],
            key=lambda k: k['name'],
        )
    )
    assert (
        sorted(
            expected_result['feedback_rating_mapping'],
            key=lambda k: k['rating'],
        )
        == sorted(
            content['supported_feedback_choices']['feedback_rating_mapping'],
            key=lambda k: k['rating'],
        )
    )


@pytest.mark.user_experiments('five_stars')
def test_tow_feedback_badges_user_with_expr_without_config(
        taxi_protocol, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
        headers={'Accept-Language': 'en-EN'},
    )
    assert response.status_code == 200
    content = response.json()
    assert content['supported_feedback_choices']['feedback_badges'] == []
    assert (
        content['supported_feedback_choices']['feedback_rating_mapping'] == []
    )


@pytest.mark.user_experiments('five_stars')
@pytest.mark.config(
    FEEDBACK_BADGES_MAPPING={
        'feedback_badges': [
            {
                'name': 'pleasantmusic',
                'label': 'feedback_badges.pleasantmusic',
                'filters': {'tariffs': ['default']},
            },
            {
                'name': 'pong',
                'label': 'feedback_badges.pong',
                'filters': {'tariffs': ['comfort', 'econom']},
            },
            {
                'name': 'other',
                'label': 'feedback_badges.other',
                'images': {
                    'active_image_tag': 'tag.other',
                    'inactive_image_tag': 'tag.inother',
                },
                'filters': {'tariffs': ['vip', 'comfort']},
            },
        ],
        'feedback_rating_mapping': [
            {'rating': 1, 'badges': []},
            {'rating': 2, 'badges': []},
            {'rating': 3, 'badges': []},
            {
                'rating': 4,
                'choice_title': 'feedback_badges.rating_title_4',
                'badges': ['pong'],
            },
            {
                'rating': 5,
                'choice_title': 'feedback_badges.rating_title_5',
                'badges': ['pleasantmusic', 'other'],
            },
        ],
    },
)
def test_tow_feedback_badges_check_tariffs_filter(
        taxi_protocol, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
        headers={'Accept-Language': 'en-EN'},
    )
    assert response.status_code == 200
    content = response.json()
    expected_result = {
        'feedback_badges': [
            {'name': 'pleasantmusic', 'label': 'GOOD MUSIC'},
            {'name': 'pong', 'label': 'PONG'},
        ],
        'feedback_rating_mapping': [
            {'rating': 1, 'badges': []},
            {'rating': 2, 'badges': []},
            {'rating': 3, 'badges': []},
            {'rating': 4, 'choice_title': 'RATING 4', 'badges': ['pong']},
            {
                'rating': 5,
                'choice_title': 'RATING 5',
                'badges': ['pleasantmusic'],
            },
        ],
    }

    assert (
        sorted(expected_result['feedback_badges'], key=lambda k: k['name'])
        == sorted(
            content['supported_feedback_choices']['feedback_badges'],
            key=lambda k: k['name'],
        )
    )
    assert (
        sorted(
            expected_result['feedback_rating_mapping'],
            key=lambda k: k['rating'],
        )
        == sorted(
            content['supported_feedback_choices']['feedback_rating_mapping'],
            key=lambda k: k['rating'],
        )
    )


@pytest.mark.user_experiments('five_stars')
@pytest.mark.config(
    FEEDBACK_BADGES_MAPPING={
        'feedback_badges': [
            {
                'name': 'pleasantmusic',
                'label': 'feedback_badges.pleasantmusic',
                'filters': {'tariffs': ['default']},
            },
            {
                'name': 'pong',
                'label': 'feedback_badges.pong',
                'filters': {'tariffs': ['comfort', 'econom']},
            },
            {
                'name': 'other',
                'label': 'feedback_badges.other',
                'images': {
                    'active_image_tag': 'tag.other',
                    'inactive_image_tag': 'tag.inother',
                },
                'filters': {'tariffs': ['vip', 'comfort']},
            },
            {
                'name': 'nochange',
                'label': 'feedback_badges.nochange',
                'filters': {'tariffs': ['default'], 'cash': True},
            },
            {
                'name': 'notrip',
                'label': 'feedback_badges.notrip',
                'filters': {'tariffs': ['default'], 'notrip': True},
            },
        ],
        'feedback_rating_mapping': [
            {'rating': 1, 'badges': []},
            {'rating': 2, 'badges': []},
            {'rating': 3, 'badges': ['nochange']},
            {
                'rating': 4,
                'choice_title': 'feedback_badges.rating_title_4',
                'badges': ['pong'],
            },
            {
                'rating': 5,
                'choice_title': 'feedback_badges.rating_title_5',
                'badges': ['pleasantmusic', 'other'],
            },
        ],
    },
)
def test_tow_feedback_badges_check_filters(
        taxi_protocol, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
        headers={'Accept-Language': 'en-EN'},
    )
    assert response.status_code == 200
    content = response.json()
    expected_result = {
        'feedback_badges': [
            {'name': 'pleasantmusic', 'label': 'GOOD MUSIC'},
            {'name': 'pong', 'label': 'PONG'},
            {'name': 'nochange', 'label': 'NOCHANGE'},
        ],
        'feedback_rating_mapping': [
            {'rating': 1, 'badges': []},
            {'rating': 2, 'badges': []},
            {'rating': 3, 'badges': ['nochange']},
            {'rating': 4, 'choice_title': 'RATING 4', 'badges': ['pong']},
            {
                'rating': 5,
                'choice_title': 'RATING 5',
                'badges': ['pleasantmusic'],
            },
        ],
    }

    assert (
        sorted(expected_result['feedback_badges'], key=lambda k: k['name'])
        == sorted(
            content['supported_feedback_choices']['feedback_badges'],
            key=lambda k: k['name'],
        )
    )
    assert (
        sorted(
            expected_result['feedback_rating_mapping'],
            key=lambda k: k['rating'],
        )
        == sorted(
            content['supported_feedback_choices']['feedback_rating_mapping'],
            key=lambda k: k['rating'],
        )
    )


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.filldb(
    tariff_settings='change_payment',
    orders='change_payment',
    order_proc='change_payment',
)
@pytest.mark.parametrize(
    'user_id, order_id, expected_options',
    [
        (
            'b300bda7d41b4bae8d58dfa93221ef16',
            '8c83b49edb274ce0992f337061047375',
            {'applepay', 'card', 'googlepay'},
        ),
        (
            'b300bda7d41b4bae8d58dfa93221ef16',
            '8c83b49edb274ce0992f337061047376',
            {},
        ),
        (
            'b300bda7d41b4bae8d58dfa93221ef16',
            '8c83b49edb274ce0992f337061047396',
            {},
        ),
    ],
)
def test_tow_allow_change_payment(
        taxi_protocol,
        default_driver_position,
        user_id,
        order_id,
        expected_options,
):
    request = {'format_currency': True, 'id': user_id, 'orderid': order_id}

    response = taxi_protocol.post('3.0/taxiontheway', request)
    assert response.status_code == 200
    content = response.json()

    payment_change = list(
        filter(lambda i: i['name'] == 'payment', content['allowed_changes']),
    )
    options = set([])
    if len(payment_change) > 0:
        options = set(payment_change[0]['available_methods'])
    assert options == set(expected_options)


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.filldb(
    tariff_settings='change_payment',
    orders='change_payment',
    order_proc='change_payment',
)
@pytest.mark.parametrize(
    'user_id, order_id, expected_options',
    [
        (
            'b300bda7d41b4bae8d58dfa93221ef16',
            '8c83b49edb274ce0992f337061047375',
            {'applepay', 'card', 'googlepay'},
        ),
    ],
)
@pytest.mark.parks_activation(
    [
        {
            'park_id': '999012',
            'city_id': 'Москва',
            'revision': 1,
            'last_modified': '1970-01-15T03:56:07.000',
            'data': {
                'deactivated': False,
                'can_cash': True,
                'can_card': True,
                'can_coupon': True,
                'can_corp': True,
            },
        },
    ],
)
@pytest.mark.config(API_OVER_DATA_WORK_MODE=API_OVER_DATA_WORK_MODE)
def test_tow_allow_change_payment_park_activation(
        taxi_protocol,
        default_driver_position,
        user_id,
        order_id,
        expected_options,
):
    request = {'format_currency': True, 'id': user_id, 'orderid': order_id}

    response = taxi_protocol.post('3.0/taxiontheway', request)
    assert response.status_code == 200
    content = response.json()

    payment_change = list(
        filter(lambda i: i['name'] == 'payment', content['allowed_changes']),
    )
    options = set([])
    if len(payment_change) > 0:
        options = set(payment_change[0]['available_methods'])
    assert options == set(expected_options)


@pytest.mark.filldb(
    tariff_settings='change_destinations',
    orders='change_payment',
    order_proc='change_payment',
)
def test_tow_allow_change_destinations(taxi_protocol, default_driver_position):
    request = {
        'format_currency': True,
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '8c83b49edb274ce0992f337061047375',
    }

    response = taxi_protocol.post('3.0/taxiontheway', request)
    assert response.status_code == 200
    content = response.json()

    destinations = filter(
        lambda i: i['name'] == 'destinations', content['allowed_changes'],
    )
    assert len(list(destinations)) == 1


@pytest.mark.filldb(
    tariff_settings='disable_change_destinations',
    orders='change_payment',
    order_proc='change_payment',
)
def test_tow_disable_change_destinations(
        taxi_protocol, default_driver_position,
):
    request = {
        'format_currency': True,
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '8c83b49edb274ce0992f337061047375',
    }

    response = taxi_protocol.post('3.0/taxiontheway', request)
    assert response.status_code == 200
    content = response.json()

    destinations = filter(
        lambda i: i['name'] == 'destinations', content['allowed_changes'],
    )
    assert len(list(destinations)) == 0


def call_tow(taxi_protocol, order_id):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': order_id,
            'supported': ['midpointchange'],
        },
    )
    assert response.status_code == 200
    return response


def update_destinations(db, order_id, destinations):
    db.order_proc.update(
        {'_id': order_id},
        {'$set': {'order.request.destinations': destinations}},
    )


def update_tariff(db, order_id, nz, tariff):
    db.order_proc.update(
        {'_id': order_id},
        {'$set': {'order.performer.tariff.class': tariff, 'order.nz': nz}},
    )


@pytest.mark.user_experiments('supported_midpoint_change')
@pytest.mark.filldb(
    orders='eta_driving',
    order_proc='eta_driving',
    tariff_settings='change_destinations',
)
@pytest.mark.translations(
    tariff={
        'old_category_name.econom': {'ru': 'Эконом'},
        'name.comfortplus': {'ru': 'Здесь могла бы быть доставка'},
    },
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=10))
@pytest.mark.config(
    TAXIONTHEWAY_ENABLE_DESTINATION_CHANGES={
        '__default__': {'__default__': True, 'comfortplus': False},
        'moscow': {'__default__': False, 'comfortplus': True},
    },
)
@pytest.mark.parametrize(
    ('zone', 'tariff', 'midpoint_changes_allowed'),
    [
        pytest.param(
            'moscow', 'econom', False, id='defined zone with default category',
        ),
        pytest.param(
            'moscow',
            'comfortplus',
            True,
            id='defined zone with defined category',
        ),
        pytest.param(
            'almaty',
            'econom',
            True,
            id='undefined zone with defined category',
        ),
        pytest.param(
            'almaty',
            'comfortplus',
            False,
            id='undefined zone with undefined category',
        ),
    ],
)
def test_driving_change_midpoint(
        taxi_protocol,
        mockserver,
        db,
        tracker,
        now,
        load_binary,
        zone,
        tariff,
        midpoint_changes_allowed,
):
    destinations = [
        {
            'country': 'Россия',
            'description': 'микрорайон Родники, Новосибирск, Россия',
            'exact': True,
            'fullname': 'Россия, Новосибирск, мкр Родники, улица Тюленина, 15',
            'geopoint': [1, 2],
            'locality': 'Новосибирск',
            'object_type': 'другое',
            'premisenumber': '123',
            'short_text': 'улица Тюленина, 15',
            'thoroughfare': 'улица Тюленина',
            'type': 'address',
            'use_geopoint': False,
        },
        {
            'country': 'Россия',
            'description': 'микрорайон Родники, Новосибирск, Россия',
            'exact': True,
            'fullname': 'Россия, Новосибирск, мкр Родники, улица Тюленина, 15',
            'geopoint': [2, 3],
            'locality': 'Новосибирск',
            'object_type': 'другое',
            'premisenumber': '123',
            'short_text': 'улица Тюленина, 15',
            'thoroughfare': 'улица Тюленина',
            'type': 'address',
            'use_geopoint': False,
        },
    ]

    allowed_changes = [
        {'name': 'comment'},
        {'name': 'porchnumber'},
        {
            'name': 'payment',
            'available_methods': ['card', 'applepay', 'googlepay'],
        },
    ]

    if midpoint_changes_allowed:
        allowed_changes.insert(
            2,
            {
                'points': [
                    {'edit': False, 'remove': False, 'insert_before': False},
                    {'edit': False, 'remove': False, 'insert_before': False},
                    {'edit': False, 'remove': False, 'insert_before': False},
                ],
                'name': 'destination_changes',
            },
        )

    order_id = '8c83b49edb274ce0992f337061047375'
    update_tariff(db, order_id, zone, tariff)
    tracker.set_position('999012_a5709ce56c2740d9a536650f5390de0b', now, 1, 0)

    @mockserver.json_handler('/maps-router/route_jams/')
    def route_jams(request):
        return mockserver.make_response(
            load_binary('route_jams.protobuf'),
            content_type='application/x-protobuf',
        )

    content = call_tow(taxi_protocol, order_id).json()
    assert content['allowed_changes'] == allowed_changes
    assert content['status'] == 'driving'

    update_destinations(db, order_id, destinations)

    if midpoint_changes_allowed:
        points = [
            {'edit': True, 'remove': True, 'insert_before': False},
            {'edit': True, 'remove': False, 'insert_before': False},
        ]
        allowed_changes[2]['points'] = points
        allowed_changes.insert(2, {'name': 'destinations'})

    content = call_tow(taxi_protocol, order_id).json()
    assert content['allowed_changes'] == allowed_changes

    update_destinations(db, order_id, destinations[:1])

    if midpoint_changes_allowed:
        points = [{'edit': True, 'remove': False, 'insert_before': True}]
        allowed_changes[3]['points'] = points
    else:
        allowed_changes.insert(2, {'name': 'destinations'})

    content = call_tow(taxi_protocol, order_id).json()
    assert content['allowed_changes'] == allowed_changes


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='totw_request_feedback_from_api_proxy_passenger_feedback',
    consumers=['protocol/taxiontheway'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
def test_tow_no_call_feedback_by_exp_passenger_feedback(
        taxi_protocol, mockserver,
):
    @mockserver.json_handler('/feedback/1.0/retrieve')
    def mock_feedback_retrieve(request):
        assert False

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
        headers={'Accept-Language': 'en-EN'},
    )
    assert response.status_code == 200
    assert 'feedback' not in response.json()


@pytest.mark.filldb(dbdrivers='deaf', dbcars='deaf')
@pytest.mark.config(
    TAXIONTHEWAY_DEAF_DRIVER_ICON='path to deaf driver icon',
    TAXIONTHEWAY_DEAF_DRIVER_SHOW_ICON_ON_STATUS=['waiting'],
    TAXIONTHEWAY_DEAF_DRIVER_FORCE_DESTINATION_ON_STATUS=['waiting'],
    TAXIONTHEWAY_DEAF_DRIVER_BUTTON_MODIFIERS_ON_STATUS=['waiting'],
)
@pytest.mark.translations(
    client_messages={
        # button_modifiers
        'deaf_driver.call_to_driver.label': {'ru': 'deaf driver label'},
        'deaf_driver.call_to_driver.dialog_title': {'ru': 'dialog title'},
        'deaf_driver.call_to_driver.dialog_message': {'ru': 'dialog message'},
        'deaf_driver.call_to_driver.button_title_back': {
            'ru': 'back button title',
        },
        # force_destination
        'deaf_driver.force_destination.dialog_title': {'ru': 'dialog title'},
        'deaf_driver.force_destination.dialog_message': {
            'ru': 'dialog message',
        },
        'deaf_driver.force_destination.button_title_destination': {
            'ru': 'destination button title',
        },
        'deaf_driver.force_destination.button_title_back': {
            'ru': 'back button title',
        },
    },
)
@pytest.mark.order_experiments('deaf_driver')
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_tow_deaf_driver(
        taxi_protocol,
        default_driver_position,
        mock_order_core,
        order_core_switch_on,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
        headers={'Accept-Language': 'ru-RU'},
    )
    assert response.status_code == 200

    content = response.json()
    assert content['button_modifiers'] == [
        {
            'button': 'call_to_driver',
            'inactive': True,
            'inactive_icon_tag': 'path to deaf driver icon',
            'label': 'deaf driver label',
            'dialog': {
                'title': 'dialog title',
                'message': 'dialog message',
                'options': [
                    {
                        'action': 'back_to_driving_screen',
                        'button_title': 'back button title',
                    },
                ],
            },
        },
    ]

    assert content['force_destination'] == {
        'dialog': {
            'title': 'dialog title',
            'message': 'dialog message',
            'options': [
                {
                    'action': 'go_to_edit_destination',
                    'button_title': 'destination button title',
                },
                {
                    'action': 'back_to_driving_screen',
                    'button_title': 'back button title',
                },
            ],
        },
    }

    assert mock_order_core.get_fields_times_called == int(order_core_switch_on)


@pytest.mark.config(
    TAXIONTHEWAY_DEAF_DRIVER_ICON='path to deaf driver icon',
    TAXIONTHEWAY_DEAF_DRIVER_SHOW_ICON_ON_STATUS=['waiting'],
    TAXIONTHEWAY_DEAF_DRIVER_FORCE_DESTINATION_ON_STATUS=['waiting'],
    TAXIONTHEWAY_DEAF_DRIVER_BUTTON_MODIFIERS_ON_STATUS=['waiting'],
)
@pytest.mark.order_experiments('deaf_driver')
def test_tow_deaf_driver_no_translation(
        taxi_protocol, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
        headers={'Accept-Language': 'ru-RU'},
    )
    assert response.status_code == 200

    content = response.json()
    assert 'button_modifiers' not in content
    assert 'force_destination' not in content


@pytest.mark.translations(
    geoareas={'aze': {'en': 'Azerbaijan!'}},
    client_messages={
        'taxiontheway.driver_license_label': {'en': 'Country: %(country)s'},
    },
)
@pytest.mark.config(
    TAXIONTHEWAY_LICENSE_LABEL_ENABLE_ZONES=['moscow'],
    TAXIONTHEWAY_LICENSE_LABEL_LICENSE_ZONES=['aze'],
)
def test_tow_driver_license(db, taxi_protocol, mockserver):
    testcase = {'called': 0}

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        testcase['called'] += 1
        testcase['query_string'] = request.query_string
        return {
            'direction': 328,
            'lat': 55.5,
            'lon': 37.7,
            'speed': 30,
            'timestamp': 1502366306,
        }

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
        headers={'Accept-Language': 'en'},
    )

    assert response.status_code == 200

    data = response.json()
    assert data['driver']['license_label'] == 'Country: Azerbaijan!'


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(orders='eta_driving', order_proc='eta_driving')
@pytest.mark.fixture_now(datetime.timedelta(minutes=10))
def test_tow_driving_empty_smooth_routing(
        taxi_protocol, mockserver, tracker, now, db, load,
):
    order_id = '8c83b49edb274ce0992f337061047375'

    tracker.set_position('999012_a5709ce56c2740d9a536650f5390de0b', now, 1, 0)

    @mockserver.json_handler('/tracker/smooth-routing')
    def mock_smooth_routing(request):
        return {'error': 'some_error'}

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': order_id,
        },
    )

    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'driving'


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(orders='eta_transporting', order_proc='eta_transporting')
@pytest.mark.config(ROUTER_MAPS_ENABLED=True)
@pytest.mark.fixture_now(datetime.timedelta(minutes=10))
def test_tow_bad_router_response(
        taxi_protocol, mockserver, tracker, now, db, load,
):
    order_id = '8c83b49edb274ce0992f337061047375'

    @mockserver.json_handler('/maps-router/route_jams/')
    def route_jams(request):
        return mockserver.make_response('', 502)

    tracker.set_position('999012_a5709ce56c2740d9a536650f5390de0b', now, 1, 0)

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': order_id,
        },
    )

    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'transporting'
    assert 'routeinfo' not in content


@pytest.mark.parametrize(
    'unset_paid_supply_price,unset_performer_paid_supply,discount_expected',
    [(False, False, False), (False, True, True), (True, True, False)],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(orders='paid_supply', order_proc='paid_supply')
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
def test_tow_paid_supply(
        taxi_protocol,
        default_driver_position,
        db,
        unset_paid_supply_price,
        unset_performer_paid_supply,
        discount_expected,
):
    if unset_paid_supply_price:
        # This will mean that paid supply was not offered
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {'$unset': {'order.fixed_price.paid_supply_price': 1}},
        )
        db.orders.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {'$unset': {'fixed_price.paid_supply_price': 1}},
        )

    if unset_performer_paid_supply:
        # This will mean that paid supply did not actually happen
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {'$set': {'order.performer.paid_supply': False}},
        )
        db.orders.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {'$set': {'performer.paid_supply': False}},
        )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()

    if discount_expected:
        assert 'paid_supply_discount' in content
        assert content['paid_supply_discount'] == {
            'dialog': {
                'title': 'Поездка будет дешевле',
                'message': 'Поездка будет стоить 151\xa0$SIGN$$CURRENCY$.',
                'options': [
                    {
                        'action': 'back_to_driving_screen',
                        'button_title': 'Замечательно',
                    },
                ],
            },
        }
    else:
        assert 'paid_supply_discount' not in content

    assert 'final_cost' in content
    if unset_performer_paid_supply:
        assert content['final_cost'] == 151
    else:
        assert content['final_cost'] == 151 + 77

    assert 'cancel_rules' in content
    assert content['cancel_rules']['state'] == 'free'
    assert content['cancel_rules']['message_key'] == 'free.driving'


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(orders='paid_supply', order_proc='paid_supply_paid_cancel')
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
@pytest.mark.experiments3(filename='exp3_paid_supply_paid_cancel.json')
@pytest.mark.parametrize(
    'switch_to_waiting,expected_key,expected_cost',
    [
        (False, 'paid.paidsupply.driving', 78),
        (True, 'paid.paidsupply.waiting', 77 + 99),
    ],
)
def test_tow_paid_supply_paid_cancel(
        taxi_protocol,
        recalc_order,
        default_driver_position,
        db,
        switch_to_waiting,
        expected_key,
        expected_cost,
):
    if switch_to_waiting:
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {'$set': {'order.taxi_status': 'waiting'}},
        )
        db.orders.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {'$set': {'taxi_status': 'waiting'}},
        )

    # Just a request before cancel
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()

    assert 'paid_supply_discount' not in content
    assert 'final_cost' in content
    assert 'cancel_rules' in content

    assert content['final_cost'] == 151 + 77
    assert content['cancel_rules']['state'] == 'paid'
    assert content['cancel_rules']['message_key'] == expected_key

    # Unsuccessful cancel request, because it expects free cancel
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'break': 'user',
            'cancel_state': 'free',
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 409
    if switch_to_waiting:
        expected_409_message_suffix = '+ minimal [w].'
    else:
        expected_409_message_suffix = '[d].'
    assert response.json() == {
        'error': {
            'code': 'ERROR_CANCEL_STATE_CHANGED',
            'text': {
                'title': 'Cancel this order?',
                'message': (
                    'Cancel price will be equal to paid supply '
                    'price %s' % expected_409_message_suffix
                ),
                'message_support': (
                    'Please indicate if the driver\'s at fault.'
                ),
            },
            'cancel_state': 'paid',
        },
    }

    recalc_order.set_recalc_result(expected_cost, expected_cost)

    # Cancel request
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'break': 'user',
            'cancel_state': 'paid',
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()

    assert 'cost' in content
    assert 'final_cost' in content
    assert 'cost_message' in content
    assert content['cost'] == expected_cost
    assert content['final_cost'] == expected_cost
    assert (
        content['cost_message']
        == 'Paid supply with paid cancel in '
        + ('waiting' if switch_to_waiting else 'driving')
        + ' OK'
    )
    proc = db.order_proc.find_one({'_id': '8c83b49edb274ce0992f337061047375'})
    order_commit_common.check_current_prices(proc, 'final_cost', expected_cost)


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(
    orders='paid_cancel_in_driving', order_proc='paid_cancel_in_driving',
)
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
@pytest.mark.config(ROUTER_42GROUP_ENABLED=False)
@pytest.mark.parametrize(
    'order_proc_setup, paid_cancel_expected, user_tags',
    [
        ({}, False, False),
        (
            {
                'order.paid_cancel_in_driving': {
                    'price': 75,
                    'free_cancel_timeout': 300,
                    'for_paid_supply': True,
                },
                'order.user_tags': [],
            },
            True,
            False,
        ),
        (
            {
                'order.paid_cancel_in_driving': {
                    'price': 75,
                    'free_cancel_timeout': 0,
                    'for_paid_supply': False,
                },
                'order.pricing_data.user.paid_cancel_by_tags_price': 30,
            },
            True,
            True,
        ),
    ],
)
def test_tow_paid_cancel_in_driving(
        taxi_protocol,
        recalc_order,
        default_driver_position,
        db,
        config,
        order_proc_setup,
        paid_cancel_expected,
        user_tags,
):
    if order_proc_setup != {}:
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {'$set': order_proc_setup},
        )
    # Just a request before cancel
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()

    assert 'final_cost' in content
    assert 'cancel_rules' in content

    assert content['final_cost'] == 151
    assert content['cancel_rules']['state'] == (
        'paid' if paid_cancel_expected else 'free'
    )
    message_key = (
        'tags'
        if user_tags
        else ('paid.card.driving' if paid_cancel_expected else 'free.driving')
    )
    assert content['cancel_rules']['message_key'] == message_key

    if paid_cancel_expected:
        # Unsuccessful cancel request, because it expects free cancel
        response = taxi_protocol.post(
            '3.0/taxiontheway',
            {
                'break': 'user',
                'cancel_state': 'free',
                'format_currency': True,
                'id': 'b300bda7d41b4bae8d58dfa93221ef16',
                'orderid': '8c83b49edb274ce0992f337061047375',
            },
        )
        assert response.status_code == 409
        assert response.json() == {
            'error': {
                'code': 'ERROR_CANCEL_STATE_CHANGED',
                'text': {
                    'title': 'Cancel this order?',
                    'message': 'Cancel will be paid!',
                    'message_support': (
                        'Please indicate if the driver\'s at fault.'
                    ),
                },
                'cancel_state': 'paid',
            },
        }

    # Cancel request
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'break': 'user',
            'cancel_state': 'paid' if paid_cancel_expected else 'free',
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    proc = db.order_proc.find_one({'_id': '8c83b49edb274ce0992f337061047375'})
    if paid_cancel_expected:
        assert 'cost' in content
        assert 'final_cost' in content
        assert 'cost_message' in content
        assert content['cost'] == 75
        assert content['final_cost'] == 75
        assert (
            content['cost_message']
            == 'You were charged for canceling a $TARIFF_NAME$ class order.'
        )
        order_commit_common.check_current_prices(proc, 'final_cost', 75)
    else:
        assert 'cost' not in content
        assert 'final_cost' not in content
        order_commit_common.check_current_prices(proc, 'final_cost', 0)


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(
    orders='transporting_cancel_limit', order_proc='transporting_cancel_limit',
)
@pytest.mark.config(MAX_TRANSPORTING_TIME_TO_CANCEL=300)
@pytest.mark.parametrize(
    'date_diff,can_cancel',
    [(200, True), (300, True), (301, False), (400, False)],
)
def test_tow_transporting_cancel_limit(
        taxi_protocol,
        default_driver_position,
        db,
        config,
        date_diff,
        mocked_time,
        can_cancel,
):
    osu = mocked_time.now - datetime.timedelta(seconds=date_diff)
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'order.status_updated': osu}},
    )
    # Cancel request
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'break': 'user',
            'cancel_state': 'paid',
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    desired_status = 'cancelled' if can_cancel else 'transporting'
    assert response.json()['status'] == desired_status


@pytest.mark.now('2022-05-25T11:30:00+0300')
@pytest.mark.filldb(
    orders='paid_cancel_in_waiting', order_proc='paid_cancel_in_waiting',
)
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
@pytest.mark.experiments3(
    filename='exp3_paid_cancel_in_waiting_min_free_time.json',
)
@pytest.mark.parametrize(
    'paid_cancel_in_driving',
    [
        None,
        {
            'paid_cancel_in_driving': {
                'for_paid_supply': True,
                'free_cancel_timeout': 1000000,
                'price': 78,
            },
        },
    ],
)
def test_free_cancel_in_waiting_by_exp(
        taxi_protocol,
        db,
        mockserver,
        default_driver_position,
        paid_cancel_in_driving,
):
    if paid_cancel_in_driving is not None:
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {
                '$set': {
                    'order.paid_cancel_in_driving': paid_cancel_in_driving[
                        'paid_cancel_in_driving'
                    ],
                },
            },
        )

    # Cancel request
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'break': 'user',
            'cancel_state': 'free',
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'cancelled'
    proc = db.order_proc.find_one({'_id': '8c83b49edb274ce0992f337061047375'})
    order = proc['order']
    assert (
        'free_cancel_reason' in order
        and order['free_cancel_reason'] == 'DRIVER_ASSIGNED_TOO_RECENTLY'
    )


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(
    orders='cancel_with_accident', order_proc='cancel_with_accident',
)
@pytest.mark.config(MAX_TRANSPORTING_TIME_TO_CANCEL=300)
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
@pytest.mark.parametrize('accident_check', (True, False))
@pytest.mark.parametrize(
    'taxi_status,status_updated_diff,',
    [
        ('transporting', 299),  # normal cancel won't work because of position
        ('transporting', 301),  # normal cancel won't work because of time
    ],
)
def test_tow_cancel_with_accident_transporting(
        taxi_protocol,
        tracker,
        now,
        db,
        config,
        mocked_time,
        accident_check,
        taxi_status,
        status_updated_diff,
):
    ORDER_ID = '8c83b49edb274ce0992f337061047375'
    DEFAULT_DIRVER_POS = [55.73341076871702, 37.58917997300821]
    config.set(
        TAXIONTHEWAY_CHECK_IF_ACCIDENT_HAPPENED_ON_CANCEL=accident_check,
    )
    osu = mocked_time.now - datetime.timedelta(seconds=status_updated_diff)
    db.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.status_updated': osu}},
    )
    tracker.set_position(
        '999012_a5709ce56c2740d9a536650f5390de0b', now, *DEFAULT_DIRVER_POS,
    )
    # we don't care if cancel is paid, but we need to know its status exactly
    # to make cancel request
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
            'position': {'point': DEFAULT_DIRVER_POS, 'dx': 0},
        },
    )
    # Cancel request
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'break': 'accident',
            'cancel_state': response.json()['cancel_rules']['state'],
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
            'position': {'point': DEFAULT_DIRVER_POS[::-1], 'dx': 0},
        },
    )
    assert response.status_code == 200
    desired_status = 'cancelled' if not accident_check else taxi_status
    assert response.json()['status'] == desired_status


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(user_phones='extra_contact')
def test_tow_extra_contact(
        taxi_protocol, tracker, now, db, config, mockserver,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def mock_personal(request):
        request_json = json.loads(request.get_data())
        assert request_json == {'id': '04a77147dab440479711d995610d77ee'}
        return {
            'id': '04a77147dab440479711d995610d77ee',
            'value': '+79007654321',
        }

    order_id = '8c83b49edb274ce0992f337061047375'

    tracker.set_position('999012_a5709ce56c2740d9a536650f5390de0b', now, 1, 0)

    response = taxi_protocol.post(
        '/3.0/taxiontheway',
        {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'orderid': order_id},
    )

    assert response.status_code == 200
    content = response.json()
    assert 'extra_contact_phone' not in content
    assert mock_personal.times_called == 0

    db.order_proc.update(
        {'_id': order_id},
        {
            '$set': {
                'order.request.extra_user_phone_id': bson.ObjectId(
                    '28967c5b6195542e9b567356',
                ),
            },
        },
    )

    response = taxi_protocol.post(
        '/3.0/taxiontheway',
        {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'orderid': order_id},
    )

    assert response.status_code == 200
    content = response.json()
    assert content['extra_contact_phone'] == '+79007654321'
    assert mock_personal.times_called == 1


def make_afs_is_spammer_true_response_builder(add_sec_to_block_time=0):
    def response_builder(now):
        blocked_until = now + datetime.timedelta(seconds=add_sec_to_block_time)
        return {
            'is_spammer': True,
            'blocked_until': utils.timestring(blocked_until),
        }

    return response_builder


def afs_is_spammer_true_response_no_time_builder(_):
    return {'is_spammer': True}


def afs_is_spammer_false_response_builder(_):
    return {'is_spammer': False}


MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE = (
    'Мультизаказ недоступен из-за частых отмен'
)
UNBLOCK_DUR = ', попробуйте через %(unblock_after_duration)s'


def make_multiorder_disallowed_in_duration_err(duration):
    prefix = MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE + ', попробуйте через '
    return prefix + duration


@pytest.mark.filldb(users='make_more_orders', user_phones='make_more_orders')
@pytest.mark.translations(
    client_messages={
        'multiorder.warn_cant_make_more_orders_for_spammer': {
            'ru': MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE,
        },
        'multiorder.warn_cant_make_more_orders_for_spammer_with_duration': {
            'ru': MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE + UNBLOCK_DUR,
        },
    },
    tariff={
        'round.minute': {'ru': '%(value).0f мин'},
        'round.hours': {'ru': '%(value).0f ч'},
    },
)
@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_ANTIFRAUD_CHECK_IS_NOT_SPAMMER=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
    MULTIORDER_ANTIFRAUD_FOR_CAN_MAKE_MORE_ORDERS=True,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi', 'android': 'yataxi'},
)
@pytest.mark.now('2018-11-20T11:00:00+0300')
@pytest.mark.parametrize(
    'afs_resp_builder,exp_reason',
    [
        (
            make_afs_is_spammer_true_response_builder(0),
            make_multiorder_disallowed_in_duration_err('1 мин'),
        ),
        (
            make_afs_is_spammer_true_response_builder(-1),
            make_multiorder_disallowed_in_duration_err('1 мин'),
        ),
        (
            make_afs_is_spammer_true_response_builder(60 * 60 * 4),
            make_multiorder_disallowed_in_duration_err('4 ч'),
        ),
        (
            afs_is_spammer_true_response_no_time_builder,
            MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE,
        ),
        (afs_is_spammer_false_response_builder, None),
    ],
)
def test_multiorder_is_spammer_check(
        taxi_protocol,
        load_json,
        mockserver,
        now,
        afs_resp_builder,
        exp_reason,
        pricing_data_preparer,
):
    # make an order
    order = make_order(taxi_protocol, load_json)
    user_id = 'f4eb6aaa29ad4a6eb53f8a7620793561'

    # cancel the order to be able getting can_make_more_orders
    cancel_resp = taxi_protocol.post(
        '3.0/taxiontheway',
        {'break': 'user', 'id': user_id, 'orderid': order['orderid']},
    )
    assert cancel_resp.status_code == 200

    # make an order to have 1 active order
    make_order(taxi_protocol, load_json)

    @mockserver.json_handler('/antifraud/client/user/is_spammer')
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': True,
            'user_id': user_id,
            'user_phone_id': '59246c5b6195542e9b084206',
            'device_id': 'c02c705e98588f724ca046ac59cafece65501e36',
        }
        return afs_resp_builder(now)

    req_body = {'id': user_id, 'orderid': order['orderid']}
    resp = taxi_protocol.post('3.0/taxiontheway', req_body)
    assert resp.status_code == 200
    resp_data = resp.json()
    if exp_reason is None:
        assert resp_data['can_make_more_orders'] == 'allowed'
        assert 'no_more_orders_reason' not in resp_data
    else:
        assert resp_data['can_make_more_orders'] == 'disallowed'
        assert resp_data['no_more_orders_reason'] == exp_reason


EXPECTED_PARTNER_RESPONSE = {
    'name': 'Главное Такси',
    'phone': '+79321259615',
    'yamoney': False,
    'long_name': 'Organization',
    'legal_address': 'Street',
    'id': '999012',
}


@pytest.mark.parametrize('show_tin', [True, False])
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(order_proc='carrier', countries='carrier_disabled')
@pytest.mark.translations(
    client_messages={
        'taxiontheway.carrier.name': {'ru': 'Название: %(name)s'},
        'taxiontheway.carrier.address': {'ru': 'Адрес: %(address)s'},
        'taxiontheway.carrier.ogrn': {'ru': 'ОГРН: %(reg_number)s'},
        'taxiontheway.carrier.working_hours': {
            'ru': 'Часы работы: %(working_hours)s',
        },
    },
)
def test_tow_carrier_disabled(
        taxi_protocol, mockserver, default_driver_position, db, show_tin,
):
    expected_result = copy.deepcopy(EXPECTED_PARTNER_RESPONSE)
    if show_tin:
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {'$set': {'order.performer.tin': 'tin_number'}},
        )
        expected_result['tin'] = 'tin_number'

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()

    assert 'partner' not in content
    assert content['park'] == expected_result


@pytest.mark.parametrize('show_tin', [True, False])
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(order_proc='carrier')
@pytest.mark.translations(
    client_messages={
        'taxiontheway.carrier.name': {'ru': 'Название: %(name)s'},
        'taxiontheway.carrier.address': {'ru': 'Адрес: %(address)s'},
        'taxiontheway.carrier.ogrn': {'ru': 'ОГРН: %(reg_number)s'},
        'taxiontheway.carrier.working_hours': {
            'ru': 'Часы работы: %(working_hours)s',
        },
    },
)
def test_tow_carrier_enabled_and_carrier_exists(
        taxi_protocol, mockserver, default_driver_position, db, show_tin,
):
    expected_park_result = {
        'legal_address': 'Адрес: Organization Address',
        'working_hours': 'Часы работы: 10-22',
        'name': 'Название: Carrier ltd',
        'ogrn': 'ОГРН: 123456789',
    }
    expected_partner_result = copy.deepcopy(EXPECTED_PARTNER_RESPONSE)
    if show_tin:
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {'$set': {'order.performer.tin': 'tin_number'}},
        )
        expected_partner_result['tin'] = 'tin_number'
        expected_park_result['tin'] = 'tin_number'

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()

    assert content['park'] == expected_park_result
    assert content['partner'] == expected_partner_result


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(
    order_proc='carrier', tariff_settings='disable_legal_entities',
)
@pytest.mark.translations(
    client_messages={
        'taxiontheway.carrier.name': {'ru': 'Название: %(name)s'},
        'taxiontheway.carrier.address': {'ru': 'Адрес: %(address)s'},
        'taxiontheway.carrier.ogrn': {'ru': 'ОГРН: %(reg_number)s'},
        'taxiontheway.carrier.working_hours': {
            'ru': 'Часы работы: %(working_hours)s',
        },
    },
)
def test_tow_carrier_exists_entities_disabled(
        taxi_protocol, mockserver, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert 'park' not in content
    assert 'partner' not in content


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(order_proc='carrier_missing')
@pytest.mark.translations(
    client_messages={
        'taxiontheway.carrier.name': {'ru': 'Название: %(name)s'},
        'taxiontheway.carrier.address': {'ru': 'Адрес: %(address)s'},
        'taxiontheway.carrier.ogrn': {'ru': 'ОГРН: %(reg_number)s'},
        'taxiontheway.carrier.working_hours': {
            'ru': 'Часы работы: %(working_hours)s',
        },
    },
)
def test_tow_carrier_build_enabled_and_carrier_is_missing(
        taxi_protocol, mockserver, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert (
        content['park']
        == content['partner']
        == {
            'name': 'Главное Такси',
            'phone': '+79321259615',
            'yamoney': False,
            'long_name': 'Organization',
            'legal_address': 'Street',
            'id': '999012',
        }
    )


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(order_proc='carrier_empty')
@pytest.mark.translations(
    client_messages={
        'taxiontheway.carrier.name': {'ru': 'Название: %(name)s'},
        'taxiontheway.carrier.address': {'ru': 'Адрес: %(address)s'},
        'taxiontheway.carrier.ogrn': {'ru': 'ОГРН: %(reg_number)s'},
        'taxiontheway.carrier.working_hours': {
            'ru': 'Часы работы: %(working_hours)s',
        },
    },
)
def test_tow_carrier_build_enabled_and_carrier_is_empty(
        taxi_protocol, mockserver, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert (
        content['park']
        == content['partner']
        == {
            'name': 'Главное Такси',
            'phone': '+79321259615',
            'yamoney': False,
            'long_name': 'Organization',
            'legal_address': 'Street',
            'id': '999012',
        }
    )


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(order_proc='carrier_partial')
@pytest.mark.translations(
    client_messages={
        'taxiontheway.carrier.name': {'ru': 'Название: %(name)s'},
        'taxiontheway.carrier.address': {'ru': 'Адрес: %(address)s'},
        'taxiontheway.carrier.ogrn': {'ru': 'ОГРН: %(reg_number)s'},
        'taxiontheway.carrier.working_hours': {
            'ru': 'Часы работы: %(working_hours)s',
        },
    },
)
def test_tow_carrier_build_enabled_and_carrier_has_partial_data(
        taxi_protocol, mockserver, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['park'] == {
        'legal_address': 'Адрес: Organization Address',
        'name': 'Название: Name',
    }
    assert content['partner'] == {
        'name': 'Главное Такси',
        'phone': '+79321259615',
        'yamoney': False,
        'long_name': 'Organization',
        'legal_address': 'Street',
        'id': '999012',
    }


@pytest.mark.translations(
    client_messages={
        'hourly_rental.taxiontheway.transporting.'
        'status_info.card_subtitle_template': {'ru': 'Дополнительное время'},
        'hourly_rental.taxiontheway.transporting.'
        'notifications.prepaid_time_ends_soon.title': {
            'ru': 'prepaid_time_ends_soon.title',
        },
        'hourly_rental.taxiontheway.transporting.'
        'notifications.prepaid_time_ends_soon.subtitle': {
            'ru': 'prepaid_time_ends_soon.subtitle',
        },
        'hourly_rental.taxiontheway.transporting.title': {
            'ru': 'transporting.title',
        },
        'hourly_rental.taxiontheway.transporting.notifications.'
        'prepaid_time_ends_now.title': {'ru': 'prepaid_time_ends_now.title'},
        'hourly_rental.taxiontheway.transporting.notifications.'
        'prepaid_time_ends_now.subtitle': {
            'ru': 'prepaid_time_ends_now.subtitle',
        },
        'hourly_rental.taxiontheway.transporting.cost_message': {
            'ru': '%(price)s, %(paid_time)s, %(paid_distance)s',
        },
    },
)
@pytest.mark.parametrize('show', [False, True])
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(order_proc='hourly_rental', requirements='hourly_rental')
def test_tow_hourly_rental(
        taxi_protocol, default_driver_position, now, db, show,
):
    if show:
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {
                '$push': {
                    'order_info.statistics.status_updates': {
                        'c': now,
                        'h': False,
                        'i': 0,
                        'l': 0.0395042986111,
                        't': 'transporting',
                    },
                },
                '$set': {
                    'status': 'transporting',
                    'order.taxi_status': 'transporting',
                },
            },
        )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()

    assert content['cost_message'] == '2,000 $SIGN$$CURRENCY$, 60, 100'
    assert content['cost_as_str'] == '2,000 $SIGN$$CURRENCY$, 60, 100'
    if show:
        # prepaid_time_ends_at = now + 1 hour
        assert content['status_info'] == {
            'prepaid_time_ends_at': '2016-12-15T09:30:00+0000',
            'translations': {'card': {'title_template': 'transporting.title'}},
        }
        # show_time = prepaid_time_ends_at - 600 sec
        # (config HOURLY_RENTAL_NOTIFICATION_INTERVAL)
        assert content['notifications'] == {
            'prepaid_time_ends_now': {
                'show_count': 1,
                'show_time': '2016-12-15T09:30:00+0000',
                'translations': {
                    'subtitle_template': 'prepaid_time_ends_now.subtitle',
                    'title_template': 'prepaid_time_ends_now.title',
                },
                'type': 'push',
            },
            'prepaid_time_ends_soon': {
                'show_count': 1,
                'show_time': '2016-12-15T09:20:00+0000',
                'translations': {
                    'subtitle_template': 'prepaid_time_ends_soon.subtitle',
                    'title_template': 'prepaid_time_ends_soon.title',
                },
                'type': 'push',
            },
        }
    else:
        assert 'status_info' not in content
        assert 'notifications' not in content


@pytest.mark.translations(
    client_messages={
        'hourly_rental.taxiontheway.cost_breakdown.booking_cost': {
            'en': 'Hourly rental: %(hours_count)s',
        },
        'hourly_rental.taxiontheway.cost_breakdown.taximeter_cost': {
            'en': 'Taximeter cost',
        },
    },
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(order_proc='hourly_rental', requirements='hourly_rental')
def test_tow_hourly_rental_complete(
        taxi_protocol, default_driver_position, db,
):
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$set': {
                'status': 'complete',
                'order.taxi_status': 'complete',
                'order.status': 'finished',
                'order.cost': 3000,
            },
        },
    )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()

    assert content['cost_as_str'] == '3,000 $SIGN$$CURRENCY$'
    assert content['cost_message_details'] == {
        'cost_breakdown': [
            {
                'display_amount': '2,000 $SIGN$$CURRENCY$',
                'display_name': 'Hourly rental: 1',
            },
            {
                'display_amount': '1,000 $SIGN$$CURRENCY$',
                'display_name': 'Taximeter cost',
            },
        ],
    }


@pytest.mark.translations(
    client_messages={
        'hourly_rental.taxiontheway.transporting.title': {
            'ru': 'transporting.title',
        },
        'hourly_rental.taxiontheway.transporting.cost_message': {
            'ru': '%(price)s, %(paid_time)s, %(paid_distance)s',
        },
    },
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(order_proc='hourly_rental', requirements='hourly_rental')
def test_tow_hourly_rental_old_tariff(
        taxi_protocol, default_driver_position, now, db,
):
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$push': {
                'order_info.statistics.status_updates': {
                    'c': now,
                    'h': False,
                    'i': 0,
                    'l': 0.0395042986111,
                    't': 'transporting',
                },
            },
            '$set': {
                'status': 'transporting',
                'order.taxi_status': 'transporting',
                'order.performer.tariff.id': '12312312313123123123123123123',
                'order.performer.tariff.ci': '12312312313123123123123123123',
            },
        },
    )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()

    assert content['cost_message'] == '3,000 $SIGN$$CURRENCY$, 60, 100'
    assert content['cost_as_str'] == '3,000 $SIGN$$CURRENCY$, 60, 100'

    # prepaid_time_ends_at = now + 1 hour
    assert content['status_info'] == {
        'prepaid_time_ends_at': '2016-12-15T09:30:00+0000',
        'translations': {'card': {'title_template': 'transporting.title'}},
    }


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(order_proc='driver_phone_forwarding')
def test_tow_cancel_phone_returned(taxi_protocol, default_driver_position):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'break': 'user',
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )

    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'cancelled'
    assert content['driver']['phone'] == '+79321259615'


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(order_proc='driver_phone_forwarding')
@pytest.mark.config(TAXIONTHEWAY_FETCH_FORWARDING_ON_CANCEL=True)
def test_tow_cancel_forwarding_returned(
        taxi_protocol, default_driver_position,
):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'break': 'user',
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )

    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'cancelled'
    assert content['driver']['phone'] == '+7123456789,,007'


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(orders='paid_supply', order_proc='paid_supply_paid_cancel')
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
@pytest.mark.experiments3(filename='exp3_paid_supply_paid_cancel.json')
@pytest.mark.config(
    FLAT_TIPS_SETTINGS_V3={
        'countries': {
            'rus': {
                '__default__': {
                    'log_base': 14,
                    'percents': [5, 10, 15],
                    'manual_entry_allowed': True,
                    'decimal_digits': 0,
                    'min_tips_value': 10,
                    'tips_limit': {'max_tips': 100},
                    'base_numerator': 10,
                    'base_denominator': 10,
                    'additional_constant': 1,
                },
            },
        },
        'zones': {},
    },
    CURRENCY_FORMATTING_RULES={'__default__': {'__default__': 2}},
)
def test_decimal_values(
        taxi_protocol, recalc_order, default_driver_position, db,
):
    order_id = '8c83b49edb274ce0992f337061047375'
    db.orders.update(
        {'_id': order_id}, {'$set': {'creditcard.tips.type': 'flat'}},
    )
    db.order_proc.update(
        {'_id': order_id}, {'$set': {'order.creditcard.tips.type': 'flat'}},
    )

    recalc_order.set_recalc_result(78.0, 78.0)

    # Cancel request
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'break': 'user',
            'cancel_state': 'paid',
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': order_id,
        },
    )
    assert response.status_code == 200
    content = response.json()

    assert content['cost_decimal_value'] == '78.00'
    assert content['final_cost_decimal_value'] == '78.00'

    dec_val = content['tips_suggestions']['variants'][0]['choices'][0][
        'decimal_value'
    ]
    assert content['tips']['decimal_value'] == '0'
    assert dec_val == '0'
    proc = db.order_proc.find_one({'_id': '8c83b49edb274ce0992f337061047375'})
    order_commit_common.check_current_prices(proc, 'final_cost', 78)


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(orders='multiclass', order_proc='multiclass')
@pytest.mark.translations(
    client_messages={
        'multiclass.notify.description.fixed_price': {
            'ru': 'цена %(localized_cost)s, тариф: %(tariff_name)s',
        },
        'multiclass.notify.description.not_fixed_price': {
            'ru': 'цена от %(localized_cost)s, тариф: %(tariff_name)s',
        },
    },
)
@pytest.mark.parametrize('already_got_notification', [True, False])
@pytest.mark.parametrize('fixed_price', [True, False])
@pytest.mark.fixture_now(datetime.timedelta(minutes=10))
def test_tow_multiclass_notify(
        taxi_protocol, already_got_notification, tracker, now, fixed_price, db,
):
    order_id = '8c83b49edb274ce0992f337061047375'
    tracker.set_position('999012_a5709ce56c2740d9a536650f5390de0b', now, 1, 0)

    request = {
        'format_currency': True,
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': order_id,
    }

    if already_got_notification:
        request['notification_fetched_for_status'] = 'transporting'
    if fixed_price:
        db.orders.update(
            {'_id': order_id}, {'$set': {'order.fixed_price.price': 300}},
        )
        db.order_proc.update(
            {'_id': order_id}, {'$set': {'order.fixed_price.price': 300}},
        )
    response = taxi_protocol.post(
        '3.0/taxiontheway', request, headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200
    content = response.json()
    notifications = content.get('notifications', None)

    if already_got_notification:
        assert notifications is None
    else:
        description = 'цена от 300 $SIGN$$CURRENCY$, тариф: Эконом'
        if fixed_price:
            description = 'цена 300 $SIGN$$CURRENCY$, тариф: Эконом'
        assert notifications == {
            'multiclass_assign': {
                'mode': 'per_order',
                'type': 'multiclass_assign',
                'show_count': 1,
                'translations': {'title': description},
            },
        }


@pytest.mark.filldb(orders='eta_transporting', order_proc='eta_transporting')
def test_point_passed_status_in_response(
        taxi_protocol, tracker, now, db, load_binary,
):
    order_id = '8c83b49edb274ce0992f337061047375'
    user_id = 'b300bda7d41b4bae8d58dfa93221ef16'
    destinations_statuses = [True, False, False]
    update_destinations_statuses(db, order_id, destinations_statuses)

    tracker.set_position('999012_a5709ce56c2740d9a536650f5390de0b', now, 1, 0)

    response = make_taxiontheway_request(taxi_protocol, user_id, order_id)
    assert response.status_code == 200
    content = response.json()

    check_points_statuses(content, destinations_statuses)

    new_destinations_statuses = [True, True, False]
    update_destinations_statuses(db, order_id, new_destinations_statuses)

    response = make_taxiontheway_request(taxi_protocol, user_id, order_id)
    assert response.status_code == 200
    content = response.json()

    check_points_statuses(content, new_destinations_statuses)


@pytest.mark.translations(
    client_messages={
        'courier.taxiontheway.driving.title': {'ru': 'courier title'},
        'courier.taxiontheway.driving.subtitle': {'ru': 'courier %(name)s'},
    },
    geoareas={'moscow': {'en': 'Москва'}},
    tariff={'old_category_name.courier': {'en': 'Courier'}},
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(order_proc='driving_courier')
@pytest.mark.config(
    TOTW_STATUS_INFO_BY_CLASS={
        '__default__': {},
        'courier': {
            'driving': {
                'card': {
                    'title': 'courier.taxiontheway.driving.title',
                    'subtitle': 'courier.taxiontheway.driving.subtitle',
                },
            },
        },
    },
)
def test_totw_courier_statuses(
        taxi_protocol, default_driver_position, now, db,
):
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$push': {
                'order_info.statistics.status_updates': {
                    'c': now,
                    'h': False,
                    'i': 0,
                    'l': 0.0395042986111,
                    't': 'driving',
                },
            },
            '$set': {
                'status': 'driving',
                'order.taxi_status': 'driving',
                'order.performer.tariff.id': '12312312313123123123123123123',
                'order.performer.tariff.ci': '12312312313123123123123123123',
            },
        },
    )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status_info'] == {
        'translations': {
            'card': {
                'title_template': 'courier title',
                'subtitle_template': 'courier Бородач Исак Арнольдович',
            },
        },
    }


@pytest.mark.now('2020-05-29T15:35:00+0300')
@pytest.mark.filldb(
    orders='transporting_cancel_limit', order_proc='transporting_cancel_limit',
)
@pytest.mark.config(CARGO_ORDERS_CANCEL_FORBIDDEN=True)
def test_cancel_cargo_order(
        taxi_protocol, default_driver_position, db, config, mocked_time,
):
    osu = mocked_time.now - datetime.timedelta(seconds=200)
    # Make order cargo
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$set': {
                'order.status_updated': osu,
                'order.request.cargo_ref_id': (
                    'f7793a14a2e94cd78dbdb2831476aafc'
                ),
                'order.application': 'cargo',
            },
        },
    )
    # Cancel request
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'break': 'user',
            'cancel_state': 'paid',
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'cancelled'


ORDER_AND_PROC_COURIER_UPDATES = [
    (
        'orders',
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            'calc.allowed_tariffs.__park__': {'courier': 190},
            'performer.tariff.class': 'courier',
            'request.class': ['courier'],
        },
    ),
    (
        'order_proc',
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            'order.performer.tariff.class': 'courier',
            'candidates.0.tariff_class': 'courier',
            'order.request.class': ['courier'],
        },
    ),
]

DBDRIVERS_WALKING_COURIER_UPDATE = (
    'dbdrivers',
    {'driver_id': 'a5709ce56c2740d9a536650f5390de0b'},
    {'courier_type': 'walking_courier'},
)


@pytest.mark.translations(
    tariff={'old_category_name.courier': {'en': 'Courier'}},
)
@pytest.mark.filldb(orders='eta_transporting', order_proc='eta_transporting')
@pytest.mark.config(ROUTER_MAPS_ENABLED=True)
@pytest.mark.parametrize(
    'is_exp_enabled',
    [
        pytest.param(
            False,
            marks=pytest.mark.experiments3(
                filename='exp3_totw_use_pedestrian_router_disabled.json',
            ),
        ),
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                filename='exp3_totw_use_pedestrian_router_enabled.json',
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'is_pedestrian,mongo_updates',
    [
        pytest.param(False, [], id='Not a courier'),
        pytest.param(False, ORDER_AND_PROC_COURIER_UPDATES, id='Car courier'),
        pytest.param(
            True,
            [
                *ORDER_AND_PROC_COURIER_UPDATES,
                DBDRIVERS_WALKING_COURIER_UPDATE,
            ],
            id='Pedestrian courier',
        ),
    ],
)
def test_pedestrian_courier_router(
        taxi_protocol,
        db,
        tracker,
        mockserver,
        load_binary,
        now,
        is_exp_enabled,
        is_pedestrian,
        mongo_updates,
):
    @mockserver.json_handler('/maps-router/route_jams/')
    def _router(request):
        return mockserver.make_response(
            load_binary('route_jams.protobuf'),
            content_type='application/x-protobuf',
        )

    @mockserver.json_handler('/router-yamaps-masstransit/pedestrian/route')
    def _pedestrian_router(request):
        return mockserver.make_response(
            load_binary('pedestrian_route.protobuf'),
            content_type='application/x-protobuf',
        )

    tracker.set_position('999012_a5709ce56c2740d9a536650f5390de0b', now, 1, 0)
    for mongo_update in mongo_updates:
        update_mongo(db, *mongo_update)

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )

    assert response.status_code == 200
    if is_exp_enabled and is_pedestrian:
        assert _router.times_called == 0
        assert _pedestrian_router.times_called == 1
    else:
        assert _router.times_called == 1
        assert _pedestrian_router.times_called == 0


@pytest.mark.translations(
    client_messages={
        'courier.taxiontheway.driving.title': {'ru': 'courier title'},
        'courier.taxiontheway.driving.subtitle': {'ru': 'courier %(name)s'},
        'courier.taxiontheway.driver.model': {'ru': 'Пеший курьер'},
    },
    geoareas={'moscow': {'en': 'Москва'}},
    tariff={'old_category_name.courier': {'en': 'Courier'}},
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(order_proc='driving_courier')
@pytest.mark.config(
    TOTW_STATUS_INFO_BY_CLASS={
        '__default__': {},
        'courier': {
            'driving': {
                'card': {
                    'title': 'courier.taxiontheway.driving.title',
                    'subtitle': 'courier.taxiontheway.driving.subtitle',
                },
            },
        },
    },
)
@pytest.mark.config(
    CONTRACTOR_TRANSPORT_HIDE_ENABLED={
        '__default__': False,
        'taxiontheway': True,
    },
)
@pytest.mark.config()
@pytest.mark.parametrize(
    'model, color, plates',
    [
        pytest.param(
            'Skoda Fabia',
            True,
            True,
            marks=[
                pytest.mark.config(
                    CONTRACTOR_TRANSPORT_HIDE_SETTINGS={
                        '__default__': {
                            'number': False,
                            'model': False,
                            'color': False,
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            '',
            False,
            False,
            marks=[
                pytest.mark.config(
                    CONTRACTOR_TRANSPORT_HIDE_SETTINGS={
                        '__default__': {
                            'number': False,
                            'model': False,
                            'color': False,
                        },
                        'pedestrian': {
                            'number': True,
                            'model': True,
                            'color': True,
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            'Пеший курьер',
            False,
            False,
            marks=[
                pytest.mark.config(
                    CONTRACTOR_TRANSPORT_HIDE_SETTINGS={
                        '__default__': {
                            'number': False,
                            'model': False,
                            'color': False,
                        },
                        'pedestrian': {
                            'number': True,
                            'model': True,
                            'color': True,
                            'model_template_key': (
                                'courier.taxiontheway.driver.model'
                            ),
                        },
                    },
                ),
            ],
        ),
    ],
)
def test_totw_hide_transport(
        taxi_protocol,
        default_driver_position,
        db,
        mockserver,
        plates,
        model,
        color,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def mock_personal(request):
        request_json = json.loads(request.get_data())
        assert request_json == {'id': '1fab75363700481a9adf5e31c3b6e673'}
        return {
            'id': '1fab75363700481a9adf5e31c3b6e673',
            'value': '+79031520355',
        }

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )

    driver = response.json()['driver']
    if plates:
        assert driver['plates']
    else:
        assert 'plates' not in driver

    if color:
        assert driver['color']
    else:
        assert 'color' not in driver
    assert driver['model'] == model
    assert driver['color_code']


@pytest.mark.filldb
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_agent_payment_no_fail(
        taxi_protocol, db, now, mockserver, tracker, pricing_data_preparer,
):
    tracker.set_position('999012_a5709ce56c2740d9a536650f5390de0b', now, 1, 0)

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def mock_personal(request):
        return {
            'id': '1fab75363700481a9adf5e31c3b6e673',
            'value': '+79031520355',
        }

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '10eaaafb1afb48c084a2e536b95bfa5d',
        },
    )
    assert response.status_code == 200


def test_tow_currency_rules(taxi_protocol, default_driver_position):
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['currency_rules'] == {
        'code': 'RUB',
        'cost_precision': 0,
        'sign': '₽',
        'template': '$VALUE$\xa0$SIGN$$CURRENCY$',
        'text': 'rub',
    }
