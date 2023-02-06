# pylint: disable=C0302
import pytest

GOOD_HEADERS: dict = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'}
AVATAR_TEMPLATE = 'https://center.yandex-team.ru/api/v1/user/%s/photo/300.jpg'
S3_FILE_TEMPLATE = 'https://s3.mds.yandex.net/taxiagent/%s'


@pytest.mark.now('2022-01-01T00:00:00')
@pytest.mark.parametrize(
    'creator, channel_id, name,description,avatar,'
    'subscribed_teams,admins,subscribed_projects,'
    'teams_with_read_access,projects_with_read_access,public,status',
    [
        (
            'team_1_lead',
            '12345',
            'Первый канал',
            'описание',
            'avatar_1',
            ['team_1'],
            ['team_1_lead'],
            ['project_1'],
            ['team_1', 'team_2'],
            ['project_1', 'project_2'],
            True,
            201,
        ),
        (
            'team_2_lead',
            '12345',
            'Первый канал',
            'описание',
            'avatar_1',
            ['team_1'],
            ['team_2_lead'],
            ['project_1'],
            [],
            [],
            False,
            403,
        ),
        (
            'team_1_lead',
            'existing_channel',
            'existing_channel_name',
            'existing_channel_description',
            'avatar_1',
            ['team_1'],
            ['team_1_lead'],
            ['project_1'],
            ['team_1'],
            ['project_1'],
            False,
            409,
        ),
        (
            'team_1_lead',
            'channel_without_admin',
            'channel_without_admin_name',
            'channel_without_admin_description',
            'avatar_1',
            ['team_1'],
            [],
            ['project_1'],
            [],
            [],
            False,
            400,
        ),
        (
            'team_1_lead',
            'channel_without_subscribers',
            'channel_without_subscribers_name',
            'channel_without_subscribers_description',
            'avatar_1',
            [],
            ['team_1_lead'],
            [],
            [],
            [],
            False,
            201,
        ),
        (
            'team_1_lead',
            'channel_with_short_name',
            '',
            'channel_with_short_name',
            'avatar_1',
            [],
            ['team_1_lead'],
            [],
            [],
            [],
            False,
            400,
        ),
    ],
)
async def test_channel_create(
        web_app_client,
        web_context,
        creator,
        channel_id,
        name,
        description,
        subscribed_teams,
        admins,
        status,
        avatar,
        subscribed_projects,
        teams_with_read_access,
        projects_with_read_access,
        public,
):
    response = await web_app_client.post(
        '/channel/create',
        headers={'X-Yandex-Login': creator, 'Accept-Language': 'ru-ru'},
        json={
            'channel_id': channel_id,
            'name': name,
            'description': description,
            'subscribed_teams': subscribed_teams,
            'admins': admins,
            'subscribed_projects': subscribed_projects,
            'avatar_file_id': avatar,
            'teams_with_read_access': teams_with_read_access,
            'projects_with_read_access': projects_with_read_access,
            'public': public,
        },
    )

    assert response.status == status
    if response.status == 200:
        content = await response.json()
        assert content['channel_id'] == channel_id
        assert content['name'] == name
        assert content['description'] == description
        assert content['subscribed_teams'] == subscribed_teams
        assert content['admins'] == admins
        assert content['avatar'].find(avatar) != -1
        assert content['teams_with_read_access'] == teams_with_read_access
        assert (
            content['projects_with_read_access'] == projects_with_read_access
        )
        assert content['public'] == public

    query = f"""SELECT * FROM agent.channels
                where key = \'{channel_id}\'"""
    async with web_context.pg.slave_pool.acquire() as conn:
        rows = await conn.fetch(query)
        expected_rows = 1 if status in (201, 409) else 0
        assert len(rows) == expected_rows
        if expected_rows:
            created_channel = rows[0]
            assert created_channel['key'] == channel_id
            assert created_channel['creator'] == creator
            assert created_channel['name'] == name
            assert created_channel['deleted'] is False
            assert created_channel['description'] == description

    query = f"""SELECT * FROM agent.channel_admins
                where channel_key = \'{channel_id}\'"""
    async with web_context.pg.slave_pool.acquire() as conn:
        rows = await conn.fetch(query)
        expected_saved_admins = len(admins) if status in (201, 409) else 0
        saved_admins = dict(rows)
        assert len(saved_admins) == expected_saved_admins
        if expected_saved_admins:
            for admin in admins:
                assert admin in saved_admins
                assert saved_admins[admin] == channel_id

    query = f"""SELECT * FROM agent.team_subscriptions
                where channel_key = \'{channel_id}\'"""
    async with web_context.pg.slave_pool.acquire() as conn:
        rows = await conn.fetch(query)
        expected_team_subscriptions = (
            len(subscribed_teams) if status in (201, 409) else 0
        )
        saved_subscribed_teams = dict(rows)
        assert len(saved_subscribed_teams) == expected_team_subscriptions
        if expected_team_subscriptions:
            for team in subscribed_teams:
                assert team in saved_subscribed_teams
                assert saved_subscribed_teams[team] == channel_id

    query = f"""SELECT * FROM agent.project_subscriptions
                where channel_key = \'{channel_id}\'"""
    async with web_context.pg.slave_pool.acquire() as conn:
        rows = await conn.fetch(query)
        expected_project_subscriptions = (
            len(subscribed_projects) if status in (201, 409) else 0
        )
        saved_subscribed_projects = dict(rows)
        assert len(saved_subscribed_projects) == expected_project_subscriptions
        if expected_project_subscriptions:
            for projects in subscribed_projects:
                assert projects in saved_subscribed_projects
                assert saved_subscribed_projects[projects] == channel_id

    query = f"""SELECT * FROM agent.channels_teams_access
                where channel_key = \'{channel_id}\'"""
    async with web_context.pg.slave_pool.acquire() as conn:
        rows = await conn.fetch(query)
        expected_teams_with_read_access = (
            len(teams_with_read_access) if status in (201, 409) else 0
        )
        saved_teams_with_read_access = dict(rows)
        assert (
            len(saved_teams_with_read_access)
            == expected_teams_with_read_access
        )
        if expected_teams_with_read_access:
            for team in teams_with_read_access:
                assert team in saved_teams_with_read_access
                assert saved_teams_with_read_access[team] == channel_id

    query = f"""SELECT * FROM agent.channels_projects_access
                where channel_key = \'{channel_id}\'"""
    async with web_context.pg.slave_pool.acquire() as conn:
        rows = await conn.fetch(query)
        expected_projects_with_access = (
            len(projects_with_read_access) if status in (201, 409) else 0
        )
        saved_projects_with_read_access = dict(rows)
        assert (
            len(saved_projects_with_read_access)
            == expected_projects_with_access
        )
        if expected_projects_with_access:
            for project in projects_with_read_access:
                assert project in saved_projects_with_read_access
                assert saved_projects_with_read_access[project] == channel_id


@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {},
        'project_1': {'main_permission': 'user_project_1'},
    },
)
@pytest.mark.parametrize(
    'viewer, channel_id, expected_response, status',
    [
        (
            'team_1_lead',
            'existing_channel',
            {
                'channel_id': 'existing_channel',
                'created': '2020-01-01T07:00:00+00:00',
                'creator': 'team_1_lead',
                'name': 'existing_channel_name',
                'deleted': False,
                'description': 'existing_channel_description',
                'admins': ['team_1_lead'],
                'subscribed_teams': ['team_1'],
                'subscribed_projects': ['project_1'],
                'subscribers': 2,
                'avatar': 'https://s3.mds.yandex.net/taxiagent/avatar_id',
                'teams_with_read_access': ['team_1'],
                'projects_with_read_access': ['project_1'],
                'public': True,
            },
            200,
        ),
        (
            'team_1_lead',
            'existing_channel_without_subscribers',
            {
                'channel_id': 'existing_channel_without_subscribers',
                'created': '2020-01-01T07:00:00+00:00',
                'creator': 'team_1_lead',
                'name': 'existing_channel_without_subscribers_name',
                'deleted': False,
                'description': (
                    'existing_channel_without_subscribers_description'
                ),
                'admins': ['team_1_lead'],
                'subscribers': 0,
                'avatar': 'https://s3.mds.yandex.net/taxiagent/avatar_id',
                'teams_with_read_access': [],
                'projects_with_read_access': [],
                'public': True,
            },
            200,
        ),
        ('team_2_lead', 'existing_channel', None, 403),
        ('team_1_lead', 'not_existing_channel', {}, 404),
    ],
)
async def test_channel_full_get(
        web_app_client,
        web_context,
        viewer,
        channel_id,
        expected_response,
        status,
):
    response = await web_app_client.get(
        f'/channel/{channel_id}/full',
        headers={'X-Yandex-Login': viewer, 'Accept-Language': 'ru-ru'},
    )

    assert response.status == status
    if response.status == 200:
        assert await response.json() == expected_response


@pytest.mark.parametrize(
    'viewer, channel_id, expected_response, status',
    [
        (
            'team_1_lead',
            'existing_channel',
            {
                'channel_id': 'existing_channel',
                'name': 'existing_channel_name',
                'deleted': False,
                'description': 'existing_channel_description',
                'subscribers': 1,
                'subscribed': True,
                'can_edit': True,
                'can_unsubscribe': False,
                'avatar': 'https://s3.mds.yandex.net/taxiagent/avatar_id',
            },
            200,
        ),
        (
            'team_2_lead',
            'existing_channel',
            {
                'channel_id': 'existing_channel',
                'name': 'existing_channel_name',
                'deleted': False,
                'description': 'existing_channel_description',
                'subscribers': 1,
                'subscribed': False,
                'can_edit': False,
                'can_unsubscribe': True,
                'avatar': 'https://s3.mds.yandex.net/taxiagent/avatar_id',
            },
            200,
        ),
        (
            'team_1_lead',
            'existing_channel_without_subscribers',
            {
                'channel_id': 'existing_channel_without_subscribers',
                'name': 'existing_channel_without_subscribers_name',
                'deleted': False,
                'description': (
                    'existing_channel_without_subscribers_description'
                ),
                'subscribers': 0,
                'subscribed': False,
                'can_edit': True,
                'can_unsubscribe': False,
                'avatar': 'https://s3.mds.yandex.net/taxiagent/avatar_id',
            },
            200,
        ),
        ('team_1_lead', 'not_existing_channel', {}, 404),
        ('team_1_lead', 'deleted_channel', {}, 404),
        ('no_access_user', 'private_channel', {}, 403),
    ],
)
async def test_channel_get(
        web_app_client,
        web_context,
        viewer,
        channel_id,
        expected_response,
        status,
):
    response = await web_app_client.get(
        f'/channel/{channel_id}',
        headers={'X-Yandex-Login': viewer, 'Accept-Language': 'ru-ru'},
    )

    assert response.status == status
    if response.status == 200:
        assert await response.json() == expected_response


@pytest.mark.parametrize(
    'editor, data, expected_response, status',
    [
        (
            'team_1_lead',
            {
                'avatar_file_id': 'new_avatar',
                'channel_id': 'existing_channel',
                'name': 'existing_channel_name',
                'description': 'existing_channel_description',
                'subscribed_teams': ['team_1'],
                'admins': ['team_1_lead'],
                'subscribed_projects': ['new_project'],
                'teams_with_read_access': ['team_2'],
                'projects_with_read_access': ['project_2'],
                'public': True,
            },
            {
                'avatar': 'https://s3.mds.yandex.net/taxiagent/new_avatar',
                'channel_id': 'existing_channel',
                'name': 'existing_channel_name',
                'description': 'existing_channel_description',
                'subscribed_teams': ['team_1'],
                'admins': ['team_1_lead'],
                'subscribed_projects': ['new_project'],
                'teams_with_read_access': ['team_1', 'team_2'],
                'projects_with_read_access': ['new_project', 'project_2'],
                'public': True,
            },
            200,
        ),
        (
            'team_1_lead',
            {
                'avatar_file_id': 'new_avatar',
                'channel_id': 'existing_channel',
                'name': 'new_existing_channel_name',
                'description': 'new_existing_channel_description',
                'subscribed_teams': ['team_2', 'team_3'],
                'admins': ['team_2_lead', 'team_3_lead'],
                'subscribed_projects': [],
                'teams_with_read_access': [],
                'projects_with_read_access': [],
                'public': True,
            },
            {
                'avatar': 'https://s3.mds.yandex.net/taxiagent/new_avatar',
                'channel_id': 'existing_channel',
                'name': 'new_existing_channel_name',
                'description': 'new_existing_channel_description',
                'subscribed_teams': ['team_2', 'team_3'],
                'admins': ['team_2_lead', 'team_3_lead'],
                'subscribed_projects': [],
                'teams_with_read_access': ['team_2', 'team_3'],
                'projects_with_read_access': [],
                'public': True,
            },
            200,
        ),
        (
            'team_2_lead',
            {
                'avatar_file_id': 'new_avatar',
                'channel_id': 'existing_channel',
                'name': 'new_existing_channel_name',
                'description': 'new_existing_channel_description',
                'subscribed_teams': ['team_2'],
                'admins': ['team_1_lead', 'team_2_lead'],
                'subscribed_projects': [],
                'teams_with_read_access': [],
                'projects_with_read_access': [],
                'public': True,
            },
            None,
            403,
        ),
        (
            'team_1_lead',
            {
                'avatar_file_id': 'new_avatar',
                'channel_id': 'not_existing_channel',
                'name': 'new_not_existing_channel_name',
                'description': 'new_not_existing_channel_description',
                'subscribed_teams': ['team_2'],
                'admins': ['team_1_lead', 'team_2_lead'],
                'subscribed_projects': [],
                'teams_with_read_access': [],
                'projects_with_read_access': [],
                'public': True,
            },
            None,
            404,
        ),
        (
            'team_1_lead',
            {
                'avatar_file_id': 'new_avatar',
                'channel_id': 'existing_channel',
                'name': 'existing_channel_name',
                'description': 'existing_channel_description',
                'subscribed_teams': ['team_1'],
                'admins': [],
                'subscribed_projects': [],
                'teams_with_read_access': [],
                'projects_with_read_access': [],
                'public': True,
            },
            None,
            400,
        ),
        (
            'team_1_lead',
            {
                'avatar_file_id': 'new_avatar',
                'channel_id': 'existing_channel',
                'name': 'existing_channel',
                'description': 'existing_channel',
                'subscribed_teams': [],
                'admins': ['team_1_lead'],
                'subscribed_projects': [],
                'teams_with_read_access': [],
                'projects_with_read_access': [],
                'public': True,
            },
            {
                'avatar': 'https://s3.mds.yandex.net/taxiagent/new_avatar',
                'channel_id': 'existing_channel',
                'name': 'existing_channel',
                'description': 'existing_channel',
                'subscribed_teams': [],
                'admins': ['team_1_lead'],
                'subscribed_projects': [],
                'teams_with_read_access': [],
                'projects_with_read_access': [],
                'public': True,
            },
            200,
        ),
        (
            'team_1_lead',
            {
                'avatar_file_id': 'new_avatar',
                'channel_id': 'existing_channel_without_subscribers',
                'name': 'existing_channel_without_subscribers_name',
                'description': (
                    'existing_channel_without_subscribers_description'
                ),
                'subscribed_teams': ['team_1'],
                'admins': ['team_1_lead'],
                'subscribed_projects': [],
                'teams_with_read_access': [],
                'projects_with_read_access': [],
                'public': True,
            },
            {
                'avatar': 'https://s3.mds.yandex.net/taxiagent/new_avatar',
                'channel_id': 'existing_channel_without_subscribers',
                'name': 'existing_channel_without_subscribers_name',
                'description': (
                    'existing_channel_without_subscribers_description'
                ),
                'subscribed_teams': ['team_1'],
                'admins': ['team_1_lead'],
                'subscribed_projects': [],
                'teams_with_read_access': ['team_1'],
                'projects_with_read_access': [],
                'public': True,
            },
            200,
        ),
    ],
)
async def test_channel_edit(
        web_app_client, web_context, editor, data, expected_response, status,
):
    response = await web_app_client.post(
        '/channel/edit',
        headers={'X-Yandex-Login': editor, 'Accept-Language': 'ru-ru'},
        json=data,
    )

    assert response.status == status
    if response.status == 200:
        assert await response.json() == expected_response


@pytest.mark.parametrize(
    'input_data,user,status',
    [
        ({'channel_id': 'existing_channel'}, 'team_1_lead', 200),
        ({'channel_id': 'existing_channel'}, 'team_2_lead', 403),
        ({'channel_id': 'not_existing_channel'}, 'team_1_lead', 404),
    ],
)
async def test_channel_delete(web_app_client, input_data, user, status):
    response = await web_app_client.post(
        '/channel/delete',
        headers={'X-Yandex-Login': user, 'Accept-Language': 'ru-ru'},
        json=input_data,
    )
    assert response.status == status


@pytest.mark.parametrize(
    'input_data,user,status',
    [
        ({'channel_id': 'channel_1'}, 'team_1_lead', 200),
        ({'channel_id': 'channel_1'}, 'subscribed_user', 200),
        ({'channel_id': 'not_existing_channel'}, 'team_1_lead', 404),
        ({'channel_id': 'private_channel'}, 'no_access_user', 403),
    ],
)
async def test_channel_subscribe(
        web_app_client, web_context, input_data, user, status,
):
    response = await web_app_client.post(
        '/channel/subscribe',
        json=input_data,
        headers={'X-Yandex-Login': user, 'Accept-Language': 'ru-ru'},
    )
    assert response.status == status

    if status == 200:
        query = f"""SELECT * FROM agent.subscriptions
                    where login = \'{user}\'"""
        async with web_context.pg.slave_pool.acquire() as conn:
            rows = await conn.fetch(query)
            assert len(rows) == 1
            assert rows[0]['login'] == user
            assert rows[0]['channel_key'] == input_data['channel_id']


@pytest.mark.parametrize(
    'input_data,user,status',
    [
        ({'channel_id': 'channel_1'}, 'team_1_lead', 200),
        ({'channel_id': 'channel_1'}, 'subscribed_user', 200),
        ({'channel_id': 'not_existing_channel'}, 'team_1_lead', 404),
        ({'channel_id': 'private_channel'}, 'no_access_user', 403),
    ],
)
async def test_channel_unsubscribe(
        web_app_client, web_context, input_data, user, status,
):
    response = await web_app_client.post(
        '/channel/unsubscribe',
        json=input_data,
        headers={'X-Yandex-Login': user, 'Accept-Language': 'ru-ru'},
    )
    assert response.status == status

    if status == 200:
        query = f"""SELECT * FROM agent.subscriptions
                    where login = \'{user}\'
                    and channel_key = \'{input_data['channel_id']}\'"""
        async with web_context.pg.slave_pool.acquire() as conn:
            rows = await conn.fetch(query)
            assert not rows


@pytest.mark.now('2022-01-01T10:00:00')
@pytest.mark.parametrize(
    'input_data,user,expected_response,status',
    [
        (
            {
                'post_id': 'post_1',
                'channels': ['existing_channel', 'channel_1'],
                'text': '!@#$%%^&*()_+-\"\'',
                'images': ['image_1', 'image_2'],
                'format': 'text',
            },
            'team_1_lead',
            {
                'id': 'post_1',
                'author': {
                    'first_name': 'team_1_lead',
                    'last_name': 'team_1_lead',
                    'login': 'team_1_lead',
                    'avatar': AVATAR_TEMPLATE % 'team_1_lead',
                },
                'channels': [
                    {
                        'channel_id': 'existing_channel',
                        'channel_name': 'existing_channel_name',
                    },
                    {
                        'channel_id': 'channel_1',
                        'channel_name': 'channel_1_name',
                    },
                ],
                'likes': 0,
                'views': 0,
                'images': [
                    {
                        'file_id': 'image_1',
                        'url': 'https://s3.mds.yandex.net/taxiagent/image_1',
                    },
                    {
                        'file_id': 'image_2',
                        'url': 'https://s3.mds.yandex.net/taxiagent/image_2',
                    },
                ],
                'text': '!@#$%%^&*()_+-\"\'',
                'format': 'text',
                'can_manage': True,
                'liked': False,
                'viewed': False,
            },
            201,
        ),
        (
            {
                'post_id': 'existing_post',
                'channels': ['existing_channel', 'channel_1'],
                'text': 'text',
                'format': 'text',
            },
            'team_1_lead',
            None,
            409,
        ),
        (
            {
                'post_id': 'post_1',
                'channels': ['existing_channel', 'not_existing_channel'],
                'text': '!@#$%%^&*()_+-\"\'',
                'format': 'text',
            },
            'team_1_lead',
            None,
            404,
        ),
        (
            {
                'post_id': 'post_1',
                'channels': ['existing_channel', 'channel_1_name'],
                'text': '!@#$%%^&*()_+-\"\'',
                'format': 'text',
            },
            'team_2_lead',
            None,
            403,
        ),
        (
            {
                'post_id': 'post_1',
                'channels': [],
                'text': '!@#$%%^&*()_+-\"\'',
                'format': 'text',
            },
            'team_1_lead',
            None,
            400,
        ),
        (
            {
                'post_id': 'post_1',
                'channels': ['existing_channel', 'channel_1'],
                'text': '!@#$%%^&*()_+-\"\'',
                'images': [],
                'format': 'text',
            },
            'team_1_lead',
            {
                'id': 'post_1',
                'author': {
                    'first_name': 'team_1_lead',
                    'last_name': 'team_1_lead',
                    'login': 'team_1_lead',
                    'avatar': AVATAR_TEMPLATE % 'team_1_lead',
                },
                'channels': [
                    {
                        'channel_id': 'existing_channel',
                        'channel_name': 'existing_channel_name',
                    },
                    {
                        'channel_id': 'channel_1',
                        'channel_name': 'channel_1_name',
                    },
                ],
                'images': [],
                'likes': 0,
                'views': 0,
                'text': '!@#$%%^&*()_+-\"\'',
                'format': 'text',
                'can_manage': True,
                'liked': False,
                'viewed': False,
            },
            201,
        ),
        (
            {
                'post_id': 'post_1',
                'channels': ['existing_channel', 'channel_1'],
                'text': '!@#$%%^&*()_+-\"\'',
                'format': 'text',
            },
            'team_1_lead',
            {
                'id': 'post_1',
                'author': {
                    'first_name': 'team_1_lead',
                    'last_name': 'team_1_lead',
                    'login': 'team_1_lead',
                    'avatar': AVATAR_TEMPLATE % 'team_1_lead',
                },
                'channels': [
                    {
                        'channel_id': 'existing_channel',
                        'channel_name': 'existing_channel_name',
                    },
                    {
                        'channel_id': 'channel_1',
                        'channel_name': 'channel_1_name',
                    },
                ],
                'images': [],
                'likes': 0,
                'views': 0,
                'text': '!@#$%%^&*()_+-\"\'',
                'format': 'text',
                'can_manage': True,
                'liked': False,
                'viewed': False,
            },
            201,
        ),
    ],
)
async def test_post_create(
        web_app_client,
        web_context,
        input_data,
        user,
        expected_response,
        status,
):
    response = await web_app_client.post(
        '/post/create',
        json=input_data,
        headers={'X-Yandex-Login': user, 'Accept-Language': 'ru-ru'},
    )
    assert response.status == status

    if status == 201:
        body = await response.json()
        body.pop('created')
        assert body == expected_response


@pytest.mark.now('2022-01-01T10:00:00')
@pytest.mark.parametrize(
    'input_data,user,expected_response,status',
    [
        (
            {
                'post_id': 'existing_post',
                'channels': ['existing_channel'],
                'text': '!@#$%%^&*()_+-\"\'',
                'images': ['new_image'],
                'format': 'new_formet',
            },
            'team_1_lead',
            {
                'id': 'existing_post',
                'author': {
                    'first_name': 'team_1_lead',
                    'last_name': 'team_1_lead',
                    'login': 'team_1_lead',
                    'avatar': AVATAR_TEMPLATE % 'team_1_lead',
                },
                'channels': [
                    {
                        'channel_id': 'existing_channel',
                        'channel_name': 'existing_channel_name',
                    },
                ],
                'likes': 0,
                'views': 0,
                'images': [
                    {
                        'file_id': 'new_image',
                        'url': 'https://s3.mds.yandex.net/taxiagent/new_image',
                    },
                ],
                'text': '!@#$%%^&*()_+-\"\'',
                'format': 'new_formet',
                'can_manage': True,
                'liked': False,
                'viewed': False,
            },
            200,
        ),
        (
            {
                'post_id': 'not_existing_post',
                'channels': ['existing_channel'],
                'text': '!@#$%%^&*()_+-\"\'',
                'images': ['image_1'],
                'format': 'new_formet',
            },
            'team_1_lead',
            None,
            404,
        ),
        (
            {
                'post_id': 'existing_post',
                'channels': ['existing_channel'],
                'text': '!@#$%%^&*()_+-\"\'',
                'images': ['image_1'],
                'format': 'new_formet',
            },
            'team_2_lead',
            None,
            403,
        ),
        (
            {
                'post_id': 'existing_post',
                'channels': [],
                'text': '!@#$%%^&*()_+-\"\'',
                'images': ['image_1'],
                'format': 'new_formet',
            },
            'team_1_lead',
            None,
            400,
        ),
    ],
)
async def test_post_edit(
        web_app_client,
        web_context,
        input_data,
        user,
        expected_response,
        status,
):
    response = await web_app_client.post(
        '/post/edit',
        json=input_data,
        headers={'X-Yandex-Login': user, 'Accept-Language': 'ru-ru'},
    )
    assert response.status == status

    if status == 200:
        body = await response.json()
        body.pop('created')
        assert body == expected_response


@pytest.mark.parametrize(
    'viewer, post_id, expected_response, status',
    [
        (
            'team_1_lead',
            'existing_post_1',
            {
                'id': 'existing_post_1',
                'author': {
                    'first_name': 'team_1_lead',
                    'last_name': 'team_1_lead',
                    'login': 'team_1_lead',
                    'avatar': AVATAR_TEMPLATE % 'team_1_lead',
                },
                'channels': [
                    {
                        'channel_id': 'existing_channel',
                        'channel_name': 'existing_channel_name',
                    },
                    {
                        'channel_id': 'channel_1',
                        'channel_name': 'channel_1_name',
                    },
                ],
                'images': [],
                'likes': 1,
                'views': 1,
                'text': 'text',
                'format': 'text',
                'can_manage': True,
                'liked': True,
                'viewed': True,
            },
            200,
        ),
        (
            'team_1_lead',
            'existing_post_2',
            {
                'id': 'existing_post_2',
                'author': {
                    'first_name': 'team_2_lead',
                    'last_name': 'team_2_lead',
                    'login': 'team_2_lead',
                    'avatar': AVATAR_TEMPLATE % 'team_2_lead',
                },
                'channels': [
                    {
                        'channel_id': 'channel_1',
                        'channel_name': 'channel_1_name',
                    },
                ],
                'likes': 0,
                'views': 0,
                'text': 'text',
                'format': 'text',
                'images': [
                    {
                        'file_id': 'image_1',
                        'url': 'https://s3.mds.yandex.net/taxiagent/image_1',
                    },
                ],
                'can_manage': False,
                'liked': False,
                'viewed': False,
            },
            200,
        ),
        ('team_1_lead', 'not_existing_post', None, 404),
        ('team_1_lead', 'deleted_post', None, 404),
        ('no_access_user', 'private_channel_post', None, 403),
    ],
)
async def test_post_get(
        web_app_client,
        web_context,
        viewer,
        post_id,
        expected_response,
        status,
):
    response = await web_app_client.get(
        f'/post/{post_id}',
        headers={'X-Yandex-Login': viewer, 'Accept-Language': 'ru-ru'},
    )

    assert response.status == status
    if response.status == 200:
        body = await response.json()
        body.pop('created')
        assert body == expected_response


@pytest.mark.parametrize(
    'user,input_data,expected_db_records_count,status',
    [
        ('team_1_lead', {'post_id': 'existing_post', 'liked': True}, 1, 200),
        ('team_1_lead', {'post_id': 'existing_post_1', 'liked': True}, 1, 200),
        ('team_2_lead', {'post_id': 'existing_post_1', 'liked': True}, 1, 200),
        (
            'team_1_lead',
            {'post_id': 'existing_post_1', 'liked': False},
            0,
            200,
        ),
        ('team_1_lead', {'post_id': 'existing_post', 'liked': False}, 0, 200),
        (
            'team_1_lead',
            {'post_id': 'not_existing_post', 'liked': False},
            0,
            404,
        ),
        (
            'no_access_user',
            {'post_id': 'private_channel_post', 'liked': True},
            0,
            403,
        ),
    ],
)
async def test_post_like(
        web_app_client,
        web_context,
        user,
        input_data,
        expected_db_records_count,
        status,
):
    response = await web_app_client.post(
        '/post/like',
        json=input_data,
        headers={'X-Yandex-Login': user, 'Accept-Language': 'ru-ru'},
    )
    assert response.status == status

    if status == 200:
        query = f"""SELECT * FROM agent.post_likes
                    where login = \'{user}\'
                    and post_id = \'{input_data['post_id']}\'"""
        async with web_context.pg.slave_pool.acquire() as conn:
            rows = await conn.fetch(query)
            assert len(rows) == expected_db_records_count


@pytest.mark.parametrize(
    'user,input_data,status',
    [
        ('team_1_lead', {'post_id': 'existing_post'}, 200),
        ('team_1_lead', {'post_id': 'existing_post_2'}, 403),
        ('team_1_lead', {'post_id': 'not_existing_post'}, 404),
    ],
)
async def test_post_delete(
        web_app_client, web_context, input_data, user, status,
):
    response = await web_app_client.post(
        '/post/delete',
        json=input_data,
        headers={'X-Yandex-Login': user, 'Accept-Language': 'ru-ru'},
    )
    assert response.status == status

    if status == 200:
        query = f"""SELECT * FROM agent.news
                    where id = \'{input_data['post_id']}\'"""
        async with web_context.pg.slave_pool.acquire() as conn:
            row = await conn.fetchrow(query)
            assert row['deleted']


@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'project_1': {'main_permission': 'user_project_1'},
    },
)
@pytest.mark.parametrize(
    'viewer, expected_response',
    [
        (
            'subscribed_user',
            {
                'main': [],
                'subscriptions': [
                    {
                        'channel_id': 'channel_1',
                        'name': 'channel_1_name',
                        'avatar': (
                            'https://s3.mds.yandex.net/taxiagent/avatar_id'
                        ),
                    },
                ],
            },
        ),
        (
            'user_subscribed_via_project',
            {
                'main': [
                    {
                        'channel_id': 'existing_channel',
                        'name': 'existing_channel_name',
                        'avatar': (
                            'https://s3.mds.yandex.net/taxiagent/avatar_id'
                        ),
                    },
                ],
                'subscriptions': [],
            },
        ),
        (
            'team_1_lead',
            {
                'main': [
                    {
                        'channel_id': 'existing_channel',
                        'name': 'existing_channel_name',
                        'avatar': (
                            'https://s3.mds.yandex.net/taxiagent/avatar_id'
                        ),
                    },
                    {
                        'avatar': (
                            'https://s3.mds.yandex.net/taxiagent/avatar_id'
                        ),
                        'channel_id': 'existing_channel_without_subscribers',
                        'name': 'existing_channel_without_subscribers_name',
                    },
                ],
                'subscriptions': [],
            },
        ),
        ('not_subscribed_user', {'main': [], 'subscriptions': []}),
        (
            'user_subscribed_via_team_and_manually',
            {
                'main': [
                    {
                        'channel_id': 'channel_3',
                        'name': 'channel_3_name',
                        'avatar': S3_FILE_TEMPLATE % 'channel_3_avatar_id',
                    },
                ],
                'subscriptions': [],
            },
        ),
        ('no_access_user', {'main': [], 'subscriptions': []}),
    ],
)
async def test_user_channels_get(
        web_app_client, web_context, viewer, expected_response,
):
    response = await web_app_client.get(
        '/user_channels',
        headers={'X-Yandex-Login': viewer, 'Accept-Language': 'ru-ru'},
    )

    assert await response.json() == expected_response


@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'project_2': {'main_permission': 'user_project_2'},
    },
    AGENT_FEED_RESPONSE_LENGTH=3,
)
@pytest.mark.parametrize(
    'url, viewer, expected_response',
    [
        (
            '/feed',
            'feed_test_user',
            [
                {
                    'id': 'feed_test_post_2',
                    'author': {
                        'avatar': AVATAR_TEMPLATE % 'feed_test_user',
                        'first_name': 'feed_test_user',
                        'last_name': 'feed_test_user',
                        'login': 'feed_test_user',
                    },
                    'channels': [
                        {
                            'channel_id': 'feed_test_channel_1',
                            'channel_name': 'feed_test_channel_1_name',
                        },
                        {
                            'channel_id': 'feed_test_channel_2',
                            'channel_name': 'feed_test_channel_2_name',
                        },
                        {
                            'channel_id': 'feed_test_channel_3',
                            'channel_name': 'feed_test_channel_3_name',
                        },
                    ],
                    'created': '2022-01-09T00:00:00+03:00',
                    'likes': 0,
                    'views': 0,
                    'text': 'feed_test_post_2_text',
                    'images': [],
                    'format': '',
                    'can_manage': True,
                    'liked': False,
                    'viewed': False,
                },
                {
                    'id': 'feed_test_post_3',
                    'author': {
                        'avatar': AVATAR_TEMPLATE % 'feed_test_user',
                        'first_name': 'feed_test_user',
                        'last_name': 'feed_test_user',
                        'login': 'feed_test_user',
                    },
                    'channels': [
                        {
                            'channel_id': 'feed_test_channel_3',
                            'channel_name': 'feed_test_channel_3_name',
                        },
                    ],
                    'created': '2022-01-08T00:00:00+03:00',
                    'likes': 0,
                    'views': 0,
                    'text': 'feed_test_post_3_text',
                    'images': [],
                    'format': '',
                    'can_manage': True,
                    'liked': False,
                    'viewed': False,
                },
                {
                    'id': 'feed_test_post_4',
                    'author': {
                        'avatar': AVATAR_TEMPLATE % 'feed_test_user',
                        'first_name': 'feed_test_user',
                        'last_name': 'feed_test_user',
                        'login': 'feed_test_user',
                    },
                    'channels': [
                        {
                            'channel_id': 'feed_test_channel_1',
                            'channel_name': 'feed_test_channel_1_name',
                        },
                    ],
                    'created': '2022-01-07T00:00:00+03:00',
                    'likes': 0,
                    'views': 0,
                    'text': 'feed_test_post_4_text',
                    'images': [],
                    'format': '',
                    'can_manage': True,
                    'liked': False,
                    'viewed': False,
                },
            ],
        ),
        (
            '/feed?start_post_id=feed_test_post_2',
            'feed_test_user',
            [
                {
                    'id': 'feed_test_post_3',
                    'author': {
                        'avatar': AVATAR_TEMPLATE % 'feed_test_user',
                        'first_name': 'feed_test_user',
                        'last_name': 'feed_test_user',
                        'login': 'feed_test_user',
                    },
                    'channels': [
                        {
                            'channel_id': 'feed_test_channel_3',
                            'channel_name': 'feed_test_channel_3_name',
                        },
                    ],
                    'created': '2022-01-08T00:00:00+03:00',
                    'likes': 0,
                    'views': 0,
                    'text': 'feed_test_post_3_text',
                    'images': [],
                    'format': '',
                    'can_manage': True,
                    'liked': False,
                    'viewed': False,
                },
                {
                    'id': 'feed_test_post_4',
                    'author': {
                        'avatar': AVATAR_TEMPLATE % 'feed_test_user',
                        'first_name': 'feed_test_user',
                        'last_name': 'feed_test_user',
                        'login': 'feed_test_user',
                    },
                    'channels': [
                        {
                            'channel_id': 'feed_test_channel_1',
                            'channel_name': 'feed_test_channel_1_name',
                        },
                    ],
                    'created': '2022-01-07T00:00:00+03:00',
                    'likes': 0,
                    'views': 0,
                    'text': 'feed_test_post_4_text',
                    'images': [],
                    'format': '',
                    'can_manage': True,
                    'liked': False,
                    'viewed': False,
                },
                {
                    'id': 'feed_test_post_6',
                    'author': {
                        'avatar': AVATAR_TEMPLATE % 'feed_test_user',
                        'first_name': 'feed_test_user',
                        'last_name': 'feed_test_user',
                        'login': 'feed_test_user',
                    },
                    'channels': [
                        {
                            'channel_id': 'feed_test_channel_3',
                            'channel_name': 'feed_test_channel_3_name',
                        },
                    ],
                    'created': '2022-01-05T00:00:00+03:00',
                    'likes': 0,
                    'views': 0,
                    'text': 'feed_test_post_6_text',
                    'images': [],
                    'format': '',
                    'can_manage': True,
                    'liked': False,
                    'viewed': False,
                },
            ],
        ),
        ('/feed?start_post_id=feed_test_post_6', 'feed_test_user', []),
        ('/feed', 'not_subscribed_user', []),
        (
            '/feed?channel_id=feed_test_channel_2',
            'feed_test_user',
            [
                {
                    'id': 'feed_test_post_2',
                    'author': {
                        'avatar': AVATAR_TEMPLATE % 'feed_test_user',
                        'first_name': 'feed_test_user',
                        'last_name': 'feed_test_user',
                        'login': 'feed_test_user',
                    },
                    'channels': [
                        {
                            'channel_id': 'feed_test_channel_1',
                            'channel_name': 'feed_test_channel_1_name',
                        },
                        {
                            'channel_id': 'feed_test_channel_2',
                            'channel_name': 'feed_test_channel_2_name',
                        },
                        {
                            'channel_id': 'feed_test_channel_3',
                            'channel_name': 'feed_test_channel_3_name',
                        },
                    ],
                    'created': '2022-01-09T00:00:00+03:00',
                    'likes': 0,
                    'views': 0,
                    'text': 'feed_test_post_2_text',
                    'images': [],
                    'format': '',
                    'can_manage': True,
                    'liked': False,
                    'viewed': False,
                },
            ],
        ),
        ('/feed', 'no_access_user', []),
    ],
)
async def test_feed(
        web_app_client, web_context, url, viewer, expected_response,
):
    response = await web_app_client.get(
        url, headers={'X-Yandex-Login': viewer, 'Accept-Language': 'ru-ru'},
    )

    assert await response.json() == expected_response
