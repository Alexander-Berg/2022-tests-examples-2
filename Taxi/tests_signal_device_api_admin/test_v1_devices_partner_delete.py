import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'v1/devices/partner'


def check_web_info_deleted_from_db(pgsql, device_id):
    db = pgsql['signal_device_api_meta_db'].cursor()
    query_str = (
        'SELECT '
        '  id   '
        'FROM signal_device_api.devices_web_info '
        'WHERE id='
        '   (SELECT id FROM signal_device_api.devices '
        '    WHERE public_id=\'{}\');'.format(str(device_id))
    )
    print('Looking up device web info not present with query ' + query_str)
    db.execute(query_str)
    assert list(db) == []


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'device_id',
    [web_common.DEVICE_ID_PARTNER_1, web_common.DEVICE_ID_NO_PARTNER],
)
async def test_ok(taxi_signal_device_api_admin, pgsql, device_id):
    response = await taxi_signal_device_api_admin.delete(
        ENDPOINT, json={}, params={'device_id': device_id},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {}
    check_web_info_deleted_from_db(pgsql, device_id)


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
async def test_404(taxi_signal_device_api_admin, pgsql):
    @utils.check_table_not_changed(pgsql, 'devices_web_info')
    async def _():
        response = await taxi_signal_device_api_admin.delete(
            ENDPOINT,
            json={},
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
