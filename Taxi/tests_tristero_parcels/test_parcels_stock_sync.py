import pytest


@pytest.mark.suspend_periodic_tasks('parcels-stocks-sync-periodic')
@pytest.mark.parametrize('deffered_acceptence_enabled', [True, False])
async def test_basic(
        taxi_tristero_parcels,
        tristero_parcels_db,
        pgsql,
        mockserver,
        taxi_config,
        deffered_acceptence_enabled,
):
    """ Test that parcels-stocks-sync working properly """

    config_setting = taxi_config.get(
        'TRISTERO_PARCELS_DEFFERED_ACCEPTANCE_SETTINGS',
    )
    config_setting['enabled'] = deffered_acceptence_enabled
    taxi_config.set(
        TRISTERO_PARCELS_DEFFERED_ACCEPTANCE_SETTINGS=config_setting,
    )
    await taxi_tristero_parcels.invalidate_caches()

    tristero_parcels_db.flush_distlocks()

    statuses = [
        'reserved',
        'created',
        'expecting_delivery',
        'in_depot',
        'order_cancelled',
        'ready_for_delivery',
        'delivering',
        'delivered',
    ]

    parcels = []
    parcels_in_depot = []
    parcel_ordered = None

    with tristero_parcels_db as db:
        order = db.add_order(1, status='received')
        parcels.append(order.add_parcel(1, status='ordered'))
        for i, status in enumerate(statuses):
            parcels.append(order.add_parcel(i + 2, status=status))

        parcel_ordered = parcels[0]
        parcels_in_depot = parcels[1:]

    @mockserver.json_handler('/grocery-wms/api/external/products/v1/stocks')
    def mock_wms(request):
        response = {'code': 'OK', 'cursor': 'end', 'stocks': []}
        if not request.json['cursor']:
            for parcel in parcels:
                response['stocks'].append(
                    {
                        'count': 1,
                        'product_id': parcel.wms_id,
                        'shelf_type': 'parcel',
                        'store_id': order.depot_id,
                    },
                )
        return response

    await taxi_tristero_parcels.run_periodic_task(
        'parcels-stocks-sync-periodic',
    )
    assert mock_wms.times_called == 2

    assert len(parcels_in_depot) == len(statuses)
    for parcel in parcels_in_depot:
        parcel.update_from_db()
        assert parcel.status == 'in_depot'

    # ordered status is in depot already. wont update
    parcel_ordered.update_from_db()
    assert parcel_ordered.status == 'ordered'

    order.update_from_db()
    assert order.status == 'received'


@pytest.mark.suspend_periodic_tasks('parcels-stocks-sync-periodic')
async def test_bad_wms_response(
        taxi_tristero_parcels, tristero_parcels_db, pgsql, mockserver,
):
    """
    Test that parcels-stocks-sync works properly when wms responses some shit
    """

    tristero_parcels_db.flush_distlocks()

    with tristero_parcels_db as db:
        order = db.add_order(1)
        parcel_wrong1 = order.add_parcel(1, status='created')
        parcel_wrong2 = order.add_parcel(2, status='created')
        parcel_ok = order.add_parcel(3, status='created')

    @mockserver.json_handler('/grocery-wms/api/external/products/v1/stocks')
    def mock_wms(request):
        response = {'code': 'OK', 'cursor': 'end', 'stocks': []}
        if not request.json['cursor']:
            response['stocks'].append(
                {
                    'count': 1,
                    'product_id': parcel_wrong1.wms_id,
                    'shelf_type': 'store',  # wrong type
                    'store_id': order.depot_id,
                },
            )
            response['stocks'].append(
                {
                    'count': 2,  # wrong count
                    'product_id': parcel_wrong2.wms_id,
                    'shelf_type': 'parcel',
                    'store_id': order.depot_id,
                },
            )
            response['stocks'].append(
                {
                    'count': 1,
                    'product_id': parcel_ok.wms_id,
                    'shelf_type': 'parcel',
                    'store_id': order.depot_id,
                },
            )
        return response

    await taxi_tristero_parcels.run_periodic_task(
        'parcels-stocks-sync-periodic',
    )
    assert mock_wms.times_called == 2

    parcel_wrong1.update_from_db()
    assert parcel_wrong1.status == 'created'
    assert parcel_ok.in_stock_quantity == 0
    parcel_wrong2.update_from_db()
    assert parcel_wrong2.status == 'created'
    assert parcel_ok.in_stock_quantity == 0
    parcel_ok.update_from_db()
    assert parcel_ok.status == 'in_depot'
    assert parcel_ok.in_stock_quantity == 1

    order.update_from_db()
    assert order.status == 'received_partialy'


@pytest.mark.suspend_periodic_tasks('parcels-stocks-sync-periodic')
async def test_update_parcel_quantity(
        taxi_tristero_parcels, tristero_parcels_db, pgsql, mockserver,
):
    """ Test that parcels-stocks-sync updates in-stock-quantity of parcel """

    tristero_parcels_db.flush_distlocks()

    with tristero_parcels_db as db:
        order = db.add_order(1)
        parcel_to_depot = order.add_parcel(
            1, status='created', in_stock_quantity=0,
        )
        parcel_to_deliver = order.add_parcel(
            2, status='ordered', in_stock_quantity=1,
        )

    @mockserver.json_handler('/grocery-wms/api/external/products/v1/stocks')
    def mock_wms(request):
        response = {'code': 'OK', 'cursor': 'end', 'stocks': []}
        if not request.json['cursor']:
            response['stocks'].append(
                {
                    'count': 1,
                    'product_id': parcel_to_depot.wms_id,
                    'shelf_type': 'parcel',
                    'store_id': order.depot_id,
                },
            )
            response['stocks'].append(
                {
                    'count': 0,
                    'product_id': parcel_to_deliver.wms_id,
                    'shelf_type': 'parcel',
                    'store_id': order.depot_id,
                },
            )
        return response

    await taxi_tristero_parcels.run_periodic_task(
        'parcels-stocks-sync-periodic',
    )
    assert mock_wms.times_called == 2

    parcel_to_depot.update_from_db()
    assert parcel_to_depot.in_stock_quantity == 1
    parcel_to_deliver.update_from_db()
    assert parcel_to_deliver.in_stock_quantity == 0


@pytest.mark.suspend_periodic_tasks('parcels-stocks-sync-periodic')
async def test_stocks_sync_statistics(
        taxi_tristero_parcels,
        taxi_tristero_parcels_monitor,
        tristero_parcels_db,
        pgsql,
        mockserver,
):
    """ Test that parcels-stocks-sync collects metrics """

    tristero_parcels_db.flush_distlocks()

    await taxi_tristero_parcels.tests_control(reset_metrics=True)

    with tristero_parcels_db as db:
        order = db.add_order(1)
        parcel_to_depot = order.add_parcel(1, status='created')  # count=1, Ok
        parcel_to_user = order.add_parcel(
            2, status='in_depot',
        )  # count=0, Wrong statuses!
        parcel_ordered = order.add_parcel(
            3, status='ordered',
        )  # count=0, Ok (parcel status=ordered)
        parcel_to_dp_wrong = order.add_parcel(
            4, status='created',
        )  # count=0, Wrong statuses!

        order2 = db.add_order(2, status='cancelled')
        parcel_to_depot2 = order2.add_parcel(
            1, status='created',
        )  # count=1, Ok
        parcel_to_user2 = order2.add_parcel(
            2, status='in_depot',
        )  # count=0, Ok (order status=cancelled)
        parcel_ordered2 = order2.add_parcel(
            3, status='ordered',
        )  # count=0, Ok (both statuses are ok)

    @mockserver.json_handler('/grocery-wms/api/external/products/v1/stocks')
    def mock_wms(request):
        # словарь, в который будем собирать ответ
        response = {'code': 'OK', 'cursor': 'end', 'stocks': []}
        if not request.json['cursor']:
            # order 1
            response['stocks'].append(
                {
                    'count': 1,
                    'product_id': parcel_to_depot.wms_id,
                    'shelf_type': 'parcel',
                    'store_id': order.depot_id,
                },
            )
            response['stocks'].append(
                {
                    'count': 0,
                    'product_id': parcel_to_user.wms_id,
                    'shelf_type': 'parcel',
                    'store_id': order.depot_id,
                },
            )
            response['stocks'].append(
                {
                    'count': 0,
                    'product_id': parcel_ordered.wms_id,
                    'shelf_type': 'parcel',
                    'store_id': order.depot_id,
                },
            )
            response['stocks'].append(
                {
                    'count': 0,
                    'product_id': parcel_to_dp_wrong.wms_id,
                    'shelf_type': 'parcel',
                    'store_id': order.depot_id,
                },
            )

            # order 2
            response['stocks'].append(
                {
                    'count': 1,
                    'product_id': parcel_to_depot2.wms_id,
                    'shelf_type': 'parcel',
                    'store_id': order2.depot_id,
                },
            )
            response['stocks'].append(
                {
                    'count': 0,
                    'product_id': parcel_to_user2.wms_id,
                    'shelf_type': 'parcel',
                    'store_id': order2.depot_id,
                },
            )
            response['stocks'].append(
                {
                    'count': 0,
                    'product_id': parcel_ordered2.wms_id,
                    'shelf_type': 'parcel',
                    'store_id': order2.depot_id,
                },
            )
        return response

    await taxi_tristero_parcels.run_periodic_task(
        'parcels-stocks-sync-periodic',
    )
    assert mock_wms.times_called == 2

    statistics = await taxi_tristero_parcels_monitor.get_metric(
        'stocks_sync_statistics',
    )
    assert statistics['inconsistent_stocks'] == 2


async def test_order_cancelled_and_in_depot_states_race_condition(
        taxi_tristero_parcels, tristero_parcels_db, mockserver,
):
    """ The test case:
     - Get parcel quantity by means of WMS cursor (returns only changes)
     - The parcel is ordered
     - The order was canceled before the parcel left the warehouse
     - The status of the parcel should become "in_depot"
    """

    # Initial state after sync of stocks with WMS
    with tristero_parcels_db as db:
        order = db.add_order(1)
        parcel_in_stock = order.add_parcel(
            1, status='ordered', in_stock_quantity=1,
        )
        parcel_gone = order.add_parcel(
            2, status='ordered', in_stock_quantity=0,
        )

    await taxi_tristero_parcels.invalidate_caches()

    # Cancel order
    response = await taxi_tristero_parcels.put(
        '/internal/v1/parcels/v1/set-state',
        json={
            'parcel_wms_ids': [
                parcel_in_stock.product_key,
                parcel_gone.product_key,
            ],
            'state': 'order_cancelled',
            'state_meta': {'some_id': '1122334455'},
        },
    )
    assert response.status_code == 200
    assert set(response.json()['parcel_wms_ids']) == {
        parcel_in_stock.product_key,
        parcel_gone.product_key,
    }

    parcel_in_stock.update_from_db()
    parcel_gone.update_from_db()
    assert parcel_in_stock.status == 'in_depot'
    assert parcel_gone.status == 'order_cancelled'


async def test_order_return_to_vendor(
        taxi_tristero_parcels, tristero_parcels_db, mockserver,
):
    """ Parcel status should be set to returned_to_vendor
    if order state is cancelled and we got 0 quantity from WMS
    """
    tristero_parcels_db.flush_distlocks()

    with tristero_parcels_db as db:
        order = db.add_order(1, status='cancelled')
        parcel = order.add_parcel(1, status='in_depot', in_stock_quantity=1)

    @mockserver.json_handler('/grocery-wms/api/external/products/v1/stocks')
    def mock_wms(request):
        response = {'code': 'OK', 'cursor': 'end', 'stocks': []}
        if not request.json['cursor']:
            response['stocks'].append(
                {
                    'count': 0,
                    'product_id': parcel.wms_id,
                    'shelf_type': 'parcel',
                    'store_id': order.depot_id,
                },
            )
        return response

    await taxi_tristero_parcels.run_periodic_task(
        'parcels-stocks-sync-periodic',
    )

    parcel.update_from_db()
    assert mock_wms.times_called == 2
    assert parcel.status == 'returned_to_vendor'


@pytest.mark.suspend_periodic_tasks('parcels-stocks-sync-periodic')
@pytest.mark.parametrize(
    'deffered_acceptence_enabled,parcel_status,order_status,rows_count',
    [(True, 'created', 'reserved', 1), (False, 'in_depot', 'received', 0)],
)
async def test_deffered_acceptance_on_demand(
        taxi_tristero_parcels,
        tristero_parcels_db,
        pgsql,
        mockserver,
        taxi_config,
        deffered_acceptence_enabled,
        parcel_status,
        order_status,
        rows_count,
):
    """
    not parcels nor order status should change if
    order is in reserved state and
    deffered_acceptence_enabled is true
    """

    config_setting = taxi_config.get(
        'TRISTERO_PARCELS_DEFFERED_ACCEPTANCE_SETTINGS',
    )
    config_setting['enabled'] = deffered_acceptence_enabled
    taxi_config.set(
        TRISTERO_PARCELS_DEFFERED_ACCEPTANCE_SETTINGS=config_setting,
    )
    await taxi_tristero_parcels.invalidate_caches()

    tristero_parcels_db.flush_distlocks()

    with tristero_parcels_db as db:
        order = db.add_order(1, status='reserved')
        parcel = order.add_parcel(1, status='created')

    @mockserver.json_handler('/grocery-wms/api/external/products/v1/stocks')
    def mock_wms(request):
        response = {'code': 'OK', 'cursor': 'end', 'stocks': []}
        if not request.json['cursor']:
            response['stocks'].append(
                {
                    'count': 1,
                    'product_id': parcel.wms_id,
                    'shelf_type': 'parcel',
                    'store_id': order.depot_id,
                },
            )
        return response

    await taxi_tristero_parcels.run_periodic_task(
        'parcels-stocks-sync-periodic',
    )
    assert mock_wms.times_called == 2

    parcel.update_from_db()
    assert parcel.status == parcel_status

    order.update_from_db()
    assert order.status == order_status

    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(
        """SELECT item_id, accepted, new_acceptance_time
        FROM parcels.deffered_acceptance""",
    )
    rows = cursor.fetchall()
    assert len(rows) == rows_count
    if rows_count > 0:
        assert rows[0][0] == parcel.item_id
        assert rows[0][1] is False
        assert rows[0][2] is None


@pytest.mark.suspend_periodic_tasks('parcels-stocks-sync-periodic')
@pytest.mark.parametrize(
    'has_timeslot,parcel_status,order_status,rows_count',
    [(False, 'created', 'reserved', 1), (True, 'in_depot', 'received', 0)],
)
async def test_deffered_acceptance_timeslot(
        taxi_tristero_parcels,
        tristero_parcels_db,
        pgsql,
        mockserver,
        taxi_config,
        has_timeslot,
        parcel_status,
        order_status,
        rows_count,
):
    """
    parcels and order status should change if
    order has timeslot even if deffered_acceptence_enabled is true
    ans orders state is reserved
    """

    config_setting = taxi_config.get(
        'TRISTERO_PARCELS_DEFFERED_ACCEPTANCE_SETTINGS',
    )
    config_setting['enabled'] = True
    taxi_config.set(
        TRISTERO_PARCELS_DEFFERED_ACCEPTANCE_SETTINGS=config_setting,
    )
    await taxi_tristero_parcels.invalidate_caches()

    tristero_parcels_db.flush_distlocks()

    with tristero_parcels_db as db:
        if has_timeslot:
            order = db.add_order(
                1,
                status='reserved',
                timeslot_start='2021-07-15T18:00:00+03:00',
            )
        else:
            order = db.add_order(1, status='reserved')
        parcel = order.add_parcel(1, status='created')

    @mockserver.json_handler('/grocery-wms/api/external/products/v1/stocks')
    def mock_wms(request):
        response = {'code': 'OK', 'cursor': 'end', 'stocks': []}
        if not request.json['cursor']:
            response['stocks'].append(
                {
                    'count': 1,
                    'product_id': parcel.wms_id,
                    'shelf_type': 'parcel',
                    'store_id': order.depot_id,
                },
            )
        return response

    await taxi_tristero_parcels.run_periodic_task(
        'parcels-stocks-sync-periodic',
    )
    assert mock_wms.times_called == 2

    parcel.update_from_db()
    assert parcel.status == parcel_status

    order.update_from_db()
    assert order.status == order_status

    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(
        """SELECT item_id, accepted, new_acceptance_time
        FROM parcels.deffered_acceptance""",
    )
    rows = cursor.fetchall()
    assert len(rows) == rows_count
    if rows_count > 0:
        assert rows[0][0] == parcel.item_id
        assert rows[0][1] is False
        assert rows[0][2] is None


@pytest.mark.suspend_periodic_tasks('parcels-stocks-sync-periodic')
@pytest.mark.parametrize(
    'parcel_depot_id,parcel_status,order_status,rows_count',
    [('1', 'created', 'reserved', 1), ('2', 'in_depot', 'received', 0)],
)
async def test_deffered_acceptance_depot_id(
        taxi_tristero_parcels,
        tristero_parcels_db,
        pgsql,
        mockserver,
        taxi_config,
        parcel_depot_id,
        parcel_status,
        order_status,
        rows_count,
):
    """
    if depot_ids is not empty then deffered_acceptance
    should work only in specified depot_ids
    """

    config_setting = taxi_config.get(
        'TRISTERO_PARCELS_DEFFERED_ACCEPTANCE_SETTINGS',
    )
    config_setting['enabled'] = True
    config_setting['depot_ids'] = ['1']
    taxi_config.set(
        TRISTERO_PARCELS_DEFFERED_ACCEPTANCE_SETTINGS=config_setting,
    )
    await taxi_tristero_parcels.invalidate_caches()

    tristero_parcels_db.flush_distlocks()

    with tristero_parcels_db as db:
        order = db.add_order(1, status='reserved', depot_id=parcel_depot_id)
        parcel = order.add_parcel(1, status='created')

    @mockserver.json_handler('/grocery-wms/api/external/products/v1/stocks')
    def mock_wms(request):
        response = {'code': 'OK', 'cursor': 'end', 'stocks': []}
        if not request.json['cursor']:
            response['stocks'].append(
                {
                    'count': 1,
                    'product_id': parcel.wms_id,
                    'shelf_type': 'parcel',
                    'store_id': order.depot_id,
                },
            )
        return response

    await taxi_tristero_parcels.run_periodic_task(
        'parcels-stocks-sync-periodic',
    )
    assert mock_wms.times_called == 2

    parcel.update_from_db()
    assert parcel.status == parcel_status

    order.update_from_db()
    assert order.status == order_status

    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(
        """SELECT item_id, accepted, new_acceptance_time
        FROM parcels.deffered_acceptance""",
    )
    rows = cursor.fetchall()
    assert len(rows) == rows_count
    if rows_count > 0:
        assert rows[0][0] == parcel.item_id
        assert rows[0][1] is False
        assert rows[0][2] is None


@pytest.mark.suspend_periodic_tasks('parcels-stocks-sync-periodic')
async def test_deffered_acceptance_repeated(
        taxi_tristero_parcels,
        tristero_parcels_db,
        pgsql,
        mockserver,
        taxi_config,
):
    """
    repeated acceptances should be ignored
    """

    config_setting = taxi_config.get(
        'TRISTERO_PARCELS_DEFFERED_ACCEPTANCE_SETTINGS',
    )
    config_setting['enabled'] = True
    config_setting['depot_ids'] = []
    taxi_config.set(
        TRISTERO_PARCELS_DEFFERED_ACCEPTANCE_SETTINGS=config_setting,
    )
    await taxi_tristero_parcels.invalidate_caches()

    tristero_parcels_db.flush_distlocks()

    with tristero_parcels_db as db:
        order = db.add_order(1, status='reserved')
        parcel = order.add_parcel(1, status='created')

    times_called = 0

    @mockserver.json_handler('/grocery-wms/api/external/products/v1/stocks')
    def mock_wms(request):
        nonlocal times_called
        response = {'code': 'OK', 'cursor': 'end', 'stocks': []}
        if times_called < 3:
            response['stocks'].append(
                {
                    'count': (times_called + 1) % 2,
                    'product_id': parcel.wms_id,
                    'shelf_type': 'parcel',
                    'store_id': order.depot_id,
                },
            )
        times_called += 1
        return response

    await taxi_tristero_parcels.run_periodic_task(
        'parcels-stocks-sync-periodic',
    )
    assert mock_wms.times_called == 4

    parcel.update_from_db()
    assert parcel.status == 'created'

    order.update_from_db()
    assert order.status == 'reserved'

    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(
        """SELECT item_id, accepted, new_acceptance_time
        FROM parcels.deffered_acceptance""",
    )
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0][0] == parcel.item_id
    assert rows[0][1] is False
    assert rows[0][2] is None
