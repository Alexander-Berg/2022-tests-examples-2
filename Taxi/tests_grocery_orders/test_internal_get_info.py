import pytest

from . import consts
from . import headers
from . import models


HEADERS = {
    'X-YaTaxi-Pass-Flags': '',
    'X-YaTaxi-User': 'eats_user_id=test_eats_user_id',
    'X-YaTaxi-Session': 'test_domain:test_session',
    'X-YaTaxi-Bound-Sessions': 'old_test_domain:old_test_session',
}


async def test_basic(taxi_grocery_orders, pgsql, grocery_depots):
    dispatch_id = 'test_dispatch_id'
    billing_settings_version = 'settings-version'
    grocery_flow_version = 'grocery_flow_v3'

    order = models.Order(
        pgsql=pgsql,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=dispatch_id,
            dispatch_status='revoked',
            dispatch_cargo_status='delivered',
        ),
        finish_started=consts.NOW,
        billing_settings_version=billing_settings_version,
        grocery_flow_version=grocery_flow_version,
        personal_email_id='personal_email_id',
        entrance='7',
        vip_type='ultima',
        timeslot_request_kind='wide_slot',
        comment='comment',
    )

    tin = 'tin-for-depot'
    grocery_depots.add_depot(legacy_depot_id=order.depot_id, tin=tin)

    response = await taxi_grocery_orders.post(
        '/internal/v1/get-info',
        headers=HEADERS,
        json={'order_id': order.order_id},
    )

    country = models.Country.Russia
    assert response.status_code == 200
    assert response.json() == {
        'cart_id': order.cart_id,
        'cart_version': order.cart_version,
        'created': order.created.isoformat(),
        'due': order.due.isoformat(),
        'idempotency_token': order.idempotency_token,
        'offer_id': order.offer_id,
        'order_id': order.order_id,
        'order_version': order.order_version,
        'status': order.status,
        'country_iso2': country.country_iso2,
        'country_iso3': country.country_iso3,
        'locale': 'RU',
        'country': country.name,
        'location': [10.0, 20.0],
        'dispatch_id': dispatch_id,
        'region_id': 213,
        'depot_id': order.depot_id,
        'depot': {'id': order.depot_id, 'tin': tin, 'city': order.city},
        'yandex_uid': '12345678',
        'finish_started': order.finish_started,
        'user_info': {
            'taxi_user_id': order.taxi_user_id,
            'eats_user_id': order.eats_user_id,
            'phone_id': order.phone_id,
            'personal_phone_id': order.personal_phone_id,
            'personal_email_id': order.personal_email_id,
            'yandex_uid': order.yandex_uid,
            'appmetrica_device_id': order.appmetrica_device_id,
            'app_vars': order.app_info,
            'user_ip': order.user_ip,
        },
        'billing_flow': 'grocery_payments',
        'billing_settings_version': billing_settings_version,
        'grocery_flow_version': grocery_flow_version,
        'app_info': headers.APP_INFO,
        'dispatch_status_info': {
            'cargo_status': 'delivered',
            'dispatch_id': 'test_dispatch_id',
            'performer_info': {},
            'status': 'revoked',
        },
        'short_order_id': order.short_order_id,
        'city_label': 'Москва',
        'leave_at_door': order.left_at_door,
        'city': order.city,
        'street': order.street,
        'house': order.house,
        'entrance': order.entrance,
        'flat': order.flat,
        'vip_type': order.vip_type,
        'timeslot_request_kind': order.timeslot_request_kind,
        'comment': order.comment,
        'grocery_order_status': 'created',
    }


@pytest.mark.parametrize(
    'delivery_type, expected_result',
    [('rover', 'rover'), ('random_text', 'other'), (None, 'other')],
)
@pytest.mark.parametrize(
    'personal_tin_id,'
    'organization_name,'
    'vat,'
    'balance_client_id,'
    'eats_courier_id,'
    'billing_type',
    [
        (
            '1234',
            'OOO Testing',
            '18',
            'balance_client_id-123',
            'eats_courier_id-123',
            'courier_service',
        ),
        (None, None, None, None, None, None),
    ],
)
async def test_get_courier_info(
        taxi_grocery_orders,
        pgsql,
        grocery_depots,
        delivery_type,
        expected_result,
        personal_tin_id,
        organization_name,
        vat,
        balance_client_id,
        eats_courier_id,
        billing_type,
):
    order = models.Order(
        pgsql=pgsql,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=consts.DEFAULT_DISPATCH_ID,
            dispatch_status='revoked',
            dispatch_cargo_status='delivered',
            dispatch_transport_type=delivery_type,
        ),
        dispatch_performer=models.DispatchPerformer(
            driver_id='test-driver-id',
            personal_tin_id=personal_tin_id,
            organization_name=organization_name,
            vat=vat,
            balance_client_id=balance_client_id,
            eats_courier_id=eats_courier_id,
            billing_type=billing_type,
        ),
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/internal/v1/get-info',
        headers=HEADERS,
        json={'order_id': order.order_id},
    )

    assert response.status_code == 200
    courier_info = response.json()['courier_info']
    _check_courier_info(
        courier_info,
        id=order.dispatch_performer.driver_id,
        transport_type=expected_result,
        personal_tin_id=personal_tin_id,
        organization_name=organization_name,
        vat=vat,
        balance_client_id=balance_client_id,
        eats_courier_id=eats_courier_id,
        billing_type=billing_type,
    )


@pytest.mark.config(GROCERY_ORDERS_USE_COLD_STORAGE=True)
async def test_cold_storage(
        taxi_grocery_orders,
        pgsql,
        grocery_depots,
        grocery_cold_storage,
        load_json,
):
    order_id = '9dc2300a4d004a9e9d854a9f5e45816a-grocery'
    depot_id = '60287'

    grocery_depots.add_depot(legacy_depot_id=depot_id, tin='tin')

    cold_storage_request = load_json('cold_storage_request.json')
    grocery_cold_storage.set_orders_response(
        items=load_json('cold_storage_response.json')['items'],
    )
    grocery_cold_storage.check_orders_request(
        item_ids=cold_storage_request['item_ids'],
        fields=cold_storage_request['fields'],
    )

    driver_id = 'driver_id'
    eats_courier_id = 'eats_courier_id'
    organization_name = 'organization_name'
    personal_tin_id = 'personal_tin_id'
    vat = 'vat'
    balance_client_id = 'balance_client_id'
    billing_type = 'self_employed'

    performer_info = models.DispatchPerformer(
        driver_id=driver_id,
        eats_courier_id=eats_courier_id,
        courier_full_name='courier_full_name',
        first_name='first_name',
        organization_name=organization_name,
        legal_address='legal_address',
        ogrn='ogrn',
        work_schedule='work_schedule',
        personal_tin_id=personal_tin_id,
        vat=vat,
        balance_client_id=balance_client_id,
        billing_type=billing_type,
        car_number='car_number',
        car_model='car_model',
        car_color='car_color',
        car_color_hex='car_color_hex',
    )
    models.update_dispatch_performer(pgsql, order_id, performer_info)

    response = await taxi_grocery_orders.post(
        '/internal/v1/get-info', headers=HEADERS, json={'order_id': order_id},
    )

    assert response.status_code == 200
    assert grocery_cold_storage.orders_times_called() == 1

    body = response.json()

    assert body['courier_info'] == {
        'balance_client_id': balance_client_id,
        'billing_type': billing_type,
        'eats_courier_id': eats_courier_id,
        'id': driver_id,
        'organization_name': organization_name,
        'personal_tin_id': personal_tin_id,
        'transport_type': 'pedestrian',
        'vat': vat,
    }


def _check_courier_info(courier_info, **kwargs):
    for key, value in kwargs.items():
        if value is not None:
            assert courier_info[key] == value, key
        else:
            assert key not in courier_info


@pytest.mark.config(GROCERY_ORDERS_USE_COLD_STORAGE=True)
async def test_cold_storage_null_in_response(
        taxi_grocery_orders,
        pgsql,
        grocery_depots,
        grocery_cold_storage,
        load_json,
):
    order_id = '9dc2300a4d004a9e9d854a9f5e45816a-grocery'
    depot_id = '60287'

    grocery_depots.add_depot(legacy_depot_id=depot_id, tin='tin')

    cold_storage_request = load_json('cold_storage_request.json')
    cold_storage_response = load_json('cold_storage_response.json')['items']

    cold_storage_response[0]['additional_table'][0][
        'appmetrica_device_id'
    ] = None

    grocery_cold_storage.set_orders_response(items=cold_storage_response)
    grocery_cold_storage.check_orders_request(
        item_ids=cold_storage_request['item_ids'],
        fields=cold_storage_request['fields'],
    )

    response = await taxi_grocery_orders.post(
        '/internal/v1/get-info', headers=HEADERS, json={'order_id': order_id},
    )

    assert response.status_code == 200
    assert 'appmetrica_device_id' not in response.json()['user_info']

    assert grocery_cold_storage.orders_times_called() == 1


@pytest.mark.parametrize(
    'cancel_reason_type, expect_cancel_reason_type',
    [
        ('timeout', 'timeout'),
        ('failure', 'failure'),
        ('user_request', 'user_request'),
        ('payment_failed', 'payment_failed'),
        ('admin_request', 'admin_request'),
        ('payment_timeout', 'payment_timeout'),
        ('fraud', 'fraud'),
        ('invalid_payment_method', 'invalid_payment_method'),
        ('dispatch_failure', 'dispatch_failure'),
    ],
)
async def test_get_cancel_reason(
        taxi_grocery_orders,
        pgsql,
        grocery_depots,
        cancel_reason_type,
        expect_cancel_reason_type,
):
    cancel_reason_message = 'some reason message'
    order = models.Order(
        pgsql=pgsql,
        cancel_reason_type=cancel_reason_type,
        cancel_reason_message=cancel_reason_message,
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/internal/v1/get-info',
        headers=HEADERS,
        json={'order_id': order.order_id},
    )

    assert response.status_code == 200
    assert expect_cancel_reason_type == response.json()['cancel_reason_type']
    assert cancel_reason_message == response.json()['cancel_reason_message']
