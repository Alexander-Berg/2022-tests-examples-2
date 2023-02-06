import pytest

from form_builder.generated.cron import run_cron


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
async def test_task(mockserver, cron_context):
    @mockserver.json_handler('/ok')
    def _ok_handler(request):
        assert request.method == 'POST'
        assert request.headers['content-type'] == 'application/json'
        assert request.json == {'a': 'A', 'b': 1}
        return {}

    @mockserver.json_handler('/ok/2')
    def _ok_2_handler(request):
        assert request.method == 'POST'
        assert request.headers['content-type'] == 'application/json'
        assert request.headers['some'] == 'b'
        assert request.json == {'a': 'A', 'submit_id': 'b'}
        return {}

    @mockserver.json_handler('/fail')
    def _fail_handler(_):
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/fail/2')
    def _fail_2_handler(_):
        return mockserver.make_response(status=500)

    await run_cron.main(
        ['form_builder.crontasks.stages_submitter', '-t', '0', '-d'],
    )
    data = await cron_context.pg.primary.fetch(
        'SELECT * FROM form_builder.partial_request_queue',
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
