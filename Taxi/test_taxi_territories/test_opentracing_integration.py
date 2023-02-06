import logging

import pytest

HEADERS = {'YaTaxi-Api-Key': 'secret'}


@pytest.mark.config(
    TRACING_SAMPLING_PROBABILITY={'taxi_territories_web': {'es': 1}},
)
async def test_intergration(
        taxi_territories_client, tracing_reporting_enabled, caplog,
):
    caplog.set_level(logging.INFO, logger='taxi.opentracing.reporter')

    await taxi_territories_client.post('/ping', headers=HEADERS, json={})
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
