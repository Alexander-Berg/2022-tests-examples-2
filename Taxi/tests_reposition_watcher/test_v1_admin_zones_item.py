# pylint: disable=import-only-modules
import pytest

from tests_reposition_watcher.utils import select_named


@pytest.mark.pgsql('reposition_watcher', files=['modes_zones.sql'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.parametrize('check', [False, True])
async def test_put(taxi_reposition_watcher, pgsql, check):
    url = '/v1/admin/zones/item'
    check_part = '/check' if check else ''
    full_url = f'{url}{check_part}?zone=moscow'
    response = await taxi_reposition_watcher.put(full_url, json={})
    assert response.status_code == 200
    assert response.json() == {}

    if not check:
        rows = select_named(
            'SELECT zone_name FROM config.zones WHERE zone_name = \'moscow\'',
            pgsql['reposition_watcher'],
        )
        assert len(rows) == 1
        assert rows[0]['zone_name'] == 'moscow'

    #  twice
    response = await taxi_reposition_watcher.put(full_url, json={})
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.pgsql(
    'reposition_watcher', files=['modes_zones.sql', 'config_checks.sql'],
)
@pytest.mark.geoareas(filename='geoareas_spb.json')
@pytest.mark.parametrize('check', [False, True])
@pytest.mark.parametrize('cloning_enabled', [True, False])
async def test_put_clone(
        taxi_reposition_watcher, pgsql, taxi_config, cloning_enabled, check,
):
    taxi_config.set_values(
        {'REPOSITION_MATCHER_FORMULAS_CLONING_ENABLED': cloning_enabled},
    )

    url = '/v1/admin/zones/item'
    check_part = '/check' if check else ''
    full_url = f'{url}{check_part}?zone=spb'
    response = await taxi_reposition_watcher.put(
        full_url, json={'zone_to_clone': '__default__'},
    )
    assert response.status_code == 200
    assert response.json() == {}

    if not check:
        rows = select_named(
            'SELECT zone_name FROM config.zones WHERE zone_name = \'spb\'',
            pgsql['reposition_watcher'],
        )
        assert len(rows) == 1
        assert rows[0]['zone_name'] == 'spb'
        select_def = (
            '(SELECT zone_id FROM config.zones'
            ' WHERE zone_name = \'__default__\')'
        )
        select_spb = (
            '(SELECT zone_id FROM config.zones WHERE zone_name = \'spb\')'
        )
        if cloning_enabled:
            orig_conf = select_named(
                f'SELECT * FROM config.checks WHERE zone_id = {select_def}',
                pgsql['reposition_watcher'],
            )
            clone_conf = select_named(
                f'SELECT * FROM config.checks WHERE zone_id = {select_spb}',
                pgsql['reposition_watcher'],
            )
            assert len(orig_conf) == 3
            assert len(orig_conf) == len(clone_conf)
            for chk in orig_conf:
                chk.pop('zone_id', None)
            for chk in clone_conf:
                chk.pop('zone_id', None)
            assert orig_conf == clone_conf

    #  twice
    response = await taxi_reposition_watcher.put(
        full_url, json={'zone_to_clone': '__default__'},
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.parametrize('check', [False, True])
@pytest.mark.parametrize('has_dependencies', [False, True])
async def test_delete(
        taxi_reposition_watcher, pgsql, check, load, has_dependencies,
):
    queries = [load('modes_zones.sql')]
    pgsql['reposition_watcher'].apply_queries(queries)

    url = '/v1/admin/zones/item'
    check_part = '/check' if check else ''
    full_url = f'{url}{check_part}?zone=moscow'
    response = await taxi_reposition_watcher.delete(full_url)
    assert response.status_code == 200
    assert response.json() == {}

    if not check:
        rows = select_named(
            'SELECT zone_name FROM config.zones WHERE zone_name = \'moscow\'',
            pgsql['reposition_watcher'],
        )
        assert not rows

    # twice
    response = await taxi_reposition_watcher.delete(full_url)
    assert response.status_code == 200
    assert response.json() == {}
