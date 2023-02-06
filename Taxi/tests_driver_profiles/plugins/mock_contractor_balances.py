import pytest


def equals(first, second):
    return abs(float(first) - float(second)) < 0.00005


class DriverBalanceLimitUpdatedTrigger:
    def __init__(self, db):
        self.mock_callback = None
        self.return_error = False
        self.has_calls = False
        self.request_body = None
        self._db = db
        self._old_balance_limit = 0.0
        self._new_balance_limit = 0.0

    def _get_balance_limit(self, park_id, driver_id):
        driver = self._db.dbdrivers.find_one(
            {'park_id': park_id, 'driver_id': driver_id},
        )
        return 0.0 if driver is None else driver.pop('balance_limit', 0.0)

    def save_old_balance_limit(self, park_id, driver_id):
        self._old_balance_limit = self._get_balance_limit(park_id, driver_id)

    def save_new_balance_limit(self, park_id, driver_id):
        self._new_balance_limit = self._get_balance_limit(park_id, driver_id)

    def check_calls(self):
        assert self.has_calls == (
            not equals(self._new_balance_limit, self._old_balance_limit)
        )

    def check_body(self, park_id, driver_id, datetime_now=None):
        body = self.request_body
        assert equals(body.pop('new_balance_limit'), self._new_balance_limit)
        assert equals(body.pop('old_balance_limit'), self._old_balance_limit)
        assert body.pop('park_id') == park_id
        assert body.pop('contractor_profile_id') == driver_id

        if datetime_now:
            assert body['balance_limit_updated_at'] == datetime_now

    def check(self, park_id, driver_id, datetime_now=None):
        self.save_new_balance_limit(park_id, driver_id)
        self.check_calls()
        if self.has_calls:
            self.check_body(park_id, driver_id, datetime_now)


@pytest.fixture
def mock_contractor_balances(mongodb, mockserver):
    context = DriverBalanceLimitUpdatedTrigger(mongodb)

    @mockserver.json_handler(
        '/contractor-balances/internal/v1/balance-limit-updated-trigger',
    )
    def _mock_callback(request):
        context.has_calls = True
        context.request_body = request.json
        if context.return_error:
            return mockserver.make_response(status=500)
        return {}

    context.mock_callback = _mock_callback
    return context
