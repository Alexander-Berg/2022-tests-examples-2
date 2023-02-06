import pytest


@pytest.fixture(name='full_run_fixtures')
def _full_run_fixtures(
        taxi_config,
        business_rules_mock,
        client_info_mock,
        taxi_eats_billing_processor,
        stq,
        stq_runner,
        pgsql,
):
    class Fixtures:
        def __init__(
                self,
                taxi_config,
                business_rules_mock,
                client_info_mock,
                taxi_eats_billing_processor,
                stq,
                stq_runner,
                pgsql,
        ):
            self.taxi_config = taxi_config
            self.business_rules_mock = business_rules_mock
            self.client_info_mock = client_info_mock
            self.taxi_eats_billing_processor = taxi_eats_billing_processor
            self.stq = stq
            self.stq_runner = stq_runner
            self.pgsql = pgsql

    return Fixtures(
        taxi_config,
        business_rules_mock,
        client_info_mock,
        taxi_eats_billing_processor,
        stq,
        stq_runner,
        pgsql,
    )
