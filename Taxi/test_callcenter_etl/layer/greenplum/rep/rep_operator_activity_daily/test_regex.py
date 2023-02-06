import re
import pytest

from callcenter_etl.layer.greenplum.rep.rep_operator_activity_daily.impl import (
    _META_QUEUE_REGEX
)

@pytest.mark.parametrize(
    "false_strings, true_strings", [
        ('ru_taxi_disp_economy', 'ru_taxi_disp_econom'),
        ('sgsdfg', 'ar_davos_disp_econ'),
        ('', 'by_davos_disp_sdfgvdfg'),
    ]
)
def test_regex(false_strings, true_strings):
    assert re.match(_META_QUEUE_REGEX, false_strings) is None
    assert re.match(_META_QUEUE_REGEX, true_strings) is not None
