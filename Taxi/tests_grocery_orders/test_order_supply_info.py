import copy

import pytest

from . import headers
from . import models


def _get_valid_order(pgsql):
    order = models.Order(
        pgsql,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='dispatch_id',
            dispatch_status='revoked',
            dispatch_cargo_status='delivered',
            dispatch_transport_type='performer_transport_type',
            dispatch_car_number='performer_car_number',
        ),
        dispatch_performer=models.DispatchPerformer(
            driver_id='performer_driver_id',
            eats_courier_id='performer_eats_courier_id',
            courier_full_name='performer_courier_full_name',
            first_name='performer_name',
            organization_name='performer_organization_name',
            legal_address='performer_legal_address',
            ogrn='performer_ogrn',
            work_schedule='performer_work_schedule',
            personal_tin_id='performer_tin',
            vat='performer_vat',
            balance_client_id='performer_balance_client_id',
            car_number='performer_car_number',
        ),
    )
    return order


def _get_expected_tracking_info(dispatch_performer, country_iso3='RUS'):
    result = ''
    has_organisation_info = False
    if country_iso3 == 'FRA':
        if dispatch_performer.organization_name is not None:
            result += dispatch_performer.organization_name
            has_organisation_info = True
    elif country_iso3 == 'RUS':
        if dispatch_performer.organization_name is not None:
            result += dispatch_performer.organization_name
            has_organisation_info = True
            if dispatch_performer.legal_address is not None:
                result += ', ' + dispatch_performer.legal_address
            if dispatch_performer.ogrn is not None:
                result += ', ОГРН ' + dispatch_performer.ogrn

    if dispatch_performer.courier_full_name is not None:
        if has_organisation_info:
            result += ', '
        result += dispatch_performer.courier_full_name
    elif not has_organisation_info:
        return None
    return result + '.'


@pytest.mark.translations(grocery_orders={'delivery_ogrn': {'ru': 'ОГРН'}})
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_supply,
        grocery_cart,
        grocery_depots,
):
    order = _get_valid_order(pgsql)
    grocery_cart.set_depot_id(depot_id=order.depot_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/supply-info',
        headers=headers.DEFAULT_HEADERS,
        json={'order_id': order.order_id},
    )

    assert response.status_code == 200
    assert response.json() == {
        'driver_id': 'performer_driver_id',
        'eats_courier_id': 'performer_eats_courier_id',
        'courier_full_name': 'performer_courier_full_name',
        'courier_name': 'performer_name',
        'organization_name': 'performer_organization_name',
        'legal_address': 'performer_legal_address',
        'ogrn': 'performer_ogrn',
        'work_schedule': 'performer_work_schedule',
        'tin': 'performer_tin',
        'vat': 'performer_vat',
        'transport_type': 'performer_transport_type',
        'tracking_info': _get_expected_tracking_info(order.dispatch_performer),
    }


async def test_not_found_disptach_status_info(taxi_grocery_orders, pgsql):
    order = models.Order(pgsql)
    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/supply-info',
        headers=headers.DEFAULT_HEADERS,
        json={'order_id': order.order_id},
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    'order_uid, user_uid, order_session, user_session, expected_code',
    [
        (
            'matching-uid',
            'matching-uid',
            'matching-session',
            'matching-session',
            200,
        ),
        (
            'matching-uid',
            'matching-uid',
            'non_matching-session-A',
            'non_matching-session-B',
            200,
        ),
        (
            'non_matching-A',
            'non_matching-B',
            'matching-session',
            'matching-session',
            200,
        ),
        (
            'non_matching-A',
            'non_matching-B',
            'non_matching-session-A',
            'non_matching-session-B',
            404,
        ),
        (None, 'any-uid', 'matching-session', 'matching-session', 200),
        (
            None,
            'any-uid',
            'non_matching-session-A',
            'non_matching-session-B',
            404,
        ),
        ('any-uid', None, 'matching-session', 'matching-session', 200),
        (
            'any-uid',
            None,
            'non_matching-session-A',
            'non_matching-session-B',
            404,
        ),
    ],
)
async def test_user_access_with_uid(
        taxi_grocery_orders,
        pgsql,
        order_uid,
        user_uid,
        order_session,
        user_session,
        expected_code,
):
    order = _get_valid_order(pgsql)
    order.yandex_uid = order_uid
    order.session = order_session
    order.upsert()

    modified_headers = copy.deepcopy(headers.DEFAULT_HEADERS)
    modified_headers['X-Yandex-UID'] = user_uid
    modified_headers['X-YaTaxi-Session'] = user_session

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/supply-info',
        headers=modified_headers,
        json={'order_id': order.order_id},
    )

    assert response.status_code == expected_code


@pytest.mark.translations(grocery_orders={'delivery_ogrn': {'ru': 'ОГРН'}})
@pytest.mark.parametrize(
    'old_tin, new_personal_tin, expected_tin',
    [
        ('old_tin_id', None, 'old_tin_id'),
        ('old_tin_id', 'new_tin_id', 'new_tin_id'),
        (None, 'new_tin_id', 'new_tin_id'),
        (None, None, None),
    ],
)
async def test_migration_71_using_personal_tin_id_instead_tin(
        taxi_grocery_orders,
        pgsql,
        old_tin,
        new_personal_tin,
        expected_tin,
        grocery_cart,
        grocery_depots,
):
    dispatch_performer = models.DispatchPerformer(
        driver_id='performer_driver_id',
        eats_courier_id='performer_eats_courier_id',
        courier_full_name='performer_courier_full_name',
        organization_name='performer_organization_name',
        legal_address='performer_legal_address',
        ogrn='performer_ogrn',
        work_schedule='performer_work_schedule',
        vat='performer_vat',
        balance_client_id='performer_balance_client_id',
        car_number='performer_car_number',
        car_model='performer_car_model',
        car_color='performer_car_color',
        car_color_hex='performer_car_color_hex',
    )
    order = models.Order(
        pgsql,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='dispatch_id',
            dispatch_status='revoked',
            dispatch_cargo_status='delivered',
            dispatch_transport_type='performer_transport_type',
        ),
        dispatch_performer=dispatch_performer,
    )
    grocery_cart.set_depot_id(depot_id=order.depot_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    order.pg_db.cursor().execute(
        models.UPSERT_PERFORMER_SQL,
        [
            order.order_id,
            dispatch_performer.driver_id,
            dispatch_performer.eats_courier_id,
            dispatch_performer.courier_full_name,
            dispatch_performer.first_name,
            dispatch_performer.organization_name,
            dispatch_performer.legal_address,
            dispatch_performer.ogrn,
            dispatch_performer.work_schedule,
            new_personal_tin,
            old_tin,
            dispatch_performer.vat,
            dispatch_performer.balance_client_id,
            dispatch_performer.billing_type,
            dispatch_performer.car_number,
            dispatch_performer.car_model,
            dispatch_performer.car_color,
            dispatch_performer.car_color_hex,
            order.created,
        ],
    )

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/supply-info',
        headers=headers.DEFAULT_HEADERS,
        json={'order_id': order.order_id},
    )

    if expected_tin is not None:
        tin_response = {'tin': expected_tin}
    else:
        tin_response = {}

    assert response.status_code == 200
    assert response.json() == {
        'driver_id': 'performer_driver_id',
        'eats_courier_id': 'performer_eats_courier_id',
        'courier_full_name': 'performer_courier_full_name',
        'organization_name': 'performer_organization_name',
        'legal_address': 'performer_legal_address',
        'ogrn': 'performer_ogrn',
        'work_schedule': 'performer_work_schedule',
        'vat': 'performer_vat',
        'transport_type': 'performer_transport_type',
        'tracking_info': _get_expected_tracking_info(order.dispatch_performer),
        **tin_response,
    }


@pytest.mark.translations(grocery_orders={'delivery_ogrn': {'ru': 'ОГРН'}})
@pytest.mark.parametrize(
    'courier_full_name,organization_name,legal_address,' 'ogrn, country_iso3',
    [
        ('Ivan Ivanovich', 'OOO Romashka', 'Moscow city', '123456', 'RUS'),
        ('Ivan Ivanovich', 'OOO Romashka', 'Moscow city', '123456', 'FRA'),
        ('Ivan Ivanovich', 'OOO Romashka', 'Moscow city', '123456', 'ISR'),
        ('Ivan Ivanovich', 'OOO Romashka', None, '123456', 'RUS'),
        ('Ivan Ivanovich', None, None, None, 'RUS'),
        (None, None, None, None, 'RUS'),
    ],
)
async def test_tracking_legal_info(
        pgsql,
        taxi_grocery_orders,
        courier_full_name,
        organization_name,
        legal_address,
        ogrn,
        country_iso3,
        grocery_depots,
        grocery_cart,
):
    dispatch_performer = models.DispatchPerformer(
        driver_id='performer_driver_id',
        eats_courier_id='performer_eats_courier_id',
        courier_full_name=courier_full_name,
        organization_name=organization_name,
        legal_address=legal_address,
        ogrn=ogrn,
        vat='performer_vat',
        balance_client_id='performer_balance_client_id',
    )
    order = models.Order(
        pgsql,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='dispatch_id',
            dispatch_status='revoked',
            dispatch_cargo_status='delivered',
            dispatch_transport_type='performer_transport_type',
        ),
        dispatch_performer=dispatch_performer,
    )
    grocery_cart.set_depot_id(depot_id=order.depot_id)
    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, country_iso3=country_iso3,
    )

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/supply-info',
        headers=headers.DEFAULT_HEADERS,
        json={'order_id': order.order_id},
    )
    expected_tracking_info = _get_expected_tracking_info(
        dispatch_performer, country_iso3,
    )
    if expected_tracking_info is not None:
        assert response.json()['tracking_info'] == expected_tracking_info


@pytest.mark.translations(
    grocery_orders={
        'additional_car_info': {
            'ru': '%(car_color)s автомобиль, модель %(car_model)s',
            'en': '%(car_color)s car, model %(car_model)s',
        },
        'model_car_info': {
            'ru': 'модель %(car_model)s',
            'en': 'model %(car_model)s',
        },
    },
)
@pytest.mark.parametrize(
    'locale, car_colour, car_model',
    [
        ['ru', 'красный', 'майбах'],
        ['ru', None, 'майбах'],
        ['en', 'red', 'maybach'],
        ['en', None, 'maybach'],
        ['fr', 'red', 'maybach'],
        ['fr', None, 'maybach'],
        ['iz', 'red', 'maybach'],
        ['iz', None, 'maybach'],
    ],
)
async def test_car_additional_info(
        pgsql,
        taxi_grocery_orders,
        grocery_depots,
        grocery_cart,
        locale,
        car_colour,
        car_model,
):
    dispatch_performer = models.DispatchPerformer(
        driver_id='performer_driver_id',
        eats_courier_id='performer_eats_courier_id',
        vat='performer_vat',
        balance_client_id='performer_balance_client_id',
        car_model=car_model,
        car_color=car_colour,
    )
    order = models.Order(
        pgsql,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='dispatch_id',
            dispatch_status='revoked',
            dispatch_cargo_status='delivered',
            dispatch_transport_type='performer_transport_type',
            dispatch_car_model=car_model,
            dispatch_car_color=car_colour,
        ),
        dispatch_performer=dispatch_performer,
        locale=locale,
    )
    grocery_cart.set_depot_id(depot_id=order.depot_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/supply-info',
        headers=headers.DEFAULT_HEADERS,
        json={'order_id': order.order_id},
    )

    if locale == 'ru':
        if car_colour:
            assert (
                response.json()['car_additional_info']
                == 'красный автомобиль, модель майбах'
            )
        else:
            assert response.json()['car_additional_info'] == 'модель майбах'
    elif locale == 'en':
        if car_colour:
            assert (
                response.json()['car_additional_info']
                == 'red car, model maybach'
            )
        else:
            assert response.json()['car_additional_info'] == 'model maybach'
    else:
        assert 'car_additional_info' not in response.json()


@pytest.mark.translations(
    grocery_orders={
        'additional_car_info': {
            'ru': '%(car_color)s автомобиль, модель %(car_model)s',
            'en': '%(car_color)s car, model %(car_model)s',
        },
        'model_car_info': {
            'ru': 'модель %(car_model)s',
            'en': 'model %(car_model)s',
        },
    },
)
async def test_israel_courier_forced_pedestrian(
        pgsql, taxi_grocery_orders, grocery_depots, grocery_cart,
):
    dispatch_performer = models.DispatchPerformer(
        driver_id='performer_driver_id',
        eats_courier_id='performer_eats_courier_id',
        vat='performer_vat',
        balance_client_id='performer_balance_client_id',
        car_model='maybach',
        car_color='red',
    )
    order = models.Order(
        pgsql,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='dispatch_id',
            dispatch_status='revoked',
            dispatch_cargo_status='delivered',
            dispatch_transport_type='car',
            dispatch_car_model=dispatch_performer.car_model,
            dispatch_car_color=dispatch_performer.car_color,
        ),
        dispatch_performer=dispatch_performer,
        locale='en',
    )
    grocery_cart.set_depot_id(depot_id=order.depot_id)
    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, country_iso3='ISR',
    )

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/supply-info',
        headers=headers.DEFAULT_HEADERS,
        json={'order_id': order.order_id},
    )

    assert response.status_code == 200

    assert response.json()['transport_type'] == 'pedestrian'
    assert 'car_additional_info' not in response.json()
