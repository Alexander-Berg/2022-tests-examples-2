import pytest


CORP_TARIFF_ID = (
    '5dd417dc3ebca0a502e88efa'
    + '-ea19e833f1bd43f2825dd50d2cc80880'
    + '-cf8512ab89d94db0a9314d0a4117fe2e'
)


@pytest.mark.parametrize(
    'req, expected_code, expected_response, auth, headers',
    [
        (
            {'ids': []},
            200,
            {},
            {
                'park_id': 'park_id_000',
                'session': 'session_000',
                'uuid': 'driver_id_000',
            },
            {'X-Driver-Session': 'session_000'},
        ),
        (
            {'ids': ['bad_id_1', 'g/bad_id_2/preved/medved']},
            400,
            None,  # won't check body
            {
                'park_id': 'park_id_000',
                'session': 'session_000',
                'uuid': 'driver_id_000',
            },
            {'X-Driver-Session': 'session_000'},
        ),
        (
            {
                'ids': [
                    'g/1f121111472a45e9bcbb7c72200c6340',
                    'g/6082e94591484e7cb008bf126b462477',
                    'g/not_existing_id',
                    'c/76a1b30d99f14cb78bd1adec06ea324c',
                    'c/76a1b30d99f14cb78bd1adec06ea324c/moscow/dme',
                    'c/76a1b30d99f14cb78bd1adec06ea324c/vko/suburb',
                    'c/76a1b30d99f14cb78bd1adec06ea324c/not_existing/transfer',
                ],
            },
            400,
            None,  # won't check body
            {
                'park_id': 'park_id_000',
                'session': 'session_000',
                'uuid': 'driver_id_000',
            },
            {'X-Driver-Session': 'session_000'},
        ),
        (
            {
                'ids': [
                    'g/1f121111472a45e9bcbb7c72200c6340',
                    'g/6082e94591484e7cb008bf126b462477',
                    'c/76a1b30d99f14cb78bd1adec06ea324c',
                    'c/76a1b30d99f14cb78bd1adec06ea324c/moscow/dme',
                    'c/76a1b30d99f14cb78bd1adec06ea324c/vko/suburb',
                    'c/76a1b30d99f14cb78bd1adec06ea324c/not_existing/transfer',
                ],
            },
            200,
            {
                'g/1f121111472a45e9bcbb7c72200c6340': 'g_moscow.base64',
                'g/6082e94591484e7cb008bf126b462477': (
                    'g_moscow_activation.base64'
                ),
                'c/76a1b30d99f14cb78bd1adec06ea324c': (
                    'c_moscow_maybach.base64'
                ),
                'c/76a1b30d99f14cb78bd1adec06ea324c/moscow/dme': (
                    'c_moscow_maybach_transfer_moscow_dme.base64'
                ),
                'c/76a1b30d99f14cb78bd1adec06ea324c/vko/suburb': (
                    'c_moscow_maybach_transfer_vko_suburb.base64'
                ),
                'c/76a1b30d99f14cb78bd1adec06ea324c/not_existing/transfer': (
                    'c_moscow_maybach.base64'
                ),
            },
            {
                'park_id': 'park_id_000',
                'session': 'session_000',
                'uuid': 'driver_id_000',
            },
            {'X-Driver-Session': 'session_000'},
        ),
        (
            {
                'ids': [
                    'g/REMOVED_MOSCOW',  # should be loaded from mongo
                    'c/00000000000000000000000000000001',  # also from mongo
                    'c/00000000000000000000000000000001/moscow/vko',  # also
                    'g/6082e94591484e7cb008bf126b462477',  # from cache
                ],
            },
            200,
            {
                'g/REMOVED_MOSCOW': 'g_removed_moscow.base64',
                'c/00000000000000000000000000000001': (
                    'c_moscow_old_econom.base64'
                ),
                'c/00000000000000000000000000000001/moscow/vko': (
                    'c_moscow_old_econom_transfer_moscow_vko.base64'
                ),
                'g/6082e94591484e7cb008bf126b462477': (
                    'g_moscow_activation.base64'
                ),
            },
            {
                'park_id': 'park_id_000',
                'session': 'session_000',
                'uuid': 'driver_id_000',
            },
            {'X-Driver-Session': 'session_000'},
        ),
        (
            {
                'ids': [
                    'd/' + CORP_TARIFF_ID + '/category_id',
                    'd/tariff_id/category_id/not_existing/dme',
                    'd/tariff_id/category_id/moscow/not_existing',
                    'd/tariff_id/category_id/moscow/dme',
                ],
            },
            200,
            {
                'd/' + CORP_TARIFF_ID + '/category_id': 'c_decoupling.base64',
                'd/tariff_id/category_id/not_existing/dme': (
                    'c_decoupling.base64'
                ),
                'd/tariff_id/category_id/moscow/not_existing': (
                    'c_decoupling.base64'
                ),
                'd/tariff_id/category_id/moscow/dme': (
                    'c_decoupling_transfer.base64'
                ),
            },
            {
                'park_id': 'park_id_000',
                'session': 'session_000',
                'uuid': 'driver_id_000',
            },
            {'X-Driver-Session': 'session_000'},
        ),
    ],
)
async def test_v1_get_tariff_info(
        taxi_pricing_taximeter,
        mockserver,
        driver_authorizer,
        load,
        req,
        expected_code,
        expected_response,
        auth,
        headers,
):

    driver_authorizer.set_session(
        auth['park_id'], auth['session'], auth['uuid'],
    )

    @mockserver.json_handler('/corp-tariffs/v1/tariff')
    def _mock_corp_tariffs_current(request):
        data = request.args
        assert 'id' in data and (
            data['id'] == 'tariff_id' or data['id'] == CORP_TARIFF_ID
        )
        return {
            'tariff': {
                'id': 'corp_tariff_id',
                'categories': [
                    {
                        'disable_surge': True,
                        'id': 'category_id',
                        'category_name': 'econom',
                        'category_type': 'application',
                        'time_from': '00:00',
                        'time_to': '23:59',
                        'name_key': 'some_val',
                        'category_name_key': 'some_val',
                        'day_type': 2,
                        'currency': 'some_val',
                        'included_one_of': [],
                        'minimal': 49.0,
                        'paid_cancel_fix': 100.0,
                        'add_minimal_to_paid_cancel': True,
                        'meters': [],
                        'special_taximeters': [
                            {
                                'zone_name': 'moscow',
                                'price': {
                                    'time_price_intervals': [
                                        {'begin': 0.0, 'price': 0.5},
                                    ],
                                    'time_price_intervals_meter_id': 0,
                                    'distance_price_intervals': [
                                        {'begin': 0.0, 'price': 2.0},
                                    ],
                                    'distance_price_intervals_meter_id': 0,
                                },
                            },
                        ],
                        'zonal_prices': [
                            {
                                'source': 'moscow',
                                'destination': 'dme',
                                'route_without_jams': False,
                                'price': {
                                    'time_price_intervals': [
                                        {'begin': 0.0, 'price': 1.0},
                                    ],
                                    'time_price_intervals_meter_id': 0,
                                    'distance_price_intervals': [
                                        {'begin': 0.0, 'price': 3.0},
                                    ],
                                    'distance_price_intervals_meter_id': 0,
                                },
                            },
                        ],
                    },
                ],
                'home_zone': 'moscow',
            },
            'disable_fixed_price': False,
            'disable_paid_supply_price': False,
        }

    response = await taxi_pricing_taximeter.post(
        'v1/get_tariff_info',
        json=req,
        headers=headers,
        params={'park_id': auth['park_id']},
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        expected_result = {}
        for key, value in expected_response.items():
            expected_result[key] = load(value).strip()
        assert response.json() == expected_result


@pytest.mark.parametrize('corp_tariff_result', ['ok', 'timeout', 'error'])
async def test_v1_get_tariff_info_corp_tariff_errors(
        taxi_pricing_taximeter,
        mockserver,
        driver_authorizer,
        corp_tariff_result,
):
    auth = {
        'park_id': 'park_id_000',
        'session': 'session_000',
        'uuid': 'driver_id_000',
    }

    driver_authorizer.set_session(
        auth['park_id'], auth['session'], auth['uuid'],
    )

    @mockserver.json_handler('/corp-tariffs/v1/tariff')
    def _mock_corp_tariffs_current(request):
        data = request.args
        assert 'id' in data and (
            data['id'] == 'tariff_id' or data['id'] == CORP_TARIFF_ID
        )
        if corp_tariff_result == 'timeout':
            raise mockserver.TimeoutError()
        elif corp_tariff_result == 'error':
            return mockserver.make_response('Internal Error', status=500)

        return {
            'tariff': {
                'id': 'corp_tariff_id',
                'categories': [
                    {
                        'disable_surge': True,
                        'id': 'category_id',
                        'category_name': 'econom',
                        'category_type': 'application',
                        'time_from': '00:00',
                        'time_to': '23:59',
                        'name_key': 'some_val',
                        'category_name_key': 'some_val',
                        'day_type': 2,
                        'currency': 'some_val',
                        'included_one_of': [],
                        'minimal': 49.0,
                        'paid_cancel_fix': 100.0,
                        'add_minimal_to_paid_cancel': True,
                        'meters': [],
                        'special_taximeters': [
                            {
                                'zone_name': 'moscow',
                                'price': {
                                    'time_price_intervals': [
                                        {'begin': 0.0, 'price': 0.5},
                                    ],
                                    'time_price_intervals_meter_id': 0,
                                    'distance_price_intervals': [
                                        {'begin': 0.0, 'price': 2.0},
                                    ],
                                    'distance_price_intervals_meter_id': 0,
                                },
                            },
                        ],
                        'zonal_prices': [
                            {
                                'source': 'moscow',
                                'destination': 'dme',
                                'route_without_jams': False,
                                'price': {
                                    'time_price_intervals': [
                                        {'begin': 0.0, 'price': 1.0},
                                    ],
                                    'time_price_intervals_meter_id': 0,
                                    'distance_price_intervals': [
                                        {'begin': 0.0, 'price': 3.0},
                                    ],
                                    'distance_price_intervals_meter_id': 0,
                                },
                            },
                        ],
                    },
                ],
                'home_zone': 'moscow',
            },
            'disable_fixed_price': False,
            'disable_paid_supply_price': False,
        }

    response = await taxi_pricing_taximeter.post(
        'v1/get_tariff_info',
        json={'ids': ['d/' + CORP_TARIFF_ID + '/category_id']},
        headers={'X-Driver-Session': 'session_000'},
        params={'park_id': auth['park_id']},
    )
    assert response.status_code == 200 if corp_tariff_result == 'ok' else 500
