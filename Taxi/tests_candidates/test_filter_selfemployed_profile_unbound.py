import pytest


def _make_marks(
        has_profile: bool = True,
        enabled: bool = True,
        has_bond: bool = True,
        is_bound: bool = True,
):
    profiles = {}
    bonds = {}
    if has_profile:
        profiles['dbid0_uuid0'] = {
            'park_id': 'dbid0',
            'contractor_profile_id': 'uuid0',
            'do_send_receipts': enabled,
            'inn_pd_id': has_bond and 'inn_pd_id0' or None,
        }
        if has_bond:
            bonds['inn_pd_id0'] = {
                'inn_pd_id': 'inn_pd_id0',
                'status': is_bound and 'COMPLETED' or 'FAILED',
            }
    return [
        pytest.mark.selfemployed_profiles(profiles),
        pytest.mark.nalogru_bonds(bonds),
    ]


@pytest.mark.parametrize(
    'expect_found',
    [
        pytest.param(True, marks=_make_marks(), id='Enabled, bound'),
        pytest.param(
            False,
            marks=_make_marks(has_bond=False),
            id='Enabled, has no bond',
        ),
        pytest.param(
            False, marks=_make_marks(is_bound=False), id='Enabled, unbound',
        ),
        pytest.param(
            True,
            marks=_make_marks(enabled=False, is_bound=False),
            id='Disabled, unbound',
        ),
        pytest.param(
            True,
            marks=_make_marks(has_profile=False),
            id='Not a selfemployed',
        ),
    ],
)
async def test_selfemployed_profiles(
        taxi_candidates, driver_positions, expect_found,
):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/selfemployed_profile_unbound'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200

    drivers = response.json()['drivers']
    assert bool(drivers) == expect_found
