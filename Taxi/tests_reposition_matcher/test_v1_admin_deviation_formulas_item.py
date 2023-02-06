# pylint: disable=import-only-modules
import pytest

from tests_reposition_matcher.utils import select_named

REGULAR3 = {
    'da_distance_ratio': 31.0,
    'da_time_ratio': 32.0,
    'formula_type': 'regular_mode',
    'home_cancel_prob': 33.0,
    'home_distance_ratio': 34.0,
    'home_time_ratio': 35.0,
    'min_home_distance_ratio': 36.0,
    'min_home_time_ratio': 37.0,
    'min_order_distance': 38,
    'min_order_time': 39,
}

SURGE1 = {
    'formula_type': 'surge_mode',
    'min_b_lrsp_time': 1.0,
    'min_b_surge': 2.0,
    'min_order_distance': 3,
    'min_order_time': 4,
}

SURGE1_DB = {
    'min_b_lrsp_time': 1.0,
    'min_b_surge': 2.0,
    'min_order_distance': 3,
    'min_order_time': 4,
}

SLA_PARAMS = {'a': 1.0, 'b': 1.0, 'c': 1.0, 'd': 1.0, 'max_coef': 1.0}

REGULAR1_DB = {
    'da_dist_ratio': 1.0,
    'da_time_ratio': 2.0,
    'home_cancel_prob': 3.0,
    'home_dist_ratio': 4.0,
    'home_time_ratio': 5.0,
    'min_home_dist_ratio': 6.0,
    'min_home_time_ratio': 7.0,
    'min_order_distance': 8,
    'min_order_time': 9,
    'sla_params': SLA_PARAMS,
}

REGULAR3_DB = {
    'da_dist_ratio': 31.0,
    'da_time_ratio': 32.0,
    'home_cancel_prob': 33.0,
    'home_dist_ratio': 34.0,
    'home_time_ratio': 35.0,
    'min_home_dist_ratio': 36.0,
    'min_home_time_ratio': 37.0,
    'min_order_distance': 38,
    'min_order_time': 39,
}

REGULAR_OFFER2_DB = {
    'da_dist_ratio': 11.0,
    'da_time_ratio': 12.0,
    'home_cancel_prob': 13.0,
    'home_dist_ratio': 14.0,
    'home_time_ratio': 15.0,
    'min_b_surge': 110.0,
    'min_home_dist_ratio': 16.0,
    'min_home_time_ratio': 17.0,
    'min_order_distance': 18,
    'min_order_time': 19,
    'min_surge_gradient': 111.0,
}

REGULAR_OFFER3_DB = {
    'da_dist_ratio': 21.0,
    'da_time_ratio': 22.0,
    'home_cancel_prob': 23.0,
    'home_dist_ratio': 24.0,
    'home_time_ratio': 25.0,
    'min_b_surge': 210.0,
    'min_home_dist_ratio': 26.0,
    'min_home_time_ratio': 27.0,
    'min_order_distance': 28,
    'min_order_time': 29,
    'min_surge_gradient': 211.0,
    'sla_params': '(1,1,1,1,1)',
}

REGULAR_OFFER3 = {
    'da_distance_ratio': 21.0,
    'da_time_ratio': 22.0,
    'formula_type': 'regular_offer_mode',
    'home_cancel_prob': 23.0,
    'home_distance_ratio': 24.0,
    'home_time_ratio': 25.0,
    'min_b_surge': 210.0,
    'min_home_distance_ratio': 26.0,
    'min_home_time_ratio': 27.0,
    'min_order_distance': 28,
    'min_order_time': 29,
    'min_surge_gradient': 211.0,
    'sla_params': SLA_PARAMS,
}


async def get_formula_by_id(pgsql, formula_type, formula_id):
    formula = select_named(
        f'SELECT * FROM formulas.{formula_type} '
        f'WHERE formula_id = {formula_id}',
        pgsql['reposition_matcher'],
    )
    assert len(formula) == 1
    formula[0].pop('formula_id', None)
    return formula[0]


async def test_put_invalid_zone(taxi_reposition_matcher, mockserver):
    data = {'riding': REGULAR3}
    response = await taxi_reposition_matcher.put(
        'v1/admin/deviation_formulas/item?zone=kek&mode=home', json=data,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Zone \'kek\' not found',
    }


@pytest.mark.pgsql('reposition_matcher', files=['modes_zones.sql'])
async def test_put_invalid_mode(taxi_reposition_matcher, mockserver):
    data = {'riding': REGULAR3}
    response = await taxi_reposition_matcher.put(
        'v1/admin/deviation_formulas/item?zone=moscow&mode=kek', json=data,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Mode \'kek\' not found',
    }


@pytest.mark.pgsql('reposition_matcher', files=['modes_zones.sql'])
async def test_put_invalid_submode(taxi_reposition_matcher, mockserver):
    data = {'riding': REGULAR3}
    response = await taxi_reposition_matcher.put(
        'v1/admin/deviation_formulas/item?zone=moscow&mode=poi' '&submode=kek',
        json=data,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Submode \'kek\' not found',
    }


@pytest.mark.pgsql('reposition_matcher', files=['modes_zones.sql'])
async def test_put_invalid_type(taxi_reposition_matcher, mockserver):
    data = {'riding': REGULAR3}
    response = await taxi_reposition_matcher.put(
        'v1/admin/deviation_formulas/item?zone=moscow&mode=surge', json=data,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'Invalid riding formula type, allowed: '
            'surge_mode,regular_offer_mode'
        ),
    }


@pytest.mark.parametrize('override', [False, True])
async def test_put_area(
        taxi_reposition_matcher, mockserver, pgsql, override, load,
):
    queries = [load('modes_zones.sql')]
    if override:
        queries.append(load('formulas.sql'))
    pgsql['reposition_matcher'].apply_queries(queries)
    data = {'riding': {'formula_type': 'area_mode'}}
    response = await taxi_reposition_matcher.put(
        f'v1/admin/deviation_formulas/item?zone=moscow&mode=District',
        json=data,
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.parametrize('bonus', [False, True])
@pytest.mark.parametrize('submode', [None, 'fast', 'slow'])
@pytest.mark.parametrize('override', [False, True])
@pytest.mark.parametrize('fallback', [False, True])
async def test_put(
        taxi_reposition_matcher,
        mockserver,
        pgsql,
        bonus,
        submode,
        load,
        override,
        fallback,
):
    zone = 'moscow'
    mode = 'poi'
    zone_id = 1
    mode_id = 2
    submode_id = 1 if submode == 'fast' else 2
    submode_opt = f'&submode={submode}' if submode else ''
    queries = [load('modes_zones.sql')]
    if override:
        queries.append(load('formulas.sql'))
    pgsql['reposition_matcher'].apply_queries(queries)

    data = {'riding': SURGE1}
    if bonus:
        data['bonus'] = REGULAR_OFFER3
    if fallback:
        data['fallback'] = {'riding': SURGE1}

    response = await taxi_reposition_matcher.put(
        f'v1/admin/deviation_formulas/item?zone={zone}&mode={mode}'
        f'{submode_opt}',
        json=data,
    )
    submode_req = (
        f'AND submode_id = {submode_id}'
        if submode
        else 'AND submode_id IS NULL'
    )
    if submode and not override:
        submode_req = ''
    rows = select_named(
        'SELECT * FROM config.deviation_formulas fs '
        f'WHERE zone_id = {zone_id} AND mode_id = {mode_id}'
        f' {submode_req}',
        pgsql['reposition_matcher'],
    )
    assert response.status_code == 200
    assert response.json() == {}

    has_bonus = False

    for row in rows:
        if not fallback:
            assert not row['is_fallback']
        if fallback and row['is_fallback']:
            assert row['surge_mode']
            formula = await get_formula_by_id(
                pgsql, 'surge', row['surge_mode'],
            )
            assert formula == SURGE1_DB
            continue

        if row['bonus']:
            has_bonus = True
            assert row['regular_offer_mode']
            formula = await get_formula_by_id(
                pgsql, 'regular_offer', row['regular_offer_mode'],
            )
            assert formula == REGULAR_OFFER3_DB
            continue
        assert row['surge_mode']
        formula = await get_formula_by_id(pgsql, 'surge', row['surge_mode'])
        assert formula == SURGE1_DB
    assert has_bonus == bonus

    if override:
        submode_opt = (
            ' AND submode_id IS NOT NULL'
            if not submode
            else f' AND submode_id <> {submode_id}'
        )
        rows = select_named(
            'SELECT * FROM config.deviation_formulas fs '
            f'WHERE zone_id = {zone_id} AND mode_id = {mode_id}'
            f'{submode_opt}',
            pgsql['reposition_matcher'],
        )
        assert rows
