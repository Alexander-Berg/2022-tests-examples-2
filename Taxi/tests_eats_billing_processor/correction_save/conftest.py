import pytest


@pytest.fixture(name='correction_save_fixtures')
def _correction_save_fixtures(
        taxi_eats_billing_processor, billing_reports_mock, stq, pgsql,
):
    class Fixtures:
        def __init__(
                self,
                taxi_eats_billing_processor,
                billing_reports_mock,
                stq,
                pgsql,
        ):
            self.taxi_eats_billing_processor = taxi_eats_billing_processor
            self.billing_reports_mock = billing_reports_mock
            self.pgsql = pgsql
            self.stq = stq

    return Fixtures(
        taxi_eats_billing_processor, billing_reports_mock, stq, pgsql,
    )
