import pytest


@pytest.fixture(name='deal_id_fixtures')
def _deal_id_fixtures(taxi_eats_billing_processor, client_info_mock, pgsql):
    class Fixtures:
        def __init__(
                self, taxi_eats_billing_processor, client_info_mock, pgsql,
        ):
            self.taxi_eats_billing_processor = taxi_eats_billing_processor
            self.client_info_mock = client_info_mock
            self.pgsql = pgsql

    return Fixtures(taxi_eats_billing_processor, client_info_mock, pgsql)
