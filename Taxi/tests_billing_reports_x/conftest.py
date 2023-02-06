# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from billing_reports_x_plugins import *  # noqa: F403 F401


@pytest.fixture(name='billing_reports', autouse=False)
def _billing_reports(mockserver, load_json):
    class Context:
        def __init__(self):
            self.settings = None
            self.called = 0

        def setup(self, settings_path):
            self.settings = load_json(settings_path)
            self.called = 0

        def inc_called(self):
            self.called += 1

        def times_called(self):
            return self.called

    ctx = Context()

    @mockserver.json_handler('/billing-reports/v1/balances/select')
    def _mock_balances_select(request):
        ctx.inc_called()
        settings = ctx.settings['br_mock']
        return mockserver.make_response(
            json=settings.get('response'), status=settings['response_code'],
        )

    return ctx


@pytest.fixture(name='billing_accounts', autouse=False)
def _billing_accounts(mockserver, load_json):
    class Context:
        def __init__(self):
            self.settings = None
            self.accounts_called = 0
            self.balances_called = 0

        def setup(self, settings_path):
            self.settings = load_json(settings_path)
            self.accounts_called = 0
            self.balances_called = 0

        def inc_accounts_called(self):
            self.accounts_called += 1

        def inc_balances_called(self):
            self.balances_called += 1

        def times_accounts_called(self):
            return self.accounts_called

        def times_balances_called(self):
            return self.balances_called

    ctx = Context()

    @mockserver.json_handler('/billing-accounts/v2/accounts/search')
    def _mock_accounts_search(request):
        ctx.inc_accounts_called()
        settings = ctx.settings['ba_mock']['accounts']
        requested_accounts = [
            acc['entity_external_id'] for acc in request.json['accounts']
        ]
        response = {
            'accounts': list(
                filter(
                    lambda account: account['entity_external_id']
                    in requested_accounts,
                    settings['response']['accounts'],
                ),
            ),
        }

        return mockserver.make_response(
            json=response, status=settings['response_code'],
        )

    @mockserver.json_handler('/billing-accounts/v2/balances/select')
    def _mock_balances_select(request):
        ctx.inc_balances_called()
        settings = ctx.settings['ba_mock']['balances']
        requested_accounts = [
            acc['entity_external_id'] for acc in request.json['accounts']
        ]
        response = list(
            filter(
                lambda acc_bal: acc_bal['account']['entity_external_id']
                in requested_accounts,
                settings['response'],
            ),
        )

        return mockserver.make_response(
            json=response, status=settings['response_code'],
        )

    return ctx
