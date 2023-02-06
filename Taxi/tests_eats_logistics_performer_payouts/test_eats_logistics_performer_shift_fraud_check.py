import pytest


# Default configs:

CFG_RATE_RETRY_DFT = {
    'interval_ms': 100,
    'interval_retry_ms': 100,
    'max_retry_count': 2,
}
CFG_RATE_SETTINGS_DFT = {
    'common': {
        'eats_shifts': {'common': CFG_RATE_RETRY_DFT},
        'eats_core_integration': {'common': CFG_RATE_RETRY_DFT},
        'driver_profiles': {'common': CFG_RATE_RETRY_DFT},
        'eats_logistics_performer_payouts': {'common': CFG_RATE_RETRY_DFT},
        'yt_hahn': {'rate': {'interval_ms': 100}},
    },
}

CFG_FRAUD_EVENT_TYPES_DFT = ['fake_gps_protector', 'root_protector']
CFG_YT_TABLE_DFT = '//home/testsuite/fraud_signals'
CFG_YT_LIMIT_DFT = 4000

# pylint: disable=W0102
def cfg_make_fraud_check_settings(event_types=CFG_FRAUD_EVENT_TYPES_DFT):
    cfg_fraud_check_settings = {
        'fraud_event_types': event_types,
        'fraud_event_lifetime_s': 259200,
        'fraud_event_interval_s': 1800,
        'fraud_signals_yt': {
            'table': CFG_YT_TABLE_DFT,
            'initial_cursor': '0',
            'limit': CFG_YT_LIMIT_DFT,
            'fetch_period_ms': 900000,
        },
    }

    return cfg_fraud_check_settings


CFG_FRAUD_CHECK_SETTINGS_DFT = cfg_make_fraud_check_settings()


# Stq kwargs:

STQ_SHIFT_1 = {
    'shift_id': '1',
    'driver_uuid': '00A3',
    'start_at': '2020-06-30T11:00:00+03:00',
}
STQ_SHIFT_2 = {
    'shift_id': '2',
    'driver_uuid': '00D5',
    'start_at': '2020-06-30T11:00:00+03:00',
}
STQ_SHIFT_3 = {
    'shift_id': '3',
    'driver_uuid': 'CC02',
    'start_at': '2020-06-30T13:00:00+03:00',
}

STQ_KWARGS = {'shifts': [STQ_SHIFT_1, STQ_SHIFT_2, STQ_SHIFT_3]}


# Subjects:

SUBJ_FRAUD_SHIFT_1 = {
    'id': {'id': '1', 'type': 'shift'},
    'factors': [{'name': 'fraud_on_start', 'type': 'int', 'value': 2}],
}
SUBJ_FRAUD_SHIFT_2 = {
    'id': {'id': '2', 'type': 'shift'},
    'factors': [{'name': 'fraud_on_start', 'type': 'int', 'value': 1}],
}

SUBJ_FRAUD = [SUBJ_FRAUD_SHIFT_1, SUBJ_FRAUD_SHIFT_2]


@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=[
        'eats_logistics_performer_payouts/insert_all_factors.sql',
        'eats_logistics_performer_payouts/insert_fraud_event_cache.sql',
    ],
)
@pytest.mark.now('2020-06-30T08:35:00+0000')
@pytest.mark.config(
    EATS_LOGISTICS_PERFORMER_PAYOUTS_FRAUD_CHECK_SETTINGS_V4=CFG_FRAUD_CHECK_SETTINGS_DFT,  # noqa: E501 pylint: disable=line-too-long
    EATS_LOGISTICS_PERFORMER_PAYOUTS_RATE_SETTINGS=CFG_RATE_SETTINGS_DFT,
)
async def test_shift_fraud_check(stq, stq_runner, testpoint):
    @testpoint('test_subject_request')
    def test_subject(data):
        assert data in SUBJ_FRAUD

    await stq_runner.eats_logistics_performer_shift_fraud_check.call(
        task_id='dummy_task', kwargs=STQ_KWARGS,
    )

    assert test_subject.times_called == 2
