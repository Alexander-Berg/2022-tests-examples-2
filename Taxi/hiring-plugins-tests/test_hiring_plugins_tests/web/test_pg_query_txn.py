import json
import logging
import urllib.parse

import pytest


@pytest.mark.config(
    TRACING_SAMPLING_PROBABILITY={'hiring_plugins_tests_web': {'es': 1}},
)
async def test_opentracing_log(
        hiring_forms_mockserver,
        # pylint: disable=redefined-outer-name
        process_query,
        wait_until_ready,
        caplog,
        tracing_reporting_enabled,
        monkeypatch,
):

    caplog.set_level(logging.INFO, logger='taxi.opentracing.reporter')
    await wait_until_ready()

    prev_records = _get_records(caplog)
    row = await process_query('a', 'b')
    assert row == {'key': 'a', 'value': 'b'}

    records = _get_records(caplog, prev_records)

    if tracing_reporting_enabled:
        ids = set(x['trace_id'] for x in records)
        ops = set(x['operation_name'] for x in records)

        ops_txn = set(
            (x['operation_name'], x['tags'].get('db.txn')) for x in records
        )

        assert 'database fetch' in ops, 'database fetch in opentracing log'
        assert 'database transaction' in ops, 'database transaction'
        assert 'database use connection' in ops, 'database use in log'

        assert ('database transaction', 'commit') in ops_txn
        assert ('database transaction', 'rollback') in ops_txn

        assert len(ids) == 1, 'One trace id in all records'
        assert len(records) > 1, 'More than one records'


@pytest.fixture
def process_query(web_app_client):
    async def _process_query(key: str, value: str):
        key = urllib.parse.quote(key)
        value = urllib.parse.quote(value)
        response = await web_app_client.get(
            '/v1/pg/query-txn?key={}&value={}'.format(key, value),
        )
        assert response.status == 200
        return await response.json()

    return _process_query


def _get_records(caplog, prev_records: list = None):
    records = [
        json.loads(x.extdict.get('body'))
        for x in caplog.records
        if getattr(x, 'extdict', {}).get('_type') == 'span'
    ]

    if prev_records is not None:
        return records[len(prev_records) :]
    return records
