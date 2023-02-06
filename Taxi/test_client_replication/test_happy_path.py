from taxi.clients import replication


async def test_replication(library_context, mockserver):
    url = '/replication/data/rule'
    mocked_result = {'some': 'tome'}

    @mockserver.handler(url)
    def patched(request):
        return mockserver.make_response(json=mocked_result)

    result = await library_context.client_replication.put_data_into_queue(
        'rule',
        [replication.ReplicationItem('id', {'data': None})],
        log_extra={},
    )

    assert result == mocked_result
    assert patched.times_called == 1
    patched_call_args = await patched.wait_call()
    patched_call_request = patched_call_args['request']
    assert patched_call_request.method == 'POST'
    assert patched_call_request.url.endswith(url)
    # not checking headers, mockserver makes them like real
    assert patched_call_request.json == {
        'items': [{'data': {'data': None}, 'id': 'id'}],
    }
