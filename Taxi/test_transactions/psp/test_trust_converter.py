# pylint: disable=protected-access
import datetime as dt

import pytest

from generated.models import psp

from transactions.internal.payment_gateways.psp import trust_converter


_PAYMENT_CREATED = psp.EventPaymentCreated(
    origin='PaymentCreated',
    payment=psp.Payment(
        authorization_due_date=dt.datetime(2022, 1, 1),
        cash=psp.Cash(
            amount=20000, currency=psp.Currency(symbolic_code='RUB'),
        ),
        created_at=dt.datetime(2022, 1, 4),
        flow=psp.PaymentFlowType('hold'),
        payment_id='some_payment_id',
        payment_method_id='some_payment_method_id',
        payment_session_id='some_payment_session_id',
        trust_payment_id='some_trust_payment_id',
    ),
)


@pytest.mark.now('2022-01-01T00:00:00+00:00')
@pytest.mark.parametrize(
    'events_response, expected',
    [
        pytest.param(
            [
                _PAYMENT_CREATED,
                psp.EventPaymentStatusChanged(
                    origin='PaymentStatusChanged',
                    payment_id='some_payment_id',
                    payment_method_id='some_payment_method_id',
                    payment_status='authorized',
                    authorized_cash=psp.Cash(
                        amount=20000,
                        currency=psp.Currency(
                            symbolic_code='RUB', exponent='2',
                        ),
                    ),
                    response_code='success',
                ),
                psp.EventPaymentStatusChanged(
                    origin='PaymentStatusChanged',
                    payment_id='payment_some_id',
                    payment_method_id='some_payment_method_id',
                    payment_status='cancelled',
                    response_code='success',
                ),
            ],
            {
                'uid': 'some_uid',
                'amount': '200',
                'currency': 'RUB',
                'unhold_real_ts': '1640984400.0',
                'final_status_ts': '1640984400.0',
                'payment_ts': '1641243600.0',
                'paysys_sent_ts': '1641243600.0',
                'start_ts': '1641243600.0',
                'payment_resp_code': 'success',
            },
            id='it should add unhold_real_ts',
        ),
        pytest.param(
            [
                _PAYMENT_CREATED,
                psp.EventPaymentStatusChanged(
                    origin='PaymentStatusChanged',
                    payment_id='some_payment_id',
                    payment_method_id='some_payment_method_id',
                    payment_status='authorized',
                    authorized_cash=psp.Cash(
                        amount=20000,
                        currency=psp.Currency(
                            symbolic_code='RUB', exponent='2',
                        ),
                    ),
                    response_code='success',
                ),
                psp.EventPaymentStatusChanged(
                    origin='PaymentStatusChanged',
                    payment_id='payment_some_id',
                    payment_method_id='some_payment_method_id',
                    payment_status='captured',
                    captured_cash=psp.Cash(
                        amount=10000,
                        currency=psp.Currency(
                            symbolic_code='RUB', exponent='2',
                        ),
                    ),
                    response_code='recurring_token_revoked',
                    additional_transaction_info=(
                        psp.AdditionalTransactionInfo(
                            trust_terminal_id=666, rrn='123',
                        )
                    ),
                    payer=psp.Payer(
                        contact_info=psp._PayerContactInfo(
                            phone='+75556667788',
                        ),
                        ip_address='127.0.0.1',
                    ),
                    payment_method_details=(
                        psp.PaymentMethodDetails(
                            payment_method_type='bank_card',
                            bank_card_metadata=(
                                psp.PaymentMethodsStoredBankCard(
                                    first6='123456',
                                    last4='1234',
                                    payment_system='visa',
                                )
                            ),
                        )
                    ),
                ),
            ],
            {
                'uid': 'some_uid',
                'terminal': {'id': 666},
                'primary_terminal': {'id': 666},
                'payment_ts': '1641243600.0',
                'paysys_sent_ts': '1641243600.0',
                'start_ts': '1641243600.0',
                'clear_real_ts': '1640984400.0',
                'clear_ts': '1640984400.0',
                'reversal_id': 'payment_some_id/reversal',
                'amount': '200',
                'orig_amount': '200',
                'current_amount': '100',
                'cleared_amount': '100',
                'rrn': '123',
                'payment_method': 'card',
                'currency': 'RUB',
                'payment_resp_code': 'restricted_card',
                'user_account': '123456****1234',
                'card_type': 'visa',
                'user_phone': '+75556667788',
                'final_status_ts': '1640984400.0',
            },
            id='it should add all relevant fields',
        ),
    ],
)
def test_convert_to_tx_response(events_response, expected):
    actual = trust_converter.convert_to_tx_response(
        events_response, 'some_uid',
    )
    assert actual == expected


@pytest.mark.parametrize(
    'events_response, expected',
    [
        pytest.param(
            [
                psp.EventRefundStatusChanged(
                    origin='RefundStatusChanged',
                    payment_id='some_payment_id',
                    refund_id='some_refund_id',
                    refund_status='succeeded',
                    additional_transaction_info=(
                        psp.AdditionalTransactionInfo()
                    ),
                    response_code='success',
                ),
                psp.EventRefundStatusChanged(
                    origin='RefundStatusChanged',
                    payment_id='some_payment_id',
                    refund_id='failed_refund_id',
                    refund_status='failed',
                    additional_transaction_info=(
                        psp.AdditionalTransactionInfo()
                    ),
                    response_code='incorrect_customer_billing_data',
                ),
            ],
            {
                'some_refund_id': {'status': 'success'},
                'failed_refund_id': {'status': 'failed'},
            },
            id='it should return status & status_desc',
        ),
    ],
)
def test_convert_to_refunds_responses(events_response, expected):
    actual = trust_converter.convert_to_refunds_responses(events_response)
    assert actual == expected
