import datetime as dt

import pytest

from billing_functions import config


@pytest.mark.config(PROCESS_SHIFT_ENDED_MIN_MSK_TIME='04:00')
def test_process_shift_ended_min_msk_time(stq3_context):
    actual = config.process_shift_ended_min_msk_time(stq3_context.config)
    assert actual == dt.time(4, 0)


@pytest.mark.config(
    BILLING_SUBVENTIONS_LOGISTICS_SHIFT_DELAY=100,
    BILLING_SUBVENTIONS_TAXI_SHIFT_DELAY=200,
)
def test_shift_processing_delay(stq3_context):
    cargo = config.shift_processing_delay(True, stq3_context.config)
    assert cargo == dt.timedelta(seconds=100)

    taxi = config.shift_processing_delay(False, stq3_context.config)
    assert taxi == dt.timedelta(seconds=200)
