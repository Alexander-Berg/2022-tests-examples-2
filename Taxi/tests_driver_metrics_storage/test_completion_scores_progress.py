import pytest


@pytest.fixture(name='driver_metrics_mock')
def _driver_metrics_mock(mockserver):
    class Context:
        def __init__(self):
            self._count = 0

        def set_blocking_count_value(self, value: int):
            self._count = value

        @property
        def blocking_count_value(self):
            return self._count

    ctx = Context()

    @mockserver.json_handler(
        '/driver-metrics/v1/contractor/blocking/complete_scores/count',
    )
    def _handle(data):
        return {'count': ctx.blocking_count_value}

    return ctx


def patch_handle_expectation(expected_json, handle_blocking_seconds):
    expected_json['levels'][0]['punishments']['blocking'][
        'duration_seconds'
    ] = handle_blocking_seconds
    return expected_json


@pytest.mark.parametrize(
    'handle_uri',
    ['/v1/completion_scores/progress', '/admin/v1/completion_scores/progress'],
)
@pytest.mark.now('2021-09-17T12:00:00+0000')
@pytest.mark.parametrize(
    (
        'unique_driver_id, handle_result_json, '
        'handle_blocking_seconds, progressive_blocking_count'
    ),
    (
        pytest.param(
            '100000000000000000000000',
            'handle_matched_exp_result.json',
            None,
            0,
            id='exp3 matched',
            marks=(pytest.mark.experiments3(filename='exp3_config.json'),),
        ),
        pytest.param(
            '100000000000000000000000',
            'handle_matched_exp_result.json',
            300,
            0,
            id='exp3 matched progressive 1st',
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_config_progressive.json',
                ),
            ),
        ),
        pytest.param(
            '100000000000000000000000',
            'handle_matched_exp_result.json',
            600,
            1,
            id='exp3 matched progressive 2nd',
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_config_progressive.json',
                ),
            ),
        ),
        pytest.param(
            '100000000000000000000000',
            'handle_matched_exp_result.json',
            1800,
            5,  # blocking count is greater than actual list size, pick last
            id='exp3 matched progressive last',
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_config_progressive.json',
                ),
            ),
        ),
        pytest.param(
            '200000000000000000000000',
            'handle_default_exp_result.json',
            None,
            0,
            id='exp3 default',
            marks=(pytest.mark.experiments3(filename='exp3_config.json'),),
        ),
        pytest.param(
            '300000000000000000000000',
            'handle_less_minimal_exp_result.json',
            None,
            0,
            id='exp3 less minimal',
            marks=(pytest.mark.experiments3(filename='exp3_config.json'),),
        ),
    ),
)
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
async def test_completion_scores_progress(
        taxi_driver_metrics_storage,
        handle_uri,
        experiments3,
        load_json,
        unique_driver_id,
        handle_result_json,
        handle_blocking_seconds,
        progressive_blocking_count,
        driver_metrics_mock,
):
    driver_metrics_mock.set_blocking_count_value(progressive_blocking_count)
    await taxi_driver_metrics_storage.invalidate_caches()
    await taxi_driver_metrics_storage.run_task('dist-version-refresher')

    exp3_recorder = experiments3.record_match_tries('completion_scores_levels')
    response = await taxi_driver_metrics_storage.post(
        handle_uri,
        json={
            'unique_driver_id': unique_driver_id,
            'tariff_zone': 'custom-tariff_zone-1',
            'tags': ['custom-tag-1', 'someone-else-tag'],
        },
    )

    await exp3_recorder.get_match_tries(ensure_ntries=1)

    assert response.status_code == 200
    if handle_blocking_seconds is None:
        assert response.json() == load_json(handle_result_json)
    else:
        assert response.json() == patch_handle_expectation(
            load_json(handle_result_json), handle_blocking_seconds,
        )


@pytest.mark.parametrize(
    'handle_uri',
    ['/v1/completion_scores/progress', '/admin/v1/completion_scores/progress'],
)
@pytest.mark.now('2021-09-17T12:00:00+0000')
@pytest.mark.parametrize(
    'unique_driver_id, http_retcode',
    (
        pytest.param(
            '300000000000000000000000',
            404,
            id='exp3 bad experiment3 config',
            marks=(pytest.mark.experiments3(filename='exp3_bad_config.json'),),
        ),
        pytest.param(
            '300000000000000000000000',
            404,
            id='exp3 not found',
            marks=(pytest.mark.experiments3(filename='exp3_out_of_exp.json'),),
        ),
    ),
)
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
async def test_completion_scores_progress_bad_cases(
        taxi_driver_metrics_storage,
        handle_uri,
        experiments3,
        load_json,
        unique_driver_id,
        http_retcode,
        driver_metrics_mock,
):
    await taxi_driver_metrics_storage.invalidate_caches()
    await taxi_driver_metrics_storage.run_task('dist-version-refresher')

    exp3_recorder = experiments3.record_match_tries('completion_scores_levels')
    response = await taxi_driver_metrics_storage.post(
        handle_uri,
        json={
            'unique_driver_id': unique_driver_id,
            'tariff_zone': 'custom-tariff_zone-1',
            'tags': ['custom-tag-1', 'someone-else-tag'],
        },
    )

    await exp3_recorder.get_match_tries(ensure_ntries=1)

    assert response.status_code == http_retcode
