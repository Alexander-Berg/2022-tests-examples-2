# pylint: disable=import-error
import datetime

from geobus_tools import geobus  # noqa: F401 C5521
import pytest


NOW = datetime.datetime(2001, 9, 9, 1, 46, 39)


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.pgsql(
    'combo_contractors',
    files=[
        'create_contractor_partitions.sql',
        'contractors.sql',
        'orders.sql',
        'order_match_rule.sql',
    ],
)
@pytest.mark.config(ROUTER_SELECT=[{'routers': ['linear-fallback']}])
@pytest.mark.now(f'{NOW:%Y-%m-%d %H:%M:%S%z}')
async def test_contractors_updater(
        taxi_combo_contractors, load_json, testpoint, pgsql, redis_store,
):
    @testpoint('geobus-positions_payload_processed')
    def geobus_payload_processed(data):
        pass

    await taxi_combo_contractors.enable_testpoints()

    positions = load_json('positions.json')
    redis_store.publish(
        'channel:yaga:edge_positions',
        geobus.serialize_edge_positions_v2(positions, NOW),
    )

    await geobus_payload_processed.wait_call()

    await taxi_combo_contractors.run_task('distlock/contractors-updater')

    cursor = pgsql['combo_contractors'].cursor()
    cursor.execute(
        """
        select
          chunk_id,
          dbid_uuid,
          to_char(updated, 'DD Mon YYYY HH:MI:SS') updated,
          has_chain_parent,
          orders->'orders' orders
        from
          combo_contractors.contractor
        """,
    )
    colnames = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    rows = [dict(zip(colnames, row)) for row in rows]

    # sort orders array of each row
    drivers = []
    for row in rows:
        driver = {}
        for key, value in row.items():
            if key == 'orders':
                driver[key] = sorted(value, key=lambda x: x['order_id'])
            else:
                driver[key] = value
        drivers.append(driver)

    expected_redis = {
        'order_id0': b'{"t":640,"d":4447.803189385088}',
        'order_id5': None,
        'order_id6': None,
    }
    new_info = b'{"t":990,"d":44.803189385088}'

    for order_id, expected_value in expected_redis.items():
        redis_key = 'BaseOrderRoute:' + order_id
        res = redis_store.get(redis_key)
        assert expected_value == res
        if order_id == 'order_id0':
            redis_store.set(redis_key, new_info)

    assert sorted(drivers, key=lambda x: x['dbid_uuid']) == load_json(
        'expected_contractors.json',
    )

    info_check = 0

    @testpoint('get_contractor_route_info')
    def geobus_payload_processed(data):
        nonlocal info_check
        if data['d'] == 44.803189385088:
            info_check += 1
            assert data['t'] == 990

    await taxi_combo_contractors.enable_testpoints()
    await taxi_combo_contractors.run_task('distlock/contractors-updater')
    assert info_check == 1


@pytest.mark.parametrize(
    'testcase',
    [
        'first_order',
        'chain_transporting',
        'chain_one_finished',
        'combo_and_old',
        'legacy_driving',
        'legacy_transporting',
    ],
)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.pgsql(
    'combo_contractors',
    files=['create_contractor_partitions.sql', 'order_match_rule.sql'],
)
@pytest.mark.config(ROUTER_SELECT=[{'routers': ['linear-fallback']}])
@pytest.mark.now(f'{NOW:%Y-%m-%d %H:%M:%S%z}')
async def test_combo_info(
        taxi_combo_contractors,
        load_json,
        load,
        testpoint,
        pgsql,
        redis_store,
        testcase,
):
    cursor = pgsql['combo_contractors'].cursor()
    cursor.execute(load(f'combo_info_{testcase}.sql'))

    @testpoint('geobus-positions_payload_processed')
    def geobus_payload_processed(data):
        pass

    await taxi_combo_contractors.enable_testpoints()

    positions = load_json('positions.json')
    redis_store.publish(
        'channel:yaga:edge_positions',
        geobus.serialize_edge_positions_v2(positions, NOW),
    )

    await geobus_payload_processed.wait_call()

    await taxi_combo_contractors.run_task('distlock/contractors-updater')

    cursor = pgsql['combo_contractors'].cursor()
    cursor.execute(
        """
        select
          combo_info
        from
          combo_contractors.contractor
        """,
    )
    colnames = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    combo_info = [dict(zip(colnames, row)) for row in rows]

    assert combo_info == load_json(f'combo_info_{testcase}.json')


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.pgsql(
    'combo_contractors',
    files=[
        'create_contractor_partitions.sql',
        'contractors.sql',
        'orders.sql',
        'order_match_rule.sql',
    ],
)
@pytest.mark.config(
    ROUTER_SELECT=[
        {'routers': ['linear-fallback']},
        {
            'routers': ['tigraph'],
            'target': 'tigraph',
            'service': 'combo-contractors',
        },
    ],
    ROUTER_TIGRAPH_USERVICES_ENABLED=True,
)
@pytest.mark.now(f'{NOW:%Y-%m-%d %H:%M:%S%z}')
@pytest.mark.parametrize('use_tigraph', [True, False])
async def test_contractors_updater_router_selection(
        taxi_combo_contractors,
        load_json,
        testpoint,
        redis_store,
        mockserver,
        experiments3,
        use_tigraph,
):
    @testpoint('geobus-positions_payload_processed')
    def geobus_payload_processed(data):
        pass

    @mockserver.handler('tigraph-router/route')
    async def tigraph_router_handler(request):
        raise mockserver.TimeoutError()

    if use_tigraph:
        experiments3.add_experiments_json(
            load_json('experiments3_routing_settings.json'),
        )

    await taxi_combo_contractors.enable_testpoints()

    positions = load_json('positions.json')
    redis_store.publish(
        'channel:yaga:edge_positions',
        geobus.serialize_edge_positions_v2(positions, NOW),
    )

    await geobus_payload_processed.wait_call()

    await taxi_combo_contractors.run_task('distlock/contractors-updater')

    expected_times_called = 24 if use_tigraph else 0
    assert tigraph_router_handler.times_called == expected_times_called
