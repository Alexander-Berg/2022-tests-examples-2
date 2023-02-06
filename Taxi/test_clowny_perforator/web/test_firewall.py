import copy


REQUEST_BODY = {
    'from': {'firewall-macro': '_HWTAXINET_'},
    'to': {'l7-balancer-hostname': 'service.taxi.yandex.net'},
    'port': 80,
}


async def test_rules_get_ok(
        web_app_client, mockserver, puncher_mockserver, puncher_context,
):
    puncher_mockserver()
    puncher_context.set_data(
        {
            'rules': {
                '_HWTAXINET_': {'count': 1, 'rules': [1], 'status': 'success'},
            },
        },
    )

    response = await web_app_client.post(
        '/v1/firewall/check', json=REQUEST_BODY,
    )
    content = await response.json()
    response.raise_for_status()
    assert response.status == 200
    assert content == {'rule-exists': True}


async def test_rules_get_absent(
        web_app_client, mockserver, puncher_mockserver,
):
    puncher_mockserver()

    response = await web_app_client.post(
        '/v1/firewall/check', json=REQUEST_BODY,
    )
    content = await response.json()
    response.raise_for_status()
    assert response.status == 200
    assert content == {'rule-exists': False}


async def test_rules_invalid_request(web_app_client):
    data = copy.deepcopy(REQUEST_BODY)
    data['to'] = data['from']

    response = await web_app_client.post('/v1/firewall/check', json=data)
    content = await response.json()
    assert response.status == 400
    assert content == {
        'code': 'INVALID_INPUT',
        'message': (
            '"only "firewall-macro" is allowed for "from"'
            ' and only "l7-balancer-hostname" is allowed for "to"'
        ),
    }
