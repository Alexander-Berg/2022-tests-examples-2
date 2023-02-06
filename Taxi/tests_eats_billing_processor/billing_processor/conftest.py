import pytest


@pytest.fixture(name='billing_processor_fixtures')
def _billing_processor_fixtures(load_json, stq_runner, pgsql, stq, mockserver):
    class Fixtures:
        def __init__(self, load_json, stq_runner, pgsql, stq, mockserver):
            self.load_json = load_json
            self.stq_runner = stq_runner
            self.pgsql = pgsql
            self.stq = stq
            self.mockserver = mockserver

    return Fixtures(load_json, stq_runner, pgsql, stq, mockserver)
