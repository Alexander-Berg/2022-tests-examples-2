import http

import psycopg2.extras
import pytest

from testsuite.utils import callinfo

DEFAULT_PARAMS = {'email_id': 'personal_email_id_1'}


def _create_request(
        transaction_uuid: str,
        idempotency_token: str = 'new-idempotency-token',
):
    return {
        'transaction_uuid': transaction_uuid,
        'idempotency_token': idempotency_token,
    }


@pytest.mark.parametrize(
    ('params', 'request_body', 'expected_code'),
    (
        pytest.param(
            _create_request('transaction_uuid__3'),
            DEFAULT_PARAMS,
            http.HTTPStatus.OK,
            id='OK',
        ),
        pytest.param(
            _create_request('transaction_uuid__1'),
            DEFAULT_PARAMS,
            http.HTTPStatus.BAD_REQUEST,
            id='wrong-status-cancelled',
        ),
        pytest.param(
            _create_request('transaction_uuid__2'),
            DEFAULT_PARAMS,
            http.HTTPStatus.BAD_REQUEST,
            id='wrong-status-in-progress',
        ),
        pytest.param(
            _create_request(
                'transaction_uuid__3', 'unique_idempotency_token_1',
            ),
            DEFAULT_PARAMS,
            http.HTTPStatus.CONFLICT,
            id='idempotency-error',
        ),
        pytest.param(
            _create_request('not-found-uuid'),
            DEFAULT_PARAMS,
            http.HTTPStatus.NOT_FOUND,
            id='not-found',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=[
        'tables.sql',
        'orders.sql',
        'payment_transactions.sql',
        'receipts.sql',
    ],
)
async def test_admin_transactions_receipt_send(
        taxi_eats_integration_offline_orders_web,
        params,
        stq,
        pgsql,
        request_body,
        expected_code,
):
    response = await taxi_eats_integration_offline_orders_web.post(
        '/admin/v1/transactions/receipt', params=params, json=request_body,
    )
    assert response.status == expected_code

    try:
        stq_info = stq.eats_send_receipts_requests.next_call()
    except callinfo.CallQueueEmptyError:
        assert expected_code is not http.HTTPStatus.OK
        return

    assert expected_code is http.HTTPStatus.OK

    receipt_id = stq_info['args'][0]
    cursor = pgsql['eats_integration_offline_orders'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute(
        f"""
SELECT * from receipts
WHERE uuid='{receipt_id}'
        """,
    )
    row = cursor.fetchone()
    assert row
    assert row['transaction_uuid'] == params['transaction_uuid']
    assert row['idempotency_token'] == params['idempotency_token']
    assert row['uuid'] == receipt_id
    assert row['status'] == 'queued'
