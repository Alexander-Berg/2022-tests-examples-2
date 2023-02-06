import typing as tp

import pytest


def _make_marks(
        has_profile: bool = True,
        enabled: bool = True,
        exceeded_legal_income_year: tp.Optional[int] = None,
        exceeded_reported_income_year: tp.Optional[int] = None,
):
    profiles = {}
    bonds: tp.Dict[str, tp.Dict[str, tp.Union[int, str]]] = {}
    if has_profile:
        profiles['dbid0_uuid0'] = {
            'park_id': 'dbid0',
            'contractor_profile_id': 'uuid0',
            'do_send_receipts': enabled,
            'inn_pd_id': 'inn_pd_id0',
        }
        bonds['inn_pd_id0'] = {
            'status': 'COMPLETED',
            'inn_pd_id': 'inn_pd_id0',
        }
        if exceeded_legal_income_year:
            bonds['inn_pd_id0'][
                'exceeded_legal_income_year'
            ] = exceeded_legal_income_year
        if exceeded_reported_income_year:
            bonds['inn_pd_id0'][
                'exceeded_reported_income_year'
            ] = exceeded_reported_income_year
    return [
        pytest.mark.selfemployed_profiles(profiles),
        pytest.mark.nalogru_bonds(bonds),
    ]


@pytest.mark.now('2021-11-15')
@pytest.mark.parametrize(
    'expect_found',
    [
        pytest.param(
            True,
            marks=_make_marks(),
            id='Enabled, not exceeded annual income',
        ),
        pytest.param(
            False,
            marks=_make_marks(exceeded_legal_income_year=2021),
            id='Enabled, exceeded annual income',
        ),
        pytest.param(
            True,
            marks=_make_marks(exceeded_legal_income_year=2020),
            id='Enabled, exceeded annual income previous year',
        ),
        pytest.param(
            False,
            marks=_make_marks(exceeded_reported_income_year=2021),
            id='Enabled, exceeded annual reported income',
        ),
        pytest.param(
            True,
            marks=_make_marks(exceeded_reported_income_year=2020),
            id='Enabled, exceeded annual reported income previous year',
        ),
        pytest.param(
            True,
            marks=_make_marks(enabled=False),
            id='Disabled, not exceeded annual income',
        ),
        pytest.param(
            True,
            marks=_make_marks(enabled=False, exceeded_legal_income_year=2021),
            id='Disabled, exceeded annual income',
        ),
        pytest.param(
            True,
            marks=_make_marks(enabled=False, exceeded_legal_income_year=2020),
            id='Disabled, exceeded annual income previous year',
        ),
        pytest.param(
            True,
            marks=_make_marks(
                enabled=False, exceeded_reported_income_year=2021,
            ),
            id='Disabled, exceeded reported annual income',
        ),
        pytest.param(
            True,
            marks=_make_marks(has_profile=False),
            id='Not a selfemployed',
        ),
    ],
)
async def test_selfemployed_income_exceeded(
        taxi_candidates, driver_positions, expect_found,
):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/selfemployed_income_exceeded'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200

    drivers = response.json()['drivers']
    assert bool(drivers) == expect_found
