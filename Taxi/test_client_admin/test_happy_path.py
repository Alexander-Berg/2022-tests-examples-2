async def test_admin(library_context, patch_aiohttp_session, response_mock):
    promocode_data = {'code': '1982'}
    url = (
        'https://tariff-editor-unstable.taxi.tst.yandex-team.ru/api-u/'
        'support_promocodes/generate/'
    )

    @patch_aiohttp_session(url)
    def test(method, url, params, json, headers):
        return response_mock(json=promocode_data)

    phone_type = 'yandex'
    series_id = '122112'
    phone = '1121212'
    ticket = '111'
    ticket_type = 'chatterbox'

    result = await library_context.client_admin.generate_promocode(
        phone_type, series_id, phone, ticket, token='aa',
    )

    assert result == promocode_data
    calls = test.calls
    assert len(calls) == 1
    assert calls[0]['headers'].pop('X-YaRequestId')
    assert calls == [
        {
            'method': 'post',
            'url': url,
            'params': None,
            'headers': {'X-YaTaxi-API-Key': 'aa'},
            'json': {
                'phone_type': 'yandex',
                'phone': phone,
                'series_id': series_id,
                'zendesk_ticket': ticket,
                'ticket_type': ticket_type,
            },
        },
    ]


async def test_gen_promocode_with_cookie(
        library_context, patch_aiohttp_session, response_mock,
):
    promocode_data = {'code': '1982'}
    url = (
        'https://tariff-editor-unstable.taxi.tst.yandex-team.ru/api-u/'
        'support_promocodes/generate/'
    )

    @patch_aiohttp_session(url)
    def test(method, url, params, json, headers):
        if url.endswith('/me'):
            return response_mock(json={'csrf_token': 'csrf_token'})
        return response_mock(json=promocode_data)

    phone_type = 'yandex'
    series_id = '122112'
    phone = '1121212'
    ticket = '111'

    result = await library_context.client_admin.generate_promocode(
        phone_type,
        series_id,
        phone,
        ticket,
        cookies={'some': 'cookies'},
        real_ip='127.0.0.1',
    )

    assert result == promocode_data
    calls = test.calls
    assert len(calls) == 2
    assert calls[0]['headers'].pop('X-YaRequestId')
    assert calls[1]['headers'].pop('X-YaRequestId')
    assert calls == [
        {
            'method': 'get',
            'url': (
                'https://tariff-editor-unstable.taxi.tst.yandex-team.ru/'
                'api-u/me'
            ),
            'params': None,
            'json': None,
            'headers': {'Cookie': 'some=cookies', 'X-Real-Ip': '127.0.0.1'},
        },
        {
            'method': 'post',
            'url': (
                'https://tariff-editor-unstable.taxi.tst.yandex-team.ru/'
                'api-u/support_promocodes/generate/'
            ),
            'params': None,
            'json': {
                'phone_type': 'yandex',
                'phone': '1121212',
                'series_id': '122112',
                'zendesk_ticket': '111',
                'ticket_type': 'chatterbox',
            },
            'headers': {
                'Cookie': 'some=cookies',
                'X-Csrf-Token': 'csrf_token',
                'X-Real-Ip': '127.0.0.1',
            },
        },
    ]


async def test_activity_amnesty(
        library_context, patch_aiohttp_session, response_mock,
):
    data = {
        'udid': 'unique_driver_id',
        'mode': 'additive',
        'value': 'value',
        'idempotency_token': 'token',
    }
    url = (
        'https://tariff-editor-unstable.taxi.tst.yandex-team.ru/api-u/'
        'admin/driver-metrics/v1/service/activity_value/'
    )

    @patch_aiohttp_session(url)
    def test(method, url, params, json, headers):
        if url.endswith('/me'):
            return response_mock(json={'csrf_token': 'csrf_token'})
        return response_mock(json=data)

    result = await library_context.client_admin.activity_amnesty(
        data=data, cookies={'some': 'cookies'},
    )

    assert result == data
    calls = test.calls
    assert len(calls) == 2
    assert calls[0]['headers'].pop('X-YaRequestId')
    assert calls[1]['headers'].pop('X-YaRequestId')
    assert calls == [
        {
            'method': 'get',
            'url': (
                'https://tariff-editor-unstable.taxi.tst.yandex-team.ru/'
                'api-u/me'
            ),
            'params': None,
            'json': None,
            'headers': {'Cookie': 'some=cookies'},
        },
        {
            'method': 'post',
            'url': (
                'https://tariff-editor-unstable.taxi.tst.yandex-team.ru/'
                'api-u/admin/driver-metrics/v1/service/activity_value/'
            ),
            'params': None,
            'json': {
                'udid': 'unique_driver_id',
                'mode': 'additive',
                'value': 'value',
                'idempotency_token': 'token',
            },
            'headers': {
                'Cookie': 'some=cookies',
                'X-Csrf-Token': 'csrf_token',
            },
        },
    ]
