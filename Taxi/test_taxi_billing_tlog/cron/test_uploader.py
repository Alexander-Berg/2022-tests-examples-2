import pytest

from taxi_billing_tlog import pgaas
from taxi_billing_tlog.crontasks import uploader


@pytest.mark.nofilldb
@pytest.mark.parametrize(
    'expected_strategy',
    [
        pytest.param(
            pgaas.BarrierLoadStrategy('table'),
            marks=pytest.mark.config(BILLING_TLOG_PG_ROW_LOAD_STRATEGY={}),
        ),
        pytest.param(
            pgaas.DelayLoadStrategy(10, 'table'),
            marks=pytest.mark.config(
                BILLING_TLOG_PG_ROW_LOAD_STRATEGY={
                    'consumer_2': {'name': 'barrier', 'parameters': {}},
                    '__default__': {
                        'name': 'delay',
                        'parameters': {'id_delay': 10},
                    },
                },
            ),
        ),
        pytest.param(
            pgaas.DelayLoadStrategy(10, 'table'),
            marks=pytest.mark.config(
                BILLING_TLOG_PG_ROW_LOAD_STRATEGY={
                    '__default__': {'name': 'barrier', 'parameters': {}},
                    'consumer_1': {
                        'name': 'delay',
                        'parameters': {'id_delay': 10},
                    },
                },
            ),
        ),
    ],
)
def test_build_row_load_strategy(cron_context, expected_strategy):
    strategy = uploader.build_row_load_strategy(
        cron_context.config, 'consumer.1', 'table',
    )
    assert strategy == expected_strategy
