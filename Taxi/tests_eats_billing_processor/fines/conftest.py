import pytest


@pytest.fixture(name='fines_fixtures')
def _fines_fixtures(taxi_eats_billing_processor, mockserver):
    class Fixtures:
        def __init__(self, taxi_eats_billing_processor, mockserver):
            self.taxi_eats_billing_processor = taxi_eats_billing_processor
            self.mockserver = mockserver

    return Fixtures(taxi_eats_billing_processor, mockserver)
