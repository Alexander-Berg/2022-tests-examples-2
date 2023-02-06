import copy

import pytest


DEFAULT_PARAMS = {
    'timeFrom': '2019-04-05 01:00:00Z',
    'timeTo': '2019-04-05 02:00:00Z',
    'access_token': 'token1',
}


@pytest.mark.now('2019-04-05T05:00:00')
@pytest.mark.config(
    LICENSE_MATCH_PATTERN='0',
    EXTERNAL_ACCESS_TOKEN='token1',
    STATUS_RANGES_EXPORT_FROM_STORAGE='mongo',
)
async def test_drivers_activity(web_app_client):
    response = await web_app_client.get(
        '/v1/drivers_activity', params=DEFAULT_PARAMS,
    )
    assert response.status == 200
    result = await response.json()
    assert len(result['drivers']) == 1
    assert result['drivers'][0]['licenseId'] == '9900530553'


@pytest.mark.now('2019-04-05T05:00:00')
@pytest.mark.config(
    LICENSE_MATCH_PATTERN='0',
    EXTERNAL_ACCESS_TOKEN='token1',
    STATUS_RANGES_EXPORT_FROM_STORAGE='mongo',
)
async def test_outdated_time_from(web_app_client):
    params = copy.deepcopy(DEFAULT_PARAMS)
    params['timeFrom'] = '2019-04-03 10:00:00Z'
    response = await web_app_client.get('/v1/drivers_activity', params=params)
    assert response.status == 400


@pytest.mark.now('2019-04-05T05:00:00')
@pytest.mark.config(
    LICENSE_MATCH_PATTERN='1',
    EXTERNAL_ACCESS_TOKEN='token1',
    STATUS_RANGES_EXPORT_FROM_STORAGE='mongo',
)
async def test_no_matching_license(web_app_client):
    response = await web_app_client.get(
        '/v1/drivers_activity', params=DEFAULT_PARAMS,
    )
    assert response.status == 200
    result = await response.json()
    assert not result['drivers']


@pytest.mark.now('2019-04-05T05:00:00')
@pytest.mark.config(
    LICENSE_MATCH_PATTERN='',
    EXTERNAL_ACCESS_TOKEN='token1',
    STATUS_RANGES_EXPORT_FROM_STORAGE='mongo',
)
async def test_empty_license_pattern(web_app_client):
    response = await web_app_client.get(
        '/v1/drivers_activity', params=DEFAULT_PARAMS,
    )
    assert response.status == 403


@pytest.mark.now('2019-04-05T05:00:00')
@pytest.mark.config(
    LICENSE_MATCH_PATTERN='0',
    EXTERNAL_ACCESS_TOKEN='token1',
    MAX_DRIVERS_FOR_EXPORT=1,
    STATUS_RANGES_EXPORT_FROM_STORAGE='mongo',
)
async def test_drivers_limit(web_app_client):
    response = await web_app_client.get(
        '/v1/drivers_activity', params=DEFAULT_PARAMS,
    )
    assert response.status == 200
    result = await response.json()
    assert len(result['drivers']) == 1


@pytest.mark.now('2019-04-05T05:00:00')
@pytest.mark.config(
    LICENSE_MATCH_PATTERN='0',
    EXTERNAL_ACCESS_TOKEN='token1',
    MAX_DRIVERS_FOR_EXPORT=2,
    STATUS_RANGES_EXPORT_FROM_STORAGE='postgres',
)
async def test_activity_from_pg(web_app_client, pgsql):
    response = await web_app_client.get(
        '/v1/drivers_activity', params=DEFAULT_PARAMS,
    )
    assert response.status == 200
    result = await response.json()
    assert len(result['drivers']) == 2
    for driver in result['drivers']:
        assert driver['licenseId'] in ['9900530551', '9900530552']


@pytest.mark.now('2019-04-05T05:00:00')
@pytest.mark.config(LICENSE_MATCH_PATTERN='0', EXTERNAL_ACCESS_TOKEN='token2')
async def test_wrong_token(web_app_client):
    params = copy.deepcopy(DEFAULT_PARAMS)
    del params['timeFrom']
    del params['timeTo']
    request = {'driver': {'licenseId': '9900530553'}}
    response = await web_app_client.post(
        '/v1/driver_activity_time', params=params, json=request,
    )
    assert response.status == 400


@pytest.mark.now('2019-04-05T05:00:00Z')
@pytest.mark.config(
    LICENSE_MATCH_PATTERN='0',
    EXTERNAL_ACCESS_TOKEN='token1',
    RETURN_ZERO_ONORDER_TIME=False,
)
async def test_get_driver_activity(web_app_client, pgsql):
    params = copy.deepcopy(DEFAULT_PARAMS)
    del params['timeFrom']
    del params['timeTo']
    request = {'driver': {'licenseId': '9900530553'}}
    response = await web_app_client.post(
        '/v1/driver_activity_time', params=params, json=request,
    )
    assert response.status == 200
    result = await response.json()
    assert result['driver']['time'] == 1200


@pytest.mark.now('2019-04-05T05:00:00Z')
@pytest.mark.config(
    LICENSE_MATCH_PATTERN='0',
    EXTERNAL_ACCESS_TOKEN='token1',
    RETURN_ZERO_ONORDER_TIME=True,
)
async def test_get_driver_activity_zero(web_app_client, pgsql):
    params = copy.deepcopy(DEFAULT_PARAMS)
    del params['timeFrom']
    del params['timeTo']
    request = {'driver': {'licenseId': '9900530553'}}
    response = await web_app_client.post(
        '/v1/driver_activity_time', params=params, json=request,
    )
    assert response.status == 200
    result = await response.json()
    assert result['driver']['time'] == 0


@pytest.mark.now('2019-04-05T05:00:00Z')
@pytest.mark.config(
    LICENSE_MATCH_PATTERN='0',
    EXTERNAL_ACCESS_TOKEN='token1',
    RETURN_ZERO_ONORDER_TIME=True,
    TEST_LICENSE_ID='test_license1',
    TEST_DRIVER_ONORDER_TIME=600,
)
async def test_get_test_driver_activity(web_app_client, pgsql):
    params = copy.deepcopy(DEFAULT_PARAMS)
    del params['timeFrom']
    del params['timeTo']
    request = {'driver': {'licenseId': 'test_license1'}}
    response = await web_app_client.post(
        '/v1/driver_activity_time', params=params, json=request,
    )
    assert response.status == 200
    result = await response.json()
    assert result['driver']['time'] == 600


@pytest.mark.now('2019-04-05T05:00:00Z')
@pytest.mark.config(
    LICENSE_MATCH_PATTERN='0',
    EXTERNAL_ACCESS_TOKEN='token1',
    RETURN_ZERO_ONORDER_TIME=False,
)
async def test_get_driver_activity_absent(web_app_client, pgsql):
    params = copy.deepcopy(DEFAULT_PARAMS)
    del params['timeFrom']
    del params['timeTo']
    request = {'driver': {'licenseId': '9900530557'}}
    response = await web_app_client.post(
        '/v1/driver_activity_time', params=params, json=request,
    )
    assert response.status == 200
    result = await response.json()
    assert result['driver']['time'] == 0
