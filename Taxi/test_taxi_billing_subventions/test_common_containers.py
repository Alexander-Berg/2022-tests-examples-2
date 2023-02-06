import pytest

from taxi_billing_subventions.common import containers


@pytest.mark.nofilldb()
def test_universe():
    assert object() in containers.Universe()
