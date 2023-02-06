import pytest


@pytest.fixture(name='transformer_fixtures')
def _transformer_fixtures(
        stq_runner,
        pgsql,
        stq,
        taxi_config,
        business_rules_mock,
        client_info_mock,
        billing_orders_mock,
        billing_reports_mock,
):
    class Fixtures:
        def __init__(
                self,
                stq_runner,
                pgsql,
                stq,
                taxi_config,
                business_rules_mock,
                client_info_mock,
                billing_orders_mock,
                billing_reports_mock,
        ):
            self.stq_runner = stq_runner
            self.pgsql = pgsql
            self.stq = stq
            self.taxi_config = taxi_config
            self.business_rules_mock = business_rules_mock
            self.client_info_mock = client_info_mock
            self.billing_orders_mock = billing_orders_mock
            self.billing_reports_mock = billing_reports_mock

    return Fixtures(
        stq_runner,
        pgsql,
        stq,
        taxi_config,
        business_rules_mock,
        client_info_mock,
        billing_orders_mock,
        billing_reports_mock,
    )
