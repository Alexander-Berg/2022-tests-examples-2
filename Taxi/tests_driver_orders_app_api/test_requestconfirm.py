import copy
import json

import pytest

import tests_driver_orders_app_api.auth_helpers as auth
import tests_driver_orders_app_api.redis_helpers as rh
import tests_driver_orders_app_api.requestconfirm_helpers as rch

CONTENT_HEADER = {'Content-Type': 'application/x-www-form-urlencoded'}


def _create_different_terminal_status_test(redis_status):
    query_status = 8 if redis_status != rh.OrderStatus.Failed else 6
    return (
        'driver_id_0',
        {'session': 'test_session', 'park_id': 'park_id_0'},
        'order=order_id_0&date=date=2020-04-14T16%3A02%3A02.0000000&'
        'status={}'.format(query_status),
        False,
        redis_status,
        0,
        406,
        False,
        '',
        None,
    )


def _create_same_terminal_status_test(redis_status):
    query_status = (
        0
        if redis_status == rh.OrderStatus.Expired
        else rch.STATUS_VALUES.get(redis_status.name.lower(), 0)
    )
    return (
        'driver_id_0',
        {'session': 'test_session', 'park_id': 'park_id_0'},
        'order=order_id_0&date=2020-04-14T16%3A02%3A02.0000000'
        '&status={}'.format(query_status),
        False,
        redis_status,
        0,
        200,
        False,
        '',
        None,
    )


@pytest.mark.parametrize(
    'driver_id,params,data,has_setcar,order_status,event_queue_size,'
    'code,locked,output,ds_status',
    [
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            'provider=2&order=order_id_0&'
            'date=2020-04-14T16%3A02%3A02.0000000&status=5',
            False,
            None,
            0,
            200,
            False,
            {'status': 5},
            'transporting',
        ),
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            'provider=2&order=order_id_0&'
            'date=2020-04-14T16%3A02%3A02.0000000&status=2',
            True,
            None,
            1,
            200,
            False,
            {'status': 2},
            'driving',
        ),
        # тест на неправильный статус
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            'provider=2&order=order_id_0&'
            'date=2020-04-14T16%3A02%3A02.0000000&status=25',
            False,
            None,
            0,
            400,
            False,
            '',
            None,
        ),
        # тест на отсутствующий парк
        (
            'driver_id_0',
            {
                'session': 'test_session',
                'park_id': 'missing_park_id_for_fleet_parks',
            },
            'provider=2&order=order_id_0&'
            'date=2020-04-14T16%3A02%3A02.0000000&status=2',
            False,
            None,
            0,
            500,
            False,
            '',
            None,
        ),
        ####
        # Дальше идут тесты на непосредственно код из view.cpp и далее
        #
        # тесты на ветку кода if (IsTerminalStatus(current_status)) {
        _create_different_terminal_status_test(rh.OrderStatus.Complete),
        _create_different_terminal_status_test(rh.OrderStatus.Cancelled),
        _create_different_terminal_status_test(rh.OrderStatus.Failed),
        _create_different_terminal_status_test(rh.OrderStatus.Expired),
        _create_same_terminal_status_test(rh.OrderStatus.Complete),
        _create_same_terminal_status_test(rh.OrderStatus.Cancelled),
        _create_same_terminal_status_test(rh.OrderStatus.Failed),
        # Проверяем ветку -- Подправляем статус
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            'order=order_id_0&date=2020-04-14T16%3A02%3A02.0000000&'
            'status=8&comment=Клиент%20не%20вышел',
            False,
            rh.OrderStatus.Cancelled,
            0,
            200,
            False,
            '',
            None,
        ),
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            'order=order_id_0&date=2020-04-14T16%3A02%3A02.0000000&'
            'status=8&comment=Клиент%20не%20вышел',
            False,
            rh.OrderStatus.Failed,
            0,
            406,
            False,
            '',
            None,
        ),
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            'order=order_id_0&date=2020-04-14T16%3A02%3A02.0000000&'
            'status=8&comment=Клиент%20не%20вышел&failed=true',
            False,
            rh.OrderStatus.Failed,
            0,
            200,
            False,
            '',
            None,
        ),
        # тест на то, что в редисе лок уже взят
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            'order=order_id_0&date=2020-04-14T16%3A02%3A02.0000000&'
            'status=2',
            False,
            None,
            0,
            429,
            True,
            '',
            None,
        ),
    ],
)
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_SEND_DATA_TO_DRIVER_STATUS=True,
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
)
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
@pytest.mark.parametrize(
    'api_schema', ['compatible', 'requestconfirm_status_v2'],
)
async def test_handle_request_confirm_responsive(
        taxi_driver_orders_app_api,
        driver_authorizer,
        fleet_parks,
        yataxi_client,
        driver_status,
        driver_trackstory,
        fleet_parks_shard,
        taximeter_xservice,
        pgsql,
        load_json,
        redis_store,
        driver_id,
        params,
        data,
        has_setcar,
        order_status,
        event_queue_size,
        code,
        locked,
        output,
        ds_status,
        mocked_time,
        api_schema,
):
    def check_date(setcar, date_field):
        assert date_field in setcar
        assert setcar['date_last_change'] == mocked_time.now().strftime(
            rch.TAXIMETER_DATE_FORMAT,
        )

    user_agent = (
        auth.USER_AGENT_TAXIMETER
        if driver_id == 'driver_id_0'
        else auth.USER_AGENT_UBER
    )
    park_id = params['park_id']
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}
    order_id = data_dict['order']
    status = data_dict.get('status')
    app_family = auth.get_app_family(user_agent)
    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = user_agent

    if locked:
        rh.set_redis_lock(redis_store, park_id, order_id)
    rh.set_order_status(redis_store, park_id, order_id, order_status)

    if params['park_id'] == 'park_id_0':
        fleet_parks.parks = {'parks': [load_json('parks.json')[0]]}

    if has_setcar:
        setcar = load_json('full_setcar.json')
        setcar['id'] = order_id
        rh.set_redis_for_order_cancelling(
            redis_store, park_id, order_id, driver_id, setcar_item=setcar,
        )

    url = rch.get_requestconfirm_url(api_schema, status)
    if not url:
        return
    headers = rch.get_headers(auth.USER_AGENT_TAXIMETER, park_id, driver_id)
    data = rch.process_data(api_schema, data_dict, data)
    response = await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type(api_schema), **headers},
        data=data,
        params=params,
    )

    assert response.status_code == code

    assert rh.get_event_queue_size(redis_store) == event_queue_size
    if not locked:
        assert rh.redis_lock_not_exists(redis_store, park_id, order_id)

    if output:
        output_copy = copy.deepcopy(output)
        output_copy.update(rch.HAS_SETCAR_DATA)
        assert response.json() == output_copy
    if has_setcar:
        setcar = json.loads(rh.get_setcar_item(redis_store, park_id, order_id))
        check_date(setcar, 'date_last_change')
        check_date(setcar, 'date_create')
        assert 'phone_options' in response.json()

    if ds_status:
        handler_args = await driver_status.order_store.wait_call()
        request = handler_args['request'].json
        assert request['park_id'] == park_id
        assert request['profile_id'] == driver_id
        assert request['alias_id'] == order_id
        assert request['status'] == ds_status
    assert not driver_status.order_store.has_calls
