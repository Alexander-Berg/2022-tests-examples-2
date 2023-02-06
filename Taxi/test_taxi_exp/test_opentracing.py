import logging

import pytest

HEADERS = {'YaTaxi-Api-Key': 'secret'}


@pytest.mark.skip('flaps, fix in TAXIBACKEND-20335')
async def test_integration(taxi_exp_client, tracing_reporting_enabled, caplog):
    caplog.set_level(logging.INFO, logger='taxi.opentracing.reporter')

    await taxi_exp_client.get('/v1/experiments/list', headers=HEADERS)

    records = [
        x
        for x in caplog.records
        if getattr(x, 'extdict', {}).get('_type') == 'span'
    ]
    if tracing_reporting_enabled:
        assert len(records) == 1
        record = records[0]
        assert record.levelname == 'INFO'
        assert record.message == 'Span finished'
        assert 'parent_id' not in record.extdict
    else:
        assert not records
