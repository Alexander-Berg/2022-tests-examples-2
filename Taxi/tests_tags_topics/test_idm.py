import pytest

from testsuite.utils import ordered_object

from tests_tags_topics import constants


@pytest.fixture(name='mock_tags_v1_topics')
def _mock_tags_v1_topics(mockserver):
    def _impl(tags_service, topics):
        @mockserver.json_handler(f'/{tags_service}/v1/topics')
        def topic_handler(request):
            response_topics = []
            for topic in topics:
                response_topics.append(
                    {
                        'name': topic,
                        'description': 'topic_description',
                        'is_financial': False,
                    },
                )
            return {'items': response_topics}

        return topic_handler

    return _impl


_EMPTY_SERVICE_ROLES = {
    'slug': 'access',
    'name': 'Доступ',
    'values': {
        'topic_access': {
            'name': 'Доступ к топикам',
            'roles': {'slug': 'topic', 'name': 'Топик', 'values': {}},
        },
    },
}


@pytest.fixture(name='mock_tags_v1_topics_empty')
def _mock_tags_v1_topics_empty(mock_tags_v1_topics):
    mock_tags_v1_topics(constants.TAGS_SERVICE, [])
    mock_tags_v1_topics(constants.PASSENGER_TAGS_SERVICE, [])
    mock_tags_v1_topics(constants.EATS_TAGS_SERVICE, [])
    mock_tags_v1_topics(constants.GROCERY_TAGS_SERVICE, [])


def has_permission(pgsql, login, service, role):
    db = pgsql['tags_topics']
    cursor = db.cursor()
    cursor.execute(
        'SELECT count(1)  FROM permissions.user_roles '
        'JOIN permissions.roles '
        'on permissions.roles.id = permissions.user_roles.role_id '
        'WHERE '
        f'login = \'{login}\' AND slug = \'{role}\' '
        f'AND service = \'{service}\'',
    )

    res = cursor.fetchone()

    if res is None:
        return False

    return res[0] != 0


@pytest.mark.parametrize(
    'api, expected_code', [('info', 200), ('get-all-roles', 200)],
)
async def test_idm_get(
        taxi_tags_topics, api, expected_code, mock_tags_v1_topics_empty,
):
    response = await taxi_tags_topics.get(f'idm/{api}')
    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'api, expected_code', [('add-role', 200), ('remove-role', 200)],
)
async def test_idm_post(taxi_tags_topics, api, expected_code):
    response = await taxi_tags_topics.post(
        f'idm/{api}',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )
    assert response.status_code == expected_code


async def test_idm_info_empty(taxi_tags_topics, mock_tags_v1_topics_empty):
    response = await taxi_tags_topics.get(f'idm/info')
    assert response.status_code == 200
    expected = {
        'code': 0,
        'roles': {
            'slug': 'service',
            'name': 'Cервис тегов Такси',
            'values': {
                'tags': {
                    'name': 'Теги водителей',
                    'roles': _EMPTY_SERVICE_ROLES,
                },
                'passenger-tags': {
                    'name': 'Теги пассажиров',
                    'roles': _EMPTY_SERVICE_ROLES,
                },
                'eats-tags': {
                    'name': 'Теги еды',
                    'roles': _EMPTY_SERVICE_ROLES,
                },
                'grocery-tags': {
                    'name': 'Теги лавки',
                    'roles': _EMPTY_SERVICE_ROLES,
                },
            },
        },
    }

    assert response.json() == expected


@pytest.mark.config(
    TAGS_TOPICS_TAGS_CLIENTS_BLACKLIST=[
        'tags',
        'passenger-tags',
        'grocery-tags',
    ],
)
async def test_idm_info_empty_blacklist(
        taxi_tags_topics, mock_tags_v1_topics_empty,
):
    response = await taxi_tags_topics.get(f'idm/info')
    assert response.status_code == 200
    expected = {
        'code': 0,
        'roles': {
            'slug': 'service',
            'name': 'Cервис тегов Такси',
            'values': {
                'eats-tags': {
                    'name': 'Теги еды',
                    'roles': _EMPTY_SERVICE_ROLES,
                },
            },
        },
    }

    assert response.json() == expected


async def test_idm_info_roles(taxi_tags_topics, mock_tags_v1_topics):
    mock_tags_v1_topics(constants.TAGS_SERVICE, ['topic1', 'topic2'])
    mock_tags_v1_topics(constants.PASSENGER_TAGS_SERVICE, ['topic3', 'topic4'])
    mock_tags_v1_topics(constants.GROCERY_TAGS_SERVICE, ['topic5'])
    mock_tags_v1_topics(constants.EATS_TAGS_SERVICE, ['topic5'])
    response = await taxi_tags_topics.get(f'idm/info')
    assert response.status_code == 200
    expected = {
        'code': 0,
        'roles': {
            'slug': 'service',
            'name': 'Cервис тегов Такси',
            'values': {
                'tags': {
                    'name': 'Теги водителей',
                    'roles': {
                        'slug': 'access',
                        'name': 'Доступ',
                        'values': {
                            'topic_access': {
                                'name': 'Доступ к топикам',
                                'roles': {
                                    'slug': 'topic',
                                    'name': 'Топик',
                                    'values': {
                                        'topic1': 'topic1',
                                        'topic2': 'topic2',
                                    },
                                },
                            },
                        },
                    },
                },
                'passenger-tags': {
                    'name': 'Теги пассажиров',
                    'roles': {
                        'slug': 'access',
                        'name': 'Доступ',
                        'values': {
                            'topic_access': {
                                'name': 'Доступ к топикам',
                                'roles': {
                                    'slug': 'topic',
                                    'name': 'Топик',
                                    'values': {
                                        'topic3': 'topic3',
                                        'topic4': 'topic4',
                                    },
                                },
                            },
                        },
                    },
                },
                'grocery-tags': {
                    'name': 'Теги лавки',
                    'roles': {
                        'slug': 'access',
                        'name': 'Доступ',
                        'values': {
                            'topic_access': {
                                'name': 'Доступ к топикам',
                                'roles': {
                                    'slug': 'topic',
                                    'name': 'Топик',
                                    'values': {'topic5': 'topic5'},
                                },
                            },
                        },
                    },
                },
                'eats-tags': {
                    'name': 'Теги еды',
                    'roles': {
                        'slug': 'access',
                        'name': 'Доступ',
                        'values': {
                            'topic_access': {
                                'name': 'Доступ к топикам',
                                'roles': {
                                    'slug': 'topic',
                                    'name': 'Топик',
                                    'values': {'topic5': 'topic5'},
                                },
                            },
                        },
                    },
                },
            },
        },
    }

    assert response.json() == expected


async def test_idm_add_role_good(taxi_tags_topics, pgsql):
    assert has_permission(pgsql, 'user2', 'tags', 'topic2') is False

    response = await taxi_tags_topics.post(
        f'idm/add-role',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={
            'login': 'user2',
            'role': (
                '{"service": "tags", "access": "topic_access",'
                ' "topic": "topic2"}'
            ),
        },
    )
    assert response.status_code == 200
    assert response.json()['code'] == 0

    assert has_permission(pgsql, 'user2', 'tags', 'topic2') is True


@pytest.mark.pgsql('tags_topics', files=['permissions_initial.sql'])
async def test_idm_add_role_existing_role(taxi_tags_topics, pgsql):
    assert has_permission(pgsql, 'user2', 'tags', 'topic1') is True

    response = await taxi_tags_topics.post(
        f'idm/add-role',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={
            'login': 'user2',
            'role': (
                '{"service": "tags", "access": "topic_access",'
                ' "topic": "topic1"}'
            ),
        },
    )
    assert response.status_code == 200
    assert response.json()['code'] == 0

    assert has_permission(pgsql, 'user2', 'tags', 'topic1') is True
    assert has_permission(pgsql, 'user1', 'tags', 'topic1') is True


async def test_idm_add_role_bad(taxi_tags_topics, pgsql):
    assert (
        has_permission(pgsql, 'frodo', constants.UNKNOWN_SERVICE, 'topic1')
        is False
    )

    response = await taxi_tags_topics.post(
        f'idm/add-role',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={
            'login': 'frodo',
            'role': (
                '{'
                f'"service": "{constants.UNKNOWN_SERVICE}",'
                '"access": "topic_access", "topic": "topic1"'
                '}'
            ),
        },
    )

    assert response.status_code == 200
    assert response.json()['code'] == 400

    assert (
        has_permission(pgsql, 'frodo', constants.UNKNOWN_SERVICE, 'topic1')
        is False
    )


@pytest.mark.pgsql('tags_topics', files=['permissions_initial.sql'])
async def test_idm_remove_role_good(taxi_tags_topics, pgsql):
    assert has_permission(pgsql, 'user1', 'tags', 'topic1') is True

    response = await taxi_tags_topics.post(
        f'idm/remove-role',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={
            'login': 'user1',
            'role': (
                '{"service": "tags", "access": "topic_access", '
                ' "topic": "topic1"}'
            ),
        },
    )
    assert response.status_code == 200
    assert response.json()['code'] == 0

    assert has_permission(pgsql, 'user1', 'tags', 'topic1') is False


async def test_idm_remove_role_bad(taxi_tags_topics, pgsql):
    assert has_permission(pgsql, 'frodo', 'tags', 'topic1') is False

    response = await taxi_tags_topics.post(
        f'idm/remove-role',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={
            'login': 'frodo',
            'role': (
                '{"service": "tags", "access": "topic_access",'
                ' "topic": "topic1"}'
            ),
        },
    )
    assert response.status_code == 200
    assert response.json()['code'] == 0

    assert has_permission(pgsql, 'frodo', 'tags', 'topic1') is False


async def test_idm_get_all_roles_empty(taxi_tags_topics):
    response = await taxi_tags_topics.get(f'idm/get-all-roles')
    assert response.status_code == 200
    expected = {'code': 0, 'users': []}

    assert response.json() == expected


@pytest.mark.pgsql('tags_topics', files=['permissions_initial.sql'])
async def test_idm_get_all_roles(taxi_tags_topics):
    response = await taxi_tags_topics.get(f'idm/get-all-roles')
    assert response.status_code == 200
    expected = {
        'code': 0,
        'users': [
            {
                'login': 'user1',
                'roles': [
                    {
                        'service': 'tags',
                        'access': 'topic_access',
                        'topic': 'topic1',
                    },
                    {
                        'service': 'tags',
                        'access': 'topic_access',
                        'topic': 'topic2',
                    },
                ],
            },
            {
                'login': 'user2',
                'roles': [
                    {
                        'service': 'tags',
                        'access': 'topic_access',
                        'topic': 'topic1',
                    },
                ],
            },
        ],
    }

    response_data = response.json()
    ordered_object.assert_eq(response_data, expected, ['users', 'users.roles'])
