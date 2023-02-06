# pylint: disable=import-error,wildcard-import
# flake8: noqa
import pytest

import uuid
import hashlib

from cargo_fiscal_transactions_ng import *  # noqa: F401 C5521

from tests_cargo_fiscal import const


async def test_stq_transactions_ng(
        stq_runner,
        create_context_record,
        taxi_cargo_fiscal,
        set_default_transactions_ng_response,
        get_default_fiscal_transactions,
):
    await stq_runner.cargo_fiscal_generate_transactions_ng.call(
        task_id=uuid.uuid4().hex,
        kwargs={
            'topic_id': const.TOPIC_ID,
            'consumer': 'delivery',
            'domain': 'orders',
        },
        expect_fail=False,
    )
    response = await taxi_cargo_fiscal.post(
        f'/internal/cargo-fiscal/receipts/delivery/'
        f'orders/result?topic_id={const.TOPIC_ID}',
    )

    assert response.status_code == 200

    # context in result handle checked in test_result.py
    response_json = response.json()
    response_json.pop('context')
    for receipt in response_json['receipts']:
        if 'context' in receipt:
            receipt.pop('context')

    assert response_json == {
        'receipts': [
            # supplied topic and transaction are absent in mock_t_ng response
            {'is_ready': False, 'transaction_id': const.TRANSACTION_ID},
            # topic and transaction are present in mock_t_ng response and
            # are saved
            {
                'is_ready': True,
                'transaction_id': '3f2d033a62d9961417410b9f1a57b079',
                'url': (
                    'https://trust.yandex.ru/pchecks/'
                    '3f2d033a62d9961417410b9f1a57b079/receipts/'
                    '3f2d033a62d9961417410b9f1a57b079?mode=mobile'
                ),
            },
            {
                'is_ready': True,
                'transaction_id': '3f2d033a62d9961417410b9f1a57b079_clearing',
                'url': 'some_url_should_be_here',
            },
        ],
    }


@pytest.mark.parametrize(
    'topic_id,transaction_id,is_return',
    (
        pytest.param(
            const.TOPIC_ID,
            const.TRANSACTION_ID,
            True,
            id='kz_buhta_refund_topic_context',
        ),
        pytest.param(
            const.TOPIC_ID_2,
            const.TRANSACTION_ID_2,
            False,
            id='kz_buhta_payment_topic_context',
        ),
        pytest.param(
            const.TOPIC_ID_01,
            const.TRANSACTION_ID_01,
            True,
            id='kz_buhta_refund_transaction_context',
        ),
        pytest.param(
            const.TOPIC_ID_21,
            const.TRANSACTION_ID_21,
            False,
            id='kz_buhta_payment_transaction_context',
        ),
    ),
)
async def test_stq_kaz_buhta(
        stq_runner,
        mock_buhta,
        taxi_cargo_fiscal,
        create_context_record,
        topic_id,
        transaction_id,
        is_return,
):
    await stq_runner.cargo_fiscal_generate_kaz_buhta.call(
        task_id=uuid.uuid4().hex,
        kwargs={
            'topic_id': topic_id,
            'transaction_id': transaction_id,
            'consumer': 'delivery',
            'domain': 'orders',
        },
        expect_fail=False,
    )
    response = await taxi_cargo_fiscal.post(
        f'/internal/cargo-fiscal/receipts/delivery/'
        f'orders/result?topic_id={topic_id}',
    )
    buhta_call = mock_buhta.next_call()
    assert buhta_call['request'].json == {
        'ride_id': topic_id,
        'payment_id': hashlib.md5(transaction_id.encode('utf-8')).hexdigest(),
        'partner_tax_id': '12345',
        'ride_finish_dt': '2021-05-31T19:00:00+0000',
        'text': 'Услуги доставки',
        'ride_amount': '120.0',
        'customer_payment_type': 'CASH',
        'is_return': is_return,
    }

    assert response.status_code == 200

    # context in result handle checked in test_result.py
    response_json = response.json()
    if 'context' in response_json:
        response_json.pop('context')
    for receipt in response_json['receipts']:
        receipt.pop('context')

    assert response_json == {
        'receipts': [
            {
                'is_ready': True,
                'transaction_id': transaction_id,
                'url': f'https://buhta.kz/yt/{topic_id}',
            },
        ],
    }


async def test_stq_kaz_buhta_bad(
        stq_runner, mock_buhta_bad, taxi_cargo_fiscal, create_context_record,
):
    await stq_runner.cargo_fiscal_generate_kaz_buhta.call(
        task_id=uuid.uuid4().hex,
        kwargs={
            'topic_id': const.TOPIC_ID,
            'transaction_id': const.TRANSACTION_ID,
            'consumer': 'delivery',
            'domain': 'orders',
        },
        expect_fail=False,
    )
    response = await taxi_cargo_fiscal.post(
        f'/internal/cargo-fiscal/receipts/delivery/'
        f'orders/result?topic_id={const.TOPIC_ID}',
    )

    assert response.status_code == 200

    # context in result handle checked in test_result.py
    response_json = response.json()
    response_json.pop('context')
    for receipt in response_json['receipts']:
        receipt.pop('context')

    assert response_json == {
        'receipts': [
            {
                'error': {
                    'code': 'logical_error',
                    'message': (
                        f'server responded with error, code '
                        f'PARTNER_NOT_FOUND'
                    ),
                    'details': {},
                },
                'is_ready': False,
                'transaction_id': const.TRANSACTION_ID,
            },
        ],
    }


@pytest.mark.parametrize(
    'topic_id,transaction_id,is_return,expected_prices,expected_receipt_type,validate_company_type',
    [
        pytest.param(
            const.TOPIC_ID_3,
            const.TRANSACTION_ID_3,
            False,
            ['102.560000', '120.0', '120.0'],
            305,
            1,
            id='payment_minus_vat_with_token_refresh',
        ),
        pytest.param(
            const.TOPIC_ID_4,
            const.TRANSACTION_ID_4,
            True,
            ['-120.100000', '-120.100000', '-120.100000'],
            400,
            2,
            id='refund_keep_vat_sum_to_negative_with_park_update',
        ),
        pytest.param(
            const.TOPIC_ID_5,
            const.TRANSACTION_ID_5,
            False,
            ['102.560000', '120.0', '120.0'],
            305,
            1,
            id='payment_minus_vat_with_token_refresh_cash',
        ),
        pytest.param(
            const.TOPIC_ID_6,
            const.TRANSACTION_ID_6,
            True,
            ['102.560000', '120.0', '120.0'],
            330,
            1,
            id='refund_minus_vat_no_negative',
        ),
        pytest.param(
            const.TOPIC_ID_3_TC,
            const.TRANSACTION_ID_3_TC,
            False,
            ['102.560000', '120.0', '120.0'],
            305,
            1,
            id='payment_minus_vat_with_token_refresh_transaction_context',
        ),
        pytest.param(
            const.TOPIC_ID_4_TC,
            const.TRANSACTION_ID_4_TC,
            True,
            ['-120.100000', '-120.100000', '-120.100000'],
            400,
            2,
            id='refund_keep_vat_with_park_update_transaction_context',
        ),
        pytest.param(
            const.TOPIC_ID_5_TC,
            const.TRANSACTION_ID_5_TC,
            False,
            ['102.560000', '120.0', '120.0'],
            305,
            1,
            id='payment_minus_vat_with_token_refresh_cash_transaction_context',
        ),
    ],
)
async def test_stq_isr_ezcount(
        stq_runner,
        mock_ez,
        mock_ez_auth,
        taxi_cargo_fiscal,
        create_context_record,
        topic_id,
        transaction_id,
        is_return,
        expected_prices,
        expected_receipt_type,
        validate_company_type,
):
    await stq_runner.cargo_fiscal_generate_isr_ez.call(
        task_id=uuid.uuid4().hex,
        kwargs={
            'topic_id': topic_id,
            'transaction_id': transaction_id,
            'consumer': 'delivery',
            'domain': 'orders',
        },
        expect_fail=False,
    )
    response = await taxi_cargo_fiscal.post(
        f'/internal/cargo-fiscal/receipts/delivery/'
        f'orders/result?topic_id={topic_id}',
    )

    # first call was with wrong auth token
    for _ in range(2):
        ez_call = mock_ez.next_call()
        if topic_id == const.TOPIC_ID_6:
            break

    if topic_id in (const.TOPIC_ID_5, const.TOPIC_ID_5_TC, const.TOPIC_ID_6):
        assert ez_call['request'].json == {
            'developer_email': 'v@v.ru',
            'auto_balance': True,
            'api_key': '5460afaa648bc05e4056b7b51aedeb3a9e7ef63d',
            'transaction_id': transaction_id,
            'type': expected_receipt_type,
            'customer_name': 'Beloved Client',
            'item': [
                {
                    'details': 'Delivery',
                    'price': expected_prices[0],
                    'amount': 1,
                },
            ],
            'payment': [
                {'payment_type': 1, 'payment_sum': expected_prices[1]},
            ],
            'price_total': expected_prices[2],
            'validate_company_type': validate_company_type,
        }
        return

    assert ez_call['request'].json == {
        'developer_email': 'v@v.ru',
        'auto_balance': True,
        'api_key': '5460afaa648bc05e4056b7b51aedeb3a9e7ef63d',
        'transaction_id': transaction_id,
        'type': expected_receipt_type,
        'customer_name': 'Beloved Client',
        'item': [
            {'details': 'Delivery', 'price': expected_prices[0], 'amount': 1},
        ],
        'payment': [
            {
                'payment_type': 3,
                'payment_sum': expected_prices[1],
                'cc_type': 2,
                'cc_type_name': 'Visa',
                'cc_number': '1234',
                'cc_deal_type': 1,
                'cc_num_of_payments': 1,
                'cc_payment_num': 1,
            },
        ],
        'price_total': expected_prices[2],
        'validate_company_type': validate_company_type,
    }

    assert response.status_code == 200

    # context in result handle checked in test_result.py
    response_json = response.json()
    if 'context' in response_json:
        response_json.pop('context')
    for receipt in response_json['receipts']:
        receipt.pop('context')

    assert response_json == {
        'receipts': [
            {
                'transaction_id': transaction_id,
                'is_ready': True,
                'url': (
                    'https://demo.ezcount.co.il/front/documents/get/3d0c6bd8'
                ),
            },
        ],
    }
