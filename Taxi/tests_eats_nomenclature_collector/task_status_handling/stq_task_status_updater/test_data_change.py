import datetime as dt

import pytest
import pytz


QUEUE_NAME = 'eats_nomenclature_collector_task_status_updater'

MOCK_OLD = dt.datetime(2020, 4, 1, 12, tzinfo=pytz.UTC)
MOCK_NOW = dt.datetime(2021, 4, 1, 12, tzinfo=pytz.UTC)
PLACE_ID = '1'
BRAND_ID = '1'


@pytest.mark.parametrize(
    'input_task_data, expected_db_task_data',
    [
        # check known task types
        pytest.param(
            {
                'stq_task_type': 'nomenclature',
                'db_status': 'creating',
                'stq_status': 'started',
            },
            {'status': 'started'},
            id='nomenclature',
        ),
        pytest.param(
            {
                'stq_task_type': 'price',
                'db_status': 'creating',
                'stq_status': 'started',
            },
            {'status': 'started'},
            id='price',
        ),
        pytest.param(
            {
                'stq_task_type': 'stock',
                'db_status': 'creating',
                'stq_status': 'started',
            },
            {'status': 'started'},
            id='stock',
        ),
        pytest.param(
            {
                'stq_task_type': 'availability',
                'db_status': 'creating',
                'stq_status': 'started',
            },
            {'status': 'started'},
            id='availability',
        ),
        pytest.param(
            {
                'stq_task_type': 'some unknown task type',
                'db_task_type': 'nomenclature',
                'db_status': 'creating',
                'status': 'started',
            },
            {'status': 'creating', 'status_synchronized_at': MOCK_OLD},
            id='unknown task type',
        ),
        # check known task statuses
        pytest.param(
            {'db_status': 'creating', 'stq_status': 'created'},
            {'status': 'created'},
            id='created',
        ),
        pytest.param(
            {'db_status': 'creating', 'status': 'started'},
            {'status': 'started'},
            id='started',
        ),
        pytest.param(
            {
                'db_status': 'creating',
                'stq_status': 'finished',
                'data_file_url': 'smthsmth_path',
            },
            {'status': 'finished', 'file_path': 'smthsmth_path'},
            id='finished',
        ),
        pytest.param(
            {
                'db_status': 'creating',
                'stq_status': 'failed',
                'reason': 'because error',
            },
            {'status': 'failed', 'reason': 'because error'},
            id='failed',
        ),
        pytest.param(
            {
                'db_status': 'creating',
                'stq_status': 'cancelled',
                'reason': 'because cancel',
            },
            {'status': 'cancelled', 'reason': 'because cancel'},
            id='cancelled',
        ),
        pytest.param(
            {'db_status': 'creating', 'stq_status': 'some unknown status'},
            {'status': 'creating', 'status_synchronized_at': MOCK_OLD},
            id='unknown status',
        ),
        # check final task statuses
        pytest.param(
            {'db_status': 'failed', 'stq_status': 'created'},
            {'status': 'failed', 'status_synchronized_at': MOCK_OLD},
            id='from failed',
        ),
        pytest.param(
            {'db_status': 'creation_failed', 'stq_status': 'created'},
            {'status': 'creation_failed', 'status_synchronized_at': MOCK_OLD},
            id='from creation_failed',
        ),
        pytest.param(
            {'db_status': 'processed', 'stq_status': 'created'},
            {'status': 'processed', 'status_synchronized_at': MOCK_OLD},
            id='from processed',
        ),
    ],
)
@pytest.mark.now(MOCK_NOW.isoformat())
async def test_task_data_change(
        pg_cursor,
        stq_enqueue_and_call,
        config_set_push_model,
        sql_add_place_task_for_task_status_test,
        # parametrize
        input_task_data,
        expected_db_task_data,
):
    config_set_push_model(place_ids=[PLACE_ID])

    stq_task_type = input_task_data.get('stq_task_type', 'nomenclature')
    db_task_type = input_task_data.get('db_task_type', stq_task_type)
    task_id = PLACE_ID

    _sql_add_place_task(
        sql_add_place_task_for_task_status_test,
        brand_id=BRAND_ID,
        place_id=PLACE_ID,
        task_id=task_id,
        task_type=db_task_type,
        status=input_task_data.get('db_status', 'creating'),
        synced_at=MOCK_OLD.isoformat(),
    )

    kwargs = {
        'place_id': PLACE_ID,
        'integration_task_id': task_id,
        'integration_task_type': stq_task_type,
        'status': input_task_data.get('stq_status', 'created'),
        'reason': None,
        'data_file_url': None,
    }
    kwargs.update(input_task_data)

    await stq_enqueue_and_call(QUEUE_NAME, task_id=task_id, kwargs=kwargs)

    db_task_data = _sql_get_task_data(
        pg_cursor, task_id=task_id, task_type=db_task_type,
    )
    if 'status_synchronized_at' not in expected_db_task_data:
        assert db_task_data['status_synchronized_at'] >= MOCK_NOW
    _verify_db_task_data_part(db_task_data, expected_db_task_data)


def _verify_db_task_data_part(db_task_data, expected_task_data):
    for argname, expected_argvalue in expected_task_data.items():
        val = db_task_data[argname]
        if isinstance(expected_argvalue, list):
            assert sorted(val) == sorted(expected_argvalue)
        else:
            assert val == expected_argvalue


def _sql_get_task_data(pg_cursor, task_id, task_type):
    table_name = (
        'nomenclature_place_tasks'
        if task_type == 'nomenclature'
        else f'{task_type}_tasks'
    )

    pg_cursor.execute(
        f"""
        select status, reason, file_path, status_synchronized_at
        from eats_nomenclature_collector.{table_name}
        where id = '{task_id}'
        """,
    )
    return pg_cursor.fetchone()


def _sql_add_place_task(
        sql_add_place_task_for_task_status_test,
        task_id,
        place_id=PLACE_ID,
        brand_id=BRAND_ID,
        task_type='nomenclature',
        status='creating',
        synced_at=MOCK_NOW.isoformat(),
):
    sql_add_place_task_for_task_status_test(
        task_id=task_id,
        place_id=place_id,
        brand_id=brand_id,
        task_type=task_type,
        status=status,
        synced_at=synced_at,
    )
