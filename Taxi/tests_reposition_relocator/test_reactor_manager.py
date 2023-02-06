# pylint: disable=import-only-modules
import copy
import json

import pytest

from .utils import select_named

OAUTH_HEADER = 'OAuth secret'

INITIAL_REACTIONS = [
    {
        'reaction_id': '121',
        'is_subscribed': False,
        'notification_status': 'ENABLED',
    },
    {
        'reaction_id': '122',
        'is_subscribed': False,
        'notification_status': 'DISABLED_NEW',
    },
    {
        'reaction_id': '123',
        'is_subscribed': False,
        'notification_status': 'DISABLED_NEW',
    },
    {
        'reaction_id': '124',
        'is_subscribed': False,
        'notification_status': 'DISABLED_BY_TIME',
    },
]

INITIAL_QUEUE_REACTIONS = [
    {'reaction_id': '121', 'queue_id': None},
    {'reaction_id': '122', 'queue_id': None},
    {'reaction_id': '123', 'queue_id': None},
    {'reaction_id': '124', 'queue_id': None},
]

TELEGRAM_CHAT_ID = 'some_tg_chat_id'
TELEGRAM_CHAT_FULL_ID = 'telegram:' + TELEGRAM_CHAT_ID


@pytest.mark.now('2017-10-15T12:00:00')
@pytest.mark.config(
    REPOSITION_RELOCATOR_REACTOR_NOTIFICATIONS={
        'telegram_chats_ids': [TELEGRAM_CHAT_ID],
    },
    REPOSITION_RELOCATOR_DEBUG_NOTIFICATIONS={
        '__default__': {'day_limit': 1, 'force_enable_notifications': True},
    },
)
@pytest.mark.pgsql('reposition-relocator', files=['reactions.sql'])
async def test_notifications_subscription(
        taxi_reposition_relocator, pgsql, mockserver, testpoint,
):
    @testpoint('reactor_manager::notifications_end')
    def end(data):
        pass

    testpoint_data = {}

    @testpoint('reactor_manager::processing_reaction')
    def _processing_reaction(data):
        testpoint_data['reaction_id'] = data

    @mockserver.json_handler('/nirvana-reactor/api/v1/n/notification/list')
    def _mock_list(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER

        if testpoint_data['reaction_id'] == '122':
            return mockserver.make_response(
                json.dumps(
                    {
                        'notifications': [
                            {
                                'notificationId': '1',
                                'namespaceId': '122',
                                'eventType': 'REACTION_FAILED',
                                'transport': 'TELEGRAM',
                                'recipient': TELEGRAM_CHAT_FULL_ID,
                            },
                            {
                                'notificationId': '2',
                                'namespaceId': '122',
                                'eventType': 'REACTION_CANCELED',
                                'transport': 'TELEGRAM',
                                'recipient': TELEGRAM_CHAT_FULL_ID,
                            },
                        ],
                    },
                ),
                status=200,
            )

        return mockserver.make_response(
            json.dumps({'notifications': []}), status=200,
        )

    @mockserver.json_handler('/nirvana-reactor/api/v1/n/notification/change')
    def _mock_change(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER

        reaction_id = testpoint_data['reaction_id']

        if reaction_id == '122':
            assert request.json == {
                'notificationIdsToDelete': ['1', '2'],
                'notificationsToCreate': [
                    {
                        'namespace': {'namespaceId': '221'},
                        'eventType': 'REACTION_FAILED',
                        'transport': 'TELEGRAM',
                        'recipient': TELEGRAM_CHAT_FULL_ID,
                    },
                    {
                        'namespace': {'namespaceId': '221'},
                        'eventType': 'REACTION_CANCELED',
                        'transport': 'TELEGRAM',
                        'recipient': TELEGRAM_CHAT_FULL_ID,
                    },
                ],
            }
        elif reaction_id == '123':
            assert request.json == {
                'notificationIdsToDelete': [],
                'notificationsToCreate': [
                    {
                        'namespace': {'namespaceId': '321'},
                        'eventType': 'REACTION_FAILED',
                        'transport': 'TELEGRAM',
                        'recipient': TELEGRAM_CHAT_FULL_ID,
                    },
                    {
                        'namespace': {'namespaceId': '321'},
                        'eventType': 'REACTION_CANCELED',
                        'transport': 'TELEGRAM',
                        'recipient': TELEGRAM_CHAT_FULL_ID,
                    },
                ],
            }
        elif reaction_id == '124':
            assert request.json == {
                'notificationIdsToDelete': [],
                'notificationsToCreate': [
                    {
                        'namespace': {'namespaceId': '421'},
                        'eventType': 'REACTION_FAILED',
                        'transport': 'TELEGRAM',
                        'recipient': TELEGRAM_CHAT_FULL_ID,
                    },
                    {
                        'namespace': {'namespaceId': '421'},
                        'eventType': 'REACTION_CANCELED',
                        'transport': 'TELEGRAM',
                        'recipient': TELEGRAM_CHAT_FULL_ID,
                    },
                ],
            }
        else:
            assert False

        return mockserver.make_response(json.dumps({}))

    def get_reactions_to_subscribe():
        return select_named(
            """
            SELECT * FROM state.reactions_notifications
            WHERE notification_status <> 'ENABLED' ORDER BY reaction_id
            """,
            pgsql['reposition-relocator'],
        )

    response = await taxi_reposition_relocator.post(
        'service/cron', json={'task_name': 'reactor_manager-notifications'},
    )
    assert response.status_code == 200

    await end.wait_call()
    assert _mock_list.times_called == 3

    assert _mock_change.times_called == 3

    assert get_reactions_to_subscribe() == []


@pytest.mark.now('2018-11-27T12:00:00')
@pytest.mark.config(
    REPOSITION_RELOCATOR_REACTOR_NOTIFICATIONS={
        'telegram_chats_ids': [TELEGRAM_CHAT_ID],
    },
    REPOSITION_RELOCATOR_DEBUG_NOTIFICATIONS={
        '__default__': {'day_limit': 2, 'force_enable_notifications': False},
        'reaction3': {'force_enable_notifications': False},
        'reaction4': {'force_enable_notifications': True},
        'reaction5': {'day_limit': 1, 'force_enable_notifications': True},
        'reaction7': {'day_limit': 1},
    },
)
@pytest.mark.pgsql(
    'reposition-relocator', files=['reactions_config_check.sql'],
)
async def test_notifications_subscription_config(
        taxi_reposition_relocator, pgsql, mockserver, testpoint,
):
    @testpoint('reactor_manager::notifications_end')
    def end(data):
        pass

    @testpoint('reactor_manager::old_notifications_end')
    def end_old(data):
        pass

    testpoint_data = {}

    @testpoint('reactor_manager::processing_reaction')
    def _processing_reaction(data):
        testpoint_data['reaction_id'] = data

    @testpoint('reactor_manager::processing_old_reaction')
    def _processing_old_reaction(data):
        testpoint_data['reaction_id'] = data

    @mockserver.json_handler('/nirvana-reactor/api/v1/n/notification/list')
    def _mock_list(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER

        if testpoint_data['reaction_id'] in ('125', '126', '127'):
            return mockserver.make_response(
                json.dumps(
                    {
                        'notifications': [
                            {
                                'notificationId': '1',
                                'namespaceId': testpoint_data['reaction_id'],
                                'eventType': 'REACTION_FAILED',
                                'transport': 'TELEGRAM',
                                'recipient': TELEGRAM_CHAT_FULL_ID,
                            },
                            {
                                'notificationId': '2',
                                'namespaceId': testpoint_data['reaction_id'],
                                'eventType': 'REACTION_CANCELED',
                                'transport': 'TELEGRAM',
                                'recipient': TELEGRAM_CHAT_FULL_ID,
                            },
                        ],
                    },
                ),
                status=200,
            )

        return mockserver.make_response(
            json.dumps({'notifications': []}), status=200,
        )

    @mockserver.json_handler('/nirvana-reactor/api/v1/n/notification/change')
    def _mock_change(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER

        reaction_id = testpoint_data['reaction_id']
        namespace_id = reaction_id[-1] + '21'

        if reaction_id in ('126', '127'):
            assert request.json == {
                'notificationIdsToDelete': ['1', '2'],
                'notificationsToCreate': [],
            }
        elif reaction_id == '121':
            assert request.json == {
                'notificationIdsToDelete': [],
                'notificationsToCreate': [
                    {
                        'namespace': {'namespaceId': namespace_id},
                        'eventType': 'REACTION_FAILED',
                        'transport': 'TELEGRAM',
                        'recipient': TELEGRAM_CHAT_FULL_ID,
                    },
                    {
                        'namespace': {'namespaceId': namespace_id},
                        'eventType': 'REACTION_CANCELED',
                        'transport': 'TELEGRAM',
                        'recipient': TELEGRAM_CHAT_FULL_ID,
                    },
                ],
            }
        elif reaction_id == '124':
            assert request.json == {
                'notificationIdsToDelete': [],
                'notificationsToCreate': [
                    {
                        'namespace': {'namespaceId': namespace_id},
                        'eventType': 'REACTION_FAILED',
                        'transport': 'TELEGRAM',
                        'recipient': TELEGRAM_CHAT_FULL_ID,
                    },
                    {
                        'namespace': {'namespaceId': namespace_id},
                        'eventType': 'REACTION_CANCELED',
                        'transport': 'TELEGRAM',
                        'recipient': TELEGRAM_CHAT_FULL_ID,
                    },
                ],
            }
        else:
            assert False

        return mockserver.make_response(json.dumps({}))

    def get_reactions_to_subscribe():
        return select_named(
            """
            SELECT * FROM state.reactions_notifications
            WHERE notification_status <> 'ENABLED' ORDER BY reaction_id
            """,
            pgsql['reposition-relocator'],
        )

    response = await taxi_reposition_relocator.post(
        'service/cron', json={'task_name': 'reactor_manager-notifications'},
    )
    assert response.status_code == 200
    await end.wait_call()

    response = await taxi_reposition_relocator.post(
        'service/cron',
        json={'task_name': 'reactor_manager-old-notifications'},
    )
    assert response.status_code == 200
    await end_old.wait_call()

    assert _mock_list.times_called == 4

    assert _mock_change.times_called == 4

    assert get_reactions_to_subscribe() == [
        {
            'reaction_id': '122',
            'is_subscribed': False,
            'notification_status': 'DISABLED_BY_TIME',
        },
        {
            'reaction_id': '123',
            'is_subscribed': False,
            'notification_status': 'DISABLED_BY_TIME',
        },
        {
            'reaction_id': '126',
            'is_subscribed': False,
            'notification_status': 'DISABLED_BY_TIME',
        },
        {
            'reaction_id': '127',
            'is_subscribed': False,
            'notification_status': 'DISABLED_BY_TIME',
        },
    ]


@pytest.mark.config(REPOSITION_RELOCATOR_SERVICE_ENABLED=True)
@pytest.mark.pgsql(
    'reposition-relocator', files=['reactions.sql', 'queues.sql'],
)
async def test_save_queues(
        taxi_reposition_relocator, pgsql, mockserver, testpoint,
):
    @mockserver.json_handler('/nirvana-reactor/api/v1/q/update')
    def _mock_queue(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER
        return mockserver.make_response(json.dumps({}), status=200)

    def get_reactions_to_queue():
        return select_named(
            'SELECT * FROM state.reactions_queues ORDER BY reaction_id',
            pgsql['reposition-relocator'],
        )

    response = await taxi_reposition_relocator.post(
        'service/cron', json={'task_name': 'reactor_manager-queues'},
    )
    assert response.status_code == 200
    assert _mock_queue.times_called == 1

    expected_result = copy.deepcopy(INITIAL_QUEUE_REACTIONS)
    for res in expected_result:
        res['queue_id'] = 'q123'

    assert get_reactions_to_queue() == expected_result


@pytest.mark.config(REPOSITION_RELOCATOR_SERVICE_ENABLED=False)
@pytest.mark.pgsql('reposition-relocator', files=['reactions.sql'])
async def test_disabled_notifications(
        taxi_reposition_relocator, pgsql, mockserver, testpoint,
):
    @testpoint('reactor_manager::notifications_end')
    def end(data):
        pass

    @mockserver.json_handler('/nirvana-reactor/api/v1/n/notification/list')
    def _mock_list(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER
        return mockserver.make_response(
            json.dumps({'notifications': []}), status=200,
        )

    @mockserver.json_handler('/nirvana-reactor/api/v1/n/notification/change')
    def _mock_change(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER
        return mockserver.make_response(json.dumps({}))

    def get_reactions_to_subscribe():
        return select_named(
            'SELECT * FROM state.reactions_notifications ORDER BY reaction_id',
            pgsql['reposition-relocator'],
        )

    response = await taxi_reposition_relocator.post(
        'service/cron', json={'task_name': 'reactor_manager-notifications'},
    )
    assert response.status_code == 200

    await end.wait_call()

    assert _mock_list.times_called == 0
    assert _mock_change.times_called == 0

    assert get_reactions_to_subscribe() == INITIAL_REACTIONS


@pytest.mark.config(REPOSITION_RELOCATOR_SERVICE_ENABLED=False)
@pytest.mark.pgsql(
    'reposition-relocator', files=['reactions.sql', 'queues.sql'],
)
async def test_disabled_queues(
        taxi_reposition_relocator, pgsql, mockserver, testpoint,
):
    @mockserver.json_handler('/nirvana-reactor/api/v1/q/update')
    def _mock_queue(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER
        return mockserver.make_response(json.dumps({}), status=200)

    def get_reactions_to_queue():
        return select_named(
            'SELECT * FROM state.reactions_queues ORDER BY reaction_id',
            pgsql['reposition-relocator'],
        )

    response = await taxi_reposition_relocator.post(
        'service/cron', json={'task_name': 'reactor_manager-queues'},
    )
    assert response.status_code == 200
    assert _mock_queue.times_called == 0

    assert get_reactions_to_queue() == INITIAL_QUEUE_REACTIONS
