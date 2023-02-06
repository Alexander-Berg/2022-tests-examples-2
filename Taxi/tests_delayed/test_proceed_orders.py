import copy
import datetime
import json

import bson
import pytest

from tests_delayed import mock_utils


@pytest.mark.config(
    DELAYED_ENABLED=True,
    DELAYED_DISPATCHED_ORDERS_STAY_SEC=1,
    DELAYED_ORDERS_CONFIGURATION={
        '__default__': [
            {
                'time_until_due_min': 30,
                'needed_drivers_count': 20,
                'maximum_route_time_min': 10,
            },
            {
                'time_until_due_min': 20,
                'needed_drivers_count': 10,
                'maximum_route_time_min': 10,
            },
            {
                'time_until_due_min': 5,
                'needed_drivers_count': 0,
                'maximum_route_time_min': 0,
            },
        ],
    },
)
async def test_full_cycle(
        taxi_delayed, driver_eta, archive, pgsql, mocked_time, mockserver,
):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/start-lookup',
    )
    def mock_order_core(req):
        assert req.args['order_id'] == 'order_id_1'
        body = bson.BSON.decode(req.get_data())
        assert body == {'filter': {'status': 'pending'}}
        return {}

    # Setting up mocks
    archive.set_order_procs(
        [
            {
                # This order has to be dispatched at third
                # processing call, due to failed table requirements
                '_id': 'order_id_1',
                'order': {
                    '_id': 'order_id_1',
                    'created': datetime.datetime(2019, 3, 18),
                    'request': {
                        'due': datetime.datetime(2019, 3, 18, 5, 0, 0),
                    },
                },
            },
        ],
    )

    driver_eta.set_drivers_for_order(
        {
            # first table row configuration
            'order_id_1': mock_utils.build_eta_drivers(20, 10),
        },
    )

    now_time = datetime.datetime(2019, 3, 18, 00, 00, 00)
    mocked_time.set(now_time)
    await taxi_delayed.tests_control()

    # Adding order for delayed processing
    added_time = copy.deepcopy(now_time)

    response = await taxi_delayed.post(
        'v1/add',
        json={'order_id': 'order_id_1', 'link_id': 'test_link'},
        headers={'X-YaRequestId': 'test_link'},
    )
    assert response.status_code == 200, response.content

    # Checking data in database
    delayed_orders = mock_utils.validate_items_count_in_db(
        delayed_orders=1, dispatched_orders=0, pgsql=pgsql,
    )[0]

    assert delayed_orders == [
        mock_utils.create_order_entry(
            order_id='order_id_1',
            due=datetime.datetime(2019, 3, 18, 5, 0),
            link_id='test_link',
            is_processing=False,
            last_processing=now_time,
            is_processing_change_time=added_time,
            zone='moscow',
            tariff='econom',
        ),
    ]

    # 2019-03-18 00:05:00
    old_now = copy.deepcopy(now_time)
    now_time += datetime.timedelta(minutes=5)

    # Running processing job
    await mock_utils.successful_processing_run(taxi_delayed)
    assert mock_order_core.times_called == 0

    # pylint: disable=len-as-condition
    assert len(driver_eta.requests) == 0

    # Checking data in database
    delayed_orders = mock_utils.validate_items_count_in_db(
        delayed_orders=1, dispatched_orders=0, pgsql=pgsql,
    )[0]

    assert delayed_orders == [
        mock_utils.create_order_entry(
            order_id='order_id_1',
            due=datetime.datetime(2019, 3, 18, 5, 0),
            link_id='test_link',
            is_processing=False,
            last_processing=old_now,
            is_processing_change_time=added_time,
            zone='moscow',
            tariff='econom',
        ),
    ]

    # Moving closer to run
    # 2019-03-18 04:30:00
    now_time += datetime.timedelta(hours=4, minutes=25)
    mocked_time.set(now_time)
    await taxi_delayed.tests_control()

    # Running processing job
    await mock_utils.successful_processing_run(taxi_delayed)
    assert mock_order_core.times_called == 0

    expected_eta_request = {
        'order_id': 'order_id_1',
        'experiments': [],
        'requirements': {
            'animaltransport': True,
            'capacity': [1],
            'cargo_loaders': [1, 1],
            'childchair_moscow': 7,
            'creditcard': True,
            'passengers_count': 1,
        },
        'intent': 'eta-delayed',
        'point': [11.111111, 22.222222],
        'zone_id': 'moscow',
        'classes': ['vip', 'econom'],
        'destination': [33.333333, 44.444444],
        'provide_candidates': True,
        'order': {
            'virtual_tariffs': [
                {
                    'class': 'econom',
                    'special_requirements': [{'id': 'food_delivery'}],
                },
            ],
        },
        'extended_radius': True,
        'airport': False,
    }

    assert driver_eta.requests[-1] == expected_eta_request

    delayed_orders = mock_utils.validate_items_count_in_db(
        delayed_orders=1, dispatched_orders=0, pgsql=pgsql,
    )[0]

    # Checking status
    response = await taxi_delayed.post('v1/status', {'order_id': 'order_id_1'})
    assert response.status_code == 200, response.content
    assert json.loads(response.content) == {
        'dispatched': False,
        'due': '2019-03-18T05:00:00+00:00',
        'last_update_time': '2019-03-18T04:30:00+00:00',
    }

    assert delayed_orders == [
        mock_utils.create_order_entry(
            order_id='order_id_1',
            due=datetime.datetime(2019, 3, 18, 5, 0),
            link_id='test_link',
            is_processing=False,
            last_processing=now_time,
            is_processing_change_time=datetime.datetime(2019, 3, 18, 0, 0),
            zone='moscow',
            tariff='econom',
        ),
    ]

    # Reconfiguring client mock to fail conditions
    driver_eta.set_drivers_for_order(
        {
            # bad for second table row configuration
            'order_id_1': mock_utils.build_eta_drivers(15, 15),
        },
    )

    # Moving closer to run
    # 2019-03-18 04:40:00
    now_time += datetime.timedelta(minutes=10)
    mocked_time.set(now_time)
    await taxi_delayed.tests_control()

    # Running processing job
    await mock_utils.successful_processing_run(taxi_delayed)

    # order_id_1 order was dispatched due to failed driver-eta request
    assert mock_order_core.times_called == 1

    expected_eta_request.update({'extended_radius': True})

    assert driver_eta.requests[-1] == expected_eta_request

    dispatched_orders = mock_utils.validate_items_count_in_db(
        delayed_orders=0, dispatched_orders=1, pgsql=pgsql,
    )[1]

    assert dispatched_orders == [
        mock_utils.create_dispatched_entry(
            order_id='order_id_1',
            due=datetime.datetime(2019, 3, 18, 5, 0),
            dispatched_at=now_time,
        ),
    ]

    await mock_utils.successful_clear_dispatched_run(taxi_delayed)
    mock_utils.validate_items_count_in_db(
        delayed_orders=0, dispatched_orders=1, pgsql=pgsql,
    )

    # Check status
    response = await taxi_delayed.post('v1/status', {'order_id': 'order_id_1'})
    assert response.status_code == 200, response.content
    assert json.loads(response.content) == {
        'dispatch_time': '2019-03-18T04:40:00+00:00',
        'dispatched': True,
        'due': '2019-03-18T05:00:00+00:00',
    }

    # Moving closer to dispatch order remove
    # 2019-03-18 05:01:00
    now_time += datetime.timedelta(minutes=21)  # 1 sec in configuration
    mocked_time.set(now_time)
    await taxi_delayed.tests_control()

    # Running clear job
    await mock_utils.successful_clear_dispatched_run(taxi_delayed)
    mock_utils.validate_items_count_in_db(
        delayed_orders=0, dispatched_orders=0, pgsql=pgsql,
    )


@pytest.mark.pgsql('delayed_orders', files=['failed_delayed_orders.sql'])
@pytest.mark.config(
    DELAYED_ENABLED=True,
    DELAYED_DISPATCHED_ORDERS_STAY_SEC=1,
    DELAYED_ORDERS_CONFIGURATION={
        '__default__': [
            {
                'time_until_due_min': 30,
                'needed_drivers_count': 20,
                'maximum_route_time_min': 10,
            },
            {
                'time_until_due_min': 20,
                'needed_drivers_count': 10,
                'maximum_route_time_min': 10,
            },
            {
                'time_until_due_min': 5,
                'needed_drivers_count': 1,
                'maximum_route_time_min': 0,
            },
        ],
    },
)
async def test_fail_fallback(
        taxi_delayed, driver_eta, archive, pgsql, mocked_time,
):
    # Setting up mocks
    orders_due = datetime.datetime(2019, 2, 3, 4, 0, 0)

    driver_eta.set_drivers_for_order(
        {
            # second table row configuration
            'delayed_order_id_1': mock_utils.build_eta_drivers(10, 10),
            'delayed_order_id_2': mock_utils.build_eta_drivers(10, 10),
        },
    )

    archive.set_order_procs(
        [
            {
                '_id': 'delayed_order_id_1',
                'order': {
                    '_id': 'delayed_order_id_1',
                    'created': datetime.datetime(2019, 2, 3),
                    'request': {'due': datetime.datetime(2019, 2, 3, 4, 0, 0)},
                },
            },
            {
                '_id': 'delayed_order_id_2',
                'order': {
                    '_id': 'delayed_order_id_2',
                    'created': datetime.datetime(2019, 2, 3),
                    'request': {'due': datetime.datetime(2019, 2, 3, 4, 0, 0)},
                },
            },
        ],
    )

    now_time = datetime.datetime(2019, 2, 3, 3, 45, 00)
    mocked_time.set(now_time)
    await taxi_delayed.tests_control()

    # Processing orders
    await mock_utils.successful_processing_run(taxi_delayed)

    delayed_orders = mock_utils.validate_items_count_in_db(
        delayed_orders=2, dispatched_orders=0, pgsql=pgsql,
    )[0]

    assert sorted(delayed_orders) == sorted(
        [
            mock_utils.create_order_entry(
                order_id='delayed_order_id_1',
                due=orders_due,
                link_id='link_1',
                is_processing=False,
                last_processing=now_time,
                is_processing_change_time=datetime.datetime(
                    2019, 2, 3, 0, 0, 0,
                ),
            ),
            mock_utils.create_order_entry(
                order_id='delayed_order_id_2',
                due=orders_due,
                link_id='link_2',
                is_processing=True,
                last_processing=now_time,
                is_processing_change_time=datetime.datetime(
                    2019, 2, 3, 3, 45, 0,
                ),
            ),
        ],
    )

    now_time += datetime.timedelta(minutes=15)
    mocked_time.set(now_time)
    await taxi_delayed.tests_control()

    driver_eta.set_drivers_for_order(
        {
            # last, impossible table row configuration
            'delayed_order_id_1': mock_utils.build_eta_drivers(10, 5),
            'delayed_order_id_2': mock_utils.build_eta_drivers(10, 5),
        },
    )

    # Time to dispatch both orders
    await mock_utils.successful_processing_run(taxi_delayed)

    mock_utils.validate_items_count_in_db(
        delayed_orders=0, dispatched_orders=2, pgsql=pgsql,
    )


@pytest.mark.pgsql('delayed_orders', files=['retry_in_client_error.sql'])
@pytest.mark.config(
    DELAYED_ENABLED=True,
    DELAYED_DISPATCHED_ORDERS_STAY_SEC=1,
    DELAYED_ORDERS_CONFIGURATION={
        '__default__': [
            {
                'time_until_due_min': 20,
                'needed_drivers_count': 20,
                'maximum_route_time_min': 10,
            },
        ],
    },
    DELAYED_DRIVER_ETA_CLIENT_QOS={
        '__default__': {'attempts': 5, 'timeout-ms': 200},
    },
)
async def test_retry_in_client_error(
        taxi_delayed, archive, mocked_time, mockserver,
):
    @mockserver.json_handler('/driver-eta/eta')
    def _eta(request):
        _eta.counter += 1
        return mockserver.make_response(json=None, status=500)

    _eta.counter = 0

    archive.set_order_procs(
        [
            {
                '_id': 'delayed_order_id_1',
                'order': {
                    '_id': 'delayed_order_id_1',
                    'created': datetime.datetime(2019, 2, 3),
                    'request': {'due': datetime.datetime(2019, 2, 3, 4, 0, 0)},
                },
            },
        ],
    )

    now_time = datetime.datetime(2019, 2, 3, 3, 45, 00)
    mocked_time.set(now_time)

    await taxi_delayed.tests_control()
    await mock_utils.successful_processing_run(taxi_delayed)

    assert _eta.counter == 5


@pytest.mark.config(
    DELAYED_ENABLED=True,
    DELAYED_DISPATCHED_ORDERS_STAY_SEC=1,
    DELAYED_ORDERS_CONFIGURATION={
        '__default__': [
            {
                'time_until_due_min': 30,
                'needed_drivers_count': 20,
                'maximum_route_time_min': 10,
            },
            {
                'time_until_due_min': 20,
                'needed_drivers_count': 10,
                'maximum_route_time_min': 10,
            },
            {
                'time_until_due_min': 5,
                'needed_drivers_count': 0,
                'maximum_route_time_min': 0,
            },
        ],
    },
)
@pytest.mark.parametrize(
    'predicate',
    [
        (  # cargo_ref_id
            {
                'init': {
                    'set': ['cargo_ref_id_value_1'],
                    'arg_name': 'cargo_ref_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            }
        ),
        (  # user_id
            {
                'init': {
                    'set': ['user_id_value_1'],
                    'arg_name': 'user_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            }
        ),
        (  # zone_name
            {
                'init': {
                    'set': ['zone_name_value_1'],
                    'arg_name': 'zone_name',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            }
        ),
        (  # corp_client_id
            {
                'init': {
                    'set': ['corp_client_id_value_1'],
                    'arg_name': 'corp_client_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            }
        ),
        (  # classes
            {
                'init': {
                    'arg_name': 'classes',
                    'set_elem_type': 'string',
                    'value': 'econom',
                },
                'type': 'contains',
            }
        ),
    ],
)
async def test_experiments_order_processing_delay(
        predicate,
        taxi_delayed,
        driver_eta,
        archive,
        pgsql,
        mocked_time,
        experiments3,
        mockserver,
):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/start-lookup',
    )
    def mock_order_core(req):
        assert req.args['order_id'] == 'order_id_1'
        body = bson.BSON.decode(req.get_data())
        assert body == {'filter': {'status': 'pending'}}
        return {}

    # Setting up mocks
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='delayed_settings_exp',
        consumers=['delayed/add'],
        clauses=[
            {
                'title': 'Enabled',
                'value': {
                    'delayed_settings': {'time_until_due_to_proceed_min': 22},
                },
                'predicate': copy.deepcopy(predicate),
            },
        ],
    )
    await taxi_delayed.invalidate_caches()
    #    raise RuntimeError(experiments3.__dict__)

    archive.set_order_procs(
        [
            {
                '_id': 'order_id_1',
                'order': {
                    '_id': 'order_id_1',
                    'nz': 'zone_name_value_1',
                    'user_id': 'user_id_value_1',
                    'created': datetime.datetime(2019, 3, 18),
                    'request': {
                        'due': datetime.datetime(2019, 3, 18, 5, 0, 0),
                        'cargo_ref_id': 'cargo_ref_id_value_1',
                        'corp': {'client_id': 'corp_client_id_value_1'},
                        'class': ['econom', 'business'],
                    },
                },
            },
        ],
    )

    driver_eta.set_drivers_for_order(
        {
            # Order must be dispatched in first iteration
            # but experiment value must delay it
            'order_id_1': mock_utils.build_eta_drivers(
                amount=5, total_time_min=10,
            ),
        },
    )

    now_time = datetime.datetime(2019, 3, 18, 00, 00, 00)
    mocked_time.set(now_time)
    await taxi_delayed.tests_control()

    # Adding order into delayed
    added_time = copy.deepcopy(now_time)

    response = await taxi_delayed.post(
        '/v1/add',
        json={'order_id': 'order_id_1', 'link_id': 'test_link'},
        headers={'X-YaRequestId': 'test_link'},
    )
    assert response.status_code == 200, response.content

    # Checking data in database
    delayed_orders = mock_utils.validate_items_count_in_db(
        delayed_orders=1, dispatched_orders=0, pgsql=pgsql,
    )[0]

    assert delayed_orders == [
        mock_utils.create_order_entry(
            order_id='order_id_1',
            due=datetime.datetime(2019, 3, 18, 5, 0),
            link_id='test_link',
            is_processing=False,
            last_processing=now_time,
            is_processing_change_time=added_time,
            additional_properties={
                'settings': {'time_until_due_to_proceed_min': 22},
            },
            zone='zone_name_value_1',
            tariff='business',
        ),
    ]

    # 2019-03-18 04:35:00
    now_time += datetime.timedelta(hours=4, minutes=35)
    mocked_time.set(now_time)
    await taxi_delayed.tests_control()

    # Running processing jobs
    await mock_utils.successful_processing_run(taxi_delayed)
    assert mock_order_core.times_called == 0

    # 2019-03-18 04:38:00
    now_time += datetime.timedelta(hours=0, minutes=3)
    mocked_time.set(now_time)
    await taxi_delayed.tests_control()

    # Running processing jobs
    await mock_utils.successful_processing_run(taxi_delayed)
    assert mock_order_core.times_called == 1


@pytest.mark.config(
    DELAYED_ENABLED=True,
    DELAYED_DISPATCHED_ORDERS_STAY_SEC=1,
    DELAYED_ORDERS_CONFIGURATION={
        '__default__': [
            {
                'time_until_due_min': 30,
                'needed_drivers_count': 20,
                'maximum_route_time_min': 10,
            },
            {
                'time_until_due_min': 20,
                'needed_drivers_count': 10,
                'maximum_route_time_min': 10,
            },
            {
                'time_until_due_min': 5,
                'needed_drivers_count': 0,
                'maximum_route_time_min': 0,
            },
        ],
    },
)
@pytest.mark.parametrize(
    'predicate',
    [
        (  # cargo_ref_id
            {
                'init': {
                    'set': ['cargo_ref_id_value_1'],
                    'arg_name': 'cargo_ref_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            }
        ),
        (  # user_id
            {
                'init': {
                    'set': ['user_id_value_1'],
                    'arg_name': 'user_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            }
        ),
        (  # zone_name
            {
                'init': {
                    'set': ['zone_name_value_1'],
                    'arg_name': 'zone_name',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            }
        ),
        (  # corp_client_id
            {
                'init': {
                    'set': ['corp_client_id_value_1'],
                    'arg_name': 'corp_client_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            }
        ),
        (  # classes
            {
                'init': {
                    'arg_name': 'classes',
                    'set_elem_type': 'string',
                    'value': 'econom',
                },
                'type': 'contains',
            }
        ),
    ],
)
async def test_experiments_order_processing_guarantee_dispatch(
        predicate,
        taxi_delayed,
        driver_eta,
        archive,
        pgsql,
        mocked_time,
        experiments3,
        mockserver,
):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/start-lookup',
    )
    def mock_order_core(req):
        assert req.args['order_id'] == 'order_id_1'
        body = bson.BSON.decode(req.get_data())
        assert body == {'filter': {'status': 'pending'}}
        return {}

    # Setting up mocks
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='delayed_settings_exp',
        consumers=['delayed/add'],
        clauses=[
            {
                'title': 'Enabled',
                'value': {
                    'delayed_settings': {
                        'guarantee_dispatch_time_before_due_min': 26,
                    },
                },
                'predicate': copy.deepcopy(predicate),
            },
        ],
    )
    await taxi_delayed.invalidate_caches()

    archive.set_order_procs(
        [
            {
                '_id': 'order_id_1',
                'order': {
                    '_id': 'order_id_1',
                    'nz': 'zone_name_value_1',
                    'user_id': 'user_id_value_1',
                    'created': datetime.datetime(2019, 3, 18),
                    'request': {
                        'due': datetime.datetime(2019, 3, 18, 5, 0, 0),
                        'cargo_ref_id': 'cargo_ref_id_value_1',
                        'corp': {'client_id': 'corp_client_id_value_1'},
                        'class': ['econom', 'business'],
                    },
                },
            },
        ],
    )

    driver_eta.set_drivers_for_order(
        {
            # Order must be dispatched in first iteration
            # but experiment value must delay it
            'order_id_1': mock_utils.build_eta_drivers(
                amount=50, total_time_min=1,
            ),
        },
    )

    now_time = datetime.datetime(2019, 3, 18, 00, 00, 00)
    mocked_time.set(now_time)
    await taxi_delayed.tests_control()

    # Adding order into delayed
    added_time = copy.deepcopy(now_time)

    response = await taxi_delayed.post(
        '/v1/add',
        json={'order_id': 'order_id_1', 'link_id': 'test_link'},
        headers={'X-YaRequestId': 'test_link'},
    )
    assert response.status_code == 200, response.content

    # Checking data in database
    delayed_orders = mock_utils.validate_items_count_in_db(
        delayed_orders=1, dispatched_orders=0, pgsql=pgsql,
    )[0]

    assert delayed_orders == [
        mock_utils.create_order_entry(
            order_id='order_id_1',
            due=datetime.datetime(2019, 3, 18, 5, 0),
            link_id='test_link',
            is_processing=False,
            last_processing=now_time,
            is_processing_change_time=added_time,
            additional_properties={
                'settings': {'guarantee_dispatch_time_before_due_min': 26},
            },
            zone='zone_name_value_1',
            tariff='business',
        ),
    ]

    # 2019-03-18 04:30:00
    now_time += datetime.timedelta(hours=4, minutes=30)
    mocked_time.set(now_time)
    await taxi_delayed.tests_control()

    # Running processing jobs
    await mock_utils.successful_processing_run(taxi_delayed)
    assert mock_order_core.times_called == 0

    # 2019-03-18 04:35:00
    now_time += datetime.timedelta(minutes=5)
    mocked_time.set(now_time)
    await taxi_delayed.tests_control()

    # Running processing jobs
    await mock_utils.successful_processing_run(taxi_delayed)
    assert mock_order_core.times_called == 1


@pytest.mark.pgsql('delayed_orders', files=['failed_delayed_orders.sql'])
@pytest.mark.config(
    DELAYED_ENABLED=True,
    DELAYED_DISPATCHED_ORDERS_STAY_SEC=1,
    DELAYED_ORDERS_CONFIGURATION={
        '__default__': [
            {
                'time_until_due_min': 30,
                'needed_drivers_count': 20,
                'maximum_route_time_min': 10,
            },
            {
                'time_until_due_min': 20,
                'needed_drivers_count': 10,
                'maximum_route_time_min': 10,
            },
            {
                'time_until_due_min': 5,
                'needed_drivers_count': 1,
                'maximum_route_time_min': 0,
            },
        ],
    },
)
async def test_filter_orders_by_status(
        taxi_delayed, driver_eta, archive, pgsql, mocked_time,
):
    # Setting up mocks
    driver_eta.set_drivers_for_order(
        {
            'delayed_order_id_1': mock_utils.build_eta_drivers(10, 10),
            'delayed_order_id_2': mock_utils.build_eta_drivers(10, 10),
        },
    )

    # cancelled and finished orders with due in the past
    archive.set_order_procs(
        [
            {
                '_id': 'delayed_order_id_1',
                'order': {
                    '_id': 'delayed_order_id_1',
                    'created': datetime.datetime(2019, 2, 3),
                    'status': 'finished',
                    'request': {'due': datetime.datetime(2019, 2, 3, 4, 0, 0)},
                },
            },
            {
                '_id': 'delayed_order_id_2',
                'order': {
                    '_id': 'delayed_order_id_2',
                    'created': datetime.datetime(2019, 2, 3),
                    'status': 'cancelled',
                    'request': {'due': datetime.datetime(2019, 2, 3, 4, 0, 0)},
                },
            },
        ],
    )

    now_time = datetime.datetime(2019, 2, 3, 5, 0, 0)
    mocked_time.set(now_time)
    await taxi_delayed.tests_control()

    # Trying to proceed one of 2 orders
    # (cause one of them already marked as proceed)
    await mock_utils.successful_processing_run(taxi_delayed)
    mock_utils.validate_items_count_in_db(
        delayed_orders=0, dispatched_orders=0, pgsql=pgsql,
    )
