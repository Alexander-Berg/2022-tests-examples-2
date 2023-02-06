import utils


TAXIMETER_PROXY_BASE_URL = 'http://localhost:8888/'


def test_taximeter_proxy_run():
    response = utils.retry_request(
        'get',
        TAXIMETER_PROXY_BASE_URL + 'taximeter/status',
    )
    assert response.status_code == 200
