import uuid

import pytest

from scooter_accumulator_bot.telegram_bot import notification


ENDPOINT = '/scooter-accumulator-bot/v1/bot/message'


@pytest.mark.usefixtures(
    'scooter_accumulator_bot_personal_mocks',
    'scooter_accumulator_bot_experiments_mocks',
)
@pytest.mark.parametrize(
    'message, user_role, text_format, send_to_all, '
    'chat_id, exp_times_called, notification_type',
    [
        pytest.param(
            'Message to admin',
            'admin',
            'none',
            False,
            'admin_id',
            1,
            notification.Type.VALIDATE_ACCUMULATORS_RESPONSE,
            id='Send message to all working admins',
        ),
        pytest.param(
            'Message to storekeeper',
            'storekeeper',
            'markdown',
            False,
            'storekeeper_id2',
            2,
            notification.Type.VALIDATE_ACCUMULATORS_RESPONSE,
            marks=pytest.mark.config(
                SCOOTER_ACCUMULATOR_BOT_SEND_MESSAGE={
                    'STOREKEEPER': {
                        'send_to_all': False,
                        'recipients_if_nobody_works': [
                            'pd_id_storekeeper_id2',
                        ],
                    },
                },
            ),
            id=(
                'All storekeepers are not working, '
                'send to storekeeper_id2 by config as fallback'
            ),
        ),
        pytest.param(
            'Message to repairer',
            'repairer',
            'html',
            False,
            'repairer_id1',
            1,
            notification.Type.JOB_SKIPPED,
            marks=pytest.mark.config(
                SCOOTER_ACCUMULATOR_BOT_SEND_MESSAGE={
                    'REPAIRER': {
                        'send_to_all': True,
                        'recipients_if_nobody_works': [],
                    },
                },
            ),
            id='Send to all repairer by config',
        ),
        pytest.param(
            'Message to repairer',
            'repairer',
            'html',
            True,
            'repairer_id1',
            1,
            notification.Type.JOB_SKIPPED,
            marks=pytest.mark.config(
                SCOOTER_ACCUMULATOR_BOT_SEND_MESSAGE={
                    'REPAIRER': {
                        'send_to_all': False,
                        'recipients_if_nobody_works': [],
                    },
                },
            ),
            id='Send to all repairer by request',
        ),
        pytest.param(
            'Message to storekeeper_manager',
            'storekeeper_manager',
            'html',
            False,
            'storekeeper_manager_id1',
            1,
            notification.Type.VALIDATE_ACCUMULATORS_RESPONSE,
            id='Send to all storekeeper_manager by request',
        ),
    ],
)
async def test_ok(
        taxi_scooter_accumulator_bot_web,
        stq,
        mock_personal,
        message,
        user_role,
        text_format,
        send_to_all,
        chat_id,
        exp_times_called,
        notification_type,
        scooter_accumulator_bot_experiments_mocks,
        mock_experiments3,
):
    x_idempotency_token = str(uuid.uuid4())
    headers = {'X-Idempotency-Token': x_idempotency_token}

    json_request = {
        'message': message,
        'user_role': user_role,
        'format': text_format,
        'send_to_all': send_to_all,
        'notification_type': notification_type,
    }

    response = await taxi_scooter_accumulator_bot_web.post(
        ENDPOINT, headers=headers, json=json_request,
    )

    assert response.status == 200
    stq_args = stq.scooter_accumulator_bot_send_message.next_call()
    assert stq_args['queue'] == 'scooter_accumulator_bot_send_message'
    assert stq_args['id'] == f'{x_idempotency_token}_1'
    assert stq_args['args'][0] == chat_id
    assert stq_args['args'][1] == message
    assert stq_args['args'][2] == text_format

    assert (
        scooter_accumulator_bot_experiments_mocks.times_called
        == exp_times_called
    )
