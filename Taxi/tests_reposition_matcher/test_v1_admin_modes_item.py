# pylint: disable=import-only-modules
import pytest

from tests_reposition_matcher.utils import select_named


@pytest.mark.geoareas(filename='geoareas_moscow_spb.json')
@pytest.mark.parametrize('override', [False, True])
@pytest.mark.parametrize('check', [False, True])
@pytest.mark.parametrize('has_submodes', [False, True])
async def test_put(
        taxi_reposition_matcher, pgsql, load, check, override, has_submodes,
):
    if override:
        queries = [load('modes_zones.sql')]
        pgsql['reposition_matcher'].apply_queries(queries)

    data = {'type': 'ToPoint', 'offer_only': False}
    if has_submodes:
        data['submodes'] = {
            'names': ['fast', 'notfast', 'faster'],
            'default': 'notfast',
        }
    url = '/v1/admin/modes/item'
    check_part = '/check' if check else ''
    full_url = f'{url}{check_part}?mode=poi'

    response = await taxi_reposition_matcher.put(full_url, json=data)
    assert response.status_code == 200
    assert response.json() == {}

    if not check:
        mode = select_named(
            'SELECT mode_id, mode_name, offer_only, mode_type'
            ' FROM config.modes WHERE mode_name = \'poi\'',
            pgsql['reposition_matcher'],
        )
        assert len(mode) == 1
        assert mode[0]['mode_name'] == 'poi'
        assert not mode[0]['offer_only']
        assert mode[0]['mode_type'] == 'ToPoint'
        if has_submodes:
            mode_id = mode[0]['mode_id']
            submodes = select_named(
                'SELECT submode_name, is_default FROM config.submodes'
                f' WHERE mode_id = {mode_id}',
                pgsql['reposition_matcher'],
            )
            assert len(submodes) == len(data['submodes']['names'])
            for submode in submodes:
                if submode['submode_name'] == 'notfast':
                    assert submode['is_default']

    #  twice
    response = await taxi_reposition_matcher.put(full_url, json=data)
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.parametrize('check', [False, True])
@pytest.mark.parametrize('has_dependencies', [False, True])
async def test_delete(
        taxi_reposition_matcher, pgsql, check, load, has_dependencies,
):
    queries = [load('modes_zones.sql')]
    if has_dependencies:
        queries.append(load('formulas.sql'))
    pgsql['reposition_matcher'].apply_queries(queries)
    mode_id_rows = select_named(
        'SELECT mode_id FROM config.modes WHERE mode_name = \'poi\'',
        pgsql['reposition_matcher'],
    )
    assert len(mode_id_rows) == 1
    mode_id = mode_id_rows[0]['mode_id']

    url = '/v1/admin/modes/item'
    check_part = '/check' if check else ''
    full_url = f'{url}{check_part}?mode=poi'
    response = await taxi_reposition_matcher.delete(full_url)
    if not has_dependencies:
        assert response.status_code == 200
        assert response.json() == {}
    else:
        assert response.status_code == 400
        assert response.json() == {
            'code': '400',
            'message': 'Mode or submodes for mode \'poi\' has dependencies',
        }

    if not check and not has_dependencies:
        rows = select_named(
            'SELECT mode_name FROM config.modes WHERE mode_name = \'poi\'',
            pgsql['reposition_matcher'],
        )
        assert not rows

        submodes = select_named(
            'SELECT submode_name FROM config.submodes'
            f' WHERE mode_id = {mode_id}',
            pgsql['reposition_matcher'],
        )
        assert not submodes

    # twice
    if not has_dependencies:
        response = await taxi_reposition_matcher.delete(full_url)
        assert response.status_code == 200
        assert response.json() == {}
