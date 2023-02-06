import pytest

input_json = {
    'id': 'ea173bdf73bce2724d8546cf160080f9',
    'results': 1,
    'skip': 0,
    'sort': 'dist',
    'what': [60.864131, 56.658118],
}


@pytest.mark.config(GEOSEARCH_RESULTS_LIMIT=100)
def test_geosearch_below_threshold(taxi_protocol):
    response = taxi_protocol.post('3.0/geosearch', input_json)
    assert response.status_code == 200


@pytest.mark.config(GEOSEARCH_RESULTS_LIMIT=0)
def test_geosearch_above_threshold(taxi_protocol):
    response = taxi_protocol.post('3.0/geosearch', input_json)
    assert response.status_code == 400


@pytest.mark.config(GEOSEARCH_RESULTS_LIMIT=100)
def test_geosearch_response_with_uri(taxi_protocol, mockserver, load_json):
    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        geo_docs = load_json('yamaps_luzhniki.json')
        return geo_docs

    response = taxi_protocol.post('3.0/geosearch', input_json)

    assert response.status_code == 200
    assert 'uri' in response.json()['objects'][0]
