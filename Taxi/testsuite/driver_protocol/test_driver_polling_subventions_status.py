# coding=utf-8
from copy import deepcopy
import json
from random import shuffle

import pytest

from . import common


DMS_ACTIVITY_VALUES = {'5b7b0c694f007eaf8578b531': 94}


def _check_subvention_view_status_query(
        request, session, lon, lat, park_id, order_id, subventions_id,
):
    assert request.headers['Accept-Language'] == 'en'
    assert (
        request.headers['User-Agent']
        == 'yandex-taxi/3.18.0.7675 Android/6.0 (testenv client)'
    )
    assert request.headers['X-Driver-Session'] == session
    args = request.args
    assert float(args['lon']) == float(lon)
    assert float(args['lat']) == float(lat)
    assert args['subventions_id'] == subventions_id
    assert args['park_id'] == park_id
    assert args.get('order_id') == order_id


def _prepare_driver_points_in_expected_result(expected_response, dms_context):
    if not dms_context.use_dms_driver_points:
        return expected_response
    response = deepcopy(expected_response)
    for subvention_status in response['subventions_status']:
        if 'description_items' not in subvention_status:
            continue
        for description_item in subvention_status['description_items']:
            if 'subtitle' not in description_item:
                continue
            if description_item['subtitle'] == 'У Вас 90':
                description_item['subtitle'] = 'У Вас ' + str(
                    int(
                        dms_context.fetch_driver_points(
                            '5b7b0c694f007eaf8578b531',
                        ),
                    ),
                )
    return response


@pytest.mark.now('1970-01-01T00:00:12Z')
@pytest.mark.parametrize(
    ('request_arguments', 'expect_dms_called', 'expected_status_code'),
    [
        (  # request_arguments0
            {  # Success. No order_id
                'db': '777',
                'session': 'qwerty',
                'lon': '37.6',
                'lat': '55.73',
                'subventions_id': '_id/subvention_1',
            },
            True,
            200,
        ),
        (  # request_arguments1
            {  # Success. Order found by order_id
                'db': '777',
                'session': 'qwerty',
                'lon': '37.6',
                'lat': '55.73',
                'subventions_id': '_id/subvention_1',
                'order_id': 'order_id_0',
            },
            True,
            200,
        ),
        (  # request_arguments2
            {  # Success. Order found by alias_id
                'db': '777',
                'session': 'qwerty',
                'lon': '37.6',
                'lat': '55.73',
                'subventions_id': '_id/subvention_1',
                'order_id': 'alias_id_0',
            },
            True,
            200,
        ),
        (  # request_arguments3
            {  # Success. Order doesn't exist
                'db': '777',
                'session': 'qwerty',
                'lon': '37.6',
                'lat': '55.73',
                'subventions_id': '_id/subvention_1',
                'order_id': 'non_existing_order_id',
            },
            True,
            200,
        ),
        (  # request_arguments4
            {
                'db': '777',
                'session': 'qwerty',
                'lon': '37.6',
                'subventions_id': '_id/subvention_1',
            },
            False,
            500,
        ),
        (  # request_arguments5
            {
                'lon': '37.6',
                'lat': '55.73',
                'subventions_id': '_id/subvention_1',
            },
            False,
            401,
        ),
        (  # request_arguments6
            {
                'db': '777',
                'session': 'qwerty',
                'lon': 'not_a_number',
                'lat': '55.73',
                'subventions_id': '_id/subvention_1',
            },
            False,
            500,
        ),
        (  # request_arguments7
            {
                'db': '777',
                'session': 'qwerty',
                'lon': '37.6',
                'lat': 'not_a_number',
                'subventions_id': '_id/subvention_1',
            },
            False,
            500,
        ),
    ],
)
@pytest.mark.config(
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=True,
    ENABLE_SUBVENTIONS_STATUS_ACTIVE_ON_ORDER_ACCEPTED_IN_ZONE=True,
    SUBVENTIONS_STATUS_SORT_RESPONSE_ITEMS=True,
    BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=[
        '/driver/polling/subvention-status',
    ],
)
@pytest.mark.parametrize(
    'dummy',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.filldb(localization_tariff='old_category'),
                pytest.mark.config(
                    USE_OLD_TANKER_TARIFF_CLASSES_IN_SUBVENTIONS_STATUS=True,
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    USE_OLD_TANKER_TARIFF_CLASSES_IN_SUBVENTIONS_STATUS=False,
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize('proxy_mode', ('no_proxy', 'compare', 'proxy'))
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_geoareas_arguments_validation(
        mockserver,
        now,
        bss,
        taxi_driver_protocol,
        load_json,
        request_arguments,
        expect_dms_called,
        expected_status_code,
        driver_authorizer_service,
        dummy,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
        proxy_mode,
):
    config.set_values(dict(SUBVENTION_VIEW_STATUS_PROXY_MODE=proxy_mode))
    dms_context.set_expect_dms_called(
        dms_context.expect_dms_called
        and expect_dms_called
        and proxy_mode != 'proxy',
    )

    @mockserver.json_handler('/subvention_view/v1/status')
    def mock_subvention_view_status(request):
        assert proxy_mode != 'no_proxy'
        _check_subvention_view_status_query(
            request,
            request_arguments['session'],
            request_arguments['lon'],
            request_arguments['lat'],
            request_arguments['db'],
            request_arguments.get('order_id'),
            request_arguments['subventions_id'],
        )
        if expected_status_code == 500:
            return
        return {'subventions_status': []}

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_tracker_profile(request):
        return load_json('tracker_response.json')

    driver_authorizer_service.set_session('777', 'qwerty', '888')

    rules = load_json('rules_select_response.json')
    shuffle(rules)
    for rule in rules:
        bss.add_rule(rule)

    for rule_status in load_json('by_driver_response.json'):
        bss.add_by_driver_subvention(rule_status)

    taxi_driver_protocol.invalidate_caches(now=now)

    response = taxi_driver_protocol.get(
        'driver/polling/subventions_status?'
        + '&'.join(['='.join(kv) for kv in request_arguments.items()]),
    )

    assert response.status_code == expected_status_code
    bss.clean_rules()
    bss.clean_by_driver_subvention()
    if expected_status_code == 200:
        assert mock_subvention_view_status.times_called == (
            proxy_mode != 'no_proxy'
        )


@pytest.mark.now('1970-01-01T00:00:12Z')
@pytest.mark.parametrize(
    ('rules_file', 'rules_status_file', 'current_point', 'order_id'),
    (
        (  # current and order accept points are in moscow zone
            'rules_select_response.json',
            'by_driver_response.json',
            [37.6, 55.75],
            None,
        ),
    ),
)
@pytest.mark.parametrize(
    'dummy',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.filldb(localization_tariff='old_category'),
                pytest.mark.config(
                    USE_OLD_TANKER_TARIFF_CLASSES_IN_SUBVENTIONS_STATUS=True,
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    USE_OLD_TANKER_TARIFF_CLASSES_IN_SUBVENTIONS_STATUS=False,
                ),
            ],
        ),
    ],
)
@pytest.mark.config(
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=False,
    ENABLE_SUBVENTIONS_STATUS_ACTIVE_ON_ORDER_ACCEPTED_IN_ZONE=True,
    BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=[
        '/driver/polling/subvention-status',
    ],
)
@pytest.mark.parametrize(
    'subvention_view_fails, proxy_mode, expected_dp_response_file,'
    'expected_sv_response_file',
    (
        (True, 'compare', 'expected_response.json', 'expected_response.json'),
        (True, 'proxy', None, None),
        (
            False,
            'compare',
            'expected_response.json',
            'expected_zeroed_status_response.json',
        ),
        (
            False,
            'proxy',
            'expected_response.json',
            'expected_zeroed_status_response.json',
        ),
    ),
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_view_fail_or_different(
        mockserver,
        now,
        bss,
        taxi_driver_protocol,
        load_json,
        rules_file,
        rules_status_file,
        current_point,
        order_id,
        expected_dp_response_file,
        expected_sv_response_file,
        driver_authorizer_service,
        dummy,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
        proxy_mode,
        subvention_view_fails,
):
    config.set_values(dict(SUBVENTION_VIEW_STATUS_PROXY_MODE=proxy_mode))
    dms_context.set_expect_dms_called(
        dms_context.expect_dms_called and proxy_mode != 'proxy',
    )

    driver_authorizer_service.set_session('777', 'qwerty', '888')

    rules = load_json(rules_file)
    rules_status = load_json(rules_status_file)

    # Setting up bss
    for rule in rules_status:
        bss.add_by_driver_subvention(rule)

    subventions_ids = ['some_random_id']
    for rule in rules:
        bss.add_rule(rule)
        subventions_ids.append(rule['subvention_rule_id'])
    subventions_ids_str = ','.join(subventions_ids)

    @mockserver.json_handler('/subvention_view/v1/status')
    def mock_subvention_view_status(request):
        _check_subvention_view_status_query(
            request,
            'qwerty',
            current_point[0],
            current_point[1],
            '777',
            order_id if order_id else None,
            subventions_ids_str,
        )
        if subvention_view_fails:
            return
        expected_response = load_json(expected_sv_response_file)
        return _prepare_driver_points_in_expected_result(
            expected_response, dms_context,
        )

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_tracker_profile(request):
        tracker_response = load_json('tracker_response.json')
        tracker_response['point'] = current_point
        return tracker_response

    taxi_driver_protocol.invalidate_caches(now=now)

    assert len(current_point) == 2
    lon, lat = current_point
    request = (
        'driver/polling/subventions_status?'
        'db=777&session=qwerty&lon={}&lat={}&subventions_id={}{}'.format(
            lon,
            lat,
            subventions_ids_str,
            '&order_id=' + order_id if order_id else '',
        )
    )
    response = taxi_driver_protocol.get(request)
    if subvention_view_fails and proxy_mode == 'proxy':
        assert response.status_code == 500
        return
    assert response.status_code == 200

    expected_response = {}
    if proxy_mode == 'proxy':
        expected_response = load_json(expected_sv_response_file)
    else:
        expected_response = load_json(expected_dp_response_file)

    response = response.json()
    response['subventions_status'].sort(key=lambda k: k['id'], reverse=True)
    assert response == _prepare_driver_points_in_expected_result(
        expected_response, dms_context,
    )
    assert mock_subvention_view_status.times_called == (
        proxy_mode != 'no_proxy'
    )
    if proxy_mode == 'proxy':
        return
    rules_select_response = json.loads(
        bss.rules_select_subventions_call_params[0],
    )
    rules_select_response['rule_ids'].sort(reverse=True)
    assert rules_select_response == {
        'limit': 1000,
        'status': 'enabled',
        'tariff_zone': 'moscow',
        'rule_ids': [
            'some_random_id',
            '_id/subvention_3',
            '_id/subvention_2',
            '_id/subvention_1',
        ],
    }

    by_driver_response = json.loads(bss.by_driver_subventions_call_params[0])
    by_driver_response['subvention_rule_ids'].sort(reverse=True)
    assert by_driver_response == {
        'subvention_rule_ids': ['_id/subvention_2', '_id/subvention_1'],
        'time_range': {
            'end_time': '1970-01-01T21:00:00+00:00',
            'start_time': '1969-12-31T21:00:00+00:00',
        },
        'unique_driver_id': '5b7b0c694f007eaf8578b531',
    }

    bss.clean_rules()
    bss.clean_by_driver_subvention()


@pytest.mark.now('1970-01-01T00:00:12Z')
@pytest.mark.parametrize(
    (
        'rules_file',
        'rules_status_file',
        'current_point',
        'order_id',
        'expected_response_file',
    ),
    [
        (  # current and order accept points are in moscow zone
            'rules_select_response.json',
            'by_driver_response.json',
            [37.6, 55.75],
            None,
            'expected_response.json',
        ),
        (  # current and order accept points are in moscow zone
            'rules_select_response.json',
            'by_driver_response_empty.json',
            [37.6, 55.75],
            None,
            'expected_zeroed_status_response.json',
        ),
        (  # order accept point is in moscow zone, current point is outside
            'rules_select_response.json',
            'by_driver_response.json',
            [37.327150, 55.821896],
            'order_id_0',
            'expected_out_of_zone_response_1.json',
        ),
        (  # the same but find by alias_id instead of order_id
            'rules_select_response.json',
            'by_driver_response.json',
            [37.327150, 55.821896],
            'alias_id_0',
            'expected_out_of_zone_response_1.json',
        ),
        (  # current and order accept points are outside moscow zone
            'rules_select_response.json',
            'by_driver_response.json',
            [37.327150, 55.821896],
            'order_id_1',
            'expected_out_of_zone_response_2.json',
        ),
        (  # current and order accept points are outside moscow zone
            'rules_select_response.json',
            'by_driver_response.json',
            [37.327150, 55.821896],
            'unknown_order_id',
            'expected_out_of_zone_response_2.json',
        ),
    ],
)
@pytest.mark.parametrize(
    'dummy',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.filldb(localization_tariff='old_category'),
                pytest.mark.config(
                    USE_OLD_TANKER_TARIFF_CLASSES_IN_SUBVENTIONS_STATUS=True,
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    USE_OLD_TANKER_TARIFF_CLASSES_IN_SUBVENTIONS_STATUS=False,
                ),
            ],
        ),
    ],
)
@pytest.mark.config(
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=False,
    ENABLE_SUBVENTIONS_STATUS_ACTIVE_ON_ORDER_ACCEPTED_IN_ZONE=True,
    SUBVENTIONS_STATUS_SORT_RESPONSE_ITEMS=True,
    BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=[
        '/driver/polling/subvention-status',
    ],
)
@pytest.mark.parametrize('proxy_mode', ('no_proxy', 'compare', 'proxy'))
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_active_subvention_geoareas(
        mockserver,
        now,
        bss,
        taxi_driver_protocol,
        load_json,
        rules_file,
        rules_status_file,
        current_point,
        order_id,
        expected_response_file,
        driver_authorizer_service,
        dummy,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
        proxy_mode,
):
    config.set_values(dict(SUBVENTION_VIEW_STATUS_PROXY_MODE=proxy_mode))
    dms_context.set_expect_dms_called(
        dms_context.expect_dms_called and proxy_mode != 'proxy',
    )

    driver_authorizer_service.set_session('777', 'qwerty', '888')

    rules = load_json(rules_file)
    rules_status = load_json(rules_status_file)
    expected_response = load_json(expected_response_file)
    # Setting up bss
    for rule in rules_status:
        bss.add_by_driver_subvention(rule)

    subventions_ids = ['some_random_id']
    shuffle(rules)
    for rule in rules:
        bss.add_rule(rule)
        subventions_ids.append(rule['subvention_rule_id'])
    subventions_ids_str = ','.join(subventions_ids)

    @mockserver.json_handler('/subvention_view/v1/status')
    def mock_subvention_view_status(request):
        assert proxy_mode != 'no_proxy'
        _check_subvention_view_status_query(
            request,
            'qwerty',
            current_point[0],
            current_point[1],
            '777',
            order_id if order_id else None,
            subventions_ids_str,
        )
        return _prepare_driver_points_in_expected_result(
            expected_response, dms_context,
        )

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_tracker_profile(request):
        tracker_response = load_json('tracker_response.json')
        tracker_response['point'] = current_point
        return tracker_response

    taxi_driver_protocol.invalidate_caches(now=now)

    assert len(current_point) == 2
    lon, lat = current_point
    request = (
        'driver/polling/subventions_status?'
        'db=777&session=qwerty&lon={}&lat={}&subventions_id={}{}'.format(
            lon,
            lat,
            subventions_ids_str,
            '&order_id=' + order_id if order_id else '',
        )
    )
    response = taxi_driver_protocol.get(request)
    assert response.status_code == 200
    response = response.json()
    assert response == _prepare_driver_points_in_expected_result(
        expected_response, dms_context,
    )
    assert mock_subvention_view_status.times_called == (
        proxy_mode != 'no_proxy'
    )
    if proxy_mode == 'proxy':
        return
    rules_select_response = json.loads(
        bss.rules_select_subventions_call_params[0],
    )
    rules_select_response['rule_ids'].sort(reverse=True)
    assert rules_select_response == {
        'limit': 1000,
        'status': 'enabled',
        'tariff_zone': 'moscow',
        'rule_ids': [
            'some_random_id',
            '_id/subvention_3',
            '_id/subvention_2',
            '_id/subvention_1',
        ],
    }

    by_driver_response = json.loads(bss.by_driver_subventions_call_params[0])
    by_driver_response['subvention_rule_ids'].sort(reverse=True)
    assert by_driver_response == {
        'subvention_rule_ids': ['_id/subvention_2', '_id/subvention_1'],
        'time_range': {
            'end_time': '1970-01-01T21:00:00+00:00',
            'start_time': '1969-12-31T21:00:00+00:00',
        },
        'unique_driver_id': '5b7b0c694f007eaf8578b531',
    }

    bss.clean_rules()
    bss.clean_by_driver_subvention()


@pytest.mark.now('1970-01-01T00:00:12Z')
@pytest.mark.parametrize(
    ('rules_file', 'rules_status_file', 'show_if_0'),
    [
        ('rules_select_response.json', 'by_driver_response.json', True),
        ('rules_select_response.json', 'by_driver_response.json', False),
    ],
)
@pytest.mark.config(
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=False,
    ENABLE_SUBVENTIONS_STATUS_ACTIVE_ON_ORDER_ACCEPTED_IN_ZONE=True,
    SUBVENTIONS_STATUS_SORT_RESPONSE_ITEMS=True,
    BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=[
        '/driver/polling/subvention-status',
    ],
)
@pytest.mark.parametrize('proxy_mode', ('no_proxy', 'compare', 'proxy'))
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_show_activity_restriction(
        mockserver,
        bss,
        taxi_driver_protocol,
        load_json,
        rules_file,
        rules_status_file,
        show_if_0,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
        proxy_mode,
):
    config.set_values(
        dict(
            SUBVENTIONS_GEO_BOOKING_SHOW_ZERO_ACTIVITY_RESTRICTIONS=show_if_0,
            SUBVENTION_VIEW_STATUS_PROXY_MODE=proxy_mode,
        ),
    )
    dms_context.set_expect_dms_called(
        dms_context.expect_dms_called and proxy_mode != 'proxy',
    )

    driver_authorizer_service.set_session('777', 'qwerty', '888')

    rules = load_json(rules_file)
    rules_status = load_json(rules_status_file)

    # Setting up bss
    for rule in rules_status:
        bss.add_by_driver_subvention(rule)

    subventions_ids = ['some_random_id']
    for rule in rules:
        bss.add_rule(rule)
        subventions_ids.append(rule['subvention_rule_id'])
    subventions_ids_str = ','.join(subventions_ids)

    @mockserver.json_handler('/subvention_view/v1/status')
    def mock_subvention_view_status(request):
        assert proxy_mode != 'no_proxy'
        _check_subvention_view_status_query(
            request, 'qwerty', 37.6, 55.75, '777', '', subventions_ids_str,
        )
        response = {
            'subventions_status': [
                {'id': 'a'},
                {'id': 'b'},
                {
                    'id': '_id/subvention_1',
                    'description_items': [{}, {'title': ''}],
                },
            ],
        }
        if show_if_0:
            response['subventions_status'][2]['description_items'][1][
                'title'
            ] = 'Активность не ниже 0'
        return response

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_tracker_profile(request):
        tracker_response = load_json('tracker_response.json')
        tracker_response['point'] = [37.6, 55.75]
        return tracker_response

    request = (
        'driver/polling/subventions_status?'
        'db=777&session=qwerty&lon={}&lat={}&subventions_id={}{}'.format(
            37.6, 55.75, ','.join(subventions_ids), '&order_id=',
        )
    )
    response = taxi_driver_protocol.get(request)
    assert response.status_code == 200
    response = response.json()
    subvention_1 = response['subventions_status'][2]
    assert subvention_1['id'] == '_id/subvention_1'
    assert (
        subvention_1['description_items'][1]['title'] == 'Активность не ниже 0'
    ) == show_if_0

    assert mock_subvention_view_status.times_called == (
        proxy_mode != 'no_proxy'
    )
    if proxy_mode == 'proxy':
        return
    rules_select_response = json.loads(
        bss.rules_select_subventions_call_params[0],
    )
    rules_select_response['rule_ids'].sort(reverse=True)
    assert rules_select_response == {
        'limit': 1000,
        'status': 'enabled',
        'tariff_zone': 'moscow',
        'rule_ids': [
            'some_random_id',
            '_id/subvention_3',
            '_id/subvention_2',
            '_id/subvention_1',
        ],
    }

    by_driver_response = json.loads(bss.by_driver_subventions_call_params[0])
    by_driver_response['subvention_rule_ids'].sort(reverse=True)
    assert by_driver_response == {
        'subvention_rule_ids': ['_id/subvention_2', '_id/subvention_1'],
        'time_range': {
            'end_time': '1970-01-01T21:00:00+00:00',
            'start_time': '1969-12-31T21:00:00+00:00',
        },
        'unique_driver_id': '5b7b0c694f007eaf8578b531',
    }

    bss.clean_rules()
    bss.clean_by_driver_subvention()


TEMPLATE_RULE = {
    'tariff_zones': ['moscow'],
    'status': 'enabled',
    'start': '2019-02-26T21:00:00.000000+00:00',
    'end': '2019-03-28T21:00:00.000000+00:00',
    'type': 'geo_booking',
    'is_personal': False,
    'taxirate': '',
    'subvention_rule_id': '_id/subvention_1',
    'cursor': '2019-03-28T21:00:00.000000+00:00/5c768761254e5eb96aa023b4',
    'tags': [],
    'time_zone': {'id': 'Europe/Moscow', 'offset': '+03:00'},
    'currency': 'RUB',
    'updated': '2019-02-27T12:49:37.835000+00:00',
    'tariff_classes': ['econom'],
    'has_commission': False,
    'week_days': ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
    'geoareas': ['polygon'],
    'workshift': {'start': '14:00', 'end': '14:15'},
    'payment_type': 'add',
    'min_activity_points': 2,
    'min_online_minutes': 2,
    'rate_on_order_per_minute': '1024',
    'rate_free_per_minute': '1024',
    'hours': [],
    'visible_to_driver': True,
    'order_payment_type': None,
    'profile_payment_type_restrictions': 'none',
}

SATISFY_CRITERIA = {
    'none': {'none': True, 'cash': True, 'online': True, 'any': True},
    'cash': {'none': False, 'cash': True, 'online': False, 'any': True},
    'online': {'none': False, 'cash': False, 'online': True, 'any': True},
}


@pytest.mark.now('1970-01-01T00:00:12Z')
@pytest.mark.parametrize('driver_payment_type', ['none', 'cash', 'online'])
@pytest.mark.parametrize(
    'restriction_payment_type', ['none', 'cash', 'online', 'any'],
)
@pytest.mark.config(
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=False,
    BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=[
        '/driver/polling/subvention-status',
    ],
    SUBVENTIONS_GEO_BOOKING_SHOW_PAYMENT_RESTRICTIONS=True,
)
@pytest.mark.parametrize('proxy_mode', ('no_proxy', 'compare', 'proxy'))
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_payment_type_restriction(
        mockserver,
        now,
        bss,
        taxi_driver_protocol,
        load_json,
        driver_payment_type,
        restriction_payment_type,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
        proxy_mode,
):
    config.set_values(dict(SUBVENTION_VIEW_STATUS_PROXY_MODE=proxy_mode))
    dms_context.set_expect_dms_called(
        dms_context.expect_dms_called and proxy_mode != 'proxy',
    )
    driver_payment_type_loc = {
        'none': 'любой',
        'cash': 'наличные',
        'online': 'картой',
    }
    restriction_payment_type_loc = {
        'none': 'любой',
        'cash': 'наличные',
        'online': 'картой',
    }

    descr_item = {}
    satisfy = SATISFY_CRITERIA[driver_payment_type][restriction_payment_type]
    if restriction_payment_type != 'any':
        descr_item = {
            'subtitle': (
                'у вас выбрана оплата '
                + driver_payment_type_loc[driver_payment_type]
            ),
            'title': (
                'нужна оплата '
                + restriction_payment_type_loc[restriction_payment_type]
            ),
            'type': 'tip_detail',
        }

        if satisfy:
            descr_item['left_tip'] = {
                'background_color': '#F1F0ED',
                'form': 'round',
                'icon': {'icon_type': 'check', 'tint_color': '#0596FA'},
            }
        else:
            descr_item['left_tip'] = {
                'background_color': '#FA3E2C',
                'form': 'round',
                'icon': {'icon_type': 'cross', 'tint_color': '#FFFFFF'},
            }

    driver_authorizer_service.set_session('777', 'qwerty', '888')

    rules_status = load_json('by_driver_response.json')

    rule = TEMPLATE_RULE
    rule['profile_payment_type_restrictions'] = restriction_payment_type
    subventions_id = []
    bss.add_rule(rule)
    subventions_id.append(rule['subvention_rule_id'])
    subventions_ids_str = ','.join(subventions_id)

    @mockserver.json_handler('/subvention_view/v1/status')
    def mock_subvention_view_status(request):
        assert proxy_mode != 'no_proxy'
        _check_subvention_view_status_query(
            request, 'qwerty', 37.6, 55.75, '777', '', subventions_ids_str,
        )
        res = {'subventions_status': [{}]}
        subv = res['subventions_status'][0]
        satisfy = SATISFY_CRITERIA[driver_payment_type][
            restriction_payment_type
        ]
        subv['are_restrictions_satisfied'] = satisfy
        if restriction_payment_type != 'any':
            subv['description_items'] = []
            subv['description_items'].append(descr_item)
        return res

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_tracker_profile(request):
        tracker_response = load_json('tracker_response.json')
        tracker_response['point'] = [37.6, 55.75]
        return tracker_response

    @mockserver.json_handler('/tracker/service/drivers-classes-bulk')
    def mock_drivers_classes_bulk(request):
        return {
            'results': [
                {
                    'driver_classes': ['econom'],
                    'payment_type_restrictions': driver_payment_type,
                    'uuid': '888',
                    'clid': 'clid777',
                },
            ],
        }

    # Setting up bss
    for rule in rules_status:
        if rule['subvention_rule_id'] in subventions_id:
            bss.add_by_driver_subvention(rule)

    request = (
        'driver/polling/subventions_status?'
        'db=777&session=qwerty&lon={}&lat={}&subventions_id={}{}'.format(
            37.6, 55.75, subventions_ids_str, '&order_id=',
        )
    )
    response = taxi_driver_protocol.get(request)
    assert response.status_code == 200
    res = response.json()

    subv = res['subventions_status'][0]
    assert subv['are_restrictions_satisfied'] == satisfy
    if restriction_payment_type != 'any':
        assert descr_item in subv['description_items']

    assert mock_subvention_view_status.times_called == (
        proxy_mode != 'no_proxy'
    )
    bss.clean_rules()
    bss.clean_by_driver_subvention()


@pytest.mark.now('1970-01-01T00:00:12Z')
@pytest.mark.config(
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=False,
    BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=[
        '/driver/polling/subvention-status',
    ],
    SUBVENTIONS_GEO_BOOKING_SHOW_PAYMENT_RESTRICTIONS=True,
    USE_PARK_UUID_FOR_CLASSES_IN_SUBVENTIONS=True,
)
@pytest.mark.parametrize('proxy_mode', ('no_proxy', 'compare', 'proxy'))
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_driver_categories(
        mockserver,
        now,
        bss,
        taxi_driver_protocol,
        load_json,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
        proxy_mode,
):
    config.set_values(dict(SUBVENTION_VIEW_STATUS_PROXY_MODE=proxy_mode))
    dms_context.set_expect_dms_called(
        dms_context.expect_dms_called and proxy_mode != 'proxy',
    )

    driver_authorizer_service.set_session('777', 'qwerty', '888')

    rules_status = load_json('by_driver_response.json')

    rule = TEMPLATE_RULE
    subventions_id = []
    bss.add_rule(rule)
    subventions_id.append(rule['subvention_rule_id'])
    subventions_ids_str = ','.join(subventions_id)

    @mockserver.json_handler('/subvention_view/v1/status')
    def mock_subvention_view_status(request):
        assert proxy_mode != 'no_proxy'
        _check_subvention_view_status_query(
            request, 'qwerty', 37.6, 55.75, '777', '', subventions_ids_str,
        )
        response = {'subventions_status': [{}]}
        response['subventions_status'][0]['are_restrictions_satisfied'] = True
        return response

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_tracker_categories(request):
        assert json.loads(request.get_data()) == {
            'db_id': '777',
            'uuid': '888',
            'point': [37.6, 55.75],
        }
        tracker_response = load_json('tracker_response.json')
        return tracker_response

    @mockserver.json_handler('/tracker/service/drivers-classes-bulk')
    def mock_tracker_classes(request):
        return {
            'results': [
                {
                    'driver_classes': ['econom'],
                    'payment_type_restrictions': 'none',
                    'uuid': '888',
                    'clid': '777',
                },
            ],
        }

    # Setting up bss
    for rule in rules_status:
        if rule['subvention_rule_id'] in subventions_id:
            bss.add_by_driver_subvention(rule)

    request = (
        'driver/polling/subventions_status?'
        'db=777&session=qwerty&lon={}&lat={}&subventions_id={}{}'.format(
            37.6, 55.75, subventions_ids_str, '&order_id=',
        )
    )
    response = taxi_driver_protocol.get(request)
    assert response.status_code == 200
    res = response.json()

    subv = res['subventions_status'][0]
    assert subv['are_restrictions_satisfied']

    bss.clean_rules()
    bss.clean_by_driver_subvention()
    if proxy_mode == 'no_proxy':
        assert mock_tracker_categories.times_called == 1
    else:
        assert mock_subvention_view_status.times_called == 1
