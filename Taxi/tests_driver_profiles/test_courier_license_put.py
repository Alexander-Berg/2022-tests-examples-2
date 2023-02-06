from aiohttp import web
import pytest


ENDPOINT = '/v1/courier/license'
PERSONAL_DRIVER_LICENSES_STORE = '/personal/v1/driver_licenses/store'
DRIVER_WORK_RULES_CHANGE_LOGGER = '/driver-work-rules/service/v1/change-logger'

COFFEE_LICENSE = 'COURIER00000000000000C0FFEE000000000000'
COFFEE_PD_ID = 'coffee_pd_id'
CAFE_LICENSE = 'COURIER00000000000000CAFE00000000000000'
CAFE_PD_ID = 'cafe_pd_id'
BAD_LICENSE = 'COURIER00000000000000BAD000000000000000'


@pytest.mark.parametrize(
    'driver_profile_id,number,status,message,diff',
    [
        (
            'courier',
            '7706999999',
            400,
            'Value of \'license.number\': value (7706999999) doesn\'t match '
            'pattern \'^COURIER[A-F0-9]{32}$\'',
            None,
        ),
        ('taxi', CAFE_LICENSE, 404, 'Courier not found', None),
        ('no_provider', CAFE_LICENSE, 404, 'Courier not found', None),
        ('courier', BAD_LICENSE, 500, 'Personal request error', None),
        ('courier', COFFEE_LICENSE, 200, None, None),
        (
            'courier',
            CAFE_LICENSE,
            200,
            None,
            [
                dict(field='license', old=COFFEE_LICENSE, new=CAFE_LICENSE),
                dict(
                    field='license_number',
                    old=COFFEE_LICENSE,
                    new=CAFE_LICENSE,
                ),
                dict(
                    field='license_normalized',
                    old=COFFEE_LICENSE,
                    new=CAFE_LICENSE,
                ),
                dict(
                    field='driver_license_pd_id',
                    old=COFFEE_PD_ID,
                    new=CAFE_PD_ID,
                ),
            ],
        ),
    ],
)
async def test_courier_license(
        taxi_driver_profiles,
        mockserver,
        mongodb,
        driver_profile_id,
        number,
        status,
        message,
        diff,
):
    personal_map = {COFFEE_LICENSE: COFFEE_PD_ID, CAFE_LICENSE: CAFE_PD_ID}

    @mockserver.json_handler(DRIVER_WORK_RULES_CHANGE_LOGGER)
    def change_logger(request):
        return web.json_response(data={})

    @mockserver.json_handler(PERSONAL_DRIVER_LICENSES_STORE)
    def _store_license(request):
        value = request.json['value']
        if value in personal_map:
            return web.json_response(
                data=dict(id=personal_map[value], value=value),
            )
        return web.json_response(status=500, data={})

    def _get_driver():
        return mongodb.dbdrivers.find_one(
            dict(park_id='park1', driver_id=driver_profile_id),
            {
                'license',
                'license_series',
                'license_number',
                'license_normalized',
                'driver_license_pd_id',
                'modified_date',
                'updated_ts',
            },
        )

    old_driver = _get_driver()

    new_license = {}
    if number:
        new_license['number'] = number
    author = dict(consumer='qc', identity=dict(type='job', job_name='updater'))
    response = await taxi_driver_profiles.put(
        ENDPOINT,
        params=dict(park_id='park1', driver_profile_id=driver_profile_id),
        json=dict(author=author, license=new_license),
    )
    assert response.status_code == status

    driver = _get_driver()

    if diff is not None:
        assert change_logger.times_called == 1
        body = change_logger.next_call()['request'].json
        body.pop('entity_id')
        assert body == dict(
            park_id='park1',
            change_info=dict(
                object_id=driver_profile_id,
                object_type='MongoDB.Docs.Driver.DriverDoc',
                diff=diff,
            ),
            author=dict(
                display_name='platform', dispatch_user_id='', user_ip='',
            ),
        )

    if status == 200:
        assert driver['modified_date'] > old_driver['modified_date']
        assert driver['updated_ts'] > old_driver['updated_ts']
        assert driver['license'] == number
        assert driver['license_number'] == number
        assert driver['license_normalized'] == number
        assert driver['driver_license_pd_id'] == personal_map[number]
        assert driver.get('license_series') is None
    else:
        assert response.json()['code'] == str(status)
        assert old_driver == driver


async def test_remove_series(taxi_driver_profiles, mockserver, mongodb):
    driver_profile_id = 'courier_with_series'

    @mockserver.json_handler(DRIVER_WORK_RULES_CHANGE_LOGGER)
    def change_logger(request):
        return web.json_response(data={})

    @mockserver.json_handler(PERSONAL_DRIVER_LICENSES_STORE)
    def _store_license(request):
        value = request.json['value']
        return web.json_response(data=dict(id=COFFEE_PD_ID, value=value))

    def _get_driver():
        return mongodb.dbdrivers.find_one(
            dict(park_id='park1', driver_id=driver_profile_id),
            {
                'license',
                'license_series',
                'license_number',
                'license_normalized',
                'driver_license_pd_id',
            },
        )

    old_driver = _get_driver()

    author = dict(consumer='qc', identity=dict(type='job', job_name='updater'))
    response = await taxi_driver_profiles.put(
        ENDPOINT,
        params=dict(park_id='park1', driver_profile_id=driver_profile_id),
        json=dict(author=author, license=dict(number=COFFEE_LICENSE)),
    )
    assert response.status_code == 200

    driver = _get_driver()

    assert change_logger.times_called == 1
    body = change_logger.next_call()['request'].json
    body.pop('entity_id')
    assert body == dict(
        park_id='park1',
        change_info=dict(
            object_id=driver_profile_id,
            object_type='MongoDB.Docs.Driver.DriverDoc',
            diff=[dict(field='license_series', old='COURIER', new='')],
        ),
        author=dict(display_name='platform', dispatch_user_id='', user_ip=''),
    )

    old_driver.pop('license_series')
    assert driver == old_driver
