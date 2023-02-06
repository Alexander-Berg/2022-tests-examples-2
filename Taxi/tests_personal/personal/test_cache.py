import pytest


@pytest.mark.parametrize(
    (
        'first_method,first_data,first_hit,first_put,'
        'second_method,second_data,second_hit,second_put'
    ),
    [
        (
            'phones/store',
            {'phone': '+73333333333'},
            0,
            1,
            'phones/store',
            {'phone': '+73333333333'},
            1,
            0,
        ),
        (
            'phones/store',
            {'phone': '+73333333333'},
            0,
            1,
            'phones/find',
            {'phone': '+73333333333'},
            1,
            0,
        ),
        (
            'phones/store',
            {'phone': '+71111111111'},
            0,
            1,
            'phones/retrieve',
            {'id': '8657329a87d7456380afb287874f022c'},
            1,
            0,
        ),
        (
            'phones/retrieve',
            {'id': '8657329a87d7456380afb287874f022c'},
            0,
            1,
            'phones/store',
            {'phone': '+71111111111'},
            1,
            0,
        ),
        (
            'phones/retrieve',
            {'id': '8657329a87d7456380afb287874f022c'},
            0,
            1,
            'phones/find',
            {'phone': '+71111111111'},
            1,
            0,
        ),
        (
            'phones/bulk_store',
            {
                'items': [
                    {'phone': '+71111111111'},
                    {'phone': '+72222222222'},
                    {'phone': '+73333333333'},
                    {'phone': '+71111111111'},
                ],
            },
            0,
            4,
            'phones/bulk_store',
            {
                'items': [
                    {'phone': '+75555555555'},
                    {'phone': '+71111111111'},
                    {'phone': '+72222222222'},
                    {'phone': '+74444444444'},
                    {'phone': '+71111111111'},
                    {'phone': '+74444444444'},
                ],
            },
            3,
            3,
        ),
        (
            'phones/bulk_store',
            {
                'items': [
                    {'phone': '+71111111111'},
                    {'phone': '+72222222222'},
                    {'phone': '+73333333333'},
                    {'phone': '+71111111111'},
                ],
            },
            0,
            4,
            'phones/bulk_retrieve',
            {
                'items': [
                    {'id': '8657329a87d7456380afb287874f022c'},
                    {'id': '97ac523d491745d1afae88bea477cc36'},
                    {'id': '7c606cadc49c4cd79b0782aeff0e7318'},
                    {'id': '8657329a87d7456380afb287874f022c'},
                    {'id': '12345678901234567890123456789012'},
                ],
            },
            3,
            1,
        ),
    ],
)
@pytest.mark.config(PERSONAL_MONGO_CACHE_ENABLED=True)
async def test_cache_methods(
        taxi_personal,
        mongodb,
        testpoint,
        first_method,
        first_data,
        first_hit,
        first_put,
        second_method,
        second_data,
        second_hit,
        second_put,
):
    @testpoint('personal-cache-hit')
    def _mock_cache_hit(request):
        return {}

    @testpoint('personal-cache-put')
    def _mock_cache_put(request):
        return {}

    first_response = await taxi_personal.post(
        first_method,
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json=first_data,
    )
    assert first_response.status_code == 200
    assert _mock_cache_hit.times_called == first_hit
    assert _mock_cache_put.times_called == first_put
    _mock_cache_hit.flush()
    _mock_cache_put.flush()

    second_response = await taxi_personal.post(
        second_method,
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json=second_data,
    )
    assert second_response.status_code == 200
    assert _mock_cache_hit.times_called == second_hit
    assert _mock_cache_put.times_called == second_put


@pytest.mark.parametrize(
    'request_method,request_data,response_data',
    [
        (
            'phones/store',
            {'phone': '+71111111111'},
            {
                'id': '8657329a87d7456380afb287874f022c',
                'phone': '+71111111111',
            },
        ),
        (
            'phones/retrieve',
            {'id': '8657329a87d7456380afb287874f022c'},
            {
                'id': '8657329a87d7456380afb287874f022c',
                'phone': '+71111111111',
            },
        ),
        (
            'phones/find',
            {'phone': '+71111111111'},
            {
                'id': '8657329a87d7456380afb287874f022c',
                'phone': '+71111111111',
            },
        ),
        (
            'phones/bulk_store',
            {'items': [{'phone': '+71111111111'}]},
            {
                'items': [
                    {
                        'id': '8657329a87d7456380afb287874f022c',
                        'phone': '+71111111111',
                    },
                ],
            },
        ),
        (
            'phones/bulk_retrieve',
            {'items': [{'id': '8657329a87d7456380afb287874f022c'}]},
            {
                'items': [
                    {
                        'id': '8657329a87d7456380afb287874f022c',
                        'phone': '+71111111111',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.config(PERSONAL_MONGO_CACHE_ENABLED=True)
async def test_cache_mongo_unused(
        taxi_personal, mongodb, request_method, request_data, response_data,
):
    async def _test_request():
        response = await taxi_personal.post(
            request_method,
            headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
            params={'source': 'testsuite'},
            json=request_data,
        )
        assert response.status_code == 200
        assert response.json() == response_data

    # first request to load data from mongo
    await _test_request()

    # change mongo data
    mongodb.personal_phones.find_and_modify(
        {'_id': '8657329a87d7456380afb287874f022c'},
        {'$set': {'value': 'should_not_be_used'}},
    )

    # second request to check data got from cache
    await _test_request()


@pytest.mark.parametrize(
    (
        'first_method,first_data,first_hit,first_put,'
        'second_method,second_data,second_hit,second_put'
    ),
    [
        (
            'v1/phones/store',
            {'value': '+73333333333'},
            0,
            1,
            'v1/phones/store',
            {'value': '+73333333333'},
            1,
            0,
        ),
        (
            'v1/phones/store',
            {'value': '+73333333333'},
            0,
            1,
            'v1/phones/find',
            {'value': '+73333333333'},
            1,
            0,
        ),
        (
            'v1/phones/store',
            {'value': '+71111111111'},
            0,
            1,
            'v1/phones/retrieve',
            {'id': '8657329a87d7456380afb287874f022c'},
            1,
            0,
        ),
        (
            'v1/phones/retrieve',
            {'id': '8657329a87d7456380afb287874f022c'},
            0,
            1,
            'v1/phones/store',
            {'value': '+71111111111'},
            1,
            0,
        ),
        (
            'v1/phones/retrieve',
            {'id': '8657329a87d7456380afb287874f022c'},
            0,
            1,
            'v1/phones/find',
            {'value': '+71111111111'},
            1,
            0,
        ),
        (
            'v1/phones/bulk_store',
            {
                'items': [
                    {'value': '+71111111111'},
                    {'value': '+72222222222'},
                    {'value': '+73333333333'},
                    {'value': '+71111111111'},
                ],
            },
            0,
            4,
            'v1/phones/bulk_store',
            {
                'items': [
                    {'value': '+75555555555'},
                    {'value': '+71111111111'},
                    {'value': '+72222222222'},
                    {'value': '+74444444444'},
                    {'value': '+71111111111'},
                    {'value': '+74444444444'},
                ],
            },
            3,
            3,
        ),
        (
            'v1/phones/bulk_store',
            {
                'items': [
                    {'value': '+71111111111'},
                    {'value': '+72222222222'},
                    {'value': '+73333333333'},
                    {'value': '+71111111111'},
                ],
            },
            0,
            4,
            'v1/phones/bulk_retrieve',
            {
                'items': [
                    {'id': '8657329a87d7456380afb287874f022c'},
                    {'id': '97ac523d491745d1afae88bea477cc36'},
                    {'id': '7c606cadc49c4cd79b0782aeff0e7318'},
                    {'id': '8657329a87d7456380afb287874f022c'},
                    {'id': '12345678901234567890123456789012'},
                ],
            },
            3,
            1,
        ),
    ],
)
@pytest.mark.config(PERSONAL_MONGO_CACHE_ENABLED=True)
async def test_cache_v1_methods(
        taxi_personal,
        mongodb,
        testpoint,
        first_method,
        first_data,
        first_hit,
        first_put,
        second_method,
        second_data,
        second_hit,
        second_put,
):
    @testpoint('personal-cache-hit')
    def _mock_cache_hit(request):
        return {}

    @testpoint('personal-cache-put')
    def _mock_cache_put(request):
        return {}

    first_response = await taxi_personal.post(first_method, json=first_data)
    assert first_response.status_code == 200
    assert _mock_cache_hit.times_called == first_hit
    assert _mock_cache_put.times_called == first_put
    _mock_cache_hit.flush()
    _mock_cache_put.flush()

    second_response = await taxi_personal.post(second_method, json=second_data)
    assert second_response.status_code == 200
    assert _mock_cache_hit.times_called == second_hit
    assert _mock_cache_put.times_called == second_put
