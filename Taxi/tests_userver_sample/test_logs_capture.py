async def test_select(taxi_userver_sample):
    async with taxi_userver_sample.capture_logs() as capture:
        response = await taxi_userver_sample.post(
            'json-echo', json={'hello': 'world'},
        )
        assert response.status_code == 200

    assert capture.select(
        link=response.headers['x-yarequestid'], text='json-echo handler body',
    )


async def test_subscribe(taxi_userver_sample, mockserver):
    async with taxi_userver_sample.capture_logs() as capture:

        @capture.subscribe(
            text='json-echo handler body', trace_id=mockserver.trace_id,
        )
        def log_event(link, **other):
            pass

        response = await taxi_userver_sample.post(
            'json-echo', json={'hello': 'world'},
        )
        assert response.status_code == 200
        call = await log_event.wait_call()
        assert call['link'] == response.headers['x-yarequestid']
