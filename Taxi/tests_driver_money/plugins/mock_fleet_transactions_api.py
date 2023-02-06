# pylint: disable=invalid-name
import pytest


@pytest.fixture(name='fleet_transactions_api')
def fleet_transactions_api(mockserver, load_json):
    class Context:
        def __init__(self):
            self.counter_t = -1
            self.counter_b = -1
            self.prefix = ''
            self.transactions_list_429_enabled = False
            self.transactions_list_429_enabled_with_msg = False
            self.balances_list_429_enabled = False
            self.balances_list_429_enabled_with_msg = False

        def set_folder(self, name):
            context.prefix = '' if not name else name + '/'

        def set_transactions_list_429(self, is_body_enabled=False):
            self.transactions_list_429_enabled = not is_body_enabled
            self.transactions_list_429_enabled_with_msg = is_body_enabled

        def set_balances_list_429(self, is_body_enabled=False):
            self.balances_list_429_enabled = not is_body_enabled
            self.balances_list_429_enabled_with_msg = is_body_enabled

    context = Context()

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/transactions/list',
    )
    async def _transactions_handler(request):
        if 'cursor' in request.json:
            assert request.json['cursor'] != 'bnVsbA'  # base64 null
        context.counter_t += 1

        if context.transactions_list_429_enabled:
            return mockserver.make_response(status=429)
        if context.transactions_list_429_enabled_with_msg:
            return mockserver.make_response('Too many requests', status=429)
        return load_json(
            '{}fleet_transactions_api_transactions_{}.json'.format(
                context.prefix, context.counter_t,
            ),
        )

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    async def _balances_handler(request):
        context.counter_b += 1
        if context.balances_list_429_enabled:
            return mockserver.make_response(status=429)
        if context.balances_list_429_enabled_with_msg:
            return mockserver.make_response('Too many requests', status=429)
        return load_json(
            '{}fleet_transactions_api_balances_{}.json'.format(
                context.prefix, context.counter_b,
            ),
        )

    return context
