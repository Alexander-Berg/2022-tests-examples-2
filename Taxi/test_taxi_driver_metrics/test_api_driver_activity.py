import pytest


HANDLER_PATH = 'v1/driver/activity/'
TST_UDID = '5b05621ee6c22ea2654849c9'
OTHER_UDID = '5bee7e37254e5eb96a36dca4'
INVALID_UDID = '________________________'
FALLBACK = 90


@pytest.mark.parametrize('dms_response', [92, 93, None])
@pytest.mark.parametrize('request_udid', [TST_UDID, INVALID_UDID, OTHER_UDID])
@pytest.mark.filldb(unique_drivers='common')
async def test_driver_activity(
        web_context, web_app_client, mockserver, request_udid, dms_response,
):
    @mockserver.json_handler('/driver-metrics-storage/v2/activity_values/list')
    def _patch_dms(*_args, **_kwargs):
        item = {
            'unique_driver_id': request_udid,
            'value': dms_response or FALLBACK,
        }

        return {'items': [item]}

    response = await web_app_client.post(
        HANDLER_PATH, json={'unique_driver_id': request_udid},
    )
    content = await response.json()

    assert response.status == 200
    assert content['activity'] == dms_response or FALLBACK
