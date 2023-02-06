# flake8: noqa E501
import datetime

import pytest

# pylint: disable=redefined-outer-name
from infra_events.generated.cron import run_cron


@pytest.mark.config(INFRA_EVENTS_VIEWS=['taxi', 'eda'])
@pytest.mark.parametrize('project', ['taxi', 'eda'])
async def test_fetch_c_tickets_events(mockserver, mongo, project):
    @mockserver.handler('/conductor/api/custom/project-logs')
    def _custom_project_logs(request):
        if request.args['project'] != project:
            return mockserver.make_response(status=200, json={'logs': []})
        return mockserver.make_response(
            status=200,
            json={
                'logs': [
                    {
                        'id': 0,
                        'ticket_id': 0,
                        'task_id': 0,
                        'status': 'deploying',
                        'from': '2009-11-09T19:58:16+03:00',
                        'to': '2009-11-09T19:59:16+03:00',
                        'branch': 'stable',
                    },
                ],
            },
        )

    @mockserver.handler('/conductor/api/v2/tasks/0')
    def _task_by_id(request):
        return mockserver.make_response(
            status=200,
            json={
                'data': {
                    'id': '0',
                    'type': 'tasks',
                    'links': {
                        'self': 'https://c.yandex-team.ru/api/v2/tasks/0',
                    },
                    'attributes': {
                        'name': 'TT-0-0',
                        'status': 'obsolete',
                        'message': None,
                        'paused': False,
                        'number': 1,
                        'deploy_scope': 1,
                        'done_at': None,
                        'created_at': '2009-11-09T19:58:16+03:00',
                        'updated_at': '2017-10-10T11:32:22+03:00',
                    },
                    'relationships': {
                        'ticket': {
                            'links': {
                                'self': 'https://c.yandex-team.ru/api/v2/tasks/0/relationships/ticket',
                                'related': 'https://c.yandex-team.ru/api/v2/tasks/0/ticket',
                            },
                        },
                        'project': {
                            'links': {
                                'self': 'https://c.yandex-team.ru/api/v2/tasks/0/relationships/project',
                                'related': 'https://c.yandex-team.ru/api/v2/tasks/0/project',
                            },
                        },
                        'packages': {
                            'links': {
                                'self': 'https://c.yandex-team.ru/api/v2/tasks/0/relationships/packages',
                                'related': 'https://c.yandex-team.ru/api/v2/tasks/0/packages',
                            },
                        },
                    },
                },
            },
        )

    @mockserver.handler('/conductor/api/task/TT-0-0')
    def _task_by_name(request):
        if request.args['format'] != 'json':
            return mockserver.make_response(status=500, json={})
        return mockserver.make_response(
            status=200,
            json={
                'status': 'obsolete',
                'author': 'admin',
                'paused': False,
                'locker': None,
                'branch': 'fallback',
                'created_at': '2009-11-09T19:58:16+03:00',
                'comment': 'this is another test ticket',
                'autoinstall': False,
                'packages': {
                    'yandex-test1': {
                        'version': '3.25',
                        'upgrade_only': False,
                        'parallel_percent': None,
                        'repos': {
                            'test': {
                                'need_dmove': True,
                                'dmove_key': 'test',
                                'host': 'test.dist.yandex.ru',
                                'os_type': 'debian',
                                'secure': False,
                                'path': '',
                            },
                        },
                        'preservices': [],
                        'services': [],
                        'install_delay': -1,
                        'groups': [],
                        'hosts': [],
                    },
                    'yandex-test2': {
                        'version': '3.56-4',
                        'upgrade_only': False,
                        'parallel_percent': 100,
                        'repos': {
                            'test-common': {
                                'need_dmove': True,
                                'dmove_key': 'test-common',
                                'host': 'test-common.dist.yandex.ru',
                                'os_type': 'debian',
                                'secure': False,
                                'path': '',
                            },
                        },
                        'preservices': [],
                        'services': ['test2'],
                        'install_delay': -1,
                        'groups': [],
                        'hosts': [],
                    },
                },
                'remove_packages': {},
                'versioned': False,
                'deploy_by_dc': False,
                'deploy_by_root_dc': False,
                'deploy_scope': 1,
                'prehooks': [],
                'hooks': [],
            },
        )

    await run_cron.main(
        ['infra_events.crontasks.fetch_taxirel_c_tickets_events', '-t', '0'],
    )

    res = await mongo.lenta_events.find_one()
    del res['_id']
    assert res == {
        'timestamp': datetime.datetime(2009, 11, 9, 16, 58, 16),
        'header': 'Началась выкатка на %None',
        'body': (
            'В таске ((https://c.yandex-team.ru/tasks/TT-0-0 TT-0-0))'
            ' ставятся пакеты:\n\tyandex-test1=3.25\t, yandex-test2=3.56-4'
        ),
        'tags': [],
        'source': 'conductor',
        'views': [project],
    }
