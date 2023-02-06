async def test_parameters(taxi_test_service, mockserver):
    valid_response = {
        '1stInvalidParameter': 'foo',
        '2ndInvalidParameter': 'bar',
    }

    @mockserver.json_handler('/test-service/invalid-names/parameters')
    def _handler(_req):
        _resp = {
            '1stInvalidParameter': _req.query['1stInvalidParameter'],
            '2ndInvalidParameter': _req.query['2ndInvalidParameter'],
        }

        assert _resp == valid_response
        return _resp

    response = await taxi_test_service.get(
        'invalid-names/parameters',
        params={'1stInvalidParameter': 'foo', '2ndInvalidParameter': 'bar'},
    )

    assert _handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == valid_response


async def test_parameters_defs(taxi_test_service, mockserver):
    valid_response = {'1stInvalidParameter': 'foo'}

    @mockserver.json_handler('/test-service/invalid-names/parameters-defs')
    def _handler(_req):
        _resp = {'1stInvalidParameter': _req.query['1stInvalidParameter']}

        assert _resp == valid_response
        return _resp

    response = await taxi_test_service.get(
        'invalid-names/parameters-defs', params={'1stInvalidParameter': 'foo'},
    )

    assert _handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == valid_response


async def test_responses(taxi_test_service, mockserver):
    data = {'1stInvalidProperty': {'value': 'foobar'}}

    @mockserver.json_handler('/test-service/invalid-names/responses')
    def _handler(_):
        return data

    response = await taxi_test_service.get('invalid-names/responses')

    assert _handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == data


async def test_responses_defs(taxi_test_service, mockserver):
    data = {'1stInvalidProperty': {'value': 'foobar'}}

    @mockserver.json_handler('/test-service/invalid-names/responses-defs')
    def _handler(_):
        return data

    response = await taxi_test_service.get('invalid-names/responses-defs')

    assert _handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == data


async def test_schemas(taxi_test_service, mockserver):
    valid_response = {'1stInvalidProperty': {'value': 'foobar'}}

    @mockserver.json_handler('/test-service/invalid-names/schemas')
    def _handler(_req):
        _resp = _req.json

        assert _resp == valid_response
        return _resp

    response = await taxi_test_service.post(
        'invalid-names/schemas',
        json={'1stInvalidProperty': {'value': 'foobar'}},
    )

    assert _handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == valid_response


async def test_schemas_defs(taxi_test_service, mockserver):
    valid_response = {'1stInvalidProperty': {'value': 'foobar'}}

    @mockserver.json_handler('/test-service/invalid-names/schemas-defs')
    def _handler(_req):
        _resp = _req.json

        assert _resp == valid_response
        return _resp

    response = await taxi_test_service.post(
        'invalid-names/schemas-defs',
        json={'1stInvalidProperty': {'value': 'foobar'}},
    )

    assert _handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == valid_response
