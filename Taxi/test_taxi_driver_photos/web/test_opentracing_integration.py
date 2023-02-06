import logging

import pytest

from taxi import config


@pytest.mark.skip('flaps, fix in TAXIBACKEND-20335')
@pytest.mark.parametrize('reporting_enabled', (True, False))
async def test_intergration(
        reporting_enabled, web_app_client, caplog, monkeypatch,
):
    caplog.set_level(logging.INFO, logger='taxi.opentracing.reporter')
    monkeypatch.setattr(
        config.Config,
        'OPENTRACING_REPORT_SPAN_ENABLED',
        {'__default__': reporting_enabled},
    )
    await web_app_client.get('/ping')
    records = [
        x
        for x in caplog.records
        if getattr(x, 'extdict', {}).get('_type') == 'span'
    ]
    if reporting_enabled:
        assert len(records) == 1
        record = records[0]
        assert record.levelname == 'INFO'
        assert record.message == 'Span finished'
        assert 'parent_id' not in record.extdict
    else:
        assert not records
