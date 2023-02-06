import json
import logging

import pytest


@pytest.mark.config(
    TRACING_SAMPLING_PROBABILITY={'passenger_profile_web': {'es': 1}},
)
async def test_integration(
        web_app_client, client_experiments3, tracing_reporting_enabled, caplog,
):
    caplog.set_level(logging.INFO, logger='taxi.opentracing.reporter')

    await web_app_client.get('/ping')

    records = []
    for record in caplog.records:
        record_type = getattr(record, 'extdict', {}).get('_type')
        if record_type != 'span':
            continue
        body = json.loads(record.extdict.get('body', '{}'))
        if body.get('operation_name') == '/experiments3/ping':
            continue

        records.append(record)

    if tracing_reporting_enabled:
        assert len(records) == 1
        record = records[0]
        assert record.levelname == 'INFO'
        assert record.message == 'Span finished'
        assert 'parent_id' not in record.extdict

    else:
        assert not records
