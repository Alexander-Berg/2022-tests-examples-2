# pylint: disable=unused-variable,too-many-lines,too-many-arguments
from __future__ import annotations

import copy
import datetime as dt
import decimal
import itertools
import typing as tp
from typing import Any
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional
import uuid

import aiohttp
import pytest
import pytz

from taxi import billing
from taxi import db as taxi_db
from taxi.billing import clients as billing_clients
from taxi.billing.clients import exceptions as client_exceptions
from taxi.billing.clients.billing_commissions import models as client_models
from taxi.billing.clients.models import billing_docs as docs_client_models
from taxi.billing.clients.models import billing_reports as reports_models
from taxi.billing.util import dates as billing_dates
from taxi.clients import driver_work_modes
from taxi.clients import subvention_communications
from taxi.clients import tvm

from taxi_billing_subventions import config
from taxi_billing_subventions import process_doc
from taxi_billing_subventions.common import data_structures
from taxi_billing_subventions.common import intervals
from taxi_billing_subventions.common import models
from taxi_billing_subventions.common import type_aliases as cta
from taxi_billing_subventions.common.db.rule import _mongo
from taxi_billing_subventions.common.models import config as models_config
from taxi_billing_subventions.common.models import driver_modes
from taxi_billing_subventions.process_doc import _shift_ended
from taxi_billing_subventions.process_doc import _subvention_antifraud_check
from taxi_billing_subventions.services import docs as docs_service
from test_taxi_billing_subventions import helpers

_DOC_ID = 12345678

_SAVE_TAGS_IN_SHIFT_ENDED = True
_DONT_SAVE_TAGS_IN_SHIFT_ENDED = False

_SAVE_SUBVENTION_SUPPORT_INFO = True
_DONT_SAVE_SUBVENTION_SUPPORT_INFO = False

_CONVERT_UNFIT_TO_SUPPORT_INFO = True
_SAVE_UNFIT = False


def _build_new_billing_migration(zone_name, first_date_str):
    return {
        kind: _enabled_migration(zone_name, first_date_str)
        for kind in models.Migration.Query.ALLOWED_KINDS
    }


def _enabled_migration(zone_name, first_date_str):
    return {'enabled': {zone_name: [{'first_date': first_date_str}]}}


_ENABLED_BILLING_EVERYWHERE = _build_new_billing_migration(
    '__default__', '0001-01-01',
)

_ENABLED_PAYOUT = _build_new_billing_migration('__default__', '0001-01-01')
_DISABLED_PAYOUT: dict = {}

_ENABLED_BILLING_COMMISSIONS = {'default_for_all': 'full_usage'}

_ENABLED_PAYOUT_CFG: Mapping[str, Any] = {'PAYOUT_MIGRATION': _ENABLED_PAYOUT}

_DISABLED_PAYOUT_CFG: Mapping[str, Any] = {
    'PAYOUT_MIGRATION': _DISABLED_PAYOUT,
}
_ENABLED_BILLING_COMMISSIONS_CFG: Mapping[str, Any] = {
    'BILLING_SUBVENTIONS_USE_BILLING_COMMISSIONS': (
        _ENABLED_BILLING_COMMISSIONS
    ),
}


def _build_common_park_commission_rules():
    return {
        'rules': [
            {
                'work_rule_id': 'e26a3cf21acfe01198d50030487e046b',
                'kind': 'order',
                'amount_rate': '0.1333',
                'amount_fixed': '0.0000',
                'is_platfrom_commission_enabled': True,
                'is_commission_if_platform_commission_is_null_enabled': True,
                'rule_type_id': '4964b852670045b196e526d59915b777',
            },
            {
                'work_rule_id': 'e26a3cf21acfe01198d50030487e046b',
                'kind': 'driver_fix',
                'amount_rate': '0.0000',
            },
            {
                'work_rule_id': 'e26a3cf21acfe01198d50030487e046b',
                'kind': 'subvention',
                'amount_rate': '0.0265',
            },
            {
                'work_rule_id': 'e26a3cf21acfe01198d50030487e046b',
                'kind': 'workshift',
                'amount_rate': '0.0000',
            },
        ],
    }


Balances = tp.Dict[  # pylint: disable=invalid-name
    models.BalanceQuery, tp.List[dict],
]


class StqAgentClientMock:
    def __init__(self, *args, **kwargs):
        self.calls = []

    async def put_task(
            self, queue, eta=None, task_id=None, args=None, kwargs=None,
    ):
        self.calls.append(
            {
                'queue': queue,
                'eta': eta,
                'task_id': task_id,
                'args': args,
                'kwargs': kwargs,
            },
        )

    async def reschedule(self, queue, task_id, eta, log_extra=None):
        pass


class DocsClient:
    def __init__(
            self,
            ready_doc: dict,
            existing_docs: List[dict],
            incomplete_docs_by_tag: bool,
    ) -> None:
        if existing_docs is None:
            existing_docs = []
        self._next_doc_id = 0
        self._ready_doc = ready_doc
        self.created_docs: List[dict] = []
        self.finished_docs: List[dict] = []
        self._create_required_fields = {
            'kind',
            'external_obj_id',
            'external_event_ref',
            'service',
            'data',
            'event_at',
            'journal_entries',
        }
        self._execute_required_fields = {
            'kind',
            'topic',
            'external_ref',
            'service',
            'data',
            'event_at',
            'journal_entries',
        }
        self._incomplete_docs_by_tag = incomplete_docs_by_tag
        self.existing_docs = existing_docs
        self.update_events: List[dict] = []

    async def is_ready_for_processing(
            self, data: dict, log_extra=None,
    ) -> dict:
        return {'ready': True, 'doc': self._ready_doc}

    async def finish_processing(self, data: dict, log_extra=None) -> dict:
        self.finished_docs.append(data)
        return {}

    async def execute_v2(self, data: dict, log_extra=None) -> list:
        docs = data['docs']
        result = []
        for doc in docs:
            actual_keys = set(doc.keys())
            if self._execute_required_fields - actual_keys:
                raise Exception(
                    'Validation error: {keys}'.format(
                        keys=', '.join(
                            self._execute_required_fields - actual_keys,
                        ),
                    ),
                )
            self.created_docs.append(doc)
            doc_copy = copy.deepcopy(doc)
            doc_copy['doc_id'] = self._next_doc_id
            self._next_doc_id += 1
            result.append(doc_copy)
        return result

    async def create(self, data: dict, log_extra=None) -> dict:
        actual_keys = set(data.keys())
        if self._create_required_fields - actual_keys:
            raise Exception(
                'Validation error: {keys}'.format(
                    keys=', '.join(self._create_required_fields - actual_keys),
                ),
            )
        self.created_docs.append(data)
        result = copy.deepcopy(data)
        result['doc_id'] = self._next_doc_id
        if 'process_at' not in data:
            result['process_at'] = billing_dates.format_time(
                dt.datetime.utcnow(),
            )
        self._next_doc_id += 1
        return result

    async def search(self, query: dict, log_extra=None) -> list:
        docs = []
        query.pop('use_master', None)
        for doc in self.existing_docs:
            if all(item in doc.items() for item in query.items()):
                docs.append(doc)
        return docs

    async def journal_search_v2(self, data, log_extra):
        entries = []
        for query in data['docs']:
            doc_id = query['doc_id']
            for doc in self.existing_docs:
                if doc['doc_id'] == doc_id:
                    entries.extend(doc.get('journal_entries', []))
        return {'entries': entries}

    async def all_docs_by_tag(
            self,
            tag: str,
            event_at_begin: dt.datetime,
            event_at_end: dt.datetime,
            max_requests: int,
            limit: tp.Optional[int],
            log_extra=None,
    ) -> tp.List[dict]:
        docs = []
        for doc in self.existing_docs:
            if tag in doc.get('tags', []):
                docs.append(doc)
        if self._incomplete_docs_by_tag:
            raise billing_clients.billing_docs.IncompleteResultError(docs)
        return docs

    async def update_v2(
            self,
            data: docs_client_models.V2DocsUpdateRequest,
            *,
            timeout: Optional[float] = None,
            attempts: Optional[int] = None,
            log_extra: Optional[dict] = None,
    ) -> docs_client_models.V2DocsUpdateResponse:
        self.update_events.append(data.prepare_for_api())
        return docs_client_models.V2DocsUpdateResponse(
            doc_id=data.doc_id,
            data=data.data,
            entry_ids=data.entry_ids,
            revision=data.revision + 1,
            idempotency_key=data.idempotency_key,
            status=data.status,
        )


class ReportsClient:
    def __init__(self, docs_client, accounts_client):
        self.docs_client = docs_client
        self.accounts_client = accounts_client

    async def select_all_docs(self, query, max_num_iterations, log_extra):
        query.pop('limit')
        query.pop('begin_time')
        query.pop('end_time')
        query.pop('cursor')
        return await self.docs_client.search(query)

    async def get_journal_entries(self, query, log_extra):
        assert 'doc_ref' in query, query
        doc_id = int(query['doc_ref'])
        for doc in self.docs_client.existing_docs:
            if doc['doc_id'] == doc_id:
                return doc['journal_entries']

    async def get_docs_by_id(self, query, log_extra=None):
        assert len(query.doc_ids) == 1
        return await self.docs_client.search(
            {'doc_id': query.doc_ids[0]}, log_extra,
        )

    async def all_docs_by_tag(
            self,
            tag: str,
            event_at_begin: dt.datetime,
            event_at_end: dt.datetime,
            max_requests: int,
            limit: int,
            log_extra: Optional[dict] = None,
    ) -> List[dict]:
        return await self.docs_client.all_docs_by_tag(
            tag, event_at_begin, event_at_end, max_requests, limit, log_extra,
        )

    async def select_journal_till_end(
            self,
            query: reports_models.ReportsJournalSelectRequest,
            log_extra=None,
    ):
        result = []
        for account in query.accounts:
            account_dict = dict(
                entity_external_id=account.entity_external_id,
                agreement_id=account.agreement_id,
                sub_account=account.sub_account,
            )
            entries = await self.accounts_client.get_journal_entries(
                account_dict,
                None,
                query.begin_time,
                query.end_time,
                query.cursor,
                query.limit,
                log_extra=log_extra,
            )
            for entry in entries['entries']:
                journal_entry = reports_models.JournalEntry(
                    entry_id=entry['entry_id'],
                    account=reports_models.ReportsAccount(
                        account_id=entry['account_id'], **entry['account'],
                    ),
                    amount=decimal.Decimal(entry['amount']),
                    doc_ref='',
                    event_at=entry['event_at'],
                    created=entry['created'],
                    reason='',
                    details=entry.get('details'),
                )
                result.append(journal_entry)
        return result


class AccountsClient:
    def __init__(self, balances, journal_entries, existing_accounts):
        self.next_account_id = 0
        self.created_accounts = []
        self.created_entities = []
        self._balances = balances
        self._journal_entries = journal_entries
        self.existing_accounts = existing_accounts

    async def search_entities(self, external_id: str, log_extra=None) -> list:
        return list(
            filter(
                lambda item: item['external_id'] == external_id,
                self.created_entities,
            ),
        )

    def _match_account(
            self,
            item: dict,
            entity_external_id: str,
            agreement_id: Optional[str],
            currency: Optional[str],
            sub_account: Optional[str],
    ) -> bool:
        return (
            (item['entity_external_id'] == entity_external_id)
            and (agreement_id is None or agreement_id == item['agreement_id'])
            and (currency is None or currency == item['currency'])
            and (sub_account is None or sub_account == item['sub_account'])
        )

    async def search_accounts(
            self,
            *,
            entity_external_id: str,
            agreement_id: Optional[str],
            currency: Optional[str],
            sub_account: Optional[str],
            log_extra=None,
    ) -> list:
        return list(
            filter(
                lambda item: self._match_account(
                    item,
                    entity_external_id,
                    agreement_id,
                    currency,
                    sub_account,
                ),
                self.created_accounts,
            ),
        )

    async def create_entity(self, data: dict, log_extra=None) -> dict:
        self.created_entities.append(data)
        return {}

    async def create_account(self, data: dict, log_extra=None) -> dict:
        self.created_accounts.append(data)
        data['account_id'] = self.next_account_id
        self.next_account_id += 1
        return data

    async def get_balances(
            self,
            accounts,
            accrued_at,
            limit,
            offset,
            timeout=None,
            log_extra=None,
    ) -> tp.List[dict]:
        assert len(accounts) == 1
        acc = accounts[0]
        query = models.BalanceQuery(  # type: ignore
            entity_id=acc.get('entity_external_id'),
            agreement_id=acc['agreement_id'],
            sub_account=acc['sub_account'],
            accrued_at=tuple(accrued_at),  # type: ignore
        )
        return self._balances.get(query, [])

    async def get_journal_entries(
            self,
            account,
            doc_ref,
            begin_time,
            end_time,
            cursor,
            limit,
            log_extra=None,
    ) -> dict:
        query = models.BalanceQuery(
            entity_id=account['entity_external_id'],
            agreement_id=account['agreement_id'],
            sub_account=account['sub_account'],
            accrued_at=(begin_time, end_time),
        )
        return {'entries': self._journal_entries.get(query, [])}

    async def search_accounts_v2(
            self, *accounts: dict, log_extra: dict = None,
    ) -> dict:
        result = []
        for query in accounts:
            for an_account in self.existing_accounts:
                if 'account_id' in query:
                    if an_account['account_id'] == query['account_id']:
                        result.append(an_account)
                else:
                    matched = self._match_account(
                        an_account,
                        query['entity_external_id'],
                        query.get('agreement_id'),
                        query.get('currency'),
                        query.get('sub_account'),
                    )
                    if matched:
                        result.append(an_account)
        return {'accounts': result}


class OrdersClient:
    def __init__(self):
        self.created_docs = []

    async def v2_process_event_async(self, request, log_extra):
        self.created_docs.append(request.dump())


class AntifraudClient:
    def __init__(self, af_check_subvention_resp='pay'):
        self._af_check_subvention_resp = af_check_subvention_resp

    async def check_orders(
            self, orders_with_licenses: list, log_extra=None,
    ) -> dict:
        return {
            'orders': [
                {
                    'order_id': order['order_id'],
                    'license_id': order['license'],
                    'frauder': False,
                    'found': True,
                }
                for order in orders_with_licenses
            ],
        }

    async def check_subventions(self, queries, log_extra=None) -> dict:
        response_items = []
        for query in queries:
            billing_id = query['billing_id']
            item = {
                'antifraud_id': billing_id,
                'billing_id': f'antifraud_id/{billing_id}',
                'action': self._af_check_subvention_resp,
            }
            if self._af_check_subvention_resp == 'delay':
                item['till'] = '2018-11-30T19:31:35+00:00'
            response_items.append(item)
        return {'items': response_items}

    async def check_reason(self, reason, log_extra=None):
        return {
            'message': {
                'keyset': 'antifraud',
                'key': 'Subvention.nMFG.DriverFraud.Deal.Message',
            },
        }


class DriversProfilesClient:
    def __init__(self, profiles):
        self.profiles = profiles

    async def retrieve(self, ids, projection, log_extra=None):
        return {'profiles': [self.profiles[id_] for id_ in ids]}


class PersonalApiClient:
    def __init__(self, drivers_licenses):
        self.drivers_licenses = drivers_licenses

    async def retrieve(self, data_type, request_id, log_extra=None):
        return self.drivers_licenses[request_id]


class ParksReplicaClient:
    def __init__(
            self,
            billing_client_ids_mapping: tp.Optional[tp.Dict[str, str]] = None,
    ):
        self._billing_client_ids_mapping = {'__default__': 'billing_client_id'}
        if billing_client_ids_mapping:
            self._billing_client_ids_mapping.update(billing_client_ids_mapping)

    async def fetch_billing_client_id(self, park_id, timestamp, log_extra):
        return self._billing_client_ids_mapping.get(
            park_id, self._billing_client_ids_mapping['__default__'],
        )


class GeoBookingRulesCache:
    def __init__(self, rules):
        self.items = rules


class ZonesCache:
    def __init__(self, zones):
        self._zones_by_name = {zone.name: zone for zone in zones}
        self._tzinfo_by_zone = {zone.name: zone.tzinfo for zone in zones}

    def get_zone(self, name: str) -> models.Zone:
        return self._zones_by_name[name]

    @property
    def zones_by_name(self):
        return self._zones_by_name

    @property
    def tzinfo_by_zone(self):
        return self._tzinfo_by_zone


class SubventionsClient:
    def __init__(self):
        self.requests = {}

    async def process_doc(
            self,
            doc_id: int,
            doc_kind: Optional[str] = None,
            process_at: Optional[dt.datetime] = None,
            log_extra=None,
    ) -> dict:
        self.requests[doc_id] = process_at
        return {}


class AgglomerationsClient:
    def __init__(self, desired_response=None):
        self.desired_response = desired_response

    async def maybe_get_mvp_oebs_id(self, **kwargs) -> Optional[str]:
        return self.desired_response


class ProcessingClient:
    def __init__(self):
        self.sent_data = []

    async def v1_scope_queue_create_event(self, data, *args, **kwargs):
        return self.sent_data.append(data)


class CommissionsClient:
    def __init__(self):
        self._raise_exception = False
        self._responses: (
            tp.List[
                tp.Tuple[
                    client_models.billing_commissions.CommissionsMatchResponse,
                    tp.Optional[str],
                ]
            ]
        ) = []

    def add_response(
            self,
            response: (
                client_models.billing_commissions.CommissionsMatchResponse
            ),
            expected_status: tp.Optional[str] = None,
    ):
        self._responses.append((response, expected_status))

    def set_exception(self):
        self._raise_exception = True

    async def match(
            self,
            data: client_models.billing_commissions.CommissionsMatchRequest,
            log_extra=None,
    ) -> client_models.billing_commissions.CommissionsMatchResponse:
        if self._raise_exception:
            raise client_exceptions.RequestRetriesExceeded(
                '{} API request failed after {} retries'.format(
                    'billing-commissions', 1,
                ),
            )
        assert self._responses
        response = self._responses.pop(0)
        if response[1]:
            assert data.billing_type == response[1]
        return response[0]


class BillingReplicationClient:
    def __init__(self, active_contracts=None):
        self._active_contracts = active_contracts or []

    async def get_active_contracts(
            self,
            billing_client_id: str,
            active_ts: str,
            actual_ts: str,
            service_ids: List[int],
            service_ids_prev_active: List[int],
            timeout: int,
    ) -> List[dict]:
        return self._active_contracts


class DriverWorkModesClient:
    def __init__(self, park_commission_rules=None, resp_status=200):
        self._park_commission_rules = park_commission_rules or []
        self._resp_status = resp_status or 200

    async def v1_park_commission_rules_match(
            self,
            park_id: str,
            driver_profile_id: str,
            matching_at_as_str: str,
            payment_type: tp.Optional[str],
            order_status: tp.Optional[str],
            **opts,
    ) -> dict:
        if self._resp_status != 200:
            raise driver_work_modes.ResponseError(
                status=self._resp_status, body='',
            )
        return self._park_commission_rules


@pytest.fixture(name='session')
async def make_session():
    session = aiohttp.client.ClientSession()
    yield session
    await session.close()


class ContextData:
    # pylint: disable=too-many-instance-attributes
    def __init__(
            self,
            doc: dict,
            rules: list,
            zones: list,
            db: Optional[taxi_db.Database],
            balances: Balances,
            journal_entries=None,
            drivers_profiles=None,
            drivers_licenses=None,
            existing_docs=None,
            existing_accounts=None,
            new_billing_migration=None,
            payout_migration=None,
            payout_migration_af=None,
            stop_write_to_py2_collections=None,
            tlog_park_ids=None,
            minimize_reversals=False,
            use_noop_antifraud=True,
            min_msk_time='',
            always_create_subventions_antifraud_check=False,
            no_entries_no_antifraud_check=False,
            park_account_history_usage='disable',
            replication_contracts_usage='disable',
            replication_contracts=None,
            save_tags_in_shift_ended=False,
            convert_unfit_to_support_info=False,
            fix_minimal_reversals_since=None,
            relax_rebill_checks=False,
            geobooking_migration_date=None,
            write_only_useful_journal_entries=None,
            save_commission_support_info=None,
            save_subvention_support_info=False,
            save_nmfg_tag=False,
            save_nmfg_support_info=False,
            pay_out_subventions=False,
            pay_out_subventions_af=False,
            af_check_subvention_resp='pay',
            billing_client_ids_mapping=None,
            old_journal_limit_days=None,
            desired_agglomeration=None,
            incomplete_related_docs=False,
            billing_commissions_usage=None,
            park_commission_rules=None,
            park_commission_rules_status=None,
            session=None,
    ) -> None:
        # pylint: disable=too-many-arguments
        self.config = config.Config()
        # setattr to prevent failure in "invalid-name" check
        setattr(
            self.config, 'BILLING_PROCESS_DRIVER_GEOAREA_ACTIVITY_DOC', True,
        )
        setattr(
            self.config,
            'BILLING_SUBVENTIONS_PROCESS_SINGLE_ORDER_RULES',
            True,
        )
        setattr(self.config, 'BILLING_SUBVENTIONS_SHIFT_ENDED_WINDOW', 0)
        setattr(
            self.config, 'BILLING_SUBVENTIONS_PROCESS_SHIFT_ENDED_DOC', True,
        )
        setattr(self.config, 'BILLING_SUBVENTIONS_PROCESS_REFERRAL', True)
        setattr(self.config, 'BILLING_NOTIFY_ON_FULFILLED_SUBVENTIONS', True)
        setattr(
            self.config, 'BILLING_NOTIFY_ON_DONE_PERSONAL_SUBVENTIONS', True,
        )
        setattr(
            self.config,
            'BILLING_SUBVENTIONS_PROCESS_SUBVENTION_ANTIFRAUD_ENTRIES',
            True,
        )
        setattr(
            self.config,
            'BILLING_SUBVENTIONS_CREATE_SUBVENTION_ANTIFRAUD_ENTRIES_DOCS',
            '2000-01-01T00:00:00+00:00',
        )
        setattr(
            self.config,
            'BILLING_SUBVENTIONS_FETCH_ALIAS_ID_FROM_DETAILS',
            True,
        )
        self.config.BILLING_SUBVENTIONS_ANTIFRAUD_PREFIX = 'test_new_billing_'
        self.config.BILLING_SUBVENTIONS_PROCESS_NOTIFY = True
        if new_billing_migration is not None:
            self.config.NEW_BILLING_MIGRATION = new_billing_migration
        if billing_commissions_usage is not None:
            self.config.BILLING_SUBVENTIONS_USE_BILLING_COMMISSIONS = (
                billing_commissions_usage
            )
        if payout_migration is not None:
            self.config.PAYOUT_MIGRATION = payout_migration
        if payout_migration_af is not None:
            self.config.SUBVENTION_ANTIFRAUD_PAYOUT_MIGRATION = (
                payout_migration_af
            )
        if stop_write_to_py2_collections is not None:
            self.config.BILLING_SUBVENTIONS_STOP_WRITE_TO_PY2_COLLECTIONS = (
                stop_write_to_py2_collections
            )
        if tlog_park_ids is not None:
            self.config.BILLING_USE_TLOG_FOR_DONATIONS = {
                'park_id_regex': '|'.join(map(str, tlog_park_ids)),
            }
        self.config.BILLING_SUBVENTIONS_GEO_BOOKING_MIGRATION_DATE = (
            geobooking_migration_date
        )
        self.config.BILLING_SUBVENTIONS_MINIMIZE_REVERSALS = minimize_reversals
        self.config.BILLING_SUBVENTIONS_USE_NOOP_ANTIFRAUD = use_noop_antifraud
        self.config.BILLING_SUBVENTIONS_PROCESS_AF_ACTION = True
        self.config.BILLING_SUBVENTIONS_PROCESS_AF_DECISION = True
        self.config.BILLING_SUBVENTIONS_PROCESS_REBILL_ORDER = True
        self.config.SEND_REASON_IN_ORDER_COMPLETED_AMENDED = True
        self.config.BILLING_SUBVENTIONS_FETCH_ALIAS_ID_FROM_DETAILS = True
        self.config.PROCESS_SHIFT_ENDED_MIN_MSK_TIME = min_msk_time
        self.config.ALWAYS_CREATE_SUBVENTION_ANTIFRAUD_CHECK = (
            always_create_subventions_antifraud_check
        )
        self.config.BILLING_SUBVENTIONS_NO_ENTRIES_NO_ANTIFRAUD_CHECK = (
            no_entries_no_antifraud_check
        )
        self.config.CONVERT_UNFIT_TO_SUPPORT_INFO = (
            convert_unfit_to_support_info
        )
        self.config.PARK_ACCOUNT_HISTORY_USAGE = park_account_history_usage
        self.config.REPLICATION_CONTRACTS_USAGE = replication_contracts_usage
        self.config.SAVE_TAGS_IN_SHIFT_ENDED = save_tags_in_shift_ended
        self.config.BILLING_EYE_SAVE_ALIAS_ID_TAG = True
        self.config.BILLING_EYE_SAVE_PARENT_DOC_ID_TAG = True
        self.config.BILLING_EYE_SAVE_NMFG_TAG = True
        self.config.BILLING_RELAX_REBILL_CHECKS = relax_rebill_checks
        if write_only_useful_journal_entries is not None:
            self.config.BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES = (
                write_only_useful_journal_entries
            )
        if save_commission_support_info is not None:
            self.config.BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO = (
                save_commission_support_info
            )
        self.config.BILLING_EYE_SAVE_ORDER_SUBVENTION_SUPPORT_INFO = (
            save_subvention_support_info
        )
        if fix_minimal_reversals_since is not None:
            self.config.BILLING_FIX_MINIMAL_REVERSALS_SINCE = (
                fix_minimal_reversals_since
            )
        self.config.BILLING_EYE_SAVE_NMFG_TAG = save_nmfg_tag
        self.config.BILLING_EYE_SAVE_DOXGETY_TAG = True
        self.config.BILLING_EYE_SAVE_NMFG_SUPPORT_INFO = save_nmfg_support_info
        self.config.BILLING_EYE_SAVE_DOXGETY_SUPPORT_INFO = True
        self.config.BILLING_EYE_SAVE_GEOBOOKING_SUPPORT_INFO = True
        self.config.BILLING_SUBVENTIONS_SEND_DRIVER_FIX_NOTIFICATION = True
        self.config.BILLING_SUBVENTIONS_SEND_GEO_BOOKING_NOTIFICATION = True
        self.config.BILLING_SUBVENTIONS_SEND_NMFG_NOTIFICATION = True
        self.config.BILLING_SUBVENTIONS_PAY_OUT_SUBVENTIONS = (
            pay_out_subventions
        )
        self.config.BILLING_SUBVENTIONS_PAY_OUT_SUBVENTIONS_ANTIFRAUD = (
            pay_out_subventions_af
        )
        self.config.BILLING_PASS_SUBVENTIONS_BRO_ORDERS_IDS_TO_TLOG = {
            '__default__': False,
            'driver_fix': True,
            'do_x_get_y': True,
            'booking_geo_on_top': True,
            'booking_geo_guarantee': True,
            'nmfg': True,
        }
        self.db = db
        self.geo_booking_rules_cache = GeoBookingRulesCache(rules)
        self.zones_cache = ZonesCache(zones)
        self.tvm_client = tvm.TVMClient(
            service_name='test_taxi_billing_subventions',
            secdist={},
            config=self.config,
            session=session,
        )
        self.stq_agent = StqAgentClientMock()
        self.accounts_client = AccountsClient(
            balances=balances,
            journal_entries=journal_entries or {},
            existing_accounts=existing_accounts or [],
        )
        self.docs_client = DocsClient(
            ready_doc=doc,
            existing_docs=existing_docs,
            incomplete_docs_by_tag=incomplete_related_docs,
        )
        self.docs_service = docs_service.DocsService(
            docs_client=self.docs_client,  # type: ignore
        )
        self.reports_client = ReportsClient(
            self.docs_client, self.accounts_client,
        )
        self.antifraud_client = AntifraudClient(af_check_subvention_resp)
        self.subventions_client = SubventionsClient()
        self.drivers_profiles_client = DriversProfilesClient(drivers_profiles)
        self.personal_client = PersonalApiClient(drivers_licenses)
        self.parks_replica_client = ParksReplicaClient(
            billing_client_ids_mapping,
        )
        self.orders_client = OrdersClient()
        self.agglomerations_client = AgglomerationsClient(
            desired_agglomeration,
        )
        self.processing_client = ProcessingClient()
        self.loop = None
        self.commissions_client = CommissionsClient()
        if old_journal_limit_days is not None:
            self.config.BILLING_OLD_JOURNAL_LIMIT_DAYS = old_journal_limit_days
        self.billing_replication_client = BillingReplicationClient(
            replication_contracts,
        )
        self.config.SUBVENTION_COMMUNICATIONS_CLIENT_QOS = {
            '__default__': {'attempts': 1, 'timeout-ms': 200},
        }
        self.subvention_comms_client = subvention_communications.Client(
            session=session, config=self.config, tvm_client=self.tvm_client,
        )
        self.driver_work_modes_client = DriverWorkModesClient(
            park_commission_rules, park_commission_rules_status,
        )


@pytest.mark.parametrize(
    'request_json, expected_task_data',
    [
        ({'doc': {'id': 123}}, ('doc_id/123', None)),
        (
            {
                'doc': {'id': 345},
                'process_at': '2019-02-14T10:59:00.000000+00:00',
            },
            ('doc_id/345', dt.datetime(2019, 2, 14, 10, 59, tzinfo=pytz.utc)),
        ),
    ],
)
# pylint: disable=invalid-name
async def test_process_doc_creates_stq_task(
        billing_subventions_client,
        patch,
        request_json,
        request_headers,
        expected_task_data,
):
    stq = []

    @patch('taxi.clients.stq_agent.StqAgentClient.put_task')
    async def put(  # pylint: disable=unused-variable
            queue, eta=None, task_id=None, args=None, kwargs=None,
    ):
        stq.append((task_id, eta))

    response = await billing_subventions_client.post(
        '/v1/process_doc', headers=request_headers, json=request_json,
    )
    assert response.status == 200
    assert stq == [expected_task_data]


@pytest.mark.now('2018-11-30T19:31:35')
@pytest.mark.parametrize(
    'doc_json, rules_json, convert_unfit_to_support_info, '
    'save_tags_in_shift_ended, '
    'expected_docs_json, expected_accounts_json, expected_entities_json',
    [
        (
            'driver_geoarea_activity_doc.json',
            'geo_booking_rules.json',
            _SAVE_UNFIT,
            _DONT_SAVE_TAGS_IN_SHIFT_ENDED,
            'expected_docs.json',
            'expected_accounts.json',
            'expected_entities.json',
        ),
        (
            'driver_geoarea_activity_doc.json',
            'geo_booking_rules.json',
            _SAVE_UNFIT,
            _SAVE_TAGS_IN_SHIFT_ENDED,
            'expected_docs_with_tags.json',
            'expected_accounts.json',
            'expected_entities.json',
        ),
        (
            'driver_geoarea_activity_doc_arbitrary_interval.json',
            'geo_booking_rules.json',
            _SAVE_UNFIT,
            _DONT_SAVE_TAGS_IN_SHIFT_ENDED,
            'expected_docs_arbitrary_interval.json',
            'expected_accounts.json',
            'expected_entities.json',
        ),
        (
            'driver_geoarea_activity_doc_yesterday.json',
            'geo_booking_rules_yesterday.json',
            _SAVE_UNFIT,
            _DONT_SAVE_TAGS_IN_SHIFT_ENDED,
            'expected_docs_yesterday.json',
            'expected_accounts.json',
            'expected_entities.json',
        ),
        (
            'driver_geoarea_activity_doc.json',
            'vip_geo_booking_rules.json',
            _CONVERT_UNFIT_TO_SUPPORT_INFO,
            _DONT_SAVE_TAGS_IN_SHIFT_ENDED,
            'expected_docs_convert_unfit.json',
            'empty_accounts.json',
            'empty_entities.json',
        ),
    ],
)
# pylint: disable=invalid-name
async def test_stq_task_create_doc_with_journal_entries(
        stq_client_patched,
        doc_json,
        rules_json,
        convert_unfit_to_support_info,
        save_tags_in_shift_ended,
        expected_docs_json,
        expected_accounts_json,
        expected_entities_json,
        patch,
        load_json,
        load_py_json_dir,
        db,
):
    _patch_random(patch)
    doc = load_json(doc_json)
    expected_docs = load_json(expected_docs_json)
    expected_accounts = load_json(expected_accounts_json)
    expected_entities = load_json(expected_entities_json)
    rules = load_py_json_dir(
        'test_stq_task_create_doc_with_journal_entries', rules_json,
    )
    context = ContextData(
        doc=doc,
        rules=rules,
        zones=_build_zones(),
        db=db,
        balances={},
        min_msk_time='17:00',
        convert_unfit_to_support_info=convert_unfit_to_support_info,
        save_tags_in_shift_ended=save_tags_in_shift_ended,
    )
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=0,
    )
    _assert_docs_equal(
        expected_docs=expected_docs,
        actual_docs=context.docs_client.created_docs,
    )
    assert expected_accounts == context.accounts_client.created_accounts
    assert expected_entities == context.accounts_client.created_entities


@pytest.mark.now('2018-11-30T19:31:35')
@pytest.mark.parametrize(
    'doc_json,'
    'replication_contracts_usage, '
    'replication_contracts_json, expected_docs_json',
    [
        (
            'subvention_input_doc.json',
            'disable',
            'replication_contracts.json',
            'expected_docs.json',
        ),
        (
            'subvention_input_doc.json',
            'disable',
            'replication_contracts.json',
            'expected_docs.json',
        ),
        (
            'subvention_input_doc.json',
            'enable',
            'replication_contracts.json',
            'expected_enable_docs.json',
        ),
        (
            'subvention_input_doc.json',
            'enable',
            'replication_contracts.json',
            'expected_replication_enable_docs.json',
        ),
        (
            'subvention_input_with_currency_data_doc.json',
            'disable',
            'replication_contracts.json',
            'expected_docs.json',
        ),
        (
            'subvention_input_with_none_for_contract_doc.json',
            'disable',
            'replication_contracts.json',
            'expected_docs_with_none_for_contract.json',
        ),
        # Park without offer currency & also city has no donate_multiplier
        (
            'subvention_input_doc_without_offer_currency.json',
            'disable',
            'replication_contracts.json',
            'expected_docs_without_offer_currency.json',
        ),
        # Input with goal subvention comment
        (
            'subvention_input_doc_with_goal_comment.json',
            'disable',
            'replication_contracts.json',
            'expected_docs_with_goal_comment.json',
        ),
        (
            'subvention_input_doc.json',
            'enable',
            'replication_contracts.json',
            'expected_enable_docs.json',
        ),
    ],
)
@pytest.mark.filldb(
    parks='test_stq_task_enrich_subventions_input',
    cities='test_stq_task_enrich_subventions_input',
    currency_rates='test_stq_task_enrich_subventions_input',
)
# pylint: disable=invalid-name,too-many-arguments
async def test_stq_task_enrich_subventions_input(
        patch,
        monkeypatch,
        load_json,
        db,
        load_py_json_dir,
        doc_json,
        replication_contracts_usage,
        replication_contracts_json,
        expected_docs_json,
):
    _turn_on_enrich_subventions_input(monkeypatch)
    doc = load_json(doc_json)
    expected_docs = load_json(expected_docs_json)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        db=db,
        balances={},
        replication_contracts_usage=replication_contracts_usage,
        replication_contracts=load_json(replication_contracts_json),
    )
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
    )
    created_docs = context.docs_client.created_docs
    assert _sorted_docs(expected_docs) == _sorted_docs(created_docs)


@pytest.mark.now('2019-04-01T10:16:13')
@pytest.mark.parametrize(
    'doc_json,prev_docs_json,expected_docs_json',
    [
        (
            'subvention_update_needed_doc.json',
            'no_history.json',
            'expected_docs_no_history.json',
        ),
        (
            'subvention_update_needed_doc.json',
            'with_history.json',
            'expected_docs_with_history.json',
        ),
        (
            'exclude_rules_from_subventions.json',
            'exclude_history.json',
            'expected_docs_after_exclude.json',
        ),
    ],
)
# pylint: disable=invalid-name,too-many-arguments
async def test_create_order_subvention_changed(
        monkeypatch,
        load_json,
        stq_client_patched,
        doc_json,
        prev_docs_json,
        expected_docs_json,
):
    doc = load_json(doc_json)
    existing_docs = load_json(prev_docs_json)
    existing_docs.append(doc)
    expected_docs = load_json(expected_docs_json)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        db=None,
        balances={},
        existing_docs=existing_docs,
    )
    _turn_on_create_order_subvention_changed(monkeypatch)
    _turn_on_create_order_commission_changed_for_subvention(monkeypatch)
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
    )
    expected_kinds = (
        'order_subvention_changed',
        'subvention_value_calculated',
        'order_commission_changed',
        'subvention_commission_value_calculated',
    )
    created_docs = [
        doc
        for doc in context.docs_client.created_docs
        if doc['kind'] in expected_kinds
    ]
    assert expected_docs == created_docs


def _get_stq_calls_with_task_ids(stq_client_calls):
    return [(call['queue'], call['task_id']) for call in stq_client_calls]


def _get_stq_calls(stq_client_calls):
    return [_without_kwargs_log_extra(call) for call in stq_client_calls]


def _without_kwargs_log_extra(call):
    result = copy.deepcopy(call)
    result.get('kwargs', {}).pop('log_extra', None)
    return result


def _assert_subventions_are_equal(expected_subventions, subventions):
    IRRELEVANT_KEYS = ('_id', 'c', 'u')  # pylint: disable=invalid-name

    def _delete_irrelevant_keys(doc):
        for key in IRRELEVANT_KEYS:
            if key in doc:
                del doc[key]

    expected = sorted(expected_subventions, key=lambda s: s['v'])
    actual = sorted(subventions, key=lambda s: s['v'])
    for doc in expected:
        _delete_irrelevant_keys(doc)
    for doc in actual:
        _delete_irrelevant_keys(doc)
    assert expected == actual


@pytest.mark.filldb(
    commission_contracts=(
        'for_test_process_ready_for_billing_' 'without_antifraud'
    ),
    parks='for_test_process_ready_for_billing_without_antifraud',
    cities='for_test_process_doc',
)
@pytest.mark.now('2018-11-30T19:31:35')
@pytest.mark.parametrize(
    'doc_json, default_rules_json, personal_rules_json, '
    'expected_docs_json, expected_accounts_json, expected_entities_json',
    [
        (
            'ready_for_billing_doc.json',
            'default_rules.json',
            'personal_rules.json',
            'expected_docs.json',
            'expected_accounts.json',
            'expected_entities.json',
        ),
    ],
)
async def test_process_ready_for_billing_without_antifraud(
        doc_json,
        default_rules_json,
        personal_rules_json,
        expected_docs_json,
        expected_accounts_json,
        expected_entities_json,
        db,
        load_json,
        load_py_json_dir,
        monkeypatch,
        patch,
):
    # pylint: disable=invalid-name,too-many-arguments
    _turn_on_commissions(monkeypatch)
    await _patch_database_calls(
        json_path='test_process_ready_for_billing_without_antifraud',
        patch=patch,
        load_py_json_dir=load_py_json_dir,
        default_rules_json=default_rules_json,
        personal_rules_json=personal_rules_json,
    )
    doc = load_json(doc_json)
    expected_docs = load_json(expected_docs_json)
    expected_accounts = load_json(expected_accounts_json)
    expected_entities = load_json(expected_entities_json)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        db=db,
        existing_docs=[doc],
        balances={},
    )
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
    )
    _assert_docs_equal(
        expected_docs=expected_docs,
        actual_docs=context.docs_client.created_docs,
    )
    assert context.accounts_client.created_accounts == expected_accounts
    assert context.accounts_client.created_entities == expected_entities


async def _patch_get_balances(
        json_path, patch, load_py_json_dir, balances_json,
):
    @patch('taxi_billing_subventions.common.accounts.get_balances')
    async def get_balances(
            accounts_client: billing_clients.BillingAccountsClient,
            balance_queries: tp.List[models.BalanceQuery],
            limit: int,
            timeout: tp.Optional[int],
            log_extra: cta.LogExtra,
    ) -> tp.List[dict]:
        return load_py_json_dir(json_path, balances_json)


async def _patch_database_calls(
        json_path,
        patch,
        load_py_json_dir,
        default_rules_json,
        personal_rules_json,
):
    @patch(
        'taxi_billing_subventions.common.db.rule.fetch_rule_by_agreement_ref',
    )
    async def fetch_rule_by_agreement_ref(
            database: taxi_db.Database,
            agreement_ref: models.AgreementRef,
            tzinfo_by_zone: cta.TZInfoByZone,
            log_extra: cta.LogExtra,
    ) -> models.Rule:
        if agreement_ref.scope == models.AgreementRef.DEFAULT_SCOPE:
            priority = models.Rule.DEFAULT_PRIORITY
        elif agreement_ref.scope == models.AgreementRef.PERSONAL_SCOPE:
            priority = models.Rule.PERSONAL_PRIORITY
        docs = load_py_json_dir(json_path, default_rules_json)
        # pylint: disable=protected-access
        rules = _mongo._convert_docs_to_rules(
            due_interval=intervals.unbounded(),
            tzinfo_by_zone=tzinfo_by_zone,
            docs=docs,
            priority=priority,
            log_extra=log_extra,
        )
        for rule in rules:
            if rule.agreement_ref == agreement_ref:
                return rule
        raise ValueError('Agreement ref matches nothing')

    @patch(
        'taxi_billing_subventions.common.db.rule._mongo.fetch_default_rules',
    )
    async def fetch_default_rules(
            database: taxi_db.Database,
            zone_name: str,
            due_interval: intervals.Interval[dt.datetime],
            tzinfo: cta.TZInfo,
            active_week_days: tp.Optional[tp.Iterable[int]],
            log_extra: cta.LogExtra,
    ) -> tp.List[models.Rule]:
        docs = load_py_json_dir(json_path, default_rules_json)
        # pylint: disable=protected-access
        return _mongo._convert_docs_to_rules(
            due_interval=due_interval,
            tzinfo_by_zone={zone_name: tzinfo},
            docs=docs,
            # pylint: disable=protected-access
            priority=models.Rule.DEFAULT_PRIORITY,
            log_extra=log_extra,
        )

    @patch(
        'taxi_billing_subventions.common.db.rule.'
        '_mongo.fetch_personal_rules_by_order',
    )
    async def fetch_personal_rules_by_order(
            database: taxi_db.Database,
            order: models.doc.Order,
            log_extra: cta.LogExtra,
    ) -> tp.List[models.Rule]:
        rules = load_py_json_dir(json_path, personal_rules_json)
        # pylint: disable=protected-access
        return _mongo._convert_docs_to_rules(
            # pylint: disable=protected-access
            due_interval=_mongo._get_rule_related_interval(order),
            tzinfo_by_zone={order.zone_name: order.tzinfo},
            docs=rules,
            # pylint: disable=protected-access
            priority=models.Rule.PERSONAL_PRIORITY,
            log_extra=log_extra,
        )


async def _get_subventions(collection, alias_id):
    cursor = collection.find({'a': alias_id})
    return await cursor.to_list(None)


@pytest.mark.now('2018-11-30T19:31:35')
@pytest.mark.filldb(
    cities='for_test_process_ready_for_billing_doc_with_antifraud',
    commission_contracts=(
        'for_test_process_ready_for_billing_doc_with_antifraud'
    ),
    currency_rates='for_test_process_ready_for_billing_doc_with_antifraud',
    parks='for_test_process_ready_for_billing_doc_with_antifraud',
)
@pytest.mark.parametrize(
    'doc_json, '
    'default_rules_json, '
    'personal_rules_json, '
    'replication_contracts_usage, '
    'replication_contracts_json, '
    'save_tags_in_shift_ended, '
    'save_subvention_support_info, '
    'enable_commissions, '
    'expected_docs_json, '
    'expected_accounts_json, '
    'expected_entities_json, '
    'use_noop_antifraud, '
    'write_only_useful_journal_entries, '
    'no_entries_no_antifraud_check, '
    'subvention_antifraud_payout_migration, '
    'existing_docs_json, ',
    [
        (
            'ready_for_billing_doc.json',
            'default_rules.json',
            'personal_rules.json',
            'disable',
            'replication_contracts.json',
            _DONT_SAVE_TAGS_IN_SHIFT_ENDED,
            _DONT_SAVE_SUBVENTION_SUPPORT_INFO,
            False,
            'expected_docs.json',
            'expected_accounts.json',
            'expected_entities.json',
            True,
            True,
            False,
            _DISABLED_PAYOUT,
            'existing_docs_for_ready_for_billing_doc.json',
        ),
        (
            'ready_for_billing_doc.json',
            'default_rules.json',
            'personal_rules.json',
            'reconcile',
            'replication_contracts.json',
            _DONT_SAVE_TAGS_IN_SHIFT_ENDED,
            _DONT_SAVE_SUBVENTION_SUPPORT_INFO,
            False,
            'expected_docs.json',
            'expected_accounts.json',
            'expected_entities.json',
            True,
            True,
            False,
            _DISABLED_PAYOUT,
            'existing_docs_for_ready_for_billing_doc.json',
        ),
        (
            'ready_for_billing_doc.json',
            'default_rules.json',
            'personal_rules_with_commission.json',
            'enable',
            'replication_contracts.json',
            _DONT_SAVE_TAGS_IN_SHIFT_ENDED,
            _SAVE_SUBVENTION_SUPPORT_INFO,
            True,
            'expected_enable_docs.json',
            'expected_enable_accounts.json',
            'expected_entities.json',
            True,
            True,
            False,
            _DISABLED_PAYOUT,
            'existing_docs_for_ready_for_billing_doc.json',
        ),
        (
            'ready_for_billing_doc.json',
            'empty_rules.json',
            'zero_personal_rules.json',
            'disable',
            'replication_contracts.json',
            _DONT_SAVE_TAGS_IN_SHIFT_ENDED,
            _DONT_SAVE_SUBVENTION_SUPPORT_INFO,
            False,
            'expected_zero_personal_rules_docs.json',
            'expected_zero_personal_rules_accounts.json',
            'expected_zero_personal_rules_entities.json',
            True,
            False,
            False,
            _DISABLED_PAYOUT,
            'existing_docs_for_ready_for_billing_doc.json',
        ),
        (
            'ready_for_billing_doc.json',
            'empty_rules.json',
            'zero_personal_rules.json',
            'disable',
            'replication_contracts.json',
            _DONT_SAVE_TAGS_IN_SHIFT_ENDED,
            _DONT_SAVE_SUBVENTION_SUPPORT_INFO,
            False,
            'expected_zero_personal_rules_no_noop_docs.json',
            'expected_zero_personal_rules_no_noop_accounts.json',
            'expected_zero_personal_rules_no_noop_entities.json',
            False,
            False,
            False,
            _DISABLED_PAYOUT,
            'existing_docs_for_ready_for_billing_doc.json',
        ),
        (
            'ready_for_billing_doc.json',
            'default_rules.json',
            'personal_rules.json',
            'disable',
            'replication_contracts.json',
            _SAVE_TAGS_IN_SHIFT_ENDED,
            _DONT_SAVE_SUBVENTION_SUPPORT_INFO,
            False,
            'expected_docs_with_subventions_context.json',
            'expected_accounts.json',
            'expected_entities.json',
            True,
            True,
            False,
            _ENABLED_PAYOUT,
            'existing_docs_for_ready_for_billing_doc.json',
        ),
        (
            'old_ready_for_billing_doc.json',
            'default_rules.json',
            'personal_rules.json',
            'disable',
            'replication_contracts.json',
            _DONT_SAVE_TAGS_IN_SHIFT_ENDED,
            _DONT_SAVE_SUBVENTION_SUPPORT_INFO,
            False,
            'old_expected_docs_with_subventions_context.json',
            'expected_accounts.json',
            'expected_entities.json',
            True,
            True,
            False,
            _DISABLED_PAYOUT,
            'existing_docs_for_old_ready_for_billing_doc.json',
        ),
        (
            'ready_for_billing_doc.json',
            'empty_rules.json',
            'empty_rules.json',
            'disable',
            'replication_contracts.json',
            _DONT_SAVE_TAGS_IN_SHIFT_ENDED,
            _SAVE_SUBVENTION_SUPPORT_INFO,
            False,
            'expected_no_antifraud_docs.json',
            'expected_no_accounts.json',
            'expected_discount_entities.json',
            True,
            True,
            True,
            _DISABLED_PAYOUT,
            'existing_docs_for_ready_for_billing_doc.json',
        ),
    ],
)
async def test_process_ready_for_billing_with_antifraud(
        doc_json,
        default_rules_json,
        personal_rules_json,
        replication_contracts_usage,
        replication_contracts_json,
        save_tags_in_shift_ended,
        save_subvention_support_info,
        enable_commissions,
        expected_docs_json,
        expected_accounts_json,
        expected_entities_json,
        use_noop_antifraud,
        write_only_useful_journal_entries,
        no_entries_no_antifraud_check,
        subvention_antifraud_payout_migration,
        existing_docs_json,
        db,
        load_json,
        load_py_json,
        stq_client_patched,
        load_py_json_dir,
        monkeypatch,
        patch,
):
    # pylint: disable=invalid-name,too-many-arguments,too-many-locals
    if enable_commissions:
        _turn_on_commissions(monkeypatch)
    _turn_on_antifraud_processing(monkeypatch)
    _fill_tlog_service_ids(monkeypatch)
    _turn_on_send_contract_id_for_subventions(monkeypatch)

    await _patch_database_calls(
        json_path='test_process_ready_for_billing_with_antifraud',
        patch=patch,
        load_py_json_dir=load_py_json_dir,
        default_rules_json=default_rules_json,
        personal_rules_json=personal_rules_json,
    )

    @patch('random.randint')
    def _randint(left, right):
        return (left + right) / 2

    doc = load_json(doc_json)
    expected_docs = load_json(expected_docs_json)
    expected_accounts = load_json(expected_accounts_json)
    expected_entities = load_json(expected_entities_json)
    existing_docs = load_py_json(existing_docs_json)
    existing_docs.append(doc)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        db=db,
        existing_docs=existing_docs,
        balances={},
        use_noop_antifraud=use_noop_antifraud,
        replication_contracts_usage=replication_contracts_usage,
        replication_contracts=load_json(replication_contracts_json),
        save_tags_in_shift_ended=save_tags_in_shift_ended,
        save_subvention_support_info=save_subvention_support_info,
        write_only_useful_journal_entries=write_only_useful_journal_entries,
        always_create_subventions_antifraud_check=True,
        no_entries_no_antifraud_check=no_entries_no_antifraud_check,
        pay_out_subventions_af=True,
        payout_migration_af=subvention_antifraud_payout_migration,
    )
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
    )
    assert context.accounts_client.created_accounts == expected_accounts
    expected_docs = _docs_with_sorted_tags(expected_docs)
    created_docs = _docs_with_sorted_tags(context.docs_client.created_docs)
    _assert_docs_equal(
        expected_docs=_sorted_docs(expected_docs),
        actual_docs=_sorted_docs(created_docs),
    )
    _assert_same_entities(
        expected_entities, context.accounts_client.created_entities,
    )


@pytest.mark.now('2018-11-30T19:31:35')
@pytest.mark.parametrize(
    'doc_json, default_rules_json, personal_rules_json, '
    'payout_migration, '
    'pay_out_subventions, af_check_subvention_resp, configs, '
    'park_commission_rules_status, park_commission_rules, '
    'expected_docs_json, expected_accounts_json, expected_entities_json, '
    'expected_orders_docs_json, expected_stq_calls_json, '
    'expected_doc_updates_json',
    [
        pytest.param(
            'v2_antifraud_check_doc.json',
            'default_rules.json',
            'personal_rules.json',
            _DISABLED_PAYOUT,
            False,
            'pay',
            {},
            None,
            None,
            'v2_expected_docs.json',
            'v2_expected_accounts.json',
            'v2_expected_entities.json',
            'empty_orders_docs.json',
            'empty_stq_calls.json',
            'empty_doc_updates.json',
            id='0',
        ),
        pytest.param(
            'v2_separate_journal_topic_antifraud_check_doc.json',
            'default_rules.json',
            'personal_rules.json',
            _DISABLED_PAYOUT,
            False,
            'pay',
            {},
            None,
            None,
            'v2_separate_journal_topic_expected_docs.json',
            'v2_expected_accounts.json',
            'v2_expected_entities.json',
            'empty_orders_docs.json',
            'empty_stq_calls.json',
            'empty_doc_updates.json',
            id='1',
        ),
        pytest.param(
            'v2_antifraud_check_doc_with_payments.json',
            'default_rules.json',
            'personal_rules.json',
            _DISABLED_PAYOUT,
            False,
            'pay',
            {},
            None,
            None,
            'v2_with_payments_expected_docs.json',
            'v2_with_payments_expected_accounts.json',
            'v2_expected_entities.json',
            'empty_orders_docs.json',
            'expected_driver_fix_pay_stq_calls.json',
            'empty_doc_updates.json',
            id='2',
        ),
        pytest.param(
            'v2_antifraud_check_doc_with_payments.json',
            'default_rules.json',
            'personal_rules.json',
            _DISABLED_PAYOUT,
            False,
            'pay',
            {},
            None,
            None,
            'v2_with_payments_one_payout_expected_docs.json',
            'v2_with_payments_expected_accounts.json',
            'v2_expected_entities.json',
            'empty_orders_docs.json',
            'expected_driver_fix_pay_stq_calls.json',
            'empty_doc_updates.json',
            id='3',
        ),
        pytest.param(
            'v2_antifraud_check_doc_payout_subventions.json',
            'default_rules.json',
            'personal_rules.json',
            _ENABLED_PAYOUT,
            True,
            'pay',
            {},
            None,
            None,
            'v2_pay_expected_docs.json',
            'v2_expected_accounts.json',
            'v2_expected_entities.json',
            'v2_payout_subventions_expected_orders_docs.json',
            'empty_stq_calls.json',
            'empty_doc_updates.json',
            id='4',
        ),
        pytest.param(
            'v2_antifraud_check_doc_payout_subventions.json',
            'default_rules.json',
            'personal_rules.json',
            _DISABLED_PAYOUT,
            True,
            'block',
            {},
            None,
            None,
            'v2_block_expected_docs.json',
            'v2_expected_accounts.json',
            'v2_expected_entities.json',
            'v2_revoke_subventions_expected_orders_docs.json',
            'empty_stq_calls.json',
            'empty_doc_updates.json',
            id='5',
        ),
        pytest.param(
            'v2_antifraud_check_doc_payout_with_coupons.json',
            'default_rules.json',
            'personal_rules.json',
            _DISABLED_PAYOUT,
            False,
            'block',
            {},
            None,
            None,
            'v2_with_coupons_expected_docs.json',
            'v2_with_coupons_expected_accounts.json',
            'v2_expected_entities.json',
            'empty_orders_docs.json',
            'expected_driver_fix_block_stq_calls.json',
            'empty_doc_updates.json',
            id='6',
        ),
        pytest.param(
            'v2_antifraud_check_doc_payout_subventions.json',
            'default_rules.json',
            'personal_rules.json',
            _DISABLED_PAYOUT,
            True,
            'delay',
            {},
            None,
            None,
            'v2_delay_expected_docs.json',
            'v2_expected_accounts.json',
            'v2_expected_entities.json',
            'v2_delay_subventions_expected_orders_docs.json',
            'empty_stq_calls.json',
            'empty_doc_updates.json',
            id='7',
        ),
        pytest.param(
            'v2_antifraud_check_doc_payout_subventions_with_hold.json',
            'default_rules.json',
            'personal_rules.json',
            _DISABLED_PAYOUT,
            True,
            'delay',
            {},
            None,
            None,
            'v2_hold_delay_expected_docs.json',
            'v2_expected_accounts.json',
            'v2_expected_entities.json',
            'v2_delay_subventions_expected_orders_docs.json',
            'empty_stq_calls.json',
            'empty_doc_updates.json',
            id='8',
        ),
        pytest.param(
            'v2_antifraud_check_doc_geo_booking.json',
            'default_rules.json',
            'personal_rules.json',
            _DISABLED_PAYOUT,
            False,
            'pay',
            {},
            None,
            None,
            'v2_expected_docs_geo_booking.json',
            'v2_expected_accounts.json',
            'v2_expected_entities.json',
            'empty_orders_docs.json',
            'expected_geo_booking_pay_stq_calls.json',
            'empty_doc_updates.json',
            id='9',
        ),
        pytest.param(
            'v2_antifraud_check_doc_payout_subventions.json',
            'default_rules.json',
            'personal_rules.json',
            _ENABLED_PAYOUT,
            True,
            'pay',
            {
                'BILLING_PARK_COMMISSION_CALCULATE_BY_KIND': {
                    '__default__': False,
                    'subvention': True,
                },
            },
            200,
            _build_common_park_commission_rules(),
            'v2_pay_expected_docs.json',
            'v2_expected_accounts.json',
            'v2_expected_entities.json',
            'v2_payout_subventions_expected_orders_docs.json',
            'empty_stq_calls.json',
            'park_commission_doc_updates.json',
            id='dryrun_park_commission',
        ),
        pytest.param(
            'v2_antifraud_check_doc_payout_subventions.json',
            'default_rules.json',
            'personal_rules.json',
            _ENABLED_PAYOUT,
            True,
            'pay',
            {
                'BILLING_PARK_COMMISSION_CALCULATE_BY_KIND': {
                    '__default__': False,
                    'subvention': True,
                },
                'BILLING_PARK_COMMISSION_FLOW_BY_KIND': {
                    '__default__': {
                        '__default__': [
                            {'start_date': '2099-01-01T00:00:00+00:00'},
                        ],
                    },
                    'subvention': {
                        '__default__': [
                            {'start_date': '2000-01-01T00:00:00+00:00'},
                        ],
                    },
                },
            },
            200,
            _build_common_park_commission_rules(),
            'v2_pay_expected_docs.json',
            'v2_expected_accounts.json',
            'v2_expected_entities.json',
            (
                'v2_payout_subventions_expected_orders_docs'
                '_with_park_commission.json'
            ),
            'empty_stq_calls.json',
            'park_commission_doc_updates.json',
            id='write_park_commission',
        ),
        pytest.param(
            'v2_antifraud_check_doc_payout_subventions.json',
            'default_rules.json',
            'personal_rules.json',
            _ENABLED_PAYOUT,
            True,
            'pay',
            {
                'BILLING_PARK_COMMISSION_CALCULATE_BY_KIND': {
                    '__default__': False,
                    'subvention': True,
                },
                'BILLING_PARK_COMMISSION_FLOW_BY_KIND': {
                    '__default__': {
                        '__default__': [
                            {'start_date': '2099-01-01T00:00:00+00:00'},
                        ],
                    },
                    'subvention': {
                        '__default__': [
                            {'start_date': '2000-01-01T00:00:00+00:00'},
                        ],
                    },
                },
            },
            404,
            None,
            'v2_pay_expected_docs.json',
            'v2_expected_accounts.json',
            'v2_expected_entities.json',
            (
                'v2_payout_subventions_expected_orders_'
                'docs_park_commission_rule_not_found.json'
            ),
            'empty_stq_calls.json',
            'park_commission_rule_not_found_doc_updates.json',
            id='park_commission_rule_not_found',
        ),
        pytest.param(
            'v2_antifraud_check_doc_payout_subventions.json',
            'default_rules.json',
            'personal_rules.json',
            _DISABLED_PAYOUT,
            True,
            'block',
            {
                'BILLING_PARK_COMMISSION_CALCULATE_BY_KIND': {
                    '__default__': False,
                    'subvention': True,
                },
                'BILLING_PARK_COMMISSION_FLOW_BY_KIND': {
                    '__default__': {
                        '__default__': [
                            {'start_date': '2099-01-01T00:00:00+00:00'},
                        ],
                    },
                    'subvention': {
                        '__default__': [
                            {'start_date': '2000-01-01T00:00:00+00:00'},
                        ],
                    },
                },
            },
            None,
            None,
            'v2_block_expected_docs.json',
            'v2_expected_accounts.json',
            'v2_expected_entities.json',
            (
                'v2_revoke_subventions_expected_orders_docs'
                '_with_park_commission.json'
            ),
            'empty_stq_calls.json',
            'empty_doc_updates.json',
            id='revoke_with_billing_park_commission_flow_flag',
        ),
    ],
)
async def test_process_antifraud_check(
        doc_json,
        default_rules_json,
        personal_rules_json,
        payout_migration,
        pay_out_subventions,
        af_check_subvention_resp,
        configs,
        park_commission_rules_status,
        park_commission_rules,
        expected_docs_json,
        expected_accounts_json,
        expected_entities_json,
        expected_orders_docs_json,
        expected_stq_calls_json,
        expected_doc_updates_json,
        db,
        monkeypatch,
        load_json,
        load_py_json,
        patch,
        session,
        mock_subvention_communications,
):
    _patch_random(patch)
    _turn_on_antifraud_processing(monkeypatch)
    _turn_on_driver_fix_park_commission_sending(monkeypatch)
    _turn_on_driver_fix_create_minutes_income_journal(monkeypatch)
    doc = load_py_json(doc_json)
    expected_docs = load_py_json(expected_docs_json)
    expected_accounts = load_json(expected_accounts_json)
    expected_entities = load_json(expected_entities_json)
    expected_orders_docs = load_json(expected_orders_docs_json)
    expected_stq_calls = load_json(expected_stq_calls_json)
    expected_doc_updates = load_json(expected_doc_updates_json)
    pay_out_subventions_af = pay_out_subventions
    payout_migration_af = payout_migration
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        db=db,
        balances={},
        existing_docs=[doc],
        payout_migration=payout_migration,
        payout_migration_af=payout_migration_af,
        pay_out_subventions=pay_out_subventions,
        pay_out_subventions_af=pay_out_subventions_af,
        af_check_subvention_resp=af_check_subvention_resp,
        session=session,
        park_commission_rules=park_commission_rules,
        park_commission_rules_status=park_commission_rules_status,
    )
    _fill_arbitrary_configs(monkeypatch, configs)
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=0,
    )
    assert context.docs_client.created_docs == expected_docs
    assert context.accounts_client.created_accounts == expected_accounts
    assert context.accounts_client.created_entities == expected_entities
    assert context.orders_client.created_docs == expected_orders_docs

    assert context.stq_agent.calls == expected_stq_calls

    assert context.docs_client.update_events == expected_doc_updates


@pytest.mark.now('2018-11-30T19:31:35')
@pytest.mark.parametrize(
    'doc_json, '
    'expected_subventions_docs_json, '
    'expected_orders_docs_json, '
    'expected_accounts_json, '
    'expected_entities_json, order_ready_for_billing',
    [
        (
            'antifraud_complete_doc.json',
            'expected_docs.json',
            'empty_docs.json',
            'expected_accounts.json',
            'expected_entities.json',
            'order_ready_for_billing.json',
        ),
        (
            'with_other_docs_doc.json',
            'with_other_docs_expected_docs.json',
            'empty_docs.json',
            'with_other_docs_expected_accounts.json',
            'with_other_docs_expected_entities.json',
            'with_other_docs_order_ready_for_billing.json',
        ),
        # ORFB ID does not match antifraud doc tags, so this antifraud doc is
        # stale
        (
            'stale_antifraud_complete_doc.json',
            'stale_expected_docs.json',
            'empty_docs.json',
            'stale_expected_accounts.json',
            'stale_expected_entities.json',
            'newer_order_ready_for_billing.json',
        ),
        (
            'with_convertible_to_payout_data_doc.json',
            'with_convertible_to_payout_data_expected_subventions_docs.json',
            'with_convertible_to_payout_data_expected_orders_docs.json',
            'stale_expected_accounts.json',
            'stale_expected_entities.json',
            'newer_order_ready_for_billing.json',
        ),
    ],
)
async def test_process_antifraud_complete(
        monkeypatch,
        doc_json,
        expected_subventions_docs_json,
        expected_orders_docs_json,
        expected_accounts_json,
        expected_entities_json,
        order_ready_for_billing,
        db,
        load_json,
):
    _turn_on_antifraud_complete(monkeypatch)
    doc = load_json(doc_json)
    expected_subventions_docs = load_json(expected_subventions_docs_json)
    expected_orders_docs = load_json(expected_orders_docs_json)
    expected_accounts = load_json(expected_accounts_json)
    expected_entities = load_json(expected_entities_json)
    order_ready_for_billing = load_json(order_ready_for_billing)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        db=db,
        balances={},
        existing_docs=order_ready_for_billing,
    )
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=0,
    )
    assert context.docs_client.created_docs == expected_subventions_docs
    assert context.orders_client.created_docs == expected_orders_docs
    assert context.accounts_client.created_accounts == expected_accounts
    assert context.accounts_client.created_entities == expected_entities


@pytest.mark.now('2018-11-30T19:31:35')
@pytest.mark.parametrize(
    'doc_json, zones_json, default_rules_json, convert_unfit_to_support_info, '
    'expected_docs_json, expected_accounts_json, expected_entities_json',
    [
        (
            'order_commission_changed_doc.json',
            'zones.json',
            'default_rules.json',
            _SAVE_UNFIT,
            'expected_commission_docs.json',
            'expected_commission_accounts.json',
            'expected_entities.json',
        ),
        (
            'order_commission_changed_doc.json',
            'zones.json',
            'default_not_net_rules.json',
            _SAVE_UNFIT,
            'expected_commission_docs_no_net_rules.json',
            'empty.json',
            'empty.json',
        ),
        (
            'order_commission_changed_doc.json',
            'zones.json',
            'empty.json',
            _SAVE_UNFIT,
            'expected_commission_docs_no_net_rules.json',
            'empty.json',
            'empty.json',
        ),
        (
            'order_subvention_changed_doc.json',
            'zones.json',
            'default_rules.json',
            _SAVE_UNFIT,
            'expected_subvention_docs.json',
            'expected_subvention_accounts.json',
            'expected_entities.json',
        ),
        (
            'unfit_order_commission_changed_doc.json',
            'zones.json',
            'default_rules.json',
            _SAVE_UNFIT,
            'expected_unfit_commission_docs.json',
            'expected_unfit_commission_accounts.json',
            'expected_entities.json',
        ),
        (
            'subv_disable_all_order_commission_changed_doc.json',
            'zones.json',
            'default_rules.json',
            _SAVE_UNFIT,
            'expected_subv_disable_all_commission_docs.json',
            'expected_unfit_commission_accounts.json',
            'expected_entities.json',
        ),
        (
            'unfit_order_commission_changed_doc.json',
            'zones.json',
            'default_rules.json',
            _CONVERT_UNFIT_TO_SUPPORT_INFO,
            'expected_convert_unfit_commission_docs.json',
            'empty_accounts.json',
            'empty_entities.json',
        ),
        (
            'unfit_order_subvention_changed_doc.json',
            'zones.json',
            'default_rules.json',
            _SAVE_UNFIT,
            'expected_unfit_subvention_docs.json',
            'expected_unfit_subvention_accounts.json',
            'expected_entities.json',
        ),
        (
            'unfit_order_subvention_changed_doc.json',
            'zones.json',
            'default_rules.json',
            _CONVERT_UNFIT_TO_SUPPORT_INFO,
            'expected_convert_unfit_subvention_docs.json',
            'empty_accounts.json',
            'empty_entities.json',
        ),
    ],
)
async def test_process_order_balance_changed(
        doc_json,
        zones_json,
        default_rules_json,
        convert_unfit_to_support_info,
        expected_docs_json,
        expected_accounts_json,
        expected_entities_json,
        db,
        load_json,
        load_py_json,
        load_py_json_dir,
        patch,
):

    # pylint: disable=invalid-name
    @patch('taxi_billing_subventions.common.db.rule.fetch_daily_guarantees')
    async def fetch_daily_guarantees(
            database: taxi_db.Database,
            zone_names: tp.List[str],
            tzinfo_by_zone: cta.TZInfoByZone,
            ended_after: dt.datetime,
            started_not_after: dt.datetime,
    ) -> tp.List[models.DailyGuaranteeRule]:
        docs = load_py_json_dir(
            'test_process_order_balance_changed', default_rules_json,
        )
        # pylint: disable=protected-access
        docs_by_group_id = data_structures.group_by(
            docs, key=_mongo._get_group_id,
        )
        tzinfo_by_zone = {'moscow': pytz.timezone('Europe/Moscow')}
        rules = []
        for docs_group in docs_by_group_id.values():
            # pylint: disable=protected-access
            rules.extend(
                _mongo._build_daily_guarantee_rules(
                    docs_group, tzinfo_by_zone,
                ),
            )
        return rules

    doc = load_py_json(doc_json)
    zones = load_py_json_dir('test_process_order_balance_changed', zones_json)
    expected_docs = load_json(expected_docs_json)
    expected_accounts = load_json(expected_accounts_json)
    expected_entities = load_json(expected_entities_json)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=zones,
        db=db,
        balances={},
        convert_unfit_to_support_info=convert_unfit_to_support_info,
        save_nmfg_tag=True,
    )
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=0,
    )
    _assert_docs_equal(
        expected_docs=expected_docs,
        actual_docs=context.docs_client.created_docs,
    )
    assert context.accounts_client.created_accounts == expected_accounts
    assert context.accounts_client.created_entities == expected_entities


@pytest.mark.now('2019-02-07T15:00:00')
@pytest.mark.parametrize(
    'doc_json,default_rules_json,personal_rules_json,minimize_reversals,'
    'fix_minimal_reversals_since, save_nmfg_tag, old_journal_limit_days, '
    'existing_docs_json,existing_accounts_json,expected_created_docs,'
    'expected_accounts,expected_entities',
    [
        (
            'order_ready_for_billing_doc.json',
            'default_rules.json',
            'personal_rules.json',
            False,
            '2100-01-01T00:00:00+00:00',
            False,
            365,
            'existing_docs.json',
            'existing_accounts.json',
            'expected_created_docs.json',
            'expected_accounts.json',
            'expected_entities.json',
        ),
        (
            'separate_journal_topic_order_ready_for_billing_doc.json',
            'default_minimize_reversals_rules.json',
            'personal_rules.json',
            True,
            '2100-01-01T00:00:00+00:00',
            False,
            365,
            'existing_separate_journal_topic_docs.json',
            'existing_accounts.json',
            'expected_separate_journal_topic_created_docs.json',
            'expected_minimize_reversals_accounts.json',
            'expected_minimize_reversals_entities.json',
        ),
        (
            'order_ready_for_billing_doc.json',
            'default_minimize_reversals_rules.json',
            'personal_rules.json',
            True,
            '2100-01-01T00:00:00+00:00',
            False,
            365,
            'existing_docs.json',
            'existing_accounts.json',
            'expected_minimize_reversals_created_docs.json',
            'expected_minimize_reversals_accounts.json',
            'expected_minimize_reversals_entities.json',
        ),
        (
            'old_order_ready_for_billing_doc.json',
            'default_rules.json',
            'personal_rules.json',
            False,
            '2100-01-01T00:00:00+00:00',
            False,
            365,
            'existing_docs.json',
            'existing_accounts.json',
            'old_expected_created_docs.json',
            'old_expected_accounts.json',
            'old_expected_entities.json',
        ),
        (
            'order_ready_for_billing_doc_completed.json',
            'default_rules.json',
            'personal_rules.json',
            False,
            '2100-01-01T00:00:00+00:00',
            False,
            365,
            'existing_docs_completed.json',
            'existing_accounts.json',
            'expected_created_docs_completed.json',
            'expected_accounts.json',
            'expected_entities.json',
        ),
        (
            'order_ready_for_billing_doc.json',
            'default_minimize_reversals_rules.json',
            'personal_rules.json',
            True,
            '2100-01-01T00:00:00+00:00',
            False,
            365,
            'existing_docs_with_two_sj.json',
            'existing_accounts.json',
            'expected_minimize_reversals_created_docs_if_two_sj.json',
            'expected_minimize_reversals_accounts_if_two_sj.json',
            'expected_minimize_reversals_entities.json',
        ),
    ],
)
@pytest.mark.filldb(
    parks='for_test_order_ready_for_billing_amended',
    cities='for_test_process_doc',
)
# pylint: disable=invalid-name
# pylint: disable=too-many-arguments
async def test_order_ready_for_billing_amended(
        doc_json,
        default_rules_json,
        personal_rules_json,
        minimize_reversals,
        fix_minimal_reversals_since,
        save_nmfg_tag,
        old_journal_limit_days,
        existing_docs_json,
        existing_accounts_json,
        expected_created_docs,
        expected_accounts,
        expected_entities,
        db,
        load_json,
        load_py_json,
        load_py_json_dir,
        monkeypatch,
        patch,
):
    @patch('random.randint')
    def _randint(left, right):
        return (left + right) / 2

    _turn_on_check_rebill_allowed(monkeypatch)

    monkeypatch.setattr(
        config.Config, 'BILLING_REVERSE_DOC_ON_ORDER_AMENDED', True,
    )
    monkeypatch.setattr(
        config.Config, 'BILLING_SUBVENTIONS_DOC_IDS_TO_SKIP_ASSERTION', [100],
    )

    await _patch_database_calls(
        json_path='test_order_ready_for_billing_amended',
        patch=patch,
        load_py_json_dir=load_py_json_dir,
        default_rules_json=default_rules_json,
        personal_rules_json=personal_rules_json,
    )

    doc = load_json(doc_json)
    existing_docs = load_py_json(existing_docs_json)
    existing_accounts = load_json(existing_accounts_json)
    existing_docs.append(doc)
    expected_created_docs = load_py_json(expected_created_docs)
    expected_accounts = load_json(expected_accounts)
    expected_entities = load_json(expected_entities)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        db=db,
        balances={},
        existing_docs=existing_docs,
        existing_accounts=existing_accounts,
        minimize_reversals=minimize_reversals,
        fix_minimal_reversals_since=fix_minimal_reversals_since,
        save_nmfg_tag=save_nmfg_tag,
        old_journal_limit_days=old_journal_limit_days,
    )
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=100,
    )
    assert expected_accounts == context.accounts_client.created_accounts
    _assert_same_entities(
        expected_entities, context.accounts_client.created_entities,
    )
    _assert_docs_equal(
        expected_docs=expected_created_docs,
        actual_docs=context.docs_client.created_docs,
    )


@pytest.mark.now('2019-02-07T15:00:00')
@pytest.mark.parametrize(
    'doc_json,default_rules_json,personal_rules_json,minimize_reversals,'
    'fix_minimal_reversals_since, save_nmfg_tag, old_journal_limit_days, '
    'existing_docs_json,existing_accounts_json,expected_created_docs,'
    'expected_accounts,expected_entities',
    [
        (
            'order_ready_for_billing_doc.json',
            'default_rules.json',
            'personal_rules.json',
            False,
            '2100-01-01T00:00:00+00:00',
            False,
            365,
            'existing_docs.json',
            'existing_accounts.json',
            'expected_created_docs.json',
            'expected_accounts.json',
            'expected_entities.json',
        ),
        (
            'separate_journal_topic_order_ready_for_billing_doc.json',
            'default_minimize_reversals_rules.json',
            'personal_rules.json',
            True,
            '2100-01-01T00:00:00+00:00',
            False,
            365,
            'existing_separate_journal_topic_docs.json',
            'existing_accounts.json',
            'expected_separate_journal_topic_created_docs.json',
            'expected_minimize_reversals_accounts.json',
            'expected_minimize_reversals_entities.json',
        ),
        (
            'separate_journal_topic_order_ready_for_billing_doc.json',
            'default_minimize_reversals_rules.json',
            'personal_rules.json',
            True,
            '0001-01-01T00:00:00+00:00',
            True,
            365,
            'existing_fix_minimal_reversals_docs.json',
            'existing_accounts.json',
            'expected_fix_minimal_reversals_created_docs.json',
            'expected_minimize_reversals_accounts.json',
            'expected_minimize_reversals_entities.json',
        ),
        pytest.param(
            'separate_journal_topic_order_ready_for_billing_doc.json',
            'default_minimize_reversals_rules.json',
            'personal_rules.json',
            True,
            '0001-01-01T00:00:00+00:00',
            True,
            365,
            'existing_fix_minimal_reversals_docs_and_current_doc_journal.json',
            'existing_accounts.json',
            'expected_fix_minimal_reversals_created_docs.json',
            'expected_minimize_reversals_accounts.json',
            'expected_minimize_reversals_entities.json',
            id='Current ORFB jornal docs are ignored when do minimal reversal',
        ),
        (
            'order_ready_for_billing_doc.json',
            'default_minimize_reversals_rules.json',
            'personal_rules.json',
            True,
            '2100-01-01T00:00:00+00:00',
            False,
            365,
            'existing_docs.json',
            'existing_accounts.json',
            'expected_minimize_reversals_created_docs.json',
            'expected_minimize_reversals_accounts.json',
            'expected_minimize_reversals_entities.json',
        ),
        (
            'order_ready_for_billing_doc.json',
            'default_rules.json',
            'personal_rules.json',
            False,
            '2100-01-01T00:00:00+00:00',
            False,
            1,
            'existing_docs.json',
            'existing_accounts.json',
            'expected_created_docs_old_entries.json',
            'expected_accounts.json',
            'expected_entities.json',
        ),
    ],
)
# pylint: disable=invalid-name
# pylint: disable=too-many-arguments
@pytest.mark.filldb(
    parks='for_test_order_ready_for_billing_amended_reports',
    cities='for_test_process_doc',
)
async def test_order_ready_for_billing_amended_reports(
        doc_json,
        default_rules_json,
        personal_rules_json,
        minimize_reversals,
        fix_minimal_reversals_since,
        save_nmfg_tag,
        old_journal_limit_days,
        existing_docs_json,
        existing_accounts_json,
        expected_created_docs,
        expected_accounts,
        expected_entities,
        db,
        load_json,
        load_py_json,
        load_py_json_dir,
        monkeypatch,
        patch,
):
    monkeypatch.setattr(
        config.Config, 'BILLING_SUBVENTIONS_USE_REPORTS_FOR_ORFB', True,
    )

    await test_order_ready_for_billing_amended(
        doc_json,
        default_rules_json,
        personal_rules_json,
        minimize_reversals,
        fix_minimal_reversals_since,
        save_nmfg_tag,
        old_journal_limit_days,
        existing_docs_json,
        existing_accounts_json,
        expected_created_docs,
        expected_accounts,
        expected_entities,
        db,
        load_json,
        load_py_json,
        load_py_json_dir,
        monkeypatch,
        patch,
    )


@pytest.mark.filldb(
    tariffs='for_test_process_order_completed',
    commission_contracts='for_test_process_order_completed',
    driver_workshifts='for_test_process_order_completed',
)
@pytest.mark.now('2018-11-30T19:31:35')
@pytest.mark.parametrize(
    'doc_json, expected_docs_json, configs, '
    'park_commission_rules_status, '
    'park_commission_rules',
    [
        (
            'order_completed_doc.json',
            'order_completed_expected_docs.json',
            {},
            None,
            None,
        ),
        (
            'order_completed_doc_with_toll_road.json',
            'order_completed_with_toll_road_expected_docs.json',
            {},
            None,
            None,
        ),
        (
            'order_completed_doc_with_ya_plus.json',
            'order_completed_with_ya_plus_expected_docs.json',
            {},
            None,
            None,
        ),
        (
            'order_completed_doc_with_hold_delay.json',
            'order_completed_with_hold_delay_expected_docs.json',
            {},
            None,
            None,
        ),
        (
            'order_completed_doc_without_workshift_ids.json',
            'order_completed_without_workshift_ids_expected_docs.json',
            {},
            None,
            None,
        ),
        (
            'order_completed_doc_with_workshift_ids.json',
            'order_completed_with_workshift_ids_expected_docs.json',
            {},
            None,
            None,
        ),
        (
            'order_completed_doc_cancelled.json',
            'order_completed_cancelled_expected_docs.json',
            {},
            None,
            None,
        ),
        (
            'order_completed_doc_with_cost_for_driver.json',
            'order_completed_with_cost_for_driver_expected_docs.json',
            {},
            None,
            None,
        ),
        (
            'order_completed_doc_with_rebate.json',
            'order_completed_with_rebate_expected_docs.json',
            dict(
                BILLING_SUBVENTIONS_APPLY_REBATE_TO_SUCCESSFULL_ORDERS_ONLY=(
                    True
                ),
            ),
            None,
            None,
        ),
        (
            'order_completed_doc_no_currency_rate.json',
            'order_completed_no_currency_rate_expected_docs.json',
            {},
            None,
            None,
        ),
        (
            'order_completed_doc_not_fetch_driver_promocodes.json',
            'order_completed_not_fetch_driver_promocodes_expected_docs.json',
            {},
            None,
            None,
        ),
        (
            'order_completed_doc_with_driver_promocode.json',
            'order_completed_with_driver_promocode_expected_docs.json',
            {},
            None,
            None,
        ),
        (
            'order_completed_with_is_external_billing.json',
            'order_completed_with_is_external_billing_expected_docs.json',
            {},
            None,
            None,
        ),
        (
            'order_completed_doc_with_fine.json',
            'order_completed_with_fine_expected_docs.json',
            {},
            None,
            None,
        ),
        (
            'order_completed_doc_fetch_park_commission.json',
            'order_completed_doc_fetch_park_commission_expected_docs.json',
            {
                'BILLING_PARK_COMMISSION_CALCULATE_BY_KIND': {
                    '__default__': False,
                    'order_ready_for_billing': True,
                },
            },
            None,
            None,
        ),
        (
            'order_completed_doc_fetch_park_commission_no_work_rule_id.json',
            (
                'order_completed_doc_fetch_park_commission_no_work_rule_id'
                '_expected_docs.json'
            ),
            {
                'BILLING_PARK_COMMISSION_CALCULATE_BY_KIND': {
                    '__default__': False,
                    'order_ready_for_billing': True,
                },
            },
            200,
            {
                'rules': [
                    {
                        'kind': 'order',
                        'amount_rate': '0.5555',
                        'amount_fixed': '0.0000',
                        'is_platfrom_commission_enabled': True,
                        'is_commission_if_platform_commission_is_null_enabled': (  # noqa: E501 line too long
                            True
                        ),
                        'rule_type_id': '4964b852670045b196e526d59915b777',
                    },
                ],
            },
        ),
        (
            'order_completed_doc_fetch_park_commission_no_work_rule_id.json',
            (
                'order_completed_doc_fetch_park_commission_no_rule_found'
                '_expected_docs.json'
            ),
            {
                'BILLING_PARK_COMMISSION_CALCULATE_BY_KIND': {
                    '__default__': False,
                    'order_ready_for_billing': True,
                },
            },
            404,
            None,
        ),
        (
            'order_completed_doc_with_call_center.json',
            'order_completed_with_call_center_expected_docs.json',
            {},
            None,
            None,
        ),
    ],
)
async def test_process_order_completed(
        doc_json,
        expected_docs_json,
        configs,
        park_commission_rules_status,
        park_commission_rules,
        db,
        load_json,
        monkeypatch,
        stq_client_patched,
):
    doc = load_json(doc_json)
    zones = [
        models.Zone(
            'Moscow',
            'id',
            pytz.utc,
            'RUB',
            None,
            models.Vat.make_naive(12000),
            'rus',
        ),
        _build_moscow_zone(),
        _build_tel_aviv_zone(),
    ]
    _fill_arbitrary_configs(monkeypatch, configs)
    expected_docs = load_json(expected_docs_json)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=zones,
        db=db,
        balances={},
        park_commission_rules=(
            park_commission_rules or _build_common_park_commission_rules()
        ),
        park_commission_rules_status=park_commission_rules_status,
    )
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=doc['doc_id'],
    )
    assert context.docs_client.created_docs == expected_docs


@pytest.mark.filldb(
    tariffs='for_test_process_order_completed',
    commission_contracts='for_test_process_order_completed',
    driver_workshifts='for_test_process_order_completed',
)
@pytest.mark.now('2018-11-30T19:31:35')
@pytest.mark.parametrize(
    'doc_json, is_stq_call_expected, configs',
    [
        pytest.param(
            'order_completed_doc.json',
            True,
            {
                'BILLING_FUNCTIONS_TAXI_ORDER_MIGRATION': {
                    'by_zone': {
                        '__default__': {
                            'enabled': [
                                {'since': '2099-01-01T00:00:00+03:00'},
                            ],
                        },
                        'Moscow': {
                            'enabled': [
                                {'since': '2018-07-01T00:00:00+03:00'},
                            ],
                        },
                    },
                },
            },
            id='"taxi_order" enabled by zone',
        ),
        pytest.param(
            'order_completed_doc.json',
            False,
            {
                'BILLING_FUNCTIONS_TAXI_ORDER_MIGRATION': {
                    'by_zone': {
                        '__default__': {
                            'enabled': [
                                {'since': '2018-01-01T00:00:00+03:00'},
                            ],
                        },
                        'Moscow': {
                            'disabled': [
                                {'since': '2018-01-01T00:00:00+03:00'},
                            ],
                        },
                    },
                },
            },
            id='"taxi_order" disabled by zone',
        ),
    ],
)
async def test_schedule_taxi_order(
        doc_json, is_stq_call_expected, configs, db, load_py_json, monkeypatch,
):
    doc = load_py_json(doc_json)
    _fill_arbitrary_configs(monkeypatch, configs)
    zones = [
        models.Zone(
            'Moscow',
            'id',
            pytz.utc,
            'RUB',
            None,
            models.Vat.make_naive(12000),
            'rus',
        ),
    ]
    context = ContextData(doc=doc, rules=[], zones=zones, db=db, balances={})
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=doc['doc_id'],
    )
    calls = context.stq_agent.calls
    if is_stq_call_expected:
        assert len(calls) == 1
        assert calls[0] == load_py_json('stq_call.json')

    else:
        assert not calls


@pytest.mark.filldb(
    commission_contracts='for_test_process_shift_ended',
    subvention_rules='for_test_process_shift_ended',
    personal_subvention_rules='for_test_process_shift_ended',
    parks='for_test_process_shift_ended',
    cities='for_test_process_shift_ended',
    currency_rates='for_test_process_shift_ended',
)
@pytest.mark.now('2018-05-12T05:00:00+03:00')
@pytest.mark.parametrize(
    'contracts_json, doc_json, existing_docs_json, existing_accounts_json, '
    'journal_entries_json, '
    'expected_docs_json, expected_accounts_json, expected_entities_json, '
    'expected_fulfilled_notify_json, expected_done_p_subventions_json, '
    'num_goal_orders, new_billing_migration, '
    'incomplete_related_docs, save_nmfg_support_info, balances_version, '
    'use_billing_reports',
    [
        (
            'contracts.json',
            'b2b_driver_fix_shift_ended_doc.json',
            'empty_existing_docs.json',
            'empty_accounts.json',
            'b2b_driver_fix_journal_entries.json',
            'expected_driver_fix_docs_b2b.json',
            'expected_driver_fix_accounts_b2b.json',
            'expected_driver_fix_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            0,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            5,
            False,
        ),
        (
            'contracts.json',
            'b2b_driver_fix_shift_ended_doc.json',
            'empty_existing_docs.json',
            'existing_b2b_driver_fix_accounts.json',
            'b2b_driver_fix_journal_entries.json',
            'expected_driver_fix_docs_b2b.json',
            'expected_driver_fix_accounts_b2b.json',
            'expected_driver_fix_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            0,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            5,
            True,
        ),
        pytest.param(
            'contracts.json',
            'driver_fix_shift_ended_doc.json',
            'empty_existing_docs.json',
            'empty_accounts.json',
            'driver_fix_journal_entries.json',
            'expected_driver_fix_docs_if_commission.json',
            'expected_driver_fix_accounts_if_commission.json',
            'expected_driver_fix_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            0,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            False,
            id='driver-fix commission',
        ),
        pytest.param(
            'contracts.json',
            'driver_fix_shift_ended_doc.json',
            'empty_existing_docs.json',
            'empty_accounts.json',
            'driver_fix_journal_entries.json',
            'expected_driver_fix_docs_if_subvention.json',
            'expected_driver_fix_accounts_if_subvention.json',
            'expected_driver_fix_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            0,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            2,
            False,
            id='driver-fix subvention',
        ),
        pytest.param(
            'contracts.json',
            'driver_fix_shift_ended_doc.json',
            'empty_existing_docs.json',
            'empty_accounts.json',
            'driver_fix_with_discounts_and_promocodes_journal_entries.json',
            'expected_driver_fix_docs_with_discounts_and_promocodes.json',
            'expected_driver_fix_accounts_if_subvention.json',
            'expected_driver_fix_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            0,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            6,
            False,
            id='driver-fix with discounts and promocodes',
        ),
        pytest.param(
            'contracts_111_128_650.json',
            'driver_fix_shift_ended_doc_no_offer_contract.json',
            'empty_existing_docs.json',
            'empty_accounts.json',
            'empty_journal_entries.json',
            'expected_driver_fix_docs_if_no_offer_contract.json',
            'expected_driver_fix_accounts_if_no_offer_contract.json',
            'expected_driver_fix_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            0,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            2,
            False,
            id='driver-fix with missing offer contract',
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            'contracts_137_651.json',
            'driver_fix_shift_ended_doc_no_contract.json',
            'empty_existing_docs.json',
            'empty_accounts.json',
            'empty_journal_entries.json',
            'expected_driver_fix_docs_if_no_contract.json',
            'empty_accounts.json',
            'expected_driver_fix_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            0,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            2,
            False,
            id='driver-fix with missing contract',
            marks=pytest.mark.xfail,
        ),
        (
            'contracts.json',
            'goal_shift_ended_doc.json',
            'empty_existing_docs.json',
            'empty_accounts.json',
            'empty_journal_entries.json',
            'expected_goal_docs.json',
            'expected_goal_accounts.json',
            'expected_goal_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            15,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            False,
        ),
        (
            'contracts.json',
            'geo_booking_shift_ended_doc_from_driver_geoarea_activity.json',
            'empty_existing_docs.json',
            'empty_accounts.json',
            'geo_booking_journal_entries.json',
            'expected_geo_booking_docs.json',
            'expected_geo_booking_accounts.json',
            'expected_geo_booking_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            15,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            False,
        ),
        # geo_booking shift_ended event with ancestor_doc_id tag (orfb)
        (
            'contracts.json',
            'geo_booking_shift_ended_doc_from_order_ready_for_billing.json',
            'existing_order_ready_for_billing_docs.json',
            'empty_accounts.json',
            'geo_booking_journal_entries.json',
            'expected_geo_booking_docs.json',
            'expected_geo_booking_accounts.json',
            'expected_geo_booking_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            15,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            False,
        ),
        # geo_booking shift_ended event with ancestor_doc_id tag (cargo_orfb)
        (
            'contracts_1164_1161_1162_1163.json',
            'geo_booking_shift_ended_doc_from_order_ready_for_billing.json',
            'existing_order_ready_for_billing_docs_cargo.json',
            'empty_accounts.json',
            'geo_booking_journal_entries.json',
            'expected_geo_booking_docs_cargo.json',
            'expected_geo_booking_accounts.json',
            'expected_geo_booking_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            15,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            False,
        ),
        # geo_booking shift_ended event with ancestor_doc_id tag (taxi_order)
        (
            'contracts.json',
            'geo_booking_shift_ended_doc_from_order_ready_for_billing.json',
            'existing_taxi_order_docs.json',
            'empty_accounts.json',
            'geo_booking_journal_entries.json',
            'expected_geo_booking_docs.json',
            'expected_geo_booking_accounts.json',
            'expected_geo_booking_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            15,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            False,
        ),
        (
            'contracts.json',
            'daily_guarantee_shift_ended_doc.json',
            'empty_existing_docs.json',
            'empty_accounts.json',
            'daily_guarantee_journal_entries.json',
            'expected_incomplete_daily_guarantee_docs.json',
            'expected_daily_guarantee_accounts.json',
            'expected_daily_guarantee_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            15,
            _ENABLED_BILLING_EVERYWHERE,
            True,
            True,
            1,
            False,
        ),
        (
            'contracts.json',
            'daily_guarantee_shift_ended_doc.json',
            'empty_existing_docs.json',
            'empty_accounts.json',
            'daily_guarantee_journal_entries.json',
            'expected_daily_guarantee_docs.json',
            'expected_daily_guarantee_accounts.json',
            'expected_daily_guarantee_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            15,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            True,
            1,
            False,
        ),
        (
            'contracts.json',
            'daily_guarantee_shift_ended_doc.json',
            'empty_existing_docs.json',
            'existing_daily_guarantee_accounts.json',
            'daily_guarantee_journal_entries.json',
            'expected_daily_guarantee_docs.json',
            'expected_daily_guarantee_accounts.json',
            'expected_daily_guarantee_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            15,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            True,
            1,
            True,
        ),
        (
            'contracts.json',
            'daily_guarantee_shift_ended_with_ancestor_tag_doc.json',
            'existing_order_ready_for_billing_docs.json',
            'empty_accounts.json',
            'empty_journal_entries.json',
            'expected_daily_guarantee_with_ancestor_tag_docs.json',
            'expected_daily_guarantee_with_ancestor_tag_accounts.json',
            'expected_daily_guarantee_entities.json',
            'expected_fulfilled_notify_with_ancestor_tag_entities.json',
            'expected_empty_done_personal_subventions.json',
            15,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            False,
        ),
        (
            'contracts_1164_1161_1162_1163.json',
            'daily_guarantee_shift_ended_with_ancestor_tag_doc.json',
            'existing_order_ready_for_billing_docs_cargo.json',
            'empty_accounts.json',
            'empty_journal_entries.json',
            'expected_daily_guarantee_with_ancestor_tag_docs_cargo.json',
            'expected_daily_guarantee_with_ancestor_tag_accounts.json',
            'expected_daily_guarantee_entities.json',
            'expected_fulfilled_notify_with_ancestor_tag_entities.json',
            'expected_empty_done_personal_subventions.json',
            15,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            False,
        ),
        (
            'contracts.json',
            'daily_guarantee_shift_ended_with_ancestor_tag_doc.json',
            'existing_taxi_order_docs.json',
            'empty_accounts.json',
            'empty_journal_entries.json',
            'expected_daily_guarantee_with_taxi_order_ancestor_docs.json',
            'expected_daily_guarantee_with_ancestor_tag_accounts.json',
            'expected_daily_guarantee_entities.json',
            'expected_fulfilled_notify_with_ancestor_tag_entities.json',
            'expected_empty_done_personal_subventions.json',
            15,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            False,
        ),
        (
            'contracts.json',
            'daily_guarantee_shift_ended_with_ancestor_tag_doc.json',
            'existing_order_ready_for_billing_docs.json',
            'empty_accounts.json',
            'empty_journal_entries.json',
            (
                'expected_daily_guarantee_with_ancestor_tag_'
                'and_subventions_context_docs.json'
            ),
            'expected_daily_guarantee_with_ancestor_tag_accounts.json',
            'expected_daily_guarantee_entities.json',
            'expected_fulfilled_notify_with_ancestor_tag_entities.json',
            'expected_empty_done_personal_subventions.json',
            15,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            False,
        ),
        (
            'contracts.json',
            'commission_daily_guarantee_shift_ended_doc.json',
            'existing_unfit_docs.json',
            'empty_accounts.json',
            'commission_daily_guarantee_journal_entries.json',
            'expected_commission_daily_guarantee_docs.json',
            'expected_commission_daily_guarantee_accounts.json',
            'expected_commission_daily_guarantee_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            15,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            True,
            1,
            False,
        ),
        (
            'contracts.json',
            'goal_with_ancestor_tag_shift_ended_doc.json',
            'existing_order_ready_for_billing_docs.json',
            'empty_accounts.json',
            'goal_with_ancestor_tag_journal_entries.json',
            'expected_goal_with_ancestor_tag_docs.json',
            'expected_goal_with_ancestor_tag_accounts.json',
            'expected_goal_with_ancestor_tag_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            20,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            False,
        ),
        (
            'contracts.json',
            'goal_with_ancestor_tag_shift_ended_doc.json',
            'existing_taxi_order_docs.json',
            'empty_accounts.json',
            'goal_with_ancestor_tag_journal_entries.json',
            'expected_goal_with_taxi_order_ancestor_docs.json',
            'expected_goal_with_ancestor_tag_accounts.json',
            'expected_goal_with_ancestor_tag_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            20,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            False,
        ),
        (
            'contracts.json',
            'personal_goal_shift_ended_doc.json',
            'existing_order_ready_for_billing_docs.json',
            'empty_accounts.json',
            'empty_journal_entries.json',
            'expected_personal_goal_with_ancestor_tag_docs.json',
            'expected_personal_goal_with_ancestor_tag_accounts.json',
            'expected_goal_with_ancestor_tag_entities.json',
            'expected_fulfilled_notify.json',
            'expected_done_personal_subventions.json',
            20,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            False,
        ),
        (
            'contracts.json',
            'personal_goal_shift_ended_doc.json',
            'existing_order_ready_for_billing_docs.json',
            'existing_personal_goal_accounts.json',
            'empty_journal_entries.json',
            'expected_personal_goal_with_ancestor_tag_docs.json',
            'expected_personal_goal_with_ancestor_tag_accounts.json',
            'expected_goal_with_ancestor_tag_entities.json',
            'expected_fulfilled_notify.json',
            'expected_done_personal_subventions.json',
            20,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            True,
        ),
        (
            'contracts.json',
            'personal_goal_shift_ended_doc.json',
            'existing_taxi_order_docs.json',
            'existing_personal_goal_accounts.json',
            'empty_journal_entries.json',
            'expected_personal_goal_with_taxi_order_ancestor_docs.json',
            'expected_personal_goal_with_ancestor_tag_accounts.json',
            'expected_goal_with_ancestor_tag_entities.json',
            'expected_fulfilled_notify.json',
            'expected_done_personal_subventions.json',
            20,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            True,
        ),
        (
            'contracts.json',
            'goal_with_ancestor_tag_shift_ended_doc.json',
            'existing_order_ready_for_billing_docs.json',
            'empty_accounts.json',
            'empty_journal_entries.json',
            (
                'expected_goal_with_ancestor_tag_'
                'and_subventions_context_docs.json'
            ),
            'expected_goal_with_ancestor_tag_accounts.json',
            'expected_goal_with_ancestor_tag_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            20,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            False,
        ),
        (
            'contracts.json',
            'personal_goal_shift_ended_doc.json',
            'existing_order_ready_for_billing_docs.json',
            'empty_accounts.json',
            'empty_journal_entries.json',
            (
                'expected_personal_goal_with_ancestor_tag_'
                'and_subventions_context_docs.json'
            ),
            'expected_personal_goal_with_ancestor_tag_accounts.json',
            'expected_goal_with_ancestor_tag_entities.json',
            'expected_fulfilled_notify.json',
            'expected_done_personal_subventions.json',
            20,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            False,
        ),
        (
            'contracts.json',
            'unfulfilled_goal_shift_ended_doc.json',
            'existing_order_ready_for_billing_docs.json',
            'empty_accounts.json',
            'empty_journal_entries.json',
            'expected_unfulfilled_goal_docs.json',
            'expected_unfulfilled_goal_accounts.json',
            'expected_unfulfilled_goal_entities.json',
            'expected_unfulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            5,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            False,
        ),
        (
            'contracts.json',
            'daily_guarantee_stored_contracts_shift_ended_doc.json',
            'existing_order_ready_for_billing_docs.json',
            'empty_accounts.json',
            'daily_guarantee_journal_entries.json',
            'expected_daily_guarantee_stored_contracts_docs.json',
            'expected_daily_guarantee_with_ancestor_tag_accounts.json',
            'expected_daily_guarantee_entities.json',
            'expected_fulfilled_notify_with_ancestor_tag_entities.json',
            'expected_empty_done_personal_subventions.json',
            15,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            False,
        ),
        (
            'contracts.json',
            'geo_booking_shift_ended_doc_from_cargo_claim.json',
            'existing_cargo_claim_docs.json',
            'empty_accounts.json',
            'geo_booking_journal_entries.json',
            'expected_geo_booking_docs.json',
            'expected_geo_booking_accounts.json',
            'expected_geo_booking_entities.json',
            'expected_fulfilled_notify.json',
            'expected_empty_done_personal_subventions.json',
            15,
            _ENABLED_BILLING_EVERYWHERE,
            False,
            False,
            1,
            False,
        ),
    ],
)
async def test_process_shift_ended(
        stq_client_patched,
        contracts_json,
        doc_json,
        existing_docs_json,
        existing_accounts_json,
        journal_entries_json,
        expected_docs_json,
        expected_accounts_json,
        expected_entities_json,
        expected_fulfilled_notify_json,
        expected_done_p_subventions_json,
        num_goal_orders,
        new_billing_migration,
        incomplete_related_docs,
        save_nmfg_support_info,
        balances_version,
        use_billing_reports,
        db,
        monkeypatch,
        load_json,
        load_py_json,
        patch,
):
    # pylint: disable=too-many-arguments,too-many-locals,invalid-name
    _patch_random(patch)
    _patch_uuid(patch)
    _turn_on_commissions(monkeypatch)
    _turn_on_antifraud_processing(monkeypatch)
    _turn_on_create_subventions_input(monkeypatch)
    _fill_tlog_service_ids(monkeypatch)
    _turn_on_send_contract_id_for_subventions(monkeypatch)
    _use_billing_reports_for_shift_ended(monkeypatch, use_billing_reports)

    doc = load_json(doc_json)
    agreement_ref = doc['data']['agreement_ref']
    journal_entries = load_py_json(journal_entries_json)
    expected_docs = load_py_json(expected_docs_json)
    expected_accounts = load_json(expected_accounts_json)
    expected_entities = load_json(expected_entities_json)
    existing_docs = load_json(existing_docs_json)
    existing_accounts = load_json(existing_accounts_json)
    expected_fulfilled_notify = load_py_json(expected_fulfilled_notify_json)
    expected_done_p_subventions = load_py_json(
        expected_done_p_subventions_json,
    )
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        db=db,
        balances=_build_balances(
            num_goal_orders=num_goal_orders,
            version=balances_version,
            agreement_ref=agreement_ref,
        ),
        journal_entries=journal_entries,
        existing_docs=existing_docs,
        existing_accounts=existing_accounts,
        new_billing_migration=new_billing_migration,
        drivers_profiles={
            'db_id_uuid': {
                'data': {'license': {'pd_id': '8hd93jdlakhf84030ejd9390z'}},
            },
        },
        drivers_licenses={
            '8hd93jdlakhf84030ejd9390z': {
                'id': '8hd93jdlakhf84030ejd9390z',
                'license': '12AB345678',
            },
        },
        save_nmfg_support_info=save_nmfg_support_info,
        desired_agglomeration='mesto_vozniknoveniya_potrebnosti',
        replication_contracts=load_json(contracts_json),
        incomplete_related_docs=incomplete_related_docs,
    )
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
    )
    _assert_docs_equal(
        expected_docs=expected_docs,
        actual_docs=context.docs_client.created_docs,
    )
    assert context.accounts_client.created_accounts == expected_accounts
    assert context.accounts_client.created_entities == expected_entities

    fulfilled_notify = db.fulfilled_subventions_notify.find()
    fulfilled_notify = await fulfilled_notify.to_list(None)
    for rule in fulfilled_notify:
        del rule['_id']
    assert fulfilled_notify == expected_fulfilled_notify

    personal = await db.done_personal_subventions.find().to_list(None)
    for rule in personal:
        del rule['_id']
    assert personal == expected_done_p_subventions, personal


@pytest.mark.filldb(
    commission_contracts='for_test_process_shift_ended',
    subvention_rules='for_test_process_shift_ended',
    personal_subvention_rules='for_test_process_shift_ended',
    parks='for_test_process_shift_ended',
    cities='for_test_process_shift_ended',
    currency_rates='for_test_process_shift_ended',
)
@pytest.mark.now('2018-05-12T05:00:00+03:00')
@pytest.mark.parametrize(
    'doc_json, ' 'num_goal_orders, new_billing_migration, ' 'balances_version',
    [
        ('driver_fix_shift_ended_doc.json', 0, _ENABLED_BILLING_EVERYWHERE, 3),
        ('driver_fix_shift_ended_doc.json', 0, _ENABLED_BILLING_EVERYWHERE, 4),
    ],
)
async def test_process_shift_ended_raises_amount_out_of_limit_error(
        stq_client_patched,
        doc_json,
        num_goal_orders,
        new_billing_migration,
        balances_version,
        db,
        monkeypatch,
        load_json,
        load_py_json,
        patch,
):
    # pylint: disable=too-many-arguments,too-many-locals,invalid-name
    _patch_random(patch)
    _patch_uuid(patch)
    _turn_on_commissions(monkeypatch)
    _turn_on_antifraud_processing(monkeypatch)
    _turn_on_create_subventions_input(monkeypatch)
    _fill_tlog_service_ids(monkeypatch)

    doc = load_json(doc_json)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        db=db,
        balances=_build_balances(
            num_goal_orders=num_goal_orders, version=balances_version,
        ),
        existing_docs=[],
        new_billing_migration=new_billing_migration,
        drivers_profiles={
            'db_id_uuid': {'data': {'license': {'pd_id': 'pd_id'}}},
        },
        drivers_licenses={'pd_id': {'id': 'pd_id', 'license': '12AB345678'}},
        replication_contracts=load_json('replication_contracts.json'),
    )
    setattr(
        context.config,
        'BILLING_SUBVENTIONS_PAYMENTS_LIMITS',
        {
            'subvention': {'min_value': '10', 'max_value': '200'},
            'commission/driver_fix': {'min_value': '10', 'max_value': '200'},
        },
    )
    with pytest.raises(process_doc.AmountOutOfLimitError):
        await process_doc.stq_task.task(
            context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
        )


@pytest.mark.filldb(
    commission_contracts='for_test_process_shift_ended',
    subvention_rules='for_test_process_shift_ended',
    personal_subvention_rules='for_test_process_shift_ended',
    parks='for_test_process_shift_ended',
    cities='for_test_process_shift_ended',
    currency_rates='for_test_process_shift_ended',
)
@pytest.mark.now('2018-05-12T05:00:00+03:00')
@pytest.mark.parametrize(
    'doc_json, expected_docs_json, '
    'expected_entities_json, expected_accounts_json',
    [
        (
            'driver_fix_shift_ended_doc.json',
            'expected_driver_fix_docs.json',
            'expected_driver_fix_entities.json',
            'expected_empty_accounts.json',
        ),
    ],
)
async def test_process_shift_ended_if_empty_balances(
        doc_json,
        expected_docs_json,
        expected_entities_json,
        expected_accounts_json,
        *,
        db,
        monkeypatch,
        load_json,
        patch,
):
    # pylint: disable=too-many-arguments,too-many-locals,invalid-name
    _patch_random(patch)
    _patch_uuid(patch)
    _turn_on_commissions(monkeypatch)
    _turn_on_antifraud_processing(monkeypatch)
    _turn_on_create_subventions_input(monkeypatch)
    _fill_tlog_service_ids(monkeypatch)

    doc = load_json(doc_json)
    expected_docs = load_json(expected_docs_json)
    expected_entities = load_json(expected_entities_json)
    expected_accounts = load_json(expected_accounts_json)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        db=db,
        balances={},
        existing_docs=[],
        new_billing_migration=_ENABLED_BILLING_EVERYWHERE,
        drivers_profiles={
            'db_id_uuid': {'data': {'license': {'pd_id': 'pd_id'}}},
        },
        drivers_licenses={'pd_id': {'id': 'pd_id', 'license': '12AB345678'}},
        replication_contracts=[],
    )
    setattr(
        context.config,
        'BILLING_SUBVENTIONS_PAYMENTS_LIMITS',
        {
            'subvention': {'min_value': '10', 'max_value': '200'},
            'commission/driver_fix': {'min_value': '10', 'max_value': '200'},
        },
    )
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
    )
    _assert_docs_equal(
        expected_docs=expected_docs,
        actual_docs=context.docs_client.created_docs,
    )
    assert context.accounts_client.created_accounts == expected_accounts
    assert context.accounts_client.created_entities == expected_entities


@pytest.mark.filldb(
    subvention_rules='for_test_process_shift_ended',
    parks='for_test_process_shift_ended',
    cities='for_test_process_shift_ended',
)
async def test_b2b_driver_fix_crashes_when_income_is_not_zero(
        load_json, load_py_json, db,
):
    doc = load_json('b2b_driver_fix_shift_ended_doc.json')
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        db=db,
        balances=_build_balances(
            num_goal_orders=0,
            version=7,
            agreement_ref=doc['data']['agreement_ref'],
        ),
        journal_entries=load_py_json('b2b_driver_fix_journal_entries.json'),
        drivers_profiles={
            'db_id_uuid': {'data': {'license': {'pd_id': 'pd_id'}}},
        },
        drivers_licenses={'pd_id': {'id': 'pd_id', 'license': '12AB345678'}},
    )
    with pytest.raises(AssertionError) as err:
        await process_doc.stq_task.task(
            context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
        )
    assert str(err.value) == 'Income must be zero'


@pytest.mark.now('2019-02-27T09:28:04')
@pytest.mark.parametrize(
    'test_data_json',
    [
        'block_two.json',
        'noop_second_block.json',
        'pay_two.json',
        'noop_second_pay.json',
    ],
)
@pytest.mark.filldb(
    dry_holded_subventions='for_test_process_pay_or_block_holded_subventions',
)
async def test_process_pay_or_block_holded_subventions(
        test_data_json, db, load_py_json,
):
    # pylint: disable=invalid-name
    test_data = load_py_json(test_data_json)
    context = ContextData(
        doc=test_data['doc'],
        rules=[],
        zones=_build_zones(),
        db=db,
        balances={},
    )
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=666,
    )
    expected_holded_subventions = test_data['expected_holded_subventions']
    actual_holded_subventions = await _find_actual_holded_subvention(
        db, test_data['doc']['data']['ref']['billing_v2_id'],
    )
    assert expected_holded_subventions == actual_holded_subventions


@pytest.mark.now('2019-02-27T09:28:04')
@pytest.mark.parametrize(
    'doc_json, rules_json, personal_rules_json, balances_json, '
    'replication_contracts_json, configs, '
    'expected_entities_json, expected_accounts_json, expected_docs_json, '
    'expected_commission_journal_json, expected_orders_docs_json, '
    'expected_stq_calls, billing_commissions_response,'
    'expected_order_status',
    [
        (
            'completed/order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
            ),
            'completed/expected_entities.json',
            'completed/expected_accounts.json',
            'completed/expected_docs.json',
            'completed/expected_commission_journal.json',
            'completed/expected_orders_docs.json',
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            'billing_commissions_responses/completed.json',
            'normal',
        ),
        (  # software subscription
            # Замечание: при работе этого теста fallback_to_mongo
            # срабатывает на монгу.
            # Так как ответ сервиса содержит на одну комиссию больше.
            'completed_software_subscription/order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
            ),
            'completed_software_subscription/expected_entities.json',
            'completed_software_subscription/expected_accounts.json',
            'completed_software_subscription/expected_docs.json',
            'completed_software_subscription/expected_commission_journal.json',
            'completed_software_subscription/expected_orders_docs.json',
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            (
                'billing_commissions_responses/'
                'completed_software_subscription.json'
            ),
            'normal',
        ),  # end software subscription
        (  # software subscription (park only)
            # Замечание: при работе этого теста fallback_to_mongo
            # срабатывает на монгу.
            # Так как ответ сервиса содержит на одну комиссию больше.
            (
                'completed_software_subscription_park_only/'
                'order_ready_for_billing_doc.json'
            ),
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
            ),
            'completed_software_subscription_park_only/expected_entities.json',
            'completed_software_subscription_park_only/expected_accounts.json',
            'completed_software_subscription_park_only/expected_docs.json',
            (
                'completed_software_subscription_park_only/'
                'expected_commission_journal.json'
            ),
            (
                'completed_software_subscription_park_only/'
                'expected_orders_docs.json'
            ),
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            (
                'billing_commissions_responses/'
                'completed_software_subscription_park_only.json'
            ),
            'normal',
        ),  # end software subscription (park only)
        (  # completed_custom_category_commission
            # Замечание: при работе этого теста fallback_to_mongo
            # срабатывает на монгу.
            # Так как ответ сервиса содержит на несколько комиссий больше
            (
                'completed_custom_category_commission/'
                'order_ready_for_billing_doc.json'
            ),
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
            ),
            'completed_custom_category_commission/expected_entities.json',
            'completed_custom_category_commission/expected_accounts.json',
            'completed_custom_category_commission/expected_docs.json',
            (
                'completed_custom_category_commission/'
                'expected_commission_journal.json'
            ),
            (
                'completed_custom_category_commission/'
                'expected_orders_docs.json'
            ),
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            (
                'billing_commissions_responses/'
                'completed_custom_category_commission.json'
            ),
            'normal',
        ),  # end completed_custom_category_commission
        (
            'completed_with_zero_cost/order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
            ),
            'completed_with_zero_cost/expected_entities.json',
            'completed_with_zero_cost/expected_accounts.json',
            'completed_with_zero_cost/expected_docs.json',
            'completed_with_zero_cost/expected_commission_journal.json',
            'completed_with_zero_cost/expected_orders_docs.json',
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            'billing_commissions_responses/completed.json',
            'normal',
        ),
        (
            (
                'completed_with_zero_cost_and_commission/'
                'order_ready_for_billing_doc.json'
            ),
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
            ),
            (
                'completed_with_zero_cost_and_commission/'
                'expected_entities.json'
            ),
            (
                'completed_with_zero_cost_and_commission/'
                'expected_accounts.json'
            ),
            'completed_with_zero_cost_and_commission/expected_docs.json',
            (
                'completed_with_zero_cost_and_commission/'
                'expected_commission_journal.json'
            ),
            (
                'completed_with_zero_cost_and_commission/'
                'expected_orders_docs.json'
            ),
            [('billing_consume_commission_events', 'doc_id/2')],
            'billing_commissions_responses/expired.json',
            'expired',
        ),
        (
            (
                'completed_with_zero_cost_and_commission/'
                'order_ready_for_billing_doc.json'
            ),
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
                BILLING_SUBVENTIONS_CALC_EXPIRED_STATUS_MODE=dict(
                    mode='fallback',
                    due_restriction='2099-01-01T00:00:00+00:00',
                ),
                BILLING_SUBVENTIONS_CALC_COST_FOR_COMMISSION_BEFORE_USE=dict(
                    mode='from_orfb',
                    due_restriction='1999-12-01T00:00:00+00:00',
                ),
            ),
            (
                'completed_with_zero_cost_and_commission/'
                'expected_entities.json'
            ),
            (
                'completed_with_zero_cost_and_commission/'
                'expected_accounts.json'
            ),
            'completed_with_zero_cost_and_commission/expected_docs.json',
            (
                'completed_with_zero_cost_and_commission/'
                'expected_commission_journal.json'
            ),
            (
                'completed_with_zero_cost_and_commission/'
                'expected_orders_docs.json'
            ),
            [('billing_consume_commission_events', 'doc_id/2')],
            'billing_commissions_responses/expired.json',
            'expired',
        ),
        (  # zero cost but normal order
            (
                'completed_with_zero_cost_and_commission_new_expired_flow/'
                'order_ready_for_billing_doc.json'
            ),
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
                BILLING_SUBVENTIONS_CALC_EXPIRED_STATUS_MODE={
                    'mode': 'from_status',
                    'due_restriction': '1999-01-01T00:00:00+00:00',
                },
            ),
            (
                'completed_with_zero_cost_and_commission_new_expired_flow/'
                'expected_entities.json'
            ),
            (
                'completed_with_zero_cost_and_commission_new_expired_flow/'
                'expected_accounts.json'
            ),
            (
                'completed_with_zero_cost_and_commission_new_expired_flow/'
                'expected_docs.json'
            ),
            (
                'completed_with_zero_cost_and_commission_new_expired_flow/'
                'expected_commission_journal.json'
            ),
            (
                'completed_with_zero_cost_and_commission_new_expired_flow/'
                'expected_orders_docs.json'
            ),
            [('billing_consume_commission_events', 'doc_id/2')],
            'billing_commissions_responses/completed.json',
            'normal',
        ),
        (  # zero cost but normal order is calculated as expired (too old)
            (
                'completed_with_zero_cost_and_commission_'
                'new_expired_flow_too_old/order_ready_for_billing_doc.json'
            ),
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
                BILLING_SUBVENTIONS_CALC_EXPIRED_STATUS_MODE={
                    'mode': 'from_status',
                    'due_restriction': '2099-01-01T00:00:00+00:00',
                },
            ),
            (
                'completed_with_zero_cost_and_commission_'
                'new_expired_flow_too_old/expected_entities.json'
            ),
            (
                'completed_with_zero_cost_and_commission_'
                'new_expired_flow_too_old/expected_accounts.json'
            ),
            (
                'completed_with_zero_cost_and_commission_'
                'new_expired_flow_too_old/expected_docs.json'
            ),
            (
                'completed_with_zero_cost_and_commission_'
                'new_expired_flow_too_old/expected_commission_journal.json'
            ),
            (
                'completed_with_zero_cost_and_commission_'
                'new_expired_flow_too_old/expected_orders_docs.json'
            ),
            [('billing_consume_commission_events', 'doc_id/2')],
            'billing_commissions_responses/expired.json',
            'expired',
        ),
        (  # zero cost but expired order
            (
                'expired_with_zero_cost_and_commission_new_expired_flow/'
                'order_ready_for_billing_doc.json'
            ),
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
                BILLING_SUBVENTIONS_CALC_EXPIRED_STATUS_MODE={
                    'mode': 'from_status',
                    'due_restriction': '1999-01-01T00:00:00+00:00',
                },
            ),
            (
                'expired_with_zero_cost_and_commission_new_expired_flow/'
                'expected_entities.json'
            ),
            (
                'expired_with_zero_cost_and_commission_new_expired_flow/'
                'expected_accounts.json'
            ),
            (
                'expired_with_zero_cost_and_commission_new_expired_flow/'
                'expected_docs.json'
            ),
            (
                'expired_with_zero_cost_and_commission_new_expired_flow/'
                'expected_commission_journal.json'
            ),
            (
                'expired_with_zero_cost_and_commission_new_expired_flow/'
                'expected_orders_docs.json'
            ),
            [('billing_consume_commission_events', 'doc_id/2')],
            'billing_commissions_responses/expired.json',
            'expired',
        ),
        (
            'completed/order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
            ),
            'completed/expected_entities.json',
            'completed/expected_accounts.json',
            'completed/expected_docs.json',
            'completed/expected_commission_journal.json',
            'completed/expected_orders_docs.json',
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            'billing_commissions_responses/completed.json',
            'normal',
        ),
        (
            'completed_with_workshift/order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
            ),
            'completed_with_workshift/expected_entities.json',
            'completed_with_workshift/expected_accounts.json',
            'completed_with_workshift/expected_docs.json',
            'completed_with_workshift/expected_commission_journal.json',
            'completed_with_workshift/expected_orders_docs.json',
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            'billing_commissions_responses/completed.json',
            'normal',
        ),
        (
            'completed_with_workshift/order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
            ),
            'completed_with_workshift/expected_entities.json',
            'completed_with_workshift/expected_accounts.json',
            'completed_with_workshift/expected_docs.json',
            'completed_with_workshift/expected_commission_journal.json',
            'completed_with_workshift/expected_orders_docs.json',
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            'billing_commissions_responses/completed.json',
            'normal',
        ),
        (
            'hiring/order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=False,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=False,
            ),
            'hiring/expected_entities.json',
            'hiring/expected_accounts.json',
            'hiring/expected_docs.json',
            'hiring/expected_commission_journal.json',
            'hiring/expected_orders_docs.json',
            [('billing_consume_commission_events', 'doc_id/2')],
            'billing_commissions_responses/hiring.json',
            'normal',
        ),
        (
            'hiring_with_rent/order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=False,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=False,
            ),
            'hiring_with_rent/expected_entities.json',
            'hiring_with_rent/expected_accounts.json',
            'hiring_with_rent/expected_docs.json',
            'hiring_with_rent/expected_commission_journal.json',
            'hiring_with_rent/expected_orders_docs.json',
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            'billing_commissions_responses/hiring_with_rent.json',
            'normal',
        ),
        (
            'cancelled/order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
            ),
            'cancelled/expected_entities.json',
            'cancelled/expected_accounts.json',
            'cancelled/expected_docs.json',
            'cancelled/expected_commission_journal.json',
            'cancelled/expected_orders_docs.json',
            [('billing_consume_commission_events', 'doc_id/2')],
            'billing_commissions_responses/cancelled.json',
            'normal',
        ),
        (
            'cancelled_by_dispatcher/order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
            ),
            'cancelled_by_dispatcher/expected_entities.json',
            'cancelled_by_dispatcher/expected_accounts.json',
            'cancelled_by_dispatcher/expected_docs.json',
            'cancelled_by_dispatcher/expected_commission_journal.json',
            'cancelled_by_dispatcher/expected_orders_docs.json',
            [('billing_consume_commission_events', 'doc_id/2')],
            'billing_commissions_responses/cancelled_by_dispatcher.json',
            'cancel',
        ),
        (
            'mqc/order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=False,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
            ),
            'mqc/expected_entities.json',
            'mqc/expected_accounts.json',
            'mqc/expected_docs.json',
            'mqc/expected_commission_journal.json',
            'mqc/expected_orders_docs.json',
            [],
            'billing_commissions_responses/mqc.json',
            'normal',
        ),
        (
            'rebate/order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts_rebate.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=False,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=False,
            ),
            'rebate/expected_entities.json',
            'rebate/expected_accounts.json',
            'rebate/expected_docs.json',
            'rebate/expected_commission_journal.json',
            'rebate/expected_orders_docs.json',
            [('billing_consume_commission_events', 'doc_id/2')],
            'billing_commissions_responses/rebate.json',
            'normal',
        ),
        (
            'rebate_cancelled/order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts_rebate.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=False,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=False,
            ),
            'rebate_cancelled/expected_entities.json',
            'rebate_cancelled/expected_accounts.json',
            'rebate_cancelled/expected_docs.json',
            'rebate_cancelled/expected_commission_journal.json',
            'rebate_cancelled/expected_orders_docs.json',
            [('billing_consume_commission_events', 'doc_id/2')],
            'billing_commissions_responses/rebate_cancelled.json',
            'cancel',
        ),
        (  # old flow
            'rebate_cancelled_by_dispatcher/order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts_rebate.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=False,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=False,
            ),
            'rebate_cancelled_by_dispatcher/expected_entities.json',
            'rebate_cancelled_by_dispatcher/expected_accounts.json',
            'rebate_cancelled_by_dispatcher/expected_docs.json',
            'rebate_cancelled_by_dispatcher/expected_commission_journal.json',
            'rebate_cancelled_by_dispatcher/expected_orders_docs.json',
            [('billing_consume_commission_events', 'doc_id/2')],
            (
                'billing_commissions_responses/rebate_'
                'cancelled_by_dispatcher.json'
            ),
            'cancel',
        ),
        (
            'bel/order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts_bel.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=False,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=False,
            ),
            'bel/expected_entities.json',
            'bel/expected_accounts.json',
            'bel/expected_docs.json',
            'bel/expected_commission_journal.json',
            'bel/expected_orders_docs.json',
            [('billing_consume_commission_events', 'doc_id/2')],
            'billing_commissions_responses/bel.json',
            'normal',
        ),
        (
            'completed/order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
                BILLING_SUBVENTIONS_STOP_WRITE_TO_PY2_COLLECTIONS={
                    '__default__': '2019-02-01T00:00:00.000000+00:00',
                },
            ),
            'completed/expected_entities.json',
            'completed/expected_accounts.json',
            'completed/expected_docs_stop_write_py2_col.json',
            'completed/expected_commission_journal.json',
            'completed/expected_orders_docs.json',
            [],  # no stq tasks
            'billing_commissions_responses/completed.json',
            'normal',
        ),
        (
            'hiring_returned/order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=False,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=False,
            ),
            'hiring_returned/expected_entities.json',
            'hiring_returned/expected_accounts.json',
            'hiring_returned/expected_docs.json',
            'hiring_returned/expected_commission_journal.json',
            'hiring_returned/expected_orders_docs.json',
            [('billing_consume_commission_events', 'doc_id/2')],
            'billing_commissions_responses/hiring_returned.json',
            'normal',
        ),
        (
            'completed_fine/order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
            ),
            'completed_fine/expected_entities.json',
            'completed_fine/expected_accounts.json',
            'completed_fine/expected_docs.json',
            'completed_fine/expected_commission_journal.json',
            'completed_fine/expected_orders_docs.json',
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            'billing_commissions_responses/completed_fine.json',
            'normal',
        ),
        (  # cost not zero paid cancel
            'cancelled_paid/order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
            ),
            'cancelled_paid/expected_entities.json',
            'cancelled_paid/expected_accounts.json',
            'cancelled_paid/expected_docs.json',
            'cancelled_paid/expected_commission_journal.json',
            'cancelled_paid/expected_orders_docs.json',
            [('billing_consume_commission_events', 'doc_id/2')],
            'billing_commissions_responses/cancelled.json',
            'normal',
        ),
        (  # cost is zero paid cancel
            (
                'cancelled_minimal_tariff_cost_old/'
                'order_ready_for_billing_doc.json'
            ),
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
            ),
            'cancelled_minimal_tariff_cost_old/expected_entities.json',
            'cancelled_minimal_tariff_cost_old/expected_accounts.json',
            'cancelled_minimal_tariff_cost_old/expected_docs.json',
            (
                'cancelled_minimal_tariff_cost_old/'
                'expected_commission_journal.json'
            ),
            'cancelled_minimal_tariff_cost_old/expected_orders_docs.json',
            [('billing_consume_commission_events', 'doc_id/2')],
            'billing_commissions_responses/cancelled_cancel.json',
            'cancel',
        ),
        (  # cost is zero paid cancel and calc cost_details before using
            (
                'cancelled_minimal_tariff_cost_new/'
                'order_ready_for_billing_doc.json'
            ),
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
                BILLING_SUBVENTIONS_CALC_COST_FOR_COMMISSION_BEFORE_USE=dict(
                    mode='from_calc',
                    due_restriction='1999-12-01T00:00:00+00:00',
                ),
            ),
            'cancelled_minimal_tariff_cost_new/expected_entities.json',
            'cancelled_minimal_tariff_cost_new/expected_accounts.json',
            'cancelled_minimal_tariff_cost_new/expected_docs.json',
            (
                'cancelled_minimal_tariff_cost_new/'
                'expected_commission_journal.json'
            ),
            'cancelled_minimal_tariff_cost_new/expected_orders_docs.json',
            [('billing_consume_commission_events', 'doc_id/2')],
            'billing_commissions_responses/cancelled_cancel.json',
            'cancel',
        ),
        (  # цена 0, платная отмена, толко сверяем cost_details
            (
                'cancelled_minimal_tariff_cost_fallback/'
                'order_ready_for_billing_doc.json'
            ),
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
                BILLING_SUBVENTIONS_CALC_COST_FOR_COMMISSION_BEFORE_USE=dict(
                    mode='fallback',
                    due_restriction='1999-12-01T00:00:00+00:00',
                ),
            ),
            'cancelled_minimal_tariff_cost_fallback/expected_entities.json',
            'cancelled_minimal_tariff_cost_fallback/expected_accounts.json',
            'cancelled_minimal_tariff_cost_fallback/expected_docs.json',
            (
                'cancelled_minimal_tariff_cost_fallback/'
                'expected_commission_journal.json'
            ),
            'cancelled_minimal_tariff_cost_fallback/expected_orders_docs.json',
            [('billing_consume_commission_events', 'doc_id/2')],
            'billing_commissions_responses/cancelled_cancel.json',
            'cancel',
        ),
        (  # цена 0, платная отмена, due не подходит для новго флоу
            (
                'cancelled_minimal_tariff_cost_fallback/'
                'order_ready_for_billing_doc.json'
            ),
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'replication_contracts.json',
            dict(
                BILLING_WRITE_ONLY_USEFUL_JOURNAL_ENTRIES=True,
                BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO=True,
                BILLING_SUBVENTIONS_CALC_COST_FOR_COMMISSION_BEFORE_USE=dict(
                    mode='from_calc',
                    due_restriction='2099-12-01T00:00:00+00:00',
                ),
            ),
            'cancelled_minimal_tariff_cost_fallback/expected_entities.json',
            'cancelled_minimal_tariff_cost_fallback/expected_accounts.json',
            'cancelled_minimal_tariff_cost_fallback/expected_docs.json',
            (
                'cancelled_minimal_tariff_cost_fallback/'
                'expected_commission_journal.json'
            ),
            'cancelled_minimal_tariff_cost_fallback/expected_orders_docs.json',
            [('billing_consume_commission_events', 'doc_id/2')],
            'billing_commissions_responses/cancelled_cancel.json',
            'cancel',
        ),
    ],
)
@pytest.mark.filldb(
    currency_rates='for_test_stq_task_create_commission_journal',
    parks='for_test_stq_task_create_commission_journal',
    cities='for_test_process_doc',
)
@pytest.mark.config(
    BILLING_SUBVENTIONS_USE_BILLING_COMMISSIONS={
        'default_for_all': 'full_usage',
    },
)
# pylint: disable=invalid-name,too-many-arguments,too-many-locals
async def test_stq_task_create_commission_journal(
        patch,
        monkeypatch,
        doc_json,
        rules_json,
        personal_rules_json,
        balances_json,
        replication_contracts_json,
        expected_entities_json,
        expected_accounts_json,
        expected_docs_json,
        expected_commission_journal_json,
        expected_orders_docs_json,
        expected_stq_calls,
        load_json,
        db,
        load_py_json_dir,
        billing_commissions_response,
        configs,
        expected_order_status,
):
    commission_response = load_py_json_dir(
        'test_stq_task_create_commission_journal',
        billing_commissions_response,
    )
    _set_billing_commissions_level(monkeypatch, 'full_usage')
    _set_process_commission(monkeypatch, True)
    _set_commission_substitutions(monkeypatch)
    _turn_on_create_childseat_rented_doc(monkeypatch)
    _turn_on_create_commission_transactions_doc(monkeypatch)
    _turn_on_pay_out_childseat(monkeypatch)
    _turn_on_create_order_commission_changed_for_order(monkeypatch)
    _fill_tlog_service_ids(monkeypatch)
    _fill_arbitrary_configs(monkeypatch, configs)

    doc = load_json(doc_json)
    expected_entities = load_json(expected_entities_json)
    expected_accounts = load_json(expected_accounts_json)
    expected_docs = load_json(expected_docs_json)
    expected_commission_journal = load_json(expected_commission_journal_json)
    expected_docs.append(expected_commission_journal)
    expected_orders_docs = load_json(expected_orders_docs_json)
    await _patch_database_calls(
        'test_stq_task_create_commission_journal',
        patch,
        load_py_json_dir,
        rules_json,
        personal_rules_json,
    )
    await _patch_get_balances(
        'test_stq_task_create_commission_journal',
        patch,
        load_py_json_dir,
        balances_json,
    )
    _patch_order_commission_enabled_check(patch)
    replication_contracts = load_json(replication_contracts_json)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        db=db,
        existing_docs=[doc],
        balances={},
        replication_contracts_usage='enable',
        replication_contracts=replication_contracts,
    )
    context.commissions_client.add_response(
        commission_response, expected_order_status,
    )
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
    )
    created_docs = context.docs_client.created_docs
    for doc in created_docs:
        if 'tags' in doc['data']:
            doc['data']['tags'] = sorted(doc['data']['tags'])
    _assert_docs_equal(
        expected_docs=_sorted_docs(expected_docs),
        actual_docs=_sorted_docs(created_docs),
    )
    assert expected_orders_docs == context.orders_client.created_docs
    assert expected_accounts == context.accounts_client.created_accounts
    assert expected_entities == context.accounts_client.created_entities
    stq_calls = _get_stq_calls_with_task_ids(context.stq_agent.calls)
    assert stq_calls == expected_stq_calls


@pytest.mark.now('2019-02-27T09:28:04')
@pytest.mark.parametrize(
    'doc_json, '
    'replication_contracts_json, '
    'configs,'
    'billing_commissions_response, '
    'expected_entities_json,'
    'expected_accounts_json, '
    'expected_docs_json, '
    'expected_orders_docs_json, '
    'expected_stq_calls',
    [
        pytest.param(
            'order_ready_for_billing_doc.json',
            'replication_contracts.json',
            {**_ENABLED_BILLING_COMMISSIONS_CFG},
            'bc_response.json',
            'expected_entities.json',
            'expected_accounts.json',
            'py2_flow/expected_docs.json',
            'py2_flow/expected_orders_docs.json',
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            id='0',
        ),
        pytest.param(
            'order_ready_for_billing_doc.json',
            'replication_contracts.json',
            {**_ENABLED_PAYOUT_CFG, **_ENABLED_BILLING_COMMISSIONS_CFG},
            'bc_response.json',
            'expected_entities.json',
            'expected_accounts.json',
            'payout_flow/expected_docs.json',
            'payout_flow/expected_orders_docs.json',
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            id='1',
        ),
        pytest.param(
            'order_ready_for_billing_doc_cargo.json',
            'replication_contracts.json',
            {**_ENABLED_PAYOUT_CFG, **_ENABLED_BILLING_COMMISSIONS_CFG},
            'bc_response_software_subscription.json',
            'expected_entities.json',
            'expected_accounts_with_billing_commissions.json',
            'payout_flow/expected_docs_with_billing_commissions.json',
            (
                'payout_flow/expected_orders_docs_with_billing_commissions_'
                'cargo.json'
            ),
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            id='cargo_order',
        ),
        pytest.param(
            'order_ready_for_billing_doc.json',
            'replication_contracts.json',
            {**_ENABLED_PAYOUT_CFG, **_ENABLED_BILLING_COMMISSIONS_CFG},
            'bc_response_software_subscription.json',
            'expected_entities.json',
            'expected_accounts_with_billing_commissions.json',
            'payout_flow/expected_docs_with_billing_commissions.json',
            'payout_flow/expected_orders_docs_with_billing_commissions.json',
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            id='2',
        ),
        pytest.param(
            'order_ready_for_billing_doc_hiring.json',
            'replication_contracts.json',
            {**_ENABLED_PAYOUT_CFG, **_ENABLED_BILLING_COMMISSIONS_CFG},
            'bc_response_hiring.json',
            'expected_entities.json',
            'expected_accounts_with_billing_commissions_hiring.json',
            'payout_flow/expected_docs_with_billing_commissions_hiring.json',
            (
                'payout_flow/expected_orders_docs_with_billing_commissions_'
                'hiring.json'
            ),
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            id='3',
        ),
        pytest.param(
            'order_ready_for_billing_doc_corp.json',
            'replication_contracts_two_not_finished.json',
            {**_ENABLED_PAYOUT_CFG, **_ENABLED_BILLING_COMMISSIONS_CFG},
            'bc_response.json',
            'expected_entities.json',
            'payout_flow/expected_accounts_corp_order.json',
            'payout_flow/expected_docs_corp_order.json',
            'payout_flow/expected_orders_docs_corp_order.json',
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            id='4',
        ),
        pytest.param(
            'order_ready_for_billing_doc_no_billing_client_id.json',
            'replication_contracts_no_billing_client_id.json',
            {**_ENABLED_PAYOUT_CFG, **_ENABLED_BILLING_COMMISSIONS_CFG},
            'bc_response.json',
            'expected_entities.json',
            'expected_accounts_no_billing_client_id.json',
            'payout_flow/expected_docs_no_billing_client_id.json',
            'payout_flow/expected_orders_docs_no_billing_client_id.json',
            [('billing_consume_commission_events', 'doc_id/2')],
            id='5',
        ),
        pytest.param(
            'take_park_b2b_fixed_commission_with_park_ids.json',
            'replication_contracts_b2b_fixed_commission.json',
            {**_ENABLED_PAYOUT_CFG, **_ENABLED_BILLING_COMMISSIONS_CFG},
            None,
            'expected_entities_b2b_fixed_commission.json',
            'expected_accounts_b2b_fixed_commission.json',
            'payout_flow/expected_docs_b2b_fixed_commission.json',
            (
                'payout_flow/expected_orders_docs_b2b_fixed_commission_'
                'park_ids_from_input_doc.json'
            ),
            [],
            id='6',
        ),
        pytest.param(
            'order_ready_for_billing_doc.json',
            'replication_contracts.json',
            {**_ENABLED_PAYOUT_CFG, **_ENABLED_BILLING_COMMISSIONS_CFG},
            (
                'bc_response_software_subscription_and_reposition_'
                'vat_included.json'
            ),
            'expected_entities.json',
            (
                'expected_accounts_with_billing_commissions_'
                'with_reposition_vat_included.json'
            ),
            (
                'payout_flow/expected_docs_with_billing_commissions_'
                'and_reposition_vat_included.json'
            ),
            (
                'payout_flow/expected_orders_docs_with_billing_commissions'
                '_and_reposition_vat_included.json'
            ),
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            id='commission_vat_and_amount_on_same_accounts',
        ),
        pytest.param(
            'order_ready_for_billing_doc_promocode.json',
            'replication_contracts.json',
            {**_ENABLED_PAYOUT_CFG, **_ENABLED_BILLING_COMMISSIONS_CFG},
            (
                'bc_response_software_subscription_and_reposition_'
                'vat_included.json'
            ),
            'expected_entities.json',
            'expected_accounts_billing_commissions_promocode.json',
            'payout_flow/expected_docs_billing_commissions_promocode.json',
            'payout_flow/'
            'expected_orders_docs_billing_commissions_promocode.json',
            [('billing_consume_commission_events', 'doc_id/2')],
            id='billing commissions if promocode',
        ),
        pytest.param(
            'order_ready_for_billing_doc_promocode.json',
            'replication_contracts.json',
            {
                **_ENABLED_PAYOUT_CFG,
                **_ENABLED_BILLING_COMMISSIONS_CFG,
                'BILLING_COMMISSIONS_IGNORE_DRIVER_PROMOCODE': {
                    'categories': ['reposition'],
                },
            },
            (
                'bc_response_software_subscription_and_reposition_'
                'vat_included.json'
            ),
            'expected_entities.json',
            'expected_accounts_billing_commissions_ignored_promocode.json',
            (
                'payout_flow/'
                'expected_docs_billing_commissions_ignored_promocode.json'
            ),
            (
                'payout_flow/expected_orders_'
                'docs_billing_commissions_ignored_promocode.json'
            ),
            [('billing_consume_commission_events', 'doc_id/2')],
            id='billing commissions if ignored promocode',
        ),
        pytest.param(
            'order_ready_for_billing_doc_shift.json',
            'replication_contracts.json',
            {**_ENABLED_PAYOUT_CFG, **_ENABLED_BILLING_COMMISSIONS_CFG},
            (
                'bc_response_software_subscription_and_reposition_'
                'vat_included.json'
            ),
            'expected_entities.json',
            'expected_accounts_billing_commissions_shift.json',
            'payout_flow/expected_docs_billing_commissions_shift.json',
            'payout_flow/expected_orders_docs_billing_commissions_shift.json',
            [('billing_consume_commission_events', 'doc_id/2')],
            id='billing commissions if shift',
        ),
        pytest.param(
            'order_ready_for_billing_doc_shift.json',
            'replication_contracts.json',
            {
                **_ENABLED_PAYOUT_CFG,
                **_ENABLED_BILLING_COMMISSIONS_CFG,
                'BILLING_COMMISSIONS_IGNORE_DRIVER_SHIFT': {
                    'categories': ['reposition'],
                },
            },
            (
                'bc_response_software_subscription_and_reposition_'
                'vat_included.json'
            ),
            'expected_entities.json',
            'expected_accounts_billing_commissions_ignored_shift.json',
            'payout_flow/expected_docs_billing_commissions_ignored_shift.json',
            (
                'payout_flow/'
                'expected_orders_docs_billing_commissions_ignored_shift.json'
            ),
            [('billing_consume_commission_events', 'doc_id/2')],
            id='billing commissions if ignored shift',
        ),
        pytest.param(
            'order_ready_for_billing_doc_promocode_and_shift.json',
            'replication_contracts.json',
            {**_ENABLED_PAYOUT_CFG, **_ENABLED_BILLING_COMMISSIONS_CFG},
            (
                'bc_response_software_subscription_and_reposition_'
                'vat_included.json'
            ),
            'expected_entities.json',
            'expected_accounts_billing_commissions_promocode_and_shift.json',
            (
                'payout_flow/'
                'expected_docs_billing_commissions_promocode_and_shift.json'
            ),
            (
                'payout_flow/expected_orders_docs_billing_commissions'
                '_promocode_and_shift.json'
            ),
            [('billing_consume_commission_events', 'doc_id/2')],
            id='billing commissions if shift and promocode',
        ),
        pytest.param(
            'order_ready_for_billing_doc_promocode_and_shift.json',
            'replication_contracts.json',
            {
                **_ENABLED_PAYOUT_CFG,
                **_ENABLED_BILLING_COMMISSIONS_CFG,
                'BILLING_COMMISSIONS_IGNORE_DRIVER_SHIFT': {
                    'categories': ['reposition'],
                },
            },
            (
                'bc_response_software_subscription_and_reposition_'
                'vat_included.json'
            ),
            'expected_entities.json',
            (
                'expected_accounts_billing_commissions_promocode_'
                'and_ignored_shift.json'
            ),
            (
                'payout_flow/expected_docs_billing_commissions_promocode_'
                'and_ignored_shift.json'
            ),
            (
                'payout_flow/expected_orders_docs_billing_commissions_'
                'promocode_and_ignored_shift.json'
            ),
            [('billing_consume_commission_events', 'doc_id/2')],
            id='billing commissions if ignored shift and promocode',
        ),
        pytest.param(
            'order_ready_for_billing_doc_promocode_and_shift.json',
            'replication_contracts.json',
            {
                **_ENABLED_PAYOUT_CFG,
                **_ENABLED_BILLING_COMMISSIONS_CFG,
                'BILLING_COMMISSIONS_IGNORE_DRIVER_PROMOCODE': {
                    'categories': ['reposition'],
                },
            },
            (
                'bc_response_software_subscription_and_reposition_'
                'vat_included.json'
            ),
            'expected_entities.json',
            (
                'expected_accounts_billing_commissions_ignored_'
                'promocode_and_shift.json'
            ),
            (
                'payout_flow/expected_docs_billing_commissions_ignored_'
                'promocode_and_shift.json'
            ),
            (
                'payout_flow/expected_orders_docs_billing_commissions_'
                'ignored_promocode_and_shift.json'
            ),
            [('billing_consume_commission_events', 'doc_id/2')],
            id='billing commissions if shift and ignored promocode',
        ),
        pytest.param(
            'order_ready_for_billing_doc_promocode_and_shift.json',
            'replication_contracts.json',
            {
                **_ENABLED_PAYOUT_CFG,
                **_ENABLED_BILLING_COMMISSIONS_CFG,
                'BILLING_COMMISSIONS_IGNORE_DRIVER_PROMOCODE': {
                    'categories': ['reposition'],
                },
                'BILLING_COMMISSIONS_IGNORE_DRIVER_SHIFT': {
                    'categories': ['reposition'],
                },
            },
            (
                'bc_response_software_subscription_and_reposition_'
                'vat_included.json'
            ),
            'expected_entities.json',
            (
                'expected_accounts_billing_commissions_ignored_'
                'promocode_and_ignored_shift.json'
            ),
            (
                'payout_flow/expected_docs_billing_commissions_ignored'
                '_promocode_and_ignored_shift.json'
            ),
            (
                'payout_flow/expected_orders_docs_billing_commissions_'
                'ignored_promocode_and_ignored_shift.json'
            ),
            [('billing_consume_commission_events', 'doc_id/2')],
            id='billing commissions if ignored shift and ignored promocode',
        ),
        pytest.param(
            'order_ready_for_billing_doc.json',
            'replication_contracts.json',
            {**_ENABLED_PAYOUT_CFG, **_ENABLED_BILLING_COMMISSIONS_CFG},
            'bc_response_software_subscription_and_reposition.json',
            'expected_entities.json',
            'expected_accounts_with_billing_commissions_with_reposition.json',
            (
                'payout_flow/expected_docs_with_billing_commissions_'
                'and_reposition.json'
            ),
            (
                'payout_flow/expected_orders_docs_with_billing_commissions'
                '_and_reposition.json'
            ),
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            id='commission_vat_and_amount_on_different_accounts',
        ),
        pytest.param(
            'order_ready_for_billing_doc_support_promocode.json',
            'replication_contracts.json',
            {
                **_ENABLED_PAYOUT_CFG,
                **_ENABLED_BILLING_COMMISSIONS_CFG,
                'BILLING_SUBVENTIONS_DISTINGUISH_DRIVER_COUPONS': True,
            },
            (
                'bc_response_software_subscription_and_reposition_'
                'vat_included.json'
            ),
            'expected_entities.json',
            'expected_accounts_billing_commissions_promocode.json',
            'payout_flow/expected_docs_billing_commissions_promocode.json',
            'payout_flow/expected_orders_docs_billing_commissions_'
            'support_promocode.json',
            [('billing_consume_commission_events', 'doc_id/2')],
            id='distinguish driver coupon from support',
        ),
        pytest.param(
            'order_ready_for_billing_doc_marketing_promocode.json',
            'replication_contracts.json',
            {
                **_ENABLED_PAYOUT_CFG,
                **_ENABLED_BILLING_COMMISSIONS_CFG,
                'BILLING_SUBVENTIONS_DISTINGUISH_DRIVER_COUPONS': True,
            },
            (
                'bc_response_software_subscription_and_reposition_'
                'vat_included.json'
            ),
            'expected_entities.json',
            'expected_accounts_billing_commissions_promocode.json',
            'payout_flow/expected_docs_billing_commissions_promocode.json',
            'payout_flow/expected_orders_docs_billing_commissions_'
            'marketing_promocode.json',
            [('billing_consume_commission_events', 'doc_id/2')],
            id='distinguish driver coupon from marketing',
        ),
        pytest.param(
            'order_ready_for_billing_doc_hiring_returned.json',
            'replication_contracts.json',
            {
                **_ENABLED_PAYOUT_CFG,
                **_ENABLED_BILLING_COMMISSIONS_CFG,
                'BILLING_EYE_SAVE_COMMISSION_SUPPORT_INFO': True,
                'BILLING_SUBVENTIONS_COMMISSION_TEMPLATE_SUBSTITUTIONS': {
                    'hiring_map': {
                        'commercial_returned': 'returned_commercial',
                        'commercial_with_rent': 'with_rent_commercial',
                        'commercial': 'simple_commercial',
                    },
                    'hiring_sub_account': {
                        'commercial_returned': 'returned_commercial_sub',
                        'commercial_with_rent': 'with_rent_commercial_sub',
                        'commercial': 'simple_commercial_sub',
                    },
                },
            },
            'bc_response_hiring_returned.json',
            'expected_entities.json',
            'expected_accounts_with_billing_commissions_hiring_returned.json',
            'payout_flow/expected_docs_with_billing_commissions_hiring_'
            'returned.json',
            (
                'payout_flow/expected_orders_docs_with_billing_commissions_'
                'hiring_returned.json'
            ),
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            id='hiring_type_returned_driver',
        ),
        pytest.param(
            'order_ready_for_billing_doc.json',
            'replication_contracts.json',
            {
                **_ENABLED_PAYOUT_CFG,
                **_ENABLED_BILLING_COMMISSIONS_CFG,
                'BILLING_SUBVENTIONS_WRITE_OPTEUM_VAT_SINCE': (
                    '2019-02-27T02:42:00+03:00'
                ),
            },
            'bc_response_software_subscription.json',
            'expected_entities.json',
            'expected_accounts_with_billing_commissions.json',
            'payout_flow/expected_docs_with_billing_commissions.json',
            (
                'payout_flow/expected_orders_docs_with_billing_commissions'
                '_opteum_vat.json'
            ),
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            id='opteum_with_vat',
        ),
        pytest.param(
            'order_ready_for_billing_doc_corp_rebate.json',
            'replication_contracts_two_not_finished.json',
            {**_ENABLED_PAYOUT_CFG, **_ENABLED_BILLING_COMMISSIONS_CFG},
            'bc_response.json',
            'expected_entities.json',
            'payout_flow/expected_accounts_corp_rebate_order.json',
            'payout_flow/expected_docs_corp_rebate_order.json',
            'payout_flow/expected_orders_docs_corp_rebate_order.json',
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            id='corp_rebate_order',
        ),
        pytest.param(
            'order_ready_for_billing_doc_corp_rebate_cancelled_old_flow.json',
            'replication_contracts_two_not_finished.json',
            {**_ENABLED_PAYOUT_CFG, **_ENABLED_BILLING_COMMISSIONS_CFG},
            'bc_response.json',
            'expected_entities.json',
            (
                'payout_flow/expected_accounts_corp_rebate_cancelled_order_'
                'old_flow.json'
            ),
            (
                'payout_flow/expected_docs_corp_rebate_cancelled_order_'
                'old_flow.json'
            ),
            (
                'payout_flow/expected_orders_docs_corp_rebate_cancelled_order_'
                'old_flow.json'
            ),
            [('billing_consume_commission_events', 'doc_id/2')],
            id='corp_rebate_cancelled_order_old_flow_with_rebate_for_all',
        ),
        pytest.param(
            'order_ready_for_billing_doc_corp_rebate_cancelled.json',
            'replication_contracts_two_not_finished.json',
            {**_ENABLED_PAYOUT_CFG, **_ENABLED_BILLING_COMMISSIONS_CFG},
            'bc_response_cancelled.json',
            'expected_entities.json',
            'payout_flow/expected_accounts_corp_rebate_cancelled_order.json',
            'payout_flow/expected_docs_corp_rebate_cancelled_order.json',
            (
                'payout_flow/expected_orders_docs_corp_rebate_'
                'cancelled_order.json'
            ),
            [('billing_consume_commission_events', 'doc_id/2')],
            id='corp_rebate_cancelled_order',
        ),
        pytest.param(
            (
                'order_ready_for_billing_doc_corp_rebate_cancelled_'
                'paid_for_driver.json'
            ),
            'replication_contracts_two_not_finished.json',
            {**_ENABLED_PAYOUT_CFG, **_ENABLED_BILLING_COMMISSIONS_CFG},
            'bc_response.json',
            'expected_entities.json',
            (
                'payout_flow/expected_accounts_corp_rebate_cancelled'
                '_paid_for_driver_order.json'
            ),
            (
                'payout_flow/expected_docs_corp_rebate_cancelled'
                '_paid_for_driver_order.json'
            ),
            (
                'payout_flow/expected_orders_docs_corp_rebate_'
                'cancelled_paid_for_driver_order.json'
            ),
            [('billing_consume_commission_events', 'doc_id/2')],
            id='corp_rebate_cancelled_paid_for_driver_order',
        ),
        pytest.param(
            (
                'order_ready_for_billing_doc_corp_rebate_cancelled_'
                'by_dispatcher.json'
            ),
            'replication_contracts_two_not_finished.json',
            {**_ENABLED_PAYOUT_CFG, **_ENABLED_BILLING_COMMISSIONS_CFG},
            'bc_response_cancelled.json',
            'expected_entities.json',
            (
                'payout_flow/expected_accounts_corp_rebate_cancelled_'
                'by_dispatcher_order.json'
            ),
            (
                'payout_flow/expected_docs_corp_rebate_cancelled_'
                'by_dispatcher_order.json'
            ),
            (
                'payout_flow/expected_orders_docs_corp_rebate_cancelled_'
                'by_dispatcher_order.json'
            ),
            [('billing_consume_commission_events', 'doc_id/2')],
            id='corp_rebate_cancelled_order',
        ),
        pytest.param(
            'order_ready_for_billing_doc.json',
            'replication_contracts.json',
            {**_ENABLED_PAYOUT_CFG, **_ENABLED_BILLING_COMMISSIONS_CFG},
            'bc_response_fine.json',
            'expected_entities.json',
            'expected_accounts_with_billing_commissions_fine.json',
            'payout_flow/expected_docs_with_billing_commissions_fine.json',
            (
                'payout_flow/expected_orders_docs_'
                'with_billing_commissions_fine.json'
            ),
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            id='order_with_fine',
        ),
        pytest.param(
            'order_ready_for_billing_doc_hiring_bel.json',
            'replication_contracts.json',
            {**_ENABLED_PAYOUT_CFG, **_ENABLED_BILLING_COMMISSIONS_CFG},
            'bc_response_hiring.json',
            'expected_entities.json',
            'expected_accounts_with_billing_commissions_hiring_bel.json',
            (
                'payout_flow/expected_docs_with_billing_commissions_'
                'hiring_bel.json'
            ),
            (
                'payout_flow/expected_orders_docs_with_billing_commissions_'
                'hiring_bel.json'
            ),
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            id='hiring_bel_disabled',
        ),
        pytest.param(
            'order_ready_for_billing_doc_hiring_bel.json',
            'replication_contracts.json',
            {
                **_ENABLED_PAYOUT_CFG,
                **_ENABLED_BILLING_COMMISSIONS_CFG,
                'BILLING_SUBVENTIONS_WRITE_BEL_VAT_SINCE': (
                    '1999-01-01T00:00:00+00:00'
                ),
            },
            'bc_response_hiring.json',
            'expected_entities.json',
            'expected_accounts_with_billing_commissions_hiring_bel.json',
            (
                'payout_flow/expected_docs_with_billing_commissions_'
                'hiring_bel.json'
            ),
            (
                'payout_flow/expected_orders_docs_with_billing_commissions_'
                'hiring_bel_with_nds.json'
            ),
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            id='hiring_bel_enabled',
        ),
        pytest.param(
            'order_ready_for_billing_doc_with_park_commission.json',
            'replication_contracts.json',
            {
                **_ENABLED_PAYOUT_CFG,
                **_ENABLED_BILLING_COMMISSIONS_CFG,
                'BILLING_PARK_COMMISSION_CALCULATE_BY_KIND': {
                    '__default__': False,
                    'order_ready_for_billing': True,
                },
                'BILLING_PARK_COMMISSION_FLOW_BY_KIND': {
                    '__default__': {
                        '__default__': [
                            {
                                'start_date': '2099-01-01T00:00:00+00:00',
                                'end_date': '2099-01-01T00:00:00+00:00',
                            },
                        ],
                    },
                    'order_ready_for_billing': {
                        '__default__': [
                            {'start_date': '2000-01-01T00:00:00+00:00'},
                        ],
                    },
                },
            },
            'bc_response_fine.json',
            'expected_entities.json',
            'expected_accounts_with_billing_commissions_fine.json',
            'payout_flow/expected_docs_with_park_commission.json',
            'payout_flow/expected_orders_docs_with_park_commission.json',
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            id='order_with_park_commission',
        ),
        pytest.param(
            'order_ready_for_billing_doc_with_park_commission.json',
            'replication_contracts.json',
            {
                **_ENABLED_PAYOUT_CFG,
                **_ENABLED_BILLING_COMMISSIONS_CFG,
                'BILLING_PARK_COMMISSION_CALCULATE_BY_KIND': {
                    '__default__': False,
                    'order_ready_for_billing': True,
                },
                'BILLING_PARK_COMMISSION_FLOW_BY_KIND': {
                    '__default__': {
                        '__default__': [
                            {'start_date': '2099-01-01T00:00:00+00:00'},
                        ],
                    },
                },
            },
            'bc_response_fine.json',
            'expected_entities.json',
            'expected_accounts_with_billing_commissions_fine.json',
            'payout_flow/expected_docs_with_park_commission.json',
            (
                'payout_flow/'
                'expected_orders_docs_with_park_commission_dryrun.json'
            ),
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            id='order_with_park_commission_dryrun',
        ),
        pytest.param(
            'order_ready_for_billing_doc_park_commission_workshift.json',
            'replication_contracts.json',
            {
                **_ENABLED_PAYOUT_CFG,
                **_ENABLED_BILLING_COMMISSIONS_CFG,
                'BILLING_PARK_COMMISSION_CALCULATE_BY_KIND': {
                    '__default__': False,
                    'order_ready_for_billing': True,
                },
                'BILLING_PARK_COMMISSION_FLOW_BY_KIND': {
                    '__default__': {
                        '__default__': [
                            {
                                'start_date': '2099-01-01T00:00:00+00:00',
                                'end_date': '2099-01-01T00:00:00+00:00',
                            },
                        ],
                    },
                    'order_ready_for_billing': {
                        '__default__': [
                            {'start_date': '2000-01-01T00:00:00+00:00'},
                        ],
                    },
                },
            },
            'bc_response_fine.json',
            'expected_entities.json',
            'expected_accounts_park_commission_workshift.json',
            'payout_flow/expected_docs_park_commission_workshift.json',
            'payout_flow/expected_orders_docs_park_commission_workshift.json',
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            id='order_park_commission_workshift',
        ),
        pytest.param(
            (
                'order_ready_for_billing_doc_'
                'park_commission_zero_commission_and_cost.json'
            ),
            'replication_contracts.json',
            {
                **_ENABLED_PAYOUT_CFG,
                **_ENABLED_BILLING_COMMISSIONS_CFG,
                'BILLING_PARK_COMMISSION_CALCULATE_BY_KIND': {
                    '__default__': False,
                    'order_ready_for_billing': True,
                },
                'BILLING_PARK_COMMISSION_FLOW_BY_KIND': {
                    '__default__': {
                        '__default__': [
                            {
                                'start_date': '2099-01-01T00:00:00+00:00',
                                'end_date': '2099-01-01T00:00:00+00:00',
                            },
                        ],
                    },
                    'order_ready_for_billing': {
                        '__default__': [
                            {'start_date': '2000-01-01T00:00:00+00:00'},
                        ],
                    },
                },
            },
            'bc_response_fine.json',
            'expected_entities.json',
            'expected_accounts_park_commission_zero_commission_and_cost.json',
            (
                'payout_flow/'
                'expected_docs_park_commission_zero_commission_and_cost.json'
            ),
            (
                'payout_flow/expected_orders_docs_park_commission_'
                'zero_commission_and_cost.json'
            ),
            [('billing_consume_commission_events', 'doc_id/2')],
            id='order_park_commission_zero_commission_and_cost',
        ),
        pytest.param(
            'order_ready_for_billing_doc_corp_rebate_with_promocode.json',
            'replication_contracts_two_not_finished.json',
            {
                **_ENABLED_PAYOUT_CFG,
                **_ENABLED_BILLING_COMMISSIONS_CFG,
                'BILLING_COMMISSIONS_PROMOCODE_WITH_REBATE_SINCE': (
                    '2019-02-20T23:38:21+00:00'
                ),
            },
            'bc_response.json',
            'expected_entities.json',
            (
                'payout_flow/expected_accounts_corp_rebate'
                '_with_promocode_order.json'
            ),
            'payout_flow/expected_docs_corp_rebate_with_promocode_order.json',
            (
                'payout_flow/expected_orders_docs_corp_rebate_with_'
                'promocode_order.json'
            ),
            [
                ('billing_consume_commission_events', 'doc_id/2'),
                ('billing_consume_commission_events', 'doc_id/3'),
            ],
            id='corp_rebate_with_promoсode_order',
        ),
    ],
)
@pytest.mark.filldb(
    currency_rates='for_test_stq_task_pay_out_commission',
    parks='for_test_stq_task_pay_out_commission',
    cities='for_test_stq_task_pay_out_commission',
)
# pylint: disable=invalid-name,too-many-arguments,too-many-locals
async def test_stq_task_pay_out_commission(
        patch,
        monkeypatch,
        doc_json,
        replication_contracts_json,
        configs,
        billing_commissions_response,
        expected_entities_json,
        expected_accounts_json,
        expected_docs_json,
        expected_orders_docs_json,
        expected_stq_calls,
        load_json,
        db,
        load_py_json_dir,
):
    _set_process_commission(monkeypatch, True)
    _turn_on_create_childseat_rented_doc(monkeypatch)
    _turn_on_create_commission_transactions_doc(monkeypatch)
    _turn_on_pay_out_childseat(monkeypatch)
    _turn_on_pay_out_commission(monkeypatch)
    _turn_on_pay_out_b2b_fixed_commission(monkeypatch)
    _turn_on_commission_fees_processing(monkeypatch)
    _turn_on_hiring_components(monkeypatch)
    _set_no_billing_client_id_zones(monkeypatch)
    _fill_tlog_service_ids(monkeypatch)
    _fill_arbitrary_configs(monkeypatch, configs)

    doc = load_json(doc_json)
    expected_entities = load_json(expected_entities_json)
    expected_accounts = load_json(expected_accounts_json)
    expected_docs = load_json(expected_docs_json)
    expected_orders_docs = load_json(expected_orders_docs_json)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        db=db,
        existing_docs=[doc],
        balances={},
        replication_contracts=load_json(replication_contracts_json),
        replication_contracts_usage='enable',
        billing_client_ids_mapping={
            '__default__': 'billing_client_id',
            '111111': None,
        },
    )
    if billing_commissions_response:
        _set_commission_substitutions(monkeypatch)
        commission_response = load_py_json_dir(
            'test_stq_task_pay_out_commission', billing_commissions_response,
        )
        context.commissions_client.add_response(commission_response)

    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
    )
    created_docs = context.docs_client.created_docs
    for doc in created_docs:
        if 'tags' in doc['data']:
            doc['data']['tags'] = sorted(doc['data']['tags'])
    _assert_docs_equal(
        expected_docs=_sorted_docs(expected_docs),
        actual_docs=_sorted_docs(created_docs),
    )
    assert context.orders_client.created_docs == expected_orders_docs
    assert context.accounts_client.created_accounts == expected_accounts
    assert context.accounts_client.created_entities == expected_entities
    stq_calls = _get_stq_calls_with_task_ids(context.stq_agent.calls)
    assert stq_calls == expected_stq_calls


@pytest.mark.now('2019-02-27T09:28:04')
@pytest.mark.parametrize(
    'doc_json, rules_json, personal_rules_json, balances_json, '
    'expected_entities_json, expected_accounts_json, expected_docs_json, '
    'expected_orders_docs_json',
    [
        (
            'order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'expected_entities.json',
            'expected_accounts.json',
            'expected_docs.json',
            'expected_orders_docs.json',
        ),
        (
            'order_ready_for_billing_doc_netting.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'expected_entities.json',
            'expected_accounts.json',
            'expected_docs_netting.json',
            'expected_orders_docs_netting.json',
        ),
        (
            'order_ready_for_billing_doc_cargo.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'expected_entities.json',
            'expected_accounts.json',
            'expected_docs.json',
            'expected_orders_docs_cargo.json',
        ),
        (
            'order_ready_for_billing_doc_cargo_netting.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'expected_entities.json',
            'expected_accounts.json',
            'expected_docs.json',
            'expected_orders_docs_cargo_netting.json',
        ),
    ],
)
@pytest.mark.filldb(
    currency_rates='for_test_stq_task_pay_out_promocode',
    parks='for_test_stq_task_pay_out_promocode',
    cities='for_test_stq_task_pay_out_promocode',
)
# pylint: disable=invalid-name,too-many-arguments,too-many-locals
async def test_stq_task_pay_out_promocode(
        patch,
        monkeypatch,
        doc_json,
        rules_json,
        personal_rules_json,
        balances_json,
        expected_entities_json,
        expected_accounts_json,
        expected_docs_json,
        expected_orders_docs_json,
        load_json,
        db,
        load_py_json_dir,
):
    _turn_on_pay_out_promocode(monkeypatch)
    _fill_tlog_service_ids(monkeypatch)

    doc = load_json(doc_json)
    expected_entities = load_json(expected_entities_json)
    expected_accounts = load_json(expected_accounts_json)
    expected_docs = load_json(expected_docs_json)
    expected_orders_docs = load_json(expected_orders_docs_json)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        db=db,
        existing_docs=[doc],
        balances={},
        replication_contracts_usage='enable',
        replication_contracts=load_json('replication_contracts.json'),
        payout_migration=_build_new_billing_migration(
            '__default__', '0001-01-01',
        ),
    )

    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
    )
    created_docs = context.docs_client.created_docs
    for doc in created_docs:
        if 'tags' in doc['data']:
            doc['data']['tags'] = sorted(doc['data']['tags'])
    _assert_docs_equal(
        expected_docs=_sorted_docs(expected_docs),
        actual_docs=_sorted_docs(created_docs),
    )
    assert expected_orders_docs == context.orders_client.created_docs
    assert expected_accounts == context.accounts_client.created_accounts
    assert expected_entities == context.accounts_client.created_entities


@pytest.mark.now('2019-02-27T09:28:04')
@pytest.mark.parametrize(
    'doc_json,'
    'expected_accounts_json,expected_commission,expected_commission_vat',
    [
        # basic 10% commission
        (
            'no_tags/order_ready_for_billing_doc.json',
            'no_tags/expected_accounts.json',
            decimal.Decimal('30'),
            decimal.Decimal('6'),
        ),
        # increased 20% commission by tag commission_tag_1
        (
            'commission_tag_1/order_ready_for_billing_doc.json',
            'commission_tag_1/expected_accounts.json',
            decimal.Decimal('60'),
            decimal.Decimal('12'),
        ),
        # increased 30% commission by tag commission_tag_2
        (
            'commission_tag_2/order_ready_for_billing_doc.json',
            'commission_tag_2/expected_accounts.json',
            decimal.Decimal('90'),
            decimal.Decimal('18'),
        ),
        # basic 10% commission
        (
            'no_commission_tags/order_ready_for_billing_doc.json',
            'no_commission_tags/expected_accounts.json',
            decimal.Decimal('30'),
            decimal.Decimal('6'),
        ),
    ],
)
@pytest.mark.filldb(
    commission_contracts='for_test_commission_by_tag',
    parks='for_test_commission_by_tag',
    cities='for_test_process_doc',
)
# pylint: disable=invalid-name,too-many-arguments,too-many-locals
async def test_commission_by_tag(
        patch,
        monkeypatch,
        stq_client_patched,
        doc_json,
        expected_accounts_json,
        expected_commission,
        expected_commission_vat,
        load_json,
        load_py_json,
        db,
        load_py_json_dir,
):
    _set_process_commission(monkeypatch, True)

    doc = load_py_json(doc_json)
    doc_dict = {
        'doc_id': _DOC_ID,
        'kind': 'order_ready_for_billing',
        'external_obj_id': f'alias_id/{doc.order.alias_id}',
        'external_event_ref': 'order_ready_for_billing',
        'status': 'new',
        'data': models.doc.convert_order_ready_for_billing_to_json(doc),
    }
    context = ContextData(
        doc=doc_dict,
        rules=[],
        zones=_build_zones(),
        db=db,
        existing_docs=[doc_dict],
        balances={},
    )

    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
    )
    created_docs = context.docs_client.created_docs
    commission_journal = [
        doc for doc in created_docs if doc['kind'] == 'commission_journal'
    ][0]
    commission_account_id = 0
    commission_vat_account_id = 1
    actual_commission = None
    actual_commission_vat = None
    for journal_entry in commission_journal['journal_entries']:
        if journal_entry['account_id'] == commission_account_id:
            assert actual_commission is None
            actual_commission = decimal.Decimal(journal_entry['amount'])
        elif journal_entry['account_id'] == commission_vat_account_id:
            assert actual_commission_vat is None
            actual_commission_vat = decimal.Decimal(journal_entry['amount'])
    assert actual_commission == expected_commission
    assert actual_commission_vat == expected_commission_vat


@pytest.mark.now('2018-11-30T19:31:35')
@pytest.mark.filldb(
    parks='test_process_manual_subvention',
    cities='test_process_manual_subvention',
    currency_rates='test_process_manual_subvention',
)
@pytest.mark.parametrize(
    'test_data_json , pay_out_subventions, configs, '
    'park_commission_rules_status, park_commission_rules',
    [
        (
            'manual_subvention_doc.json',
            False,
            {**_DISABLED_PAYOUT_CFG},
            None,
            None,
        ),
        (
            'manual_subvention_doc_covid-19_compensation.json',
            False,
            {**_DISABLED_PAYOUT_CFG},
            None,
            None,
        ),
        (
            'manual_subvention_doc_zero_covid-19_compensation.json',
            False,
            {**_DISABLED_PAYOUT_CFG},
            None,
            None,
        ),
        (
            'manual_subvention_doc_covid-19_compensation_pay_out.json',
            True,
            {**_ENABLED_PAYOUT_CFG},
            None,
            None,
        ),
        (
            'manual_subvention_doc_pay_out.json',
            True,
            {
                **_ENABLED_PAYOUT_CFG,
                'BILLING_PARK_COMMISSION_CALCULATE_BY_KIND': {
                    '__default__': False,
                    'subvention': True,
                },
            },
            200,
            _build_common_park_commission_rules(),
        ),
        (
            'manual_subvention_doc_pay_out_dry_mode.json',
            True,
            {**_DISABLED_PAYOUT_CFG},
            None,
            None,
        ),
        (
            'manual_subvention_doc_pay_out_with_park_commission.json',
            True,
            {
                **_ENABLED_PAYOUT_CFG,
                'BILLING_PARK_COMMISSION_CALCULATE_BY_KIND': {
                    '__default__': False,
                    'subvention': True,
                },
                'BILLING_PARK_COMMISSION_FLOW_BY_KIND': {
                    '__default__': {
                        '__default__': [
                            {'start_date': '2099-01-01T00:00:00+00:00'},
                        ],
                    },
                    'subvention': {
                        '__default__': [
                            {'start_date': '2000-01-01T00:00:00+00:00'},
                        ],
                    },
                },
            },
            200,
            _build_common_park_commission_rules(),
        ),
        (
            (
                'manual_subvention_doc_pay_out_'
                'park_commission_rule_not_found.json'
            ),
            True,
            {
                **_ENABLED_PAYOUT_CFG,
                'BILLING_PARK_COMMISSION_CALCULATE_BY_KIND': {
                    '__default__': False,
                    'subvention': True,
                },
                'BILLING_PARK_COMMISSION_FLOW_BY_KIND': {
                    '__default__': {
                        '__default__': [
                            {'start_date': '2099-01-01T00:00:00+00:00'},
                        ],
                    },
                    'subvention': {
                        '__default__': [
                            {'start_date': '2000-01-01T00:00:00+00:00'},
                        ],
                    },
                },
            },
            404,
            None,
        ),
        (
            'manual_subvention_doc_taxi_order_fallback.json',
            False,
            {**_DISABLED_PAYOUT_CFG},
            None,
            None,
        ),
        (
            'manual_subvention_doc_taxi_order_cargo.json',
            False,
            {**_DISABLED_PAYOUT_CFG},
            None,
            None,
        ),
        (
            'manual_subvention_doc_cargo.json',
            False,
            {**_DISABLED_PAYOUT_CFG},
            None,
            None,
        ),
        (
            'manual_subvention_doc_cargo_claim_fallback.json',
            False,
            {**_DISABLED_PAYOUT_CFG},
            None,
            None,
        ),
    ],
)
async def test_process_manual_subvention(
        monkeypatch,
        db,
        test_data_json,
        pay_out_subventions,
        configs,
        park_commission_rules_status,
        park_commission_rules,
        load_py_json,
):
    _turn_on_create_subventions_input(monkeypatch)
    _turn_on_rus_netting(monkeypatch)
    _fill_tlog_service_ids(monkeypatch)
    _turn_on_send_contract_id_for_subventions(monkeypatch)
    test_data = load_py_json(test_data_json)
    doc_for_processing = test_data['doc']
    existing_docs = test_data['existing_docs']
    expected_created_docs = test_data['expected_created_docs']
    expected_accounts = test_data['expected_accounts']
    expected_entities = test_data['expected_entities']
    expected_created_orders_docs = test_data['expected_created_orders_docs']
    expected_docs_updated_events = test_data['expected_docs_updated_events']
    zones = [
        models.Zone(
            'moscow',
            'id',
            pytz.utc,
            'RUB',
            None,
            models.Vat.make_naive(12000),
            'rus',
        ),
    ]
    context = ContextData(
        doc=doc_for_processing,
        existing_docs=existing_docs,
        rules=[],
        zones=zones,
        db=db,
        balances={},
        pay_out_subventions=pay_out_subventions,
        replication_contracts=test_data['replication_contracts'],
        park_commission_rules=park_commission_rules,
        park_commission_rules_status=park_commission_rules_status,
    )
    _fill_arbitrary_configs(monkeypatch, configs)
    await process_doc.stq_task.task(
        context,
        task_info=helpers.create_task_info(),
        doc_id=doc_for_processing['doc_id'],
    )
    _assert_docs_equal(
        expected_docs=expected_created_docs,
        actual_docs=context.docs_client.created_docs,
    )
    assert expected_accounts == context.accounts_client.created_accounts
    assert expected_entities == context.accounts_client.created_entities
    assert expected_created_orders_docs == context.orders_client.created_docs
    assert expected_docs_updated_events == context.docs_client.update_events


@pytest.mark.now('2018-11-30T19:31:35')
@pytest.mark.parametrize(
    'test_data_json ',
    [
        'rebill_order.json',
        'rebill_old_billing_order.json',
        'rebill_relaxed_checks_order.json',
    ],
)
async def test_process_rebill_order(monkeypatch, test_data_json, load_py_json):
    test_data = load_py_json(test_data_json)
    doc_for_processing = test_data['doc']
    expected_stq_calls = test_data['expected_stq_calls']
    expected_finished_docs = test_data['expected_finished_docs']
    zones = [
        models.Zone(
            'moscow',
            'id',
            pytz.utc,
            'RUB',
            None,
            models.Vat.make_naive(12000),
            'rus',
        ),
        models.Zone(
            'obninsk',
            'id',
            pytz.utc,
            'RUB',
            None,
            models.Vat.make_naive(12000),
            'rus',
        ),
    ]
    context = ContextData(
        doc=doc_for_processing,
        rules=[],
        zones=zones,
        db=None,
        balances={},
        new_billing_migration=test_data['new_billing_migration'],
        relax_rebill_checks=test_data['relax_rebill_checks'],
    )
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=0,
    )
    actual_stq_calls = _get_stq_calls(context.stq_agent.calls)
    assert expected_stq_calls == actual_stq_calls
    assert expected_finished_docs == context.docs_client.finished_docs


@pytest.mark.parametrize(
    'test_case_json',
    [
        pytest.param(
            'goal_notification.json',
            marks=pytest.mark.now('2019-02-27T09:28:04'),
        ),
        pytest.param(
            'daily_guarantee_notification.json',
            marks=pytest.mark.now('2019-02-27T09:28:04'),
        ),
        pytest.param(
            'geo_booking_notification.json',
            marks=pytest.mark.now('2019-02-27T09:28:04'),
        ),
        pytest.param(
            'geo_booking_notification_not_migrated.json',
            marks=pytest.mark.now('2019-02-26T09:28:04'),
        ),
    ],
)
@pytest.mark.filldb(subvention_rules='for_test_process_notify')
async def test_process_notify(
        stq_client_patched, patch, test_case_json, load_py_json, db,
):
    _patch_uuid(patch)
    test_case = load_py_json(test_case_json)
    context = ContextData(
        doc=test_case['doc'],
        rules=[],
        zones=_build_zones(),
        db=db,
        balances={},
        existing_docs=[],
        geobooking_migration_date='2019-02-27',
    )

    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
    )

    fulfilled_notify = db.fulfilled_subventions_notify.find()
    fulfilled_notify = await fulfilled_notify.to_list(None)
    for rule in fulfilled_notify:
        del rule['_id']
    assert fulfilled_notify == test_case['expected']['fulfilled_notify']

    personal = await db.done_personal_subventions.find().to_list(None)
    for rule in personal:
        del rule['_id']
    assert personal == test_case['expected']['done_personal_subventions']


@pytest.mark.now('2018-11-30T19:31:35')
@pytest.mark.parametrize(
    'doc_json, payout_migration, '
    'expected_docs_json, expected_orders_docs_json',
    [
        (
            'referral_subvention_doc.json',
            _DISABLED_PAYOUT,
            'expected_docs.json',
            'py2_flow/expected_orders_docs.json',
        ),
        (
            'referral_subvention_doc.json',
            _ENABLED_PAYOUT,
            'expected_docs.json',
            'payout_flow/expected_orders_docs.json',
        ),
        # Park without offer currency & also city has no donate_multiplier
        (
            'referral_subvention_doc_without_offer_currency.json',
            _DISABLED_PAYOUT,
            'expected_docs_without_offer_currency.json',
            'expected_orders_docs_without_offer_currency.json',
        ),
    ],
)
@pytest.mark.filldb(
    parks='test_stq_task_enrich_subventions_input',
    cities='test_stq_task_enrich_subventions_input',
    currency_rates='test_stq_task_enrich_subventions_input',
)
# pylint: disable=invalid-name,too-many-arguments
async def test_stq_task_driver_referral_payment(
        patch,
        monkeypatch,
        load_json,
        db,
        load_py_json_dir,
        doc_json,
        payout_migration,
        expected_docs_json,
        expected_orders_docs_json,
):
    _fill_tlog_service_ids(monkeypatch)
    _turn_on_send_contract_id_for_subventions(monkeypatch)
    doc = load_json(doc_json)
    expected_docs = load_json(expected_docs_json)
    expected_orders_docs = load_json(expected_orders_docs_json)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=[],
        db=db,
        balances={},
        pay_out_subventions=True,
        payout_migration=payout_migration,
        replication_contracts=load_json('replication_contracts.json'),
    )
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
    )
    created_docs = context.docs_client.created_docs
    assert _sorted_docs(expected_docs) == _sorted_docs(created_docs)
    created_orders_docs = context.orders_client.created_docs
    assert expected_orders_docs == created_orders_docs


@pytest.mark.now('2019-03-01T00:00:00Z')
@pytest.mark.parametrize('use_execute,', [(False,), (True,)])
@pytest.mark.parametrize(
    'driver_mode, old_journal_limit_days, '
    'doc_json, rules_json, personal_rules_json, balances_json, '
    'journal_entries_json, '
    'expected_entities_json, expected_accounts_json, expected_docs_json',
    [
        (
            'orders',
            365,
            'order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'orders/journal_entries.json',
            'orders/expected_entities.json',
            'orders/expected_accounts.json',
            'orders/expected_docs.json',
        ),
        (
            'driver_fix',
            365,
            'order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'driver_fix/journal_entries.json',
            'driver_fix/expected_entities.json',
            'driver_fix/expected_accounts.json',
            'driver_fix/expected_docs.json',
        ),
        (
            'uberdriver',
            365,
            'order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'orders/journal_entries.json',
            'orders/expected_entities.json',
            'orders/expected_accounts.json',
            'orders/expected_docs.json',
        ),
        (
            'orders',
            1,
            'order_ready_for_billing_doc.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'orders/journal_entries.json',
            'orders/expected_entities.json',
            'orders/expected_accounts_old_entries.json',
            'orders/expected_docs_old_entries.json',
        ),
        (
            'orders',
            1,
            'order_ready_for_billing_doc_with_toll_road.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'orders/journal_entries_toll_road.json',
            'orders/expected_entities_toll_road.json',
            'orders/expected_accounts_toll_road.json',
            'orders/expected_docs_toll_road.json',
        ),
    ],
)
# pylint: disable=invalid-name,too-many-arguments
@pytest.mark.filldb(
    parks='for_test_stq_task_process_payment', cities='for_test_process_doc',
)
async def test_stq_task_process_payment(
        patch,
        monkeypatch,
        use_execute,
        driver_mode,
        old_journal_limit_days,
        doc_json,
        rules_json,
        personal_rules_json,
        balances_json,
        expected_entities_json,
        journal_entries_json,
        expected_accounts_json,
        expected_docs_json,
        load_json,
        db,
        load_py_json_dir,
):
    monkeypatch.setattr(
        config.Config, 'BILLING_SUBVENTIONS_PROCESS_PAYMENT', True,
    )

    monkeypatch.setattr(
        config.Config, 'BILLING_SEND_INCOME_ENTRIES_MODE', 'enable',
    )

    monkeypatch.setattr(
        config.Config,
        'BILLING_INCOME_ENTRIES_CASH_FILTERS',
        {
            'black_list': [],
            'white_list': [
                {
                    'entity_external_id': 'taximeter_driver_id/%/%',
                    'sub_account': 'payment/cash',
                },
                {
                    'entity_external_id': 'taximeter_driver_id/%/%',
                    'sub_account': 'toll_road/cash',
                },
            ],
        },
    )

    monkeypatch.setattr(
        config.Config,
        'BILLING_SUBVENTIONS_CREATE_BALANCE_CHANGED_VIA_EXECUTE',
        use_execute,
    )

    doc = load_json(doc_json)
    journal_entries_data = load_json(journal_entries_json)
    expected_entities = load_json(expected_entities_json)
    expected_accounts = load_json(expected_accounts_json)
    expected_docs = load_json(expected_docs_json)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        db=db,
        existing_docs=[doc],
        balances={},
        old_journal_limit_days=old_journal_limit_days,
    )

    @patch(
        'taxi_billing_subventions.process_doc.subscriptions.get_driver_mode',
    )
    async def _get_driver_mode(**kwargs):
        default_rule_fetcher = driver_modes.DefaultRuleFetcher(
            database=db, geo_booking_rules=[], log_extra={}, ctx=context,
        )
        return driver_modes.DriverMode(
            subscription=None,
            name=driver_mode,
            rule_fetcher=default_rule_fetcher,
            settings=models_config.driver_mode.DEFAULT_SETTINGS,
        )

    def _patch_doc_status(docs):
        # emulate doc creation with docs/execute as it's been created
        # with docs/create
        patched_docs: List[Dict] = []
        for one_doc in docs:
            if 'status' not in one_doc:
                one_doc['status'] = 'new'
            patched_docs.append(one_doc)
        return patched_docs

    @patch(
        'test_taxi_billing_subventions.test_process_doc.ReportsClient.'
        'get_journal_entries',
    )
    async def _get_journal_entries(**kwargs):
        return journal_entries_data['$journal_entries']

    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
    )
    created_docs = _patch_doc_status(context.docs_client.created_docs)

    _assert_docs_equal(
        expected_docs=_sorted_docs(expected_docs),
        actual_docs=_sorted_docs(_convert_docs_to_v1(created_docs)),
    )

    assert expected_accounts == context.accounts_client.created_accounts
    _assert_same_entities(
        expected_entities, context.accounts_client.created_entities,
    )

    assert (
        context.processing_client.sent_data
        == journal_entries_data['$expected_processing_payload']
    )


@pytest.mark.now('2019-03-01T00:00:00Z')
@pytest.mark.parametrize(
    'driver_mode, old_journal_limit_days, doc_json, existing_docs_json, '
    'rules_json, personal_rules_json, balances_json, '
    'expected_entities_json, expected_accounts_json, expected_docs_json',
    [
        (
            'orders',
            365,
            'order_ready_for_billing_doc.json',
            'orders/existing_docs.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'orders/expected_entities.json',
            'orders/expected_accounts.json',
            'orders/expected_docs.json',
        ),
        (
            'driver_fix',
            365,
            'order_ready_for_billing_doc.json',
            'orders/existing_docs.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'orders/expected_entities.json',
            'driverfix/expected_accounts.json',
            'driverfix/expected_docs.json',
        ),
        (
            'driver_fix',
            365,
            'driver_fix/order_ready_for_billing_amended_doc.json',
            'driver_fix/existing_docs.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'orders/expected_entities.json',
            'driver_fix/expected_accounts.json',
            'driver_fix/expected_docs.json',
        ),
        (
            'uberdriver',
            365,
            'order_ready_for_billing_doc.json',
            'orders/existing_docs.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'orders/expected_entities.json',
            'orders/expected_accounts.json',
            'uberdriver/expected_docs.json',
        ),
        (
            'orders',
            365,
            'cancelled_order_ready_for_billing_doc.json',
            'orders/existing_docs.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'orders/cancelled_expected_entities.json',
            'orders/cancelled_expected_accounts.json',
            'orders/cancelled_expected_docs.json',
        ),
        (
            'orders',
            365,
            'corp_order_ready_for_billing_doc.json',
            'orders/existing_docs.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'orders/expected_entities.json',
            'orders/expected_accounts.json',
            'orders/corp_expected_docs.json',
        ),
        (
            'orders',
            1,
            'order_ready_for_billing_doc.json',
            'orders/existing_docs.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'orders/expected_entities_old_entries.json',
            'orders/expected_accounts_old_entries.json',
            'orders/expected_docs_old_entries.json',
        ),
        (
            'orders',
            365,
            'orfb_corp_without_vat.json',
            'orders/existing_docs.json',
            'single_order_goal_rules.json',
            'empty_personal_rules.json',
            'single_order_goal_rules_balances.json',
            'orders/expected_entities.json',
            'orders/expected_accounts_corp_no_vat.json',
            'orders/expected_docs_corp_no_vat.json',
        ),
    ],
)
# pylint: disable=invalid-name,too-many-arguments
@pytest.mark.filldb(
    parks='for_test_stq_task_create_order_income_docs',
    cities='for_test_process_doc',
)
async def test_stq_task_create_order_income_docs(
        patch,
        monkeypatch,
        driver_mode,
        old_journal_limit_days,
        doc_json,
        existing_docs_json,
        rules_json,
        personal_rules_json,
        balances_json,
        expected_entities_json,
        expected_accounts_json,
        expected_docs_json,
        load_json,
        db,
        load_py_json_dir,
):
    _turn_on_create_order_income_doc(monkeypatch)

    _turn_on_reverse_on_order_amended(monkeypatch)

    _turn_on_use_reports_for_orfb(monkeypatch)

    doc = load_json(doc_json)
    existing_docs = load_json(existing_docs_json)
    expected_entities = load_json(expected_entities_json)
    expected_accounts = load_json(expected_accounts_json)
    expected_docs = load_json(expected_docs_json)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        db=db,
        existing_docs=existing_docs,
        balances={},
        old_journal_limit_days=old_journal_limit_days,
    )

    @patch(
        'taxi_billing_subventions.process_doc.subscriptions.get_driver_mode',
    )
    async def _get_driver_mode(**kwargs):
        default_rule_fetcher = driver_modes.DefaultRuleFetcher(
            database=db, geo_booking_rules=[], log_extra={}, ctx=context,
        )
        subscription = None
        if driver_mode == 'driver_fix':
            subscription = driver_modes.Subscription(
                ref='driver_fix_subscription',
                start=dt.datetime.now(tz=dt.timezone.utc),
                shift_close_time=None,
            )
        return driver_modes.DriverMode(
            subscription=subscription,
            name=driver_mode,
            rule_fetcher=default_rule_fetcher,
            settings=models_config.driver_mode.DEFAULT_SETTINGS,
        )

    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
    )
    created_docs = context.docs_client.created_docs
    _assert_docs_equal(
        expected_docs=_sorted_docs(expected_docs),
        actual_docs=_sorted_docs(created_docs),
    )
    assert expected_accounts == context.accounts_client.created_accounts
    _assert_same_entities(
        expected_entities, context.accounts_client.created_entities,
    )


@pytest.mark.now('2018-11-30T19:31:35')
@pytest.mark.parametrize(
    'doc_json, existing_docs_json,' 'expected_docs_json',
    [
        ('delay_doc.json', 'single_check_doc.json', 'empty_docs.json'),
        ('pay_doc.json', 'single_check_doc.json', 'pay_expected_docs.json'),
        (
            'block_doc.json',
            'single_separate_journal_topic_check_doc.json',
            'block_expected_docs.json',
        ),
        ('pay_doc.json', 'single_check_hold_doc.json', 'empty_docs.json'),
        ('pay_doc.json', 'taxi_goal_shift.json', 'af_goal_decision.json'),
        (
            'pay_doc.json',
            'taxi_geo_booking_shift.json',
            'af_geo_booking_decision.json',
        ),
        ('pay_doc.json', 'taxi_order.json', 'af_order_decision.json'),
        ('pay_doc.json', 'cargo_claim.json', 'af_cargo_claim_decision.json'),
    ],
)
async def test_process_antifraud_action(
        load_py_json,
        db,
        doc_json,
        existing_docs_json,
        expected_docs_json,
        monkeypatch,
):
    doc = load_py_json(doc_json)
    existing_docs = load_py_json(existing_docs_json)
    expected_docs = load_py_json(expected_docs_json)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=[],
        db=db,
        balances={},
        existing_docs=existing_docs,
    )
    _fill_arbitrary_configs(
        monkeypatch,
        {
            'BILLING_FUNCTIONS_TAXI_ORDER_MIGRATION': {
                'by_zone': {
                    '__default__': {
                        'enabled': [{'since': '1999-06-18T07:15:00+03:00'}],
                    },
                },
            },
        },
    )
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
    )
    created_docs = context.docs_client.created_docs
    assert _sorted_docs(expected_docs) == _sorted_docs(created_docs)


@pytest.mark.now('2018-11-30T19:31:35')
@pytest.mark.parametrize(
    'doc_json, existing_docs_json, pay_out_subventions, configs,'
    'park_commission_rules_status, park_commission_rules, '
    'expected_docs_json, expected_orders_docs_json, '
    'expected_doc_updates_json',
    [
        # PAY decision that does not revert previous entries
        (
            'pay_decision_doc.json',
            'empty_docs.json',
            False,
            {},
            None,
            None,
            'pay_decision_expected_docs.json',
            'empty_orders_docs.json',
            'empty_doc_updates.json',
        ),
        (
            'pay_decision_separate_journal_topic_doc.json',
            'empty_docs.json',
            False,
            {},
            None,
            None,
            'pay_decision_separate_journal_topic_expected_docs.json',
            'empty_orders_docs.json',
            'empty_doc_updates.json',
        ),
        # PAY decision that reverts previous entries
        (
            'pay_decision_doc.json',
            'pay_decision_with_revert_prev_docs.json',
            False,
            {},
            None,
            None,
            'pay_decision_with_revert_expected_docs.json',
            'empty_orders_docs.json',
            'empty_doc_updates.json',
        ),
        (
            'pay_decision_doc_pay_subvention.json',
            'empty_docs.json',
            True,
            {},
            None,
            None,
            'pay_decision_pay_subvention_expected_docs.json',
            'pay_decision_pay_subvention_expected_orders_docs.json',
            'empty_doc_updates.json',
        ),
        (
            'pay_decision_doc_pay_subvention_unrealized_sub_commission.json',
            'empty_docs.json',
            True,
            {},
            None,
            None,
            'pay_decision_pay_subvention_unrealized_expected_docs.json',
            'pay_decision_pay_subvention_unrealized_expected_orders_docs.json',
            'empty_doc_updates.json',
        ),
        (
            'block_decision_doc_pay_subvention.json',
            'empty_docs.json',
            True,
            {},
            None,
            None,
            'block_decision_pay_subvention_expected_docs.json',
            'block_decision_pay_subvention_expected_orders_docs.json',
            'empty_doc_updates.json',
        ),
        (
            'pay_decision_doc_pay_subvention_zero.json',
            'empty_docs.json',
            True,
            {},
            None,
            None,
            'pay_decision_pay_subvention_zero_expected_docs.json',
            'pay_decision_pay_subvention_zero_expected_orders_docs.json',
            'empty_doc_updates.json',
        ),
        (
            'pay_decision_doc_pay_subvention.json',
            'skip_by_version_prev_docs_af_check.json',
            True,
            {},
            None,
            None,
            'pay_decision_pay_subvention_expected_docs.json',
            'empty_orders_docs.json',
            'empty_doc_updates.json',
        ),
        (
            'pay_decision_doc_pay_subvention.json',
            'skip_by_version_prev_docs_af_decision.json',
            True,
            {},
            None,
            None,
            'pay_decision_pay_subvention_expected_docs.json',
            'empty_orders_docs.json',
            'empty_doc_updates.json',
        ),
        (
            'pay_decision_doc_pay_subvention.json',
            'empty_docs.json',
            True,
            {
                'BILLING_PARK_COMMISSION_CALCULATE_BY_KIND': {
                    '__default__': False,
                    'subvention': True,
                },
            },
            200,
            _build_common_park_commission_rules(),
            'pay_decision_pay_subvention_expected_docs.json',
            'pay_decision_pay_subvention_expected_orders_docs.json',
            'park_commission_doc_updates.json',
        ),
        (
            'pay_decision_doc_pay_subvention.json',
            'empty_docs.json',
            True,
            {
                'BILLING_PARK_COMMISSION_CALCULATE_BY_KIND': {
                    '__default__': False,
                    'subvention': True,
                },
                'BILLING_PARK_COMMISSION_FLOW_BY_KIND': {
                    '__default__': {
                        '__default__': [
                            {'start_date': '2099-01-01T00:00:00+00:00'},
                        ],
                    },
                    'subvention': {
                        '__default__': [
                            {'start_date': '2000-01-01T00:00:00+00:00'},
                        ],
                    },
                },
            },
            200,
            _build_common_park_commission_rules(),
            'pay_decision_pay_subvention_expected_docs.json',
            (
                'pay_decision_pay_subvention_expected_orders_docs'
                '_park_comission.json'
            ),
            'park_commission_doc_updates.json',
        ),
        (
            'pay_decision_doc_pay_subvention.json',
            'empty_docs.json',
            True,
            {
                'BILLING_PARK_COMMISSION_CALCULATE_BY_KIND': {
                    '__default__': False,
                    'subvention': True,
                },
                'BILLING_PARK_COMMISSION_FLOW_BY_KIND': {
                    '__default__': {
                        '__default__': [
                            {'start_date': '2099-01-01T00:00:00+00:00'},
                        ],
                    },
                    'subvention': {
                        '__default__': [
                            {'start_date': '2000-01-01T00:00:00+00:00'},
                        ],
                    },
                },
            },
            404,
            None,
            'pay_decision_pay_subvention_expected_docs.json',
            (
                'pay_decision_pay_subvention_expected_orders_docs_'
                'park_comission_rule_not_found.json'
            ),
            'park_commission_rule_not_found_doc_updates.json',
        ),
    ],
)
async def test_process_antifraud_decision(
        load_py_json,
        db,
        doc_json,
        existing_docs_json,
        pay_out_subventions,
        configs,
        park_commission_rules_status,
        park_commission_rules,
        expected_docs_json,
        expected_orders_docs_json,
        expected_doc_updates_json,
        monkeypatch,
):
    doc = load_py_json(doc_json)
    existing_docs = load_py_json(existing_docs_json)
    existing_docs.append(doc)
    expected_docs = load_py_json(expected_docs_json)
    expected_orders = load_py_json(expected_orders_docs_json)
    expected_doc_updates = load_py_json(expected_doc_updates_json)
    pay_out_subventions_af = pay_out_subventions
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        db=db,
        balances={},
        existing_docs=existing_docs,
        payout_migration=_ENABLED_PAYOUT,
        payout_migration_af=_DISABLED_PAYOUT,
        pay_out_subventions=pay_out_subventions,
        pay_out_subventions_af=pay_out_subventions_af,
        park_commission_rules=park_commission_rules,
        park_commission_rules_status=park_commission_rules_status,
    )
    _fill_arbitrary_configs(monkeypatch, configs)
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
    )
    created_docs = context.docs_client.created_docs
    created_orders = context.orders_client.created_docs
    doc_updates = context.docs_client.update_events
    assert _sorted_docs(expected_docs) == _sorted_docs(created_docs)
    assert expected_orders == created_orders
    assert expected_doc_updates == doc_updates


@pytest.mark.parametrize(
    'doc_info, existing_doc_infos, expected_docs_json, '
    'expected_account_ids, expected_entities_json',
    [
        # Delay the full sum if we received first DELAY
        #       delay
        # total  91
        # mfg    81
        # disc   10
        # comm   9.1
        (
            ('mfg__discount_payback.json', 'doc_id/123456', 'delay'),
            [],
            'write_to_hold_docs.json',
            [3, 0, 1, 7, 4, 5],
            'expected_entities.json',
        ),
        # Revert DELAY if we received PAY
        #       delay -> pay
        # total  91   ->  0
        # mfg    81   ->  0
        # disc   10   ->  0
        # comm   9.1  ->  0
        (
            ('mfg__discount_payback.json', 'doc_id/123456', 'pay'),
            [('mfg__discount_payback.json', 'doc_id/123456', 'delay')],
            'revert_hold_docs.json',
            [3, 0, 1, 7, 4, 5],
            'expected_entities.json',
        ),
        # Delay part of the sum if subvention has been delayed and paid already
        #       delay -> pay -> delay
        # total  91   ->  0  ->  9
        # r_mfg  0    ->  0  ->  90
        # mfg    81   ->  0  ->  -81
        # disc   10   ->  0  ->  0
        # comm   9.1  ->  0  ->  0.9
        (
            ('rmfg__discount_payback.json', 'doc_id/7891011', 'delay'),
            [
                ('mfg__discount_payback.json', 'doc_id/123456', 'delay'),
                ('mfg__discount_payback.json', 'doc_id/123456', 'pay'),
            ],
            'write_part_sum_to_hold_docs.json',
            [3, 0, 2, 7, 4, 6],
            'expected_entities.json',
        ),
        # Revert the delayed sum on second PAY
        #       delay -> pay -> delay -> pay
        # total  91   ->  0  ->  9    -> 0
        # r_mfg  0    ->  0  ->  90   -> 0
        # mfg    81   ->  0  ->  -81  -> 0
        # disc   10   ->  0  ->  0    -> 0
        # comm   9.1  ->  0  ->  0.9  -> 0
        (
            ('rmfg__discount_payback.json', 'doc_id/7891011', 'pay'),
            [
                ('mfg__discount_payback.json', 'doc_id/123456', 'delay'),
                ('mfg__discount_payback.json', 'doc_id/123456', 'pay'),
                ('rmfg__discount_payback.json', 'doc_id/7891011', 'delay'),
            ],
            'revert_delay_and_pay_docs.json',
            [3, 2, 0, 7, 6, 4],
            'expected_entities.json',
        ),
        # Revert DELAY if we received BLOCK
        #       delay -> block
        # total  91   ->  0
        # mfg    81   ->  0
        # disc   10   ->  0
        # comm   9.1  ->  0
        (
            ('mfg__discount_payback.json', 'doc_id/123456', 'block'),
            [('mfg__discount_payback.json', 'doc_id/123456', 'delay')],
            'revert_hold_docs.json',
            [3, 0, 1, 7, 4, 5],
            'expected_entities.json',
        ),
        # Delay the full sum on DELAY after BLOCK
        #       delay -> block -> delay
        # total  91   ->  0    ->  100
        # r_mfg  0    ->  0    ->  90
        # mfg    81   ->  0    ->  0
        # disc   10   ->  0    ->  10
        # comm   9.1  ->  0    ->  10
        (
            ('rmfg__discount_payback.json', 'doc_id/7891011', 'delay'),
            [
                ('mfg__discount_payback.json', 'doc_id/123456', 'delay'),
                ('mfg__discount_payback.json', 'doc_id/123456', 'block'),
            ],
            'write_full_sum_to_hold_after_block_docs.json',
            [3, 2, 1, 7, 6, 5],
            'expected_entities.json',
        ),
        # Revert the full sum on PAY after BLOCK
        #       delay -> block -> delay -> pay
        # total  91   ->  0    ->  100  ->  0
        # r_mfg  0    ->  0    ->  90   ->  0
        # mfg    81   ->  0    ->  0    ->  0
        # disc   10   ->  0    ->  10   ->  0
        # comm   9.1  ->  0    ->  10   ->  0
        (
            ('rmfg__discount_payback.json', 'doc_id/7891011', 'pay'),
            [
                ('mfg__discount_payback.json', 'doc_id/123456', 'delay'),
                ('mfg__discount_payback.json', 'doc_id/123456', 'block'),
                ('rmfg__discount_payback.json', 'doc_id/7891011', 'delay'),
            ],
            'revert_full_sum_after_block_docs.json',
            [3, 2, 1, 7, 6, 5],
            'expected_entities.json',
        ),
        # Delay part of the sum if there is previous subvention delayed
        #       delay -> delay
        # total  91   ->  100
        # r_mfg  0    ->  90
        # mfg    81   ->  0
        # disc   10   ->  10
        # comm   9.1  ->  10
        (
            ('rmfg__discount_payback.json', 'doc_id/7891011', 'delay'),
            [('mfg__discount_payback.json', 'doc_id/123456', 'delay')],
            'write_part_sum_to_hold_docs.json',
            [3, 0, 2, 7, 4, 6],
            'expected_entities.json',
        ),
        # Revert part of the delayed sum when receive PAY for first DELAY
        #       delay -> delay -> pay
        # total  91   ->  100  ->  9
        # r_mfg  0    ->  90   ->  90
        # mfg    81   ->  0    -> -81
        # disc   10   ->  10   ->  0
        # comm   9.1  ->  10   ->  0.9
        (
            ('mfg__discount_payback.json', 'doc_id/123456', 'pay'),
            [
                ('mfg__discount_payback.json', 'doc_id/123456', 'delay'),
                ('rmfg__discount_payback.json', 'doc_id/7891011', 'delay'),
            ],
            'revert_part_sum_docs.json',
            [3, 0, 1, 7, 4, 5],
            'expected_entities.json',
        ),
        # Revert rest of the delayed sum when receive second PAY
        #       delay -> delay -> pay  -> pay
        # total  91   ->  100  ->  9   -> 0
        # r_mfg  0    ->  90   ->  90  -> 0
        # mfg    81   ->  0    -> -81  -> 0
        # disc   10   ->  10   ->  0   -> 0
        # comm   9.1  ->  10   ->  0.9 -> 0
        (
            ('rmfg__discount_payback.json', 'doc_id/7891011', 'pay'),
            [
                ('mfg__discount_payback.json', 'doc_id/123456', 'delay'),
                ('rmfg__discount_payback.json', 'doc_id/7891011', 'delay'),
                ('mfg__discount_payback.json', 'doc_id/123456', 'pay'),
            ],
            'revert_rest_sum_docs.json',
            [3, 2, 0, 7, 6, 4],
            'expected_entities.json',
        ),
    ],
)
# pylint: disable=invalid-name
async def test_process_write_subvention_antifraud_entries(
        stq_client_patched,
        doc_info,
        existing_doc_infos,
        expected_docs_json,
        expected_account_ids,
        expected_entities_json,
        patch,
        load_json,
):
    _patch_random(patch)

    def _load_doc(info, doc_id, status):
        doc = load_json(info[0])
        doc['doc_id'] = doc_id
        doc['status'] = status
        doc['data']['check_id'] = info[1]
        antifraud_action = info[2]
        doc['data']['antifraud_action'] = antifraud_action
        if antifraud_action != 'delay':
            doc['data']['due'] = doc['data']['subventions_input']['due']
            doc['data']['subventions_input'] = None
        return doc

    doc = _load_doc(doc_info, _DOC_ID, 'new')
    existing_docs = [
        _load_doc(existing_doc_info, i, 'complete')
        for i, existing_doc_info in enumerate(existing_doc_infos)
    ]

    expected_docs = load_json(expected_docs_json)
    all_accounts = load_json('all_accounts.json')
    expected_accounts = [
        dict(all_accounts[acc_num], account_id=i)
        for i, acc_num in enumerate(expected_account_ids)
    ]
    expected_entities = load_json(expected_entities_json)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        db=None,
        balances={},
        existing_docs=existing_docs + [doc],
    )
    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
    )
    _assert_docs_equal(
        expected_docs=expected_docs,
        actual_docs=context.docs_client.created_docs,
    )
    assert expected_accounts == context.accounts_client.created_accounts
    assert expected_entities == context.accounts_client.created_entities


@pytest.mark.now('2019-02-27T09:28:04')
@pytest.mark.parametrize(
    'doc_json, expected_docs_json, existing_docs_json, journal_entries_json, '
    'skip_no_contract_subvention_events',
    [
        (
            'order_ready_for_billing_doc.json',
            'expected_docs_order_ready_for_billing.json',
            'existing_docs_order_ready_for_billing.json',
            None,
            False,
        ),
        (
            'order_ready_for_billing_doc.json',
            'expected_docs_order_ready_for_billing_skip_subv_events.json',
            'existing_docs_order_ready_for_billing.json',
            None,
            True,
        ),
        (
            'order_ready_for_billing_doc_with_delay.json',
            'expected_empty_docs.json',
            'existing_docs_order_ready_for_billing_with_delay.json',
            None,
            False,
        ),
        (
            'order_ready_for_billing_doc_with_delay_promocode.json',
            'expected_empty_docs.json',
            'existing_docs_order_ready_for_billing_with_delay_promocode.json',
            None,
            False,
        ),
        (
            'order_ready_for_billing_doc_no_billing_id.json',
            'expected_docs_order_ready_for_billing_doc_no_billing_id.json',
            'existing_docs_order_ready_for_billing_doc_no_billing_id.json',
            None,
            False,
        ),
        (
            'manual_subvention_doc.json',
            'expected_docs_manual_subvention.json',
            'existing_docs_manual_subvention.json',
            None,
            False,
        ),
        (
            'driver_referral_payment_doc.json',
            'expected_docs_driver_referral_payment.json',
            'existing_docs_driver_referral_payment.json',
            None,
            False,
        ),
        (
            'shift_ended_doc.json',
            'expected_docs_shift_ended.json',
            'existing_docs_shift_ended.json',
            'daily_guarantee_journal_entries.json',
            False,
        ),
        (
            'order_ready_for_billing_doc_promocode_netting.json',
            'expected_docs_order_ready_for_billing_promocode_netting.json',
            'existing_docs_order_ready_for_billing.json',
            None,
            False,
        ),
    ],
)
@pytest.mark.filldb(
    parks='for_test_check_marketing_contract',
    cities='for_test_check_marketing_contract',
    subvention_rules='for_test_check_marketing_contract',
)
# pylint: disable=invalid-name
async def test_check_marketing_contract(
        patch,
        monkeypatch,
        doc_json,
        expected_docs_json,
        existing_docs_json,
        journal_entries_json,
        skip_no_contract_subvention_events,
        load_json,
        load_py_json,
        db,
        load_py_json_dir,
):
    delay = 24 * 60 * 60
    retry = 15 * 60

    async def _reschedule(self, queue, task_id, eta, log_extra=None):
        assert eta == dt.datetime.utcnow() + dt.timedelta(seconds=retry)

    monkeypatch.setattr(StqAgentClientMock, 'reschedule', _reschedule)

    _set_check_marketing_contract(monkeypatch)
    _set_contract_delay(monkeypatch, delay, retry)
    _set_no_billing_client_id_zones(monkeypatch)
    _set_skip_no_contract_subvention_events(
        monkeypatch, skip_no_contract_subvention_events,
    )
    _turn_on_kaz_netting(monkeypatch)
    _patch_random(patch)

    doc = load_json(doc_json)
    journal_entries = None
    if journal_entries_json is not None:
        journal_entries = load_py_json(journal_entries_json)
    expected_docs = load_json(expected_docs_json)
    existing_docs = load_json(existing_docs_json)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        journal_entries=journal_entries,
        db=db,
        existing_docs=existing_docs,
        balances=_build_balances(num_goal_orders=15, version=1),
    )

    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
    )
    created_docs = context.docs_client.created_docs
    _assert_docs_equal(
        expected_docs=_sorted_docs(expected_docs),
        actual_docs=_sorted_docs(created_docs),
    )


@pytest.mark.now('2019-02-27T09:28:04')
@pytest.mark.parametrize(
    'doc_json, expected_docs_json, replication_contracts_json',
    [
        (
            'schedule_parks_b2b_fixed_commission.json',
            'expected_docs_with_contracts_data.json',
            'replication_contracts.json',
        ),
        (
            (
                'schedule_parks_b2b_fixed_commission_partition'
                '_with_contracts_data.json'
            ),
            'expected_docs_partition_with_contracts_data.json',
            'replication_contracts.json',
        ),
    ],
)
@pytest.mark.filldb(parks='for_test_b2b_fixed_commission')
async def test_process_schedule_parks_b2b_fixed_commission(
        doc_json,
        expected_docs_json,
        replication_contracts_json,
        load_json,
        load_py_json,
        db,
        load_py_json_dir,
        monkeypatch,
):
    doc = load_py_json(doc_json)
    expected_docs = load_py_json(expected_docs_json)
    replication_contracts = load_json(replication_contracts_json)
    context = ContextData(
        doc=doc,
        rules=[],
        zones=_build_zones(),
        journal_entries=[],
        db=db,
        existing_docs=[],
        balances={},
        replication_contracts_usage='enable',
        replication_contracts=replication_contracts,
        billing_client_ids_mapping={'__default__': 'billing_client_id'},
    )

    await process_doc.stq_task.task(
        context, task_info=helpers.create_task_info(), doc_id=_DOC_ID,
    )
    created_docs = context.docs_client.created_docs
    assert created_docs == expected_docs


@pytest.mark.parametrize(
    'possible_frauder',
    [
        ({'driver_licenses': []}),
        ({'driver_licenses': [], 'driver_license_personal_ids': ['pd_id']}),
        ({'driver_licenses': ['license']}),
    ],
)
async def test_ensure_possible_frauder_license(possible_frauder, *, db):
    required_boring_args = dict(doc={}, rules=[], zones=[], db=db, balances={})
    context = ContextData(
        **required_boring_args,
        drivers_profiles={
            'db_id_uuid': {'data': {'license': {'pd_id': 'pd_id'}}},
        },
        drivers_licenses={'pd_id': {'id': 'pd_id', 'license': 'license'}},
    )
    data = {
        'possible_frauder': possible_frauder,
        'driver': {'db_id': 'db_id', 'uuid': 'uuid'},
    }
    doc = {'data': data}
    # pylint: disable=protected-access
    await _shift_ended._ensure_possible_frauder_license(context, doc, None)
    assert data['possible_frauder']['driver_licenses'] == ['license']
    assert data['possible_frauder']['driver_license_personal_ids'] == ['pd_id']


@pytest.mark.parametrize('should_send_tariff_zone', [True, False])
def test_remove_tariff_zone_from_antifraud_driver_query(
        should_send_tariff_zone, *, load_py_json,
):
    driver_data = load_py_json('driver_data.json')
    # pylint: disable=protected-access
    query = _subvention_antifraud_check._make_driver_query_object(
        should_send_tariff_zone, driver_data,
    )
    assert 'zone' in query if should_send_tariff_zone else 'zone' not in query


def _build_zones():
    return [
        _build_ekb_zone(),
        _build_moscow_zone(),
        _build_kazan_zone(),
        _build_volgograd_zone(),
        _build_narofominsk_zone(),
        _build_karagana_zone(),
        _build_minsk_zone(),
    ]


def _build_ekb_zone():
    return models.Zone(
        name='ekb',
        city_id='Екатеринбург',
        tzinfo=pytz.timezone('Asia/Yekaterinburg'),
        currency='RUB',
        locale='ru',
        vat=models.Vat(
            [(intervals.unbounded(), decimal.Decimal('1.2'))], None,
        ),
        country='rus',
    )


def _build_moscow_zone():
    return models.Zone(
        name='moscow',
        city_id='Москва',
        tzinfo=pytz.timezone('Europe/Moscow'),
        currency='RUB',
        locale='ru',
        vat=models.Vat(
            [(intervals.unbounded(), decimal.Decimal('1.2'))], None,
        ),
        country='rus',
    )


def _build_kazan_zone():
    return models.Zone(
        name='kazan',
        city_id='Казань',
        tzinfo=pytz.timezone('Europe/Moscow'),
        currency='RUB',
        locale='ru',
        vat=None,
        country='rus',
    )


def _build_volgograd_zone():
    return models.Zone(
        name='volgograd',
        city_id='Волгоград',
        tzinfo=pytz.timezone('Europe/Volgograd'),
        currency='RUB',
        locale='ru',
        vat=None,
        country='rus',
    )


def _build_narofominsk_zone():
    return models.Zone(
        name='narofominsk',
        city_id='Москва',
        tzinfo=pytz.timezone('Europe/Moscow'),
        currency='RUB',
        locale='ru',
        vat=None,
        country='rus',
    )


def _build_karagana_zone():
    return models.Zone(
        name='karaganda',
        city_id='Караганда',
        tzinfo=pytz.timezone('Asia/Almaty'),
        currency='KZT',
        locale='kk',
        vat=None,
        country='kaz',
    )


def _build_minsk_zone():
    return models.Zone(
        name='minsk',
        city_id='Минск',
        tzinfo=pytz.timezone('Asia/Almaty'),
        currency='BYR',
        locale='ru',
        vat=None,
        country='blr',
    )


def _build_tel_aviv_zone():
    return models.Zone(
        name='tel_aviv',
        city_id='Тель-Авив',
        tzinfo=pytz.timezone('Asia/Jerusalem'),
        currency='ILS',
        locale='ru',
        vat=None,
        country='isr',
    )


def _build_balances(
        num_goal_orders, version=1, agreement_ref=None,
) -> Balances:
    return {
        **_build_goal_balances(num_goal_orders),
        **_build_personal_goal_balances(num_goal_orders),
        **_build_migration_boundary_balances(num_goal_orders),
        **_build_geo_booking_balances(),
        **_build_daily_guarantee_balances(),
        **_build_commission_daily_guarantee_balances(),
        **_build_driver_fix_balances(version, agreement_ref),
    }


def _build_goal_balances(num_goal_orders) -> Balances:
    entity_id = 'unique_driver_id/111111111111111111111111'
    agreement_id = 'subvention_agreement/1/default/group_id/goal_rule_group_id'
    start = dt.datetime(2018, 5, 10, 21, tzinfo=pytz.utc)
    end = dt.datetime(2018, 5, 11, 21, tzinfo=pytz.utc)
    num_orders_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='num_orders',
        accrued_at=(start, end),
    )
    num_orders_response = _build_balance_response(
        query=num_orders_query,
        account_id=666,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after=str(num_goal_orders),
    )
    return {num_orders_query: num_orders_response}


def _build_personal_goal_balances(num_goal_orders) -> Balances:
    entity_id = 'unique_driver_id/111111111111111111111111'
    agreement_id = (
        'subvention_agreement/1/personal/group_id/p_goal_rule_group_id'
    )
    start = dt.datetime(2018, 5, 10, 21, tzinfo=pytz.utc)
    end = dt.datetime(2018, 5, 11, 21, tzinfo=pytz.utc)
    num_orders_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='num_orders',
        accrued_at=(start, end),
    )
    num_orders_response = _build_balance_response(
        query=num_orders_query,
        account_id=666,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after=str(num_goal_orders // 2),
    )

    default_num_orders_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=(
            'subvention_agreement/1/default/group_id/p_goal_rule_group_id'
        ),
        sub_account='num_orders',
        accrued_at=(start, end),
    )
    default_num_orders_response = _build_balance_response(
        query=num_orders_query,
        account_id=667,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after=str(num_goal_orders - num_goal_orders // 2),
    )
    return {
        num_orders_query: num_orders_response,
        default_num_orders_query: default_num_orders_response,
    }


def _build_migration_boundary_balances(num_goal_orders) -> Balances:
    entity_id = 'unique_driver_id/111111111111111111111111'
    agreement_id = (
        'subvention_agreement/1/personal/group_id/'
        'migration_boundary_rule_group_id'
    )
    start = dt.datetime(2018, 7, 1, 21, tzinfo=pytz.utc)
    end = dt.datetime(2018, 7, 3, 21, tzinfo=pytz.utc)
    num_orders_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='num_orders',
        accrued_at=(start, end),
    )
    num_orders_response = _build_balance_response(
        query=num_orders_query,
        account_id=666,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after=str(num_goal_orders),
    )
    return {num_orders_query: num_orders_response}


def _build_balance_response(
        query: models.BalanceQuery, account_id, currency, before, after,
):
    assert len(query.accrued_at) == 2
    return [
        {
            'account': {
                'account_id': account_id,
                'entity_external_id': query.entity_id,
                'currency': currency,
                'sub_account': query.sub_account,
                'opened': None,
                'expired': None,
            },
            'balances': [
                {'balance': before, 'accrued_at': query.accrued_at[0]},
                {'balance': after, 'accrued_at': query.accrued_at[1]},
            ],
        },
    ]


def _build_geo_booking_balances() -> Balances:
    entity_id = 'unique_driver_id/111111111111111111111111'
    agreement_id = 'subvention_agreement/1/default/_id/geo_booking_rule_id'
    start = dt.datetime(2018, 5, 10, 21, tzinfo=pytz.utc)
    end = dt.datetime(2018, 5, 11, 21, tzinfo=pytz.utc)
    income_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='income',
        accrued_at=(start, end),
    )
    income_response = _build_balance_response(
        query=income_query,
        account_id=667,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after='10',
    )
    free_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='time/free_minutes',
        accrued_at=(start, end),
    )
    free_response = _build_balance_response(
        query=free_query,
        account_id=668,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after='500',
    )
    unfit_free_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='unfit/time/free_minutes',
        accrued_at=(start, end),
    )
    unfit_free_response = _build_balance_response(
        query=unfit_free_query,
        account_id=668,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after='0',
    )
    on_order_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='time/on_order_minutes',
        accrued_at=(start, end),
    )
    on_order_response = _build_balance_response(
        query=on_order_query,
        account_id=669,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after='200',
    )
    unfit_on_order_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='unfit/time/on_order_minutes',
        accrued_at=(start, end),
    )
    unfit_on_order_response = _build_balance_response(
        query=unfit_on_order_query,
        account_id=669,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after='0',
    )
    unfit_income_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='unfit/income',
        accrued_at=(start, end),
    )
    unfit_income_response = _build_balance_response(
        query=unfit_income_query,
        account_id=667,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after='0',
    )
    return {
        income_query: income_response,
        free_query: free_response,
        on_order_query: on_order_response,
        unfit_income_query: unfit_income_response,
        unfit_free_query: unfit_free_response,
        unfit_on_order_query: unfit_on_order_response,
    }


def _build_daily_guarantee_balances() -> Balances:
    entity_id = 'unique_driver_id/111111111111111111111111'
    agreement_id = (
        'subvention_agreement/1/default/group_id/daily_guarantee_rule_group_id'
    )
    start = dt.datetime(2018, 5, 10, 21, tzinfo=pytz.utc)
    end = dt.datetime(2018, 5, 11, 21, tzinfo=pytz.utc)
    num_orders_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='num_orders',
        accrued_at=(start, end),
    )
    num_orders_response = _build_balance_response(
        query=num_orders_query,
        account_id=670,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after='16',
    )
    unfit_num_orders_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='unfit/num_orders',
        accrued_at=(start, end),
    )
    unfit_num_orders_response = _build_balance_response(
        query=unfit_num_orders_query,
        account_id=670,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after='1',
    )
    income_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='income',
        accrued_at=(start, end),
    )
    income_response = _build_balance_response(
        query=income_query,
        account_id=671,
        currency='RUB',
        before='0',
        after='500',
    )
    unfit_income_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='unfit/income',
        accrued_at=(start, end),
    )
    unfit_income_response = _build_balance_response(
        query=unfit_income_query,
        account_id=671,
        currency='RUB',
        before='0',
        after='40',
    )
    workshift_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='num_orders_per_workshift',
        accrued_at=(start, end),
    )
    workshift_response = _build_balance_response(
        query=workshift_query,
        account_id=672,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after='6',
    )
    unfit_workshift_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='unfit/num_orders_per_workshift',
        accrued_at=(start, end),
    )
    unfit_workshift_response = _build_balance_response(
        query=unfit_workshift_query,
        account_id=672,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after='0',
    )
    promocode_commission_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='promocode_commission',
        accrued_at=(start, end),
    )
    promocode_commission_response = _build_balance_response(
        query=promocode_commission_query,
        account_id=673,
        currency='RUB',
        before='0',
        after='2',
    )
    num_orders_promocode_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='num_orders_per_promocode',
        accrued_at=(start, end),
    )
    num_orders_promocode_response = _build_balance_response(
        query=num_orders_promocode_query,
        account_id=674,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after='2',
    )
    return {
        num_orders_query: num_orders_response,
        income_query: income_response,
        workshift_query: workshift_response,
        unfit_num_orders_query: unfit_num_orders_response,
        unfit_income_query: unfit_income_response,
        unfit_workshift_query: unfit_workshift_response,
        promocode_commission_query: promocode_commission_response,
        num_orders_promocode_query: num_orders_promocode_response,
    }


def _build_commission_daily_guarantee_balances() -> Balances:
    # pylint: disable=invalid-name,too-many-locals
    entity_id = 'unique_driver_id/111111111111111111111111'
    agreement_id = (
        'subvention_agreement/1/default/group_id/'
        'commission_daily_guarantee_rule_group_id'
    )
    start = dt.datetime(2018, 5, 10, 21, tzinfo=pytz.utc)
    end = dt.datetime(2018, 5, 11, 21, tzinfo=pytz.utc)
    num_orders_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='num_orders',
        accrued_at=(start, end),
    )
    num_orders_response = _build_balance_response(
        query=num_orders_query,
        account_id=670,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after='16',
    )
    unfit_num_orders_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='unfit/num_orders',
        accrued_at=(start, end),
    )
    unfit_num_orders_response = _build_balance_response(
        query=unfit_num_orders_query,
        account_id=670,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after='1',
    )
    income_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='income',
        accrued_at=(start, end),
    )
    income_response = _build_balance_response(
        query=income_query,
        account_id=671,
        currency='RUB',
        before='0',
        after='900',
    )
    unfit_income_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='unfit/income',
        accrued_at=(start, end),
    )
    unfit_income_response = _build_balance_response(
        query=unfit_income_query,
        account_id=671,
        currency='RUB',
        before='0',
        after='100',
    )
    commission_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='commission_total',
        accrued_at=(start, end),
    )
    commission_response = _build_balance_response(
        query=commission_query,
        account_id=672,
        currency='RUB',
        before='0',
        after='100',
    )
    unfit_commission_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='unfit/commission_total',
        accrued_at=(start, end),
    )
    unfit_commission_response = _build_balance_response(
        query=unfit_commission_query,
        account_id=672,
        currency='RUB',
        before='0',
        after='20',
    )
    workshift_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='num_orders_per_workshift',
        accrued_at=(start, end),
    )
    workshift_response = _build_balance_response(
        query=workshift_query,
        account_id=673,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after='6',
    )
    unfit_workshift_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='unfit/num_orders_per_workshift',
        accrued_at=(start, end),
    )
    unfit_workshift_response = _build_balance_response(
        query=unfit_workshift_query,
        account_id=673,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after='0',
    )
    promocode_commission_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='promocode_commission',
        accrued_at=(start, end),
    )
    promocode_commission_response = _build_balance_response(
        query=promocode_commission_query,
        account_id=674,
        currency='RUB',
        before='0',
        after='2',
    )
    unfit_promocode_commission_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='unfit/promocode_commission',
        accrued_at=(start, end),
    )
    unfit_promocode_commission_response = _build_balance_response(
        query=unfit_promocode_commission_query,
        account_id=674,
        currency='RUB',
        before='0',
        after='0',
    )
    num_orders_promocode_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='num_orders_per_promocode',
        accrued_at=(start, end),
    )
    num_orders_promocode_response = _build_balance_response(
        query=num_orders_promocode_query,
        account_id=675,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after='2',
    )
    unfit_num_orders_promocode_query = models.BalanceQuery(
        entity_id=entity_id,
        agreement_id=agreement_id,
        sub_account='unfit/num_orders_per_promocode',
        accrued_at=(start, end),
    )
    unfit_num_orders_promocode_response = _build_balance_response(
        query=unfit_num_orders_promocode_query,
        account_id=675,
        currency=billing.Money.NO_CURRENCY,
        before='0',
        after='0',
    )
    return {
        num_orders_query: num_orders_response,
        income_query: income_response,
        commission_query: commission_response,
        unfit_num_orders_query: unfit_num_orders_response,
        unfit_income_query: unfit_income_response,
        unfit_commission_query: unfit_commission_response,
        workshift_query: workshift_response,
        unfit_workshift_query: unfit_workshift_response,
        promocode_commission_query: promocode_commission_response,
        num_orders_promocode_query: num_orders_promocode_response,
        unfit_promocode_commission_query: unfit_promocode_commission_response,
        unfit_num_orders_promocode_query: unfit_num_orders_promocode_response,
    }


def _build_driver_fix_balances(version, agreement_ref) -> Balances:
    # pylint: disable=invalid-name,too-many-locals
    entity_id = 'unique_driver_id/111111111111111111111111'
    if agreement_ref and 'driver_fix_b2b' in agreement_ref:
        agreement_id = agreement_ref
    else:
        agreement_id = 'subvention_agreement/1/default/_id/driver_fix'
    start = dt.datetime(2018, 5, 10, 21, tzinfo=pytz.utc)
    end = dt.datetime(2018, 5, 11, 21, tzinfo=pytz.utc)

    accounts = [
        ('income', 'RUB'),
        ('guarantee', 'RUB'),
        ('time/on_order_minutes', 'XXX'),
        ('time/free_minutes', 'XXX'),
        ('discounts', 'RUB'),
        ('promocodes/marketing', 'RUB'),
        ('promocodes/support', 'RUB'),
        ('guarantee/on_order', 'RUB'),
    ]

    amounts_by_version = {
        1: ('30', '20', '5', '10', '0', '0', '0', '10'),
        2: ('20', '30', '0', '3', '0', '0', '0', '100'),
        3: ('10', '300', '2', '10', '0', '0', '0', '100'),
        4: ('300', '10', '1', '2', '0', '0', '0', '100'),
        5: ('0', '30', '15', '45', '0', '0', '0', '100'),
        6: ('20', '30', '0', '3', '100', '300', '150', '1000'),
        7: ('10', '30', '15', '45', '0', '0', '0', '100'),
    }

    account_id = 1
    balanses = {}
    for (sub_account, currency), amount in itertools.zip_longest(
            accounts, amounts_by_version[version], fillvalue='0',
    ):
        query = models.BalanceQuery(
            entity_id=entity_id,
            agreement_id=agreement_id,
            sub_account=sub_account,
            accrued_at=(start, end),
        )

        response = _build_balance_response(
            query=query,
            account_id=account_id,
            currency=currency,
            before='0',
            after=amount,
        )
        account_id += 1
        balanses.update({query: response})

    return balanses


def _turn_on_antifraud_processing(monkeypatch):
    monkeypatch.setattr(
        config.Config,
        'BILLING_SUBVENTIONS_PROCEDURE_INSTANT_SUBVENTION',
        True,
    )


def _turn_on_antifraud_complete(monkeypatch):
    monkeypatch.setattr(
        config.Config, 'BILLING_SUBVENTIONS_PROCESS_ANTIFRAUD_COMPLETE', True,
    )


def _turn_on_commissions(monkeypatch):
    monkeypatch.setattr(
        config.Config,
        'BILLING_SUBVENTIONS_PROCESS_SUBVENTION_COMMISSION',
        True,
    )


def _turn_on_create_subventions_input(monkeypatch):
    monkeypatch.setattr(
        config.Config, 'BILLING_SUBVENTIONS_CREATE_SUBVENTIONS_INPUT', True,
    )


def _turn_on_enrich_subventions_input(monkeypatch):
    monkeypatch.setattr(
        config.Config, 'BILLING_SUBVENTIONS_ENRICH_SUBVENTIONS_INPUT', True,
    )


def _turn_on_use_billing_reports(monkeypatch):
    monkeypatch.setattr(
        config.Config,
        'BILLING_SUBVENTIONS_USE_REPORTS_TO_UPDATE_LEGACY',
        True,
    )


def _use_billing_reports_for_shift_ended(monkeypatch, use_billing_reports):
    monkeypatch.setattr(
        config.Config,
        'BILLING_SUBVENTIONS_USE_REPORTS_FOR_SHIFT_ENDED',
        {'enabled': use_billing_reports},
    )


def _set_process_commission(monkeypatch, value):
    monkeypatch.setattr(
        config.Config, 'BILLING_SUBVENTIONS_PROCESS_COMMISSION', value,
    )


def _set_commission_substitutions(monkeypatch):
    monkeypatch.setattr(
        config.Config,
        'BILLING_SUBVENTIONS_COMMISSION_TEMPLATE_SUBSTITUTIONS',
        {
            'hiring_type_sub_account': {
                'commercial': 'commission/hiring_inc_vat/park_only',
                'commercial_returned': (
                    'commission/hiring_returned_inc_vat/park_only'
                ),
                'commercial_with_rent': (
                    'commission/hiring_with_car_inc_vat/park_only'
                ),
            },
            'hiring_tlog_detailed_products': {
                'commercial': 'gross_driver_hiring_commission_trips',
                'commercial_returned': 'commercial_returned',
                'commercial_with_rent': 'gross_driver_hiring_commission_trips',
            },
            'hiring_tlog_products': {
                'commercial': 'hiring_with_car',
                'commercial_returned': 'commercial_returned',
                'commercial_with_rent': 'hiring_with_car',
            },
        },
    )


def _turn_on_commission_fees_processing(monkeypatch):
    cfg_name = 'BILLING_SUBVENTIONS_USE_COMMISSION_FEES'
    monkeypatch.setattr(config.Config, cfg_name, True)


def _turn_on_create_childseat_rented_doc(monkeypatch):
    monkeypatch.setattr(
        config.Config, 'BILLING_SUBVENTIONS_CREATE_CHILDSEAT_RENTED_DOC', True,
    )


def _turn_on_pay_out_childseat(monkeypatch):
    monkeypatch.setattr(
        config.Config, 'BILLING_SUBVENTIONS_PAY_OUT_CHILDSEAT', True,
    )


def _turn_on_create_commission_transactions_doc(monkeypatch):
    monkeypatch.setattr(
        config.Config,
        'BILLING_SUBVENTIONS_CREATE_COMMISSION_TRANSACTIONS_DOC',
        True,
    )


def _turn_on_create_order_subvention_changed(monkeypatch):
    monkeypatch.setattr(
        config.Config,
        'BILLING_SUBVENTIONS_ORDER_SUBVENTION_CHANGED_PY3',
        True,
    )
    monkeypatch.setattr(
        config.Config,
        'ORDER_SUBVENTION_CHANGED_FROM_PY3_SINCE_DUE',
        '2019-04-01T00:00:00+00:00',
    )


def _turn_on_create_order_commission_changed_for_subvention(monkeypatch):
    monkeypatch.setattr(
        config.Config, 'ORDER_COMMISSION_CHANGED_FOR_SUBVENTION_PY3', True,
    )
    monkeypatch.setattr(
        config.Config,
        'ORDER_COMMISSION_CHANGED_FROM_PY3_SINCE_DUE',
        '2019-04-01T00:00:00+00:00',
    )


def _turn_on_create_order_commission_changed_for_order(monkeypatch):
    monkeypatch.setattr(
        config.Config, 'ORDER_COMMISSION_CHANGED_FOR_ORDER_PY3', True,
    )
    monkeypatch.setattr(
        config.Config,
        'ORDER_COMMISSION_CHANGED_FROM_PY3_SINCE_DUE',
        '2019-04-01T00:00:00+00:00',
    )


def _turn_on_pay_out_commission(monkeypatch):
    monkeypatch.setattr(
        config.Config, 'BILLING_SUBVENTIONS_PAY_OUT_COMMISSION', True,
    )


def _turn_on_pay_out_b2b_fixed_commission(monkeypatch):
    monkeypatch.setattr(
        config.Config, 'BILLING_MAKE_B2B_FIXED_COMMISSION_PAYOUT', True,
    )


def _turn_on_hiring_components(monkeypatch):
    monkeypatch.setattr(
        config.Config, 'BILLING_SUBVENTIONS_HIRING_PAYOUT_COMPONENTS', True,
    )
    monkeypatch.setattr(
        config.Config,
        'BILLING_SUBVENTIONS_HIRING_PAYOUT_COMPONENTS_SINCE_DUE',
        '2000-01-01T00:00:00+00:00',
    )


def _set_billing_commissions_level(monkeypatch, level):
    monkeypatch.setattr(
        config.Config,
        'BILLING_SUBVENTIONS_USE_BILLING_COMMISSIONS',
        {'default_for_all': level},
    )


def _turn_on_pay_out_promocode(monkeypatch):
    monkeypatch.setattr(
        config.Config, 'BILLING_SUBVENTIONS_PAY_OUT_PROMOCODE', True,
    )


def _turn_on_rus_netting(monkeypatch):
    monkeypatch.setattr(
        config.Config,
        'BILLING_COUNTRIES_WITH_ORDER_BILLINGS_SUBVENTION_NETTING',
        {'rus': '2000-01-01'},
    )


def _turn_on_kaz_netting(monkeypatch):
    monkeypatch.setattr(
        config.Config,
        'BILLING_COUNTRIES_WITH_ORDER_BILLINGS_SUBVENTION_NETTING',
        {'kaz': '2000-01-01'},
    )


def _turn_on_driver_fix_park_commission_sending(monkeypatch):
    monkeypatch.setattr(
        config.Config, 'BILLING_SEND_DRIVER_FIX_PARK_COMMISSION', True,
    )


def _turn_on_driver_fix_create_minutes_income_journal(monkeypatch):
    monkeypatch.setattr(
        config.Config,
        'BILLING_SUBVENTIONS_WRITE_DRIVER_FIX_INCOME_MINUTES',
        True,
    )


def _turn_on_create_order_income_doc(monkeypatch):
    monkeypatch.setattr(
        config.Config, 'BILLING_SUBVENTIONS_CREATE_ORDER_INCOME_DOC', True,
    )


def _turn_on_reverse_on_order_amended(monkeypatch):
    monkeypatch.setattr(
        config.Config, 'BILLING_REVERSE_DOC_ON_ORDER_AMENDED', True,
    )


def _turn_on_use_reports_for_orfb(monkeypatch):
    monkeypatch.setattr(
        config.Config, 'BILLING_SUBVENTIONS_USE_REPORTS_FOR_ORFB', True,
    )


def _turn_on_check_rebill_allowed(monkeypatch):
    monkeypatch.setattr(config.Config, 'BILLING_CHECK_REBILL_ALLOWED', True)


def _set_check_marketing_contract(monkeypatch):
    monkeypatch.setattr(
        config.Config,
        'BILLING_SUBVENTIONS_CHECK_MARKETING_CONTRACT',
        '2018-01-01T00:00:00+00:00',
    )
    monkeypatch.setattr(
        config.Config,
        'BILLING_SUBVENTIONS_CHECK_CONTRACT_ORFB',
        '2018-01-01T00:00:00+00:00',
    )


def _set_contract_delay(monkeypatch, delay, retry):
    monkeypatch.setattr(
        config.Config, 'BILLING_SUBVENTIONS_CONTRACT_DELAY_ENABLED', True,
    )
    monkeypatch.setattr(
        config.Config, 'BILLING_SUBVENTIONS_CONTRACT_DELAY', delay,
    )
    monkeypatch.setattr(
        config.Config, 'BILLING_SUBVENTIONS_CONTRACT_RETRY', retry,
    )


def _set_skip_no_contract_subvention_events(monkeypatch, skip: bool):
    monkeypatch.setattr(
        config.Config,
        'BILLING_SUBVENTIONS_SKIP_NO_CONTRACT_SUBVENTION_EVENTS',
        skip,
    )


def _set_no_billing_client_id_zones(monkeypatch):
    monkeypatch.setattr(
        config.Config,
        'BILLING_SUBVENTIONS_NO_BILLING_CLIENT_ID_ZONES',
        ['kazan'],
    )


def _fill_tlog_service_ids(monkeypatch):
    monkeypatch.setattr(
        config.Config,
        'BILLING_TLOG_SERVICE_IDS',
        {
            'card': 124,
            'cargo_commission/card': 1163,
            'cargo_commission/cash': 1161,
            'childchair': 111,
            'cargo_childchair': 1161,
            'client_b2b_drive_payment': 672,
            'client_b2b_trip_payment': 650,
            'commission/card': 128,
            'commission/cash': 111,
            'commission/driver_fix': 128,
            'coupon/netted': 111,
            'coupon/paid': 137,
            'cargo_coupon/netted': 1161,
            'cargo_coupon/paid': 1164,
            'driver_referrals': 137,
            'food_payment': 668,
            'park_b2b_trip_payment': 651,
            'park_b2b_fixed_commission': 697,
            'partner_scoring': 128,
            'scout': 619,
            'subvention/netted': 111,
            'subvention/paid': 137,
            'cargo_subvention/netted': 1161,
            'cargo_subvention/paid': 1164,
            'uber': 125,
        },
    )


def _fill_arbitrary_configs(monkeypatch, configs: dict):
    for key, value in configs.items():
        monkeypatch.setattr(config.Config, key, value)


def _turn_on_send_contract_id_for_subventions(monkeypatch):
    monkeypatch.setattr(
        config.Config,
        'BILLING_SUBVENTIONS_SEND_CONTRACT_ID_FOR_SUBVENTIONS',
        True,
    )


def _patch_random(patch):
    @patch('random.randint')
    def _randint(left, right):
        del right  # unused
        return left


def _patch_uuid(patch):
    @patch('uuid.uuid4')
    def uuid4():
        return uuid.UUID('11111111111111111111111111111111')


def _patch_order_commission_enabled_check(patch):
    @patch(
        'taxi_billing_subventions.process_doc._order_commission_changed.'
        'OrderCommissionChangedProducer.skip_event',
    )
    def _skip(*args, **kwargs):
        # pylint: disable=unused-argument
        return False


def _sorted_docs(docs):
    return sorted(
        docs,
        key=lambda doc: (doc['external_obj_id'], doc['external_event_ref']),
    )


def _docs_with_sorted_tags(docs):
    docs_with_sorted_tags = []
    for doc in docs:
        if 'tags' in doc:
            doc['tags'] = sorted(doc['tags'])
        docs_with_sorted_tags.append(doc)
    return docs_with_sorted_tags


def _convert_docs_to_v1(docs: List[Dict]) -> List[Dict]:
    formatted_docs: List[Dict] = []
    for one_doc in docs:
        if 'topic' in one_doc:
            one_doc['external_obj_id'] = one_doc.pop('topic')
        if 'external_ref' in one_doc:
            one_doc['external_event_ref'] = one_doc.pop('external_ref')
        formatted_docs.append(one_doc)
    return formatted_docs


def _assert_same_entities(expected, actual):
    assert _sorted_entities(expected) == _sorted_entities(actual)


def _assert_docs_equal(expected_docs, actual_docs):
    __tracebackhide__ = True
    expected = list(map(_decimalize_amounts, expected_docs))
    actual = list(map(_decimalize_amounts, actual_docs))
    for actual_doc, expected_doc in itertools.zip_longest(actual, expected):
        assert actual_doc == expected_doc


def _decimalize_amounts(doc):
    decimalized = copy.deepcopy(doc)
    if 'journal_entries' in decimalized:
        for entry in decimalized['journal_entries']:
            entry['amount'] = decimal.Decimal(entry['amount'])
    if decimalized['kind'] == 'subvention_antifraud_check':
        for key in ['block', 'execute', 'unhold_verification']:
            for entry in decimalized['data']['journal_entries'][key]:
                entry['amount'] = decimal.Decimal(entry['amount'])
        if 'subventions_input' in decimalized['data']:
            subventions_input = decimalized['data']['subventions_input']
            if subventions_input:
                for detail in subventions_input['rule_details']:
                    detail['value'] = _parse_money(detail['value'])
    if decimalized['kind'] == 'subventions_input_enrichment_needed':
        for detail in decimalized['data']['rule_details']:
            detail['value'] = _parse_money(detail['value'])
    return decimalized


def _parse_money(value):
    amount_str, currency = value.split()
    return billing.Money(decimal.Decimal(amount_str), currency)


def _sorted_entities(entities):
    return sorted(entities, key=_by_external_id)


def _by_external_id(entity):
    return entity['external_id']


async def _find_actual_holded_subvention(db, billing_v2_id):
    query = {'billing_v2_id': billing_v2_id}
    cursor = db.dry_holded_subventions.find(query)
    docs = await cursor.to_list(None)
    return {
        a_doc['_id']: {
            'force_hold': a_doc['force_hold'],
            'events': a_doc['events'],
        }
        for a_doc in docs
    }
