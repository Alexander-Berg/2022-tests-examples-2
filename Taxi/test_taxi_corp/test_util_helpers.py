import pytest

from taxi_corp.util import helpers


@pytest.mark.parametrize(
    'vat,expected_result',
    [(0.18, '18%'), (0.183, '18.3%'), (0.1, '10%'), (1, '100%')],
)
@pytest.mark.nofilldb()
def test_format_vat(vat, expected_result):
    assert helpers.format_vat(vat) == expected_result
