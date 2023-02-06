import pytest


@pytest.fixture(name='correction_info_fixtures')
def _correction_info_fixtures(
        taxi_eats_billing_processor, billing_reports_mock,
):
    class Fixtures:
        def __init__(self, taxi_eats_billing_processor, billing_reports_mock):
            self.taxi_eats_billing_processor = taxi_eats_billing_processor
            self.billing_reports_mock = billing_reports_mock

    return Fixtures(taxi_eats_billing_processor, billing_reports_mock)
