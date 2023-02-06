USER_DEFAULT_PRICE = '300'


async def test_check_price(v1_calc_creator):
    v1_calc_creator.url = '/v1/taxi/check-price'
    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    resp = response.json()

    assert resp['price'] == USER_DEFAULT_PRICE

    prepare_req = v1_calc_creator.mock_prepare.request
    assert prepare_req == {
        'categories': ['cargocorp'],
        'classes_requirements': {
            'cargocorp': {
                'door_to_door': True,
                'cargo_type': 0,
                'cargo_type_int': 1,
            },
        },
        'tolls': 'DENY',
        'user_info': {
            'application': {
                'name': 'cargo',
                'platform_version': '0.0.0',
                'version': '0.0.0',
            },
            'payment_info': {'method_id': 'corp-xxx', 'type': 'corp'},
            'user_id': 'user_id',
        },
        'waypoints': [[37.6489887, 55.5737046], [37.5447415, 55.9061769]],
        'zone': 'moscow',
        'modifications_scope': 'cargo',
        'extra': {
            'providers': {
                'discounts': {'is_enabled': False},
                'router': {'is_fallback': True},
            },
        },
    }

    recalc_req = v1_calc_creator.mock_recalc.request
    recalc_trip_details = recalc_req['user']['trip_details']
    assert recalc_req['driver']['trip_details'] == recalc_trip_details
    details = resp['details']

    assert round(recalc_trip_details['total_distance']) == round(
        float(details['total_distance']),
    )
    assert round(recalc_trip_details['total_time']) == round(
        float(details['total_time']),
    )

    assert resp['units']


async def test_calc_cant_construct_error(v1_calc_creator, mock_route):
    v1_calc_creator.url = '/v1/taxi/check-price'
    mock_route.empty_route = True
    response = await v1_calc_creator.execute()
    assert response.status_code == 400
    resp = response.json()
    assert resp == {
        'code': 'cant_construct_route',
        'message': 'Requested route is insoluble',
    }


async def test_calc_tariff_not_found(mockserver, v1_calc_creator):
    v1_calc_creator.mock_prepare.error_response = mockserver.make_response(
        json={
            'code': 'UNABLE_TO_MATCH_TARIFF',
            'message': 'Unable to match tariff for zone moscow',
        },
        status=400,
    )
    v1_calc_creator.url = '/v1/taxi/check-price'
    response = await v1_calc_creator.execute()
    assert response.status_code == 400
    resp = response.json()
    assert resp == {
        'code': 'tariff_not_found',
        'message': 'Requested tariff not found',
    }
