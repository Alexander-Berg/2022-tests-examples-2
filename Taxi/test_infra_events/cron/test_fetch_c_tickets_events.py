import datetime

import pytest

# pylint: disable=redefined-outer-name
from infra_events.generated.cron import run_cron


@pytest.mark.config(INFRA_EVENTS_VIEWS=['taxi', 'eda'])
@pytest.mark.parametrize('project', ['taxi', 'eda'])
async def test_fetch_c_tickets_events(mockserver, mongo, project):
    @mockserver.handler('/conductor/api/tasks_filter')
    def _task_filter_handler(request):
        if request.args['project'] != project:
            return mockserver.make_response(status=200, json=[])
        return mockserver.make_response(
            status=200,
            json=[
                {
                    'name': 'TESTTAXI-0-0',
                    'ticket': 1,
                    'done_at': '2021-01-01 14:36:27 +0300',
                    'branch': 'stable',
                    'project': project,
                    'packages': [
                        {'package': 'yandex-test', 'version': '1.1.1'},
                    ],
                    'author': 'test',
                    'workflow': 'taxi_test',
                    'deploy_group': 'taxi_test',
                },
            ],
        )

    await run_cron.main(
        ['infra_events.crontasks.fetch_c_tickets_events', '-t', '0'],
    )

    search = await mongo.lenta_events.find_one()
    del search['_id']
    assert search == {
        'timestamp': datetime.datetime(2021, 1, 1, 11, 36, 27),
        'header': 'Завершилась выкладка на taxi_test/taxi_test',
        'body': (
            'В таске ((https://c.yandex-team.ru/tickets/1 TESTTAXI-0-0))'
            ' установлены пакеты:\n\tyandex-test: 1.1.1\n'
        ),
        'tags': [
            'staff:test',
            'c_deploy_group:taxi_test',
            'c_workflow:taxi_test',
        ],
        'source': 'conductor',
        'views': [project],
    }
