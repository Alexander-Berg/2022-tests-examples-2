import pytest


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.tvm2_ticket({111: 'MYTICKET'})
async def test_external_echo(taxi_userver_sample, mockserver):
    # pylint: disable=W0612
    @mockserver.json_handler('/tvm2-echo')
    def tvm2_echo(request):
        assert request.headers['X-Ya-Service-Ticket'] == 'MYTICKET'
        return {key: request.args.getone(key) for key in request.args}

    params = {'hello': 'world'}
    response = await taxi_userver_sample.get(
        'tvm2/external-echo', params=params, data='{}',
    )
    assert response.status_code == 200
    assert response.json() == {'response': params}


@pytest.mark.config(
    TVM_ENABLED=True, TVM_SERVICES={'userver-sample': 2001716, 'test': 112},
)
@pytest.mark.tvm2_ticket({112: 'TESTTICKET', 111: 'INVALID'})
async def test_tvm_services(taxi_userver_sample, mockserver):
    # pylint: disable=W0612
    @mockserver.json_handler('/tvm2-echo')
    def tvm2_echo(request):
        assert request.headers['X-Ya-Service-Ticket'] == 'TESTTICKET'
        return {key: request.args.getone(key) for key in request.args}

    params = {'hello': 'world', 'tvm-service-name': 'test'}
    response = await taxi_userver_sample.get(
        'tvm2/external-echo', params=params, data='{}',
    )
    assert response.status_code == 200
    assert response.json() == {'response': params}


@pytest.mark.parametrize(
    'source_tvm_service_name', [None, 'driver-authorizer'],
)
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_SERVICES={
        'userver-sample': 2001716,
        'driver-authorizer': 424242,
        'test': 112,
    },
)
@pytest.mark.tvm2_ticket_by_src(
    {2001716: {112: 'TEST_US_TICKET'}, 424242: {112: 'TEST_DA_TICKET'}},
)
async def test_tvm_services_additional_source(
        taxi_userver_sample, mockserver, source_tvm_service_name,
):
    # pylint: disable=W0612
    @mockserver.json_handler('/tvm2-echo')
    def tvm2_echo(request):
        if source_tvm_service_name is None:
            assert request.headers['X-Ya-Service-Ticket'] == 'TEST_US_TICKET'
        else:
            assert request.headers['X-Ya-Service-Ticket'] == 'TEST_DA_TICKET'
        return {key: request.args.getone(key) for key in request.args}

    params = {'hello': 'world', 'tvm-service-name': 'test'}
    if source_tvm_service_name is not None:
        params['source-tvm-service-name'] = source_tvm_service_name

    response = await taxi_userver_sample.get(
        'tvm2/external-echo', params=params, data='{}',
    )
    assert response.status_code == 200
    assert response.json() == {'response': params}
