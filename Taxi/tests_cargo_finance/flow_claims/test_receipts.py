import pytest


RESULT_200 = {
    'receipts': [
        {
            'url': (
                'https://trust-test.yandex.ru/pchecks/'
                'aec7b89fd2c83526e70c6213f79065d7/receipts/aec7'
                'b89fd2c83526e70c6213f79065d7?mode=mobile'
            ),
        },
        {
            'url': (
                'https://trust-test.yandex.ru/pchecks/'
                'aec7b89fd2c83526e70c6213f79065d7/receipts/619f'
                'a501910d3920ed06bf35?mode=mobile'
            ),
        },
        {
            'url': (
                'https://trust-test.yandex.ru/pchecks/'
                'receipt_without_clearing_url'
            ),
        },
    ],
}

RESULT_404 = {
    'code': 'claim_invoice_not_found',
    'details': {},
    'message': 'invoice for claim not found',
}


RESULT_400 = {'code': '400', 'message': 'Failed to parse request'}


@pytest.mark.parametrize(['expected_code'], [(200,), (404,), (400,)])
async def test_get_receipts(
        mockserver, taxi_cargo_finance, load_json, expected_code,
):
    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    def _mock_invoice_retrieve(request):
        if expected_code == 200:
            assert request.json['id'] == 'claims/agent/some_id'
            return mockserver.make_response(
                json=load_json('../static/test_receipts.json'), status=200,
            )
        return mockserver.make_response(
            json={'code': 'fail', 'message': 'i fail'}, status=404,
        )

    if expected_code == 400:
        flow = 'wrong_flow'
    else:
        flow = 'claims'
    uri = f'/b2b/cargo-finance/receipts?entity_id=some_id&flow={flow}'
    response = await taxi_cargo_finance.post(uri)
    assert response.status == expected_code
    assert response.json() == globals()[f'RESULT_{expected_code}']
