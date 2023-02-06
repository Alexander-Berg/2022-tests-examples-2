import json

import pytest


@pytest.fixture
def call_cube_handle(web_app_client):
    async def _wrapper(cube_name, json_data):
        data_request = json_data['data_request']
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/', json=data_request,
        )
        assert response.status == 200, await response.text()
        content = await response.json()
        assert content == json_data['content_expected']
        return response

    return _wrapper


@pytest.fixture(name='tp_start_job_mock')
async def _tp_start_job_mock(mockserver):
    def _wrapper():
        @mockserver.json_handler('/task-processor/v1/jobs/start/')
        def _request(request):
            assert request.method == 'POST'
            return {'job_id': 100}

        return _request

    return _wrapper


@pytest.fixture(name='assert_tp_meta_jobs')
async def _assert_tp_meta_jobs():
    async def _wrapper(json_data, tp_mock):
        for expected_call in json_data.get('tp_jobs_expected', []):
            tp_request = tp_mock.next_call()['request']
            assert tp_request.json == expected_call
        assert not tp_mock.has_calls

    return _wrapper


@pytest.fixture
def assert_meta_jobs(get_job, get_job_variables):
    async def _wrapper(json_data):
        for job_expected in json_data['jobs_expected']:
            job = await get_job(job_expected['id'])
            assert len(job) == 1
            assert job[0]['job']['name'] == job_expected['name']
            variables = await get_job_variables(job_expected['id'])
            assert (
                json.loads(variables['variables']) == job_expected['variables']
            )

    return _wrapper
