import pytest


from tests_eats_payments import helpers

URL = 'v1/orders/retrieve'

BASE_REQUEST = {'id': 'test_order'}


@pytest.fixture(name='check_retrieve_order')
def check_retrieve_order_fixture(taxi_eats_payments, mockserver, load_json):
    async def _inner(response_status=200, response_body=None):
        response = await taxi_eats_payments.post(URL, json=BASE_REQUEST)
        assert response.status == response_status
        if response_body is not None:
            assert response.json() == response_body

    return _inner


@pytest.fixture(name='mock_retrieve_invoice_retrieve')
def _mock_retrieve_invoice_retrieve(mock_transactions_invoice_retrieve):
    def _inner(*args, **kwargs):
        # so that the data in test file does not interfere with test cases
        extra = {
            'sum_to_pay': [],
            'held': [],
            'cleared': [],
            'debt': [],
            **kwargs,
        }
        return mock_transactions_invoice_retrieve(*args, **extra)

    return _inner


async def test_debt_invoice_retrieve(
        check_retrieve_order,
        mock_retrieve_invoice_retrieve,
        upsert_debt_status,
        mock_debt_collector_by_ids,
):
    upsert_debt_status(order_id='test_order', debt_status='updated')

    debts = [helpers.make_debt(reason_code='technical_debt')]
    debt_collector_by_ids_mock = mock_debt_collector_by_ids(debts=debts)

    invoice_retrieve_mock = mock_retrieve_invoice_retrieve()
    await check_retrieve_order()

    assert invoice_retrieve_mock.times_called == 2
    assert debt_collector_by_ids_mock.times_called == 1
