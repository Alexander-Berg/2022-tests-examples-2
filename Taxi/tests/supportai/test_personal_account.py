import json
import pytest

from nile.api.v1 import clusters, Record
from nile.api.v1.local import StreamSource, ListSink

from projects.supportai.personal_account import statistics
from projects.supportai.personal_account import statistics_v2


@pytest.fixture
def sample_request_response():
    return [
        (
            b'link1',
            '2021-05-13 12:43:25,173998',
            {
                'chat_id': 'ticket@1424252494',
                'dialog': {
                    'messages': [
                        {
                            'author': 'user',
                            'text': 'Не могу поменять способ оплаты.',
                        },
                    ],
                },
                'features': [],
            },
            {
                'reply': {'text': '413903302'},
                'tag': {
                    'add': ['ml_topic_413903302', 'experiment3_not_available'],
                },
            },
        ),
        (
            b'link2',
            '2021-05-13 12:42:25,173998',
            {
                'chat_id': 'ticket@1424252494',
                'dialog': {
                    'messages': [
                        {
                            'author': 'user',
                            'text': 'Не могу поменять способ оплаты.',
                        },
                    ],
                },
                'features': [],
            },
            {
                'reply': {'text': '413903302'},
                'tag': {
                    'add': ['ml_topic_413903302', 'experiment3_not_available'],
                },
            },
        ),
        (
            b'link3',
            '2021-05-13 10:43:25,173998',
            {
                'dialog': {
                    'messages': [
                        {
                            'author': 'user',
                            'text': 'Не могу поменять способ оплаты.',
                        },
                    ],
                },
                'features': [],
            },
            {
                'forward': {'line': 1},
                'reply': {'text': 'forwarded'},
                'tag': {
                    'add': ['ml_topic_413903302', 'experiment3_not_available'],
                },
            },
        ),
        (
            b'link4',
            '2021-05-13 10:43:25,173998',
            {
                'dialog': {
                    'messages': [
                        {
                            'author': 'user',
                            'text': 'Не могу поменять способ оплаты.',
                        },
                    ],
                },
                'features': [],
            },
            {
                'close': {},
                'reply': {'text': 'Im finished'},
                'tag': {
                    'add': ['ml_topic_413903302', 'experiment3_not_available'],
                },
            },
        ),
    ]


@pytest.fixture
def sample_records(sample_request_response):
    return [
        Record(
            link=link,
            project=b'ya_market_support',
            request_time=date,
            response_time=date,
            request_body=json.dumps(request),
            response_body=json.dumps(response),
        )
        for link, date, request, response in sample_request_response
    ]


def test_statistics(sample_records):
    job = clusters.MockCluster().job()

    input_table = job.table('').label('input')
    statistics.eval_statistics(input_table).label('output')
    output = []

    job.local_run(
        sources={'input': StreamSource(sample_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 1
    record = output[0]
    assert record['request_number'] == 4
    assert record['ai_answered_request_number'] == 4


def test_dialogs(sample_records):
    job = clusters.MockCluster().job()

    input_table = job.table('').label('input')
    statistics.eval_example_dialogs(input_table).label('output')
    output = []

    job.local_run(
        sources={'input': StreamSource(sample_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 2


# WARN: flaky test
def test_statistics_v2(sample_records):
    job = clusters.MockCluster().job()

    input_table = job.table('').label('input')
    result = statistics_v2.eval_statistics(
        input_table, chat_finished_threshold_hours=1,
    )
    result.label('output')

    output = []

    job.local_run(
        sources={'input': StreamSource(sample_records)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 2

    record = output[0]
    assert record['chat_number'] == 2
    assert record['replied_number'] == 2
    assert record['finished_number'] == 2
    assert record['forwarded_number'] == 1
    assert record['closed_number'] == 1
