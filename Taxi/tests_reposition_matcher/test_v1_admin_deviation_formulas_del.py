# pylint: disable=import-only-modules
import pytest

from tests_reposition_matcher.utils import select_named


@pytest.mark.pgsql(
    'reposition_matcher', files=['modes_zones.sql', 'formulas.sql'],
)
async def test_del(taxi_reposition_matcher, mockserver, pgsql):
    response = await taxi_reposition_matcher.delete(
        'v1/admin/deviation_formulas/item'
        '?zone=moscow&mode=poi&submode=fast',
    )
    assert response.status_code == 200
    assert response.json() == {}
    rows = select_named(
        'SELECT * FROM config.deviation_formulas '
        'WHERE zone_id = 1 AND mode_id = 2 AND submode_id = 1',
        pgsql['reposition_matcher'],
    )
    assert rows == []


@pytest.mark.pgsql(
    'reposition_matcher', files=['modes_zones.sql', 'formulas.sql'],
)
async def test_del_nonexistent(taxi_reposition_matcher, mockserver):
    response = await taxi_reposition_matcher.delete(
        'v1/admin/deviation_formulas/item' '?zone=perm&mode=poi&submode=fast',
    )
    assert response.status_code == 200
    assert response.json() == {}
