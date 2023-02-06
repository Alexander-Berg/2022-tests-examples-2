import pytest

from transactions.clients.trust import service_details


def _build_invoice(id_: str) -> dict:
    return {'_id': id_}


def _build_taxi_invoice(alias_id: str) -> dict:
    return {'performer': {'taxi_alias': {'id': alias_id}}}


@pytest.mark.parametrize(
    'invoice_data, merchant_order_id, item_id, expected',
    [
        pytest.param(
            _build_invoice('some_invoice_id'),
            None,
            'food',
            'some_invoice_id_food',
            id='should use invoice_id if there\'s no merchant_order_id',
        ),
        pytest.param(
            _build_invoice('some_invoice_id'),
            'some_merchant_order_id',
            'food',
            'some_merchant_order_id_food',
            id='should use merchant_order_id',
        ),
    ],
)
def test_trust_details_build_trust_order_id(
        invoice_data, merchant_order_id, item_id, expected,
):
    actual = service_details.TrustDetails().build_trust_order_id(
        invoice_data=invoice_data,
        merchant_order_id=merchant_order_id,
        item_id=item_id,
    )
    assert actual == expected


@pytest.mark.parametrize(
    'invoice_data, merchant_order_id, item_id, expected',
    [
        pytest.param(
            _build_taxi_invoice('some_alias_id'),
            None,
            'ride',
            'some_alias_id',
            id='should ignore item_id == `ride`',
        ),
        pytest.param(
            _build_taxi_invoice('some_alias_id'),
            None,
            'tips',
            'some_alias_id_tips',
            id='should respect item_id != `ride`',
        ),
        pytest.param(
            _build_taxi_invoice('some_alias_id'),
            'some_merchant_order_id',
            'tips',
            'some_merchant_order_id_tips',
            id='should prefer merchant_order_id to alias_id',
        ),
    ],
)
def test_taxi_trust_details_build_trust_order_id(
        invoice_data, merchant_order_id, item_id, expected,
):
    actual = service_details.TaxiTrustDetails().build_trust_order_id(
        invoice_data=invoice_data,
        merchant_order_id=merchant_order_id,
        item_id=item_id,
    )
    assert actual == expected
