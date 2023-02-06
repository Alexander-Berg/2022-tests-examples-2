async def test_use_mimino_bb(request_proxy, mockserver):
    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return {}

    @mockserver.json_handler('/blackbox-mimino-test')
    def mock_blackbox_mimino(request):
        return {}

    await request_proxy(token='token')

    assert mock_blackbox_mimino.has_calls
    assert not mock_blackbox.has_calls
