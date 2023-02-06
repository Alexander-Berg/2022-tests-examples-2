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
    'price_tasks,'
    'core_integrations_status,'
    'expected_tasks_count,'
    'expected_mock_times_called_count',
    [
        pytest.param(
            [conftest.create_brand(1), conftest.create_brand(2)],
            [conftest.create_place_group(1, '1111111', '8:00,15:00')],
            [
                conftest.create_brand_place_group(1, 1),
                conftest.create_brand_place_group(2, 1),
            ],
            [
                conftest.create_place(1, 1, 1),
                conftest.create_place(2, 1, 1),
                conftest.create_place(3, 1, 1),
                conftest.create_place(4, 2, 1),
            ],
            [],
            200,
            4,
            4,
            id='in_schedule_time',
        ),
        pytest.param(
            [conftest.create_brand(1)],
            [
                conftest.create_place_group(
                    1,
                    '1111111',
                    '10:00,15:00',
                    price_parser_hours='08:00,15:00',
                ),
            ],
            [conftest.create_brand_place_group(1, 1)],
            [conftest.create_place(1, 1, 1)],
            [],
            200,
            1,
            1,
            id='in_price_schedule_time',
        ),
        pytest.param(
            [conftest.create_brand(1)],
            [conftest.create_place_group(1, '1111111', '10:00,15:00')],
            [conftest.create_brand_place_group(1, 1)],
            [conftest.create_place(1, 1, 1)],
            [],
            200,
            0,
            0,
            id='not_in_schedule_time',
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
            200,
            0,
            0,
            id='not_in_price_schedule_time',
        ),
        pytest.param(
            [conftest.create_brand(1)],
            [conftest.create_place_group(1, '1111111', '0800,1500')],
            [conftest.create_brand_place_group(1, 1)],
            [conftest.create_place(1, 1, 1)],
            [],
            200,
            0,
            0,
            id='incorrect_schedule_time',
        ),
        pytest.param(
            [conftest.create_brand(1)],
            [
                conftest.create_place_group(
                    1,
                    '1111111',
                    '10:00,15:00',
                    price_parser_hours='0800,1500',
                ),
            ],
            [conftest.create_brand_place_group(1, 1)],
            [conftest.create_place(1, 1, 1)],
            [],
            200,
            0,
            0,
            id='incorrect_price_schedule_time',
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
                conftest.create_price_task(1, 'created', TEST_CREATED_AT),
                conftest.create_price_task(2, 'started', TEST_CREATED_AT),
                conftest.create_price_task(3, 'finished', TEST_CREATED_AT),
                conftest.create_price_task(4, 'processed', TEST_CREATED_AT),
            ],
            200,
            6,
            2,
            id='places_have_in_progress_tasks',
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
            200,
            2,
            2,
            id='not_is_parser_enabled',
        ),
        pytest.param(
            [conftest.create_brand(1)],
            [conftest.create_place_group(1, '1111111', '8:00,15:00')],
            [conftest.create_brand_place_group(1, 1)],
            [conftest.create_place(1, 1, 1)],
            [],
            400,
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
            401,
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
            403,
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
            404,
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
            409,
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
            500,
            1,
            2,
            id='core_integrations_500',
        ),
        pytest.param(
            [conftest.create_brand(1), conftest.create_brand(2)],
            [
                conftest.create_place_group(
                    1, '1111111', '8:00,15:00', is_enabled=False,
                ),
            ],
            [
                conftest.create_brand_place_group(1, 1),
                conftest.create_brand_place_group(2, 1),
            ],
            [
                conftest.create_place(1, 1, 1),
                conftest.create_place(2, 1, 1),
                conftest.create_place(3, 1, 1),
                conftest.create_place(4, 2, 1),
            ],
            [],
            200,
            0,
            0,
            id='place_group_disabled',
        ),
    ],
)
@pytest.mark.now('2021-01-27T08:05:00+0300')  # Wednesday
async def test_price_scheduler(
        taxi_eats_nomenclature_collector,
        testpoint,
        pg_cursor,
        fill_db,
        mock_integrations,
        brands,
        place_groups,
        brands_place_groups,
        places,
        price_tasks,
        core_integrations_status,
        expected_tasks_count,
        expected_mock_times_called_count,
):
    fill_db(
        brands,
        place_groups,
        brands_place_groups,
        places,
        price_tasks=price_tasks,
    )
    integrations_mock = mock_integrations(core_integrations_status, ['price'])

    # pylint: disable=unused-variable

    @testpoint('eats_nomenclature_collector::price-scheduler')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_distlock_task('price-scheduler')
    handle_finished.next_call()
    pg_cursor.execute('select * from eats_nomenclature_collector.price_tasks;')
    rows = pg_cursor.fetchall()
    assert len(rows) == expected_tasks_count
    assert integrations_mock.times_called == expected_mock_times_called_count
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


async def test_skip_places_without_brand(
        taxi_eats_nomenclature_collector,
        testpoint,
        pg_cursor,
        fill_db,
        mock_integrations,
):
    brands = [conftest.create_brand(1)]
    place_groups = [conftest.create_place_group(1, '1111111', '8:00,15:00')]
    brands_place_groups = [conftest.create_brand_place_group(1, 1)]
    places = [conftest.create_place(1, 1, 1), conftest.create_place(2, 1, 1)]
    fill_db(
        brands,
        place_groups,
        brands_place_groups,
        places,
        availability_tasks=[],
    )
    integrations_mock = mock_integrations(
        core_integrations_status=200, expected_task_types=['price'],
    )

    @testpoint('eats-nomenclature-collector_place_to_brand_map')
    def _place_to_brand_map(param):
        return {'place_id': '1', 'brand_id': '1'}

    @testpoint('eats_nomenclature_collector::price-scheduler')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_distlock_task('price-scheduler')
    handle_finished.next_call()
    pg_cursor.execute('select * from eats_nomenclature_collector.price_tasks;')
    rows = pg_cursor.fetchall()
    assert len(rows) == 1

    assert integrations_mock.times_called == 1


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics('price-scheduler', is_distlock=True)
