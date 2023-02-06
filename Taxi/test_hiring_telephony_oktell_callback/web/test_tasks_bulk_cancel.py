import typing
from unittest import mock

import pytest

from hiring_telephony_oktell_callback.internal import constants


QUERY: str = """
SELECT task_id, is_stopped, task_state
FROM "hiring_telephony_oktell_callback"."tasks"
WHERE "task_id" in ('%s')
"""

CANCELLABLE_STATUSES: typing.Dict[str, bool] = {
    'processed': False,
    'pending': True,
    'acquired': False,
    'postponed': False,  # virtual status, not stored in postgres
    'cancelled': False,
}


@pytest.mark.parametrize(
    'task_ids,, expected_result',
    [
        (['non_existent_task'], {'cancelled_tasks': []}),
        (
            ['task_id_1', 'task_id_2', 'task_id_3', 'task_id_5'],
            {'cancelled_tasks': ['task_id_1', 'task_id_3', 'task_id_5']},
        ),
        (['task_id_4'], {'cancelled_tasks': ['task_id_4']}),
    ],
)
async def test_v1_tasks_bulk_cancel(
        web_app_client, web_context, task_ids, expected_result,
):
    # arrange
    # act
    response = await web_app_client.post(
        '/v1/tasks/bulk-cancel', json={'task_ids': task_ids},
    )
    # assert
    assert response.status == 200
    result = await response.json()
    assert result == {'cancelled_tasks': mock.ANY}
    result['cancelled_tasks'] = sorted(result['cancelled_tasks'])
    assert result['cancelled_tasks'] == expected_result['cancelled_tasks']
    task_ids = result['cancelled_tasks']
    async with web_context.pg.master_pool.acquire() as conn:
        items = await conn.fetch(QUERY % '\',\''.join(task_ids))
        for item in items:
            assert item['is_stopped'] is True
            assert item['task_state'] == 'cancelled'


@pytest.mark.parametrize(
    'task_ids, expected_status, expected_result',
    [
        (
            [f'task_in_{state}_status'],
            200,
            {
                'cancelled_tasks': (
                    [f'task_in_{state}_status']
                    if CANCELLABLE_STATUSES[state]
                    else []
                ),
            },
        )
        for state in constants.TASK_STATES
        # test-cases generates automatically to prevent errors in the future
        # when new task state may be added disregarding this functionality
    ],
)
async def test_v1_tasks_bulk_cancel__for_each_task_state(
        web_app_client,
        web_context,
        task_ids,
        expected_status,
        expected_result,
):
    # arrange
    # act
    response = await web_app_client.post(
        '/v1/tasks/bulk-cancel', json={'task_ids': task_ids},
    )

    # assert
    assert response.status == expected_status
    result = await response.json()
    assert result == expected_result


@pytest.mark.parametrize(
    'task_ids, expected_result',
    [
        (
            [f'task{task_index}' for task_index in range(10002)],
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'Some parameters are invalid',
                'details': {
                    'reason': (
                        'Invalid value for task_ids: [\'task0\', \'task1\', '
                        '\'task2\', \'task3\', \'task4\', \'task5\', '
                        '\'task6\', \'task7\', \'task8\', \'task9\', '
                        '\'task10\', \'task11\', \'task12\', \'task13\', '
                        '\'task14\', \'task15\', \'task16\', \'task17\', '
                        '\'task18\', \'task19\', \'task20\', \'task21\', '
                        '\'task22\', \'task23\', \'task24\', \'task25\', '
                        '\'task26\', \'task27\', \'task28\', \'task29\', '
                        '\'task30\', \'task31\', \'task32\', \'task33\', '
                        '\'task34\', \'task35\', \'task36\', \'task37\', '
                        '\'task38\', \'task39\', \'task40\', \'task41\', '
                        '\'task42\', \'task43\', \'task44\', \'task45\', '
                        '\'task46\', \'task47\', \'task48\', \'task49\', '
                        '\'task50\', \'task51\', \'task52\', \'task53\', '
                        '\'task54\', \'task55\', \'task56\', \'task57\', '
                        '\'task58\', \'task59\', \'task60\', \'task61\', '
                        '\'task62\', \'task63\', \'task64\', \'task65\', '
                        '\'task66\', \'task67\', \'task68\', \'task69\', '
                        '\'task70\', \'task71\', \'task72\', \'task73\', '
                        '\'task74\', \'task75\', \'task76\', \'task77\', '
                        '\'task78\', \'task79\', \'task80\', \'task81\', '
                        '\'task82\', \'task83\', \'task84\', \'task85\', '
                        '\'task86\', \'task87\', \'task88\', \'task89\', '
                        '\'task90\', \'task91\', \'task92\', \'task93\', '
                        '\'task94\', \'task95\', \'task96\', \'task97\', '
                        '\'task98\', \'task99\', \'task100\', \'task101\', '
                        '\'task102\',  number of items must be '
                        'less than or equal to 10000'
                    ),
                },
            },
        ),
        (
            [],
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'Some parameters are invalid',
                'details': {
                    'reason': (
                        'Invalid value for task_ids: [] number of items '
                        'must be greater than or equal to 1'
                    ),
                },
            },
        ),
    ],
)
async def test_v1_tasks_bulk_cancel__with_broken_restrictions__return_error(
        web_app_client, task_ids, expected_result, web_context,
):
    # arrange
    # act
    response = await web_app_client.post(
        '/v1/tasks/bulk-cancel', json={'task_ids': task_ids},
    )
    # assert
    assert response.status == 400
    result = await response.json()
    assert result == expected_result
