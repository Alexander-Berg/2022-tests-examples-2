import copy

import bson
import pytest

from tests_unique_drivers import utils


@pytest.mark.parametrize('id_scenario', [False, True])
@pytest.mark.parametrize(
    'requested_licenses, old_license, old_doc, new_license, new_doc',
    [
        (
            [{'license': 'LICENSE_001'}],
            'LICENSE_002',
            {
                'exam_score': 2,
                'license_ids': [
                    {'id': 'LICENSE_002_ID'},
                    {'id': 'LICENSE_003_ID'},
                    {'id': 'LICENSE_004_ID'},
                ],
                'licenses': [
                    {'license': 'LICENSE_002'},
                    {'license': 'LICENSE_003'},
                    {'license': 'LICENSE_004'},
                ],
                'profiles': [
                    {'driver_id': 'clid3_driver3'},
                    {'driver_id': 'clid4_driver4'},
                    {'driver_id': 'clid5_driver5'},
                    {'driver_id': 'clid6_driver6'},
                ],
            },
            'LICENSE_001',
            {
                'decoupled_from': bson.ObjectId('000000000000000000000001'),
                'license_ids': [{'id': 'LICENSE_001_ID'}],
                'licenses': [{'license': 'LICENSE_001'}],
                'profiles': [
                    {'driver_id': 'clid1_driver1'},
                    {'driver_id': 'clid2_driver2'},
                ],
            },
        ),
        (
            [{'license': 'LICENSE_002'}, {'license': 'LICENSE_003'}],
            'LICENSE_001',
            {
                'license_ids': [
                    {'id': 'LICENSE_001_ID'},
                    {'id': 'LICENSE_004_ID'},
                ],
                'licenses': [
                    {'license': 'LICENSE_001'},
                    {'license': 'LICENSE_004'},
                ],
                'profiles': [
                    {'driver_id': 'clid1_driver1'},
                    {'driver_id': 'clid2_driver2'},
                    {'driver_id': 'clid6_driver6'},
                ],
            },
            'LICENSE_002',
            {
                'exam_score': 2,
                'decoupled_from': bson.ObjectId('000000000000000000000001'),
                'license_ids': [
                    {'id': 'LICENSE_002_ID'},
                    {'id': 'LICENSE_003_ID'},
                ],
                'licenses': [
                    {'license': 'LICENSE_002'},
                    {'license': 'LICENSE_003'},
                ],
                'profiles': [
                    {'driver_id': 'clid3_driver3'},
                    {'driver_id': 'clid4_driver4'},
                    {'driver_id': 'clid5_driver5'},
                ],
            },
        ),
    ],
)
@pytest.mark.now('2021-03-01T00:00:00')
async def test_admin_divide(
        taxi_unique_drivers,
        mongodb,
        id_scenario,
        requested_licenses,
        old_license,
        old_doc,
        new_license,
        new_doc,
):
    licenses = copy.deepcopy(requested_licenses)
    if id_scenario:
        for lic in licenses:
            lic['license_pd_id'] = lic.pop('license') + '_ID'

    response = await taxi_unique_drivers.post(
        '/admin/unique-drivers/v1/divide',
        headers={'X-Yandex-Login': 'user'},
        params={'consumer': 'admin'},
        json={'licenses': requested_licenses},
    )

    old_unique_driver = utils.get_unique_driver(
        old_license, 'licenses.license', mongodb,
    )
    new_unique_driver = utils.get_unique_driver(
        new_license, 'licenses.license', mongodb,
    )

    assert response.status_code == 200
    response = response.json()

    expected_response = {
        'unique_driver': {
            'id': str(old_unique_driver['_id']),
            'license_pd_ids': old_unique_driver['license_ids'],
        },
        'decoupled_unique_driver': {
            'id': str(new_unique_driver['_id']),
            'license_pd_ids': new_unique_driver['license_ids'],
        },
        'reload': {'exams': True},
    }

    assert utils.ordered(response) == utils.ordered(expected_response)

    old_unique_driver.pop('_id')
    assert utils.ordered(old_unique_driver) == utils.ordered(old_doc)

    new_unique_driver.pop('_id')
    assert utils.ordered(new_unique_driver) == utils.ordered(new_doc)


async def test_admin_divide_bad_request(taxi_unique_drivers):
    response = await taxi_unique_drivers.post(
        '/admin/unique-drivers/v1/divide',
        headers={'X-Yandex-Login': 'user'},
        params={'consumer': 'admin'},
        json={
            'licenses': [
                {'license': 'LICENSE_001'},
                {'license': 'LICENSE_002'},
                {'license': 'LICENSE_003'},
                {'license': 'LICENSE_004'},
            ],
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'BAD_REQUEST',
        'message': 'Requested more lisences than unique_driver contains',
    }
