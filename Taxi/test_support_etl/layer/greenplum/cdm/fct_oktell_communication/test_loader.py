import re
import pytest


@pytest.mark.parametrize(
    "order_nr_gp, order_nr_dmp", [
        ('210114-396388', '210114-396388'),
        ('510114-396388', '510114-396388'),
        (' 510114-396388', '510114-396388'),
        ('510114-396388 ', '510114-396388'),
        ('_', ''),
        ('0', ''),
    ]
)
def test_regex_order_nr_pattern(order_nr_gp, order_nr_dmp, unit_test_settings):
    with unit_test_settings():
        from support_etl.layer.greenplum.cdm.fct_oktell_communication.loader import (
            REGEX_ORDER_NR_PATTERN
        )

    regex_order_nr_pattern_cpl = re.compile(REGEX_ORDER_NR_PATTERN)
    regex_order_nr_pattern_mch = regex_order_nr_pattern_cpl.match(order_nr_gp)
    if regex_order_nr_pattern_mch:
        result = regex_order_nr_pattern_mch.group(1)
    else:
        result = ''
    assert order_nr_dmp == result
