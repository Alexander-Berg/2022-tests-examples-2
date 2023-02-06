import copy
import dataclasses
import datetime as dt
from typing import Collection
from typing import Iterable
from typing import List
from typing import Optional

from taxi.billing import util
from taxi.billing.util import dates

from billing.accounts import service as aservice
from billing.docs import service as dservice


class TestEntities(aservice.Entities):
    def __init__(self):
        self.items: List[aservice.Entity] = []

    async def create(
            self, request: aservice.EntityCreateRequest,
    ) -> aservice.Entity:
        entity = await self.search(request.external_id)
        if entity:
            return entity
        entity = aservice.Entity(
            external_id=request.external_id, kind=request.kind,
        )
        self.items.append(entity)
        return entity

    async def search(self, external_id: str) -> Optional[aservice.Entity]:
        for item in self.items:
            if item.external_id == external_id:
                return item
        return None


class TestAccounts(aservice.Accounts):
    def __init__(self):
        self.items: List[aservice.Account] = []

    async def create(
            self, request: aservice.AccountCreateRequest,
    ) -> aservice.Account:
        afilter = aservice.AccountSearchByKeyRequest.Filter(
            entity_external_id=request.entity_external_id,
            agreement_id=request.agreement_id,
            currency=request.currency,
            sub_account=request.sub_account,
        )
        search = aservice.AccountSearchByKeyRequest([afilter])
        accounts = await self.search_by_key(search)
        if accounts:
            assert len(accounts) == 1
            return accounts[0]
        next_id = len(self.items) + 1
        account = aservice.Account(
            id=next_id,
            entity_external_id=request.entity_external_id,
            agreement_id=request.agreement_id,
            currency=request.currency,
            sub_account=request.sub_account,
        )
        self.items.append(account)
        return account

    async def update(
            self, request: aservice.AccountUpdateRequest,
    ) -> aservice.AccountUpdateResponse:
        return aservice.AccountUpdateResponse(
            account_id=request.account_id,
            data=request.data,
            doc_ref=request.doc_ref,
            idempotency_key=request.idempotency_key,
            created=dates.utc_now_with_tz(),
        )

    async def search_by_key(
            self, request: aservice.AccountSearchByKeyRequest,
    ) -> List[aservice.Account]:
        result = []
        for item in self.items:
            for afilter in request.filters:
                if (
                        afilter.entity_external_id
                        in [item.entity_external_id, None]
                        and afilter.agreement_id in [item.agreement_id, None]
                        and afilter.sub_account in [item.sub_account, None]
                        and afilter.currency in [item.currency, None]
                ):
                    result.append(item)
        return result

    async def search_by_id(
            self, request: aservice.AccountSearchByIdRequest,
    ) -> List[aservice.Account]:
        result = []
        for item in self.items:
            if item.id in request.account_ids:
                result.append(item)
        return result


class TestJournal(aservice.Journal):
    def __init__(
            self,
            accounts: TestAccounts,
            now: dt.datetime,
            max_entries_age_days: int,
            replication_lag_ms: int,
    ):
        self._now = now
        self._accounts = accounts
        self._max_age_for_new_entries = dt.timedelta(days=max_entries_age_days)
        self._replication_lag = dt.timedelta(milliseconds=replication_lag_ms)
        self.items: List[aservice.AppendedEntry] = []

    async def select_by_account(
            self, request: aservice.JournalByAccountRequest,
    ) -> List[aservice.SelectedEntry]:
        result = []
        for item in self.items:
            account = self._accounts.items[item.account_id - 1]
            for afilter in request.accounts:
                if (
                        afilter.entity_external_id
                        in [account.entity_external_id, None]
                        and afilter.agreement_id
                        in [account.agreement_id, None]
                        and afilter.sub_account in [account.sub_account, None]
                        and afilter.currency in [account.currency, None]
                        and request.begin_time
                        <= item.event_at
                        < request.end_time
                ):
                    selected = aservice.SelectedEntry(
                        id=item.account_id,
                        account_id=account.id,
                        entity_external_id=account.entity_external_id,
                        agreement_id=account.agreement_id,
                        currency=account.currency,
                        sub_account=account.sub_account,
                        amount=item.amount,
                        event_at=dates.ensure_aware(item.event_at),
                        created=dates.ensure_aware(item.created),
                        details=item.details,
                    )
                    result.append(selected)
        return result

    async def select_by_id(
            self, entry_ids: Collection[int],
    ) -> List[aservice.SelectedEntry]:
        result = []
        for item in self.items:
            account = self._accounts.items[item.account_id - 1]
            if item.id in entry_ids:
                selected = aservice.SelectedEntry(
                    id=item.id,
                    account_id=account.id,
                    entity_external_id=account.entity_external_id,
                    agreement_id=account.agreement_id,
                    currency=account.currency,
                    sub_account=account.sub_account,
                    amount=item.amount,
                    event_at=dates.ensure_aware(item.event_at),
                    created=dates.ensure_aware(item.created),
                    details=item.details,
                )
                result.append(selected)
        return result

    async def append(
            self, entries: Iterable[aservice.CreateEntryRequest],
    ) -> List[aservice.AppendedEntry]:
        result = []
        for entry in entries:
            if entry.account_id > len(self._accounts.items):
                raise ValueError(f'Account {entry.account_id} not found')
            if entry.idempotency_key is None:
                idempotency_key = str(entry.account_id)
            else:
                idempotency_key = entry.idempotency_key
            if len(idempotency_key) > 64:
                raise ValueError(
                    f'Invalid value for idempotency_key: "{idempotency_key}" '
                    'length must be less than or equal to 64',
                )
            appended = aservice.AppendedEntry(
                id=len(self.items) + 1,
                account_id=entry.account_id,
                amount=entry.amount,
                event_at=dates.ensure_aware(entry.event_at),
                created=self._now,
                details=entry.details,
                idempotency_key=idempotency_key,
                doc_ref=entry.doc_ref,
            )
            for item in self.items:
                item_key = f'{item.doc_ref}/{item.idempotency_key}'
                appended_key = f'{appended.doc_ref}/{appended.idempotency_key}'
                if item_key == appended_key:
                    break
            else:
                self.items.append(appended)
            result.append(appended)
        return result

    async def append_if(
            self, entry: aservice.AppendIfRequest,
    ) -> aservice.AppendedIfEntry:
        pass

    @property
    def max_age_for_new_entries(self) -> dt.timedelta:
        return self._max_age_for_new_entries

    @property
    def replication_lag(self) -> dt.timedelta:
        return self._replication_lag


class TestDocs(dservice.Docs):
    def __init__(self, replication_lag_ms: int = 0):
        self.items: List[dservice.Doc] = []
        self._replication_lag = dt.timedelta(milliseconds=replication_lag_ms)

    async def create(self, request: dservice.CreateDocRequest) -> dservice.Doc:
        doc = await self.get_by_key(
            topic=request.topic, external_ref=request.external_ref,
        )
        if doc:
            return doc
        next_id = len(self.items) + 1
        doc = dservice.Doc(
            id=next_id,
            kind=request.kind,
            topic=request.topic,
            external_ref=request.external_ref,
            event_at=request.event_at,
            process_at=request.process_at,
            status=request.status,
            data=request.data,
            entry_ids=[],
            revision=1,
        )
        self.items.append(doc)
        return doc

    async def get_by_id(
            self, doc_id: int, use_archive: bool = False,
    ) -> Optional[dservice.GetByIdResponse]:
        for item in self.items:
            if item.id == doc_id:
                return dservice.GetByIdResponse(item, False)
        return None

    async def get_by_key(
            self, topic: str, external_ref: str,
    ) -> Optional[dservice.Doc]:
        for item in self.items:
            if item.topic == topic and item.external_ref == external_ref:
                return item
        return None

    async def update(
            self, request: dservice.UpdateDocRequest,
    ) -> dservice.DocUpdate:
        for i, doc in enumerate(self.items):
            if doc.id != request.doc_id:
                continue
            data = copy.deepcopy(doc.data)
            data.update(**request.data)
            updated = dataclasses.replace(
                doc,
                data=data,
                entry_ids=[*doc.entry_ids, *request.entry_ids],
                status=request.status,
                revision=request.revision + 1,
            )
            self.items[i] = updated
            return dservice.DocUpdate(
                data=updated.data,
                entry_ids=request.entry_ids,
                revision=util.not_none(updated.revision),
                status=request.status,
            )
        raise ValueError

    async def select(
            self,
            request: dservice.SelectDocsRequest,
            secondary_preferred: bool,
    ) -> List[dservice.Doc]:
        del secondary_preferred  # unused
        return [
            item
            for item in self.items
            if request.topic == item.topic
            and request.external_ref in [None, item.external_ref]
            and request.kind in [None, item.kind]
            and request.begin_time <= item.event_at < request.end_time
        ]

    def _topic(self, topic: str) -> List[dservice.Doc]:
        return list(filter(lambda x: x.topic == topic, self.items))

    async def is_ready_for_processing(self, doc_id: int) -> bool:
        response = await self.get_by_id(doc_id)
        if not response:
            raise ValueError
        for i, doc in enumerate(self._topic(response.doc.topic)):
            if doc.id != doc_id:
                continue
            if i == 0:
                return True
            return self.items[i - 1].is_completed
        raise ValueError(f'Doc {doc_id} not found')

    async def finish_processing(self, doc_id: int):
        for i, doc in enumerate(self.items):
            if doc.id == doc_id:
                self.items[i] = dataclasses.replace(doc, status='complete')
                return
        raise ValueError(f'Doc {doc_id} not found')

    async def restore(self, doc_id: int, idempotency_key: str):
        return

    @property
    def replication_lag(self) -> dt.timedelta:
        return self._replication_lag
