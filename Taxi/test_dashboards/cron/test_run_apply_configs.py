from aiohttp import web
import pytest

from testsuite.mockserver import classes as mock_types


FETCH_APPLYING_CONFIGS_QUERY = """
SELECT start_apply_time, finish_apply_time, job_id
FROM dashboards.configs
WHERE status = 'applying'
ORDER BY job_id
"""


@pytest.fixture(name='serial_generator')
def _serial_generator():
    def _wrapper():
        id_ = 1
        while True:
            yield id_
            id_ += 1

    return _wrapper


@pytest.mark.parametrize(
    'request_error',
    [
        pytest.param(True, id='tp_request_error'),
        pytest.param(False, id='tp_request_success'),
    ],
)
@pytest.mark.pgsql(
    'dashboards', files=['init_data.sql', 'waiting_configs.sql'],
)
async def test_run_apply_configs(
        mock_task_processor,
        serial_generator,
        load_json,
        cron_runner,
        cron_context,
        request_error,
):
    job_id_gen = serial_generator()

    @mock_task_processor('/v1/jobs/start/')
    def _job_start_mock(request: mock_types.MockserverRequest):
        if request_error:
            return web.json_response(status=500)

        return {'job_id': next(job_id_gen)}

    await cron_runner.run_apply_configs()
    rows = await cron_context.pg.primary.fetch(FETCH_APPLYING_CONFIGS_QUERY)

    job_ids = [row['job_id'] for row in rows]

    if not request_error:
        assert job_ids == [1, 2]
        assert _job_start_mock.times_called == 2
        mock_calls = []
        while _job_start_mock.has_calls:
            mock_calls.append(_job_start_mock.next_call()['request'].json)
        assert mock_calls == load_json('exptected_tp_job_start_requests.json')
    else:
        assert job_ids == [None, None]

    assert all(row['start_apply_time'] is not None for row in rows)
    assert all(row['finish_apply_time'] is None for row in rows)


@pytest.mark.pgsql(
    'dashboards', files=['init_data.sql', 'waiting_and_applying_configs.sql'],
)
async def test_run_apply_configs_skip_already_applying(
        mock_task_processor, cron_runner, cron_context,
):
    @mock_task_processor('/v1/jobs/start/')
    def _job_start_mock(request):
        return {'job_id': 123}

    await cron_runner.run_apply_configs()
    rows = await cron_context.pg.primary.fetch(FETCH_APPLYING_CONFIGS_QUERY)

    job_ids = [row['job_id'] for row in rows]
    assert job_ids == [666]
    assert _job_start_mock.times_called == 0
