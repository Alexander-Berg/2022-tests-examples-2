import copy
import datetime
from fcntl import F_SETFL
import json
import uuid

import pytest

import tests_driver_orders_app_api.auth_helpers as auth
import tests_driver_orders_app_api.redis_helpers as rh
import tests_driver_orders_app_api.requestconfirm_helpers as rch

SMS_TEMPLATE = 'sms_template'

VOICE_TEMPLATE = 'voice_template'

REJECT_EVENT_TYPE, DEFAULT_EVENT_TYPE = 33, 38
SOME_DATE = '2019-05-01T16:18:00.000000Z'
DEFAULT_PARK_ID = 'park_id_0'


def _get_event_type(comment):
    return REJECT_EVENT_TYPE if comment == 'reject' else DEFAULT_EVENT_TYPE


@pytest.mark.parametrize(
    'driver_id,params,data,order_status,event_queue_size,code,output',
    [
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': DEFAULT_PARK_ID},
            'order=order_id_0&status=9&'
            'statusDistance=20.20&is_offline=false&is_captcha=true&'
            'is_fallback=false&is_airplanemode=true&'
            'driver_status=rejected',
            rh.OrderStatus.Transporting,
            1,
            200,
            {'status': 9},
        ),
        (
            'driver_with_skip_autocancel_id_0',
            {'session': 'test_session', 'park_id': DEFAULT_PARK_ID},
            'order=order_id_0&status=9&'
            'statusDistance=20.20&is_offline=false&is_captcha=true&'
            'is_fallback=false&is_airplanemode=true&'
            'driver_status=rejected',
            rh.OrderStatus.Transporting,
            1,
            200,
            {'status': 9},
        ),
    ],
)
@pytest.mark.parametrize('actual_provider', [1, 2])
@pytest.mark.parametrize('provider_source', [None, 'request', 'sql', 'both'])
@pytest.mark.parametrize('status_in_sql', [None])
@pytest.mark.parametrize('has_setcar', [True, False])
@pytest.mark.parametrize('with_push', [True, False])
@pytest.mark.parametrize(
    'comment', ['reject', 'autocancel', 'autocancel_with_chain'],
)
@pytest.mark.parametrize('comment_id', [None, 'REASON1'])
@pytest.mark.parametrize('api_schema', ['requestconfirm_status_v2'])
@pytest.mark.experiments3(filename='exp3_skip_chain_autocancel_event.json')
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_SKIP_YANDEX_ORDERS_FOR_XCALC=True,
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
    DRIVER_ORDERS_APP_API_SKIP_CHAIN_EVENT_SETTINGS=100,
)
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
async def test_handle_requestconfirm_reject(
        taxi_driver_orders_app_api,
        driver_authorizer,
        fleet_parks,
        load_json,
        taximeter_xservice,
        yataxi_client,
        driver_orders,
        fleet_parks_shard,
        redis_store,
        mocked_time,
        stq,
        actual_provider,
        provider_source,
        status_in_sql,
        has_setcar,
        with_push,
        comment,
        comment_id,
        api_schema,
        driver_id,
        params,
        data,
        order_status,
        event_queue_size,
        code,
        output,
        contractor_order_history,
):
    original_comment = comment
    comment = comment.split('_')[0]
    user_agent = (
        auth.USER_AGENT_TAXIMETER
        if driver_id in ('driver_id_0', 'driver_with_skip_autocancel_id_0')
        else auth.USER_AGENT_UBER
    )

    provider = (
        actual_provider if provider_source in ['request', 'both'] else None
    )
    if provider and api_schema != 'compatible':
        data += '&provider={}'.format(provider)
    if api_schema == 'compatible':
        if comment_id:
            data += '&comment={}'.format(comment_id)
        data += '&reason={}'.format(comment)
    elif api_schema == 'requestconfirm_status_v2':
        if comment_id:
            data += '&reject_comment={}'.format(comment_id)
        data += '&comment={}'.format(comment)

    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}
    park_id = params['park_id']
    order_id = data_dict['order']
    status = data_dict.get('status')
    app_family = auth.get_app_family(user_agent)
    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = user_agent

    with_push = False
    taximeter_xservice.set_response({'code': 200})
    rh.set_order_status(redis_store, park_id, order_id, order_status)
    if has_setcar:
        setcar_item = load_json('full_setcar.json')
        setcar_item['provider'] = actual_provider
        if original_comment == 'autocancel_with_chain':
            setcar_item['chain'] = {
                'destination': [39.207141, 51.662082],
                'left_time': 99,
                'left_dist': 500,
                'order_id': 'f3ae2a04966035119c3ea83c8d0197ae',
            }
        rh.set_redis_for_order_cancelling(
            redis_store, park_id, order_id, driver_id, setcar_item=setcar_item,
        )
    if params['park_id'] == 'park_id_0':
        fleet_parks.parks = {'parks': [load_json('parks.json')[0]]}
    params['with_push'] = with_push

    if provider_source in ['sql', 'both'] or status_in_sql:
        driver_orders.park_id = park_id
        driver_orders.order_id = order_id
        driver_orders.driver_id = driver_id
        driver_orders.provider = actual_provider
        driver_orders.status = status_in_sql

    yataxi_client.comment_id = comment_id
    yataxi_client.status_distance = float(data_dict.get('statusDistance'))

    url = rch.get_reject_url(api_schema, status)
    headers = rch.get_headers(user_agent, park_id, driver_id)
    data = rch.process_data(api_schema, data_dict, data)
    response = await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type(api_schema), **headers},
        data=data,
        params=params,
    )

    push_queue_size = int(with_push)

    assert response.status_code == code

    if original_comment == 'autocancel_with_chain' and has_setcar:
        event_queue_size = 0
    if driver_id == 'driver_with_skip_autocancel_id_0':
        assert rh.get_event_queue_size(redis_store) == event_queue_size
    if event_queue_size > 0:
        item = json.loads(
            rh.get_event_queue_items(redis_store)[0].decode('UTF-8'),
        )
        assert item['EventType'] == _get_event_type(comment)
        assert item['ServerTime'] == (
            mocked_time.now() + datetime.timedelta(hours=3)
        ).strftime(rch.TAXIMETER_DATE_FORMAT)
    assert rh.get_push_queue_size(redis_store) == push_queue_size
    assert rh.redis_lock_not_exists(redis_store, park_id, order_id)
    await contractor_order_history.update.wait_call()

    expected_message_count = int(comment == 'autocancel')
    assert (
        stq.send_driver_order_messages.times_called == expected_message_count
    )
    if expected_message_count:
        data = stq.send_driver_order_messages.next_call()
        kwargs = data['kwargs']
        kwargs.pop('log_extra')
        assert kwargs == {
            'message_code': 'Order_Message_Reject_Autocancel',
            'park_id': park_id,
            'driver_id': driver_id,
            'order_id': order_id,
            'locale': 'ru',
            'success': False,
        }

    assert stq.driver_orders_xservice_calcservice.times_called == int(
        actual_provider == 1 or (provider_source is None and not has_setcar),
    )

    if stq.driver_orders_xservice_calcservice.has_calls:
        kwargs = stq.driver_orders_xservice_calcservice.next_call()['kwargs']
        kwargs.pop('log_extra')
        assert kwargs == {
            'operation_type': 'remove',
            'park_id': park_id,
            'driver_id': driver_id,
            'order_id': order_id,
            'cost_total': 0.0,
            'sum': 0.0,
            'user': '',
        }

    if output:
        output_copy = copy.deepcopy(output)
        if actual_provider == 2:
            if has_setcar:
                output_copy.update(rch.HAS_SETCAR_DATA)
            if provider_source in ['sql', 'both']:
                output_copy.update(rch.HAS_SETCAR_DATA)
            if (
                    provider_source in ['request', 'both']
                    and api_schema != 'compatible'
            ):
                output_copy.update(rch.HAS_SETCAR_DATA)
        assert response.json() == output_copy, (
            'actual_provider={}, provider_source={}, '
            'has_setcar={}, api_schema={}'.format(
                actual_provider, provider_source, has_setcar, api_schema,
            )
        )


@pytest.mark.park_order
@pytest.mark.parametrize(
    'driver_id,params,data,order_status,event_queue_size,code,output',
    [
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': DEFAULT_PARK_ID},
            'order=order_id_0&status=9&'
            'statusDistance=20.20&is_offline=false&is_captcha=true&'
            'is_fallback=false&is_airplanemode=true&'
            'driver_status= &provider=1',
            rh.OrderStatus.Transporting,
            1,
            200,
            {'status': 9},
        ),
    ],
)
@pytest.mark.parametrize('api_schema', ['requestconfirm_status_v2'])
@pytest.mark.parametrize('setcar_has_phones', [True, False])
@pytest.mark.parametrize('setcar_sms_enabled', [True, False])
@pytest.mark.parametrize('park_has_sms', [True, False])
@pytest.mark.parametrize('park_has_voice', [True, False])
@pytest.mark.parametrize(
    'company_emails', [None, 'email@email.ru,mailto@mailto.com'],
)
@pytest.mark.parametrize('company_enabled', [True, False])
@pytest.mark.parametrize('company_disable_sms', [True, False])
@pytest.mark.parametrize('company_template', ['company_template'])
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
)
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
async def test_handle_requestconfirm_reject_park(
        taxi_driver_orders_app_api,
        driver_authorizer,
        driver_orders,
        fleet_parks,
        yataxi_client,
        load_json,
        taximeter_xservice,
        fleet_parks_shard,
        redis_store,
        pgsql,
        mocked_time,
        stq,
        api_schema,
        driver_id,
        params,
        data,
        order_status,
        event_queue_size,
        code,
        output,
        setcar_has_phones,
        setcar_sms_enabled,
        park_has_sms,
        park_has_voice,
        company_disable_sms,
        company_enabled,
        company_emails,
        company_template,
        contractor_order_history,
):
    user_agent = (
        auth.USER_AGENT_TAXIMETER
        if driver_id == 'driver_id_0'
        else auth.USER_AGENT_UBER
    )

    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}
    park_id = params['park_id']
    order_id = data_dict['order']
    status = data_dict.get('status')
    app_family = auth.get_app_family(user_agent)
    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = user_agent

    fleet_parks.communications = {
        'park_id': park_id,
        'sms': {
            'login': 'login',
            'password': 'password',
            'provider': 'provider',
        },
        'voip': {
            'ice_servers': 'ice_servers',
            'provider': 'provider',
            'show_number': False,
        },
    }

    setcar_item = load_json('full_setcar.json')
    setcar_item['provider'] = 1
    setcar_item['sms'] = setcar_sms_enabled
    if setcar_has_phones:
        setcar_item['phones'] = {
            'Driver': '+7010-000-0000',
            'Dispatch': '+7020-000-0000',
            'None': '+7030-000-0000',
        }

    company_id = str(uuid.uuid4())
    if park_has_voice:
        rh.set_park_voice(redis_store, park_id, 'DriverCancel', VOICE_TEMPLATE)
    if park_has_sms:
        rh.set_park_text(redis_store, park_id, 'DriverCancel', SMS_TEMPLATE)
    if company_disable_sms:
        rh.set_company_disable_sms(redis_store, park_id, company_id)
    if company_emails or company_enabled:
        rh.set_company_template(
            redis_store,
            park_id,
            company_id,
            'DriverCancel',
            company_emails,
            company_enabled,
            company_template,
        )
    setcar_item['company_id'] = company_id

    fleet_parks.parks = {'parks': [load_json('parks.json')[0]]}
    taximeter_xservice.set_response({'code': 200})
    rh.set_order_status(redis_store, park_id, order_id, order_status)
    rh.set_redis_for_order_cancelling(
        redis_store, park_id, order_id, driver_id, setcar_item=setcar_item,
    )

    driver_orders.park_id = park_id
    driver_orders.order_id = order_id
    driver_orders.provider = 1
    driver_orders.status = 40
    driver_orders.driver_id = driver_id

    if api_schema == 'external_cancel_v1':
        rh.create_apikey(redis_store, 'apikey', park_id)
        params['apikey'] = 'apikey'
        params['id'] = order_id
        params['comment'] = 'some_comment'

    url = rch.get_reject_url(api_schema, status)
    headers = rch.get_headers(user_agent, park_id, driver_id)
    data = rch.process_data(api_schema, data_dict, data)
    func = (
        taxi_driver_orders_app_api.post
        if api_schema != 'external_cancel_v1'
        else taxi_driver_orders_app_api.get
    )
    response = await func(
        url,
        headers={**rch.get_content_type(api_schema), **headers},
        data=data,
        params=params,
    )

    assert response.status_code == code

    assert rh.get_event_queue_size(redis_store) == event_queue_size
    item = json.loads(rh.get_event_queue_items(redis_store)[0].decode('UTF-8'))
    assert item['ServerTime'] == (
        mocked_time.now() + datetime.timedelta(hours=3)
    ).strftime(rch.TAXIMETER_DATE_FORMAT)
    assert rh.redis_lock_not_exists(redis_store, park_id, order_id)
    await contractor_order_history.update.wait_call()
    assert stq.driver_orders_xservice_calcservice.times_called == 1

    if (
            setcar_sms_enabled
            and (park_has_voice or park_has_sms)
            and (not company_disable_sms)
    ):
        assert stq.send_park_driver_sms_voice_message.times_called == 1
        stq_item = stq.send_park_driver_sms_voice_message.next_call()
        kwargs = stq_item['kwargs']
        expected_kwargs = {
            'park_id': park_id,
            'driver_id': driver_id,
            'order_id': order_id,
            'notification': 8,  # kDriverCancel
        }
        for kwarg, value in expected_kwargs.items():
            assert kwargs.get(kwarg) == value

        if park_has_sms:
            tmpl = company_template if company_enabled else SMS_TEMPLATE
            assert kwargs['template_sms'] == tmpl
        if park_has_voice:
            tmpl = company_template if company_enabled else VOICE_TEMPLATE
            assert kwargs['template_voice'] == tmpl
        if company_enabled and company_emails:
            assert 'company_emails' in kwargs, (
                'company_id={}, company_enabled={}, company_emails={}'.format(
                    company_id, company_enabled, company_emails,
                )
            )
            assert kwargs['company_emails'] == company_emails, (
                'company_id={}, company_enabled={}, company_emails={}'.format(
                    company_id, company_enabled, company_emails,
                )
            )
        else:
            assert 'company_emails' not in kwargs, (
                'company_id={}, company_enabled={}, company_emails={}'.format(
                    company_id, company_enabled, company_emails,
                )
            )
        if setcar_has_phones:
            assert kwargs['phone1'] == '+7010-000-0000'
            assert kwargs['phone2'] == '+7020-000-0000'
            assert kwargs['phone3'] == '+7030-000-0000'
        else:
            assert 'phone1' not in kwargs
            assert 'phone2' not in kwargs
            assert 'phone3' not in kwargs
