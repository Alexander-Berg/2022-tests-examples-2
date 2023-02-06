# pylint: disable=redefined-outer-name
import asyncio
import json
import logging

import aiohttp
import pytest

from taxi import config
from taxi import discovery
from taxi.clients import tvm
from taxi.clients import ucommunications

logger = logging.getLogger(__name__)


@pytest.fixture
def tvm_client(simple_secdist, patch):
    @patch('taxi.clients.tvm.TVMClient.check_rules')
    def _check_rules_mock(*args, **kwargs):
        return True

    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {tvm.TVM_TICKET_HEADER: 'ticket'}

    return tvm.TVMClient(
        service_name='ucommunications',
        secdist=simple_secdist,
        config=config,
        session=None,
    )


@pytest.fixture
async def client(db, loop, tvm_client):
    class Config(config.Config):
        UCOMMUNICATIONS_CLIENT_QOS = {
            '__default__': {'attempts': 3, 'timeout-ms': 500},
        }

    return ucommunications.UcommunicationsClient(
        service=discovery.find_service('ucommunications'),
        session=aiohttp.ClientSession(loop=loop),
        config=Config(db),
        tvm_client=tvm_client,
    )


@pytest.mark.parametrize(
    'exception_type', [aiohttp.ClientError, asyncio.TimeoutError],
)
@pytest.mark.nofilldb()
async def test_request_try_and_fail(client, patch, exception_type):
    @patch('aiohttp.ClientSession.request')
    async def _request(*args, **kwargs):
        assert kwargs['method'] == 'POST'
        assert json.loads(kwargs['data']) == {
            'phone_id': 'test_phone_id',
            'text': 'test_text',
            'intent': 'test_intent',
            'sender': 'test_sender',
        }
        raise exception_type()

    with pytest.raises(ucommunications.UcommunicationsRequestRetriesError):
        await client.send_sms_to_user(
            'test_phone_id', 'test_text', 'test_intent', 'test_sender',
        )


async def test_hide_personal(client):
    def _logging(client, url, method, data):
        for field in ucommunications.PERSONAL_FIELDS:
            assert data[field] == '***'

    patched_logging = ucommunications.hide_personal_info(_logging)
    patched_logging(client, 'test_url', 'POST', {'phone': '+79159999999'})
