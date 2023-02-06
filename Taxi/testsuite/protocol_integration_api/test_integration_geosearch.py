import pytest


@pytest.mark.config(GEOSEARCH_RESULTS_LIMIT=100)
def test_geosearch_response_with_uri(taxi_integration, mockserver, load_json):

    """
    All tests are in protocol's geosearch!
    As at the curent time int-api's geosearch is protocols's geosearch
    (just a proxy in fastcgi)
    """

    req = {
        'uri': (
            'ymapsbm1://geo?ll=37.617645%2C55.755817&'
            'spn=0.641735%2C0.466232&'
            'text=%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F%'
            '2C%20%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%20'
        ),
    }

    geo_docs = load_json('yamaps.json')

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return geo_docs

    response = taxi_integration.post('v1/geosearch', req)

    assert response.status_code == 200
    assert 'uri' in response.json()['objects'][0]
