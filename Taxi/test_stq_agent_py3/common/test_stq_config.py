import pytest

from taxi import settings

from stq_agent_py3.common import stq_config


@pytest.mark.now('2019-01-01T21:00:00Z')
def test_get_balancer_hosts_settings():
    assert (
        stq_config.get_balancer_hosts_settings(
            {'instances': 10, 'max_tasks': 90},
            {
                'node1': [0, 1],
                'node2': [1, 2],
                'node3': [0, 2],
                'node4': [0, 1, 2],
            },
        )
        == [
            {
                'name': 'node1',
                'shards': [
                    {'index': 0, 'max_tasks': 45},
                    {'index': 1, 'max_tasks': 45},
                ],
                'worker_configs': {'instances': 10},
            },
            {
                'name': 'node2',
                'shards': [
                    {'index': 1, 'max_tasks': 45},
                    {'index': 2, 'max_tasks': 45},
                ],
                'worker_configs': {'instances': 10},
            },
            {
                'name': 'node3',
                'shards': [
                    {'index': 0, 'max_tasks': 45},
                    {'index': 2, 'max_tasks': 45},
                ],
                'worker_configs': {'instances': 10},
            },
            {
                'name': 'node4',
                'shards': [
                    {'index': 0, 'max_tasks': 30},
                    {'index': 1, 'max_tasks': 30},
                    {'index': 2, 'max_tasks': 30},
                ],
                'worker_configs': {'instances': 10},
            },
        ]
    )


@pytest.mark.parametrize(
    'env,project,result',
    [
        (settings.TESTING, 'taxi-support', 'taxi'),
        (settings.TESTING, 'test-project', None),
        (settings.PRODUCTION, 'taxi-support', 'taxi'),
        (settings.PRODUCTION, 'test-project', None),
    ],
)
def test_get_namespace_for_project(
        env, project, result, web_context, monkeypatch,
):
    monkeypatch.setattr(settings, 'ENVIRONMENT', env)
    try:
        namespace = stq_config.get_namespace_for_project(web_context, project)
    except stq_config.ProjectNotFound:
        assert project == 'test-project'
        assert env == settings.PRODUCTION
        return
    assert namespace == result
