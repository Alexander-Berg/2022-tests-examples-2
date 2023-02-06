import pytest


@pytest.fixture(name='tlog_writer_fixtures')
def _tlog_writer_fixtures(
        load_json, stq_runner, pgsql, stq, billing_orders_mock,
):
    class Fixtures:
        def __init__(
                self, load_json, stq_runner, pgsql, stq, billing_orders_mock,
        ):
            self.load_json = load_json
            self.stq_runner = stq_runner
            self.pgsql = pgsql
            self.stq = stq
            self.billing_orders_mock = billing_orders_mock

    return Fixtures(load_json, stq_runner, pgsql, stq, billing_orders_mock)
