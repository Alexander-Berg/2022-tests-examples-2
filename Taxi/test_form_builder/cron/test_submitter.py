import json

import pytest

from testsuite.utils import matching


HEADERS_BOUNDARY = matching.RegexString(
    r'multipart/mixed; boundary=[0-9a-f]{32}',
)
START_PAYLOAD_BOUNDARY = matching.RegexString(r'--[0-9a-f]{32}')
FINISH_PAYLOAD_BOUNDARY = matching.RegexString(r'--[0-9a-f]{32}--')


class _AsyncWriter:
    def __init__(self):
        self.parts = []

    @property
    def data(self):
        return '\n'.join(self.parts)

    async def write(self, part):
        self.parts.append(part)


@pytest.mark.usefixtures('mockserver_personal')
@pytest.mark.config(
    FORM_SUBMIT_SETTINGS={
        'chunk_size': 2,
        'iterations_count': 4,
        'iterations_pause': 0,
        'max_fail_count': 2,
        'max_request_retries_count': 2,
    },
    FORM_SUBMIT_TIMEOUT_SETTINGS={
        'default': 0.1,
        'by_url': {'http://test2.com': 1},
        'by_host': {'test.com': 1},
    },
    TVM_RULES=[{'src': 'form-builder', 'dst': 'personal'}],
)
async def test_do_stuff(mockserver, cron_runner, cron_context):
    @mockserver.json_handler('/ok')
    def _ok_handler(request):
        assert request.method == 'POST'
        assert request.headers['content-type'] == 'application/json'
        assert request.headers['some'] == 'submit_id-1'
        assert request.json == {'a': 'A', 'b': 1, 'submit_id': 'submit_id-1'}
        return {}

    @mockserver.json_handler('/ok/2')
    def _ok_2_handler(request):
        assert request.method == 'POST'
        assert request.headers['content-type'] == 'application/json'
        assert request.json == {'a': 'A', 'b': 1, 'submit_id': 'submit_id-2'}
        return {}

    @mockserver.json_handler('/fail')
    def _fail_handler(_):
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/fail/2')
    def _fail_2_handler(_):
        return mockserver.make_response(status=500)

    await cron_runner.submitter()
    data = await cron_context.pg.primary.fetch(
        'SELECT * FROM form_builder.request_queue',
    )
    assert {x['response_id']: x['status'] for x in data} == {
        1: 'SUBMITTED',
        2: 'SUBMITTED',
        3: 'FAILED',
        4: 'FAILED',
    }
    assert (
        _ok_handler.times_called
        + _ok_2_handler.times_called
        + _fail_handler.times_called
        + _fail_2_handler.times_called
    ) == 9


def _string(val: str):
    return {'type': 'string', 'stringValue': val}


def _integer(val: int):
    return {'type': 'integer', 'integerValue': val}


def _number(val: float):
    return {'type': 'number', 'numberValue': val}


def _boolean(val: bool):
    return {'type': 'boolean', 'booleanValue': val}


def _date_time(val: str):
    return {'type': 'datetime', 'datetimeValue': val}


def _file(val: str):
    return {'type': 'file', 'fileValue': val}


def _array(*val: dict):
    return {'type': 'array', 'arrayValue': [*val]}


@pytest.mark.parametrize(
    'a_field, a_request, b_field, b_request',
    [
        (_string('A'), '"A"', _integer(1), 1),
        (_number(1.0), 1.0, _boolean(False), 'false'),
        (
            _array(_integer(1), _integer(2)),
            '[1, 2]',
            _date_time('2020-03-27T12:00:00.0Z'),
            '"2020-03-27T12:00:00.0Z"',
        ),
        (_file('YWFhYQ=='), '"YWFhYQ=="', _integer(1), 1),
    ],
)
@pytest.mark.config(
    FORM_SUBMIT_SETTINGS={
        'chunk_size': 1,
        'iterations_count': 1,
        'iterations_pause': 0,
        'max_fail_count': 1,
        'max_request_retries_count': 1,
    },
)
async def test_submitting_several_types(
        mockserver,
        cron_context,
        cron_runner,
        a_field,
        a_request,
        b_field,
        b_request,
):
    await cron_context.pg.primary.execute(
        f"""
    INSERT INTO form_builder.response_values
        (response_id,key,value,is_array, value_type)
    VALUES
       (1, 'a', '{json.dumps(a_field)}', false, 'some'),
       (1, 'b', '{json.dumps(b_field)}', false, 'some')
       ;
    """,
    )

    @mockserver.json_handler('/test')
    def _ok_handler(request):
        assert request.method == 'POST'
        assert request.headers['content-type'] == 'application/json'
        assert (
            request.get_data().decode()
            == f'{{"a": {a_request}, "b": {b_request}}}'
        )
        return {}

    await cron_runner.submitter()
    data = await cron_context.pg.primary.fetch(
        'SELECT response_id, status FROM form_builder.request_queue',
    )
    assert [dict(x) for x in data] == [
        {'response_id': 1, 'status': 'SUBMITTED'},
    ]


@pytest.mark.config(
    FORM_SUBMIT_SETTINGS={
        'chunk_size': 1,
        'iterations_count': 2,
        'iterations_pause': 0,
        'max_fail_count': 1,
        'max_request_retries_count': 1,
    },
)
async def test_multipart(mockserver, cron_context, cron_runner):
    @mockserver.handler('/submit/file-only')
    async def _file_only_handler(request):
        expected_headers = {
            'Host': matching.any_string,
            'User-Agent': matching.any_string,
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Length': '224',
            'Content-Type': HEADERS_BOUNDARY,
        }
        assert dict(request.headers) == expected_headers
        assert request.get_data().decode().split() == (
            [
                START_PAYLOAD_BOUNDARY,
                'Content-Type:',
                'application/octet-stream',
                'Content-Length:',
                '4',
                'Content-Disposition:',
                'attachment;',
                'filename="test-file";',
                'filename*=utf-8\'\'test-file',
                'aaaa',
                FINISH_PAYLOAD_BOUNDARY,
            ]
        )
        return mockserver.make_response()

    @mockserver.handler('/submit/file-n-json')
    def _file_n_json_handler(request):
        expected_headers = {
            'Host': matching.any_string,
            'User-Agent': matching.any_string,
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Length': '326',
            'Content-Type': HEADERS_BOUNDARY,
        }
        assert dict(request.headers) == expected_headers
        assert request.get_data().decode().split() == [
            START_PAYLOAD_BOUNDARY,
            'Content-Type:',
            'application/json',
            'Content-Length:',
            '10',
            '{"a":',
            '"A"}',
            START_PAYLOAD_BOUNDARY,
            'Content-Type:',
            'application/octet-stream',
            'Content-Length:',
            '4',
            'Content-Disposition:',
            'attachment;',
            'filename="test-file";',
            'filename*=utf-8\'\'test-file',
            'aaaa',
            FINISH_PAYLOAD_BOUNDARY,
        ]
        return mockserver.make_response()

    await cron_runner.submitter()

    data = await cron_context.pg.primary.fetch(
        'SELECT response_id, status FROM form_builder.request_queue',
    )
    assert [dict(x) for x in data] == [
        {'response_id': 1, 'status': 'SUBMITTED'},
        {'response_id': 2, 'status': 'SUBMITTED'},
    ]
