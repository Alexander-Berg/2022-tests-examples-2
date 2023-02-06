import pytest


HANDLER_PATH = 'v1/contractor/blocking/complete_scores/count'
TST_UDID = '5b05621ee6c22ea2654849c9'
OTHER_UDID = '5bee7e37254e5eb96a36dca4'


@pytest.mark.parametrize(
    'request_udid, count', [(TST_UDID, 1), (OTHER_UDID, 0)],
)
@pytest.mark.filldb(unique_drivers='common', dm_blocking_journal='common')
async def test_driver_activity(web_app_client, request_udid, count):
    response = await web_app_client.get(
        HANDLER_PATH, params={'unique_driver_id': request_udid},
    )
    content = await response.json()

    assert response.status == 200
    assert content['count'] == count
