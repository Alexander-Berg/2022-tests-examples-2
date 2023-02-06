import bson
import pytest

from tests_unique_drivers import utils


@pytest.mark.parametrize(
    'requested_license_pd_id, requested_merge_license_pd_id, expected_ud, '
    'expected_union_ud, expected_status',
    [
        (
            'LICENSE_001_ID',
            'LICENSE_004_ID',
            None,
            None,
            'license_has_been_added',
        ),
        (
            'LICENSE_001_ID',
            'LICENSE_003_ID',
            None,
            None,
            'licenses_already_paired',
        ),
        (
            'LICENSE_001_ID',
            'LICENSE_002_ID',
            None,
            {
                'license_ids': [
                    {'id': 'LICENSE_001_ID'},
                    {'id': 'LICENSE_002_ID'},
                    {'id': 'LICENSE_003_ID'},
                ],
                'licenses': [
                    {'license': 'LICENSE_001'},
                    {'license': 'LICENSE_002'},
                    {'license': 'LICENSE_003'},
                ],
                'unique_drivers': [
                    {
                        'unique_driver_id': bson.ObjectId(
                            '000000000000000000000002',
                        ),
                    },
                    {
                        'unique_driver_id': bson.ObjectId(
                            '000000000000000000000001',
                        ),
                    },
                ],
            },
            'uniques_have_been_merged',
        ),
    ],
)
@pytest.mark.now('2021-03-01T00:00:00')
async def test_internal_merge(
        taxi_unique_drivers,
        mongodb,
        requested_license_pd_id,
        requested_merge_license_pd_id,
        expected_ud,
        expected_union_ud,
        expected_status,
):
    response = await taxi_unique_drivers.post(
        '/internal/unique-drivers/v1/merge',
        params={'consumer': 'internal'},
        json={
            'license': {'license_pd_id': requested_license_pd_id},
            'merge_license': {'license_pd_id': requested_merge_license_pd_id},
        },
    )

    if expected_union_ud:
        union_unique_driver = utils.get_union_unique_driver(
            requested_license_pd_id, 'license_ids.id', mongodb,
        )
        assert utils.ordered(union_unique_driver) == utils.ordered(
            expected_union_ud,
        )

    assert response.status_code == 200
    response = response.json()

    unique_driver = utils.get_unique_driver(
        requested_license_pd_id, 'license_ids.id', mongodb,
    )
    merge_unique_driver = utils.get_unique_driver(
        requested_merge_license_pd_id, 'license_ids.id', mongodb,
    )

    expected_response = {
        'unique_driver': {
            'id': str(unique_driver['_id']),
            'license_pd_ids': unique_driver['license_ids'],
        },
        'status': expected_status,
    }
    if expected_union_ud:
        expected_response['merge_unique_driver'] = {
            'id': str(merge_unique_driver['_id']),
            'license_pd_ids': merge_unique_driver['license_ids'],
        }

    assert utils.ordered(response) == utils.ordered(expected_response)


async def test_internal_merge_no_unique(taxi_unique_drivers):
    response = await taxi_unique_drivers.post(
        '/internal/unique-drivers/v1/merge',
        params={'consumer': 'internal'},
        json={
            'license': {'license_pd_id': 'LICENSE_006_ID'},
            'merge_license': {'license_pd_id': 'LICENSE_002_ID'},
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'UNIQUE_NOT_FOUND',
        'message': 'Unique driver is not found',
    }
