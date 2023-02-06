import freezegun
import pytest

from taxi.robowarehouse.lib.misc.helpers import generate_id
from taxi.robowarehouse.lib.concepts import orders
from taxi.robowarehouse.lib.concepts import packages
from taxi.robowarehouse.lib.concepts import package_places
from taxi.robowarehouse.lib.concepts import warehouses

CANCEL_URL = '/dealer/v1/orders/cancel-order/'
CANCEL_STATE = orders.types.OrderState.CANCELLED


def _get_order_response(order: orders.Order, **kwargs) -> dict:
    response = {
        'order_id': order.order_id,
        'warehouse_id': order.warehouse_id,
        'customer_address': order.customer_address,
        'customer_location': order.customer_location,
        'customer_meta': order.customer_meta,
        'customer_phone': order.customer_phone,
        'customer_uid': order.customer_uid,
        'delivery_date': order.delivery_date and order.delivery_date.isoformat(),
        'external_system': order.external_system,
        'external_order_id': order.external_order_id,
        'state': order.state.value,
        'state_meta': order.state_meta,
        'token': order.token,
        'created_at': order.created_at.isoformat(),
        'updated_at': order.updated_at.isoformat(),
    }
    for key, value in kwargs.items():
        response[key] = value

    return response


def _get_package_response(package: packages.Package, **kwargs) -> dict:
    response = {
        'package_id': package.package_id,
        'order_id': package.order_id,
        'barcode': package.barcode,
        'description': package.description,
        'measurements': package.measurements,
        'state': package.state.value,
        'state_meta': package.state_meta,
        'updated_at': package.updated_at.isoformat(),
        'created_at': package.created_at.isoformat(),
    }
    for key, value in kwargs.items():
        response[key] = value

    return response


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_cancel_order_not_found(client):
    order_id = generate_id()

    data = {
        'order_id': order_id,
        'reason': 'some reasons'
    }
    response = await client.post(CANCEL_URL, json=data)

    expected = {
        'code': 'ORDER_NOT_FOUND_ERROR',
        'details': {
            'occurred_at': '2020-01-02T00:04:05+00:00',
            'order_id': order_id
        },
        'message': 'Order not found',
    }

    assert response.status_code == 404
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_post_cancel_order_to_cancelled(client):
    order1 = await orders.factories.create(state='NEW')
    package1_1 = await packages.factories.create(order_id=order1.order_id, state='NEW')
    package1_2 = await packages.factories.create(order_id=order1.order_id, state='DELIVERED')

    order2 = await orders.factories.create()
    await packages.factories.create(order_id=order2.order_id)

    data = {
        'order_id': order1.order_id,
        'reason': 'some reasons'
    }

    response = await client.post(CANCEL_URL, json=data)

    expected = _get_order_response(
        order1,
        state=CANCEL_STATE.value,
        state_meta={'reason': 'some reasons'},
        updated_at='2020-01-02T00:04:05+00:00',
    )
    expected_packages = [
        _get_package_response(
            package1_1,
            state=CANCEL_STATE.value,
            state_meta={'reason': 'some reasons'},
            updated_at='2020-01-02T00:04:05+00:00',
        ),
        _get_package_response(package1_2),
    ]
    expected['packages'] = sorted(
        expected_packages, key=lambda p: p.get('package_id', ''))

    assert response.status_code == 200

    response_json = response.json()
    assert 'packages' in response_json
    response_json['packages'] = sorted(
        response_json['packages'], key=lambda p: p.get('package_id', '')
    )

    assert response_json == expected

    response = await client.post(CANCEL_URL, json=data)

    expected = {
        'code': 'ORDER_NOT_ACTIVE',
        'details': {
            'occurred_at': '2020-01-02T00:04:05+00:00',
            'order_id': order1.order_id
        },
        'message': 'Order is not active.',
    }

    assert response.status_code == 409
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_post_cancel_order_to_cancelling(client):
    order = await orders.factories.create(state=orders.types.OrderState.RECEIVED)
    package1 = await packages.factories.create(order_id=order.order_id,
                                               state=packages.types.PackageState.IN_WAREHOUSE)
    package2 = await packages.factories.create(order_id=order.order_id,
                                               state=packages.types.PackageState.DELIVERED)

    data = {
        'order_id': order.order_id,
        'reason': 'too long'
    }

    response = await client.post(CANCEL_URL, json=data)

    expected = {
        **order.to_dict(),
        'state': orders.types.OrderState.CANCELLING,
        'created_at': order.created_at.isoformat(),
        'updated_at': '2020-01-02T00:04:05+00:00',
        'state_meta': {'reason': 'too long'},
    }

    expected_packages = [
        {
            **package1.to_dict(),
            'state': packages.types.PackageState.CANCELLING,
            'created_at': package1.created_at.isoformat(),
            'updated_at': '2020-01-02T00:04:05+00:00',
            'state_meta': {'reason': 'too long'},
        },
        {
            **package2.to_dict(),
            'created_at': package2.created_at.isoformat(),
            'updated_at': package2.updated_at.isoformat(),
        },

    ]
    expected_packages.sort(key=lambda el: el.get('package_id', ''))

    expected['packages'] = expected_packages

    assert response.status_code == 200

    response_json = response.json()
    response_json['packages'].sort(key=lambda el: el.get('package_id', ''))

    assert response_json == expected


@pytest.mark.asyncio
async def test_states_list_not_found(client):
    await orders.factories.create()
    order_ids = [generate_id() for _ in range(3)]

    data = {'order_ids': order_ids}
    response = await client.post('/dealer/v1/orders/states/list/', json=data)

    assert response.status_code == 200
    assert response.json() == {"orders": []}


@pytest.mark.asyncio
async def test_states_list_without_package(client):
    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id)

    expected = {
        "orders": [
            {
                'order_id': order.order_id,
                'warehouse_id': order.warehouse_id,
                'events': [],
                'items': [],
            },
        ],
    }

    data = {'order_ids': [order.order_id]}
    response = await client.post('/dealer/v1/orders/states/list/', json=data)

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.asyncio
async def test_states_list_without_events(client):
    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(updated_at=3, warehouse_id=warehouse.warehouse_id)
    package = await packages.factories.create(order_id=order.order_id)

    expected = {
        "orders": [
            {
                'order_id': order.order_id,
                'warehouse_id': order.warehouse_id,
                'events': [],
                'items': [
                    {
                        'package_id': package.package_id,
                        'barcode': package.barcode,
                        'events': [],
                    },
                ],
            },
        ],
    }

    data = {'order_ids': [order.order_id]}
    response = await client.post('/dealer/v1/orders/states/list/', json=data)

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.asyncio
async def test_states_list_with_multiple_order_events(client):
    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(updated_at=3, warehouse_id=warehouse.warehouse_id)

    order_events = []
    history = order.to_dict()
    for upd in range(3, 0, -1):
        history['updated_at'] = upd
        order_history = await orders.factories.create_history(**history)
        event = orders.OrderEventResponse(**history, timestamp=order_history.updated_at).dict()
        event['timestamp'] = event['timestamp'].isoformat()
        order_events.insert(0, event)

    expected = {
        "orders": [
            {
                'order_id': order.order_id,
                'warehouse_id': order.warehouse_id,
                'events': order_events,
                'items': [],
            },
        ],
    }

    data = {'order_ids': [order.order_id]}
    response = await client.post('/dealer/v1/orders/states/list/', json=data)

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.asyncio
async def test_states_list_with_single_package(client):
    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id)
    order_history = await orders.factories.create_history(**order.to_dict())
    package = await packages.factories.create(order_id=order.order_id)
    package_history = await packages.factories.create_history(**package.to_dict())

    package_event = packages.PackageEventResponse(**package_history.to_dict(), timestamp=package.updated_at).dict()
    package_event['timestamp'] = package_event['timestamp'].isoformat()
    order_event = orders.OrderEventResponse(**order_history.to_dict(), timestamp=order.updated_at).dict()
    order_event['timestamp'] = order_event['timestamp'].isoformat()

    expected = {
        "orders": [
            {
                'order_id': order.order_id,
                'warehouse_id': order.warehouse_id,
                'events': [order_event],
                'items': [
                    {
                        'package_id': package.package_id,
                        'barcode': package.barcode,
                        'events': [package_event]
                    }
                ]
            }
        ]
    }

    data = {'order_ids': [order.order_id]}
    response = await client.post('/dealer/v1/orders/states/list/', json=data)

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.asyncio
async def test_states_list_with_multiple_packages(client):
    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id)
    order_history = await orders.factories.create_history(order_id=order.order_id)
    package_list = [await packages.factories.create(order_id=order.order_id) for _ in range(3)]
    package_list.sort(key=lambda el: el.package_id)

    package_events = []
    for package in package_list:
        history = await packages.factories.create_history(**package.to_dict())
        event = packages.PackageEventResponse(**history.to_dict(), timestamp=history.updated_at).dict()
        event['timestamp'] = event['timestamp'].isoformat()
        package_events.append(event)

    order_event = orders.OrderEventResponse(**order_history.to_dict(), timestamp=order_history.updated_at).dict()
    order_event['timestamp'] = order_event['timestamp'].isoformat()

    expected = {
        "orders": [
            {
                'order_id': order.order_id,
                'warehouse_id': order.warehouse_id,
                'events': [order_event],
                'items': [
                    {
                        'package_id': package.package_id,
                        'barcode': package.barcode,
                        'events': [event]
                    }
                    for package, event in zip(package_list, package_events)
                ]
            }
        ]
    }

    data = {'order_ids': [order.order_id]}
    response = await client.post('/dealer/v1/orders/states/list/', json=data)

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.asyncio
async def test_states_list_with_multiple_package_events(client):
    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id)
    order_history = await orders.factories.create_history(order_id=order.order_id)
    package = await packages.factories.create(order_id=order.order_id, updated_at=3)

    package_events = []
    history = package.to_dict()
    for upd in range(3, 0, -1):
        history['updated_at'] = upd
        package_history = await packages.factories.create_history(**history)
        event = packages.PackageEventResponse(**package_history.to_dict(), timestamp=package_history.updated_at).dict()
        event['timestamp'] = event['timestamp'].isoformat()
        package_events.insert(0, event)

    order_event = orders.OrderEventResponse(**order_history.to_dict(), timestamp=order_history.updated_at).dict()
    order_event['timestamp'] = order_event['timestamp'].isoformat()

    expected = {
        "orders": [
            {
                'order_id': order.order_id,
                'warehouse_id': order.warehouse_id,
                'events': [order_event],
                'items': [
                    {
                        'package_id': package.package_id,
                        'barcode': package.barcode,
                        'events': package_events
                    }
                ]
            }
        ]
    }

    data = {'order_ids': [order.order_id]}
    response = await client.post('/dealer/v1/orders/states/list/', json=data)

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.asyncio
async def test_states_list_with_multiple_orders(client):
    warehouse = await warehouses.factories.create()
    order_list = [await orders.factories.create(warehouse_id=warehouse.warehouse_id) for _ in range(3)]
    order_list.sort(key=lambda el: el.order_id)

    package_list = [await packages.factories.create(order_id=order.order_id) for order in order_list]

    order_events = []
    for order in order_list:
        history = await orders.factories.create_history(**order.to_dict())
        event = orders.OrderEventResponse(**history.to_dict(), timestamp=history.updated_at).dict()
        event['timestamp'] = event['timestamp'].isoformat()
        order_events.append(event)

    package_events = []
    for package in package_list:
        history = await packages.factories.create_history(**package.to_dict())
        event = packages.PackageEventResponse(**history.to_dict(), timestamp=history.updated_at).dict()
        event['timestamp'] = event['timestamp'].isoformat()
        package_events.append(event)

    expected = {
        "orders": [
            {
                'order_id': order.order_id,
                'warehouse_id': order.warehouse_id,
                'events': [o_event],
                'items': [
                    {
                        'package_id': package.package_id,
                        'barcode': package.barcode,
                        'events': [p_event]
                    }
                ]
            }
            for order, package, o_event, p_event in zip(
                order_list[:2],
                package_list[:2],
                order_events[:2],
                package_events[:2],
            )
        ]
    }

    data = {'order_ids': [order.order_id for order in order_list[:2]]}
    response = await client.post('/dealer/v1/orders/states/list/', json=data)

    assert response.status_code == 200
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_create_order(client):
    warehouse = await warehouses.factories.create()
    await package_places.factories.create(warehouse_id=warehouse.warehouse_id)

    data = {
        'delivery_date': '2021-11-01T15:25:08.803Z',
        'warehouse_id': warehouse.warehouse_id,
        'packages': [{
            'measurements': {
                'width': 1,
                'height': 2,
                'length': 3,
                'weight': 4,
            }
        }],
        'customer_uid': 'test_customer_uid',
        'customer_location': {'lat': 10.0, 'lon': 20.0},
    }

    response = await client.post('/dealer/v1/orders/?vendor=LP&ref-order=ref_order', json=data)

    assert response.status_code == 200

    expected = {
        'order_id': response.json()['order_id'],
        'external_order_id': 'ref_order',
        'external_system': 'LP',
        'warehouse_id': warehouse.warehouse_id,
        'state': 'NEW',
        'customer_meta': None,
        'packages': [{
            'package_id': response.json()['packages'][0]['package_id'],
            'barcode': None,
            'partner_id': None,
            'measurements': {
                'width': 1,
                'height': 2,
                'length': 3,
                'weight': 4,
            },
            'state': 'NEW',
            'state_meta': {},
        }],
        'customer_address': None,
        'customer_location': {'lat': 10.0, 'lon': 20.0},
        'customer_meta': None,
        'customer_phone_number': None,
        'customer_uid': 'test_customer_uid',
        'token': None,
        'created_at': '2020-01-02T00:04:05+00:00',
        'updated_at': '2020-01-02T00:04:05+00:00',
    }

    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_rollback_create_order(client):
    warehouse = await warehouses.factories.create()

    data = {
        'delivery_date': '2021-11-01T15:25:08.803Z',
        'warehouse_id': warehouse.warehouse_id,
        'customer_uid': generate_id(),
        'packages': [{
            'measurements': {
                'width': 1,
                'height': 2,
                'length': 3,
                'weight': 4,
            },
        }],
    }

    response = await client.post('/dealer/v1/orders/?vendor=LP&ref-order=ref_order', json=data)

    orders_list = await orders.get_all()
    packages_list = await packages.get_all()

    assert response.status_code == 404
    assert orders_list == []
    assert packages_list == []


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_update_order(client):
    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id)
    await packages.factories.create(order_id=order.order_id)

    data = {
        'order_id': order.order_id,
        'delivery_date': '2021-11-01T15:25:08.803Z',
        'packages': [{
            'barcode': 'test_barcode',
            'partner_id': 'test_partner_id',
            'description': 'test_description',
            'measurements': {
                'width': 1,
                'height': 2,
                'length': 3,
                'weight': 4,
            },
        }],
        'customer_meta': {},
    }

    response = await client.put('/dealer/v1/orders/?vendor=LP&ref-order=ref_order', json=data)

    assert response.status_code == 200

    expected = {
        'order_id': order.order_id,
        'external_order_id': response.json()['external_order_id'],
        'external_system': 'LP',
        'warehouse_id': warehouse.warehouse_id,
        'state': 'NEW',
        'customer_meta': {},
        'packages': [{
            'package_id': response.json()['packages'][0]['package_id'],
            'barcode': 'test_barcode',
            'partner_id': 'test_partner_id',
            'measurements': {
                'width': 1,
                'height': 2,
                'length': 3,
                'weight': 4,
            },
            'state': 'NEW',
            'state_meta': {},
        }],
        'customer_address': None,
        'customer_location': {'lat': 0.0, 'lon': 0.0},
        'customer_phone_number': None,
        'customer_uid': response.json()['customer_uid'],
        'token': None,
        'created_at': '1970-01-01T00:00:01+00:00',
        'updated_at': '2020-01-02T00:04:05+00:00',
    }

    assert response.json() == expected
