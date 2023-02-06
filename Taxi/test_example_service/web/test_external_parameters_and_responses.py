from aiohttp import web
import pytest

from generated.clients import yet_another_service as yas_module
from taxi.codegen import swaggen_serialization as utils

from . import common


@pytest.mark.parametrize(
    'params',
    [
        common.Params(
            request={'zone_id': 'xxx', 'suggested_name': 'abc'},
            status=404,
            response={
                'code': 'ZONE_ERROR',
                'message': 'ZONE (xxx, 1, abc) not found',
            },
        ),
        common.Params(
            request={
                'zone_id': 'yyy',
                'suggested_name': 'abcdef',
                'max_accuracy': '12',
            },
            status=404,
            response={
                'code': 'ZONE_ERROR',
                'message': 'ZONE (yyy, 12, abcdef) not found',
            },
        ),
        common.Params(
            request={},
            status=400,
            response=common.make_request_error(
                'zone_id is required parameter',
            ),
        ),
        common.Params(
            request={'zone_id': 'VII'},
            status=400,
            response=common.make_request_error(
                'suggested_name is required parameter',
            ),
        ),
        common.Params(
            request={
                'zone_id': 'IIX',
                'suggested_name': 'VIII',
                'max_accuracy': '-1',
            },
            status=400,
            response=common.make_request_error(
                'Invalid value for max_accuracy: -1 '
                'must be a value greater than or equal to 1',
            ),
        ),
    ],
)
async def test_server(web_app_client, params):
    response = await web_app_client.get(
        '/external-definitions/zone', params=params.request,
    )
    assert response.status == params.status
    assert await response.json() == params.response


async def test_client_happy_path(web_context, mock_yet_another_service):
    @mock_yet_another_service('/external-definitions/zone')
    async def handle(request):
        assert request.query['suggested_name'] == 'asdad'
        assert request.query['zone_id'] == 'III'
        assert 'max_accuracy' not in request.query

    client = web_context.clients.yet_another_service
    response = await client.external_definitions_zone_get(
        suggested_name='asdad', zone_id='III',
    )

    assert response.status == 200
    assert handle.times_called == 1


@pytest.mark.parametrize(
    'suggested_name, zone_id, max_accuracy, error',
    [
        (
            'abaca',
            'III',
            -1,
            'Invalid value for max_accuracy: -1 '
            'must be a value greater than or equal to 1',
        ),
        (
            'X',
            'III',
            1,
            'Invalid value for suggested_name: \'X\' '
            'length must be greater than or equal to 3',
        ),
        (
            'abaca',
            'VIII',
            1,
            'Invalid value for zone_id: \'VIII\' '
            'length must be less than or equal to 3',
        ),
    ],
)
async def test_client_errors(
        web_context, suggested_name, zone_id, max_accuracy, error,
):
    client = web_context.clients.yet_another_service
    with pytest.raises(utils.ValidationError) as exc_info:
        await client.external_definitions_zone_get(
            suggested_name=suggested_name,
            zone_id=zone_id,
            max_accuracy=max_accuracy,
        )

    assert exc_info.value.args == (error,)


async def test_response_with_definition(web_app_client):
    response = await web_app_client.get('/1', params={'not-found': 'true'})
    assert response.status == 404
    assert await response.json() == {
        'name': 'Vasya',
        'greetings': 'Nado, Vasya, nado',
    }


@pytest.mark.config(
    XSERVICE_CLIENT_QOS={
        '/external-definitions/zone': {'attempts': 1, 'timeout-ms': 10000},
    },
)
async def test_client_response_from_definitions_dir(
        web_context, mock_yet_another_service,
):
    @mock_yet_another_service('/external-definitions/zone')
    async def handle(request):
        return web.json_response(data={'extra-name': 'n-a-m-e'}, status=500)

    client = web_context.clients.yet_another_service
    with pytest.raises(yas_module.ExternalDefinitionsZoneGet500) as exc_info:
        await client.external_definitions_zone_get(
            suggested_name='asdad', zone_id='III',
        )
    response = exc_info.value

    assert response.status == 500
    assert response.body.extra_name == 'n-a-m-e'
    assert handle.times_called == 1
