import pytest

TICKET_HEADER = 'X-Ya-Service-Ticket'
SOURCE_SERVICE_NAME = 'X-YaBank-TVM-Source-Service-Name'

CONFIG = [
    {
        'input': {'http-path-prefix': '/'},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'bank-h2h'},
        'proxy': {'server-hosts': ['*']},
    },
    {
        'input': {'http-path-prefix': '/unauth'},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'bank-h2h'},
        'proxy': {'proxy-401': True, 'server-hosts': ['*']},
    },
]
TVM_SERVICES = {
    'bank-h2h-authproxy': 1,
    'bank-h2h': 2,
    'mock': 3,
    'statistics': 4,
    'authproxy-manager': 5,
    'eda_core': 6,
    'eats-eaters': 7,
    'other': 100,
}
TVM_RULES = [
    {'src': 'bank-h2h-authproxy', 'dst': 'bank-h2h'},
    {'src': 'mock', 'dst': 'bank-h2h-authproxy'},
]

# ya tool tvmknife unittest service --src 3 --dst 1
TICKET = (
    '3:serv:CBAQ__________9_IgQIAxAB:Ho-_GzvYsBmuH2phTItfnwOa4rv7728wK47GGbh9'
    'eX1RHm1PUyxm-THYM5LbsH_6GMA8Sf8aXfTH2etcX5BKr5B0NlD6xYdClkgYcOswOcW3VdrV'
    'ShHrk3rcjEZt6PltQKc0uy_703VkUE-J6u2sJAvonN8Lvx2qrPtKTTupDA0'
)
# ya tool tvmknife unittest service --src 100 --dst 1
OTHER_TICKET = (
    '3:serv:CBAQ__________9_IgQIZBAB:FxOBqaPm31kGwZsrQ_3s1Mc34YoF0j0ct1pFhf7w'
    'a3vk_TEfSL_7_RjDGrfEQq2YlnCcy4jEh9ecS-t-zj-olY54e4xwXYTefYyXSKezCKRbtGvc'
    'w-rZtPTSlGa6-8FbaWJaO8wKKNPczgdpH5V2yImMI-BEQ5gpYcxRpUwAOko'
)


@pytest.mark.config(
    BANK_H2H_AUTHPROXY_ROUTE_RULES=CONFIG,
    TVM_ENABLED=True,
    TVM_SERVICES=TVM_SERVICES,
    TVM_RULES=TVM_RULES,
)
@pytest.mark.tvm2_ticket({2: 'MOCK_TICKET'})
async def test_request_ok(taxi_bank_h2h_authproxy, mock_remote):
    backend = mock_remote('/abc')
    response = await taxi_bank_h2h_authproxy.get(
        '/abc', headers={TICKET_HEADER: TICKET},
    )
    assert backend.has_calls
    assert response.status_code == 200
    headers = backend.next_call()['request'].headers
    assert headers[SOURCE_SERVICE_NAME] == 'mock'


@pytest.mark.config(
    BANK_H2H_AUTHPROXY_ROUTE_RULES=CONFIG,
    TVM_ENABLED=True,
    TVM_SERVICES=TVM_SERVICES,
    TVM_RULES=TVM_RULES,
)
@pytest.mark.tvm2_ticket({2: 'MOCK_TICKET'})
async def test_request_ok_but_proxy401(taxi_bank_h2h_authproxy, mock_remote):
    backend = mock_remote('/unauth')
    response = await taxi_bank_h2h_authproxy.get(
        '/unauth', headers={TICKET_HEADER: TICKET},
    )
    assert backend.has_calls
    assert response.status_code == 200
    headers = backend.next_call()['request'].headers
    assert headers[SOURCE_SERVICE_NAME] == 'mock'


@pytest.mark.config(
    BANK_H2H_AUTHPROXY_ROUTE_RULES=CONFIG,
    TVM_ENABLED=True,
    TVM_SERVICES=TVM_SERVICES,
    TVM_RULES=TVM_RULES,
)
@pytest.mark.tvm2_ticket({2: 'MOCK_TICKET'})
async def test_request_deny_by_tvm(taxi_bank_h2h_authproxy, mock_remote):
    backend = mock_remote('/abc')
    response = await taxi_bank_h2h_authproxy.get(
        '/abc', headers={TICKET_HEADER: OTHER_TICKET},
    )
    assert not backend.has_calls
    assert response.status_code == 403


@pytest.mark.config(
    BANK_H2H_AUTHPROXY_ROUTE_RULES=CONFIG,
    TVM_ENABLED=True,
    TVM_SERVICES=TVM_SERVICES,
    TVM_RULES=TVM_RULES,
)
@pytest.mark.tvm2_ticket({2: 'MOCK_TICKET'})
async def test_request_deny_by_tvm_but_proxy401(
        taxi_bank_h2h_authproxy, mock_remote,
):
    backend = mock_remote('/unauth')
    response = await taxi_bank_h2h_authproxy.get(
        '/unauth', headers={TICKET_HEADER: OTHER_TICKET},
    )
    assert not backend.has_calls
    assert response.status_code == 403
