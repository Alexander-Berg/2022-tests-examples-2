# pylint: disable=redefined-outer-name

import datetime
import decimal

import aiohttp
import pytest
import pytz

from taxi import config
from taxi import discovery
from taxi.billing.clients import billing_reports
from taxi.billing.clients.models import billing_reports as reports_models


@pytest.fixture
async def test_client():
    """
    Client fixture for API tests
    """

    class Config(config.Config):
        BILLING_REPORTS_CLIENT_QOS = {
            '__default__': {'attempts': 5, 'timeout-ms': 500},
        }

    session = aiohttp.ClientSession()
    yield billing_reports.BillingReportsApiClient(
        service=discovery.find_service('billing_reports'),
        session=session,
        config=Config(),
        api_token='secret',
    )
    await session.close()


@pytest.fixture
async def response_entry():
    """
    Fixture of transaction that should be returned in valid response.
    """
    account = reports_models.ReportsAccount(
        account_id=100200,
        entity_external_id='test',
        agreement_id='12345',
        currency='XXX',
        sub_account='test',
    )

    entry = reports_models.JournalEntry(
        account=account,
        amount=decimal.Decimal('25.10'),
        event_at=datetime.datetime(2019, 7, 26, 15, tzinfo=pytz.utc),
        created=datetime.datetime(2019, 7, 26, 13, tzinfo=pytz.utc),
        reason='treason',
        entry_id=16950035,
        doc_ref='77007700',
    )
    return entry


async def test_billing_reports_select_journal_client(
        test_client, mockserver, response_mock, response_entry,
):
    @mockserver.json_handler('/billing-reports/v1/journal/select')
    async def _mock_journal_select(request, *args, **kwargs):
        return {
            'entries': [
                {
                    'entry_id': 16950035,
                    'account': {
                        'account_id': 100200,
                        'entity_external_id': 'test',
                        'agreement_id': '12345',
                        'currency': 'XXX',
                        'sub_account': 'test',
                    },
                    'amount': '25.10',
                    'doc_ref': '77007700',
                    'event_at': '2019-07-26T15:00:00.000000+00:00',
                    'created': '2019-07-26T13:00:00.000000+00:00',
                    'details': None,
                    'reason': 'treason',
                },
            ],
            'cursor': {},
        }

    query_account = reports_models.ReportsAccount(
        entity_external_id='test', agreement_id='12345', currency='XXX',
    )

    query_data = reports_models.ReportsJournalSelectRequest(
        accounts=[query_account],
        begin_time=datetime.datetime.now(tz=datetime.timezone.utc)
        - datetime.timedelta(days=30),
        end_time=datetime.datetime.now(tz=datetime.timezone.utc)
        + datetime.timedelta(days=30),
        limit=5,
        cursor={},
    )
    response = await test_client.select_journal(query=query_data)

    assert response.entries == [response_entry]
    assert response.cursor == {}


async def test_billing_reports_journal_tag_client(
        test_client,
        patch_aiohttp_session,
        response_mock,
        response_entry,
        mockserver,
):
    @mockserver.json_handler('/billing-reports/v2/journal/by_tag')
    async def _mock_journal_by_tag(request, *args, **kwargs):
        return {
            'entries': {
                'test_tag': [
                    {
                        'entry_id': 16950035,
                        'account': {
                            'account_id': 100200,
                            'entity_external_id': 'test',
                            'agreement_id': '12345',
                            'currency': 'XXX',
                            'sub_account': 'test',
                        },
                        'amount': '25.10',
                        'doc_ref': '77007700',
                        'event_at': '2019-07-26T15:00:00.000000+00:00',
                        'created': '2019-07-26T13:00:00.000000+00:00',
                        'details': None,
                        'reason': 'treason',
                    },
                ],
            },
        }

    query_account = reports_models.ReportsTagAccount(entity_external_id='test')

    query_data = reports_models.ReportsJournalTagRequest(
        accounts=[query_account],
        tags=['test_tag'],
        begin_time=datetime.datetime.now(tz=datetime.timezone.utc)
        - datetime.timedelta(days=30),
        end_time=datetime.datetime.now(tz=datetime.timezone.utc)
        + datetime.timedelta(days=30),
    )
    response = await test_client.journal_by_tag(query=query_data)

    assert response.entries == {'test_tag': [response_entry]}


async def test_get_balances(
        test_client,
        patch_aiohttp_session,
        response_mock,
        response_entry,
        mockserver,
):
    @mockserver.json_handler('/billing-reports/v1/balances/select')
    async def _mock_balances_select(request, *args, **kwargs):
        return {
            'entries': [
                {
                    'account': {
                        'account_id': 31370003,
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'RUB',
                        'entity_external_id': 'unique_driver_id/5adf9c23',
                        'sub_account': 'income',
                    },
                    'balances': [
                        {
                            'accrued_at': '2018-10-03T23:59:00.000000+00:00',
                            'balance': '10',
                        },
                    ],
                },
            ],
        }

    query_account = reports_models.ReportsTagAccount(
        entity_external_id='unique_driver_id/5adf9c23',
    )

    query_data = reports_models.BalancesSelectRequest(
        accounts=[query_account],
        accrued_at=[datetime.datetime(2018, 10, 3, 23, 59, tzinfo=pytz.utc)],
    )
    response = await test_client.get_balances(query=query_data)

    assert len(response.entries) == 1
    assert response.entries[0].account.account_id == 31370003
    assert len(response.entries[0].balances) == 1
    assert response.entries[0].balances[0].balance == decimal.Decimal(10)
