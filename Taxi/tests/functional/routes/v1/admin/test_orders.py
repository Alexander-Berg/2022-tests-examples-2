import freezegun
import pytest
import datetime

from taxi.robowarehouse.lib.concepts import orders
from taxi.robowarehouse.lib.concepts import packages
from taxi.robowarehouse.lib.concepts import package_places
from taxi.robowarehouse.lib.concepts import warehouses
from taxi.robowarehouse.lib.concepts import courier_order_stages
from taxi.robowarehouse.lib.misc import datetime_utils
from taxi.robowarehouse.lib.misc.helpers import base64_encode
from taxi.robowarehouse.lib.misc.helpers import generate_id
from taxi.robowarehouse.lib.test_utils.helpers import convert_to_frontend_response
from taxi.robowarehouse.lib.test_utils.helpers import assert_items_equal


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_order_list_wrong_cursor_param(client):
    await orders.factories.create()

    response = await client.get('/admin/v1/orders/?newer_than=0')

    expected = {
        'code': 'REQUEST_VALIDATION_ERROR',
        'message': '1 validation errors occurred',
        'details': {
            'occurred_at': '2020-01-02T00:04:05+00:00',
            'errors': [
                {
                    'loc': ['query', 'newer_than'],
                    'msg': 'invalid base64 format',
                    'type': 'value_error'
                }
            ]
        }
    }

    assert response.status_code == 400
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_order_list_wrong_two_cursor_params(client):
    order = await orders.factories.create()

    token = base64_encode(order.order_id)
    response = await client.get(f'/admin/v1/orders/?newer_than={token}&older_than={token}')

    expected = {
        'code': 'WRONG_CURSOR_PARAM',
        'message': 'Wrong cursor params was given.',
        'details': {
            'occurred_at': '2020-01-02T00:04:05+00:00',
            'newer_than': token,
            'older_than': token
        }
    }

    assert response.status_code == 400
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_order_list_only_external_system(client):
    await orders.factories.create()

    response = await client.get('/admin/v1/orders/?external_system=LP')

    expected = {
        'code': 'VALIDATION_ERROR',
        'message': 'Bad request',
        'details': {
            'occurred_at': '2020-01-02T00:04:05+00:00',
            'external_order_id': None,
            'external_system': 'LP',
            'errors': [
                {
                    'loc': ['query', 'external_system'],
                    'msg': 'Only with external_order_id',
                    'type': 'value_error.missing'
                }
            ]
        }
    }

    assert response.status_code == 400
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_order_list_only_external_order_id(client):
    await orders.factories.create()

    response = await client.get('/admin/v1/orders/?external_order_id=1234')

    expected = {
        'code': 'VALIDATION_ERROR',
        'message': 'Bad request',
        'details': {
            'occurred_at': '2020-01-02T00:04:05+00:00',
            'external_order_id': '1234',
            'external_system': None,
            'errors': [
                {
                    'loc': ['query', 'external_order_id'],
                    'msg': 'Only with external_system',
                    'type': 'value_error.missing'
                }
            ]
        }
    }

    assert response.status_code == 400
    assert response.json() == expected


@pytest.mark.asyncio
async def test_get_order_list_with_barcode(client):
    order = await orders.factories.create()
    await orders.factories.create()
    await packages.factories.create(order_id=order.order_id, barcode='12345')
    await packages.factories.create(barcode='67890')

    response = await client.get('/admin/v1/orders/?barcode=1234')

    expected_results = [{**order.to_dict()}]

    expected_results = convert_to_frontend_response(expected_results)

    assert response.status_code == 200
    assert response.json() == {'orders': expected_results}


@pytest.mark.asyncio
async def test_get_orders_list(client):
    order_list = sorted([await orders.factories.create() for _ in range(10)], key=lambda el: el.order_id)

    newer_than = base64_encode(order_list[1].order_id)
    next = base64_encode(order_list[3].order_id)
    prev = base64_encode(order_list[2].order_id)

    response = await client.get(f'/admin/v1/orders/?newer_than={newer_than}&limit=2')

    expected_results = [{**order.to_dict()} for order in order_list]
    expected_results = convert_to_frontend_response(expected_results[2:4])

    assert response.status_code == 200
    assert response.json() == {
        'newerThan': next,
        'olderThan': prev,
        'orders': expected_results
    }


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_order_not_found(client):
    order_id = generate_id()

    response = await client.get(f'/admin/v1/orders/{order_id}/')

    expected = {
        'code': 'ORDER_NOT_FOUND_ERROR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'order_id': order_id},
        'message': 'Order not found',
    }

    assert response.status_code == 404
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_order(client):
    now = datetime_utils.get_now()
    delta_20m = datetime.timedelta(minutes=20)
    delta_10m = datetime.timedelta(minutes=10)

    order = await orders.factories.create()
    packages_list = [await packages.factories.create(order_id=order.order_id) for _ in range(2)]
    places = [
        await package_places.factories.create(package_id=package.package_id) for package in packages_list
    ]
    stage = await courier_order_stages.factories.create(order_id=order.order_id, effective_time=now - delta_10m)
    await courier_order_stages.factories.create(order_id=order.order_id, effective_time=now - delta_20m)
    await courier_order_stages.factories.create(order_id=order.order_id)

    packages_list.sort(key=lambda el: el.package_id)
    places.sort(key=lambda el: el.package_id)

    expected_result = orders.AdminOrderResponse(
        **order.to_dict(),
        package_places=[package_places.PackagePlaceResponse(**place.to_dict()) for place in places],
        packages=[packages.PackageResponse(**package.to_dict()) for package in packages_list],
        courier_order_stage=courier_order_stages.CourierOrderStageResponse(**stage.to_dict())
    )

    response = await client.get(f'/admin/v1/orders/{order.order_id}/')
    expected_result = convert_to_frontend_response(expected_result.dict())

    assert response.status_code == 200
    assert response.json() == expected_result


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_order_history(client):
    now = datetime_utils.get_now()
    delta_30m = datetime.timedelta(minutes=30)
    delta_20m = datetime.timedelta(minutes=20)
    delta_10m = datetime.timedelta(minutes=10)

    order = await orders.factories.create()
    order_history1 = await orders.factories.create_history(order_id=order.order_id)
    package_history1 = await packages.factories.create_history(order_id=order_history1.order_id, barcode='123')
    order_history2 = await orders.factories.create_history(order_id=order_history1.order_id,
                                                           updated_at=now - delta_30m,
                                                           state=orders.types.OrderState.RECEIVED,
                                                           delivery_date=now - delta_30m)
    package_history2 = await packages.factories.create_history(order_id=order_history1.order_id,
                                                               package_id=package_history1.package_id,
                                                               updated_at=now - delta_30m,
                                                               state=packages.types.PackageState.IN_WAREHOUSE,
                                                               barcode='1234')
    stage1 = await courier_order_stages.factories.create(
        courier_id='undefined',
        order_id=order_history1.order_id,
        effective_time=now - delta_30m,
    )
    stage2 = await courier_order_stages.factories.create(
        courier_id='undefined',
        order_id=order_history1.order_id,
        effective_time=now - delta_20m,
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
    )
    stage3 = await courier_order_stages.factories.create(
        courier_id='undefined',
        order_id=order_history1.order_id,
        effective_time=now - delta_10m,
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
    )
    get_params_from_order = lambda order: {
        'updated_at': order.updated_at,
        'state': order.state,
        'state_meta': order.state_meta,
        'delivery_date': order.delivery_date,
        'order_id': order.order_id,
        'model': 'Order',
        'metadata': orders.HistoryMetaDataResponse(**{
            'external_system': order.external_system,
            'external_order_id': order.external_order_id,
            'warehouse_id': order.warehouse_id,
            'customer_address': order.customer_address,
            'customer_location': order.customer_location,
            'customer_meta': order.customer_meta,
            'customer_phone': order.customer_phone,
            'customer_uid': order.customer_uid,
        })
    }
    get_params_from_package = lambda package: {
        'updated_at': package.updated_at,
        'state': package.state,
        'state_meta': package.state_meta,
        'barcode': package.barcode,
        'order_id': package.order_id,
        'package_id': package.package_id,
        'model': 'Package',
        'metadata': orders.HistoryMetaDataResponse(**{
            'description': package.description,
            'measurements': package.measurements,
        })
    }

    get_params_from_stage = lambda stage: {
        'updated_at': stage.effective_time,
        'state': stage.type,
        'state_meta': stage.type_meta,
        'courier_id': stage.courier_id,
        'order_id': stage.order_id,
        'model': 'CourierOrderStage',
    }
    history_result = [
        orders.AdminHistoryResponse(**get_params_from_order(order_history1)),
        orders.AdminHistoryResponse(**get_params_from_package(package_history1)),
        orders.AdminHistoryResponse(**get_params_from_order(order_history2)),
        orders.AdminHistoryResponse(**get_params_from_package(package_history2)),
        orders.AdminHistoryResponse(**get_params_from_stage(stage1)),
        orders.AdminHistoryResponse(**get_params_from_stage(stage2)),
        orders.AdminHistoryResponse(**get_params_from_stage(stage3)),
    ]

    expected_result = orders.AdminHistoryListResponse(history=history_result).dict()

    expected_result = convert_to_frontend_response(expected_result)

    response = await client.get(f'/admin/v1/orders/{order.order_id}/history/')

    assert response.status_code == 200
    assert response.json() == expected_result


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_receive_order_not_found(client):
    order_id = generate_id()

    response = await client.post(f'/admin/v1/orders/{order_id}/receive/')

    expected = {
        'code': 'ORDER_NOT_FOUND_ERROR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'order_id': order_id},
        'message': 'Order not found',
    }

    assert response.status_code == 404
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_receive_order_already_received(client):
    order = await orders.factories.create(state=orders.types.OrderState.RECEIVED)

    response = await client.post(f'/admin/v1/orders/{order.order_id}/receive/')

    expected = {
        'code': 'ORDER_ALREADY_RECEIVED',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'order_id': order.order_id},
        'message': 'Order has received already.',
    }

    assert response.status_code == 409
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_receive_order(client):
    now = datetime_utils.get_now()

    order = await orders.factories.create()
    await orders.factories.create()

    package = await packages.factories.create(order_id=order.order_id)

    response = await client.post(f'/admin/v1/orders/{order.order_id}/receive/')

    expected = orders.OrderResponse(**{
        **order.to_dict(),
        'state': orders.types.OrderState.RECEIVED,
        'updated_at': now
    }).dict()
    expected = convert_to_frontend_response(expected)

    assert response.status_code == 200
    assert response.json() == expected

    new_package = await packages.get_by_package_id(package.package_id)
    expected_package = {
        **package.to_dict(),
        'state': packages.types.PackageState.IN_WAREHOUSE,
        'updated_at': now,
    }
    assert new_package.to_dict() == expected_package

    stages = await courier_order_stages.get_all()
    expected_stage = courier_order_stages.factories.build(
        courier_id='undefined',
        order_id=order.order_id,
        effective_time=now,
        type_=courier_order_stages.types.CourierOrderStageType.NEW,
    )
    assert len(stages) == 1
    assert stages[0].to_dict() == expected_stage.to_dict()


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_cancel_order_not_found(client):
    order_id = generate_id()

    response = await client.post(f'/admin/v1/orders/{order_id}/cancel/', json={'reason': 'reason'})

    expected = {
        'code': 'ORDER_NOT_FOUND_ERROR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'order_id': order_id},
        'message': 'Order not found',
    }

    assert response.status_code == 404
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_cancel_order_not_active(client):
    order = await orders.factories.create(state=orders.types.OrderState.DELIVERED)

    response = await client.post(f'/admin/v1/orders/{order.order_id}/cancel/', json={'reason': 'reason'})

    expected = {
        'code': 'ORDER_NOT_ACTIVE',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'order_id': order.order_id},
        'message': 'Order is not active.',
    }

    assert response.status_code == 409
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_cancel_order_not_cancelling(client):
    order = await orders.factories.create()

    response = await client.post(f'/admin/v1/orders/{order.order_id}/cancel/',
                                 json={'reason': 'reason', 'give_back': True})

    expected = {
        'code': 'ORDER_NOT_CANCELLING',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'order_id': order.order_id},
        'message': 'Order is not cancelling. Cancellation is forbidden',
    }

    assert response.status_code == 409
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_cancel_order_to_cancelled(client):
    now = datetime_utils.get_now()
    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id)
    package = await packages.factories.create(order_id=order.order_id)
    place = await package_places.factories.create(
        package_id=package.package_id,
        state=package_places.types.PackagePlaceState.FILLED,
        warehouse_id=warehouse.warehouse_id,
    )

    response = await client.post(f'/admin/v1/orders/{order.order_id}/cancel/', json={'reason': 'reason'})

    new_order = await orders.get_by_order_id(order_id=order.order_id)
    new_package = await packages.get_by_package_id(package_id=package.package_id)
    new_place = (await package_places.get_all())[0]

    assert response.status_code == 200
    assert response.json() == convert_to_frontend_response(new_order.to_dict())
    assert new_order.to_dict() == {
        **order.to_dict(),
        'state': orders.types.OrderState.CANCELLED,
        'updated_at': now,
        'state_meta': {'reason': 'reason'},
    }
    assert new_package.to_dict() == {
        **package.to_dict(),
        'state': packages.types.PackageState.CANCELLED,
        'updated_at': now,
        'state_meta': {'reason': 'reason'},
    }
    assert new_place.to_dict() == {
        **place.to_dict(),
        'state': package_places.types.PackagePlaceState.EMPTY,
        'updated_at': now,
        'package_id': None,
    }


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_cancel_order_to_cancelling(client):
    now = datetime_utils.get_now()
    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id,
                                          state=orders.types.OrderState.RECEIVED)
    package = await packages.factories.create(order_id=order.order_id,
                                              state=packages.types.PackageState.IN_WAREHOUSE)
    place = await package_places.factories.create(
        package_id=package.package_id,
        state=package_places.types.PackagePlaceState.FILLED,
        warehouse_id=warehouse.warehouse_id,
    )

    response = await client.post(f'/admin/v1/orders/{order.order_id}/cancel/', json={'reason': 'reason'})

    new_order = await orders.get_by_order_id(order_id=order.order_id)
    new_package = await packages.get_by_package_id(package_id=package.package_id)
    new_place = (await package_places.get_all())[0]

    assert response.status_code == 200
    assert response.json() == convert_to_frontend_response(new_order.to_dict())
    assert new_order.to_dict() == {
        **order.to_dict(),
        'state': orders.types.OrderState.CANCELLING,
        'updated_at': now,
        'state_meta': {'reason': 'reason'},
    }
    assert new_package.to_dict() == {
        **package.to_dict(),
        'state': packages.types.PackageState.CANCELLING,
        'updated_at': now,
        'state_meta': {'reason': 'reason'},
    }
    assert new_place.to_dict() == place.to_dict()


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_cancel_order_give_back(client):
    now = datetime_utils.get_now()
    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id,
                                          state=orders.types.OrderState.CANCELLING,
                                          state_meta={'reason': 'reason'})
    package = await packages.factories.create(order_id=order.order_id,
                                              state=packages.types.PackageState.CANCELLING,
                                              state_meta={'reason': 'reason'})
    place = await package_places.factories.create(
        package_id=package.package_id,
        state=package_places.types.PackagePlaceState.FILLED,
        warehouse_id=warehouse.warehouse_id,
    )

    response = await client.post(f'/admin/v1/orders/{order.order_id}/cancel/',
                                 json={'reason': 'reason', 'give_back': True})

    new_order = await orders.get_by_order_id(order_id=order.order_id)
    new_package = await packages.get_by_package_id(package_id=package.package_id)
    new_place = (await package_places.get_all())[0]

    assert response.status_code == 200
    assert response.json() == convert_to_frontend_response(new_order.to_dict())
    assert new_order.to_dict() == {
        **order.to_dict(),
        'state': orders.types.OrderState.CANCELLED,
        'updated_at': now,
    }
    assert new_package.to_dict() == {
        **package.to_dict(),
        'state': packages.types.PackageState.CANCELLED,
        'updated_at': now,
    }
    assert new_place.to_dict() == {
        **place.to_dict(),
        'state': package_places.types.PackagePlaceState.EMPTY,
        'updated_at': now,
        'package_id': None,
    }


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_renew_order_not_found(client):
    order_id = generate_id()

    response = await client.post(f'/admin/v1/orders/{order_id}/renew/')

    expected = {
        'code': 'ORDER_NOT_FOUND_ERROR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'order_id': order_id},
        'message': 'Order not found',
    }

    assert response.status_code == 404
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_renew_order_not_active(client):
    order = await orders.factories.create(state=orders.types.OrderState.DELIVERED)

    response = await client.post(f'/admin/v1/orders/{order.order_id}/renew/')

    expected = {
        'code': 'ORDER_NOT_ACTIVE',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'order_id': order.order_id},
        'message': 'Order is not active.',
    }

    assert response.status_code == 409
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_renew_order(client):
    now = datetime_utils.get_now()
    order = await orders.factories.create(state=orders.types.OrderState.RECEIVED)
    package = await packages.factories.create(order_id=order.order_id,
                                              state=packages.types.PackageState.IN_WAREHOUSE)
    await courier_order_stages.factories.create(
        courier_id='undefined',
        order_id=order.order_id,
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED
    )

    response = await client.post(f'/admin/v1/orders/{order.order_id}/renew/')

    new_order = await orders.get_by_order_id(order_id=order.order_id)
    new_package = await packages.get_by_package_id(package_id=package.package_id)
    stages = await courier_order_stages.get_all()
    stages.sort(key=lambda el: el.effective_time)

    assert response.status_code == 200
    assert response.json() == convert_to_frontend_response(new_order.to_dict())
    assert new_order.to_dict() == {
        **order.to_dict(),
        'state': orders.types.OrderState.NEW,
        'updated_at': now,
    }
    assert new_package.to_dict() == {
        **package.to_dict(),
        'state': packages.types.PackageState.NEW,
        'updated_at': now,
    }
    assert len(stages) == 2
    assert stages[-1].to_dict() == {
        'courier_id': 'undefined',
        'order_id': order.order_id,
        'effective_time': now,
        'type': courier_order_stages.types.CourierOrderStageType.NEW,
        'type_meta': {}
    }


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_set_delivered_not_found(client):
    order_id = generate_id()

    response = await client.post(f'/admin/v1/orders/{order_id}/set-delivered/')

    expected = {
        'code': 'ORDER_NOT_FOUND_ERROR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'order_id': order_id},
        'message': 'Order not found',
    }

    assert response.status_code == 404
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_set_delivered(client):
    now = datetime_utils.get_now()

    order = await orders.factories.create(state=orders.types.OrderState.DELIVERING)
    package = await packages.factories.create(order_id=order.order_id,
                                              state=packages.types.PackageState.DELIVERING)
    place = await package_places.factories.create(package_id=package.package_id,
                                                  state=package_places.types.PackagePlaceState.FILLED)

    response = await client.post(f'/admin/v1/orders/{order.order_id}/set-delivered/')

    new_order = await orders.get_by_order_id(order.order_id)
    new_package = await packages.get_by_package_id(package.package_id)
    new_place = (await package_places.get_all())[0]

    order_history = await orders.get_all_history()
    package_history = await packages.get_all_history()
    place_history = await package_places.get_all_history()

    assert response.status_code == 200
    assert response.json() == convert_to_frontend_response(new_order.to_dict())

    assert new_order.to_dict() == {**order.to_dict(),
                                   'state': orders.types.OrderState.DELIVERED,
                                   'updated_at': now,
                                   'delivery_date': now}
    assert new_package.to_dict() == {**package.to_dict(),
                                     'state': packages.types.PackageState.DELIVERED,
                                     'updated_at': now}
    assert new_place.to_dict() == {**place.to_dict(),
                                   'package_id': None,
                                   'state': package_places.types.PackagePlaceState.EMPTY,
                                   'updated_at': now}
    assert_items_equal([order_h.to_dict() for order_h in order_history], [new_order.to_dict()])
    assert_items_equal([package_h.to_dict() for package_h in package_history], [new_package.to_dict()])
    assert_items_equal([place_h.to_dict() for place_h in place_history], [new_place.to_dict()])
