import json

import pytest

from billing_fin_payouts.stq import process_payments
from test_billing_fin_payouts import common_utils
from . import stq_payout_common_utils

_PAYMENT_ORDER_DESCRIPTION = (
    'Опл.по Дог. {contract_id} от {contract_dt} {amount} {currency}'
)
_PAYMENT_REQUIREMENT_DESCRIPTION = (
    'Опл.по Дог. {contract_id} от {contract_dt} {amount} {currency}'
)
_PAYMENT_REVENUE_REQUIREMENT_DESCRIPTION = (
    'Опл. по счету № {lst} за услуги по доступу к сервису {amount} {currency}'
)


@pytest.mark.config(
    BILLING_FIN_PAYOUTS_STQ_PROCESS_PAYMENTS_ENABLED=True,
    BILLING_FIN_PAYOUTS_SEND_PAYMENTS_TO_BANK_ENABLED=True,
    BILLING_FIN_PAYOUTS_SEND_DRY_PAYMENTS_TO_BANK_ENABLED=True,
    BILLING_FIN_PAYOUTS_YANDEX_FIRM_BANK_DETAILS={
        '13': [
            {
                'start': '1999-01-01T00:00:00.000000+00:00',
                'end': '2099-01-01T00:00:00.000000+00:00',
                'bank_details': {
                    'account_number': '40700000000000000000',
                    'secdist_token_key': 'taxi',
                },
            },
        ],
    },
    BILLING_FIN_PAYOUTS_WALLET_PAYMENT_BANK_DETAILS=[
        {
            'start': '1999-01-01T00:00:00.000000+00:00',
            'end': '2099-01-01T00:00:00.000000+00:00',
            'bank_details': {
                'inn': '7750004168',
                'name': 'АО "Яндекс Банк"// ',
            },
        },
    ],
    BILLING_FIN_PAYOUTS_YA_BANK_PAYMENT_DESCRIPTION={
        'PAYMENT_ORDER_PAYMENT': _PAYMENT_ORDER_DESCRIPTION,
        'PAYMENT_REQUIREMENT_PAYMENT': _PAYMENT_REQUIREMENT_DESCRIPTION,
        'PAYMENT_ORDER_EXPENSE': _PAYMENT_ORDER_DESCRIPTION,
        'PAYMENT_REQUIREMENT_EXPENSE': _PAYMENT_REQUIREMENT_DESCRIPTION,
        'PAYMENT_ORDER_REVENUE': _PAYMENT_ORDER_DESCRIPTION,
        'PAYMENT_REQUIREMENT_REVENUE': (
            _PAYMENT_REVENUE_REQUIREMENT_DESCRIPTION
        ),
        'PAYMENT_ORDER_NETTING': _PAYMENT_ORDER_DESCRIPTION,
        'PAYMENT_REQUIREMENT_NETTING': _PAYMENT_ORDER_DESCRIPTION,
        'PAYMENT_REQUIREMENT_NETTING_WITH_LST': (
            _PAYMENT_REVENUE_REQUIREMENT_DESCRIPTION
        ),
    },
    BILLING_FIN_PAYOUTS_PAYMENTS_RESCHEDULE_SETTINGS={
        '__default__': {'eta_min_interval': 0, 'eta_max_interval': 0},
    },
)
@pytest.mark.now('2022-06-01T00:00:00.000000+00:00')
@pytest.mark.parametrize(
    """
    test_data_json
    """,
    [
        pytest.param(
            'payment_order.json',
            marks=[
                pytest.mark.pgsql(
                    dbname='billing_fin_payouts', files=('payment_order.sql',),
                ),
            ],
        ),
        pytest.param(
            'payment_order_fake_contract.json',
            marks=[
                pytest.mark.pgsql(
                    dbname='billing_fin_payouts',
                    files=('payment_order_fake_contract.sql',),
                ),
                pytest.mark.config(
                    BILLING_FIN_PAYOUTS_YA_BANK_FAKE_CONTRACT={
                        'enabled': True,
                        'contract_data': {
                            'client_id': '1234343',
                            'FIRM_ID': 13,
                            'EXTERNAL_ID': 'FAKE-123456/12',
                            'YANDEX_BANK_ENABLED': 1,
                            'YANDEX_BANK_WALLET_PAY': 1,
                            'YANDEX_BANK_WALLET_ID': 'some fake wallet id',
                            'YANDEX_BANK_ACCOUNT_ID': None,
                            'DT': '2019-03-15',
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            'payment_requirement.json',
            marks=[
                pytest.mark.pgsql(
                    dbname='billing_fin_payouts',
                    files=('payment_requirement.sql',),
                ),
            ],
        ),
        pytest.param(
            'payment_requirement_netting.json',
            marks=[
                pytest.mark.pgsql(
                    dbname='billing_fin_payouts',
                    files=('payment_requirement_netting.sql',),
                ),
            ],
        ),
        pytest.param(
            'payment_requirement_netting_no_lst.json',
            marks=[
                pytest.mark.pgsql(
                    dbname='billing_fin_payouts',
                    files=('payment_requirement_netting_no_lst.sql',),
                ),
            ],
        ),
        pytest.param(
            'payment_order_sent_to_bank_accepted.json',
            marks=[
                pytest.mark.pgsql(
                    dbname='billing_fin_payouts',
                    files=('payment_order_sent_to_bank.sql',),
                ),
            ],
        ),
        pytest.param(
            'payment_order_sent_to_bank_new.json',
            marks=[
                pytest.mark.pgsql(
                    dbname='billing_fin_payouts',
                    files=('payment_order_sent_to_bank.sql',),
                ),
            ],
        ),
        pytest.param(
            'payment_order_sent_to_bank_finished.json',
            marks=[
                pytest.mark.pgsql(
                    dbname='billing_fin_payouts',
                    files=('payment_order_sent_to_bank.sql',),
                ),
            ],
        ),
        pytest.param(
            'payment_order_sent_to_bank_finished_partial.json',
            marks=[
                pytest.mark.pgsql(
                    dbname='billing_fin_payouts',
                    files=('payment_order_sent_to_bank.sql',),
                ),
            ],
        ),
        pytest.param(
            'payment_order_sent_to_bank_failed.json',
            marks=[
                pytest.mark.pgsql(
                    dbname='billing_fin_payouts',
                    files=('payment_order_sent_to_bank.sql',),
                ),
            ],
        ),
        pytest.param(
            'payment_order_failed.json',
            marks=[
                pytest.mark.pgsql(
                    dbname='billing_fin_payouts',
                    files=('payment_order_failed.sql',),
                ),
            ],
        ),
        pytest.param(
            'payment_requirement_sent_to_bank_finished.json',
            marks=[
                pytest.mark.pgsql(
                    dbname='billing_fin_payouts',
                    files=('payment_requirement_sent_to_bank.sql',),
                ),
            ],
        ),
        pytest.param(
            'payment_order_sent_to_bank_finished_cpf_refund.json',
            marks=[
                pytest.mark.pgsql(
                    dbname='billing_fin_payouts',
                    files=('payment_order_sent_to_bank_cpf_refund.sql',),
                ),
            ],
        ),
    ],
)
async def test_process_payments(
        stq3_context,
        stq,
        load_json,
        process_payments_task_info,
        patch,
        mockserver,
        test_data_json,
):
    test_data = load_json(test_data_json)

    # pylint: disable=unused-variable
    @patch('jwt.encode')
    def _do_not_encode_jwt(payload, *args, **kwargs) -> bytes:
        return json.dumps(payload).encode()

    @mockserver.json_handler('/billing-replication/v2/contract/by_id/')
    async def _contract_by_id(request):
        resp = test_data['billing_replication_resp']['/v2/contract/by_id/'][0]
        resp['json']['ID'] = request.json['ID']
        return mockserver.make_response(**resp)

    actual_document = None

    @mockserver.json_handler('/bank-h2h/h2h/v1/process_document')
    async def _v1_process_document(request):
        nonlocal actual_document
        actual_document = json.loads(request.json['document_jwt'])
        resp = test_data['bank_h2h_resp']['/h2h/v1/process_document'][0]
        return mockserver.make_response(**resp)

    document_details_request = None

    @mockserver.json_handler('/bank-h2h/h2h/v1/get_document_details')
    async def _v1_get_document_details(request):
        nonlocal document_details_request
        document_details_request = json.loads(request.json['request_jwt'])
        resp = test_data['bank_h2h_resp']['/h2h/v1/get_document_details'][0]
        return mockserver.make_response(**resp)

    await process_payments.task(
        context=stq3_context,
        task_info=process_payments_task_info,
        payment_id=1,
    )

    pool = await stq3_context.pg.master_pool

    await stq_payout_common_utils.check_payment_event_log(
        pool=pool, data_expected=test_data['expected_payment_event_log'],
    )

    await stq_payout_common_utils.check_cash_payment_fact(
        pool=pool,
        data_expected=test_data.get('expected_cash_payment_fact', []),
    )

    assert actual_document == test_data['expected_bank_document']
    assert (
        document_details_request
        == test_data['expected_bank_document_details_request']
    )
    common_utils.check_stq_calls(
        queue=stq.billing_fin_payouts_process_payments,
        expected_calls=test_data['expected_stq_calls'],
    )
