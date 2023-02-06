import copy
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from taxi.billing.util import dates

from test_taxi_billing_calculators import common


class BillingAccountsClient:
    def __init__(self, existing_accounts=None):
        self._created_accounts = (
            existing_accounts if existing_accounts is not None else []
        )
        self._created_entities = []
        self._next_account_id = len(self._created_accounts) + 1

    async def search_accounts(
            self,
            *,
            entity_external_id: str,
            agreement_id: Optional[str],
            currency: Optional[str],
            sub_account: Optional[str],
            log_extra=None,
    ) -> List[Dict[str, Any]]:
        search_account = {'entity_external_id': entity_external_id}
        if agreement_id:
            search_account['agreement_id'] = agreement_id
        if currency:
            search_account['currency'] = currency
        if sub_account:
            search_account['sub_account'] = sub_account

        found = [
            account
            for account in self._created_accounts
            if (
                all(item in account.items() for item in search_account.items())
            )
        ]

        return found

    async def search_accounts_v2(
            self, *accounts: dict, log_extra: dict = None,
    ) -> dict:
        result = []
        for account in accounts:
            if account.get('account_id'):
                result.append(self._created_accounts[account['account_id']])
            else:
                result.extend(
                    await self.search_accounts(
                        entity_external_id=account['entity_external_id'],
                        agreement_id=account.get('agreement_id'),
                        currency=account.get('currency'),
                        sub_account=account.get('sub_account'),
                    ),
                )
        return {'accounts': result}

    async def create_account(self, data: dict, log_extra=None) -> dict:
        self.created_accounts.append(data)
        data['account_id'] = self._next_account_id
        self._next_account_id += 1
        return self.created_accounts[-1]

    async def search_entities(self, external_id: str, log_extra=None) -> list:
        return list(
            filter(
                lambda item: item['external_id'] == external_id,
                self._created_entities,
            ),
        )

    async def create_entity(self, data: dict, log_extra=None) -> dict:
        self._created_entities.append(data)
        return {}

    @property
    def created_accounts(self):
        return self._created_accounts

    @property
    def created_entities(self):
        return self._created_entities


class BillingDocsClient:
    next_doc_id = 77777

    def __init__(self, existing_docs=None):
        self._created_docs = []
        self._existing_docs = (
            existing_docs if existing_docs is not None else []
        )

    async def create(self, data: dict, log_extra=None) -> dict:
        new_doc = copy.deepcopy(data)
        new_doc['doc_id'] = self.next_doc_id
        self.next_doc_id += 1
        self._created_docs.append(data)
        return new_doc

    async def execute_v2(self, data: dict, log_extra=None) -> list:
        doc_to_create = data['docs'][0]
        new_doc = copy.deepcopy(doc_to_create)
        new_doc['doc_id'] = self.next_doc_id
        self.next_doc_id += 1
        doc_to_create['external_obj_id'] = doc_to_create.pop('topic')
        doc_to_create['external_event_ref'] = doc_to_create.pop('external_ref')
        doc_to_create['status'] = 'new'
        self._created_docs.append(doc_to_create)
        return [new_doc]

    async def search(self, query: dict, log_extra=None) -> list:
        query.pop('use_master')
        found = [
            doc
            for doc in self._existing_docs
            if (all(item in doc.items() for item in query.items()))
        ]
        return found

    @property
    def created_docs(self):
        return self._created_docs


class BillingReportsClient:
    def __init__(self, existing_docs=None):
        self._existing_docs = (
            existing_docs if existing_docs is not None else []
        )

    async def select_all_docs(
            self, query: dict, max_num_iterations: int, log_extra=None,
    ) -> list:
        return [
            doc
            for doc in self._existing_docs
            if (doc['external_obj_id'] == query['external_obj_id'])
        ]

    async def get_journal_entries(self, query, log_extra=None) -> list:
        assert 'doc_ref' in query, query
        doc_id = int(query['doc_ref'])
        begin_time = query['begin_time']
        end_time = query['end_time']
        for doc in self._existing_docs:
            if doc['doc_id'] == doc_id:
                return [
                    entry
                    for entry in doc['journal_entries']
                    if dates.parse_datetime(begin_time)
                    <= dates.parse_datetime(entry['event_at'])
                    < dates.parse_datetime(end_time)
                ]
        return []


class BillingTLogApiClient:
    def __init__(self):
        self._entries = []

    async def journal_append(self, entries, **opts):
        self._entries.extend(entries)
        return {'entries': common.make_tlog_response_entries(entries)}

    async def journal_append_v2(self, entries, **opts):
        self._entries.extend(entries)
        return {'entries': common.make_tlog_response_entries(entries)}

    @property
    def entries(self):
        return self._entries


class ProcessingApiClient:
    def __init__(self):
        self._processing_requests = []

    async def v1_scope_queue_create_event(
            self,
            item_id: str,
            x_idempotency_token: str,
            queue: str,
            scope: str,
            data: Dict,
            *,
            log_extra: Optional[dict] = None,
    ):
        self._processing_requests.append(
            {
                'item_id': item_id,
                'x_idempotency_token': x_idempotency_token,
                'queue': queue,
                'scope': scope,
                'data': data,
            },
        )

    @property
    def processing_requests(self):
        return self._processing_requests


class BillingLimitsApiClient:
    def __init__(self):
        self.entries = []
        self.tokens = []

    async def v1_deposit(self, data: dict, token: str, **opts):
        self.tokens.append(token)
        self.entries.append(data)


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
