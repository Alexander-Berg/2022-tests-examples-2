import pytest

PARK_CLID = 'park_clid'
INVOICE_ID = 'invoice_id'


@pytest.mark.skip  # gather contexts handle implementation suspended
async def test_gather_context(
        taxi_cargo_fiscal,
        mock_py2_fiscal_data,
        set_default_transactions_ng_response,
):
    response = await taxi_cargo_fiscal.post(
        '/internal/cargo-fiscal/receipts/delivery/orders/fetch-context',
        json={
            'topic_id': 'topic_id',
            'park_clid': PARK_CLID,
            'invoice_id': INVOICE_ID,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'payment_method': 'card',
        'personal_tin_id': '1514a5c7d59247afa82489b273e45303',
        'provider_inn': '085715582283',
        'vat': 'vat_none',
    }


@pytest.mark.skip  # gather contexts handle implementation suspended
async def test_gather_context_bad(
        taxi_cargo_fiscal,
        mock_py2_fiscal_data,
        set_default_transactions_ng_response,
):
    response = await taxi_cargo_fiscal.post(
        '/internal/cargo-fiscal/receipts/some_service/some_id/fetch-context',
        json={
            'topic_id': 'topic_id',
            'park_clid': PARK_CLID,
            'invoice_id': INVOICE_ID,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'consumer_or_domain_not_supported',
        'details': {},
        'message': 'This combination of consumer and domain is not supported',
    }
