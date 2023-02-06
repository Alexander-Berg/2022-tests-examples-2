def test_basic(mockserver_info, _mockserver):
    assert mockserver_info.host == _mockserver.host
    assert mockserver_info.port == _mockserver.port
    assert mockserver_info.base_url == _mockserver.base_url
