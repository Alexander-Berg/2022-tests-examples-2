import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'v1/devices/partner'

DEVICE_NAME_PREFIX = 'SignalQ1_'


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
async def test_ok_first_time(taxi_signal_device_api_admin, pgsql):
    response = await taxi_signal_device_api_admin.put(
        ENDPOINT,
        json={'name': web_common.PARTNER_PASSPORT_UID_1},
        params={'device_id': web_common.DEVICE_ID_NO_PARTNER},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'name': web_common.PARTNER_PASSPORT_UID_1}
    web_common.check_device_web_info_in_db(
        pgsql,
        device_primary_key=web_common.DEVICE_PRIMARY_KEY_NO_PARTNER,
        partner_passport_uid=web_common.PARTNER_PASSPORT_UID_1,
        device_name=DEVICE_NAME_PREFIX + '5',
        driver_name=web_common.DRIVER_NAME_NO_PARTNER,
        vehicle_plate_number=web_common.VEHICLE_PLATE_NUMBER_NO_PARTNER,
        updated_at_newer_than=web_common.OLD_UPDATED_AT,
    )


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'pass_uid, device_id, device_primary_key, '
    'driver_name, vehicle_plate_number, index',
    [
        (
            web_common.PARTNER_PASSPORT_UID_1,
            web_common.DEVICE_ID_PARTNER_1,
            web_common.DEVICE_PRIMARY_KEY_PARTNER_1,
            web_common.DRIVER_NAME_PARTNER_1,
            web_common.VEHICLE_PLATE_NUMBER_PARTNER_1,
            4,
        ),
        (
            web_common.PARTNER_PASSPORT_UID_1,
            web_common.DEVICE_ID_PARTNER_2,
            web_common.DEVICE_PRIMARY_KEY_PARTNER_2,
            web_common.DRIVER_NAME_PARTNER_2,
            web_common.VEHICLE_PLATE_NUMBER_PARTNER_2,
            5,
        ),
        (
            web_common.PARTNER_PASSPORT_UID_2,
            web_common.DEVICE_ID_NO_PARTNER,
            web_common.DEVICE_PRIMARY_KEY_NO_PARTNER,
            web_common.DRIVER_NAME_NO_PARTNER,
            web_common.VEHICLE_PLATE_NUMBER_NO_PARTNER,
            2,
        ),
    ],
)
async def test_ok_overwrite(
        taxi_signal_device_api_admin,
        pgsql,
        pass_uid,
        device_id,
        device_primary_key,
        driver_name,
        vehicle_plate_number,
        index,
):
    response = await taxi_signal_device_api_admin.put(
        ENDPOINT, json={'name': pass_uid}, params={'device_id': device_id},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'name': pass_uid}
    web_common.check_device_web_info_in_db(
        pgsql,
        device_primary_key=device_primary_key,
        partner_passport_uid=pass_uid,
        device_name=DEVICE_NAME_PREFIX + str(index),
        driver_name=driver_name,
        vehicle_plate_number=vehicle_plate_number,
        updated_at_newer_than=web_common.OLD_UPDATED_AT,
    )


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
async def test_404(taxi_signal_device_api_admin, pgsql):
    @utils.check_table_not_changed(pgsql, 'devices_web_info')
    async def _():
        response = await taxi_signal_device_api_admin.put(
            ENDPOINT,
            json={'name': web_common.PARTNER_PASSPORT_UID_1},
            params={'device_id': web_common.DEVICE_ID_MISSING},
        )
        assert response.status_code == 404, response.text
        assert response.json() == {
            'code': '404',
            'message': (
                f'device with id '
                f'`{web_common.DEVICE_ID_MISSING}`'
                f' is not registered'
            ),
        }
