# pylint: disable=import-only-modules
import pytest

from tests_reposition_matcher.utils import select_named


@pytest.mark.pgsql('reposition_matcher', files=['modes_zones.sql'])
@pytest.mark.geoareas(filename='geoareas_moscow_spb.json')
@pytest.mark.parametrize('check', [False, True])
async def test_put(taxi_reposition_matcher, pgsql, check):
    url = '/v1/admin/zones/item'
    check_part = '/check' if check else ''
    full_url = f'{url}{check_part}?zone=moscow'
    response = await taxi_reposition_matcher.put(full_url, json={})
    assert response.status_code == 200
    assert response.json() == {}

    if not check:
        rows = select_named(
            'SELECT zone_name FROM config.zones WHERE zone_name = \'moscow\'',
            pgsql['reposition_matcher'],
        )
        assert len(rows) == 1
        assert rows[0]['zone_name'] == 'moscow'

    #  twice
    response = await taxi_reposition_matcher.put(full_url, json={})
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.pgsql(
    'reposition_matcher', files=['modes_zones.sql', 'formulas.sql'],
)
@pytest.mark.geoareas(filename='geoareas_moscow_spb.json')
@pytest.mark.parametrize('check', [True, False])
@pytest.mark.parametrize('cloning_enabled', [True, False])
async def test_put_clone(
        taxi_reposition_matcher, taxi_config, pgsql, check, cloning_enabled,
):
    def select_formulas(zone):
        return select_named(
            f"""
            SELECT
                mode_id,
                submode_id,
                bonus,
                regular_mode,
                regular_offer_mode,
                surge_mode,
                area_mode,
                destination_district_mode
            FROM
                config.deviation_formulas
            NATURAL JOIN
                config.zones
            WHERE zone_name = '{zone}'
            ORDER BY
                mode_id ASC,
                submode_id ASC,
                bonus ASC
            """,
            pgsql['reposition_matcher'],
        )

    def select_regular(formula_id):
        return select_named(
            f"""
            SELECT DISTINCT ON (r.formula_id)
                r.*
            FROM
                formulas.regular AS r
            INNER JOIN
                config.deviation_formulas AS df
                ON df.regular_mode = r.formula_id
            WHERE
                r.formula_id = {formula_id}
            ORDER BY
                r.formula_id ASC
            """,
            pgsql['reposition_matcher'],
        )

    def select_regular_offer(formula_id):
        return select_named(
            f"""
            SELECT DISTINCT ON (ro.formula_id)
                ro.*
            FROM
                formulas.regular_offer AS ro
            INNER JOIN
                config.deviation_formulas AS df
                ON df.regular_offer_mode = ro.formula_id
            WHERE
                ro.formula_id = {formula_id}
            ORDER BY
                ro.formula_id ASC
            """,
            pgsql['reposition_matcher'],
        )

    def select_surge(formula_id):
        return select_named(
            f"""
            SELECT DISTINCT ON (s.formula_id)
                s.*
            FROM
                formulas.surge AS s
            INNER JOIN
                config.deviation_formulas AS df
                ON df.surge_mode = s.formula_id
            WHERE
                s.formula_id = {formula_id}
            ORDER BY
                s.formula_id ASC
            """,
            pgsql['reposition_matcher'],
        )

    def select_area(formula_id):
        return select_named(
            f"""
            SELECT DISTINCT ON (a.formula_id)
                a.*
            FROM
                formulas.area AS a
            INNER JOIN
                config.deviation_formulas AS df
                ON df.area_mode = a.formula_id
            WHERE
                a.formula_id = {formula_id}
            ORDER BY
                a.formula_id ASC
            """,
            pgsql['reposition_matcher'],
        )

    def select_destination_district(formula_id):
        return select_named(
            f"""
            SELECT DISTINCT ON (dd.formula_id)
                dd.*
            FROM
                formulas.destination_district AS dd
            INNER JOIN
                config.deviation_formulas AS df
                ON df.destination_district_mode = dd.formula_id
            WHERE
                dd.formula_id = {formula_id}
            ORDER BY
                dd.formula_id ASC
            """,
            pgsql['reposition_matcher'],
        )

    def compare_formulas(msk_f, spb_f):
        assert len(msk_f) == len(spb_f)

        for msk_fe, spb_fe in zip(msk_f, spb_f):
            assert msk_fe['mode_id'] == spb_fe['mode_id']
            assert msk_fe['submode_id'] == spb_fe['submode_id']
            assert msk_fe['bonus'] == spb_fe['bonus']

            msk_fer = msk_fe['regular_mode']
            spb_fer = spb_fe['regular_mode']

            msk_fero = msk_fe['regular_offer_mode']
            spb_fero = spb_fe['regular_offer_mode']

            msk_fes = msk_fe['surge_mode']
            spb_fes = spb_fe['surge_mode']

            msk_fea = msk_fe['area_mode']
            spb_fea = spb_fe['area_mode']

            msk_fedd = msk_fe['destination_district_mode']
            spb_fedd = spb_fe['destination_district_mode']

            msk_r = select_regular(msk_fer) if msk_fer else []
            spb_r = select_regular(spb_fer) if spb_fer else []

            msk_ro = select_regular_offer(msk_fero) if msk_fero else []
            spb_ro = select_regular_offer(spb_fero) if spb_fero else []

            msk_s = select_surge(msk_fes) if msk_fes else []
            spb_s = select_surge(spb_fes) if spb_fes else []

            msk_a = select_area(msk_fea) if msk_fea else []
            spb_a = select_area(spb_fea) if spb_fea else []

            msk_dd = select_destination_district(msk_fedd) if msk_fedd else []
            spb_dd = select_destination_district(spb_fedd) if spb_fedd else []

            for msk_formulas, spb_formulas in [
                    (msk_r, spb_r),
                    (msk_ro, spb_ro),
                    (msk_s, spb_s),
                    (msk_a, spb_a),
                    (msk_dd, spb_dd),
            ]:
                for formulas in [msk_formulas, spb_formulas]:
                    for formula in formulas:
                        del formula['formula_id']

                assert msk_formulas == spb_formulas

    taxi_config.set_values(
        {'REPOSITION_MATCHER_FORMULAS_CLONING_ENABLED': cloning_enabled},
    )

    url = '/v1/admin/zones/item'
    check_part = '/check' if check else ''
    full_url = f'{url}{check_part}?zone=spb'
    response = await taxi_reposition_matcher.put(
        full_url, json={'zone_to_clone': 'moscow'},
    )
    assert response.status_code == 200
    assert response.json() == {}

    if not check:
        zones = select_named(
            'SELECT zone_name FROM config.zones WHERE zone_name = \'spb\'',
            pgsql['reposition_matcher'],
        )
        assert zones == [{'zone_name': 'spb'}]

        msk_f = select_formulas('moscow')
        spb_f = select_formulas('spb')

        if cloning_enabled:
            compare_formulas(msk_f, spb_f)
        else:
            assert spb_f == []

    #  twice
    response = await taxi_reposition_matcher.put(
        full_url, json={'zone_to_clone': 'moscow'},
    )
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

    url = '/v1/admin/zones/item'
    check_part = '/check' if check else ''
    full_url = f'{url}{check_part}?zone=moscow'
    response = await taxi_reposition_matcher.delete(full_url)
    if not has_dependencies:
        assert response.status_code == 200
        assert response.json() == {}
    else:
        assert response.status_code == 400
        assert response.json() == {
            'code': '400',
            'message': (
                'Unable to delete zone: moscow probably because it has '
                'dependencies: ERROR:  update or delete on '
                'table "zones" violates '
                'foreign key constraint "deviation_formulas_zone_id_fkey"'
                ' on table "deviation_formulas"\n'
                'DETAIL:  Key (zone_id)=(1) is still referenced from table '
                '"deviation_formulas".\n'
            ),
        }

    if not check and not has_dependencies:
        rows = select_named(
            'SELECT zone_name FROM config.zones WHERE zone_name = \'moscow\'',
            pgsql['reposition_matcher'],
        )
        assert not rows

    # twice
    if not has_dependencies:
        response = await taxi_reposition_matcher.delete(full_url)
        assert response.status_code == 200
        assert response.json() == {}
