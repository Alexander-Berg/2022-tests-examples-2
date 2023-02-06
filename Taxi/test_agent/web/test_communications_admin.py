import pytest

from agent.stq import notificatons as stq_notifications


PROJECT_SETTINGS = {
    'default': {'enable_chatterbox': False, 'profile_information': []},
    'calltaxi': {
        'enable_chatterbox': False,
        'main_permission': 'user_calltaxi',
        'profile_information': ['phones'],
    },
}


@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False, 'profile_information': []},
        'calltaxi': {
            'enable_chatterbox': False,
            'main_permission': 'user_calltaxi',
        },
        'taxisupport': {
            'enable_chatterbox': False,
            'main_permission': 'user_taxisupport',
        },
    },
)
@pytest.mark.parametrize(
    'login,status,expected_data',
    [
        (
            'webalex',
            200,
            {
                'teams': [
                    {'id': 'team_1', 'name': 'Team 1'},
                    {'id': 'team_2', 'name': 'Team 2'},
                    {'id': 'team_3', 'name': 'Team 3'},
                ],
                'projects': [
                    {'id': 'user_calltaxi', 'name': 'calltaxi'},
                    {'id': 'user_taxisupport', 'name': 'taxisupport'},
                ],
                'logins': [],
            },
        ),
    ],
)
async def test_communications_admin_targets(
        web_context, web_app_client, login, status, expected_data,
):
    response = await web_app_client.get(
        '/v1/admin/communications/targets',
        headers={'X-Yandex-Login': login, 'Accept-Language': 'ru-ru'},
    )
    assert response.status == status
    assert await response.json() == expected_data


@pytest.mark.parametrize(
    'login,json_data,status,response_content,db_expected',
    [
        (
            'webalex',
            {
                'title': 'test_1',
                'body': 'body_1',
                'link': 'link_1',
                'type': 'warning',
                'targets': [],
            },
            201,
            {
                'targets': [],
                'target_users': 6,
                'viewed_users': 0,
                'title': 'test_1',
                'body': 'body_1',
                'link': 'link_1',
                'type': 'warning',
            },
            [
                {
                    'login': 'liambaev',
                    'title': 'test_1',
                    'body': 'body_1',
                    'notification_type': 'warning',
                    'url_link': 'link_1',
                },
                {
                    'login': 'login_1',
                    'title': 'test_1',
                    'body': 'body_1',
                    'notification_type': 'warning',
                    'url_link': 'link_1',
                },
                {
                    'login': 'login_2',
                    'title': 'test_1',
                    'body': 'body_1',
                    'notification_type': 'warning',
                    'url_link': 'link_1',
                },
                {
                    'login': 'login_3',
                    'title': 'test_1',
                    'body': 'body_1',
                    'notification_type': 'warning',
                    'url_link': 'link_1',
                },
                {
                    'login': 'login_4',
                    'title': 'test_1',
                    'body': 'body_1',
                    'notification_type': 'warning',
                    'url_link': 'link_1',
                },
                {
                    'login': 'webalex',
                    'title': 'test_1',
                    'body': 'body_1',
                    'notification_type': 'warning',
                    'url_link': 'link_1',
                },
            ],
        ),
        (
            'webalex',
            {
                'title': 'test_1',
                'body': 'body_1',
                'link': 'link_1',
                'type': 'warning',
                'targets': [
                    {'type': 'logins', 'value': ['login_1', 'login_2']},
                ],
            },
            201,
            {
                'targets': [
                    {'type': 'logins', 'value': ['login_1', 'login_2']},
                ],
                'target_users': 2,
                'viewed_users': 0,
                'title': 'test_1',
                'body': 'body_1',
                'link': 'link_1',
                'type': 'warning',
            },
            [
                {
                    'login': 'login_1',
                    'title': 'test_1',
                    'body': 'body_1',
                    'notification_type': 'warning',
                    'url_link': 'link_1',
                },
                {
                    'login': 'login_2',
                    'title': 'test_1',
                    'body': 'body_1',
                    'notification_type': 'warning',
                    'url_link': 'link_1',
                },
            ],
        ),
        (
            'webalex',
            {
                'title': 'test_1',
                'body': 'body_1',
                'link': 'link_1',
                'type': 'warning',
                'targets': [{'type': 'teams', 'value': ['team_1']}],
            },
            201,
            {
                'targets': [{'type': 'teams', 'value': ['team_1']}],
                'target_users': 3,
                'viewed_users': 0,
                'title': 'test_1',
                'body': 'body_1',
                'link': 'link_1',
                'type': 'warning',
            },
            [
                {
                    'login': 'liambaev',
                    'title': 'test_1',
                    'body': 'body_1',
                    'notification_type': 'warning',
                    'url_link': 'link_1',
                },
                {
                    'login': 'login_1',
                    'title': 'test_1',
                    'body': 'body_1',
                    'notification_type': 'warning',
                    'url_link': 'link_1',
                },
                {
                    'login': 'webalex',
                    'title': 'test_1',
                    'body': 'body_1',
                    'notification_type': 'warning',
                    'url_link': 'link_1',
                },
            ],
        ),
        (
            'webalex',
            {
                'title': 'test_1',
                'body': 'body_1',
                'link': 'link_1',
                'type': 'warning',
                'targets': [{'type': 'projects', 'value': ['user']}],
            },
            201,
            {
                'targets': [{'type': 'projects', 'value': ['user']}],
                'target_users': 1,
                'viewed_users': 0,
                'title': 'test_1',
                'body': 'body_1',
                'link': 'link_1',
                'type': 'warning',
            },
            [
                {
                    'login': 'webalex',
                    'title': 'test_1',
                    'body': 'body_1',
                    'notification_type': 'warning',
                    'url_link': 'link_1',
                },
            ],
        ),
    ],
)
async def test_communications_admin_create(
        web_context,
        web_app_client,
        stq,
        stq3_context,
        login,
        json_data,
        status,
        response_content,
        db_expected,
):

    response = await web_app_client.post(
        '/v1/admin/communications',
        headers={'X-Yandex-Login': login, 'Accept-Language': 'ru-ru'},
        json=json_data,
    )
    assert stq.agent_notifications_queue.times_called == 1
    task = stq.agent_notifications_queue.next_call()
    await stq_notifications.task(stq3_context, **task['kwargs'])

    assert stq.is_empty

    assert response.status == status
    content = await response.json()
    response_content['id'] = content['id']
    response_content['created_at'] = content['created_at']
    response_content['creator'] = content['creator']
    assert content['creator'] == login
    assert content == response_content

    async with web_context.pg.slave_pool.acquire() as conn:
        notifications_query = """SELECT login,title,body,notification_type,
        url_link FROM agent.notifications ORDER BY login"""
        notifications_result = await conn.fetch(notifications_query)
        assert len(notifications_result) == response_content['target_users']
        assert [dict(row) for row in notifications_result] == db_expected

    async with web_context.pg.slave_pool.acquire() as conn:
        query = 'SELECT mass_id from agent.notifications'
        for row in await conn.fetch(query):
            assert row['mass_id'] == response_content['id']


@pytest.mark.parametrize(
    'url,status,expected_response',
    [
        (
            '/v1/admin/communications?limit=1',
            200,
            [
                {
                    'id': 'faadb32303664af38b75ff2653e1bb43',
                    'creator': 'webalex',
                    'created_at': '2022-04-20T16:10:02Z',
                    'target_users': 100,
                    'viewed_users': 0,
                    'title': 'Title 2',
                    'body': 'Body 2',
                    'link': 'url 2',
                    'type': 'warning',
                    'targets': [{'type': 'projects', 'value': ['calltaxi']}],
                },
            ],
        ),
        (
            '/v1/admin/communications?limit=1&last_created_at={}'.format(
                '2022-04-20T16:10:02Z',
            ),
            200,
            [
                {
                    'id': '63cae574fca043d8833d7bb9a9bb7ef1',
                    'creator': 'webalex',
                    'created_at': '2022-04-20T15:03:02Z',
                    'target_users': 100,
                    'viewed_users': 0,
                    'title': 'Title 1',
                    'body': 'Body 1',
                    'link': 'url 1',
                    'type': 'warning',
                    'targets': [{'type': 'teams', 'value': ['calls']}],
                },
            ],
        ),
        (
            '/v1/admin/communications',
            200,
            [
                {
                    'id': 'faadb32303664af38b75ff2653e1bb43',
                    'creator': 'webalex',
                    'created_at': '2022-04-20T16:10:02Z',
                    'target_users': 100,
                    'viewed_users': 0,
                    'title': 'Title 2',
                    'body': 'Body 2',
                    'link': 'url 2',
                    'type': 'warning',
                    'targets': [{'type': 'projects', 'value': ['calltaxi']}],
                },
                {
                    'id': '63cae574fca043d8833d7bb9a9bb7ef1',
                    'creator': 'webalex',
                    'created_at': '2022-04-20T15:03:02Z',
                    'target_users': 100,
                    'viewed_users': 0,
                    'title': 'Title 1',
                    'body': 'Body 1',
                    'link': 'url 1',
                    'type': 'warning',
                    'targets': [{'type': 'teams', 'value': ['calls']}],
                },
            ],
        ),
    ],
)
async def test_communications_admin_list(
        web_context, web_app_client, url, status, expected_response,
):
    response = await web_app_client.get(
        url, headers={'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
    )
    assert response.status == status
    assert await response.json() == expected_response
