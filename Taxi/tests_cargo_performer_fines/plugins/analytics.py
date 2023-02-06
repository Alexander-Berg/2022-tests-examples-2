import pytest


@pytest.fixture(name='default_cancel_reason')
def _default_cancel_reason():
    return 'cancel_reason'


@pytest.fixture(name='default_payload')
def _default_payload():
    return {
        'claim_status': 'pickuped',
        'items_weight': 15.0,
        'special_requirements': ['cargo_eds'],
        'tags': ['test_tag_1'],
        'time_in_status_sec': 56329990,
        'waybill_ref': 'waybill-ref',
        'zone_id': 'moscow',
        'tariff_class': 'cargo',
    }


@pytest.fixture(name='mock_analytics_job_settings')
async def _mock_job_settings(taxi_cargo_performer_fines, taxi_config):
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
            'force_execute': False,
            'check_settings': {
                'completed': True,
                'guilty': True,
                'free_cancellation_limit_exceeded': True,
            },
        },
    )
    await taxi_cargo_performer_fines.invalidate_caches()
