# pylint: disable=redefined-outer-name,unused-variable,protected-access
import aiohttp
import pytest

from taxi import config
from taxi import discovery
from taxi.clients import territories
from taxi.clients import tvm


@pytest.fixture
async def client(loop, db):
    return territories.TerritoriesApiClient(
        service=discovery.find_service('territories'),
        secdist={'settings_override': {'TERRITORIES_API_TOKEN': 'secret'}},
        config=config.Config(db),
        session=aiohttp.ClientSession(loop=loop),
        db=db,
        retries=5,
        timeout=0,
    )


async def test_territories_client(client, mockserver, response_mock):
    @mockserver.json_handler('/territories', prefix=True)
    def patch_request(request):
        if 'list' in request.url:
            return {'countries': [{'_id': 'rus'}]}
        if 'retrieve' in request.url:
            return {'_id': 'rus'}
        return None

    countries = await client.get_all_countries()
    assert countries == [{'_id': 'rus'}]
    assert patch_request.times_called == 1
    assert (
        patch_request.next_call()['request'].headers['YaTaxi-Api-Key']
        == 'secret'
    )
    country = await client.get_country('rus')
    assert patch_request.times_called == 1
    assert country == {'_id': 'rus'}

    await client.session.close()


@pytest.mark.parametrize('failed_number', [4, 6])
async def test_connection_error(
        client,
        patch_aiohttp_session,
        response_mock,
        failed_number,
        mockserver,
):
    retries_count = 0

    @mockserver.json_handler('/territories', prefix=True)
    def patch_request(*args, **kwargs):
        nonlocal retries_count
        if retries_count < failed_number:
            retries_count += 1
            raise mockserver.NetworkError()
        else:
            return {}

    try:
        await client.get_country('rus')
        assert failed_number < 5
    except territories.RequestRetriesExceeded:
        assert failed_number > 5

    await client.session.close()


@pytest.mark.parametrize('use_tvm', [True, False])
async def test_auth(
        simple_secdist,
        aiohttp_client,
        patch,
        patch_aiohttp_session,
        response_mock,
        client,
        use_tvm,
        mockserver,
):
    @mockserver.json_handler('/territories', prefix=True)
    def handle(request):
        if use_tvm:
            assert request.headers[tvm.TVM_TICKET_HEADER] == 'ticket'
        else:
            assert request.headers['YaTaxi-Api-Key'] == 'secret'

        return {'countries': []}

    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {tvm.TVM_TICKET_HEADER: 'ticket'}

    tvm_client = tvm.TVMClient(
        service_name='billing_subventions',
        secdist=simple_secdist,
        config=config,
        session=aiohttp_client,
    )

    if use_tvm:
        client._tvm = tvm_client

    await client.get_all_countries()
    assert handle.times_called == 1

    await client.session.close()
