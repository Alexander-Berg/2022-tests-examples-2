import json

import pytest

TICKET = 'ticket'
TVM_TICKETS = {'50': {'ticket': TICKET}}


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'driver_protocol', 'dst': 'experiments3-proxy'}],
    EXPERIMENTS3_PROXY_UPSTREAM_TVM_NAME='taxi_exp',
    EXPERIMENTS3_PROXY_CHECK_CONSUMER=True,
)
@pytest.mark.experiments3(
    name='test1',
    consumers=['launch', 'client_protocol/launch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'foo': 9875},
)
def test_tvm(taxi_experiments3_proxy, mockserver, load, load_json):
    @mockserver.json_handler('/experiments3-upstream/v1/experiments/updates/')
    def upstream(request):
        return load_json('experiments_without_consumers.json')

    taxi_experiments3_proxy.invalidate_caches()
    upstream.wait_call()

    tvm_header = {'X-Ya-Service-Ticket': load('tvm2_ticket_19_32')}
    response = taxi_experiments3_proxy.get(
        '/v1/experiments/updates?consumer=unknown', headers=tvm_header,
    )
    assert response.status_code == 404


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[
        {'src': 'driver_protocol', 'dst': 'experiments3-proxy'},
        {'src': 'experiments3-proxy', 'dst': 'taxi_exp'},
    ],
    EXPERIMENTS3_PROXY_UPSTREAM_TVM_NAME='taxi_exp',
    EXPERIMENTS3_PROXY_CHECK_CONSUMER=True,
)
@pytest.mark.experiments3(
    name='test1',
    consumers=['launch', 'client_protocol/launch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'foo': 9875},
)
def test_tvm_client(tvm2_client, taxi_experiments3_proxy, mockserver, load):
    tvm2_client.set_ticket(json.dumps(TVM_TICKETS))

    @mockserver.json_handler('/experiments3-upstream/v1/experiments/updates/')
    def upstream(request):
        assert 'X-Ya-Service-Ticket' in request.headers
        assert request.headers['X-Ya-Service-Ticket'] == 'ticket'
        return {'experiments': []}

    tvm_header = {'X-Ya-Service-Ticket': load('tvm2_ticket_19_32')}
    response = taxi_experiments3_proxy.get(
        '/v1/experiments/updates?consumer=unknown', headers=tvm_header,
    )
    assert response.status_code == 404
