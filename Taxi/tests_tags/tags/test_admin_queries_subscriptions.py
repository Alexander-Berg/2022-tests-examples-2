from typing import List
from typing import Optional

import pytest

from tests_tags.tags import tags_select
from tests_tags.tags import yql_tools


_TASK_TICKET = 'TASKTICKET-1234'


def _verify_subscriptions(
        db, expected_subscriptions: List[yql_tools.Subscription],
):
    rows = tags_select.select_table_named(
        'service.yql_subscriptions', 'provider_id,subscriber_login', db,
    )
    subscriptions = list(
        map(
            lambda row: (
                row['provider_id'],
                row['subscriber_login'],
                row['notifications'],
            ),
            rows,
        ),
    )
    expected = list(
        map(
            lambda row: (
                row.provider_id,
                row.subscriber_login,
                row.notifications_to_str(),
            ),
            expected_subscriptions,
        ),
    )
    assert subscriptions == expected


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    files=['pg_tags_queries.sql'],
    queries=[
        yql_tools.insert_subscriptions(
            [
                yql_tools.Subscription(
                    provider_id=0,
                    subscriber_login='login1',
                    notifications=yql_tools.SUBSCRIPTION_TYPES,
                ),
                yql_tools.Subscription(
                    provider_id=1,
                    subscriber_login='login1',
                    notifications=yql_tools.SUBSCRIPTION_TYPES,
                ),
                yql_tools.Subscription(
                    provider_id=0,
                    subscriber_login='login2',
                    notifications=yql_tools.SUBSCRIPTION_TYPES,
                ),
            ],
        ),
    ],
)
async def test_get_subscribers(taxi_tags):
    response = await taxi_tags.get(
        f'v1/admin/queries/subscriptions/list?query=first_name',
    )
    assert response.status_code == 200
    assert response.json() == {
        'subscriptions': [
            {
                'login': 'login1',
                'notifications': [{'event': 'failure', 'transport': 'email'}],
            },
            {
                'login': 'login2',
                'notifications': [{'event': 'failure', 'transport': 'email'}],
            },
        ],
    }

    response = await taxi_tags.get(
        'v1/admin/queries/subscriptions/list?query=name_extended',
    )
    assert response.status_code == 200
    assert response.json() == {
        'subscriptions': [
            {
                'login': 'login1',
                'notifications': [{'event': 'failure', 'transport': 'email'}],
            },
        ],
    }

    response = await taxi_tags.get(
        'v1/admin/queries/subscriptions/list?query=nayme_with_error',
    )
    assert response.status_code == 200
    assert response.json() == {'subscriptions': []}


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    files=['pg_tags_queries.sql'],
    queries=[
        yql_tools.insert_subscriptions(
            [
                yql_tools.Subscription(
                    provider_id=0,
                    subscriber_login='login0',
                    notifications=yql_tools.SUBSCRIPTION_TYPES,
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'login, notifications, expected_subscriptions',
    [
        # new subscriber
        (
            'login1',
            [{'event': 'failure', 'transport': 'email'}],
            [
                yql_tools.Subscription(
                    provider_id=0,
                    subscriber_login='login0',
                    notifications=yql_tools.SUBSCRIPTION_TYPES,
                ),
                yql_tools.Subscription(
                    provider_id=0,
                    subscriber_login='login1',
                    notifications=yql_tools.SUBSCRIPTION_TYPES,
                ),
            ],
        ),
        # new subscriber without notifications
        (
            'login1',
            [],
            [
                yql_tools.Subscription(
                    provider_id=0,
                    subscriber_login='login0',
                    notifications=yql_tools.SUBSCRIPTION_TYPES,
                ),
            ],
        ),
        # disable notifications
        ('login0', [], []),
    ],
)
async def test_subscribe(
        taxi_tags, pgsql, notifications, expected_subscriptions, login,
):
    data = {'query': 'first_name', 'notifications': notifications}
    response = await taxi_tags.post(
        'v1/admin/queries/subscriptions/subscribe',
        data,
        headers={'X-Yandex-Login': login},
    )
    assert response.status_code == 200
    _verify_subscriptions(pgsql['tags'], expected_subscriptions)


_SUBSCRIPTIONS = [
    yql_tools.Subscription(
        provider_id=0,
        subscriber_login='login0',
        notifications=yql_tools.SUBSCRIPTION_TYPES,
    ),
    yql_tools.Subscription(
        provider_id=1,
        subscriber_login='login1',
        notifications=yql_tools.SUBSCRIPTION_TYPES,
    ),
    yql_tools.Subscription(
        provider_id=2,
        subscriber_login='login2',
        notifications=yql_tools.SUBSCRIPTION_TYPES,
    ),
    yql_tools.Subscription(
        provider_id=0,
        subscriber_login='login1',
        notifications=yql_tools.SUBSCRIPTION_TYPES,
    ),
    yql_tools.Subscription(
        provider_id=0,
        subscriber_login='login2',
        notifications=yql_tools.SUBSCRIPTION_TYPES,
    ),
]


@pytest.mark.pgsql(
    'tags',
    files=['pg_tags_queries.sql'],
    queries=[yql_tools.insert_subscriptions(_SUBSCRIPTIONS)],
)
async def test_remove_subscribers(taxi_tags, pgsql):
    data = {'query': 'first_name', 'subscribers': ['login1', 'login2']}
    response = await taxi_tags.post(
        'v1/admin/queries/subscriptions/remove', data,
    )
    assert response.status_code == 200
    _verify_subscriptions(pgsql['tags'], _SUBSCRIPTIONS[:-2])


async def test_subscription_types(taxi_tags):
    response = await taxi_tags.get('v1/admin/queries/subscriptions/types')
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {'name': 'failure', 'title': 'Ошибка запроса'},
            {
                'name': 'query_expiration',
                'title': 'Окончание срока действия запроса',
            },
        ],
        'transports': [{'name': 'email', 'title': 'Письма на почту'}],
    }


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    files=['pg_tags_queries.sql'],
    queries=[
        yql_tools.insert_subscriptions(
            [
                yql_tools.Subscription(
                    provider_id=2,
                    subscriber_login='login0',
                    notifications=yql_tools.SUBSCRIPTION_TYPES,
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'action, query_name, expected_subscriptions',
    [
        pytest.param(
            'create',
            'new_query',
            '{"(failure,email)","(query_expiration,email)"}',
            id='query_creation',
        ),
        pytest.param(
            'create',
            'new_query',
            None,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_NOTIFICATION_SETTINGS={
                        'failure': {
                            'is_enabled': True,
                            'auto_subscribe_query_author': False,
                        },
                        'upcoming_query_expiration': {
                            'is_enabled': True,
                            'auto_subscribe_query_author': False,
                            'notification_schedule': [{'hours': 1}],
                        },
                        'query_expiration': {
                            'is_enabled': True,
                            'auto_subscribe_query_author': False,
                        },
                    },
                ),
            ],
            id='subscription_disabled',
        ),
        pytest.param(
            'edit',
            'nayme_with_error',
            # append expiration subscription
            '{"(failure,email)","(query_expiration,email)"}',
            marks=[
                pytest.mark.config(
                    TAGS_YQL_NOTIFICATION_SETTINGS={
                        'failure': {
                            'is_enabled': True,
                            'auto_subscribe_query_author': False,
                        },
                        'upcoming_query_expiration': {
                            'is_enabled': True,
                            'auto_subscribe_query_author': True,
                            'notification_schedule': [{'hours': 1}],
                        },
                        'query_expiration': {
                            'is_enabled': True,
                            'auto_subscribe_query_author': True,
                        },
                    },
                ),
            ],
            id='query_edit',
        ),
    ],
)
async def test_auto_subscribe(
        taxi_tags,
        action: str,
        query_name: str,
        expected_subscriptions: Optional[str],
        pgsql,
):
    response = await yql_tools.edit_request(
        taxi_tags,
        action,
        login='login0',
        query_name=query_name,
        query='[_INSERT_HERE_]',
        entity_type='park_car_id',
        tags=['dummy'],
        ticket=_TASK_TICKET,
        tags_limit=100,
    )
    assert response.status_code == 200

    rows = tags_select.select_named(
        """SELECT yql_subscriptions.* """
        """FROM service.yql_subscriptions JOIN service.queries """
        """ON yql_subscriptions.provider_id = queries.provider_id """
        f"""WHERE queries.name = '{query_name}'""",
        pgsql['tags'],
    )

    if expected_subscriptions:
        assert len(rows) == 1
        assert rows[0]['notifications'] == expected_subscriptions
    else:
        assert not rows
