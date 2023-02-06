import pytest
from django import test as django_test

from taxi.core import async
from taxi.external import taxi_protocol


@pytest.mark.asyncenv('blocking')
def test_not_found(patch):
    @patch('taxi.external.taxi_protocol.tariff_log_decode')
    @async.inline_callbacks
    def tariff_log_decode(*args, **kwargs):
        raise taxi_protocol.NotFoundError

    response = django_test.Client().get(
        '/api/tariff_calculator_log/b3354f2a4a440a14a4a32234391b0a2a/'
    )
    assert response.status_code == 404


@pytest.mark.asyncenv('blocking')
def test_ok(patch):
    @patch('taxi.external.taxi_protocol.tariff_log_decode')
    @async.inline_callbacks
    def tariff_log_decode(*args, **kwargs):
        yield
        async.return_value({})

    response = django_test.Client().get(
        '/api/tariff_calculator_log/b3354f2a4a440a14a4a32234391b0a2a/'
    )
    assert response.status_code == 200
