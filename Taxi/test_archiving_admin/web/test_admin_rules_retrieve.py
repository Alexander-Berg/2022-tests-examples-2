import pytest

from archiving_admin import links


async def test_retrieve_empty(web_app_client):
    response = await web_app_client.post('/admin/v1/rules/retrieve')
    assert response.status == 200
    content = await response.json()
    assert content == {'rules': []}


@pytest.mark.pgsql('archiving_admin', files=['pg_test_archiving_rules.sql'])
async def test_retrieve(web_app_client):
    response = await web_app_client.post('/admin/v1/rules/retrieve')
    assert response.status == 200
    content = await response.json()
    assert content == {
        'rules': [
            {
                'group_name': 'abc',
                'rule_name': 'test_abc',
                'source_type': 'bar',
                'period': 300,
                'sleep_delay': 2,
                'enabled': False,
                'last_run': [
                    {
                        'start_time': '2019-01-01T06:00:00+03:00',
                        'status': 'finished',
                        'link': (
                            links.make_cron_tasks_link(
                                'bar', 'test_abc', link='test_link1',
                            )
                        ),
                        'removed': 2031,
                        'sync_time': '2019-01-01T09:00:00+03:00',
                    },
                    {
                        'start_time': '2019-01-01T06:00:00+03:00',
                        'status': 'finished',
                        'link': (
                            links.make_cron_tasks_link(
                                'bar', 'test_abc', link='test_link2',
                            )
                        ),
                        'removed': 2031,
                        'sync_time': '2019-01-01T10:00:00+03:00',
                    },
                    {
                        'start_time': '2019-01-01T06:00:00+03:00',
                        'status': 'exception',
                        'link': (
                            links.make_cron_tasks_link(
                                'bar', 'test_abc', link='test_link3',
                            )
                        ),
                        'removed': 20312,
                        'sync_time': '2019-01-01T11:00:00+03:00',
                    },
                    {
                        'start_time': '2019-01-01T06:00:00+03:00',
                        'status': 'finished',
                        'link': (
                            links.make_cron_tasks_link(
                                'bar', 'test_abc', link='test_link4',
                            )
                        ),
                        'removed': 244,
                        'sync_time': '2019-01-01T12:00:00+03:00',
                    },
                    {
                        'start_time': '2019-01-01T06:00:00+03:00',
                        'status': 'finished',
                        'link': (
                            links.make_cron_tasks_link(
                                'bar', 'test_abc', link='test_link5',
                            )
                        ),
                        'removed': 2134,
                        'sync_time': '2019-01-01T13:00:00+03:00',
                    },
                ],
                'ttl_info': {'field': 'updated', 'duration_default': 123},
                'task_info': [
                    {
                        'link': links.make_cron_tasks_link('bar', 'test_abc'),
                        'link_name': 'Cron tasks',
                        'alert_status': 'ok',
                    },
                    {
                        'link': links.make_dashboards_link(['test_abc']),
                        'link_name': 'Dashboards',
                        'alert_status': 'ok',
                    },
                    {
                        'link': links.make_rule_repository_link(
                            'abc', 'test_abc',
                        ),
                        'link_name': 'Rule in repository',
                        'alert_status': 'ok',
                    },
                ],
            },
            {
                'group_name': 'foo',
                'rule_name': 'test_foo_1',
                'source_type': 'bar',
                'period': 300,
                'sleep_delay': 2,
                'enabled': False,
                'last_run': [],
                'ttl_info': {'field': 'updated', 'duration_default': 100},
                'task_info': [
                    {
                        'link': links.make_cron_tasks_link(
                            'bar', 'test_foo_1',
                        ),
                        'link_name': 'Cron tasks',
                        'alert_status': 'ok',
                    },
                    {
                        'link': links.make_dashboards_link(
                            ['test_foo_1', 'test_foo_2', 'test_foo_3'],
                        ),
                        'link_name': 'Dashboards',
                        'alert_status': 'ok',
                    },
                    {
                        'link': links.make_rule_repository_link(
                            'foo', 'test_foo_1',
                        ),
                        'link_name': 'Rule in repository',
                        'alert_status': 'ok',
                    },
                ],
            },
            {
                'group_name': 'foo',
                'rule_name': 'test_foo_2',
                'source_type': 'bar',
                'period': 300,
                'sleep_delay': 2,
                'enabled': False,
                'last_run': [
                    {
                        'start_time': '2019-01-01T06:00:00+03:00',
                        'status': 'in_progress',
                        'link': links.make_cron_tasks_link(
                            'bar', 'test_foo_2', link='test_link',
                        ),
                        'removed': 24,
                        'sync_time': '2019-01-01T09:00:00+03:00',
                    },
                ],
                'ttl_info': {'field': 'updated', 'duration_default': 100},
                'task_info': [
                    {
                        'link': links.make_cron_tasks_link(
                            'bar', 'test_foo_2',
                        ),
                        'link_name': 'Cron tasks',
                        'alert_status': 'ok',
                    },
                    {
                        'link': links.make_dashboards_link(
                            ['test_foo_1', 'test_foo_2', 'test_foo_3'],
                        ),
                        'link_name': 'Dashboards',
                        'alert_status': 'ok',
                    },
                    {
                        'link': links.make_rule_repository_link(
                            'foo', 'test_foo_2',
                        ),
                        'link_name': 'Rule in repository',
                        'alert_status': 'ok',
                    },
                ],
            },
            {
                'group_name': 'foo',
                'rule_name': 'test_foo_3',
                'source_type': 'bar',
                'period': 300,
                'sleep_delay': 2,
                'enabled': False,
                'last_run': [],
                'ttl_info': {'field': 'updated', 'duration_default': 100},
                'task_info': [
                    {
                        'link': links.make_cron_tasks_link(
                            'bar', 'test_foo_3',
                        ),
                        'link_name': 'Cron tasks',
                        'alert_status': 'ok',
                    },
                    {
                        'link': links.make_dashboards_link(
                            ['test_foo_1', 'test_foo_2', 'test_foo_3'],
                        ),
                        'link_name': 'Dashboards',
                        'alert_status': 'ok',
                    },
                    {
                        'link': links.make_rule_repository_link(
                            'foo', 'test_foo_3',
                        ),
                        'link_name': 'Rule in repository',
                        'alert_status': 'ok',
                    },
                ],
            },
        ],
    }
