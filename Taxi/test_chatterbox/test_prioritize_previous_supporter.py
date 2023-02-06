import bson
import pytest

from chatterbox import stq_task


@pytest.mark.config(
    CHATTERBOX_LINES={
        'eda_first': {'mode': 'online'},
        'eda_tips': {'mode': 'online'},
    },
    CHATTERBOX_USE_COMPENDIUM_MAX_CHATS=True,
    CHATTERBOX_LINES_WITH_PRIORITY_OF_PREVIOUS_SUPPORTER=['eda_first'],
)
@pytest.mark.parametrize(
    'task_id_str, correct_supporter_logins',
    [
        pytest.param('5b2cae5db2682a976914c2a3', ['user_3'], id='no history'),
        pytest.param('5b2cae5db2682a976914c2a4', ['user_3'], id='no login'),
        pytest.param(
            '5b2cae5db2682a976914c2a5',
            ['user_1'],
            id='priority of the previous supporter',
        ),
        pytest.param(
            '5b2cae5db2682a976914c2a6',
            ['user_3'],
            id='previous supporter reached the maximum number of tasks',
        ),
        pytest.param(
            '5b2cae5db2682a976914c2a7',
            ['user_4'],
            id='line is not specified in the config',
        ),
        pytest.param(
            '5b2cae5db2682a976914c2a8',
            ['user_4'],
            id='previous supporter does not work on current line',
        ),
        pytest.param(
            '5b2cae5db2682a976914c2a9',
            ['user_3'],
            id='defining previous supporter as the last one to perform action',
        ),
        pytest.param(
            '5b2cae5db2682a976914c2b1',
            ['user_3'],
            id='the actions of the superuser are not taken into account',
        ),
    ],
)
async def test_priority_of_previous_supporter(
        cbox, stq, task_id_str, correct_supporter_logins,
):
    task_id = bson.ObjectId(task_id_str)
    await stq_task.online_chat_processing(cbox.app, task_id, [])
    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT * FROM chatterbox.supporter_tasks WHERE task_id = $1',
            str(task_id),
        )
        assert len(result) == 1
        assert result[0]['task_id'] == str(task_id)
        assert result[0]['supporter_login'] in correct_supporter_logins
