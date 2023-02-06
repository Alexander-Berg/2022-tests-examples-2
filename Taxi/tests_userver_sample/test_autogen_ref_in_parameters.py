import pytest


async def do_test(
        client,
        mockserver,
        request_url,
        request_headers,
        request_params,
        expected_body,
        expected_headers,
        expected_code=200,
        path_name=None,
        mock_times_called=1,
) -> None:
    handler_url = 'autogen/ref-in-parameters-schema/openapi-3-0/' + request_url

    int_params = ('ref_query_int_required', 'ref_query_int', 'integer')
    headers = (
        'ref_header_string_required',
        'ref_header_string',
        'ref_header_str_enum',
        'ref_header_int',
    )

    @mockserver.json_handler('userver-sample/' + handler_url)
    def mock_view(request):
        params = {}
        if path_name and path_name in int_params:
            params[path_name] = int(request.path.split('/')[-1])
        elif path_name:
            params[path_name] = request.path.split('/')[-1]

        for param in request.query.keys():
            if param in int_params:
                params[param] = int(request.query[param])
            elif param == 'ref_query_bool':
                params[param] = bool(request.query[param])
            else:
                params[param] = request.query[param]

        return mockserver.make_response(
            headers={
                h: request.headers[h] for h in headers if h in request.headers
            },
            content_type='application/json',
            json=params,
        )

    response = await client.get(
        handler_url, headers=request_headers, params=request_params,
    )

    assert response.status_code == expected_code
    assert response.json() == expected_body
    for header_key, header_value in expected_headers.items():
        assert header_key in response.headers
        assert response.headers[header_key] == header_value

    assert mock_view.times_called == mock_times_called


async def test_ref_query_header(taxi_userver_sample, mockserver):
    headers = {'ref_header_string_required': 'qwe'}
    params = {'ref_query_int_required': 2}
    await do_test(
        taxi_userver_sample,
        mockserver,
        request_url='query_headers',
        request_headers=headers,
        request_params=params,
        expected_body=params,
        expected_headers=headers,
    )


async def test_ref_query_header_wo_required_header(
        taxi_userver_sample, mockserver,
):
    headers = {'ref_header_string': 'qwe', 'ref_header_str_enum': 'value1'}
    params = {'ref_query_int_required': 2}
    expected_body = {
        'code': '400',
        'message': 'Missing ref_header_string_required in header',
    }
    await do_test(
        taxi_userver_sample,
        mockserver,
        request_url='query_headers',
        request_headers=headers,
        request_params=params,
        expected_body=expected_body,
        expected_headers={},
        expected_code=400,
        mock_times_called=0,
    )


async def test_ref_query_header_all_headers(taxi_userver_sample, mockserver):
    headers = {
        'ref_header_string_required': 'str',
        'ref_header_string': 'qwe',
        'ref_header_str_enum': 'value1',
        'ref_header_int': '2',
    }
    params = {
        'ref_query_int_required': 2,
        'ref_query_int': 2,
        'ref_query_bool': True,
        'ref_query_string': 'str',
        'ref_query_str_enum': 'value1',
    }
    await do_test(
        taxi_userver_sample,
        mockserver,
        request_url='query_headers',
        request_headers=headers,
        request_params=params,
        expected_body=params,
        expected_headers=headers,
    )


async def test_ref_query_header_wo_required_query(
        taxi_userver_sample, mockserver,
):
    headers = {'ref_header_string_required': 'qwe'}
    params = {'ref_query_int': 2}
    expected_body = {
        'code': '400',
        'message': 'Missing ref_query_int_required in query',
    }
    await do_test(
        taxi_userver_sample,
        mockserver,
        request_url='query_headers',
        request_headers=headers,
        request_params=params,
        expected_body=expected_body,
        expected_headers={},
        expected_code=400,
        mock_times_called=0,
    )


@pytest.mark.parametrize(
    'url, response_var_name, path_param',
    [
        ('path_int', 'integer', 10),
        ('path_string', 'string', 'qwe'),
        ('path_string_enum', 'enum', 'value1'),
        ('lib_ref', 'enum', 'value1'),
    ],
)
async def test_ref_path(
        taxi_userver_sample, mockserver, url, response_var_name, path_param,
):
    expected_body = {response_var_name: path_param}
    await do_test(
        taxi_userver_sample,
        mockserver,
        request_url=f'{url}/{path_param}',
        request_headers={},
        request_params={},
        expected_body=expected_body,
        expected_headers={},
        path_name=response_var_name,
    )


@pytest.mark.parametrize(
    'url, response_var_name, path_param',
    [
        ('path_string_enum', 'enum', 'wrong_enum'),
        ('lib_ref', 'enum', 'wrong_enum'),
    ],
)
async def test_ref_path_wrong_enum_type(
        taxi_userver_sample, mockserver, url, response_var_name, path_param,
):
    expected_body = {'code': '400', 'message': 'Failed to parse request'}
    await do_test(
        taxi_userver_sample,
        mockserver,
        request_url=f'{url}/{path_param}',
        request_headers={},
        request_params={},
        expected_body=expected_body,
        expected_headers={},
        expected_code=400,
        mock_times_called=0,
    )
