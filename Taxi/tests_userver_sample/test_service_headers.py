async def test_trace_id_header(taxi_userver_sample):
    response = await taxi_userver_sample.get('/autogen/empty')
    assert response.headers['X-YaTraceId'].strip()
