# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name, protected-access
import pytest


@pytest.fixture(name='mock_fleet_payouts')
def _mock_fleet_payouts(mockserver):
    class Context:
        def __init__(self):
            self.clid = 'clid1'
            self.fleet_version = 'basic'

        def set_data(self, clid=None, fleet_version=None):
            if clid is not None:
                self.clid = clid
            if fleet_version is not None:
                self.fleet_version = fleet_version

        def _make_fleet_payouts_response(self):
            return {'fleet_version': self.fleet_version}

        @property
        def call_mock_fleet_payouts_calls(self):
            return mock_fleet_payouts.times_called

    context = Context()

    @mockserver.json_handler(
        '/fleet-payouts/internal/payouts/v1/fleet-version',
    )
    def mock_fleet_payouts(request):
        assert request.query['clid'] == context.clid
        return context._make_fleet_payouts_response()

    return context
