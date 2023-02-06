# pylint: disable=redefined-outer-name
import aiohttp
import aiohttp.web
import pytest

from taxi import config
from taxi.clients import geocoder
from taxi.clients import http_client
from taxi.clients import tvm


@pytest.fixture
def tvm_client(simple_secdist, patch):
    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {tvm.TVM_TICKET_HEADER: 'ticket'}

    return tvm.TVMClient(
        service_name='corp-cabinet',
        secdist=simple_secdist,
        config=config,
        session=None,
    )


@pytest.fixture
async def client_geocoder(loop, tvm_client):
    session = http_client.HTTPClient(loop=loop)

    yield geocoder.GeocoderClient(session, tvm_client, '$mockserver/geocoder')

    await session.close()


async def test_postal_code(
        client_geocoder: geocoder.GeocoderClient, mockserver, load_json,
):
    address = 'Москва, Льва Толстого, 16'

    stub = load_json('test_postal_code.json')

    @mockserver.json_handler('/geocoder/yandsearch')
    def _request(request):
        assert request.query == stub['request_params']
        return aiohttp.web.json_response(stub['response'])

    result = await client_geocoder.get_postal_code(address)

    assert result == '119021'


@pytest.mark.parametrize(
    'geocoder_response', [{}, {'features': []}, {'features': None}],
)
async def test_no_postal_code(
        client_geocoder: geocoder.GeocoderClient,
        mockserver,
        geocoder_response,
):
    address = 'Москва, Льва Толстого, 16'

    @mockserver.json_handler('/geocoder/yandsearch')
    def _request(request):
        return aiohttp.web.json_response(geocoder_response)

    with pytest.raises(geocoder.NoPostalCodeFound):
        await client_geocoder.get_postal_code(address)


async def test_search_organization(
        mockserver, client_geocoder: geocoder.GeocoderClient,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/geocoder/yandsearch')
    def get_by_business_oid(request):
        assert dict(request.query) == {
            'ms': 'json',
            'lang': 'ru',
            'type': 'biz',
            'business_oid': '1255966696',
            'origin': 'taxi',
            'snippets': 'businessimages/1.x',
        }
        return aiohttp.web.json_response({})

    await client_geocoder.search_organization(1255966696, 'ru')


async def test_get_locations(
        mockserver, client_geocoder: geocoder.GeocoderClient,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/geocoder/yandsearch')
    def get_by_business_oid(request):
        assert dict(request.query) == {
            'ms': 'json',
            'lang': 'ru',
            'type': 'biz',
            'text': 'chain_id:(35471869327)',
            'origin': 'taxi',
            'snippets': 'businessimages/1.x',
            'results': '1000',
        }
        return aiohttp.web.json_response({})

    await client_geocoder.get_locations_of_organization(35471869327, 'ru')


@pytest.mark.parametrize(
    'response_json, is_failed',
    [
        pytest.param(
            {
                'features': [
                    {'properties': {'GeocoderMetaData': {'Address': {}}}},
                ],
            },
            False,
            id='success',
        ),
        pytest.param({'features': None}, True, id='error'),
    ],
)
async def test_get_address_by_coordinates(
        mockserver,
        client_geocoder: geocoder.GeocoderClient,
        response_json,
        is_failed,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/geocoder/yandsearch')
    def _request(request):
        return aiohttp.web.json_response(response_json)

    error_occured = False
    try:
        await client_geocoder.get_address_by_coordinates(
            [37.473357, 55.784881],
        )
    except geocoder.NoAddressFound:
        error_occured = True

    assert error_occured == is_failed


@pytest.mark.parametrize(
    'status_code, expected_exception',
    [
        (400, geocoder.ClientError),
        (404, geocoder.ClientError),
        (464, geocoder.ClientError),
        (500, geocoder.ServerError),
        (502, geocoder.ServerError),
        (503, geocoder.ServerError),
        (556, geocoder.ServerError),
    ],
)
async def test_networking_error(
        mockserver,
        status_code,
        expected_exception,
        client_geocoder: geocoder.GeocoderClient,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/geocoder/yandsearch')
    def get_by_business_oid(request):
        return aiohttp.web.Response(status=status_code)

    with pytest.raises(expected_exception):
        await client_geocoder.search_organization(100, 'ru')
    with pytest.raises(expected_exception):
        await client_geocoder.get_locations_of_organization(100, 'ru')
