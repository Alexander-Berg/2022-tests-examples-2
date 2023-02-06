import http

import psycopg2.extras
import pytest


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=[
        'restaurants.sql',
        'tables.sql',
        'orders.sql',
        'payment_transactions.sql',
    ],
)
async def test_internal_eats_receipt_check_200(
        web_app_client, payment_transaction_uuid, load_json,
):

    response = await web_app_client.post(
        f'/internal/v1/eats-receipt-check',
        json={'document_id': payment_transaction_uuid},
    )
    assert response.status == 200
    data = await response.json()
    assert data == load_json('response_200.json')


async def test_internal_eats_receipt_check_404(
        web_app_client, payment_transaction_uuid,
):
    response = await web_app_client.post(
        f'/internal/v1/eats-receipt-check',
        json={'document_id': payment_transaction_uuid},
    )
    assert response.status == 404


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=[
        'restaurants.sql',
        'tables.sql',
        'orders.sql',
        'payment_transactions_with_empty_contacts.sql',
    ],
)
async def test_internal_eats_receipt_check_403(
        web_app_client, payment_transaction_uuid, load_json,
):

    response = await web_app_client.post(
        f'/internal/v1/eats-receipt-check',
        json={'document_id': payment_transaction_uuid},
    )
    assert response.status == 403


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=[
        'restaurants.sql',
        'tables.sql',
        'orders.sql',
        'with_zero_price_items/payment_transactions.sql',
    ],
)
async def test_receipt_check_only_non_zero_price_items(
        web_app_client, payment_transaction_uuid, load_json,
):
    response = await web_app_client.post(
        f'/internal/v1/eats-receipt-check',
        json={'document_id': payment_transaction_uuid},
    )
    assert response.status == 200
    data = await response.json()
    assert data == load_json('with_zero_price_items/response_200.json')


@pytest.mark.parametrize(
    ('document_id', 'expected_response', 'expected_status'),
    (
        pytest.param(
            'receipt_uuid__1',
            http.HTTPStatus.OK,
            'callback_processed',
            id='OK-receipt',
        ),
        pytest.param(
            'transaction_uuid__1',
            http.HTTPStatus.OK,
            None,
            id='OK-transaction',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=[
        'restaurants.sql',
        'tables.sql',
        'orders.sql',
        'payment_transactions.sql',
        'receipts.sql',
    ],
)
async def test_internal_eats_receipt_check_new_table(
        web_app_client,
        load_json,
        pgsql,
        document_id,
        expected_response,
        expected_status,
):
    response = await web_app_client.post(
        f'/internal/v1/eats-receipt-check', json={'document_id': document_id},
    )
    data = await response.json()
    assert data == load_json('response_200.json')
    cursor = pgsql['eats_integration_offline_orders'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute(
        f"""
SELECT status
FROM receipts
WHERE uuid='{document_id}'
        """,
    )
    row = cursor.fetchone()
    if expected_status is None:
        assert row is None
        return
    assert row['status'] == expected_status
