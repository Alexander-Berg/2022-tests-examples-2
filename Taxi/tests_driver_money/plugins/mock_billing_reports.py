# pylint: disable=invalid-name
import collections
import datetime

import pytest


def _make_balances(balances, accrued_ats):
    balance_by_date = {
        datetime.datetime.fromisoformat(balance['accrued_at']): balance
        for balance in balances
    }
    balance_by_date[
        datetime.datetime.fromtimestamp(0, datetime.timezone.utc)
    ] = balances[0]

    # last balance before input date
    def floor_accrued_at(accrued_at):
        accrued_at_dt = datetime.datetime.fromisoformat(accrued_at)
        best_date = max(
            date for date in balance_by_date if date <= accrued_at_dt
        )
        return dict(balance_by_date[best_date], accrued_at=accrued_at)

    return [floor_accrued_at(accrued_at) for accrued_at in accrued_ats]


@pytest.fixture(name='billing_reports', autouse=False)
def _billing_reports(mockserver):
    class BillingReportsContext:
        def __init__(self):
            self.balances_request = None
            self.balance_entries = {'entries': []}
            self.journal_entries = collections.defaultdict(list)
            self.journal_select = {}
            self.journal_calls = 0
            self.journal_select_calls = 0
            self.balance_calls = 0
            self.journal_by_tag_429_enabled = False
            self.journal_by_tag_429_enabled_with_msg = False
            self.journal_select_429_enabled = False
            self.journal_select_429_enabled_with_msg = False
            self.balances_select_429_enabled = False
            self.balances_select_429_enabled_with_msg = False

        def set_balances(self, balances):
            self.balance_entries = balances

        def add_journal_entries(self, order_id, entries):
            self.journal_entries[f'taxi/alias_id/{order_id}'].extend(entries)

        def set_journal_select(self, journal_select):
            self.journal_select = journal_select
            for entry in journal_select:
                self.add_journal_entries(entry['details']['alias_id'], [entry])

        def get_request(self):
            return self.balances_request

        def set_balances_select_429(self, is_body_enabled=False):
            self.balances_select_429_enabled = not is_body_enabled
            self.balances_select_429_enabled_with_msg = is_body_enabled

        def set_journal_by_tag_429(self, is_body_enabled=False):
            self.journal_by_tag_429_enabled = not is_body_enabled
            self.journal_by_tag_429_enabled_with_msg = is_body_enabled

        def set_journal_select_429(self, is_body_enabled=False):
            self.journal_select_429_enabled = not is_body_enabled
            self.journal_select_429_enabled_with_msg = is_body_enabled

        def get_balances_response(self, request):
            return {
                'entries': [
                    dict(
                        entry,
                        balances=_make_balances(
                            entry['balances'], request['accrued_at'],
                        ),
                    )
                    for entry in self.balance_entries['entries']
                ],
            }

    bss_context = BillingReportsContext()

    @mockserver.json_handler('/billing-reports/v1/balances/select')
    async def _balances_select(request):
        bss_context.balances_request = request.json
        bss_context.balance_calls += 1
        if bss_context.balances_select_429_enabled:
            return mockserver.make_response(status=429)
        if bss_context.balances_select_429_enabled_with_msg:
            return mockserver.make_response('Too many requests', status=429)

        return bss_context.get_balances_response(request.json)

    @mockserver.json_handler('/billing-reports/v2/journal/by_tag')
    async def _journal_by_tag(request):
        bss_context.journal_calls += 1
        if bss_context.journal_by_tag_429_enabled:
            return mockserver.make_response(status=429)
        if bss_context.journal_by_tag_429_enabled_with_msg:
            return mockserver.make_response('Too many requests', status=429)

        return {'entries': dict(bss_context.journal_entries)}

    @mockserver.json_handler('/billing-reports/v1/journal/select')
    async def _journal_select(request):
        bss_context.journal_select_calls += 1
        if bss_context.journal_select_429_enabled:
            return mockserver.make_response(status=429)
        if bss_context.journal_select_429_enabled_with_msg:
            return mockserver.make_response('Too many requests', status=429)

        return {
            'cursor': {},
            'entries': [
                entry
                for entry in bss_context.journal_select
                if request.json['begin_time']
                < entry['event_at']
                < request.json['end_time']
            ],
        }

    return bss_context
