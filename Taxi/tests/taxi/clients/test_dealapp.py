# pylint: disable=redefined-outer-name
import http

import aiohttp
import pytest


from taxi import config as config_module
from taxi.clients import dealapp

DEALAPP_INTEGRATION_ID = '1234567890'
DEALAPP_MOCK_URI = f'/dealapp/{DEALAPP_INTEGRATION_ID}/text'


@pytest.fixture
async def client(loop, simple_secdist):
    session = aiohttp.ClientSession(loop=loop)
    config = config_module.Config()
    config.DEALAPP_INTEGRATION_ID = DEALAPP_INTEGRATION_ID
    yield dealapp.DealAppClient(
        session=session, secdist=simple_secdist, config=config,
    )
    await session.close()


@pytest.mark.parametrize(
    'status,expected_exception',
    [
        (http.HTTPStatus.BAD_REQUEST, dealapp.InvalidDocumentError),
        (http.HTTPStatus.UNAUTHORIZED, dealapp.UnauthorizedError),
        (http.HTTPStatus.NOT_FOUND, dealapp.NotFoundError),
        (http.HTTPStatus.REQUEST_TIMEOUT, dealapp.RequestTimeoutError),
        (
            http.HTTPStatus.UNPROCESSABLE_ENTITY,
            dealapp.UnprocessableEntityError,
        ),
        (http.HTTPStatus.CONFLICT, dealapp.BaseError),
        (http.HTTPStatus.INTERNAL_SERVER_ERROR, dealapp.BaseError),
    ],
)
async def test_exceptions(client, mockserver, status, expected_exception):
    @mockserver.json_handler(DEALAPP_MOCK_URI)
    async def _send_chat(request):
        return mockserver.make_response(
            json={'message': 'Message', 'code': 'ERROR_CODE'}, status=status,
        )

    with pytest.raises(expected_exception):
        await client.send_chat({'key': 'value'})


async def test_send_chat(client, mockserver):
    @mockserver.json_handler(DEALAPP_MOCK_URI)
    async def _send_chat(request):
        return mockserver.make_response(
            json={'message': 'Message'}, status=http.HTTPStatus.OK,
        )

    response = await client.send_chat({'key': 'value'})
    assert response == {'message': 'Message'}
