import aiohttp


async def test_passport_internal(library_context, mockserver):
    mocked_result = {'some': 'tome', 'status': 'ok'}
    requests_list = []

    @mockserver.json_handler(
        '/passport-internal/1/bundle/account/register/by_middleman/',
    )
    async def _mock(request):
        headers = request.headers
        requests_list.append(
            {
                'method': request.method,
                'params': dict(request.args),
                'headers': {
                    'Ya-Client-User-Agent': headers['Ya-Client-User-Agent'],
                    'Ya-Consumer-Client-Ip': headers['Ya-Consumer-Client-Ip'],
                },
                'data': request.form,
            },
        )
        return mocked_result

    result = await library_context.client_passport_internal.register(
        login='login', password='password',
    )

    assert result == mocked_result
    assert requests_list == [
        {
            'method': 'POST',
            'headers': {
                'Ya-Client-User-Agent': aiohttp.http.SERVER_SOFTWARE,
                'Ya-Consumer-Client-Ip': (
                    library_context.client_passport_internal.consumer_ip
                ),
            },
            'params': {'consumer': 'client-passport-internal-library'},
            'data': {
                'country': 'ru',
                'language': 'ru',
                'login': 'login',
                'password': 'password',
            },
        },
    ]
