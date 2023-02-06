import pytest

URL = 'v1/orders/faq'

BASE_REQUEST = {'order_nr': 'test_order'}
LOCALE_ENG = {'Accept-Language': 'en'}
TEST_RESPONSE_TYPE = 'retrieve_order_response'


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    return obj


@pytest.mark.parametrize(
    ('invoice_file', 'result_file'),
    [
        ('retrieve_invoice.json', 'faq_response.json'),
        (
            'retrieve_invoice_with_cashback.json',
            'faq_response_with_cashback.json',
        ),
        (
            'retrieve_invoice_with_hold_failed.json',
            'faq_response_with_hold_failed.json',
        ),
    ],
)
async def test_successful_payment(
        taxi_eats_payments,
        mock_transactions_invoice_retrieve,
        invoice_file,
        result_file,
        load_json,
):
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        file_to_load=invoice_file,
    )
    response = await taxi_eats_payments.get(URL, params=BASE_REQUEST)

    assert response.status == 200
    assert invoice_retrieve_mock.times_called == 1

    expected_response = load_json(result_file)
    print('expected response')
    print(ordered(expected_response))
    print('got response')
    print(ordered(response.json()))
    assert ordered(expected_response) == ordered(response.json())
