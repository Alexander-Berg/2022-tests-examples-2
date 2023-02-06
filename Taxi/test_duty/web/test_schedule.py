import pytest


@pytest.fixture
def taxi_duty_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_duty_mocks')
async def test_schedule(taxi_duty_web):
    pass
