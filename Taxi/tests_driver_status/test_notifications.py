import json

import pytest
import pytz

# pylint: disable=import-only-modules
from tests_driver_status.enum_constants import LegacyDriverStatus
from tests_driver_status.enum_constants import OrderStatus
import tests_driver_status.utils as utils


async def _post_status(
        taxi_driver_status, park_id, profile_id, status, alias_id=None,
):
    body = {'target_status': status}

    if alias_id is not None:
        body['order'] = alias_id

    response = await taxi_driver_status.post(
        'v2/status/client',
        headers={
            'X-YaTaxi-Park-Id': park_id,
            'X-YaTaxi-Driver-Profile-Id': profile_id,
            'X-Request-Application-Version': '9.40',
            'X-Request-Version-Type': '',  # '' for taximeter
            'X-Request-Platform': 'android',
        },
        data=json.dumps(body),
    )
    assert response.status_code == 200


async def _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id,
        status,
        provider='yandex',
):
    body = {
        'park_id': park_id,
        'profile_id': profile_id,
        'alias_id': alias_id,
        'status': status,
        'provider': provider,
    }

    response = await taxi_driver_status.post(
        'v2/order/store', data=json.dumps(body),
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'order_status_db_lookup_for_notification', [False, True],
)
@pytest.mark.parametrize('finish_by_client', [False, True])
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.redis_store(
    ['hset', 'Order:SetCar:Items:Providers:park001', 'alias001', 2],  # yandex
)
async def test_regular_order(
        taxi_driver_status,
        taxi_config,
        testpoint,
        mocked_time,
        order_status_db_lookup_for_notification,
        finish_by_client,
):
    @testpoint('status_store_notify')
    def client_tp(data):
        pass

    @testpoint('master_order_store_notify')
    def master_tp(data):
        pass

    taxi_config.set_values(
        {
            'DRIVER_STATUS_ORDERS_FEATURES': {
                'merge_statuses': True,
                'start_by_processing': False,
                'order_status_db_lookup_for_notification': (
                    order_status_db_lookup_for_notification
                ),
                'finish_by_client': finish_by_client,
                'finish_by_client_timeout': 600,
            },
        },
    )
    await taxi_driver_status.invalidate_caches()

    park_id = 'park001'
    profile_id = 'profile001'
    alias_id = 'alias001'

    # 1. contractor becomes online
    await _post_status(
        taxi_driver_status, park_id, profile_id, LegacyDriverStatus.Online,
    )
    events = client_tp.next_call()['data']
    assert len(events) == 1
    event = events[0]
    assert not event['orders']

    mocked_time.sleep(1)
    await taxi_driver_status.invalidate_caches(
        cache_names=['driver-statuses-cache'],
    )

    # 2. backend starts new order
    await _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id,
        OrderStatus.kDriving,
    )
    event = master_tp.next_call()['data']
    assert len(event['orders']) == 1
    order = event['orders'][0]
    assert order['status'] == OrderStatus.kDriving

    mocked_time.sleep(1)
    if not order_status_db_lookup_for_notification:
        await taxi_driver_status.invalidate_caches()

    # 3. taximeter sends status update
    await _post_status(
        taxi_driver_status,
        park_id,
        profile_id,
        LegacyDriverStatus.Online,
        alias_id,
    )
    events = client_tp.next_call()['data']
    assert len(events) == 1
    event = events[0]
    order = event['orders'][0]
    assert order['status'] == OrderStatus.kDriving

    mocked_time.sleep(1)
    if not order_status_db_lookup_for_notification:
        await taxi_driver_status.invalidate_caches()

    # 4. backend order status update (skip waiting: not necessary for testing)
    await _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id,
        OrderStatus.kTransporting,
    )
    event = master_tp.next_call()['data']
    assert len(event['orders']) == 1
    order = event['orders'][0]
    assert order['status'] == OrderStatus.kTransporting

    mocked_time.sleep(1)
    if not order_status_db_lookup_for_notification:
        await taxi_driver_status.invalidate_caches()

    # 5. periodical status update by taximeter
    await _post_status(
        taxi_driver_status,
        park_id,
        profile_id,
        LegacyDriverStatus.Online,
        alias_id,
    )
    events = client_tp.next_call()['data']
    assert len(events) == 1
    event = events[0]
    order = event['orders'][0]
    assert order['status'] == OrderStatus.kTransporting

    mocked_time.sleep(1)
    if not order_status_db_lookup_for_notification:
        await taxi_driver_status.invalidate_caches()

    # 6. order complete by backend
    await _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id,
        OrderStatus.kComplete,
    )
    event = master_tp.next_call()['data']
    if finish_by_client:
        assert len(event['orders']) == 1
        order = event['orders'][0]
        assert order['status'] == OrderStatus.kTransporting
    else:
        assert not event['orders']

    mocked_time.sleep(1)
    if not order_status_db_lookup_for_notification:
        await taxi_driver_status.invalidate_caches()

    # 7. order complete by taximeter
    await _post_status(
        taxi_driver_status, park_id, profile_id, LegacyDriverStatus.Online,
    )
    events = client_tp.next_call()['data']
    assert len(events) == 1
    event = events[0]
    assert not event['orders']


@pytest.mark.parametrize(
    'order_status_db_lookup_for_notification', [False, True],
)
@pytest.mark.parametrize('finish_by_client', [False, True])
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.redis_store(
    ['hset', 'Order:SetCar:Items:Providers:park001', 'alias001', 1],  # park
)
async def test_regular_park_order(
        taxi_driver_status,
        taxi_config,
        testpoint,
        mocked_time,
        order_status_db_lookup_for_notification,
        finish_by_client,
):
    @testpoint('status_store_notify')
    def client_tp(data):
        pass

    @testpoint('master_order_store_notify')
    def master_tp(data):
        pass

    taxi_config.set_values(
        {
            'DRIVER_STATUS_ORDERS_FEATURES': {
                'merge_statuses': True,
                'start_by_processing': False,
                'order_status_db_lookup_for_notification': (
                    order_status_db_lookup_for_notification
                ),
                'finish_by_client': finish_by_client,
                'finish_by_client_timeout': 600,
            },
        },
    )
    await taxi_driver_status.invalidate_caches()

    park_id = 'park001'
    profile_id = 'profile001'
    alias_id = 'alias001'

    # 1. contractor becomes online
    await _post_status(
        taxi_driver_status, park_id, profile_id, LegacyDriverStatus.Online,
    )
    events = client_tp.next_call()['data']
    assert len(events) == 1
    event = events[0]
    assert not event['orders']

    mocked_time.sleep(1)
    await taxi_driver_status.invalidate_caches(
        cache_names=['driver-statuses-cache'],
    )

    # 2. backend starts new order
    await _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id,
        OrderStatus.kDriving,
        'park',
    )
    event = master_tp.next_call()['data']
    assert not event['orders']

    mocked_time.sleep(1)
    if not order_status_db_lookup_for_notification:
        await taxi_driver_status.invalidate_caches()

    # 3. taximeter sends status update
    await _post_status(
        taxi_driver_status,
        park_id,
        profile_id,
        LegacyDriverStatus.Online,
        alias_id,
    )
    events = client_tp.next_call()['data']
    assert len(events) == 1
    event = events[0]
    order = event['orders'][0]
    assert order['status'] == OrderStatus.kDriving

    mocked_time.sleep(1)
    if not order_status_db_lookup_for_notification:
        await taxi_driver_status.invalidate_caches()

    # 4. backend order status update (skip waiting: not necessary for testing)
    await _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id,
        OrderStatus.kTransporting,
        'park',
    )
    event = master_tp.next_call()['data']
    assert len(event['orders']) == 1
    order = event['orders'][0]
    assert order['status'] == OrderStatus.kTransporting

    mocked_time.sleep(1)
    if not order_status_db_lookup_for_notification:
        await taxi_driver_status.invalidate_caches()

    # 5. periodical status update by taximeter
    await _post_status(
        taxi_driver_status,
        park_id,
        profile_id,
        LegacyDriverStatus.Online,
        alias_id,
    )
    events = client_tp.next_call()['data']
    assert len(events) == 1
    event = events[0]
    order = event['orders'][0]
    assert order['status'] == OrderStatus.kTransporting

    mocked_time.sleep(1)
    if not order_status_db_lookup_for_notification:
        await taxi_driver_status.invalidate_caches()

    # 6. order complete by backend
    await _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id,
        OrderStatus.kComplete,
        'park',
    )
    event = master_tp.next_call()['data']
    assert len(event['orders']) == 1
    order = event['orders'][0]
    # don't use fake 'transporting' at order end for park orders
    assert order['status'] == OrderStatus.kDriving

    mocked_time.sleep(1)
    if not order_status_db_lookup_for_notification:
        await taxi_driver_status.invalidate_caches()

    # 7. order complete by taximeter
    await _post_status(
        taxi_driver_status, park_id, profile_id, LegacyDriverStatus.Online,
    )
    events = client_tp.next_call()['data']
    assert len(events) == 1
    event = events[0]
    assert not event['orders']


@pytest.mark.parametrize(
    'order_status_db_lookup_for_notification', [False, True],
)
@pytest.mark.parametrize('finish_by_client', [False, True])
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.redis_store(
    ['hset', 'Order:SetCar:Items:Providers:park001', 'alias001', 2],  # yandex
)
async def test_chain_orders(
        taxi_driver_status,
        taxi_config,
        testpoint,
        mocked_time,
        order_status_db_lookup_for_notification,
        finish_by_client,
):
    @testpoint('status_store_notify')
    def client_tp(data):
        pass

    @testpoint('master_order_store_notify')
    def master_tp(data):
        pass

    taxi_config.set_values(
        {
            'DRIVER_STATUS_ORDERS_FEATURES': {
                'merge_statuses': True,
                'start_by_processing': False,
                'order_status_db_lookup_for_notification': (
                    order_status_db_lookup_for_notification
                ),
                'finish_by_client': finish_by_client,
                'finish_by_client_timeout': 600,
            },
        },
    )
    await taxi_driver_status.invalidate_caches()

    park_id = 'park001'
    profile_id = 'profile001'
    alias_id1 = 'alias001'
    alias_id2 = 'alias002'

    # 1. contractor becomes online
    await _post_status(
        taxi_driver_status, park_id, profile_id, LegacyDriverStatus.Online,
    )
    events = client_tp.next_call()['data']
    assert len(events) == 1
    event = events[0]
    assert not event['orders']

    mocked_time.sleep(1)
    await taxi_driver_status.invalidate_caches()

    # 2. taximeter sends new order
    await _post_status(
        taxi_driver_status,
        park_id,
        profile_id,
        LegacyDriverStatus.Online,
        alias_id1,
    )
    events = client_tp.next_call()['data']
    assert len(events) == 1
    event = events[0]
    if finish_by_client:
        order = event['orders'][0]
        assert order['alias'] == alias_id1
        assert order['status'] == OrderStatus.kDriving
    else:
        assert not event['orders']

    mocked_time.sleep(1)
    if not order_status_db_lookup_for_notification:
        await taxi_driver_status.invalidate_caches()

    # 3. backend starts new order
    await _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id1,
        OrderStatus.kDriving,
    )
    event = master_tp.next_call()['data']
    assert len(event['orders']) == 1
    order = event['orders'][0]
    assert order['alias'] == alias_id1
    assert order['status'] == OrderStatus.kDriving

    mocked_time.sleep(1)
    if not order_status_db_lookup_for_notification:
        await taxi_driver_status.invalidate_caches()

    # 4. backend order status update (skip waiting: not necessary for testing)
    await _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id1,
        OrderStatus.kTransporting,
    )
    event = master_tp.next_call()['data']
    assert len(event['orders']) == 1
    order = event['orders'][0]
    assert order['alias'] == alias_id1
    assert order['status'] == OrderStatus.kTransporting

    mocked_time.sleep(1)
    if not order_status_db_lookup_for_notification:
        await taxi_driver_status.invalidate_caches()

    # 5. backend starts chain order
    await _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id2,
        OrderStatus.kDriving,
    )
    event = master_tp.next_call()['data']
    assert len(event['orders']) == 2
    orders = sorted(event['orders'], key=lambda order: order['alias'])
    assert orders[0]['alias'] == alias_id1
    assert orders[0]['status'] == OrderStatus.kTransporting
    assert orders[1]['alias'] == alias_id2
    assert orders[1]['status'] == OrderStatus.kDriving

    mocked_time.sleep(1)
    if not order_status_db_lookup_for_notification:
        await taxi_driver_status.invalidate_caches()

    # 6. first order complete by backend
    await _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id1,
        OrderStatus.kComplete,
    )
    event = master_tp.next_call()['data']
    if finish_by_client:
        assert len(event['orders']) == 2
        orders = sorted(event['orders'], key=lambda order: order['alias'])
        assert orders[0]['alias'] == alias_id1
        # see DRIVER_STATUS_ORDERS_FEATURES.finish_by_client
        assert orders[0]['status'] == OrderStatus.kTransporting
        assert orders[1]['alias'] == alias_id2
        assert orders[1]['status'] == OrderStatus.kDriving
    else:
        assert len(event['orders']) == 1
        order = event['orders'][0]
        assert order['alias'] == alias_id2
        assert order['status'] == OrderStatus.kDriving

    mocked_time.sleep(1)
    if not order_status_db_lookup_for_notification:
        await taxi_driver_status.invalidate_caches()

    # 7. first order complete by taximeter
    await _post_status(
        taxi_driver_status,
        park_id,
        profile_id,
        LegacyDriverStatus.Online,
        alias_id2,
    )
    events = client_tp.next_call()['data']
    assert len(events) == 1
    event = events[0]
    order = event['orders'][0]
    assert order['alias'] == alias_id2
    assert order['status'] == OrderStatus.kDriving

    mocked_time.sleep(1)
    if not order_status_db_lookup_for_notification:
        await taxi_driver_status.invalidate_caches()

    # 8. chain order complete by backend (skip waiting, transporting)
    await _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id2,
        OrderStatus.kComplete,
    )
    event = master_tp.next_call()['data']
    if finish_by_client:
        assert len(event['orders']) == 1
        order = event['orders'][0]
        assert order['alias'] == alias_id2
        assert order['status'] == OrderStatus.kTransporting
    else:
        assert not event['orders']

    mocked_time.sleep(1)
    if not order_status_db_lookup_for_notification:
        await taxi_driver_status.invalidate_caches()

    # 9. order complete by taximeter
    await _post_status(
        taxi_driver_status, park_id, profile_id, LegacyDriverStatus.Online,
    )
    events = client_tp.next_call()['data']
    assert len(events) == 1
    event = events[0]
    assert not event['orders']


@pytest.mark.parametrize(
    'order_status_db_lookup_for_notification', [False, True],
)
@pytest.mark.parametrize('finish_by_client', [False, True])
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.redis_store(
    ['hset', 'Order:SetCar:Items:Providers:park001', 'alias001', 2],  # yandex
)
async def test_timestamp(
        taxi_driver_status,
        taxi_config,
        testpoint,
        mocked_time,
        order_status_db_lookup_for_notification,
        finish_by_client,
):
    @testpoint('status_store_notify')
    def client_tp(data):
        pass

    @testpoint('master_order_store_notify')
    def master_tp(data):
        pass

    taxi_config.set_values(
        {
            'DRIVER_STATUS_ORDERS_FEATURES': {
                'merge_statuses': True,
                'start_by_processing': False,
                'order_status_db_lookup_for_notification': (
                    order_status_db_lookup_for_notification
                ),
                'finish_by_client': finish_by_client,
                'finish_by_client_timeout': 600,
            },
        },
    )
    await taxi_driver_status.invalidate_caches()

    park_id = 'park001'
    profile_id = 'profile001'
    alias_id1 = 'alias001'

    # 1. contractor becomes online
    became_online_ts = mocked_time.now().replace(tzinfo=pytz.utc)
    await _post_status(
        taxi_driver_status, park_id, profile_id, LegacyDriverStatus.Online,
    )
    events = client_tp.next_call()['data']
    assert len(events) == 1
    event = events[0]
    assert utils.parse_date_str(event['updated_ts']) == became_online_ts
    assert not event['orders']

    mocked_time.sleep(1)
    await taxi_driver_status.invalidate_caches()

    # 2. backend starts new order
    await _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id1,
        OrderStatus.kDriving,
    )
    event = master_tp.next_call()['data']
    assert utils.parse_date_str(event['updated_ts']) == became_online_ts
    assert len(event['orders']) == 1
    order = event['orders'][0]
    assert order['alias'] == alias_id1
    assert order['status'] == OrderStatus.kDriving
    assert utils.parse_date_str(
        order['event_ts'],
    ) == mocked_time.now().replace(tzinfo=pytz.utc)

    mocked_time.sleep(1)
    if not order_status_db_lookup_for_notification:
        await taxi_driver_status.invalidate_caches()

    # 3. backend order status update (skip waiting: not necessary for testing)
    await _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id1,
        OrderStatus.kTransporting,
    )
    event = master_tp.next_call()['data']
    assert utils.parse_date_str(event['updated_ts']) == became_online_ts
    assert len(event['orders']) == 1
    order = event['orders'][0]
    assert order['alias'] == alias_id1
    assert order['status'] == OrderStatus.kTransporting
    assert utils.parse_date_str(
        order['event_ts'],
    ) == mocked_time.now().replace(tzinfo=pytz.utc)

    mocked_time.sleep(1)
    if not order_status_db_lookup_for_notification:
        await taxi_driver_status.invalidate_caches()

    # 4. order complete by backend
    await _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id1,
        OrderStatus.kComplete,
    )
    event = master_tp.next_call()['data']
    # there are no active orders
    # and status updated TS is now()
    assert not event['orders']
    assert utils.parse_date_str(
        event['updated_ts'],
    ) == mocked_time.now().replace(tzinfo=pytz.utc)
