# pylint: disable=unused-variable
from aiohttp import web
import pytest

from hiring_utils.stq import newdriver_request
from test_hiring_utils import conftest

TOKEN = 'token_driveryandex'


@pytest.mark.parametrize('status', [200, 400, 409])
@pytest.mark.config(
    HIRING_UTILS_ENABLE_HIRING_API=True,
    INFRANAIM_NEWDRIVER_FIELDS=[
        'name',
        'phone',
        'description',
        'subject',
        'phone_pd_id',
    ],
)
@conftest.main_configuration
async def test_newdriver(
        stq3_context,
        mock_infranaim_api,
        mock_hiring_api,
        mock_territories_api,
        personal,
        status,
):
    @mock_infranaim_api('/api/v1/submit/driveryandex')
    def infranaim(request):
        if request.headers['token'] != TOKEN:
            raise ValueError(request.headers['token'])
        assert request.json.get('params', {}).get('comment')
        return web.json_response(
            {'code': status, 'message': '', 'details': ''}, status=status,
        )

    @mock_hiring_api('/v1/tickets/create')
    def hiring_api(request):
        fields = {
            item['name']: item['value'] for item in request.json['fields']
        }
        assert fields.get('personal_phone_id')
        return web.json_response(
            {'code': 'SUCCESS', 'message': '', 'details': {}}, status=status,
        )

    await newdriver_request.task(stq3_context, 'request_driver_yandex')
    assert infranaim.has_calls
    assert hiring_api.has_calls
