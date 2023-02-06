async def run_job(service, job):
    return await service.get('service/jobs/{}'.format(job))


async def successful_processing_run(taxi_delayed):
    await taxi_delayed.run_task('orders-processing')


async def successful_clear_dispatched_run(taxi_delayed):
    response = await run_job(taxi_delayed, 'clear-dispatched-orders')
    assert response.status_code == 200, response.content


async def successful_update_metrics_run(taxi_delayed):
    response = await run_job(taxi_delayed, 'update-metrics')
    assert response.status_code == 200, response.content


def execute_query(query, pgsql):
    pg_cursor = pgsql['delayed_orders'].cursor()
    pg_cursor.execute(query)
    return list(pg_cursor)


def databases_states(pgsql):
    delayed_orders = execute_query('SELECT * FROM orders.orders', pgsql)
    dispatched_orders = execute_query(
        'SELECT * FROM orders.dispatched_orders', pgsql,
    )
    return (
        delayed_orders if delayed_orders is not None else [],
        dispatched_orders if dispatched_orders is not None else [],
    )


def validate_items_count_in_db(delayed_orders, dispatched_orders, pgsql):
    delayed_db, dispatched_db = databases_states(pgsql)

    assert len(delayed_db) == delayed_orders
    assert len(dispatched_db) == dispatched_orders

    return delayed_db, dispatched_db


def build_drivers(amount, total_time_min):
    result = []

    for i in range(amount):
        result.append(
            {
                'dbid': '42',
                'uuid': 'driver_{}'.format(i),
                'position': [37.61901, 55.758671],
                'chain_info': {},
                'grade': 4,
                'status': 'free',
                'route_info': {
                    'time': total_time_min * 60,
                    'distance': 129,
                    'approximate': False,
                },
            },
        )

    return result


def build_eta_drivers(amount, total_time_min):
    result = []

    for i in range(amount):
        result.append(
            {
                'dbid': '42',
                'uuid': 'driver_{}'.format(i),
                'position': [37.61901, 55.758671],
                'chain_info': {},
                'grade': 4,
                'status': 'free',
                'route_info': {
                    'time': total_time_min * 60,
                    'distance': 129,
                    'approximate': False,
                },
            },
        )

    return result


def build_tracker_drivers(amount, total_time_min):
    result = []

    for i in range(amount):
        result.append(
            {
                'driver_id': 'driver_{}'.format(i),
                'route_info': {
                    'total_time': total_time_min * 60,
                    'total_distance': 0,
                },
            },
        )

    return result


def create_order_entry(
        order_id,
        due,
        link_id,
        is_processing,
        last_processing,
        is_processing_change_time,
        additional_properties=None,
        zone='',
        tariff='',
):
    if additional_properties is None:
        additional_properties = {}

    return (
        order_id,
        due,
        link_id,
        is_processing,
        last_processing,
        is_processing_change_time,
        additional_properties,
        zone,
        tariff,
    )


def create_dispatched_entry(order_id, due, dispatched_at):
    return (order_id, due, dispatched_at)
