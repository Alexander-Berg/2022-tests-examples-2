import datetime
import decimal
from typing import Optional

import pytest

from taxi.clients import stq_agent

from taxi_billing_calculators import config as calculators_config
from taxi_billing_calculators import models
from taxi_billing_calculators.calculators.bypass import helper


@pytest.mark.config(
    BILLING_CALCULATORS_CREATE_BY_TYPE_TAXIMETER_REQUEST_DOCS={
        '__default__': False,
        'commission_calculated': True,
    },
    TAXIMETER_BILLING_INTERACTION={'db_suffixes': [], 'enable': True},
)
@pytest.mark.parametrize(
    'kind, db_id, expected',
    [
        ('taximeter_payment', 'abcdef', False),  # disabled by kind by default
        ('commission_calculated', 'abcdef', True),  # enabled by kind and db_id
    ],
)
# pylint: disable=invalid-name
def test_create_taximeter_request_doc_by_kind(
        kind, db_id, expected, taxi_billing_calculators_stq_main_ctx,
):
    assert (
        helper.create_taximeter_request_doc(
            taxi_billing_calculators_stq_main_ctx.config,
            kind=kind,
            db_id=db_id,
        )
        == expected
    )


@pytest.mark.config(
    BILLING_CALCULATORS_CREATE_BY_TYPE_TAXIMETER_REQUEST_DOCS={
        '__default__': False,
        'commission_calculated': True,
    },
    TAXIMETER_BILLING_INTERACTION={'db_suffixes': ['abcdef'], 'enable': False},
)
@pytest.mark.parametrize(
    'kind, db_id, expected',
    [
        (  # enabled by kind, disabled by db_id
            'commission_calculated',
            'abcdef',
            False,
        ),
    ],
)
# pylint: disable=invalid-name
def test_create_taximeter_request_doc_disabled_by_db_id(
        kind, db_id, expected, taxi_billing_calculators_stq_main_ctx,
):
    assert (
        helper.create_taximeter_request_doc(
            taxi_billing_calculators_stq_main_ctx.config,
            kind=kind,
            db_id=db_id,
        )
        == expected
    )


@pytest.mark.config(
    BILLING_CALCULATORS_CREATE_BY_TYPE_TAXIMETER_REQUEST_DOCS={
        '__default__': False,
        'commission_calculated': True,
    },
    TAXIMETER_BILLING_INTERACTION={'db_suffixes': ['abcdef'], 'enable': True},
)
@pytest.mark.parametrize(
    'kind, db_id, expected',
    [
        (  # enabled by kind, enabled by db_id suffix
            'commission_calculated',
            'abcdef',
            True,
        ),
        (  # enabled by kind, disabled by db_id suffix
            'commission_calculated',
            'fedcba',
            False,
        ),
    ],
)
# pylint: disable=invalid-name
def test_create_taximeter_request_doc_by_db_id(
        kind, db_id, expected, taxi_billing_calculators_stq_main_ctx,
):
    assert (
        helper.create_taximeter_request_doc(
            taxi_billing_calculators_stq_main_ctx.config,
            kind=kind,
            db_id=db_id,
        )
        == expected
    )


@pytest.mark.config(BILLING_CALCULATORS_CREATE_TAXIMETER_REQUEST_DOC=False)
# pylint: disable=invalid-name
async def test_create_taximetre_doc_and_process(
        taxi_billing_calculators_stq_main_ctx, patch,
):
    doc = models.Doc(
        doc_id=322,
        event_at=datetime.datetime(2020, 1, 1),
        data={
            'alias_id': 'some_alias_id',
            'driver': {'db_id': 'some_db_id', 'driver_uuid': 'some_uuid'},
            'order_id': 'some_order_id',
        },
        external_event_ref='some_external_event_ref',
        external_obj_id='some_external_obj_id',
        journal_entries=[],
        kind='base_document_kind',
        tags=[],
        status=models.DocStatus.NEW.value,
    )
    entries = [
        models.Entry(
            entity=models.Entity(
                external_id='some_external_id', kind='driver',
            ),
            agreement_id='some_agreement_id',
            sub_account='some_sub_account',
            amount=decimal.Decimal('228.0'),
            currency='RUB',
        ),
    ]

    @patch('taxi_billing_calculators.stq.helper.put_to_stq_queue')
    async def _put_stq(
            config: calculators_config.config,
            stq_client: stq_agent.StqAgentClient,
            queue: str,
            task_id: str,
            kwargs: Optional[dict] = None,
            eta: Optional[datetime.datetime] = None,
            log_extra: Optional[dict] = None,
    ):
        del eta
        del log_extra
        assert queue == 'billing_calculators_taximeter_process_doc'
        assert task_id == (
            'taximeter_request/based_on_doc_id/322'
            '/transaction_id/some_transaction_id'
        )
        assert kwargs == {
            'doc_id': None,
            'kind': 'taximeter_request',
            'event_at': '2020-01-01T00:00:00.000000+00:00',
            'external_event_ref': (
                'taxi/taximeter_request/some_kind/some_transaction_id'
            ),
            'data': {
                'based_on_doc_id': 322,
                'payments': [
                    {
                        'agreement': 'some_agreement_id',
                        'amount': '228.0',
                        'currency': 'RUB',
                        'sub_account': 'some_sub_account',
                    },
                ],
                'kind': 'some_kind',
                'transaction_id': 'some_transaction_id',
                'alias_id': 'some_alias_id',
                'driver': {'db_id': 'some_db_id', 'driver_uuid': 'some_uuid'},
            },
        }

    await helper.create_taximeter_doc_and_process(
        ctx=taxi_billing_calculators_stq_main_ctx,
        doc=doc,
        kind='some_kind',
        transaction_id='some_transaction_id',
        entries=entries,
        billing_park_commission_flow=None,
        log_extra=None,
    )
