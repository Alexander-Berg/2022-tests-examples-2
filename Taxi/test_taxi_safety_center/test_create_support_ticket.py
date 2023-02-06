from taxi_safety_center.stq import create_support_ticket


async def test_task(stq3_context, monkeypatch, mock):
    kwargs = {
        'phone': '+71234567890',
        'locale': 'ru',
        'idempotency_key': 'key',
        'source': 'source',
        'log_extra': {'log': 'extra'},
    }

    json_called = False

    @mock
    async def _request_mock(*args, **kwargs):
        class ResponseStub:
            async def json(self):
                nonlocal json_called
                json_called = True
                return self

        return ResponseStub()

    monkeypatch.setattr(stq3_context.client_http, 'request', _request_mock)
    await create_support_ticket.task(stq3_context, **kwargs)
    keys = stq3_context.secdist['settings_override']
    base_url = stq3_context.config.SAFETY_CENTER_TAXI_PROTOCOL_PY3_URL
    req_json = kwargs.copy()
    req_json.pop('log_extra')
    api_key_header = create_support_ticket.YATAXI_API_KEY_HEADER
    call_kwargs = {
        'method': 'POST',
        'url': base_url + '/1.0/urgenthelp',
        'json': req_json,
        'headers': {
            api_key_header: keys['ZENDESK_URGENT_HELP_BACKEND_APIKEY'],
        },
    }

    assert _request_mock.calls == [{'args': (), 'kwargs': call_kwargs}]
    assert json_called
