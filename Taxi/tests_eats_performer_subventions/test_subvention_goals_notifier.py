import pytest


async def get_notification_performer_ids(cursor, status: str):
    cursor.execute(
        """
SELECT
    psog.performer_id AS performer_id, psn.type AS type
FROM eats_performer_subventions.performer_subvention_notifications  psn
inner join eats_performer_subventions.performer_subvention_order_goals psog
    ON  psn.goal_id = psog.id AND psn.goal_type = 'dxgy'
WHERE psn.status='{0}'
        """.format(
            status,
        ),
    )
    result = cursor.fetchall()

    return [
        {
            'performer_id': notification['performer_id'],
            'type': notification['type'],
        }
        for notification in result
    ]


@pytest.mark.translations()
@pytest.mark.pgsql(
    'eats_performer_subventions',
    files=['subvention_goals_notifier_welcome_message.sql'],
)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.config(
    EATS_PERFORMER_SUBVENTIONS_SUBVENTION_GOALS_NOTIFIER_SETTINGS={
        'period_sec': 600,
        'is_enabled': True,
        'db_read_chunk_size': 2,
    },
)
@pytest.mark.parametrize(
    'performers_with_notifications,performer_with_failed_notifications,'
    'expected_message_files',
    [
        pytest.param(
            [
                {'performer_id': '1', 'type': 'welcome'},
                {'performer_id': '7', 'type': 'welcome'},
            ],
            [
                {'performer_id': '1', 'type': 'check_state'},
                {'performer_id': '2', 'type': 'check_state'},
                {'performer_id': '2', 'type': 'welcome'},
                {'performer_id': '3', 'type': 'check_state'},
                {'performer_id': '3', 'type': 'welcome'},
                {'performer_id': '6', 'type': 'finalize'},
                {'performer_id': '8', 'type': 'finalize'},
            ],
            [
                {
                    'performer_id': '1',
                    'file': 'expected_notification_performer_welcome_1.json',
                },
                {
                    'performer_id': '7',
                    'file': 'expected_notification_performer_welcome_7.json',
                },
            ],
            marks=[pytest.mark.now('2022-01-01T15:34:00+03:00')],
            id='only notification was sent for performer with id = 1',
        ),
        pytest.param(
            [
                {'performer_id': '1', 'type': 'welcome'},
                {'performer_id': '5', 'type': 'welcome'},
                {'performer_id': '5', 'type': 'check_state'},
                {'performer_id': '7', 'type': 'welcome'},
            ],
            [
                {'performer_id': '1', 'type': 'check_state'},
                {'performer_id': '2', 'type': 'check_state'},
                {'performer_id': '2', 'type': 'welcome'},
                {'performer_id': '3', 'type': 'check_state'},
                {'performer_id': '3', 'type': 'welcome'},
                {'performer_id': '6', 'type': 'finalize'},
                {'performer_id': '8', 'type': 'finalize'},
            ],
            [
                {
                    'performer_id': '1',
                    'file': 'expected_notification_performer_welcome_1.json',
                },
                {
                    'performer_id': '5',
                    'file': 'expected_notification_performer_welcome_5.json',
                },
                {
                    'performer_id': '5',
                    'file': (
                        'expected_notification_performer_check_state_5.json'
                    ),
                },
                {
                    'performer_id': '7',
                    'file': 'expected_notification_performer_welcome_7.json',
                },
            ],
            marks=[pytest.mark.now('2022-01-01T19:34:00+03:00')],
            id='two notifications were sent for performers'
            ' with id = 1 and 5',
        ),
        pytest.param(
            [{'performer_id': '4', 'type': 'welcome'}],
            [
                {'performer_id': '1', 'type': 'welcome'},
                {'performer_id': '1', 'type': 'check_state'},
                {'performer_id': '1', 'type': 'finalize'},
                {'performer_id': '2', 'type': 'check_state'},
                {'performer_id': '2', 'type': 'welcome'},
                {'performer_id': '3', 'type': 'check_state'},
                {'performer_id': '3', 'type': 'welcome'},
                {'performer_id': '5', 'type': 'check_state'},
                {'performer_id': '5', 'type': 'welcome'},
                {'performer_id': '6', 'type': 'finalize'},
                {'performer_id': '7', 'type': 'welcome'},
                {'performer_id': '8', 'type': 'finalize'},
            ],
            [
                {
                    'performer_id': '4',
                    'file': 'expected_notification_performer_welcome_4.json',
                },
            ],
            marks=[pytest.mark.now('2022-01-02T12:34:00+03:00')],
            id='next day, only one notification was sent for performers'
            ' with id = 4, other notifications was cancelled',
        ),
        pytest.param(
            [],
            [
                {'performer_id': '1', 'type': 'welcome'},
                {'performer_id': '1', 'type': 'check_state'},
                {'performer_id': '1', 'type': 'finalize'},
                {'performer_id': '2', 'type': 'check_state'},
                {'performer_id': '2', 'type': 'welcome'},
                {'performer_id': '3', 'type': 'check_state'},
                {'performer_id': '3', 'type': 'welcome'},
                {'performer_id': '5', 'type': 'check_state'},
                {'performer_id': '5', 'type': 'welcome'},
                {'performer_id': '6', 'type': 'finalize'},
                {'performer_id': '7', 'type': 'welcome'},
                {'performer_id': '8', 'type': 'finalize'},
            ],
            [],
            marks=[pytest.mark.now('2022-01-02T06:34:00+00:00')],
            id='next day, time for sending is not come',
        ),
        pytest.param(
            [],
            [
                {'performer_id': '4', 'type': 'welcome'},
                {'performer_id': '1', 'type': 'welcome'},
                {'performer_id': '1', 'type': 'check_state'},
                {'performer_id': '1', 'type': 'finalize'},
                {'performer_id': '2', 'type': 'check_state'},
                {'performer_id': '2', 'type': 'welcome'},
                {'performer_id': '3', 'type': 'check_state'},
                {'performer_id': '3', 'type': 'welcome'},
                {'performer_id': '5', 'type': 'check_state'},
                {'performer_id': '5', 'type': 'welcome'},
                {'performer_id': '6', 'type': 'finalize'},
                {'performer_id': '7', 'type': 'welcome'},
                {'performer_id': '8', 'type': 'finalize'},
            ],
            [],
            marks=[pytest.mark.now('2022-01-02T18:34:00+00:00')],
            id='next day, all notifications were cancelled',
        ),
        pytest.param(
            [
                {'performer_id': '6', 'type': 'finalize'},
                {'performer_id': '8', 'type': 'finalize'},
            ],
            [],
            [
                {
                    'performer_id': '6',
                    'file': 'expected_notification_performer_finalize_6.json',
                },
                {
                    'performer_id': '8',
                    'file': 'expected_notification_performer_finalize_8.json',
                },
            ],
            marks=[pytest.mark.now('2021-01-08T16:34:00+00:00')],
            id='finalize message',
        ),
    ],
)
async def test_subvention_goals_notifier(
        taxi_eats_performer_subventions,
        pgsql,
        stq,
        load_json,
        performers_with_notifications,
        performer_with_failed_notifications,
        expected_message_files,
):
    await taxi_eats_performer_subventions.run_periodic_task(
        'subvention-goals-notifier-periodic',
    )

    cursor = pgsql['eats_performer_subventions'].dict_cursor()
    sent_notifications = await get_notification_performer_ids(
        cursor, 'finished',
    )

    assert (
        sorted(
            sent_notifications, key=lambda i: (i['performer_id'], i['type']),
        )
        == sorted(
            performers_with_notifications,
            key=lambda i: (i['performer_id'], i['type']),
        )
    )
    failed_notifications = await get_notification_performer_ids(
        cursor, 'cancelled',
    )

    assert (
        sorted(
            failed_notifications, key=lambda i: (i['performer_id'], i['type']),
        )
        == sorted(
            performer_with_failed_notifications,
            key=lambda i: (i['performer_id'], i['type']),
        )
    )

    assert stq.eats_courier_telegram_message.times_called == len(
        performers_with_notifications,
    )

    expected_messages = [
        {
            'performer_id': file['performer_id'],
            'text': load_json(file['file'])['text'],
        }
        for file in expected_message_files
    ]

    sent_messages = []
    while stq.eats_courier_telegram_message.has_calls:
        stq_message = stq.eats_courier_telegram_message.next_call()
        assert stq_message['kwargs']['parse_mode'] == 'HTML'

        sent_messages.append(
            {
                'performer_id': stq_message['kwargs']['performer_id'],
                'text': stq_message['kwargs']['text'],
            },
        )

    assert sorted(
        expected_messages, key=lambda i: (i['performer_id'], i['text']),
    ) == sorted(sent_messages, key=lambda i: (i['performer_id'], i['text']))

    chats_messages = []

    while stq.eats_performer_subventions_send_pro_notifications.has_calls:
        stq_message = (
            stq.eats_performer_subventions_send_pro_notifications.next_call()
        )
        chats_messages.append(stq_message['kwargs']['notification_id'])

    assert len(chats_messages) == len(expected_messages)
