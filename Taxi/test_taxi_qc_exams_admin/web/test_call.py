import typing

from aiohttp import test_utils
from aiohttp import web
import pytest


def _mock_responses(mockserver, load_json: typing.Callable[[str], dict]):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _fleet_parks_handler(request):
        return load_json('fleet_parks_response.json')

    @mockserver.json_handler('/quality-control-py3/api/v1/data')
    def _quality_control_data_handler(request):
        return load_json('quality_control_get_data_response.json')

    @mockserver.json_handler('/quality-control-py3/api/v1/state')
    def _quality_control_state_handler(request):
        return load_json('quality_control_post_state_response.json')

    @mockserver.handler('/communications/driver/notification/bulk-push')
    def _push_handler(request):
        return web.json_response(status=200, content_type='text/plain')

    @mockserver.handler('/client-notify/v2/bulk-push')
    def _push_cn_handler(request):
        return web.json_response(data={'notifications': []})


@pytest.mark.config(
    QC_COMMS_CHECK_PUSH_SETTINGS=dict(
        lag='5s', expiration='1h', use_client_notify=False,
    ),
)
async def test_call(
        web_app_client: test_utils.TestClient,
        mockserver,
        load_json: typing.Callable[[str], dict],
):
    _mock_responses(mockserver, load_json)
    resp = await web_app_client.post(
        path='/qc-admin/v1/call', json=load_json('call_driver_dkk.json'),
    )
    assert resp.status == 200


@pytest.mark.config(
    QC_COMMS_CHECK_PUSH_SETTINGS=dict(
        lag='5s', expiration='1h', use_client_notify=True,
    ),
)
async def test_call_client_notify(
        web_app_client: test_utils.TestClient,
        mockserver,
        load_json: typing.Callable[[str], dict],
):
    _mock_responses(mockserver, load_json)
    resp = await web_app_client.post(
        path='/qc-admin/v1/call', json=load_json('call_driver_dkk.json'),
    )
    assert resp.status == 200
