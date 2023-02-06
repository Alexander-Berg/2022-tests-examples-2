import datetime
import json

from django import test as django_test
import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.core import db


ES_RESPONSE_DATA = [
    {'_source': {'@timestamp': '2019-04-03T00:00:00Z', 'text': 'message 1'}},
    {'_source': {'@timestamp': '2019-04-03T00:00:01Z', 'text': 'message 2'}},
    {'_source': {'@timestamp': '2019-04-03T00:00:02Z', 'text': 'message 3'}},
]

ST_TICKET_DESCRIPTION = '''
%%
link: 1234
{}
%%
'''.format(
    '\n'.join([
        '{} {}'.format(x['_source']['@timestamp'], x['_source']['text'])
        for x in reversed(ES_RESPONSE_DATA)
    ])
).strip()


@pytest.mark.parametrize('es_logs_source', [
    settings.ELASTIC_LOG_INDEX_IMPORT,
    settings.ELASTIC_LOG_INDEX_CRONS,
    'both'
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_multi_index_elastic_source(patch, es_logs_source):
    @patch('taxiadmin.api.views.cron_tasks._load_logs_from_elastic_index')
    @async.inline_callbacks
    def search_mock(connection, index, request, rows_count, log_extra=None):
        yield
        should_return = es_logs_source == 'both' or es_logs_source == index
        return_val = ES_RESPONSE_DATA if should_return else []
        async.return_value(return_val)

    @patch('taxi.external.startrack.create_ticket')
    @async.inline_callbacks
    def st_create_ticket_mock(st_request):
        yield
        assert st_request['description'] == ST_TICKET_DESCRIPTION
        async.return_value({'key': 'TAXIBACKEND-1'})

    yield _create_monitor()

    response = django_test.Client().post(
        '/api/cron_tasks/create_ticket/',
        data=json.dumps({
            'link': '1234'
        }),
        content_type='application/json'
    )
    assert response.status_code == 200

    calls = list(search_mock.calls)
    assert len(calls) == 2

    monitor = yield db.cron_monitor.find_one({'_id': 'test-task'})
    assert monitor
    assert len(monitor['tickets']) == 1
    ticket = monitor['tickets'][0]
    assert ticket == {'number': 'TAXIBACKEND-1', 'link': '1234'}


@async.inline_callbacks
def _create_monitor():
    yield db.cron_monitor.insert({
        '_id': 'test-task',
        'history': [],
        'tickets': [],
    })


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_monitor():
    yield db.cron_monitor.insert({
        '_id': 'test-task',
        'tickets': [],
        'state': 'green',
        'history': [
            {
                'status': 'in_progress',
                'start_time': datetime.datetime(2020, 3, 16, 11),
                'link': '123',
            },
        ],
    })

    response = django_test.Client().get('/api/cron_tasks/monitor/')
    assert response.status_code == 200
    data = json.loads(response.content)
    assert len(data) == 1
    assert data[0] == {
        'tickets': [],
        'state': 'green',
        'name': 'test-task',
        'history': [
            {
                'status': 'in_progress',
                'start_time': '2020-03-16T14:00:00+0300',
                'link': '123',
            },
        ],
    }
