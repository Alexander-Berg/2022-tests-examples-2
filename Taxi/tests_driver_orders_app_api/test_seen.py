import pytest

import tests_driver_orders_app_api.auth_helpers as auth
import tests_driver_orders_app_api.redis_helpers as redis
import tests_driver_orders_app_api.requestconfirm_helpers as rch

BAD_POSITION_RESPONSE = {'error': {'text': 'bad_position'}}
WRONGWAY_RESPONSE = {'error': {'text': 'wrongway'}}
CONTENT_HEADER = {'Content-Type': 'application/x-www-form-urlencoded'}


def switch_remove_on_410(enable):
    return {
        'cities': [],
        'cities_disable': [],
        'countries': [],
        'countries_disable': [],
        'dbs': [],
        'dbs_disable': [],
        'enable': enable,
    }


@pytest.mark.parametrize(
    'driver_id, params, data, code, output, stq_called',
    [
        pytest.param(
            'driver_id_0',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            (
                'order=order_id_0&reason=received&timestamp=12345678912345&'
                'lat=12.3&lon=45.6'
            ),
            200,
            '',
            True,
            marks=pytest.mark.config(
                DRIVER_ORDERS_APP_API_SEND_MESSAGE_ON_SEEN=True,
            ),
        ),
        pytest.param(
            'driver_id_0',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            (
                'order=order_id_0&reason=received&timestamp=12345678912345&'
                'lat=12.3&lon=45.6'
            ),
            200,
            '',
            False,
            marks=pytest.mark.config(
                DRIVER_ORDERS_APP_API_SEND_MESSAGE_ON_SEEN=False,
            ),
        ),
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            (
                'order=order_id_0&reason=shown&timestamp=12345678912345&'
                'lat=12.3&lon=45.6'
            ),
            200,
            '',
            False,
        ),
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            (
                'order=order_id_0&reason=shown&timestamp=12345678912345&'
                'lat=12.3&lon=45.6&multioffer_id=123'
            ),
            200,
            '',
            False,
        ),
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            (
                'order=order_id_0&reason=shown&timestamp=-12345678912345&'
                'lat=12.3&lon=45.6'
            ),
            400,
            '',
            False,
        ),
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            'reason=shown&timestamp=12345678912345&lat=12.3&lon=45.6',
            400,
            '',
            False,
        ),
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            (
                'order=order_id_0&reason=shown&timestamp=12345678912345&'
                'lat=bad_double&lon=46.5'
            ),
            400,
            '',
            False,
        ),
        (
            'driver_id_0',
            {
                'session': 'test_session',
                'park_id': 'park_id_no_provider_config',
            },
            'order=order_id_0&reason=shown&timestamp=12345678912345&',
            400,
            '',
            False,
        ),
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': 'park_id_wrong_apikey'},
            'order=order_id_0&reason=shown&timestamp=12345678912345&',
            500,
            '',
            False,
        ),
        (
            'driver_not_found',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            'order=order_id_0&reason=received&timestamp=12345678912345&',
            404,
            '',
            True,
        ),
        (
            'driver_bad_position',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            (
                'order=order_id_0&reason=received&timestamp=12345678912345&'
                'lat=12.3&lon=45.6'
            ),
            410,
            BAD_POSITION_RESPONSE,
            True,
        ),
        (
            'driver_wrongway',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            'order=order_id_0&reason=received&timestamp=12345678912345&',
            410,
            WRONGWAY_RESPONSE,
            True,
        ),
        (
            'driver_gone',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            'order=order_id_0&reason=received&timestamp=12345678912345&',
            410,
            '',
            True,
        ),
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': 'park_id_no_clid'},
            'order=order_id_0&reason=shown&timestamp=12345678912345&',
            500,
            '',
            False,
        ),
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': 'park_id_no_apikey'},
            'order=order_id_0&reason=shown&timestamp=12345678912345&',
            500,
            '',
            False,
        ),
        (
            'driver_int_error',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            'order=order_id_0&reason=shown&timestamp=12345678912345&',
            500,
            '',
            False,
        ),
    ],
)
@pytest.mark.config(
    TAXIMETER_REMOVE_ORDER_ON_SEEN_410=switch_remove_on_410(False),
)
async def test_handle_responsive(
        taxi_driver_orders_app_api,
        driver_authorizer,
        mock_fleet_parks_list,
        yataxi_client,
        contractor_orders_multioffer,
        stq,
        driver_id,
        redis_store,
        params,
        data,
        code,
        output,
        stq_called,
):
    user_agent = (
        auth.USER_AGENT_TAXIMETER
        if driver_id == 'driver_id_0'
        else auth.USER_AGENT_UBER
    )
    app_family = auth.get_app_family(user_agent)

    driver_authorizer.set_client_session(
        app_family, params['park_id'], params['session'], driver_id,
    )
    redis.set_driver_for_order(
        redis_store, params['park_id'], 'order_id_0', driver_id,
    )
    response = await taxi_driver_orders_app_api.post(
        'v1/seen',
        headers={
            **CONTENT_HEADER,
            **rch.get_headers(user_agent, params['park_id'], driver_id),
        },
        data=data,
        params=params,
    )
    assert response.status_code == code
    if output:
        assert response.json() == output

    if stq_called:
        assert yataxi_client.seen_called == 1
        assert stq.send_driver_order_messages.times_called == 1

        kwargs = stq.send_driver_order_messages.next_call()['kwargs']
        kwargs.pop('log_extra')
        kwargs.pop('message', None)
        kwargs.pop('message_code', None)
        kwargs.pop('sender', None)
        assert kwargs == {
            'park_id': params['park_id'],
            'driver_id': driver_id,
            'order_id': 'order_id_0',
            'locale': 'ru',
            'success': code == 200,
        }
    else:
        assert not stq.send_driver_order_messages.times_called

    if 'multioffer_id' in data:
        assert yataxi_client.seen_called == 0
        data_dict = {
            kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')
        }
        assert contractor_orders_multioffer.seen.times_called == 1
        next_call = contractor_orders_multioffer.seen.next_call()
        request_json = next_call['self'].json
        assert request_json['reason'] == data_dict['reason']
        assert request_json['park_id'] == params['park_id']
        assert request_json['lat'] == float(data_dict['lat'])
        assert request_json['lon'] == float(data_dict['lon'])


@pytest.mark.parametrize('success', [True, False])
@pytest.mark.parametrize('driver_order_messages_code', [200, 500])
@pytest.mark.parametrize('sender_source', ['parks', 'fleet'])
async def test_send_driver_order_messages(
        stq_runner,
        driver_order_messages,
        taxi_config,
        success,
        driver_order_messages_code,
        sender_source,
):
    taxi_config.set_values(
        {'DRIVER_ORDERS_APP_API_MESSAGE_SENDER_SOURCE': sender_source},
    )
    driver_order_messages.set_code(driver_order_messages_code)
    await stq_runner.send_driver_order_messages.call(
        task_id='task-id',
        kwargs={
            'park_id': 'dummy_park',
            'driver_id': 'dummy_driver',
            'order_id': 'dummy_order',
            'locale': 'ru',
            'success': success,
        },
        expect_fail=driver_order_messages_code == 500,
    )

    assert driver_order_messages.last_request == {
        'message': (
            'Заказ доставлен водителю'
            if success
            else 'Заказ отозван. Плохая связь: нельзя получить данные'
        ),
        'order_id': 'dummy_order',
        'park_id': 'dummy_park',
        'user_name': '[birdperson] Alex Sergeevich Pushkin',
    }


@pytest.mark.parametrize(
    'driver_id,params,data,code',
    [
        (
            'driver_gone',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            'order=order_id_0&reason=shown&timestamp=12345678912345&',
            410,
        ),
    ],
)
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_SEND_DATA_TO_DRIVER_STATUS=True,
    TAXIMETER_REMOVE_ORDER_ON_SEEN_410=switch_remove_on_410(True),
)
async def test_cancel_on_gone(
        taxi_driver_orders_app_api,
        driver_authorizer,
        fleet_parks,
        driver_status,
        load_json,
        driver_id,
        redis_store,
        params,
        data,
        code,
):
    fleet_parks.parks = {'parks': [load_json('parks.json')[0]]}
    user_agent = auth.USER_AGENT_TAXIMETER
    app_family = auth.get_app_family(user_agent)
    driver_authorizer.set_client_session(
        app_family, params['park_id'], params['session'], driver_id,
    )

    redis.set_redis_for_order_cancelling(
        redis_store, params['park_id'], 'order_id_0', driver_id,
    )
    response = await taxi_driver_orders_app_api.post(
        'v1/seen',
        headers={
            **CONTENT_HEADER,
            **rch.get_headers(user_agent, params['park_id'], driver_id),
        },
        data=data,
        params=params,
    )
    assert response.status_code == code
    redis.check_redis_order_cancelled(
        redis_store, params['park_id'], 'order_id_0', driver_id,
    )
    assert fleet_parks.integration_called == 1

    handler_args = await driver_status.order_store.wait_call()
    request = handler_args['request'].json
    assert request['park_id'] == params['park_id']
    assert request['profile_id'] == driver_id
    assert request['alias_id'] == 'order_id_0'
    assert request['status'] == 'cancelled'
    assert not driver_status.order_store.has_calls
