import aiohttp.web


async def test_success(web_app_client, headers, mockserver):
    @mockserver.json_handler('cargo-misc/couriers/v1/create')
    async def _courier_create(request):
        assert request.json['courier_id'] is not None
        del request.json['courier_id']
        assert request.json == {
            'operation_id': 'a1-b2-c3-d4',
            'park_id': '7ad36bc7560449998acbe2c57a75c293',
            'first_name': 'Пупкин',
            'last_name': 'Вася',
            'phone': '+79600000000',
            'work_rule_id': 'e3199204cc514377a65a2804a5fc18f2',
            'birth_date': '1980-02-29',
            'courier_type': 'walking_courier',
            'balance_limit': '5',
        }
        return aiohttp.web.json_response(
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c293',
                'driver_id': '111',
                'car_id': '222',
            },
            status=200,
        )

    response = await web_app_client.post(
        '/api/v1/couriers/create',
        headers={**headers, 'X-Idempotency-Token': 'a1-b2-c3-d4'},
        json={
            'first_name': 'Пупкин',
            'last_name': 'Вася',
            'phone': '+79600000000',
            'work_rule_id': 'e3199204cc514377a65a2804a5fc18f2',
            'birth_date': '1980-02-29',
        },
    )

    assert response.status == 200


async def test_bad_request(web_app_client, headers, mockserver):
    @mockserver.json_handler('cargo-misc/couriers/v1/create')
    async def _courier_create(request):
        assert request.json['courier_id'] is not None
        del request.json['courier_id']
        assert request.json == {
            'operation_id': 'a1-b2-c3-d4',
            'park_id': '7ad36bc7560449998acbe2c57a75c293',
            'first_name': 'Пупкин',
            'last_name': 'Вася',
            'phone': '+29600000000',
            'work_rule_id': 'e3199204cc514377a65a2804a5fc18f2',
            'birth_date': '1980-02-29',
            'courier_type': 'walking_courier',
            'balance_limit': '5',
        }
        return aiohttp.web.json_response(
            {'code': 'invalid_phone', 'message': 'courier phone is incorrect'},
            status=400,
        )

    response = await web_app_client.post(
        '/api/v1/couriers/create',
        headers={**headers, 'X-Idempotency-Token': 'a1-b2-c3-d4'},
        json={
            'first_name': 'Пупкин',
            'last_name': 'Вася',
            'phone': '+29600000000',
            'work_rule_id': 'e3199204cc514377a65a2804a5fc18f2',
            'birth_date': '1980-02-29',
        },
    )

    assert response.status == 400
    data = await response.json()
    assert data['code'] == 'invalid_phone'


async def test_success_instant_payouts(web_app_client, headers, mockserver):
    @mockserver.json_handler('cargo-misc/couriers/v1/create')
    async def _courier_create(request):
        assert request.json['courier_id'] is not None
        del request.json['courier_id']
        assert request.json == {
            'operation_id': 'a1-b2-c3-d4',
            'park_id': '7ad36bc7560449998acbe2c57a75c293',
            'first_name': 'Пупкин',
            'last_name': 'Вася',
            'phone': '+79600000000',
            'work_rule_id': 'e3199204cc514377a65a2804a5fc18f2',
            'birth_date': '1980-02-29',
            'courier_type': 'walking_courier',
            'balance_limit': '5',
        }
        return aiohttp.web.json_response(
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c293',
                'driver_id': '111',
                'car_id': '222',
            },
            status=200,
        )

    @mockserver.json_handler(
        'contractor-instant-payouts/v1/contractors/rules/by-id',
    )
    async def _v1_contractors_rules_by_id(request):
        assert request.query['park_id'] == '7ad36bc7560449998acbe2c57a75c293'
        assert request.json == {'rule_id': '00000000000100010001000000000000'}
        return aiohttp.web.json_response({}, status=204)

    response = await web_app_client.post(
        '/api/v1/couriers/create',
        headers={**headers, 'X-Idempotency-Token': 'a1-b2-c3-d4'},
        json={
            'first_name': 'Пупкин',
            'last_name': 'Вася',
            'phone': '+79600000000',
            'work_rule_id': 'e3199204cc514377a65a2804a5fc18f2',
            'birth_date': '1980-02-29',
            'instant_payouts': {'rule_id': '00000000000100010001000000000000'},
        },
    )

    assert response.status == 200


async def test_failed_instant_payouts(web_app_client, headers, mockserver):
    @mockserver.json_handler(
        'contractor-instant-payouts/v1/contractors/rules/by-id',
    )
    async def _v1_contractors_rules_by_id(request):
        assert request.query['park_id'] == '7ad36bc7560449998acbe2c57a75c293'
        assert request.json == {'rule_id': '00000000000100010001000000000000'}
        return aiohttp.web.json_response(
            {'code': 'invalid_rule_id', 'message': 'rule not found'},
            status=400,
        )

    response = await web_app_client.post(
        '/api/v1/couriers/create',
        headers={**headers, 'X-Idempotency-Token': 'a1-b2-c3-d4'},
        json={
            'first_name': 'Пупкин',
            'last_name': 'Вася',
            'phone': '+79600000000',
            'work_rule_id': 'e3199204cc514377a65a2804a5fc18f2',
            'birth_date': '1980-02-29',
            'instant_payouts': {'rule_id': '00000000000100010001000000000000'},
        },
    )

    assert response.status == 400
