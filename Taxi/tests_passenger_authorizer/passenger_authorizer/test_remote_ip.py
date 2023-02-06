import json

import pytest

import utils


# Generated with:
# ya tool tvmknife unittest service --src 404 --dst 101
TVM_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIlAMQZQ:Dp-l02wKq6RMvh5VMkux17_8ES7EUAsAEvp'
    '88BYHzwCYOL6cNKKGHA21BhE5J-ePB6KdNNHpbYE2KqIDY7kssiJ2TDMQ79qlQX8qwLDl'
    'VR0QGRMuwt6C2DVhY2V9CbDaamvHTjRozKJMAJd1kX_UFCegkRYdlC-1FN18CozWrJQ'
)

AM_ROUTE_RULES = [
    utils.make_rule(
        {
            'input': {
                'prefix': '/smth',
                'priority': 300,
                'rule_name': '/smth',
            },
            'output': {'tvm_service': 'passport'},
            'proxy': {'proxy_401': True},
        },
    ),
]


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'passenger-authorizer'}],
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
@pytest.mark.parametrize(
    'ticket,use,okk',
    [
        (None, False, True),
        ('invalid', False, False),
        (TVM_SERVICE_TICKET, True, True),
    ],
)
async def test_remote_ip_tvm(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        ticket,
        use,
        okk,
):
    stats = {'call-test': 0}

    @mockserver.json_handler('/blackbox')
    def _mock_blackbox(request):
        userip = request.args.get('userip')
        if use:
            assert userip == 'remote'
        else:
            assert userip == '1.2.3.4'
        return mockserver.make_response(
            json.dumps(
                {
                    'status': {'value': 'INVALID', 'id': 5},
                    'error': 'expired_token',
                },
            ),
            status=200,
        )

    @mockserver.json_handler('/smth')
    def _test(request):
        stats['call-test'] += 1
        assert 'X-Real-IP' not in request.headers
        if use:
            assert request.headers['X-Remote-Ip'] == 'remote'
        else:
            assert request.headers['X-Remote-Ip'] == '1.2.3.4'
        return {'id': '123'}

    headers = {
        'X-Real-IP': '1.2.3.4',
        'X-Remote-Ip': 'remote',
        'X-YaTaxi-UserId': '12345',
    }
    if ticket:
        headers['X-Ya-Service-Ticket'] = ticket
    response = await taxi_passenger_authorizer.post(
        'smth', bearer='test_token', headers=headers,
    )

    if okk:
        assert response.status == 200
        assert stats['call-test'] == 1
    else:
        assert response.status == 401
        assert stats['call-test'] == 0
