import pytest

ENDPOINT = 'service/v1/uniques/merge'
COMMON_JSON = {
    'old_license_pd_id': 'license_pd_id_1',
    'new_license_pd_id': 'license_pd_id_2',
}
COMMON_PARAMS = {'consumer': 'service'}


@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.config(UNIQUE_DRIVERS_MERGE_CONSUMERS=['service1'])
async def test_merge_uniques_consumer_not_allowed(taxi_unique_drivers):
    response = await taxi_unique_drivers.post(
        ENDPOINT, params=COMMON_PARAMS, json=COMMON_JSON,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'CONSUMER_NOT_ALLOWED',
        'message': 'Consumer is not allowed.',
    }


@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.config(UNIQUE_DRIVERS_MERGE_CONSUMERS=['service'])
@pytest.mark.filldb(unique_drivers='empty')
async def test_merge_uniques_consumer_no_old_unique(taxi_unique_drivers):
    response = await taxi_unique_drivers.post(
        ENDPOINT, params=COMMON_PARAMS, json=COMMON_JSON,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'UNIQUE_NOT_FOUND',
        'message': 'Unique driver with old license_pd_id not found.',
    }


@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.config(UNIQUE_DRIVERS_MERGE_CONSUMERS=['service'])
@pytest.mark.filldb(unique_drivers='both_drivers')
async def test_merge_uniques_consumer_both_drivers_exists(taxi_unique_drivers):
    response = await taxi_unique_drivers.post(
        ENDPOINT, params=COMMON_PARAMS, json=COMMON_JSON,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'UNIQUE_ALREADY_EXISTS',
        'message': 'New license_pd_id is bind to unique driver.',
    }


@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.config(UNIQUE_DRIVERS_MERGE_CONSUMERS=['service'])
@pytest.mark.filldb(unique_drivers='first_driver')
@pytest.mark.parametrize(
    'personal_response',
    [
        [],
        [{'id': 'license_pd_id_1', 'value': 'license_1'}],
        [
            {'id': 'license_pd_id_1', 'value': 'license_1'},
            {'id': 'license_pd_id_2', 'value': 'license_2'},
        ],
    ],
)
async def test_merge_uniques_consumer_personal(
        taxi_unique_drivers, mockserver, mongodb, personal_response,
):
    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    async def _handler(request):
        return {'items': personal_response}

    unique_driver_before = mongodb.unique_drivers.find_one()
    assert unique_driver_before['license_ids'] == [{'id': 'license_pd_id_1'}]
    response = await taxi_unique_drivers.post(
        ENDPOINT, params=COMMON_PARAMS, json=COMMON_JSON,
    )
    if len(personal_response) == 2:
        assert response.status_code == 200
        unique_driver_after = mongodb.unique_drivers.find_one()
        assert unique_driver_after['license_ids'] == [
            {'id': 'license_pd_id_1'},
            {'id': 'license_pd_id_2'},
        ]
        assert unique_driver_after['licenses'] == [
            {'license': 'license_1'},
            {'license': 'license_2'},
        ]
        assert (
            unique_driver_after['updated'] != unique_driver_before['updated']
        )
        assert (
            unique_driver_after['updated_ts']
            != unique_driver_before['updated_ts']
        )
    else:
        assert response.status_code == 400
        assert response.json() == {
            'code': 'LICENSE_NOT_FOUND',
            'message': 'New license_pd_id is missing in personal service.',
        }
