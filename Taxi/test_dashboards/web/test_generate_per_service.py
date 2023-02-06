import pytest


class MockTpContext:
    def __init__(self):
        self._existed_jobs = {
            'key1': self._fill_data(1, 'success', 'github', {}, 'key1'),
            'key3': self._fill_data(2, 'in_progress', 'github', {}, 'key3'),
            'key4': self._fill_data(3, 'success', 'github', {}, 'key4'),
        }
        self._last_id = 3

    def jobs_count(self):
        return len(self._existed_jobs)

    @staticmethod
    def _fill_data(job_id, status, job_name, job_vars, change_doc_id):
        return {
            'id': job_id,
            'status': status,
            'recipe_id': 1,
            'name': job_name,
            'created_at': 1,
            'job_vars': job_vars,
            'change_doc_id': change_doc_id,
        }

    def get_jobs(self):
        return list(self._existed_jobs.values())

    def exists(self, change_doc_id):
        return change_doc_id in self._existed_jobs

    def add(self, body):
        self._last_id += 1
        change_doc_id = body['change_doc_id']
        self._existed_jobs[change_doc_id] = self._fill_data(
            self._last_id,
            'in_progress',
            body['recipe_name'],
            body['job_vars'],
            change_doc_id,
        )

    def get(self, change_doc_id):
        return self._existed_jobs[change_doc_id]


@pytest.fixture(name='mock_tp_context')
def _mock_tp_context():
    return MockTpContext()


@pytest.fixture(name='mock_tp')
def _mock_tp(mockserver, mock_tp_context):
    class Mocks:

        jobs = [1, 2, 3]

        @staticmethod
        @mockserver.json_handler(
            '/task-processor/v1/jobs/retrieve_by_change_doc_id/',
        )
        async def _retrieve_by_change_doc_id(request):
            if mock_tp_context.exists(request.json['change_doc_id']):
                job = mock_tp_context.get(request.json['change_doc_id'])
                return {'jobs': [job]}
            return mockserver.make_response(json={}, status=404)

        @staticmethod
        @mockserver.json_handler('/task-processor/v1/jobs/start/')
        async def _start(request):
            mock_tp_context.add(request.json)
            return {
                'job_id': mock_tp_context.get(request.json['change_doc_id'])[
                    'id'
                ],
            }

        @staticmethod
        @mockserver.json_handler('/task-processor/v1/jobs/')
        async def _list_jobs(request):
            return {
                'jobs': [
                    {'tasks': [], 'job_info': i}
                    for i in mock_tp_context.get_jobs()
                ],
            }

    return Mocks()


@pytest.mark.pgsql('dashboards', files=['init_data.sql'])
async def test_generate_per_service(
        web_app_client, web_context, taxi_dashboards_web, mock_tp,
):
    resp = await web_app_client.post(
        '/v1/config/generate', params={'branch_id': 123},
    )

    assert resp.status == 200, await resp.text()
    assert resp.status == 200, await resp.json()
    content = await resp.json()
    assert content == {'job_id': 4}

    resp = await web_app_client.get(
        '/v1/config/is_generable', params={'branch_id': 123},
    )
    content = await resp.json()
    assert resp.status == 409, content
    assert content == {
        'code': 'ACTIVE_JOB_FOUND',
        'message': (
            'https://tariff-editor.taxi.yandex-team.ru/'
            'task-processor/providers/70/jobs/edit/4'
        ),
    }

    resp = await web_app_client.post(
        '/v1/config/generate', params={'branch_id': 123},
    )
    content = await resp.json()
    assert resp.status == 409, content
    assert content == {
        'code': 'ACTIVE_JOB_FOUND',
        'message': 'Dashboard is already being generated',
    }
