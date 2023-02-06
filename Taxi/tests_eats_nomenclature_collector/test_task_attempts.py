import pytest

from . import conftest


CORE_INTEGRATIONS_HANDLER = (
    '/eats-core-integrations/integrations/nomenclature-collector/v1/tasks'
)
MOCK_NOW = '2021-01-27T08:05:00+03:00'
TEST_CREATED_AT = '2021-01-27T08:01:00+00:00'
TIMEOUT_REASONS = ['Connection timeout while fetch menu']
REASONS_TO_RETRY = ['Fail menu synchronization', 'Fetch menu fail']


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'task_type, task_table_name, attempts_table_name',
    [
        pytest.param(
            'nomenclature',
            'nomenclature_place_tasks',
            'nomenclature_place_task_creation_attempts',
            id='nomenclature_tasks',
        ),
        pytest.param(
            'price',
            'price_tasks',
            'price_task_creation_attempts',
            id='price_tasks',
        ),
    ],
)
@pytest.mark.parametrize(
    'place_groups, expected_place_tasks_count',
    [
        # Wednesday is in place_group schedule
        pytest.param(
            [conftest.create_place_group(1, '1111111', '8:00,15:00')],
            4,
            id='in_schedule',
        ),
        # Wednesday is not in place_group schedule
        pytest.param(
            [conftest.create_place_group(1, '1101111', '8:00,15:00')],
            2,
            id='not_in_schedule',
        ),
    ],
)
async def test_schedulers(
        taxi_eats_nomenclature_collector,
        taxi_config,
        testpoint,
        pg_cursor,
        fill_db,
        mock_integrations,
        mocked_time,
        task_type,
        task_table_name,
        attempts_table_name,
        place_groups,
        expected_place_tasks_count,
):
    taxi_config.set_values(generate_config_settings())
    place_task_creation_attempts = generate_place_task_attempts()

    db_data = {
        'brands': [conftest.create_brand(1)],
        'place_groups': place_groups,
        'brands_place_groups': [conftest.create_brand_place_group(1, 1)],
        'places': [conftest.create_place(i, 1, 1) for i in range(1, 6)],
    }
    if task_type == 'nomenclature':
        db_data['place_task_creation_attempts'] = place_task_creation_attempts
    else:
        db_data['price_task_creation_attempts'] = place_task_creation_attempts
    fill_db(**db_data)

    mock_integrations(200, [task_type])

    @testpoint(f'eats_nomenclature_collector::{task_type}-scheduler')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_distlock_task(
        f'{task_type}-scheduler',
    )
    handle_finished.next_call()

    rows = select_place_tasks(pg_cursor, task_table_name)
    assert len(rows) == expected_place_tasks_count

    # task attempts are not changed
    assert (
        select_place_task_attempts(pg_cursor, attempts_table_name)
        == place_task_creation_attempts
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'task_type,' 'task_table_name,' 'attempts_table_name',
    [
        pytest.param(
            'nomenclature',
            'nomenclature_place_tasks',
            'nomenclature_place_task_creation_attempts',
            id='nomenclature_tasks',
        ),
        pytest.param(
            'price',
            'price_tasks',
            'price_task_creation_attempts',
            id='price_tasks',
        ),
    ],
)
@pytest.mark.parametrize(
    'task_status, reason, should_retry',
    [
        # All tasks are finished
        pytest.param('finished', None, False, id='all_finished'),
        # All tasks are failed by core timeout
        pytest.param('failed', TIMEOUT_REASONS[0], True, id='timeout_reason'),
        # All tasks failed menu synchronization
        pytest.param('failed', REASONS_TO_RETRY[0], True, id='retry_reason1'),
        # All tasks failed menu fetching
        pytest.param('failed', REASONS_TO_RETRY[1], True, id='retry_reason2'),
        # All tasks failed by another reason
        pytest.param(
            'failed', 'another reason', False, id='failed_another_reason',
        ),
    ],
)
async def test_task_status_checker(
        taxi_eats_nomenclature_collector,
        taxi_config,
        mockserver,
        testpoint,
        pg_cursor,
        fill_db,
        mocked_time,
        task_type,
        task_table_name,
        attempts_table_name,
        task_status,
        reason,
        should_retry,
):
    taxi_config.set_values(generate_config_settings())
    place_task_creation_attempts = generate_place_task_attempts()

    db_data = {
        'brands': [conftest.create_brand(1)],
        'place_groups': [
            conftest.create_place_group(1, '1101111', '8:00,15:00'),
        ],
        'brands_place_groups': [conftest.create_brand_place_group(1, 1)],
        'places': [conftest.create_place(i, 1, 1) for i in range(1, 6)],
        'nomenclature_brand_tasks': [
            conftest.create_nomenclature_brand_task(
                1, 1, 'created', TEST_CREATED_AT,
            ),
        ],
    }
    if task_type == 'nomenclature':
        db_data['nomenclature_place_tasks'] = [
            conftest.create_nomenclature_place_task(
                i, 1, 'created', TEST_CREATED_AT, task_id=str(i),
            )
            for i in range(1, 6)
        ]
        db_data['place_task_creation_attempts'] = place_task_creation_attempts
    else:
        db_data['price_tasks'] = [
            conftest.create_price_task(
                i, 'created', TEST_CREATED_AT, task_id=str(i),
            )
            for i in range(1, 6)
        ]
        db_data['price_task_creation_attempts'] = place_task_creation_attempts
    fill_db(**db_data)

    # pylint: disable=unused-variable
    @mockserver.json_handler(CORE_INTEGRATIONS_HANDLER)
    def eats_core_retail(request):
        task_id = request.query['task_id']
        place_id = task_id  # mock tasks here have same id as places
        task_file_path = ''
        if task_status == 'finished':
            task_file_path = (
                f'https://eda-integration.s3.mdst.yandex.net/'
                f'some_path/{task_id}.json'
            )
        return {
            'id': task_id,
            'type': task_type,
            'place_id': place_id,
            'status': task_status,
            'data_file_url': task_file_path,
            'data_file_version': '',
            'reason': reason,
        }

    @testpoint(f'eats_nomenclature_collector::task-status-checker')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_distlock_task(
        'task-status-checker',
    )
    handle_finished.next_call()

    assert select_place_tasks(pg_cursor, task_table_name) == [
        (str(i), str(i), task_status, reason) for i in range(1, 6)
    ]

    if should_retry:
        expected_place_task_attempts = [
            conftest.create_task_creation_attempt('1', MOCK_NOW, 1, False),
            conftest.create_task_creation_attempt('2', MOCK_NOW, 2, False),
            conftest.create_task_creation_attempt('3', MOCK_NOW, 3, False),
            conftest.create_task_creation_attempt('4', MOCK_NOW, 2, False),
            conftest.create_task_creation_attempt('5', MOCK_NOW, 3, False),
        ]
    else:
        expected_place_task_attempts = [
            conftest.create_task_creation_attempt(str(i), MOCK_NOW, 0, True)
            for i in range(1, 6)
        ]
    assert (
        select_place_task_attempts(pg_cursor, attempts_table_name)
        == expected_place_task_attempts
    )


def generate_config_settings():
    return {
        'EATS_NOMENCLATURE_COLLECTOR_SCHEDULERS_SETTINGS': {
            '__default__': {
                'enabled': True,
                'period_in_sec': 60,
                'batch_size': 1000,
                'max_attempts_count': 3,
                'attempts_period_in_sec': 300,
                'timeout_reasons': TIMEOUT_REASONS,
                'reasons_to_retry': REASONS_TO_RETRY,
            },
        },
    }


def generate_place_task_attempts():
    return [
        # place 1 doesn't have place_task_creation_attempt
        # place 2 has successful place_task_creation_attempt
        conftest.create_task_creation_attempt(
            '2', '2021-01-22T08:05:00+03:00', 1, True,
        ),
        # place 3 has recent unsuccessful place_task_creation_attempt
        conftest.create_task_creation_attempt(
            '3', '2021-01-27T08:04:00+03:00', 2, False,
        ),
        # place 4 has old unsuccessful place_task_creation_attempt
        conftest.create_task_creation_attempt(
            '4', '2021-01-22T08:05:00+03:00', 1, False,
        ),
        # place 5 has old unsuccessful place_task_creation_attempt
        # with max_attempt_count
        conftest.create_task_creation_attempt(
            '5', '2021-01-22T08:05:00+03:00', 3, False,
        ),
    ]


def select_place_tasks(pg_cursor, table_name):
    pg_cursor.execute(
        f"""
        select * from eats_nomenclature_collector.{table_name}
        order by place_id""",
    )
    return [
        (row['id'], row['place_id'], row['status'], row['reason'])
        for row in pg_cursor.fetchall()
    ]


def select_place_task_attempts(pg_cursor, table_name):
    pg_cursor.execute(
        f"""
        select * from eats_nomenclature_collector.{table_name}
        order by place_id""",
    )
    return [
        (
            row['place_id'],
            row['last_creation_attempt_at'].isoformat(),
            row['attempts_count'],
            row['last_attempt_was_successful'],
        )
        for row in pg_cursor.fetchall()
    ]
