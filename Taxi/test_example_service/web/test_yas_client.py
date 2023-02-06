from aiohttp import web
import pytest

from generated.clients import yet_another_service as yas_module
from taxi.util import dates


DATE = '2017-11-01T01:10:00+03:00'


@pytest.fixture(name='client')
def yas_fixture(web_context):
    return web_context.clients.yet_another_service


@pytest.mark.now(DATE)
async def test_default(client, mock_yet_another_service):
    @mock_yet_another_service('/date')
    async def handler(request):
        assert request.query.get('int_param') is None
        return web.Response(text=dates.fast_timestring())

    response = await client.get_date()

    assert response.status == 200
    assert dates.localize(response.body).isoformat() == DATE
    assert handler.times_called == 1


async def test_x_real_ip_cutoff(client, mock_yet_another_service):
    @mock_yet_another_service('/date')
    async def handler(request):
        return web.json_response(dates.localize())

    with pytest.raises(TypeError) as exc_info:
        await client.get_date(x_real_ip='127.0.0.1')

    assert exc_info.value.args == (
        'get_date() got an unexpected keyword argument \'x_real_ip\'',
    )
    assert not handler.times_called


async def test_headers(client, mock_yet_another_service):
    @mock_yet_another_service('/echo-rate-limit')
    async def handler(request):
        limit = request.headers.get('X-RATE-LIMIT')
        return web.Response(headers={'x-rate-limit': limit})

    response = await client.echo_rate_limit(x_rate_limit=666)

    assert response.status == 200
    assert response.body is None
    assert response.headers.x_rate_limit == 666
    assert handler.times_called == 1


async def test_required_params(client, mock_yet_another_service):
    @mock_yet_another_service('/echo-rate-limit')
    async def handler(request):
        return web.Response()

    with pytest.raises(TypeError) as exc_info:
        await client.echo_rate_limit()

    assert exc_info.value.args == (
        'echo_rate_limit() missing 1 required positional '
        'argument: \'x_rate_limit\'',
    )
    assert not handler.times_called


async def test_query_multi_format(client, mock_yet_another_service):
    @mock_yet_another_service('/multi-query')
    async def handler(request):
        assert request.query.getall('multi') == ['1', '2', '3']
        return web.Response()

    response = await client.multi_query(multi=[1, 2, 3])

    assert response.status == 200
    assert response.body is None
    assert handler.times_called == 1


async def test_csv_query(client, mock_yet_another_service):
    @mock_yet_another_service('/csv-query')
    async def handler(request):
        assert request.query.getall('csv') == [','.join(['1', '2', '3'])]
        return web.Response()

    response = await client.csv_query(csv=[1, 2, 3])

    assert response.status == 200
    assert response.body is None
    assert handler.times_called == 1


async def test_csv_header(client, mock_yet_another_service):
    @mock_yet_another_service('/csv-header')
    async def handler(request):
        assert request.headers['x-csv-something'] == ','.join(['1', '2', '3'])
        return web.Response()

    response = await client.csv_header_post(x_csv_something=[1, 2, 3])

    assert response.status == 200
    assert response.body is None
    assert handler.times_called == 1


@pytest.mark.config(
    TVM_RULES=[{'src': 'example_service', 'dst': 'yet_another_service'}],
)
async def test_tvm_protected(client, mock_yet_another_service, patch):
    @patch(
        'example_service.generated.service.client_tvm.plugin.'
        'TVMClient.get_ticket',
    )
    async def get_ticket(*args, **kwargs):
        return '123'

    @mock_yet_another_service('/pong')
    async def pong_handler(request):
        assert request.headers['x-ya-service-ticket'] == '123'
        return web.Response()

    response = await client.pong(api_4_0_auth_context=None)

    assert response.status == 200
    assert response.body is None

    assert pong_handler.times_called == 1

    get_ticket_calls = get_ticket.calls
    assert len(get_ticket_calls) == 1
    assert get_ticket_calls[0]['args'][0] == 'yet_another_service'


@pytest.mark.config(
    TVM_RULES=[{'src': 'example_service', 'dst': 'yet_another_service'}],
)
async def test_tvm_unprotected(client, mock_yet_another_service, patch):
    @patch(
        'example_service.generated.service.client_tvm.plugin.'
        'TVMClient.get_ticket',
    )
    async def get_ticket(*args, **kwargs):
        return '123'

    @mock_yet_another_service('/ping')
    async def ping_handler(request):
        assert 'x-ya-service-ticket' not in request.headers
        return web.Response()

    response = await client.ping()

    assert response.status == 200
    assert response.body is None

    assert ping_handler.times_called == 1
    assert get_ticket.calls == []


@pytest.mark.now(DATE)
async def test_wrapped_client(client, mock_yet_another_service):
    @mock_yet_another_service('/date')
    async def handler(request):
        assert request.query.get('int_param') == '0'
        return web.Response(text=dates.fast_timestring())

    response = await client.get_someone_birthday()

    assert response.status == 200
    assert dates.localize(response.body).isoformat() == DATE
    assert handler.times_called == 1


async def test_extra_keys(client, mock_yet_another_service):
    @mock_yet_another_service('/get_some')
    async def handler(request):
        return web.json_response(
            {
                'name': 'abaca',
                'extra': 12,
                'extra_list': ['0', 1],
                'another': {
                    'name': 'David',
                    'extra': {'a': 'b'},
                    'extra_list': ['boom', 'clap'],
                },
                'array': [
                    {'name': 'Kent', 'extra': 1, 'extra_list': [3, 4, 5]},
                    {
                        'name': 'Clark',
                        'extra': 100500,
                        'extra_list': [{'1': 1, '2': 3}],
                    },
                ],
                'more': {
                    'size': 1020,
                    'extra': {'a': 'b'},
                    'extra_list': [1, 2, 3],
                },
            },
        )

    response = await client.get_some()

    assert response.status == 200

    def _check_extra(obj):
        assert not hasattr(obj, 'extra')
        assert not hasattr(obj, 'extra_list')

    body = response.body
    assert body.name == 'abaca'
    _check_extra(body)

    assert body.another.name == 'David'
    _check_extra(body.another)

    assert body.array[0].name == 'Kent'
    _check_extra(body.array[0])

    assert body.array[1].name == 'Clark'
    _check_extra(body.array[1])

    assert body.more.size == 1020
    _check_extra(body.more)

    assert handler.times_called == 1


async def test_additional_properties(client, mock_yet_another_service):
    @mock_yet_another_service('/get_extra')
    async def handler(request):
        return web.json_response({'name': 'ababa', 'x': 'y', 'z': [0, 1, 2]})

    response = await client.get_extra()

    assert response.status == 200
    assert response.body.name == 'ababa'
    assert response.body.extra == {'x': 'y', 'z': [0, 1, 2]}
    assert handler.times_called == 1


async def test_get_request_no_content_type(client, mock_yet_another_service):
    @mock_yet_another_service('/ping')
    async def ping_handler(request):
        assert 'Content-Type' not in request.headers
        return web.Response()

    response = await client.ping()

    assert response.status == 200
    assert response.body is None

    assert ping_handler.times_called == 1


@pytest.mark.parametrize('charset', [None, 'UTF-8', 'utf-8'])
async def test_201(client, mock_yet_another_service, charset):
    @mock_yet_another_service('/talk')
    async def handler(request):
        return web.Response(
            body='NOPE',
            status=201,
            content_type='text/plain',
            charset=charset,
        )

    response = await client.talk(log_extra={'a': 'b'})

    assert response.status == 201
    assert response.body == 'NOPE'

    assert handler.times_called == 1


async def test_common_parameters(client, mock_yet_another_service):
    @mock_yet_another_service('/common-parameters')
    async def handler(request):
        assert request.query['name'] == 'Ivan'
        assert request.query['surname'] == 'Podjigatel'
        return web.Response()

    response = await client.common_parameters_get(
        name='Ivan', surname='Podjigatel',
    )

    assert response.status == 200
    assert response.body is None

    assert handler.times_called == 1


async def test_binary(client, mock_yet_another_service):
    @mock_yet_another_service('/test_binary/add_prefix', raw_request=True)
    async def handler(request):
        assert await request.read() == b'abacaba'
        assert request.headers['Content-type'] == 'application/octet-stream'
        return web.Response(
            body=b'101', headers={'Content-Type': 'application/octet-stream'},
        )

    response = await client.test_binary_add_prefix_post(body=b'abacaba')
    assert response.status == 200
    assert response.body == b'101'

    assert handler.times_called == 1


async def test_form_multipart(client, mock_yet_another_service):
    @mock_yet_another_service('/test_forms/happy-multipart', raw_request=True)
    async def handler(request):
        form = await request.post()
        assert request.content_type == 'multipart/form-data'
        assert form.getall('name') == ['bacbac']
        assert form.getall('age') == ['11']
        assert form.getall('cars') == ['lada', 'jeep']
        assert form.getall('colors') == ['white,black']
        return web.Response(body='0')

    response = await client.test_forms_happy_multipart_post(
        name='bacbac',
        age=11,
        cars=['lada', 'jeep'],
        colors=['white', 'black'],
    )
    assert response.status == 200
    assert response.body == 0
    assert handler.times_called == 1


async def test_form_urlencoded(client, mock_yet_another_service):
    @mock_yet_another_service('/test_forms/happy-urlencoded', raw_request=True)
    async def handler(request):
        form = await request.post()
        assert request.content_type == 'application/x-www-form-urlencoded'
        assert form.getall('name') == ['bacbac']
        assert form.getall('age') == ['11']
        assert form.getall('cars') == ['lada', 'jeep']
        assert form.getall('colors') == ['white,black']
        return web.Response(body='0')

    response = await client.test_forms_happy_urlencoded_post(
        name='bacbac',
        age=11,
        cars=['lada', 'jeep'],
        colors=['white', 'black'],
    )
    assert response.status == 200
    assert response.body == 0
    assert handler.times_called == 1


async def test_form_file(client, mock_yet_another_service):
    @mock_yet_another_service('/test_forms/save-file-report', raw_request=True)
    async def handler(request):
        form = await request.post()
        assert request.content_type == 'multipart/form-data'
        report = form['report']
        assert isinstance(report, web.FileField)
        content = report.file.read()
        assert content == b'hello'
        return web.json_response(
            {'size': len(content), 'filename': report.filename},
        )

    response = await client.test_forms_save_file_report_post(
        report=b'hello', report_filename='report.csv',
    )
    assert response.status == 200
    assert response.body.size == 5
    assert response.body.filename == 'report.csv'
    assert handler.times_called == 1


async def test_binary_multipart(client, mock_yet_another_service):
    @mock_yet_another_service('/test_forms/binary-multipart', raw_request=True)
    async def handler(request):
        assert request.content_type == 'multipart/form-data'
        form = await request.post()
        binary_data = form['binary_data']
        assert isinstance(binary_data, web.FileField)
        content = binary_data.file.read()
        assert content == b'hello'
        return web.Response(body='world')

    response = await client.test_forms_binary_multipart_post(
        binary_data=b'hello',
    )
    assert response.status == 200
    assert response.body == 'world'
    assert handler.times_called == 1


async def test_lib_model(client, mock_yet_another_service):
    @mock_yet_another_service('/geopoint')
    async def handler(request):
        return {
            'lat': int(request.query.get('lat')),
            'lon': int(request.query.get('lon')),
        }

    response = await client.geopoint_get(lat=63, lon=34)
    assert response.status == 200
    assert response.body.lat == 63
    assert response.body.lon == 34
    assert handler.times_called == 1


@pytest.mark.config(
    XSERVICE_CLIENT_QOS={'__default__': {'timeout-ms': 5000, 'attempts': 2}},
    CORP_BILLING_CLIENT_QOS={
        '__default__': {'timeout-ms': 5000, 'attempts': 5},
    },
)
async def test_qos_mixing(client, mock_yet_another_service):
    # /ping use XSERVICE_CLIENT_QOS
    @mock_yet_another_service('/ping')
    async def ping_handler(request):
        return web.Response(status=500)

    # /test_inline/ping use CORP_BILLING_CLIENT_QOS
    @mock_yet_another_service('/test_inline/ping')
    async def another_ping_handler(request):
        return web.Response(status=500)

    with pytest.raises(yas_module.NotDefinedResponse) as exc_info:
        await client.ping()

    assert exc_info.value.status == 500

    with pytest.raises(yas_module.NotDefinedResponse) as exc_info:
        await client.test_inline_ping_get()

    assert exc_info.value.status == 500

    assert ping_handler.times_called == 2
    assert another_ping_handler.times_called == 5


@pytest.mark.config(SAFETY_CENTER_ACCIDENTS_RETRIES=2, GEOTRACKS_GET_RETRIES=5)
async def test_x_taxi_retries(client, mock_yet_another_service):
    # happy-urlencoded under global SAFETY_CENTER_ACCIDENTS_RETRIES
    @mock_yet_another_service('/test_forms/happy-urlencoded')
    async def handler_2_times(request):
        return web.Response(status=502)

    # happy-multipart under local GEOTRACKS_GET_RETRIES
    @mock_yet_another_service('/test_forms/happy-multipart')
    async def handler_5_times(request):
        return web.Response(status=503)

    with pytest.raises(yas_module.NotDefinedResponse) as exc_info:
        await client.test_forms_happy_urlencoded_post(
            name='bacbac',
            age=11,
            cars=['lada', 'jeep'],
            colors=['white', 'black'],
        )

    assert exc_info.value.status == 502

    with pytest.raises(yas_module.NotDefinedResponse) as exc_info:
        await client.test_forms_happy_multipart_post(
            name='bacbac',
            age=11,
            cars=['lada', 'jeep'],
            colors=['white', 'black'],
        )

    assert exc_info.value.status == 503

    assert handler_2_times.times_called == 2
    assert handler_5_times.times_called == 5


async def test_type_parameter(client, mock_yet_another_service):
    @mock_yet_another_service('/type-description')
    async def handler(request):
        return {
            'type': request.query['type'] + 'bac',
            'limit': int(request.query['limit']) + 1,
        }

    response = await client.type_description_get(type='aa', limit=10)
    assert response.status == 200
    assert response.body.type == 'aabac'
    assert response.body.limit == 11
    assert handler.times_called == 1


async def test_incorrect_content_type(client, mock_yet_another_service):
    @mock_yet_another_service('/test_binary/add_prefix', raw_request=True)
    async def handler(request):
        assert await request.read() == b'abacaba'
        assert request.headers['Content-type'] == 'application/octet-stream'
        return web.json_response({})

    with pytest.raises(
            yas_module.TestBinaryAddPrefixPostInvalidResponse,
    ) as exc_info:
        await client.test_binary_add_prefix_post(body=b'abacaba')

    assert exc_info.value.status == 200
    assert exc_info.value.exc_str == (
        'Invalid Content-Type: application/json; charset=utf-8; '
        'expected one of [\'application/octet-stream\']'
    )

    assert handler.times_called == 1


async def test_request_id(client, mock_yet_another_service):
    @mock_yet_another_service('/ping')
    async def handler(request):
        assert request.headers['X-YaRequestId']

    resp = await client.ping()

    assert resp.status == 200
    assert handler.times_called == 1


async def test_openapi_multiple_responses(client, mock_yet_another_service):
    @mock_yet_another_service('/openapi/multiple-responses')
    async def handler(request):
        if request.query['name'] == 'matrix':
            return web.Response(
                body=b'\xAA', content_type='application/octet-stream',
            )
        return web.Response(body='text')

    resp = await client.openapi_multiple_responses_get(name='matrix')
    assert resp.status == 200
    assert resp.body == b'\xAA'

    resp = await client.openapi_multiple_responses_get(name='wake up')
    assert resp.status == 200
    assert resp.body == 'text'
    assert handler.times_called == 2


async def test_not_defined_response_truncate(
        client, mock_yet_another_service, caplog,
):
    @mock_yet_another_service('/ping')
    async def handler(request):
        return web.Response(text='a' * 9000, status=500)

    with pytest.raises(yas_module.NotDefinedResponse) as exc_info:
        await client.ping()
    assert exc_info.value.status == 500
    assert handler.times_called == 3
    assert str(exc_info.value) == (
        'Not defined in schema yet-another-service response, '
        'status: 500, body: b\'' + 'a' * 4094 + '...'
    )


async def test_invalid_response_truncate(
        client, mock_yet_another_service, caplog,
):
    @mock_yet_another_service('/talk')
    async def handler(request):
        return web.Response(text='a' * 9876, status=201)

    with pytest.raises(yas_module.TalkInvalidResponse) as exc_info:
        await client.talk()
    assert exc_info.value.status == 201
    assert handler.times_called == 1
    assert str(exc_info.value) == (
        'yet-another-service invalid response: '
        'Invalid value for body: \''
        + 'a' * 1023
        + ' must be one of [\'NOPE\'], '
        'status: 201, body: b\'' + 'a' * 4094 + '...'
    )


async def test_openapi_bad_multiple_responses(
        client, mock_yet_another_service,
):
    @mock_yet_another_service('/openapi/multiple-responses')
    async def handler(request):
        return {}

    with pytest.raises(
            yas_module.OpenapiMultipleResponsesGetInvalidResponse,
    ) as exc_info:
        await client.openapi_multiple_responses_get(name='matrix')

    assert exc_info.value.status == 200
    assert handler.times_called == 1


@pytest.mark.config(
    XSERVICE_CLIENT_QOS={
        '__default__': {'timeout-ms': 5000, 'attempts': 1},
        '/path-parameters/{name}': {'timeout-ms': 5000, 'attempts': 2},
    },
)
async def test_in_path_parameters_qos_with_placeholders(
        client, mock_yet_another_service,
):
    @mock_yet_another_service('/path-parameters/vasya')
    async def handler(request):
        return web.Response(status=500)

    with pytest.raises(yas_module.NotDefinedResponse) as exc_info:
        await client.path_parameters_name_get(name='vasya')

    assert exc_info.value.status == 500
    # default config is used
    assert handler.times_called == 1


@pytest.mark.config(
    XSERVICE_CLIENT_QOS={
        '__default__': {'timeout-ms': 5000, 'attempts': 1},
        '/path-parameters/name': {'timeout-ms': 5000, 'attempts': 2},
    },
)
async def test_in_path_parameters_qos_without_placeholders(
        client, mock_yet_another_service,
):
    @mock_yet_another_service('/path-parameters/vasya')
    async def handler(request):
        return web.Response(status=500)

    with pytest.raises(yas_module.NotDefinedResponse) as exc_info:
        await client.path_parameters_name_get(name='vasya')

    assert exc_info.value.status == 500
    # values for /path-parameters/name are used
    assert handler.times_called == 2


async def test_openapi_form_multipart(client, mock_yet_another_service):
    @mock_yet_another_service(
        '/test_forms/v3/happy-multipart', raw_request=True,
    )
    async def handler(request):
        form = await request.post()
        assert request.content_type == 'multipart/form-data'
        assert form.getall('name') == ['bacbac']
        assert form.getall('age') == ['11']
        return web.Response(body='0')

    response = await client.test_forms_v3_happy_multipart_post(
        name='bacbac', age=11,
    )
    assert response.status == 200
    assert response.body == 0
    assert handler.times_called == 1


async def test_openapi_form_urlencoded(client, mock_yet_another_service):
    @mock_yet_another_service(
        '/test_forms/v3/happy-urlencoded', raw_request=True,
    )
    async def handler(request):
        form = await request.post()
        assert request.content_type == 'application/x-www-form-urlencoded'
        assert form.getall('name') == ['bacbac']
        assert form.getall('age') == ['11']
        return web.Response(body='0')

    response = await client.test_forms_v3_happy_urlencoded_post(
        name='bacbac', age=11,
    )
    assert response.status == 200
    assert response.body == 0
    assert handler.times_called == 1


async def test_openapi_form_file(client, mock_yet_another_service):
    @mock_yet_another_service(
        '/test_forms/v3/save-file-report', raw_request=True,
    )
    async def handler(request):
        form = await request.post()
        assert request.content_type == 'multipart/form-data'
        report = form['file']
        assert isinstance(report, web.FileField)
        content = report.file.read()
        assert content == b'hello'
        return web.json_response(
            {'size': len(content), 'filename': report.filename},
        )

    response = await client.test_forms_v3_save_file_report_post(file=b'hello')
    assert response.status == 200
    assert response.body.size == 5
    assert response.body.filename == 'file'
    assert handler.times_called == 1
