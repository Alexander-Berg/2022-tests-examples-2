import pytest

from market_finance_etl.layer.greenplum.ods.mbi.supplier.loader import cast_subsidy, cast_ff_program


@pytest.mark.parametrize('cast, val, expected', [
    (cast_subsidy, {'subsidies': 'on'}, True),
    (cast_subsidy, {'subsidies': 'off'}, False),
    (cast_ff_program, {'ff_program': 'REAL'}, True),
    (cast_ff_program, {'ff_program': 'no'}, False),
])
def test_casters(cast, val, expected):
    assert expected == cast(val)
