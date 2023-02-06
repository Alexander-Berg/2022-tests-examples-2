import collections
import decimal
import itertools
from unittest import mock

import aiohttp
import pytest

from taxi import discovery
from taxi.billing import clients
from taxi.clients import antifraud as antifraud_client
from taxi.clients import tvm
from taxi.clients import uantifraud as uantifraud_client

from taxi_billing_subventions import config
from taxi_billing_subventions import process_doc
from taxi_billing_subventions import services
from taxi_billing_subventions.common import models
from test_taxi_billing_subventions import helpers
from test_taxi_billing_subventions.test_process_doc import AccountsClient
from test_taxi_billing_subventions.test_process_doc import AgglomerationsClient
from test_taxi_billing_subventions.test_process_doc import (
    BillingReplicationClient,
)
from test_taxi_billing_subventions.test_process_doc import CommissionsClient
from test_taxi_billing_subventions.test_process_doc import DocsClient
from test_taxi_billing_subventions.test_process_doc import OrdersClient
from test_taxi_billing_subventions.test_process_doc import ParksReplicaClient
from test_taxi_billing_subventions.test_process_doc import ReportsClient
from test_taxi_billing_subventions.test_process_doc import StqAgentClientMock
from test_taxi_billing_subventions.test_process_doc import SubventionsClient

Result = collections.namedtuple('Result', 'accounts, docs, orders')


@pytest.mark.now('2020-09-01T20:18:35Z')
async def test_order_completed_creates_orfb(
        make_context, patch, load_json, session,
):
    doc = load_json('order_completed.json')
    context = make_context(doc)
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=doc['doc_id'],
    )
    actual_docs = context.docs_client.created_docs
    _assert_created_doc_kinds(['order_ready_for_billing'], actual_docs)
    _assert_doc(load_json('order_ready_for_billing.json'), actual_docs)


@pytest.mark.now('2020-09-01T20:18:35Z')
async def test_orfb_creates_accounts(
        make_context, patch, uantifraud, load_json,
):
    doc = load_json('order_ready_for_billing.json')
    context = make_context(doc)
    result = await process_order_ready_for_billing(context, doc, patch)
    _assert_accounts(
        result.accounts, load_json('expected_accounts_single_ontop.json'),
    )


@pytest.mark.now('2020-09-01T20:18:35Z')
async def test_orfb_get_matching_rules_from_bsx(
        make_context, patch, matcher, uantifraud, load_json,
):
    doc = load_json('order_ready_for_billing.json')
    context = make_context(doc)
    await process_order_ready_for_billing(context, doc, patch)
    assert matcher.times_called == 1
    assert matcher.next_call()['request'].json == {
        'activity_points': 90,
        'geoareas': ['test_zone_1'],
        'has_lightbox': False,
        'has_sticker': False,
        'reference_time': '2020-09-01T19:31:35.000000+00:00',
        'rule_types': ['single_ontop'],
        'tags': [],
        'tariff_class': 'econom',
        'timezone': 'Europe/Moscow',
        'unique_driver_id': '5afee214453b0a524e56d237',
        'zone': 'driver_zone',
    }


@pytest.mark.now('2020-09-01T20:18:35Z')
async def test_orfb_checks_order_in_antifraud(
        make_context, patch, uantifraud, load_json,
):
    doc = load_json('order_ready_for_billing.json')
    context = make_context(doc)
    await process_order_ready_for_billing(context, doc, patch)
    assert uantifraud.times_called == 3
    assert uantifraud.next_call()['request'].json == {
        'order': {
            'id': 'some_order_id',
            'transporting_time': 33,
            'transporting_distance': 37,
        },
        'subvention': {'type': 'single_ride'},
    }


@pytest.mark.now('2020-09-01T20:18:35Z')
async def test_orfb_sends_to_orders(
        make_context, patch, uantifraud, load_json,
):
    doc = load_json('order_ready_for_billing.json')
    context = make_context(doc)
    result = await process_order_ready_for_billing(context, doc, patch)
    _assert_orders([], result.orders)


@pytest.mark.now('2020-09-01T20:18:35Z')
async def test_orfb_creates_docs(make_context, patch, uantifraud, load_json):
    expected = [
        'payment_subvention_journal',
        'subvention_antifraud_check',
        'subvention_journal',
    ]
    doc = load_json('order_ready_for_billing.json')
    context = make_context(doc)
    result = await process_order_ready_for_billing(context, doc, patch)
    _assert_created_doc_kinds(expected, result.docs)


@pytest.mark.now('2020-09-01T20:18:35Z')
@pytest.mark.parametrize(
    'expected',
    (
        'payment_subvention_journal.json',
        'subvention_antifraud_check.json',
        'subvention_journal.json',
    ),
)
async def test_orfb_created_doc_content(
        make_context, patch, matcher, uantifraud, load_json, expected,
):
    doc = load_json('order_ready_for_billing.json')
    context = make_context(doc)
    result = await process_order_ready_for_billing(context, doc, patch)
    assert matcher.times_called == 1
    _assert_doc(load_json(expected), result.docs)


@pytest.mark.now('2020-09-01T20:18:35Z')
async def test_orfb_cancelled_creates_docs(
        make_context, patch, uantifraud, load_json,
):
    doc = load_json('order_ready_for_billing.json')
    doc['data']['order'].update({'taxi_status': 'cancelled'})
    context = make_context(doc)
    result = await process_order_ready_for_billing(context, doc, patch)
    _assert_created_doc_kinds(
        ['payment_subvention_journal', 'subvention_journal'], result.docs,
    )


@pytest.mark.now('2020-09-01T20:18:35Z')
@pytest.mark.parametrize(
    'expected',
    ('payment_subvention_journal_cancelled.json', 'subvention_journal.json'),
)
async def test_orfb_cancelled_doc_content(
        make_context, patch, uantifraud, load_json, expected,
):
    doc = load_json('order_ready_for_billing.json')
    doc['data']['order'].update({'taxi_status': 'cancelled'})
    context = make_context(doc)
    result = await process_order_ready_for_billing(context, doc, patch)
    _assert_doc(load_json(expected), result.docs)


@pytest.mark.now('2020-09-01T20:18:35Z')
async def test_orfb_blocked_by_antifraud_creates_docs(
        make_context, patch, uantifraud_block, load_json,
):
    doc = load_json('order_ready_for_billing.json')
    context = make_context(doc)
    result = await process_order_ready_for_billing(context, doc, patch)
    _assert_created_doc_kinds(
        ['payment_subvention_journal', 'subvention_journal'], result.docs,
    )


@pytest.mark.now('2020-09-01T20:18:35Z')
@pytest.mark.parametrize(
    'expected',
    (
        'payment_subvention_journal_blocked_by_antifraud_in_orfb.json',
        'subvention_journal.json',
    ),
)
async def test_orfb_blocked_by_antifraud_check_doc_content(
        make_context, patch, uantifraud_block, load_json, expected,
):
    doc = load_json('order_ready_for_billing.json')
    context = make_context(doc)
    result = await process_order_ready_for_billing(context, doc, patch)
    _assert_doc(load_json(expected), result.docs)


async def process_order_ready_for_billing(context, doc, patch):
    _patch_get_currency_data(patch)
    _enable_order_ready_for_billing_configs(context.config)
    _enable_antifraud(context.config)
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=doc['doc_id'],
    )
    return Result(
        accounts=context.accounts_client.created_accounts,
        docs=context.docs_client.created_docs,
        orders=context.orders_client.created_docs,
    )


@pytest.mark.now('2020-09-01T20:18:35Z')
@pytest.mark.parametrize('expected', ('subvention_antifraud_complete.json',))
async def test_antifraud_check_creates_doc(
        make_context, load_json, mock_antifraud, expected,
):
    mock_antifraud(load_json('antifraud_response_pay.json'))
    doc = load_json('subvention_antifraud_check.json')
    context = make_context(
        doc, existing_docs=[load_json('order_ready_for_billing.json')],
    )
    _enable_antifraud(context.config)
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=doc['doc_id'],
    )
    actual_docs = context.docs_client.created_docs
    _assert_created_doc_kinds(['subvention_antifraud_complete'], actual_docs)
    _assert_doc(load_json(expected), actual_docs)


@pytest.mark.now('2020-09-01T20:18:35Z')
@pytest.mark.parametrize(
    'antifraud_response_json,expected',
    (
        (
            'antifraud_response_pay.json',
            ['payout_subvention.json', 'payout_subvention_antifraud.json'],
        ),
        (
            'antifraud_response_delay.json',
            ['payout_subvention_antifraud_delay.json'],
        ),
        (
            'antifraud_response_block.json',
            [
                'payout_subvention_block.json',
                'payout_subvention_antifraud_block.json',
            ],
        ),
    ),
)
async def test_antifraud_check_sends_to_orders(
        make_context,
        load_json,
        mock_antifraud,
        antifraud_response_json,
        expected,
):
    mock_antifraud(load_json(antifraud_response_json))
    doc = load_json('subvention_antifraud_check.json')
    context = make_context(
        doc, existing_docs=[load_json('order_ready_for_billing.json')],
    )
    _enable_antifraud(context.config)
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=doc['doc_id'],
    )
    assert len(context.orders_client.created_docs) == len(expected)
    for order in expected:
        _assert_orders(load_json(order), context.orders_client.created_docs)


@pytest.mark.now('2020-09-01T20:18:35Z')
@pytest.mark.parametrize(
    'expected,obj_id,event_ref',
    (
        (
            'subvention_rules_restored.json',
            'alias_id/some_alias_id',
            'subvention_antifraud_check/1212/subvention_rules_restored',
        ),
        ('payment_subvention_journal_from_complete.json', None, None),
        ('subventions_update_needed.json', None, None),
    ),
)
async def test_antifraud_complete_creates_doc(
        make_context, load_json, expected, obj_id, event_ref,
):
    doc = load_json('subvention_antifraud_complete.json')
    context = make_context(
        doc,
        existing_docs=[
            load_json('order_ready_for_billing.json'),
            load_json('subvention_antifraud_check.json'),
        ],
    )
    _enable_antifraud_complete(context.config)
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=doc['doc_id'],
    )
    assert len(context.docs_client.created_docs) == 3
    if obj_id and event_ref:
        _assert_doc_by_id(
            obj_id,
            event_ref,
            load_json(expected),
            context.docs_client.created_docs,
        )
    else:
        _assert_doc(load_json(expected), context.docs_client.created_docs)


@pytest.mark.now('2020-09-01T20:18:35Z')
async def test_antifraud_complete_does_not_send_docs_to_orders(
        make_context, load_json,
):
    doc = load_json('subvention_antifraud_complete.json')
    context = make_context(
        doc,
        existing_docs=[
            load_json('order_ready_for_billing.json'),
            load_json('subvention_antifraud_check.json'),
        ],
    )
    _enable_antifraud_complete(context.config)
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=doc['doc_id'],
    )
    assert not context.orders_client.created_docs


@pytest.mark.now('2020-09-01T20:18:35Z')
@pytest.mark.parametrize('doc_json', ['subvention_rules_restored.json'])
async def test_subvention_rules_restored_creates_doc(
        make_context, load_json, doc_json,
):
    doc = load_json(doc_json)
    context = make_context(
        doc,
        existing_docs=[
            load_json('order_ready_for_billing.json'),
            load_json('subvention_antifraud_check.json'),
            load_json('subvention_antifraud_complete.json'),
        ],
    )
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=doc['doc_id'],
    )
    assert not context.docs_client.created_docs


@pytest.mark.now('2020-09-01T20:18:35Z')
@pytest.mark.parametrize(
    'expected',
    ('order_subvention_changed.json', 'subvention_value_calculated.json'),
)
async def test_subvention_updates_needed_creates_doc(
        make_context, load_json, expected,
):
    doc = load_json('subventions_update_needed.json')
    context = make_context(
        doc,
        existing_docs=[
            load_json('order_ready_for_billing.json'),
            load_json('subvention_antifraud_check.json'),
            load_json('subvention_antifraud_complete.json'),
        ],
    )
    _enable_subvention_updates_needed(context.config)
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=doc['doc_id'],
    )
    actual_docs = context.docs_client.created_docs
    _assert_created_doc_kinds(
        ['order_subvention_changed', 'subvention_value_calculated'],
        actual_docs,
    )
    _assert_doc(load_json(expected), context.docs_client.created_docs)


def _assert_accounts(actual_accounts, expected_accounts):
    for actual, expected in itertools.zip_longest(
            actual_accounts, expected_accounts,
    ):
        assert expected == actual, (
            'Failed comparing account with agreement_id="%s"'
            % expected['agreement_id']
        )


def _assert_created_doc_kinds(expected, actual_docs):
    kinds = [doc['kind'] for doc in actual_docs]
    assert sorted(expected) == sorted(kinds)


def _assert_doc(expected, actual_docs):
    expected.pop('doc_id', None)
    assert expected['kind'] in [d['kind'] for d in actual_docs], (
        'Doc %s was not created' % expected
    )
    for actual in actual_docs:
        if actual['kind'] == expected['kind']:
            assert expected == actual


def _assert_doc_by_id(obj_id, event_ref, expected, actual_docs):
    expected.pop('doc_id', None)
    for doc in actual_docs:
        if (
                doc['external_obj_id'] == obj_id
                and doc['external_event_ref'] == event_ref
        ):
            assert expected == doc
            break
    else:
        assert 0, (
            'Doc with external_obj_id="%s", external_event_ref="%s" '
            'was not created' % (obj_id, event_ref)
        )


def _assert_orders(expected, actual_docs):
    for orders in actual_docs:
        for actual in orders['orders']:
            if expected['kind'] == actual['kind']:
                assert expected == actual


def _patch_get_currency_data(patch):
    @patch(
        'taxi_billing_subventions.process_doc._order_ready_for_billing.'
        'contracts.get_currency_data',
    )
    async def _get_currency_data(*args, **kwargs):
        return models.CurrencyData(
            for_contract=models.RatedCurrency(
                currency='RUB', rate_from_local=decimal.Decimal(1),
            ),
            for_offer_contract=models.MaybeRatedCurrency(
                currency='RUB', rate_from_local=decimal.Decimal(1),
            ),
        )


class ContextData:
    def __init__(self, db, session, zones_cache, doc, existing_docs=None):
        self.config = config.Config()
        self.db = db
        self.docs_client = DocsClient(
            ready_doc=doc,
            existing_docs=(existing_docs or []) + [doc],
            incomplete_docs_by_tag=[],
        )
        self.parks_replica_client = ParksReplicaClient(None)
        self.billing_replication_client = BillingReplicationClient(None)
        self.geo_booking_rules_cache = GeoBookingRulesCache([])
        self.accounts_client = AccountsClient(
            balances=[], journal_entries={}, existing_accounts=[],
        )
        self.reports_client = ReportsClient(
            self.docs_client, self.accounts_client,
        )
        self.zones_cache = zones_cache
        tvm_client = tvm.TVMClient(
            service_name='test_taxi_billing_subventions',
            secdist={},
            config=mock.Mock(TVM_RULES={}),
            session=session,
        )
        self.bsx_client = clients.BillingSubventionsXApiClient(
            service=discovery.find_service('billing_subventions_x'),
            session=session,
            config=self.config,
            tvm_client=tvm_client,
        )
        self.antifraud_client = antifraud_client.AntifraudClient(
            service=discovery.find_service('antifraud'),
            session=session,
            tvm_client=tvm_client,
        )
        self.antifraud_service = services.antifraud.AntifraudService(
            antifraud_client=self.antifraud_client,
            uantifraud_client=uantifraud_client.UAntiFraudClient(
                session=session,
                cfg=mock.Mock(
                    UANTIFRAUD_CLIENT_QOS={
                        '__default__': {'attempts': 1, 'timeout-ms': 10000},
                    },
                ),
                tvm_client=tvm_client,
            ),
        )
        self.subventions_client = SubventionsClient()
        self.orders_client = OrdersClient()
        self.commissions_client = CommissionsClient()
        self.agglomerations_client = AgglomerationsClient()
        self.stq_agent = StqAgentClientMock()


class GeoBookingRulesCache:
    def __init__(self, rules):
        self.items = rules


@pytest.fixture(name='make_context')
def _make_context(db, session, zones_cache):
    def _maker(doc, existing_docs=None):
        return ContextData(
            db, session, zones_cache, doc, existing_docs=existing_docs or [],
        )

    return _maker


@pytest.fixture(name='uantifraud')
def mock_uantifraud(mockserver):
    @mockserver.json_handler('/uantifraud/v1/subvention/check_order')
    def _wrapper(request):
        return {'status': 'allow'}

    return _wrapper


@pytest.fixture(name='uantifraud_block')
def mock_uantifraud_blocking(mockserver):
    @mockserver.json_handler('/uantifraud/v1/subvention/check_order')
    def _wrapper(request):
        return {'status': 'block'}


@pytest.fixture(name='session')
async def make_session():
    session = aiohttp.client.ClientSession()
    yield session
    await session.close()


@pytest.fixture(name='matcher', autouse=True)
def _matcher(mock_billing_subventions_x):
    return mock_billing_subventions_x('bsx_matches.json')


def _enable_order_ready_for_billing_configs(cfg):
    setattr(cfg, 'BILLING_SUBVENTIONS_ENABLE_SMART_ONTOP', True)
    setattr(cfg, 'BILLING_SUBVENTIONS_PROCESS_SUBVENTION_COMMISSION', True)
    setattr(cfg, 'CONVERT_UNFIT_TO_SUPPORT_INFO', True)
    setattr(cfg, 'BILLING_EYE_SAVE_ORDER_SUBVENTION_SUPPORT_INFO', True)


def _enable_antifraud(cfg):
    setattr(
        cfg,
        'BILLING_SUBVENTIONS_STOP_WRITE_TO_PY2_COLLECTIONS',
        {'__default__': '2020-01-01T00:00:00+00:00'},
    )
    setattr(cfg, 'BILLING_SUBVENTIONS_PROCEDURE_INSTANT_SUBVENTION', True)
    setattr(cfg, 'BILLING_SUBVENTIONS_PAY_OUT_SUBVENTIONS', True)
    setattr(cfg, 'BILLING_SUBVENTIONS_PAY_OUT_SUBVENTIONS_ANTIFRAUD', True)
    setattr(
        cfg,
        'PAYOUT_MIGRATION',
        {
            'subventions': {
                'enabled': {'__default__': [{'first_date': '2020-01-01'}]},
            },
        },
    )
    setattr(
        cfg,
        'SUBVENTION_ANTIFRAUD_PAYOUT_MIGRATION',
        {
            'subventions': {
                'enabled': {'__default__': [{'first_date': '2020-01-01'}]},
            },
        },
    )
    setattr(cfg, 'ALWAYS_CREATE_SUBVENTION_ANTIFRAUD_CHECK', True)
    setattr(cfg, 'BILLING_SUBVENTIONS_NO_ENTRIES_NO_ANTIFRAUD_CHECK', True)


def _enable_antifraud_complete(cfg):
    setattr(cfg, 'BILLING_SUBVENTIONS_PROCESS_ANTIFRAUD_COMPLETE', True)


def _enable_subvention_updates_needed(cfg):
    setattr(cfg, 'BILLING_SUBVENTIONS_ORDER_SUBVENTION_CHANGED_PY3', True)
    setattr(cfg, 'ORDER_COMMISSION_CHANGED_FOR_SUBVENTION_PY3', True)
    setattr(
        cfg,
        'ORDER_SUBVENTION_CHANGED_FROM_PY3_SINCE_DUE',
        '2020-01-01T00:00:00+00:00',
    )
    setattr(
        cfg,
        'ORDER_COMMISSION_CHANGED_FROM_PY3_SINCE_DUE',
        '2020-01-01T00:00:00+00:00',
    )
