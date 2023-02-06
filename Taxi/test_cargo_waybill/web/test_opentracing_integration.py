import logging

import pytest


@pytest.mark.config(
    TRACING_SAMPLING_PROBABILITY={'cargo_waybill_web': {'es': 1}},
)
async def test_integration(web_app_client, tracing_reporting_enabled, caplog):
    caplog.set_level(logging.INFO, logger='taxi.opentracing.reporter')

    await web_app_client.get('/ping')
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
