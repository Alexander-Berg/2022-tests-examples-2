import pytest

AM_ROUTING_RULE = {
    'input': {
        'description': '(imported from taxi config)',
        'maintained_by': 'common_components',
        'prefix': '/4.0/',
        'priority': 100,
        'rule_name': '/4.0/',
    },
    'output': {
        'attempts': 1,
        'timeout_ms': 1000,
        'tvm_service': 'passport',
        'upstream': {'$mockserver': ''},
    },
    'proxy': {
        'auth_type': 'oauth-or-session',
        'personal': {
            'eater_id': True,
            'eater_uuid': True,
            'staff_login': False,
            'eats_email_id': False,
            'eats_phone_id': False,
        },
        'proxy_401': True,
    },
    'rule_type': 'passenger-authorizer',
}


TVM_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIlAMQZg:J8WYsLN9xPlsyTQ6vD8QtEVFsZ5y2'
    '--uZ09O1o6mUdFU_UfBeplkpHL6ZRtvPwV1-YarhTLggCZxTe0QqB1E2ALSsgqS'
    'ZA-76NYYhg0zmhlb0Tg5RGhWBPAaNZcWLRZ7h9s06YL9DPR27JYcJj0HVGLDtZE'
    'JRJeYfuExI78uwr8'
)


@pytest.mark.parametrize(
    'headers,ip_addr',
    [
        ({'X-Real-IP': '1.1.1.1'}, '1.1.1.1'),
        ({'X-Real-IP': '1.1.1.1', 'X-Remote-IP': '2.2.2.2'}, '1.1.1.1'),
        (
            {
                'X-Real-IP': '1.1.1.1',
                'X-Remote-IP': '2.2.2.2',
                'X-Ya-Service-Ticket': TVM_SERVICE_TICKET,
            },
            '2.2.2.2',
        ),
        (
            {
                'X-Real-IP': '1.1.1.1',
                'X-Remote-IP': '2.2.2.2',
                'X-Forwarded-For-Y': '3.3.3.3',
                'X-Ya-Service-Ticket': TVM_SERVICE_TICKET,
            },
            '3.3.3.3',
        ),
        (
            {
                'X-Real-IP': '1.1.1.1',
                'X-Forwarded-For-Y': '3.3.3.3',
                'X-Ya-Service-Ticket': TVM_SERVICE_TICKET,
            },
            '3.3.3.3',
        ),
    ],
)
@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(
    TVM_ENABLED=True, TVM_RULES=[{'dst': 'ya-authproxy', 'src': 'mock'}],
)
@pytest.mark.routing_rules([AM_ROUTING_RULE])
async def test_client_ip(
        taxi_ya_authproxy, blackbox_service, mockserver, headers, ip_addr,
):
    @mockserver.json_handler('/4.0/test')
    def _test(request):
        assert request.headers['x-remote-ip'] == ip_addr
        assert request.headers['x-forwarded-for-y'] == ip_addr
        return 'xxx'

    response = await taxi_ya_authproxy.post(
        path='4.0/test', data='{}', headers=headers,
    )
    assert response.status_code == 200
    assert _test.has_calls
