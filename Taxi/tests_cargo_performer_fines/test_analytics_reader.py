import pytest


@pytest.mark.pgsql('cargo_performer_fines', files=['cancellation.sql'])
@pytest.mark.yt(static_table_data=['yt_analytics.yaml'])
async def test_analytics_bulk_info(
        taxi_cargo_performer_fines,
        taxi_config,
        yt_apply,
        mock_analytics_job_settings,
        stq,
        testpoint,
        yt_rows_count=3,
):
    taxi_config.set(
        CARGO_PERFORMER_FINES_ANALYTICS_READER_SETTINGS={
            'enabled': True,
            'yt_table_path': (
                '//home/testsuite/cargo_performer_fines_analytics'
            ),
            'job_awake_hour': 10,
            'job_iteration_pause_ms': 0,
            'execute_fine_sleep_ms': 0,
            'rate_limit': {'limit': 1000, 'interval': 1, 'burst': 0},
            'force_execute': True,
            'check_settings': {
                'completed': True,
                'guilty': True,
                'free_cancellation_limit_exceeded': True,
                'exists_in_db': True,
            },
        },
    )
    await taxi_cargo_performer_fines.invalidate_caches()

    @testpoint('cargo-performer-fines-analytics-reader::result')
    def _testpoint_job_result_callback(data):
        assert data['stats']['yt']['read-rows-count'] == yt_rows_count
        assert data['stats']['fines']['set-execute-fine-stq-failed'] == 0

    await taxi_cargo_performer_fines.run_task(
        'cargo-performer-fines-analytics-reader',
    )
    assert stq.cargo_performer_fines_execute_fine.times_called == 2


@pytest.mark.pgsql('cargo_performer_fines', files=['cancellation.sql'])
@pytest.mark.yt(static_table_data=['yt_analytics.yaml'])
async def test_analytics_job_three_iteration(
        taxi_cargo_performer_fines, taxi_config, yt_apply, stq, testpoint,
):
    taxi_config.set(
        CARGO_PERFORMER_FINES_ANALYTICS_READER_SETTINGS={
            'enabled': True,
            'yt_table_path': (
                '//home/testsuite/cargo_performer_fines_analytics'
            ),
            'job_awake_hour': 10,
            'job_iteration_pause_ms': 0,
            'execute_fine_sleep_ms': 0,
            'rate_limit': {'limit': 1, 'interval': 1, 'burst': 0},
            'force_execute': True,
            'check_settings': {
                'completed': True,
                'guilty': True,
                'free_cancellation_limit_exceeded': True,
            },
        },
    )
    await taxi_cargo_performer_fines.invalidate_caches()

    @testpoint('cargo-performer-fines-analytics-reader::result')
    def _testpoint_job_result_callback(data):
        assert data['stats']['yt']['read-rows-count'] == 1
        assert data['stats']['fines']['set-execute-fine-stq-failed'] == 0

    await taxi_cargo_performer_fines.run_task(
        'cargo-performer-fines-analytics-reader',
    )
    assert stq.cargo_performer_fines_execute_fine.times_called == 1
    await taxi_cargo_performer_fines.run_task(
        'cargo-performer-fines-analytics-reader',
    )
    assert stq.cargo_performer_fines_execute_fine.times_called == 2
    await taxi_cargo_performer_fines.run_task(
        'cargo-performer-fines-analytics-reader',
    )
    assert stq.cargo_performer_fines_execute_fine.times_called == 3


@pytest.mark.pgsql('cargo_performer_fines', files=['cancellation.sql'])
@pytest.mark.yt(static_table_data=['yt_analytics.yaml'])
async def test_analytics_stq_input_data(
        taxi_cargo_performer_fines,
        yt_apply,
        stq,
        mock_analytics_job_settings,
        default_cargo_order_id,
        default_taxi_order_id,
        default_dbid_uuid,
        default_cancel_reason,
        default_payload,
        yt_rows_count=3,
):
    park_id = default_dbid_uuid['dbid']
    driver_id = default_dbid_uuid['uuid']

    await taxi_cargo_performer_fines.run_task(
        'cargo-performer-fines-analytics-reader',
    )

    assert stq.cargo_performer_fines_execute_fine.times_called == yt_rows_count
    stq_call = stq.cargo_performer_fines_execute_fine.next_call()
    assert (
        stq_call['id'] == f'cargo_performer_fines_execute_fine_'
        f'{default_taxi_order_id}_{park_id}_{driver_id}_1'
    )

    kwargs = stq_call['kwargs']
    assert kwargs['taxi_order_id'] == default_taxi_order_id
    assert kwargs['cargo_order_id'] == default_cargo_order_id
    assert kwargs['park_id'] == park_id
    assert kwargs['driver_id'] == driver_id
    assert kwargs['cargo_cancel_reason'] == default_cancel_reason
    assert kwargs['payload'] == default_payload
