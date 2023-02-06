import datetime
import decimal

import pytest

from testsuite.utils import http

from fleet_rent.generated.web import web_context as context_module
from fleet_rent.services import billing_orders


@pytest.mark.parametrize('alias_id', [None, 'some_alias'])
async def test_internal(
        web_context: context_module.Context, mock_billing_orders, alias_id,
):
    transaction = billing_orders.InternalTransactionData(
        rent_id='r',
        rent_serial_id=1,
        park_id='p',
        driver_id='d',
        scheduled_at=datetime.datetime(
            2020, 1, 2, tzinfo=datetime.timezone.utc,
        ),
        event_at=datetime.datetime.fromisoformat('2020-01-02T10:00+03:00'),
        trans_serial_id=2,
        amount=decimal.Decimal(10),
        currency='RUB',
        transfer_order_number='1',
        alias_id=alias_id,
    )

    @mock_billing_orders('/v2/process/async')
    async def _send(request: http.Request):
        result_alias = 'noorder/r'
        if alias_id:
            result_alias = alias_id
        assert request.json == {
            'orders': [
                {
                    'kind': 'arbitrary_entries',
                    'topic': 'taxi/periodic_payment/park_id/p/1/2',
                    'external_ref': '2',
                    'event_at': '2020-01-02T10:00:00+03:00',
                    'data': {
                        'schema_version': 'v1',
                        'topic_begin_at': '2020-01-02T10:00:00+03:00',
                        'event_version': 1,
                        'entries': [
                            {
                                'entity_external_id': (
                                    'taximeter_driver_id/p/d'
                                ),
                                'agreement_id': 'taxi/park_services',
                                'sub_account': 'recurring_payments',
                                'currency': 'RUB',
                                'amount': '-10',
                                'details': {
                                    'transfer_order_number': '1',
                                    'periodic_payment_data': {
                                        'scheduled_at': (
                                            '2020-01-02T00:00:00+00:00'
                                        ),
                                    },
                                },
                                'event_at': '2020-01-02T10:00:00+03:00',
                            },
                            {
                                'entity_external_id': (
                                    'taximeter_driver_id/p/d'
                                ),
                                'agreement_id': 'taxi/periodic_payments/1',
                                'sub_account': 'withhold',
                                'currency': 'RUB',
                                'amount': '10',
                                'details': {
                                    'periodic_payment_data': {
                                        'scheduled_at': (
                                            '2020-01-02T00:00:00+00:00'
                                        ),
                                    },
                                },
                                'event_at': '2020-01-02T10:00:00+03:00',
                            },
                        ],
                        'context': {
                            'alias_id': result_alias,
                            'driver': {'park_id': 'p', 'driver_uuid': 'd'},
                            'transfer_order_number': '1',
                            'taximeter_kind': 'taximeter_payment',
                        },
                    },
                },
            ],
        }
        return {
            'orders': [
                {
                    'doc_id': 2,
                    'topic': 'taxi/periodic_payment/park_id/p/1',
                    'external_ref': 'd2',
                },
            ],
        }

    bo_ = web_context.external_access.billing_orders

    await bo_.send_transactions_internal([transaction])


@pytest.mark.now('2020-01-04T16:00+00:00')
async def test_external(
        web_context: context_module.Context, mock_billing_orders,
):
    transaction = billing_orders.ExternalTransactionData(
        rent_id='r',
        amount=decimal.Decimal(10),
        park_id='p',
        local_driver_id='d',
        external_park_id='ep',
        external_driver_id='ed',
        scheduled_at=datetime.datetime(
            2020, 1, 2, tzinfo=datetime.timezone.utc,
        ),
        event_at=datetime.datetime(
            2020, 1, 4, 16, tzinfo=datetime.timezone.utc,
        ),
        event_number=2,
        transfer_order_number='1',
        park_clid='pc',
        park_currency='pc',
        park_billing_client_id='pbcli',
        park_billing_contract_id='pbcoi',
        driver_clid='dc',
        driver_billing_client_id='dbpli',
        driver_billing_contract_id='dbcoi',
    )

    @mock_billing_orders('/v2/process/async')
    async def _send(request: http.Request):
        assert request.json == {
            'orders': [
                {
                    'kind': 'periodic_payment',
                    'topic': 'taxi/periodic_payment/clid/pc/1',
                    'external_ref': '2',
                    'event_at': '2020-01-04T19:00:00+03:00',
                    'data': {
                        'schema_version': 'v1',
                        'amount': '10',
                        'currency': 'pc',
                        'transaction_type': 'PAYMENT',
                        'transfer_order_date': '2020-01-02T03:00:00+03:00',
                        'transfer_order_number': '1',
                        'external_driver': {
                            'clid': 'dc',
                            'billing_contract_id': 'dbcoi',
                            'billing_client_id': 'dbpli',
                            'db_id': 'ep',
                            'uuid': 'ed',
                        },
                        'driver': {'db_id': 'p', 'uuid': 'd'},
                        'park': {
                            'clid': 'pc',
                            'billing_contract_id': 'pbcoi',
                            'billing_client_id': 'pbcli',
                            'db_id': 'p',
                        },
                    },
                },
            ],
        }
        return {
            'orders': [
                {
                    'doc_id': 2,
                    'topic': 'taxi/periodic_payment/clid/pc/1',
                    'external_ref': 'd2',
                },
            ],
        }

    bo_ = web_context.external_access.billing_orders

    await bo_.send_transactions_external([transaction])
