import logging

import pytest


@pytest.mark.config(
    TRACING_SAMPLING_PROBABILITY={'hiring_plugins_tests_web': {'es': 1}},
)
async def test_intergration(
        hiring_forms_mockserver,
        wait_until_ready,
        web_app_client,
        tracing_reporting_enabled,
        caplog,
):
    await wait_until_ready()
    caplog.set_level(logging.INFO, logger='taxi.opentracing.reporter')

    # We call /ping to be sure we are ready
    # So shouldn't count previous calls
    prev_records = _get_records(caplog)

    await web_app_client.get('/ping')
    records = _get_records(caplog)
    if tracing_reporting_enabled:
        assert len(records) == len(prev_records) + 1
        record = records[-1]
        assert record.levelname == 'INFO'
        assert record.message == 'Span finished'
        assert 'parent_id' not in record.extdict
    else:
        assert not records


def _get_records(caplog):
    records = [
        x
        for x in caplog.records
        if getattr(x, 'extdict', {}).get('_type') == 'span'
    ]
    return records
