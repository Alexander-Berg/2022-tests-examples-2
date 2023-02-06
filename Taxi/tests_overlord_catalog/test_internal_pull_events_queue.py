import datetime

import pytest


FIRST_PULL_TIME = '2021-08-09T10:12:10+00:00'
EVENT_TIME = '2021-08-09T10:10:10+00:00'
BEFORE_EVENT_TIME = '2021-08-05T10:10:10+00:00'
NEXT_PULL_TIME = '2021-08-09T12:12:10+00:00'
NEW_EVENT_TIME = '2021-08-09T12:10:10+00:00'
PRODUCT1_PRICE_IN_DEPOT1 = 10
PRODUCT1_PRICE_IN_DEPOT2 = 20
PRODUCT2_PRICE_IN_DEPOT1 = 100


def _map_availability_events(response_json):
    events = {}
    for event in response_json['events']:
        assert event['event'] == 'availability_changed'
        events[event['product_id']] = {}
        for availability_per_depot in event['availabilities_per_depots']:
            events[event['product_id']][
                int(availability_per_depot['external_depot_id'])
            ] = availability_per_depot
    return events


def _map_price_events(response_json):
    events = {}
    for event in response_json['events']:
        assert event['event'] == 'full_price_changed'
        events[event['product_id']] = {}
        for full_price_per_depot in event['full_prices_per_depots']:
            events[event['product_id']][
                int(full_price_per_depot['external_depot_id'])
            ] = full_price_per_depot
    return events


# Проверяет, что ручка /internal/v1/catalog/v1/pull-event-queue возвращает
# события об изменениях доступности товаров.
@pytest.mark.config(
    OVERLORD_CATALOG_EVENT_QUEUES_SETTINGS={
        '__default__': {
            'pg-dist-lock-settings': {
                'table': 'catalog_wms.distlocks',
                'pg-timeout-ms': 200,
                'lock-ttl-ms': 10000,
            },
            'fallback-interval-m': 15,
        },
    },
)
async def test_pull_availability_changed_events(
        taxi_overlord_catalog, overlord_db, mocked_time,
):
    mocked_time.set(datetime.datetime.fromisoformat(FIRST_PULL_TIME))
    await taxi_overlord_catalog.invalidate_caches()

    depot1 = None
    depot2 = None
    product1_in_depot1 = None

    with overlord_db as db:
        depot1 = db.add_depot(depot_id=1)
        depot2 = db.add_depot(depot_id=2)
        # Появился
        product1_in_depot1 = depot1.add_product(
            product_id=1,
            in_stock=5,
            updated=EVENT_TIME,
            restored=EVENT_TIME,
            depleted=BEFORE_EVENT_TIME,
        )
        # Закончился
        depot2.add_product(
            product_id=1,
            in_stock=0,
            updated=EVENT_TIME,
            restored=BEFORE_EVENT_TIME,
            depleted=EVENT_TIME,
        )

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/pull-event-queue',
        json={'event': 'availability_changed'},
    )
    assert response.status_code == 200
    events = _map_availability_events(response.json())
    product1_id = product1_in_depot1.id_wms
    assert events[product1_id][depot1.depot_id] == {
        'available': True,
        'available_updated': EVENT_TIME,
        'depot_id': depot1.id_wms,
        'external_depot_id': str(depot1.depot_id),
    }
    assert events[product1_id][depot2.depot_id] == {
        'available': False,
        'available_updated': EVENT_TIME,
        'depot_id': depot2.id_wms,
        'external_depot_id': str(depot2.depot_id),
    }

    # Имитируем следующий запрос к очереди.
    mocked_time.set(datetime.datetime.fromisoformat(NEXT_PULL_TIME))
    await taxi_overlord_catalog.invalidate_caches()

    product2_in_depot1 = None
    with overlord_db as db:
        product2_in_depot1 = depot1.add_product(
            product_id=2,
            in_stock=0,
            updated=NEW_EVENT_TIME,
            restored=BEFORE_EVENT_TIME,
            depleted=NEW_EVENT_TIME,
        )

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/pull-event-queue',
        json={'event': 'availability_changed'},
    )
    assert response.status_code == 200
    new_events = _map_availability_events(response.json())
    product2_id = product2_in_depot1.id_wms
    assert new_events[product2_id][depot1.depot_id] == {
        'available': False,
        'available_updated': NEW_EVENT_TIME,
        'depot_id': depot1.id_wms,
        'external_depot_id': str(depot1.depot_id),
    }

    assert depot2.depot_id not in new_events[product2_id]
    assert product1_id not in new_events


# Проверяет, что ручка /internal/v1/catalog/v1/pull-events-queue возвращает
# события об изменениях цен товаров.
@pytest.mark.config(
    OVERLORD_CATALOG_EVENT_QUEUES_SETTINGS={
        '__default__': {
            'pg-dist-lock-settings': {
                'table': 'catalog_wms.distlocks',
                'pg-timeout-ms': 200,
                'lock-ttl-ms': 10000,
            },
            'fallback-interval-m': 15,
        },
    },
)
async def test_pull_price_changed_events(
        taxi_overlord_catalog, overlord_db, mocked_time,
):
    mocked_time.set(datetime.datetime.fromisoformat(FIRST_PULL_TIME))
    await taxi_overlord_catalog.invalidate_caches()

    depot1 = None
    depot2 = None
    product1_in_depot1 = None

    with overlord_db as db:
        depot1 = db.add_depot(depot_id=1)
        depot2 = db.add_depot(depot_id=2)
        product1_in_depot1 = depot1.add_product(
            product_id=1, price=PRODUCT1_PRICE_IN_DEPOT1, updated=EVENT_TIME,
        )
        depot2.add_product(
            product_id=1, price=PRODUCT1_PRICE_IN_DEPOT2, updated=EVENT_TIME,
        )

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/pull-event-queue',
        json={'event': 'full_price_changed'},
    )

    assert response.status_code == 200
    events = _map_price_events(response.json())
    product1_id = product1_in_depot1.id_wms
    assert events[product1_id][depot1.depot_id] == {
        'depot_id': depot1.id_wms,
        'external_depot_id': str(depot1.depot_id),
        'full_price': str(PRODUCT1_PRICE_IN_DEPOT1),
        'full_price_updated': EVENT_TIME,
    }
    assert events[product1_id][depot2.depot_id] == {
        'depot_id': depot2.id_wms,
        'external_depot_id': str(depot2.depot_id),
        'full_price': str(PRODUCT1_PRICE_IN_DEPOT2),
        'full_price_updated': EVENT_TIME,
    }

    # Имитируем следующий запрос к очереди.
    mocked_time.set(datetime.datetime.fromisoformat(NEXT_PULL_TIME))
    await taxi_overlord_catalog.invalidate_caches()

    product2_in_depot1 = None
    with overlord_db as db:
        product2_in_depot1 = depot1.add_product(
            product_id=2,
            price=PRODUCT2_PRICE_IN_DEPOT1,
            updated=NEW_EVENT_TIME,
            restored=BEFORE_EVENT_TIME,
            depleted=NEW_EVENT_TIME,
        )

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/pull-event-queue',
        json={'event': 'full_price_changed'},
    )
    new_events = _map_price_events(response.json())
    product2_id = product2_in_depot1.id_wms
    assert new_events[product2_id][depot1.depot_id] == {
        'depot_id': depot1.id_wms,
        'external_depot_id': str(depot1.depot_id),
        'full_price': str(PRODUCT2_PRICE_IN_DEPOT1),
        'full_price_updated': NEW_EVENT_TIME,
    }
    assert product1_id not in new_events
