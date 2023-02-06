import datetime
import json
import pytest

from taxi.core import arequests
from taxi.core import async
from taxi_maintenance import run
from taxi_maintenance.stuff import send_bpq_push


NOW = datetime.datetime(2018, 6, 20, 10, 20, 0)
EPOCH = datetime.datetime.utcfromtimestamp(0)
NOW_MS = (NOW - EPOCH).total_seconds() * 1000


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(BPQ_ENABLE=True)
@pytest.mark.translations([
    ('taximeter_messages', 'bpq.push.title', 'en', 'bpq title'),
    ('taximeter_messages', 'bpq.push.text', 'en', 'bpq text'),
])
@pytest.inline_callbacks
def test_send_bpq_push(patch):

    context = {'calls': 0}

    @patch('taxi.external.taximeter._request')
    @async.inline_callbacks
    def test_taximeter_request(
            method, url, params=None, data=None,
            headers=None, json=None, log_extra=None
    ):
        context['calls'] += 1
        yield
        assert method == 'POST'
        assert url == 'http://driver-protocol.taxi.tst.yandex.net/service/push'
        assert json['data'].pop('id')
        assert json == {
            'code': 100,
            'driver_id': context['driver_id'],
            'park_db_id': 'park',
            'data': {
                'message': 'bpq text',
                'name': 'bpq title',
                'format': 0,
                'flags': ['bad_position_quality']
            },
        }

    context['driver_id'] = '2'
    yield send_bpq_push.do_stuff(partition=run.JobPartition(index=0, total=2))
    assert context['calls'] == 1
    context['calls'] = 0

    context['driver_id'] = '3'
    yield send_bpq_push.do_stuff(partition=run.JobPartition(index=1, total=2))
    assert context['calls'] == 1

    # check we do not send seconds push immediately
    yield send_bpq_push.do_stuff(partition=run.JobPartition(index=1, total=2))
    assert context['calls'] == 1


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(BPQ_ENABLE=False)
@pytest.inline_callbacks
def test_send_bpq_push_disabled(patch):

    @patch('taxi.external.taximeter._request')
    @async.inline_callbacks
    def test_taximeter_request(
            method, url, params=None, data=None,
            headers=None, json=None, log_extra=None
    ):
        assert False, 'should not be called'

    yield send_bpq_push.do_stuff(partition=run.JobPartition(index=0, total=2))
    yield send_bpq_push.do_stuff(partition=run.JobPartition(index=1, total=2))


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    BPQ_ENABLE=True,
    DRIVER_STATUS_USE_IN_TAXIADMIN=True,
)
@pytest.mark.parametrize('response_template, should_send', [
    (
        {
            'status': 'online',
            'updated_ts': NOW_MS
        },
        True
    ),
    (
        {
            'status': 'busy',
            'updated_ts': NOW_MS
        },
        False
    ),
    (
        {
            'status': 'offline',
        },
        False
    ),
    (
        {
            'status': 'online',
            'updated_ts': NOW_MS,
            'orders': [{
                'id': 'some_order',
                'status': 'transporting',
            }]
        },
        False
    ),
    (
        {
            'status': 'online',
            'updated_ts': NOW_MS,
            'orders': [{
                'id': 'some_order',
                'status': 'complete',
            }]
        },
        True
    ),
])
@pytest.mark.translations([
    ('taximeter_messages', 'bpq.push.title', 'en', 'bpq title'),
    ('taximeter_messages', 'bpq.push.text', 'en', 'bpq text'),
])
@pytest.inline_callbacks
def test_use_driver_status(patch, response_template, should_send):
    @patch('taxi.core.arequests._api._request')
    @async.inline_callbacks
    def _request(method, url, **kwargs):
        assert method == 'POST'
        assert 'v2/statuses' in url
        driver_ids = kwargs['json']['driver_ids']
        statuses = []
        for driver in driver_ids:
            status = response_template.copy()
            status['park_id'] = driver['park_id']
            status['driver_id'] = driver['driver_id']
            statuses.append(status)
        response = {'statuses': statuses}
        yield async.return_value(
            arequests.Response(status_code=200, content=json.dumps(response)),
        )

    context = {'calls': 0}

    @patch('taxi.external.taximeter._request')
    @async.inline_callbacks
    def test_taximeter_request(
            method, url, params=None, data=None,
            headers=None, json=None, log_extra=None
    ):
        context['calls'] += 1
        yield

    yield send_bpq_push.do_stuff()

    if should_send:
        assert context['calls'] > 0
    else:
        assert context['calls'] == 0
