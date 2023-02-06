from __future__ import annotations

import datetime
import decimal


from aiohttp import web
import pytest

from billing.accounts import service


async def test_accounts_get_balances_queries_billing_accounts(
        library_context, account, balances_select, load_json,
):
    _ = await _get_balances(library_context, account)
    assert balances_select.times_called == 1
    assert balances_select.next_call()['request'].json == load_json(
        'v2_balances_select_request.json',
    )


async def test_accounts_get_balances_returns_found_balances(
        library_context, account, balances_select,
):
    balances = await _get_balances(library_context, account)
    assert balances == [
        service.AccountBalance(account=account, balance=decimal.Decimal(10)),
    ]


async def _get_balances(library_context, account):
    account_key = service.AccountKey(
        entity_external_id=account.entity_external_id,
        agreement_id=account.agreement_id,
        currency=account.currency,
        sub_account=account.sub_account,
    )
    return await library_context.balances.get_balances_for_period(
        accounts=[account_key],
        start=datetime.datetime(2021, 1, 31, 21, tzinfo=datetime.timezone.utc),
        end=datetime.datetime(2021, 2, 28, 21, tzinfo=datetime.timezone.utc),
    )


@pytest.fixture(name='account')
def make_account():
    return service.Account(
        id=1,
        entity_external_id='entity_id',
        agreement_id='agreement_id',
        currency='currency',
        sub_account='sub_account',
    )


@pytest.fixture(name='balances_select')
def mock_balances_select(mock_billing_accounts, load_json):
    @mock_billing_accounts('/v2/balances/select')
    def _balances_select(request):
        return web.json_response(load_json('v2_balances_select_response.json'))

    yield _balances_select


async def test_accounts_journal_select_by_ids_returns_entries(
        library_context, account, mock_journal_by_id,
):
    entries = await library_context.journal.select_by_id([1234567890])
    assert entries == [
        service.SelectedEntry(
            id=1234567890,
            account_id=6,
            entity_external_id='entity_id',
            agreement_id='agreement_id',
            currency='currency',
            sub_account='sub_account',
            amount=decimal.Decimal('100.0'),
            event_at=datetime.datetime(
                2021, 2, 28, 21, tzinfo=datetime.timezone.utc,
            ),
            created=datetime.datetime(
                2021, 1, 31, 21, tzinfo=datetime.timezone.utc,
            ),
            details=None,
        ),
    ]


async def test_accounts_journal_select_by_ids_raises(
        library_context, account, mock_journal_by_id,
):
    with pytest.raises(ValueError):
        await library_context.journal.select_by_id_or_die([1, 2, 3, 4, 5, 6])


@pytest.fixture(name='mock_journal_by_id')
def make_mock_journal_by_id(mock_billing_reports, load_json):
    @mock_billing_reports('/v1/journal/by_id')
    def _journal_by_id(request):
        return web.json_response(load_json('v1_journal_by_id_response.json'))

    yield _journal_by_id
