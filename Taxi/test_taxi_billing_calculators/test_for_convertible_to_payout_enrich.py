import pytest

from taxi import discovery
from taxi.billing.util import dates as billing_dates

from taxi_billing_calculators import models as calc_models
from taxi_billing_calculators.calculators.payout import doc_enricher


@pytest.mark.config(
    BILLING_CALCULATORS_ADD_TLOG_TARGET=True,
    BILLING_DRIVER_MODES_ENABLED=True,
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                BILLING_CALCULATORS_USE_V2_DOCS_UPDATE=False,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_CALCULATORS_USE_V2_DOCS_UPDATE=True,
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'test_data_path',
    [
        pytest.param('b2b_partner_payment.json'),
        pytest.param('invoice_transaction_cleared.json'),
        pytest.param('subvention.json'),
        pytest.param('commission.json'),
        pytest.param('promocode.json'),
    ],
)
# pylint: disable=invalid-name
async def test_enricher(
        patch_aiohttp_session,
        response_mock,
        mockserver,
        test_data_path,
        load_json,
        taxi_billing_calculators_stq_main_ctx,
):
    ctx = taxi_billing_calculators_stq_main_ctx
    test_data = load_json(test_data_path)
    input_doc_json = test_data['input_doc']

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        if 'v1/docs/update' in url:
            doc = input_doc_json.copy()
            assert doc['doc_id'] == json['doc_id']
            doc['data'].update(json['data'])
            doc['revision'] += 1
            return response_mock(json=doc)
        if 'v2/docs/update' in url:
            patch = {
                'doc_id': json['doc_id'],
                'data': json['data'],
                'entry_ids': json['entry_ids'],
                'revision': json['revision'] + 1,
                'idempotency_key': json['idempotency_key'],
                'status': json['status'],
            }
            return response_mock(json=patch)
        raise NotImplementedError

    @mockserver.json_handler('/billing-reports/v1/docs/select')
    async def _mock_billing_reports_docs_select(request, *args, **kwargs):
        nonlocal test_data
        subscription_as_of = billing_dates.parse_datetime(
            request.json['end_time'],
        )
        order_due = billing_dates.parse_datetime(
            input_doc_json['data']['driver_income']['order_event_at'],
        )
        assert subscription_as_of == order_due
        return {
            'docs': [
                {
                    'doc_id': 1000000001,
                    'kind': 'driver_mode_subscription',
                    'external_event_ref': '123',
                    'external_obj_id': (
                        'taxi/driver_mode_subscription/some_db_id/'
                        'driver-test'
                    ),
                    'data': {
                        'mode': 'orders',
                        'driver': {
                            'park_id': 'some_db_id',
                            'driver_id': 'driver-test',
                        },
                        'mode_rule': 'orders',
                    },
                    'event_at': '2019-10-01T00:00:00.000000+00:00',
                },
            ],
        }

    @mockserver.json_handler('/billing-replication/v2/contract/by_id/')
    def _patch_billing_replication_v2_contact_by_id(request):
        contract_id = request.json['ID']
        for contract in test_data['contracts']:
            if contract['ID'] == contract_id:
                return mockserver.make_response(json=contract)
        return None

    input_doc = calc_models.Doc.from_json(input_doc_json)

    enrich_doc = doc_enricher.get_data_enricher(input_doc.kind)
    enriched_doc = await enrich_doc(input_doc, ctx, None)
    assert enriched_doc.to_json() == test_data['expected_doc']
