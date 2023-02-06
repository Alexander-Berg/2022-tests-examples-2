import datetime as dt

import pytest

from taxi_billing_reports.actions import journal_select
from taxi_billing_reports.actions import v2_journal_select
from taxi_billing_reports.models import account
from taxi_billing_reports.models import journal_select as journal_select_models


@pytest.mark.parametrize(
    'now,begin_time,end_time,offets,expected_ranges',
    [
        (
            dt.datetime(2019, 1, 10, 0, 0, 0),
            dt.datetime(2019, 1, 1, 0, 0, 0),
            dt.datetime(2019, 1, 10, 0, 0, 0),
            [[6], [12]],
            [
                [
                    (
                        dt.datetime(2019, 1, 9, 18, 0, 0),
                        dt.datetime(2019, 1, 10, 0, 0, 0),
                    ),
                ],
                [
                    (
                        dt.datetime(2019, 1, 9, 6, 0, 0),
                        dt.datetime(2019, 1, 9, 18, 0, 0),
                    ),
                ],
                [
                    (
                        dt.datetime(2019, 1, 1, 0, 0, 0),
                        dt.datetime(2019, 1, 9, 6, 0, 0),
                    ),
                ],
            ],
        ),
        # end in the far future
        (
            dt.datetime(2019, 1, 10, 0, 0, 0),
            dt.datetime(2019, 1, 1, 0, 0, 0),
            dt.datetime(2020, 1, 1, 0, 0, 0),
            [[6], [12]],
            [
                [
                    (
                        dt.datetime(2019, 1, 9, 18, 0, 0),
                        dt.datetime(2020, 1, 1, 0, 0, 0),
                    ),
                ],
                [
                    (
                        dt.datetime(2019, 1, 9, 6, 0, 0),
                        dt.datetime(2019, 1, 9, 18, 0, 0),
                    ),
                ],
                [
                    (
                        dt.datetime(2019, 1, 1, 0, 0, 0),
                        dt.datetime(2019, 1, 9, 6, 0, 0),
                    ),
                ],
            ],
        ),
        # no split
        (
            dt.datetime(2019, 1, 10, 0, 0, 0),
            dt.datetime(2019, 1, 1, 0, 0, 0),
            dt.datetime(2019, 1, 10, 0, 0, 0),
            [],
            [
                [
                    (
                        dt.datetime(2019, 1, 1, 0, 0, 0),
                        dt.datetime(2019, 1, 10, 0, 0, 0),
                    ),
                ],
            ],
        ),
        # out of range
        (
            dt.datetime(2019, 1, 1, 1, 0, 0),
            dt.datetime(2019, 1, 1, 0, 0, 0),
            dt.datetime(2019, 1, 1, 1, 0, 0),
            [[6], [12]],
            [
                [
                    (
                        dt.datetime(2019, 1, 1, 0, 0, 0),
                        dt.datetime(2019, 1, 1, 1, 0, 0),
                    ),
                ],
            ],
        ),
        # bad range
        (
            dt.datetime(2019, 1, 1, 10, 0, 0),
            dt.datetime(2019, 1, 1, 10, 0, 0),
            dt.datetime(2019, 1, 1, 0, 0, 0),
            [[6], [12]],
            [],
        ),
        # begin, end in the future
        (
            dt.datetime(2019, 1, 1, 1, 0, 0),
            dt.datetime(2020, 1, 1, 0, 0, 0),
            dt.datetime(2020, 9, 1, 1, 0, 0),
            [[6], [12]],
            [
                [
                    (
                        dt.datetime(2020, 1, 1, 0, 0, 0),
                        dt.datetime(2020, 9, 1, 1, 0, 0),
                    ),
                ],
            ],
        ),
    ],
)
async def test_query_range(now, begin_time, end_time, offets, expected_ranges):

    # pylint: disable=protected-access
    ranges = list(
        journal_select._query_range(
            now=now, start=begin_time, end=end_time, offset_hours=offets,
        ),
    )
    assert ranges == expected_ranges


@pytest.mark.parametrize(
    'accounts_whitelist,accounts_blacklist,real_accounts,expected',
    [
        (
            [
                account.Account.from_json(
                    {
                        'entity_external_id': 'e1',
                        'agreement_id': 'foo_bar%',
                        'currency': 'XXX',
                    },
                ),
            ],
            [],
            [
                {
                    'entity_external_id': 'e1',
                    'agreement_id': 'foo_bar',
                    'currency': 'XXX',
                    'sub_account': 's1',
                },
                {
                    'entity_external_id': 'e1',
                    'agreement_id': 'foo_bar',
                    'currency': 'XXX',
                    'sub_account': 's2',
                },
                {
                    'entity_external_id': 'e1',
                    'agreement_id': 'foo_bar_taz',
                    'currency': 'XXX',
                    'sub_account': 's1',
                },
                {
                    'entity_external_id': 'e1',
                    'agreement_id': '_foo_bar',
                    'currency': 'XXX',
                    'sub_account': 's1',
                },
            ],
            [
                journal_select_models.V2JournalSelectYtAccount(
                    entity_external_id='e1',
                    agreement_id='foo_bar',
                    currency='XXX',
                    sub_accounts=[None],
                    skip_sub_accounts=[],
                ),
                journal_select_models.V2JournalSelectYtAccount(
                    entity_external_id='e1',
                    agreement_id='foo_bar_taz',
                    currency='XXX',
                    sub_accounts=[None],
                    skip_sub_accounts=[],
                ),
            ],
        ),
        (
            [
                account.Account.from_json(
                    {
                        'entity_external_id': 'e1',
                        'agreement_id': 'foo_bar%',
                        'currency': 'XXX',
                    },
                ),
            ],
            [account.Account.from_json({'agreement_id': '%taz%'})],
            [
                {
                    'entity_external_id': 'e1',
                    'agreement_id': 'foo_bar',
                    'currency': 'XXX',
                    'sub_account': 's1',
                },
                {
                    'entity_external_id': 'e1',
                    'agreement_id': 'foo_bar',
                    'currency': 'XXX',
                    'sub_account': 's2',
                },
                {
                    'entity_external_id': 'e1',
                    'agreement_id': 'foo_bar_taz',
                    'currency': 'XXX',
                    'sub_account': 's1',
                },
                {
                    'entity_external_id': 'e1',
                    'agreement_id': '_foo_bar',
                    'currency': 'XXX',
                    'sub_account': 's1',
                },
            ],
            [
                journal_select_models.V2JournalSelectYtAccount(
                    entity_external_id='e1',
                    agreement_id='foo_bar',
                    currency='XXX',
                    sub_accounts=[None],
                    skip_sub_accounts=[],
                ),
            ],
        ),
        (
            [
                account.Account.from_json(
                    {
                        'entity_external_id': 'e1',
                        'agreement_id': 'foo_bar%',
                        'currency': 'XXX',
                    },
                ),
            ],
            [account.Account.from_json({'sub_account': 's1'})],
            [
                {
                    'entity_external_id': 'e1',
                    'agreement_id': 'foo_bar',
                    'currency': 'XXX',
                    'sub_account': 's1',
                },
                {
                    'entity_external_id': 'e1',
                    'agreement_id': 'foo_bar',
                    'currency': 'XXX',
                    'sub_account': 's2',
                },
                {
                    'entity_external_id': 'e1',
                    'agreement_id': 'foo_bar_taz',
                    'currency': 'XXX',
                    'sub_account': 's1',
                },
                {
                    'entity_external_id': 'e1',
                    'agreement_id': '_foo_bar',
                    'currency': 'XXX',
                    'sub_account': 's1',
                },
            ],
            [
                journal_select_models.V2JournalSelectYtAccount(
                    entity_external_id='e1',
                    agreement_id='foo_bar',
                    currency='XXX',
                    sub_accounts=[None],
                    skip_sub_accounts=['s1'],
                ),
            ],
        ),
        (
            [
                account.Account.from_json(
                    {
                        'entity_external_id': 'e1',
                        'agreement_id': 'foo_bar',
                        'currency': 'XXX',
                    },
                ),
            ],
            [
                account.Account.from_json(
                    {
                        'entity_external_id': 'e1',
                        'agreement_id': 'foo_bar',
                        'currency': 'XXX',
                    },
                ),
            ],
            [],
            [
                journal_select_models.V2JournalSelectYtAccount(
                    entity_external_id='e1',
                    agreement_id='foo_bar',
                    currency='XXX',
                    sub_accounts=[None],
                    skip_sub_accounts=[None],
                ),
            ],
        ),
        (
            [
                account.Account.from_json(
                    {
                        'entity_external_id': 'e1',
                        'agreement_id': 'foo%',
                        'currency': 'XXX',
                        'sub_account': 's1',
                    },
                ),
            ],
            [
                account.Account.from_json(
                    {
                        'entity_external_id': 'e1',
                        'agreement_id': '%bar%',
                        'currency': 'XXX',
                    },
                ),
            ],
            [
                {
                    'entity_external_id': 'e1',
                    'agreement_id': 'foo',
                    'currency': 'XXX',
                    'sub_account': 's1',
                },
                {
                    'entity_external_id': 'e1',
                    'agreement_id': 'bar',
                    'currency': 'XXX',
                    'sub_account': 's1',
                },
                {
                    'entity_external_id': 'e1',
                    'agreement_id': 'foobar',
                    'currency': 'XXX',
                    'sub_account': 's1',
                },
            ],
            [
                journal_select_models.V2JournalSelectYtAccount(
                    entity_external_id='e1',
                    agreement_id='foo',
                    currency='XXX',
                    sub_accounts=['s1'],
                    skip_sub_accounts=[],
                ),
            ],
        ),
        (
            [
                account.Account.from_json(
                    {
                        'entity_external_id': 'e1',
                        'agreement_id': 'foo%',
                        'currency': 'XXX',
                    },
                ),
            ],
            [
                account.Account.from_json(
                    {
                        'entity_external_id': 'e1',
                        'agreement_id': '%bar%',
                        'currency': 'XXX',
                        'sub_account': 's2',
                    },
                ),
            ],
            [
                {
                    'entity_external_id': 'e1',
                    'agreement_id': 'foo',
                    'currency': 'XXX',
                    'sub_account': 's1',
                },
                {
                    'entity_external_id': 'e1',
                    'agreement_id': 'bar',
                    'currency': 'XXX',
                    'sub_account': 's1',
                },
                {
                    'entity_external_id': 'e1',
                    'agreement_id': 'foobar',
                    'currency': 'XXX',
                    'sub_account': 's1',
                },
            ],
            [
                journal_select_models.V2JournalSelectYtAccount(
                    entity_external_id='e1',
                    agreement_id='foo',
                    currency='XXX',
                    sub_accounts=[None],
                    skip_sub_accounts=[],
                ),
                journal_select_models.V2JournalSelectYtAccount(
                    entity_external_id='e1',
                    agreement_id='foobar',
                    currency='XXX',
                    sub_accounts=[None],
                    skip_sub_accounts=['s2'],
                ),
            ],
        ),
    ],
)
async def test_v2_expand_filters(
        accounts_whitelist,
        accounts_blacklist,
        real_accounts,
        expected,
        taxi_billing_reports_context,
        mockserver,
):
    @mockserver.json_handler('/billing-accounts/v2/accounts/search')
    def _handle_accounts_search(request):
        return mockserver.make_response(json={'accounts': real_accounts})

    actual = await v2_journal_select.prepare_filters(
        ba_client=taxi_billing_reports_context.ba_client,
        white_list=accounts_whitelist,
        black_list=accounts_blacklist,
        log_extra={},
    )

    def _key(acc):
        return (acc.entity_external_id, acc.agreement_id, acc.currency)

    assert sorted(actual, key=_key) == sorted(expected, key=_key)
