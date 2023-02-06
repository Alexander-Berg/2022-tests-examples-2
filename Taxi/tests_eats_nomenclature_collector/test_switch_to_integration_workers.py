# pylint: disable=redefined-outer-name
import pytest


CORE_INTEGRATIONS_HANDLER = (
    '/eats-core-integrations/integrations/nomenclature-collector/v1/tasks'
)
INTEGRATION_WORKERS_HANDLER = '/eats-integration-workers/v1/tasks'
PLACE_GROUPS_REPLICA_HANDLER = '/eats-place-groups-replica/v1/tasks'


@pytest.mark.parametrize('send_only_to_iw_if_switched', [False, True])
@pytest.mark.parametrize(
    'periodics_type', ['schedulers', 'task_status_checker', 'db_cleanup'],
)
@pytest.mark.parametrize(
    """switch_settings, integration_2_settings, expected_place_ids_in_core,
       expected_place_ids_in_iw, expected_place_ids_in_pgr""",
    [
        pytest.param(
            # list of brands, switched to IW
            {'nomenclature': [], 'price': [], 'stock': [], 'availability': []},
            # brand switch to place-groups-replica or integration-workers
            {
                '2': {'service_name': 'eats-integration-workers'},
                '3': {'service_name': 'eats-place-groups-replica'},
            },
            # list of expected places in core
            {
                'nomenclature': ['1', '2', '3', '4', '5', '6'],
                'price': ['1', '2', '3', '4', '5', '6'],
                'stock': ['1', '2', '3', '4', '5', '6'],
                'availability': ['1', '2', '3', '4', '5', '6'],
            },
            # list of expected places in IW
            {'nomenclature': [], 'price': [], 'stock': [], 'availability': []},
            # list of expected places in PGR
            {'nomenclature': [], 'price': [], 'stock': [], 'availability': []},
            id='all_in_core',
        ),
        pytest.param(
            # list of brands, switched to IW
            {
                'nomenclature': ['2'],
                'price': [],
                'stock': [],
                'availability': [],
            },
            # brand switch to place-groups-replica or integration-workers
            {
                '2': {'service_name': 'eats-integration-workers'},
                '3': {'service_name': 'eats-place-groups-replica'},
            },
            # list of expected places in core
            {
                'nomenclature': ['1', '2', '5', '6'],
                'price': ['1', '2', '3', '4', '5', '6'],
                'stock': ['1', '2', '3', '4', '5', '6'],
                'availability': ['1', '2', '3', '4', '5', '6'],
            },
            # list of expected places in IW
            {
                'nomenclature': ['3', '4'],
                'price': [],
                'stock': [],
                'availability': [],
            },
            # list of expected places in PGR
            {'nomenclature': [], 'price': [], 'stock': [], 'availability': []},
            id='nomenclature_in_iw',
        ),
        pytest.param(
            # list of brands, switched to IW
            {
                'nomenclature': [],
                'price': ['2'],
                'stock': [],
                'availability': [],
            },
            # brand switch to place-groups-replica or integration-workers
            {
                '2': {'service_name': 'eats-integration-workers'},
                '3': {'service_name': 'eats-place-groups-replica'},
            },
            # list of expected places in core
            {
                'nomenclature': ['1', '2', '3', '4', '5', '6'],
                'price': ['1', '2', '5', '6'],
                'stock': ['1', '2', '3', '4', '5', '6'],
                'availability': ['1', '2', '3', '4', '5', '6'],
            },
            # list of expected places in IW
            {
                'nomenclature': [],
                'price': ['3', '4'],
                'stock': [],
                'availability': [],
            },
            # list of expected places in PGR
            {'nomenclature': [], 'price': [], 'stock': [], 'availability': []},
            id='price_in_iw',
        ),
        pytest.param(
            # list of brands, switched to IW
            {
                'nomenclature': [],
                'price': [],
                'stock': ['2'],
                'availability': [],
            },
            # brand switch to place-groups-replica or integration-workers
            {
                '2': {'service_name': 'eats-integration-workers'},
                '3': {'service_name': 'eats-place-groups-replica'},
            },
            # list of expected places in core
            {
                'nomenclature': ['1', '2', '3', '4', '5', '6'],
                'price': ['1', '2', '3', '4', '5', '6'],
                'stock': ['1', '2', '5', '6'],
                'availability': ['1', '2', '3', '4', '5', '6'],
            },
            # list of expected places in IW
            {
                'nomenclature': [],
                'price': [],
                'stock': ['3', '4'],
                'availability': [],
            },
            # list of expected places in PGR
            {'nomenclature': [], 'price': [], 'stock': [], 'availability': []},
            id='stock_in_iw',
        ),
        pytest.param(
            # list of brands, switched to IW
            {
                'nomenclature': [],
                'price': [],
                'stock': [],
                'availability': ['2'],
            },
            # brand switch to place-groups-replica or integration-workers
            {
                '2': {'service_name': 'eats-integration-workers'},
                '3': {'service_name': 'eats-place-groups-replica'},
            },
            # list of expected places in core
            {
                'nomenclature': ['1', '2', '3', '4', '5', '6'],
                'price': ['1', '2', '3', '4', '5', '6'],
                'stock': ['1', '2', '3', '4', '5', '6'],
                'availability': ['1', '2', '5', '6'],
            },
            # list of expected places in IW
            {
                'nomenclature': [],
                'price': [],
                'stock': [],
                'availability': ['3', '4'],
            },
            # list of expected places in PGR
            {'nomenclature': [], 'price': [], 'stock': [], 'availability': []},
            id='availability_in_iw',
        ),
        pytest.param(
            # list of brands, switched to IW
            {
                'nomenclature': [],
                'price': ['3'],
                'stock': ['2', '3'],
                'availability': ['2'],
            },
            # brand switch to place-groups-replica or integration-workers
            {
                '2': {'service_name': 'eats-integration-workers'},
                '3': {'service_name': 'eats-place-groups-replica'},
            },
            # list of expected places in core
            {
                'nomenclature': ['1', '2', '3', '4', '5', '6'],
                'price': ['1', '2', '3', '4'],
                'stock': ['1', '2'],
                'availability': ['1', '2', '5', '6'],
            },
            # list of expected places in IW
            {
                'nomenclature': [],
                'price': [],
                'stock': ['3', '4'],
                'availability': ['3', '4'],
            },
            # list of expected places in PGR
            {
                'nomenclature': [],
                'price': ['5', '6'],
                'stock': ['5', '6'],
                'availability': [],
            },
            id='partially_in_iw',
        ),
        pytest.param(
            # list of brands, switched to IW
            {
                'nomenclature': ['1', '2', '3'],
                'price': ['1', '2', '3'],
                'stock': ['1', '2', '3'],
                'availability': ['1', '2', '3'],
            },
            # brand switch to place-groups-replica or integration-workers
            {
                '1': {'service_name': 'eats-integration-workers'},
                '2': {'service_name': 'eats-integration-workers'},
                '3': {'service_name': 'eats-integration-workers'},
            },
            # list of expected places in core
            {'nomenclature': [], 'price': [], 'stock': [], 'availability': []},
            # list of expected places in IW
            {
                'nomenclature': ['1', '2', '3', '4', '5', '6'],
                'price': ['1', '2', '3', '4', '5', '6'],
                'stock': ['1', '2', '3', '4', '5', '6'],
                'availability': ['1', '2', '3', '4', '5', '6'],
            },
            # list of expected places in PGR
            {'nomenclature': [], 'price': [], 'stock': [], 'availability': []},
            id='all_in_iw',
        ),
        pytest.param(
            # list of brands, switched to IW
            {
                'nomenclature': ['1', '2', '3'],
                'price': ['1', '2', '3'],
                'stock': ['1', '2', '3'],
                'availability': ['1', '2', '3'],
            },
            # brand switch to place-groups-replica or integration-workers
            {'2': {'service_name': 'eats-place-groups-replica'}},
            # list of expected places in core
            {'nomenclature': [], 'price': [], 'stock': [], 'availability': []},
            # list of expected places in IW
            {'nomenclature': [], 'price': [], 'stock': [], 'availability': []},
            # list of expected places in PGR
            {
                'nomenclature': ['1', '2', '3', '4', '5', '6'],
                'price': ['1', '2', '3', '4', '5', '6'],
                'stock': ['1', '2', '3', '4', '5', '6'],
                'availability': ['1', '2', '3', '4', '5', '6'],
            },
            id='all_in_pgr',
        ),
    ],
)
async def test_switch_to_integration_workers(
        taxi_eats_nomenclature_collector,
        load_json,
        pgsql,
        mockserver,
        testpoint,
        taxi_config,
        # parametrized variables
        periodics_type,
        switch_settings,
        integration_2_settings,
        send_only_to_iw_if_switched,
        expected_place_ids_in_core,
        expected_place_ids_in_iw,
        expected_place_ids_in_pgr,
):
    # pylint: disable=unused-variable
    integrations_tasks = load_json('integrations_tasks.json')

    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_COLLECTOR_SWITCH_TO_INTEGRATION_WORKERS': {
                **switch_settings,
            },
            'EATS_NOMENCLATURE_COLLECTOR_INTEGRATION_2_SETTINGS': {
                '__default__': {'service_name': 'eats-place-groups-replica'},
                **integration_2_settings,
            },
            'EATS_NOMENCLATURE_COLLECTOR_TEMPORARY_CONFIGS': {
                'use_only_new_integration_if_switched': (
                    send_only_to_iw_if_switched
                ),
            },
        },
    )

    if periodics_type == 'schedulers':

        places_sent_to_core = set()
        places_sent_to_iw = set()
        places_sent_to_pgr = set()

        @mockserver.json_handler(CORE_INTEGRATIONS_HANDLER)
        def eats_core_integrations_post(request):
            if send_only_to_iw_if_switched:
                _assert_request_is_expected(
                    request.json, expected_place_ids_in_core,
                )
            places_sent_to_core.add(request.json['place_id'])
            return {
                'id': request.json['id'],
                'type': request.json['type'],
                'place_id': request.json['place_id'],
                'status': 'created',
                'data_file_url': '',
                'data_file_version': '',
                'reason': None,
            }

        @mockserver.json_handler(INTEGRATION_WORKERS_HANDLER)
        def eats_integration_workers_post(request):
            _assert_request_is_expected(request.json, expected_place_ids_in_iw)
            places_sent_to_iw.add(request.json['place_id'])
            return {
                'id': request.json['id'],
                'type': request.json['type'],
                'place_id': request.json['place_id'],
                'status': 'created',
                'data_file_url': '',
                'data_file_version': '',
                'reason': None,
            }

        @mockserver.json_handler(PLACE_GROUPS_REPLICA_HANDLER)
        def eats_place_groups_replica_post(request):
            _assert_request_is_expected(
                request.json, expected_place_ids_in_pgr,
            )
            places_sent_to_pgr.add(request.json['place_id'])
            return {
                'id': request.json['id'],
                'type': request.json['type'],
                'place_id': request.json['place_id'],
                'status': 'created',
                'data_file_url': '',
                'data_file_version': '',
                'reason': None,
            }

        @testpoint('eats_nomenclature_collector::nomenclature-scheduler')
        def handle_nomenclature_finished(arg):
            pass

        @testpoint('eats_nomenclature_collector::price-scheduler')
        def handle_price_finished(arg):
            pass

        @testpoint('eats_nomenclature_collector::stock-scheduler')
        def handle_stock_finished(arg):
            pass

        @testpoint('eats_nomenclature_collector::availability-scheduler')
        def handle_availability_finished(arg):
            pass

        await taxi_eats_nomenclature_collector.run_distlock_task(
            'nomenclature-scheduler',
        )
        handle_nomenclature_finished.next_call()
        _assert_places_sent_to_integrations(
            expected_place_ids_in_core,
            expected_place_ids_in_iw,
            expected_place_ids_in_pgr,
            places_sent_to_core,
            places_sent_to_iw,
            places_sent_to_pgr,
            'nomenclature',
            send_only_to_iw_if_switched,
        )
        places_sent_to_core = set()
        places_sent_to_iw = set()
        places_sent_to_pgr = set()

        await taxi_eats_nomenclature_collector.run_distlock_task(
            'price-scheduler',
        )
        handle_price_finished.next_call()
        _assert_places_sent_to_integrations(
            expected_place_ids_in_core,
            expected_place_ids_in_iw,
            expected_place_ids_in_pgr,
            places_sent_to_core,
            places_sent_to_iw,
            places_sent_to_pgr,
            'price',
            send_only_to_iw_if_switched,
        )
        places_sent_to_core = set()
        places_sent_to_iw = set()
        places_sent_to_pgr = set()

        await taxi_eats_nomenclature_collector.run_distlock_task(
            'stock-scheduler',
        )
        handle_stock_finished.next_call()
        _assert_places_sent_to_integrations(
            expected_place_ids_in_core,
            expected_place_ids_in_iw,
            expected_place_ids_in_pgr,
            places_sent_to_core,
            places_sent_to_iw,
            places_sent_to_pgr,
            'stock',
            send_only_to_iw_if_switched,
        )
        places_sent_to_core = set()
        places_sent_to_iw = set()
        places_sent_to_pgr = set()

        await taxi_eats_nomenclature_collector.run_distlock_task(
            'availability-scheduler',
        )
        handle_availability_finished.next_call()
        _assert_places_sent_to_integrations(
            expected_place_ids_in_core,
            expected_place_ids_in_iw,
            expected_place_ids_in_pgr,
            places_sent_to_core,
            places_sent_to_iw,
            places_sent_to_pgr,
            'availability',
            send_only_to_iw_if_switched,
        )

    if periodics_type == 'task_status_checker':
        _sql_add_tasks(pgsql, 'started')

        @mockserver.json_handler(CORE_INTEGRATIONS_HANDLER)
        def eats_core_integrations_get(request):
            task = integrations_tasks[request.query['task_id']]
            return task

        @mockserver.json_handler(INTEGRATION_WORKERS_HANDLER)
        def eats_integration_workers_get(request):
            task = integrations_tasks[request.query['task_id']]
            _assert_request_is_expected(task, expected_place_ids_in_iw)
            return task

        @mockserver.json_handler(PLACE_GROUPS_REPLICA_HANDLER)
        def eats_place_groups_replica_get(request):
            task = integrations_tasks[request.query['task_id']]
            _assert_request_is_expected(task, expected_place_ids_in_pgr)
            return task

        @testpoint('eats_nomenclature_collector::task-status-checker')
        def handle_checker_finished(arg):
            pass

        await taxi_eats_nomenclature_collector.run_distlock_task(
            'task-status-checker',
        )
        handle_checker_finished.next_call()

    if periodics_type == 'db_cleanup':
        _sql_add_tasks(pgsql, 'failed')

        @mockserver.json_handler(CORE_INTEGRATIONS_HANDLER)
        def eats_core_integrations_delete(request):
            task = integrations_tasks[request.query['task_id']]
            return task

        @mockserver.json_handler(INTEGRATION_WORKERS_HANDLER)
        def eats_integration_workers_delete(request):
            task = integrations_tasks[request.query['task_id']]
            _assert_request_is_expected(task, expected_place_ids_in_iw)
            return task

        @mockserver.json_handler(PLACE_GROUPS_REPLICA_HANDLER)
        def eats_place_groups_replica_del(request):
            task = integrations_tasks[request.query['task_id']]
            _assert_request_is_expected(task, expected_place_ids_in_pgr)
            return task

        @testpoint('eats_nomenclature_collector::db-cleanup-finished')
        def handle_cleanup_finished(arg):
            pass

        await taxi_eats_nomenclature_collector.run_distlock_task('db-cleanup')
        handle_cleanup_finished.next_call()


def _assert_request_is_expected(request_json, expected_place_ids_by_type):
    found_type = False
    for task_type in expected_place_ids_by_type:
        if request_json['type'] == task_type:
            expected_place_ids = expected_place_ids_by_type[task_type]
            assert request_json['place_id'] in expected_place_ids
            found_type = True
    assert found_type is True


def _assert_places_sent_to_integrations(
        expected_place_ids_in_core,
        expected_place_ids_in_iw,
        expected_place_ids_in_pgr,
        places_sent_to_core,
        places_sent_to_iw,
        places_sent_to_pgr,
        task_type,
        send_only_to_iw_if_switched,
):
    if send_only_to_iw_if_switched:
        assert set(places_sent_to_core) == set(
            expected_place_ids_in_core[task_type],
        )
    else:
        assert set(places_sent_to_core) == {'1', '2', '3', '4', '5', '6'}

    assert set(places_sent_to_iw) == set(expected_place_ids_in_iw[task_type])
    assert set(places_sent_to_pgr) == set(expected_place_ids_in_pgr[task_type])


def _sql_add_tasks(pgsql, status):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
            insert into eats_nomenclature_collector.nomenclature_brand_tasks(
                id, brand_id, status, updated_at
            )
            values
                ('brand_task_id1', '1', 'created', now() - interval '1 month'),
                ('brand_task_id2', '2', 'created', now() - interval '1 month'),
                ('brand_task_id3', '3', 'created', now() - interval '1 month');

            insert into eats_nomenclature_collector.nomenclature_place_tasks(
                id, place_id, nomenclature_brand_task_id, status, updated_at
            )
            values
                ('nomenclature_1', '1', 'brand_task_id1', '{status}',
                 now() - interval '1 month'),
                ('nomenclature_2', '2', 'brand_task_id1', '{status}',
                 now() - interval '1 month'),
                ('nomenclature_3', '3', 'brand_task_id2', '{status}',
                 now() - interval '1 month'),
                ('nomenclature_4', '4', 'brand_task_id2', '{status}',
                 now() - interval '1 month'),
                 ('nomenclature_5', '5', 'brand_task_id3', '{status}',
                 now() - interval '1 month'),
                ('nomenclature_6', '6', 'brand_task_id3', '{status}',
                 now() - interval '1 month');

            insert into eats_nomenclature_collector.price_tasks(
                id, place_id, status, updated_at
            )
            values
                ('price_1', '1', '{status}', now() - interval '1 month'),
                ('price_2', '2', '{status}', now() - interval '1 month'),
                ('price_3', '3', '{status}', now() - interval '1 month'),
                ('price_4', '4', '{status}', now() - interval '1 month'),
                ('price_5', '5', '{status}', now() - interval '1 month'),
                ('price_6', '6', '{status}', now() - interval '1 month');

            insert into eats_nomenclature_collector.stock_tasks(
                id, place_id, status, updated_at
            )
            values
                ('stock_1', '1', '{status}', now() - interval '1 month'),
                ('stock_2', '2', '{status}', now() - interval '1 month'),
                ('stock_3', '3', '{status}', now() - interval '1 month'),
                ('stock_4', '4', '{status}', now() - interval '1 month'),
                ('stock_5', '5', '{status}', now() - interval '1 month'),
                ('stock_6', '6', '{status}', now() - interval '1 month');

            insert into eats_nomenclature_collector.availability_tasks(
                id, place_id, status, updated_at
            )
            values
                ('availability_1', '1', '{status}',
                 now() - interval '1 month'),
                ('availability_2', '2', '{status}',
                 now() - interval '1 month'),
                ('availability_3', '3', '{status}',
                 now() - interval '1 month'),
                ('availability_4', '4', '{status}',
                 now() - interval '1 month'),
                ('availability_5', '5', '{status}',
                 now() - interval '1 month'),
                ('availability_6', '6', '{status}',
                 now() - interval '1 month');
        """,
    )
