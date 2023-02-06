import pytest

ENDPOINT = '/driver/v1/driver-money/v1/balance/closing-documents/url'

HEADERS_DEFAULT = {
    'User-Agent': 'Taximeter 8.90 (228)',
    'Accept-Language': 'ru',
    'X-Request-Application-Version': '8.90',
    'X-YaTaxi-Park-Id': 'park_id_0',
    'X-YaTaxi-Driver-Profile-Id': 'driver',
}


@pytest.mark.now('2022-02-16T12:00:00+0300')
@pytest.mark.experiments3(filename='experiments3_closing_documents.json')
async def test_empty_url(
        load_json,
        taxi_driver_money,
        mockserver,
        mock_parks_replica,
        mock_billing_replication,
):
    @mockserver.json_handler('yadoc/public/api/documents/1/url')
    def _yadoc_handle_url(request):
        assert request.method == 'GET'
        return {}

    @mockserver.json_handler('yadoc/public/api/v1/documents')
    def _yadoc_handle_list(request):
        return load_json('yadoc_list_response.json')

    response = await taxi_driver_money.get(
        ENDPOINT, headers=HEADERS_DEFAULT, params={'document_id': 1},
    )
    assert response.status_code == 500


@pytest.mark.now('2022-02-16T12:00:00+0300')
@pytest.mark.experiments3(filename='experiments3_closing_documents.json')
@pytest.mark.parametrize(
    'yadoc_url_request', [({'document_id': 2}), ({'document_id': 4})],
)
async def test_url(
        load_json,
        taxi_driver_money,
        mockserver,
        mock_parks_replica,
        mock_billing_replication,
        yadoc_url_request,
):
    @mockserver.json_handler('yadoc/public/api/documents/2/url')
    def _yadoc_handle_url(request):
        assert request.method == 'GET'
        return {'url': 'https://mdst.yandex.net/ryadoc/'}

    @mockserver.json_handler('yadoc/public/api/v1/documents')
    def _yadoc_handle_list(request):
        return load_json('yadoc_list_response.json')

    response = await taxi_driver_money.get(
        ENDPOINT, headers=HEADERS_DEFAULT, params=yadoc_url_request,
    )
    if yadoc_url_request['document_id'] == 2:
        assert response.status_code == 200
        assert response.json() == {
            'filename_with_extension': (
                'Счет-фактура 20220131000002 от 31.01.2022.pdf'
            ),
            'is_external': True,
            'type': 'navigate_url',
            'url': 'https://mdst.yandex.net/ryadoc/',
        }
    elif yadoc_url_request['document_id'] == 4:
        assert response.status_code == 400
        assert response.json()['message'] == 'Feature disabled'


@pytest.mark.now('2022-02-16T12:00:00+0300')
async def test_access(taxi_driver_money):
    response = response = await taxi_driver_money.get(
        ENDPOINT, headers=HEADERS_DEFAULT, params={'document_id': 1},
    )
    assert response.status_code == 400
    assert response.json()['message'] == 'Feature disabled'
