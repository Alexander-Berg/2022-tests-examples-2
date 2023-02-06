# pylint: disable=import-only-modules
import copy
import json

import pytest

from .utils import format_execution_timestamp
from .utils import get_task_name

OAUTH_HEADER = 'OAuth secret'


@pytest.mark.now('2020-05-18T12:00:00')
@pytest.mark.pgsql('reposition-relocator', files=['reactions.sql'])
async def test_monitor(taxi_reposition_relocator, mockserver, now):
    @mockserver.json_handler('/nirvana/api/public/v1/findWorkflows')
    def _mock_find_workflow(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == OAUTH_HEADER

        data = json.loads(request.get_data())
        assert 'id' in data
        assert 'params' in data
        assert (
            data['params']['pattern'] == '121'
            or data['params']['pattern'] == '123'
        )
        pattern = copy.deepcopy(data['params']['pattern'])

        del data['id']
        del data['params']['pattern']

        assert data == {
            'jsonrpc': '2.0',
            'method': 'findWorkflows',
            'params': {
                'additionalFilters': {
                    'author': ['robot-reposition-tst'],
                    'completed': {'from': '2020-05-18T11:53:00+00:00'},
                    'result': ['success'],
                    'status': ['completed'],
                },
            },
        }

        return mockserver.make_response(
            json.dumps(
                {
                    'jsonrpc': '2.0',
                    'id': 'findWorkflows_1585413223448',
                    'result': {
                        'guid': '7fda40c3-acda-4695-94c1-f9789fff6457',
                        'instanceId': pattern,
                        'projectCode': 'taxi_reposition_testing',
                        'owner': 'robot-reposition-tst',
                        'instanceCreator': 'robot-reposition-tst',
                        'name': 'Dummy workflow',
                        'description': '',
                        'created': '2020-03-28T18:57:57+0300',
                        'updated': '2020-03-28T18:58:30+0300',
                        'started': '2020-03-28T19:18:22+0300',
                        'completed': format_execution_timestamp(now),
                        'lifecycleStatus': 'approved',
                        'quotaProjectId': 'default',
                        'rejected': False,
                        'archived': False,
                        'tags': [],
                    },
                },
            ),
            status=200,
        )

    response = await taxi_reposition_relocator.post(
        'service/cron', json={'task_name': get_task_name('graphs_monitor')},
    )
    assert response.status_code == 200
    assert _mock_find_workflow.times_called == 2
