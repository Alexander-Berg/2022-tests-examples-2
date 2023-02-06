import pytest

from . import conftest


TEST_CREATED_AT = '2021-01-27T08:01:00+00:00'


@pytest.mark.config(
    EATS_NOMENCLATURE_COLLECTOR_SYNCHRONIZERS_SETTINGS={
        'brands': {'chunk_size': 1000, 'enabled': False, 'period_in_sec': 300},
        'groups': {'chunk_size': 1000, 'enabled': False, 'period_in_sec': 300},
        'places': {'chunk_size': 1000, 'enabled': False, 'period_in_sec': 300},
    },
)
@pytest.mark.parametrize(
    'brands,'
    'place_groups,'
    'brands_place_groups,'
    'places,'
    'nomenclature_brand_tasks,'
    'nomenclature_place_tasks,'
    'core_integrations_status,'
    'expected_brand_tasks_count,'
    'expected_place_tasks_count,'
    'expected_mock_times_called_count',
    [
        pytest.param(
            [conftest.create_brand(1)],
            [conftest.create_place_group(1, '1111111', '8:00,15:00')],
            [conftest.create_brand_place_group(1, 1)],
            [
                conftest.create_place(1, 1, 1),
                conftest.create_place(2, 1, 1),
                conftest.create_place(3, 1, 1),
            ],
            [],
            [],
            200,
            1,
            3,
            3,
            id='in_schedule_time',
        ),
        pytest.param(
            [conftest.create_brand(1)],
            [
                conftest.create_place_group(
                    1,
                    '1111111',
                    '08:00,15:00',
                    price_parser_hours='10:00,15:00',
                ),
            ],
            [conftest.create_brand_place_group(1, 1)],
            [conftest.create_place(1, 1, 1)],
            [],
            [],
            200,
            1,
            1,
            1,
            id='ignore_price_schedule_time',
        ),
        pytest.param(
            [conftest.create_brand(1)],
            [conftest.create_place_group(1, '1111111', '8:00,15:00')],
            [conftest.create_brand_place_group(1, 1)],
            [
                conftest.create_place(1, 1, 1),
                conftest.create_place(2, 1, 1),
                conftest.create_place(3, 1, 1, is_parser_enabled=False),
            ],
            [],
            [],
            200,
            1,
            2,
            2,
            id='not_is_parser_enabled',
        ),
        pytest.param(
            [
                conftest.create_brand(1),
                conftest.create_brand(2),
                conftest.create_brand(3),
            ],
            [
                conftest.create_place_group(1, '1111111', '8:00,15:00'),
                conftest.create_place_group(2, '0000000', '8:00,15:00'),
                conftest.create_place_group(3, '0010000', '8:00,15:00'),
            ],
            [
                conftest.create_brand_place_group(1, 1),
                conftest.create_brand_place_group(1, 2),
                conftest.create_brand_place_group(2, 3),
                conftest.create_brand_place_group(3, 3),
            ],
            [
                conftest.create_place(1, 1, 1),
                conftest.create_place(2, 1, 1),
                conftest.create_place(3, 2, 3),
                conftest.create_place(4, 3, 3),
            ],
            [],
            [],
            200,
            3,
            4,
            4,
            id='many_brands',
        ),
        pytest.param(
            [conftest.create_brand(1)],
            [conftest.create_place_group(1, '1111111', '8:00,15:00')],
            [conftest.create_brand_place_group(1, 1)],
            [
                conftest.create_place(1, 1, 1),
                conftest.create_place(2, 1, 1),
                conftest.create_place(3, 1, 1),
                conftest.create_place(4, 1, 1),
                conftest.create_place(5, 1, 1),
            ],
            [
                conftest.create_nomenclature_brand_task(
                    1, 1, 'created', TEST_CREATED_AT,
                ),
            ],
            [
                conftest.create_nomenclature_place_task(
                    1, 1, 'created', TEST_CREATED_AT,
                ),
                conftest.create_nomenclature_place_task(
                    2, 1, 'started', TEST_CREATED_AT,
                ),
                conftest.create_nomenclature_place_task(
                    3, 1, 'finished', TEST_CREATED_AT,
                ),
                conftest.create_nomenclature_place_task(
                    4, 1, 'processed', TEST_CREATED_AT,
                ),
            ],
            200,
            2,
            6,
            2,  # new tasks for places 4 and 5
            id='places_have_in_progress_tasks',
        ),
        pytest.param(
            [conftest.create_brand(1)],
            [
                conftest.create_place_group(1, '1101111', '8:00,15:00'),
                conftest.create_place_group(
                    2, '1101111', '8:00,15:00', is_vendor=True,
                ),
            ],
            [
                conftest.create_brand_place_group(1, 1),
                conftest.create_brand_place_group(1, 2),
            ],
            [
                conftest.create_place(1, 1, 1),
                conftest.create_place(2, 1, 2),
                conftest.create_place(3, 1, 2),
            ],
            [],
            [],
            200,
            1,
            2,
            2,
            id='day_marked_0',
        ),
        pytest.param(
            [conftest.create_brand(1)],
            [conftest.create_place_group(1, '1111111', '8:00,15:00')],
            [conftest.create_brand_place_group(1, 1)],
            [conftest.create_place(1, 1, 1)],
            [],
            [],
            400,
            1,
            1,
            1,
            id='core_integrations_400',
        ),
        pytest.param(
            [conftest.create_brand(1)],
            [conftest.create_place_group(1, '1111111', '8:00,15:00')],
            [conftest.create_brand_place_group(1, 1)],
            [conftest.create_place(1, 1, 1)],
            [],
            [],
            401,
            1,
            1,
            1,
            id='core_integrations_401',
        ),
        pytest.param(
            [conftest.create_brand(1)],
            [conftest.create_place_group(1, '1111111', '8:00,15:00')],
            [conftest.create_brand_place_group(1, 1)],
            [conftest.create_place(1, 1, 1)],
            [],
            [],
            403,
            1,
            1,
            1,
            id='core_integrations_403',
        ),
        pytest.param(
            [conftest.create_brand(1)],
            [conftest.create_place_group(1, '1111111', '8:00,15:00')],
            [conftest.create_brand_place_group(1, 1)],
            [conftest.create_place(1, 1, 1)],
            [],
            [],
            404,
            1,
            1,
            1,
            id='core_integrations_404',
        ),
        pytest.param(
            [conftest.create_brand(1)],
            [conftest.create_place_group(1, '1111111', '8:00,15:00')],
            [conftest.create_brand_place_group(1, 1)],
            [conftest.create_place(1, 1, 1)],
            [],
            [],
            409,
            1,
            1,
            1,
            id='core_integrations_409',
        ),
        pytest.param(
            [conftest.create_brand(1)],
            [conftest.create_place_group(1, '1111111', '8:00,15:00')],
            [conftest.create_brand_place_group(1, 1)],
            [conftest.create_place(1, 1, 1)],
            [],
            [],
            500,
            1,
            1,
            2,  # 2 attempts
            id='core_integrations_500',
        ),
        pytest.param(
            [
                conftest.create_brand(1),
                conftest.create_brand(2),
                conftest.create_brand(3, is_enabled=False),
            ],
            [
                conftest.create_place_group(
                    1, '1111111', '8:00,15:00', is_enabled=False,
                ),
                conftest.create_place_group(2, '0000000', '8:00,15:00'),
                conftest.create_place_group(3, '0010000', '8:00,15:00'),
            ],
            [
                conftest.create_brand_place_group(1, 1),
                conftest.create_brand_place_group(1, 2),
                conftest.create_brand_place_group(2, 1, is_enabled=False),
                conftest.create_brand_place_group(2, 3),
                conftest.create_brand_place_group(3, 3),
            ],
            [
                conftest.create_place(1, 1, 1),
                conftest.create_place(2, 1, 1),
                conftest.create_place(3, 2, 3),
                conftest.create_place(4, 3, 3),
            ],
            [],
            [],
            200,
            1,
            1,
            1,
            id='many_brands_some_disabled',
        ),
    ],
)
@pytest.mark.now('2021-01-27T08:05:00+0300')  # Wednesday
async def test_nomenclature_scheduler(
        taxi_eats_nomenclature_collector,
        testpoint,
        pg_cursor,
        fill_db,
        mock_integrations,
        # parametrize params
        brands,
        place_groups,
        brands_place_groups,
        places,
        nomenclature_brand_tasks,
        nomenclature_place_tasks,
        core_integrations_status,
        expected_brand_tasks_count,
        expected_place_tasks_count,
        expected_mock_times_called_count,
):
    fill_db(
        brands,
        place_groups,
        brands_place_groups,
        places,
        nomenclature_brand_tasks=nomenclature_brand_tasks,
        nomenclature_place_tasks=nomenclature_place_tasks,
    )
    integrations_mock = mock_integrations(
        core_integrations_status, ['nomenclature'],
    )

    @testpoint('eats_nomenclature_collector::nomenclature-scheduler')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_distlock_task(
        'nomenclature-scheduler',
    )
    handle_finished.next_call()

    pg_cursor.execute(
        'select * from eats_nomenclature_collector.nomenclature_brand_tasks;',
    )
    rows = pg_cursor.fetchall()
    assert len(rows) == expected_brand_tasks_count
    for row in rows:
        if core_integrations_status in [400, 401, 403, 404, 409, 500]:
            assert row['status'] == 'creation_failed'

    pg_cursor.execute(
        'select * from eats_nomenclature_collector.nomenclature_place_tasks;',
    )
    rows = pg_cursor.fetchall()
    assert integrations_mock.times_called == expected_mock_times_called_count
    assert len(rows) == expected_place_tasks_count
    for row in rows:
        if core_integrations_status == 400:
            assert row['reason'] == (
                'POST /integrations/nomenclature-collector/v1/tasks, status '
                'code 400. Errors: code: BAD_REQUEST, message: '
                'bad request;'
            )
            assert row['status'] == 'creation_failed'
        elif core_integrations_status == 401:
            assert row['reason'] == (
                'POST /integrations/nomenclature-collector/v1/tasks, status '
                'code 401. Errors: code: UNAUTHOURIZED, message: '
                'unauthorized;'
            )
            assert row['status'] == 'creation_failed'
        elif core_integrations_status == 403:
            assert row['reason'] == (
                'POST /integrations/nomenclature-collector/v1/tasks, status '
                'code 403. Errors: code: FORBIDDEN, message: '
                'forbidden;'
            )
            assert row['status'] == 'creation_failed'
        elif core_integrations_status == 404:
            assert row['reason'] == (
                'POST /integrations/nomenclature-collector/v1/tasks, status '
                'code 404. Errors: code: PLACE_IS_NOT_FOUND, message: place '
                'is not found;'
            )
            assert row['status'] == 'creation_failed'
        elif core_integrations_status == 409:
            assert row['reason'] == (
                'POST /integrations/nomenclature-collector/v1/tasks, status '
                'code 409. The same task with id 1 is in progress'
            )
            assert row['status'] == 'creation_failed'
        elif core_integrations_status == 500:
            assert row['reason'] == (
                'POST /integrations/nomenclature-collector/v1/tasks, status '
                'code 500. Errors: code: INTERNAL_SERVER_ERROR, message: '
                'internal server error;'
            )
            assert row['status'] == 'creation_failed'


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics('nomenclature-scheduler', is_distlock=True)
