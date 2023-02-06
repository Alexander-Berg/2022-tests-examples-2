# pylint: disable=no-self-use,redefined-outer-name, no-member
import datetime

import pytest

from chatterbox.crontasks import check_conditional_actions_frequent

NOW = datetime.datetime(2018, 5, 7, 12, 44, 56)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_CONDITIONAL_ACTIONS_FREQUENT=[
        {
            'enabled': True,
            'conditions': {'status': 'new', 'created': {'#lt': 'since:20m'}},
            'action': 'close',
            'action_tag': 'test_tag',
            'macro_id': 3,
        },
        {
            'enabled': True,
            'conditions': {
                'status': 'new',
                'line': 'comm',
                'created': {'#lt': 'since:1m'},
                'tags': {'#nin': ['another_communicate_tag']},
            },
            'action': 'communicate',
            'action_tag': 'communicate_tag',
            'macro_id': 3,
        },
    ],
)
async def test_conditional_actions(
        cbox_context, loop, mock_chat_add_update, mock_chat_get_history,
):
    cbox_context.data.secdist['settings_override'][
        'ADMIN_ROBOT_LOGIN_BY_TOKEN'
    ] = {'some_token': 'robot-chatterbox'}
    mock_chat_get_history({'messages': []})

    await check_conditional_actions_frequent.do_stuff(cbox_context, loop)

    tasks = cbox_context.data.db.support_chatterbox.find()
    async for task in tasks:
        if task['_id'] == 'must_be_closed':
            assert task['status'] == 'closed'
        if task['_id'] == 'must_not_be_closed':
            assert task['status'] == 'new'
        if task['_id'] == 'communicate':
            assert task['status'] == 'new'
            assert 'communicate_tag' in task['tags']
        if task['_id'] == 'already_communicated':
            assert task['status'] == 'new'
            assert 'communicate_tag' not in task['tags']
