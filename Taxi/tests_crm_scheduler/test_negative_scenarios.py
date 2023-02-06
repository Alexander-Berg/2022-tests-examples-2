# pylint: disable=import-only-modules
import pytest

from tests_crm_scheduler.utils import read_count
from tests_crm_scheduler.utils import select_columns_from_table
from tests_crm_scheduler.utils import v1_get_task_list


def generate_payload(task_id, allowed, logs_saved=0):
    return {
        'task_id': task_id,
        'new_state': 'ok',
        'policy_allowed': allowed,
        'logs_saved': logs_saved,
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    }


def generate_error_payload(task_id, error_string):
    return {
        'task_id': task_id,
        'new_state': 'error',
        'error_string': error_string,
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    }


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign_small.sql',
    ],
)
async def test_negative_step_proceeded(taxi_crm_scheduler, pgsql, mocked_time):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    await taxi_crm_scheduler.post('/v1/get_task_list', {})

    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1000, 350),
    )
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_error_payload(1001, 'ERROR TEST'),
    )
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1002, 300),
    )
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1003, 400),
    )

    # Check if all policy tasks generated
    reported_state = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        ['id', 'payload_int'],
        pgsql['crm_scheduler'],
        1000,
    )

    assert reported_state == [
        {'id': 1000, 'payload_int': 350},
        {'id': 1001, 'payload_int': 0},
        {'id': 1002, 'payload_int': 300},
        {'id': 1003, 'payload_int': 400},
    ]

    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1004, 350),
    )
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_error_payload(1005, 'ERROR TEST2'),
    )
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1006, 300),
    )
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1007, 400),
    )

    # generated send tasks
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    reported_state = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        ['id', 'payload_int', 'processed'],
        pgsql['crm_scheduler'],
        1000,
    )

    assert reported_state == [
        {'id': 1001, 'payload_int': 0, 'processed': -1},
        {'id': 1005, 'payload_int': 0, 'processed': -1},
        {'id': 1000, 'payload_int': 350, 'processed': 350},
        {'id': 1002, 'payload_int': 300, 'processed': 300},
        {'id': 1003, 'payload_int': 400, 'processed': 400},
        {'id': 1004, 'payload_int': 350, 'processed': 350},
        {'id': 1006, 'payload_int': 300, 'processed': 300},
        {'id': 1007, 'payload_int': 400, 'processed': 300},
    ]

    # cleanup last step
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    push_tasks = select_columns_from_table(
        'crm_scheduler.task_pool_user_push',
        ['id'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert push_tasks == [{'id': 1010}, {'id': 1011}]

    reported_state = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        ['id', 'payload_int', 'processed'],
        pgsql['crm_scheduler'],
        1000,
    )

    assert reported_state == [
        {'id': 1006, 'payload_int': 300, 'processed': 300},
        {'id': 1007, 'payload_int': 400, 'processed': 300},
    ]

    # skip to receive push tasks
    for _ in range(7):
        await v1_get_task_list(taxi_crm_scheduler)

    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1010, 350),
    )
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_error_payload(1011, 'ERROR TEST3'),
    )
    # report last policy_task
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1008, 100),
    )

    # skip time to generate all send tasks + some log tasks
    mocked_time.sleep(5000)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    # skip to receive all tasks
    for _ in range(23):
        await v1_get_task_list(taxi_crm_scheduler)

    #  report send task
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1011, 100, 1200),
    )
    #  report send task
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1015, 100, 1200),
    )
    # report log task
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1009, 100, 1000),
    )
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1012, 100, 1000),
    )
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1013, 100, 1000),
    )

    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1014, 0),
    )

    # skip time to generate last send task
    mocked_time.sleep(5000)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    # skip to receive last log task
    for _ in range(1, 24):
        await v1_get_task_list(taxi_crm_scheduler)

    #  report last log task with errors
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended',
        generate_error_payload(1016, 'ERROR LOG SEND'),
    )

    log_restarted_task = select_columns_from_table(
        'crm_scheduler.task_pool_logs', ['id'], pgsql['crm_scheduler'], 1000,
    )

    assert log_restarted_task == [{'id': 1016}]

    # clean_up send task
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    # skip to receive all tasks
    for _ in range(1, 14):
        await v1_get_task_list(taxi_crm_scheduler)

    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1016, 0, 100),
    )

    # generate send finished
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    # skip to receive all tasks
    for _ in range(1, 14):
        await v1_get_task_list(taxi_crm_scheduler)

    #  report sending finished
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1017, 0, 0),
    )

    # check if sending finished and removed from DB
    assert read_count(pgsql, 'sendings') == 0

    sendings_finished = select_columns_from_table(
        'crm_scheduler.sendings_finished',
        ['error_details'],
        pgsql['crm_scheduler'],
        1000,
    )

    assert sendings_finished == [
        {
            'error_details': [
                'Policy error: ERROR TEST',
                'Policy error: ERROR TEST2',
                'Send to channel error: ERROR TEST3',
            ],
        },
    ]
