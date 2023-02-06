# pylint: disable=redefined-outer-name
import json

import pytest

from billing_fin_payouts import models
from billing_fin_payouts.generated.cron import cron_context
from . import configs


@pytest.mark.config(
    BILLING_FIN_PAYOUTS_SKIP_NETTING_SERVICES=(
        configs.BILLING_FIN_PAYOUTS_SKIP_NETTING_SERVICES
    ),
)
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_NETTING_SETTINGS=(
        configs.BILLING_FIN_PAYOUTS_NETTING_SETTINGS
    ),
)
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_VAT_RATE=configs.BILLING_FIN_PAYOUTS_VAT_RATE,
)
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_PRODUCT_WITH_VAT=(
        configs.BILLING_FIN_PAYOUTS_PRODUCT_WITH_VAT
    ),
)
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_ACCOUNT_INFO_FROM_BALANCE_REPLICA={
        'enabled': True,
        'client_ids': [],
    },
)
@pytest.mark.parametrize(
    'interface_model, yt_table_row_json, '
    'billing_replication_resp_json, '
    'billing_replication_expected_requests_json, '
    'interface_model_expected_payload_json, '
    'balance_replica_response_json, '
    'balance_replica_expected_requests_json,',
    [
        (
            models.InterfaceExpense,
            'expenses_yt_row.json',
            'billing_replication_response.json',
            'expenses_billing_replication_expected_requests.json',
            'expenses_model_expected_payload.json',
            'balance_replica_response.json',
            'expenses_balance_replica_expected_requests.json',
        ),
        (
            models.InterfaceExpense,
            'expenses_yt_row_cache.json',
            'billing_replication_response.json',
            'expenses_billing_replication_expected_requests_cache.json',
            'expenses_model_expected_payload_cache.json',
            'balance_replica_response.json',
            'expenses_balance_replica_expected_requests.json',
        ),
        (
            models.InterfaceExpense,
            'expenses_yt_row_cache.json',
            'billing_replication_response_no_country.json',
            'expenses_billing_replication_expected_requests_cache.json',
            'expenses_model_expected_payload_default_country.json',
            'balance_replica_response.json',
            'expenses_balance_replica_expected_requests.json',
        ),
        (
            models.InterfaceRevenue,
            'revenues_yt_row.json',
            'billing_replication_response.json',
            'revenues_billing_replication_expected_requests.json',
            'revenues_model_expected_payload.json',
            'balance_replica_response.json',
            'revenues_balance_replica_expected_requests.json',
        ),
        (
            models.InterfacePayment,
            'payments_yt_row.json',
            'billing_replication_response.json',
            'payments_billing_replication_expected_requests.json',
            'payments_model_expected_payload.json',
            'balance_replica_response.json',
            'payments_balance_replica_expected_requests.json',
        ),
    ],
    ids=[
        'enrich-expenses-row-br_200',
        'enrich-expenses-row-br_200-cache',
        'enrich-expenses-row-default_country',
        'enrich-revenues-row-br_200',
        'enrich-payments-row-br_200',
    ],
)
async def test_enrich_model(
        mockserver,
        load_json,
        interface_model,
        yt_table_row_json,
        billing_replication_resp_json,
        # pylint: disable=invalid-name
        billing_replication_expected_requests_json,
        interface_model_expected_payload_json,
        balance_replica_response_json,
        balance_replica_expected_requests_json,
):

    yt_table_row = load_json(yt_table_row_json)
    billing_replication_resp = load_json(billing_replication_resp_json)
    billing_replication_expected_requests = load_json(
        billing_replication_expected_requests_json,
    )
    interface_model_expected_payload = load_json(
        interface_model_expected_payload_json,
    )
    balance_replica_expected_requests = load_json(
        balance_replica_expected_requests_json,
    )
    balance_replica_response = load_json(balance_replica_response_json)

    contract_requests = []

    @mockserver.json_handler('/billing-replication/v2/contract/by_id/')
    async def _contract_by_id(request):
        nonlocal contract_requests
        contract_requests.append(request.json)
        resp = billing_replication_resp['/v2/contract/by_id/'][0]
        resp['json']['ID'] = request.json['ID']
        return mockserver.make_response(**resp)

    accounts_requests = []

    @mockserver.json_handler(
        '/balance-replica/v1/personal_accounts/by_contract_id',
    )
    async def _personal_accounts_by_contract_id(request):
        nonlocal accounts_requests
        accounts_requests.append(request.json)
        resp = balance_replica_response[
            '/v1/personal_accounts/by_contract_id/'
        ][0]
        return mockserver.make_response(**resp)

    context = cron_context.Context()
    await context.on_startup()

    model = interface_model.from_yt(context=context, data=yt_table_row)
    model = await model.enrich(context=context)

    await context.on_shutdown()

    # check all contact_requests
    assert (
        contract_requests
        == billing_replication_expected_requests['/v2/contract/by_id/']
    )
    assert (
        accounts_requests
        == balance_replica_expected_requests[
            '/v1/personal_accounts/by_contract_id/'
        ]
    )

    # check model payload
    assert (
        model.payload
        and json.loads(model.payload) == interface_model_expected_payload
    )
