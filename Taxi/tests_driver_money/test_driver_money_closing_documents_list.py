import pytest

ENDPOINT = '/driver/v1/driver-money/v1/balance/closing-documents/list'

HEADERS_DEFAULT = {
    'User-Agent': 'Taximeter 8.90 (228)',
    'Accept-Language': 'ru',
    'X-Request-Application-Version': '8.90',
    'X-YaTaxi-Park-Id': 'park_id_0',
    'X-YaTaxi-Driver-Profile-Id': 'driver',
}


@pytest.mark.now('2022-02-16T12:00:00+0300')
@pytest.mark.experiments3(filename='experiments3_closing_documents.json')
async def test_no_closing_document(
        taxi_driver_money,
        load_json,
        mockserver,
        driver_authorizer,
        mock_parks_replica,
        mock_billing_replication,
):
    yadoc_request = load_json('yadoc_request.json')
    yadoc_response_empty = load_json('yadoc_response_empty.json')

    @mockserver.json_handler('yadoc/public/api/v1/documents')
    def _yadoc_handle(request):
        assert request.method == 'POST'
        assert request.json == yadoc_request
        return yadoc_response_empty

    response = await taxi_driver_money.get(ENDPOINT, headers=HEADERS_DEFAULT)

    assert response.status_code == 200
    assert response.json() == load_json('expected_response_empty.json')


@pytest.mark.now('2022-02-16T12:00:00+0300')
@pytest.mark.experiments3(filename='experiments3_closing_documents.json')
async def test_closing_document(
        taxi_driver_money,
        load_json,
        mockserver,
        mock_parks_replica,
        mock_billing_replication,
):
    yadoc_request = load_json('yadoc_request.json')
    yadoc_responses = load_json('yadoc_responses.json')

    @mockserver.json_handler('yadoc/public/api/v1/documents')
    def _yadoc_handle(request):
        assert request.method == 'POST'
        if 'page' in request.query.keys():
            assert request.json == yadoc_request
            return yadoc_responses['second_response']
        assert request.json == yadoc_request
        return yadoc_responses['first_response']

    response = await taxi_driver_money.get(ENDPOINT, headers=HEADERS_DEFAULT)

    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')


@pytest.mark.now('2022-02-16T12:00:00+0300')
async def test_access(taxi_driver_money):
    response = await taxi_driver_money.get(ENDPOINT, headers=HEADERS_DEFAULT)
    assert response.status_code == 400
    assert response.json()['message'] == 'Feature disabled'
