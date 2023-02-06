# pylint: disable=C1801
import pytest


@pytest.mark.parametrize(
    'deptrans_no_permission_required, '
    'expected_drivers_count, expected_classes_without_permission',
    [
        (['vip', 'super_elite'], 2, ['vip']),
        (['super_elite'], 1, []),
        (['vip'], 2, ['vip']),
        ([], 1, []),
    ],
)
async def test_business_without_permission(
        taxi_candidates,
        driver_positions,
        deptrans_no_permission_required,
        expected_drivers_count,
        expected_classes_without_permission,
):

    await driver_positions(
        [
            # with permit
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.619757, 55.753215]},
            # without permit
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.619757, 55.753215]},
        ],
    )

    response = await taxi_candidates.post(
        'deptrans',
        json={
            'format': 'extended',
            'deptrans': {
                'classes_without_permission': deptrans_no_permission_required,
            },
        },
    )
    assert response.status_code == 200
    drivers = response.json()['drivers']
    assert len(drivers) == expected_drivers_count
    for driver in drivers:
        assert (
            driver['no_permission_classes']
            == expected_classes_without_permission
        )

        # dbid0_uuid0 hash
        if driver['id'] == '7b18551a390219976da357e490f638a7':
            assert driver['permit'] == 'permit_1'
        else:
            assert 'permit' not in driver
