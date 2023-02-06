import pytest

TRACKING_URL = '/eats/v1/eats-orders-tracking/v1/tracking'
MOCK_DATETIME = '2020-10-28T18:20:00.00+00:00'


@pytest.fixture(name='mock_eats_cargo_claims')
def _mock_eats_cargo_claims(mockserver):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/driver-voiceforwarding',
    )
    def _handler_cargo_claims_driver_voiceforwarding(request):
        mock_response = {'phone': '12345', 'ext': '123', 'ttl_seconds': 600}
        return mockserver.make_response(json=mock_response, status=200)


@pytest.fixture(name='mock_claims_performer_position')
async def _mock_performer_position(mockserver, load_json):
    async def _wrapper(claim_token):
        @mockserver.json_handler(
            '/b2b-taxi/b2b/cargo/integration/v1/claims/performer-position',
        )
        async def _handler_b2b_location(request):
            assert (
                request.headers.get('Authorization') == 'Bearer ' + claim_token
            )
            mock_response = {
                'position': {'lat': 1.0, 'lon': 2.0, 'timestamp': 1234},
            }
            return mockserver.make_response(json=mock_response, status=200)

        return _handler_b2b_location

    return _wrapper


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': False,
        'is_endpoint_claims_performer_position_enabled': True,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'disabled',
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            {'eater_id': 'eater_1', 'claim_token': 'eats123'}, id='default',
        ),
        pytest.param(
            {'eater_id': 'eater_2', 'claim_token': 'eats_kz123'}, id='kz',
        ),
        pytest.param(
            {'eater_id': 'eater_3', 'claim_token': 'store123'}, id='store',
        ),
        pytest.param(
            {'eater_id': 'eater_4', 'claim_token': 'retail123'}, id='retail',
        ),
        pytest.param(
            {'eater_id': 'eater_5', 'claim_token': 'belorussian123'},
            id='belorussian',
        ),
        pytest.param(
            {'eater_id': 'eater_6', 'claim_token': 'groceryru123'},
            id='grocery_ru',
        ),
        pytest.param(
            {'eater_id': 'eater_7', 'claim_token': 'groceryclickdelivery123'},
            id='grocery_click_delivery',
        ),
        pytest.param(
            {
                'eater_id': 'eater_8',
                'claim_token': 'groceryproductdelivery123',
            },
            id='grocery_product_delivery',
        ),
        pytest.param(
            {'eater_id': 'eater_9', 'claim_token': 'eats_new123'},
            id='eats_new',
        ),
        pytest.param(
            {'eater_id': 'eater_10', 'claim_token': 'retail_new123'},
            id='retail_new',
        ),
        pytest.param(
            {'eater_id': 'eater_11', 'claim_token': 'store_new123'},
            id='store_new',
        ),
        pytest.param(
            {'eater_id': 'eater_12', 'claim_token': 'magnit123'}, id='magnit',
        ),
        pytest.param(
            {'eater_id': 'eater_13', 'claim_token': 'eats_kz_new123'},
            id='kz_new',
        ),
    ],
)
async def test_tracked_payload(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        mock_claims_performer_position,
        mock_eats_personal,
        params,
):
    await mock_claims_performer_position(params['claim_token'])
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL,
        headers=make_tracking_headers(eater_id=params['eater_id']),
    )
    assert response.status_code == 200
    order = response.json()['payload']['trackedOrders'][0]
    assert order['courier']['location']['latitude'] == 1.0
    assert order['courier']['location']['longitude'] == 2.0


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': False,
        'is_endpoint_claims_performer_position_enabled': True,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'disabled',
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.config(
    EATS_ORDERS_TRACKING_SELECT_WAYBILL_ENABLED={
        'is_allowed_select_waybill_info': True,
    },
)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'waybills.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
@pytest.mark.experiments3(filename='exp3_use_cargo_waybills.json')
@pytest.mark.parametrize(
    'params, expected_coordinates',
    [
        pytest.param(
            {'eater_id': 'eater_1', 'claim_token': 'corp_client_id_111'},
            {'lat': 1.0, 'lon': 2.0},
            id='greenflow',
        ),
        pytest.param(
            {'eater_id': 'eater_2', 'claim_token': 'eats_kz123'},
            # fallback on courier static info
            {'lat': 1.0, 'lon': 2.0},
            id='have_no_corp_client_id',
        ),
    ],
)
async def test_tracked_payload_with_corp_client(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        mock_claims_performer_position,
        mock_eats_personal,
        params,
        expected_coordinates,
):
    if params['claim_token']:
        await mock_claims_performer_position(params['claim_token'])
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL,
        headers=make_tracking_headers(eater_id=params['eater_id']),
    )
    assert response.status_code == 200
    order = response.json()['payload']['trackedOrders'][0]
    assert (
        order['courier']['location']['latitude'] == expected_coordinates['lat']
    )
    assert (
        order['courier']['location']['longitude']
        == expected_coordinates['lon']
    )


@pytest.mark.pgsql('eats_orders_tracking')
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            {'stq_claim_alias': 'default', 'expected_claim_alias': 'default'},
            id='default',
        ),
        pytest.param(
            {'stq_claim_alias': 'kz', 'expected_claim_alias': 'kz'}, id='kz',
        ),
        pytest.param(
            {'stq_claim_alias': 'store', 'expected_claim_alias': 'store'},
            id='store',
        ),
        pytest.param(
            {'stq_claim_alias': 'retail', 'expected_claim_alias': 'retail'},
            id='retail',
        ),
        pytest.param(
            {'stq_claim_alias': 'by', 'expected_claim_alias': 'by'}, id='by',
        ),
        pytest.param(
            {
                'stq_claim_alias': 'grocery_ru',
                'expected_claim_alias': 'grocery_ru',
            },
            id='grocery_ru',
        ),
        pytest.param(
            {
                'stq_claim_alias': 'grocery_click_delivery',
                'expected_claim_alias': 'grocery_click_delivery',
            },
            id='grocery_click_delivery',
        ),
        pytest.param(
            {
                'stq_claim_alias': 'grocery_product_delivery',
                'expected_claim_alias': 'grocery_product_delivery',
            },
            id='grocery_product_delivery',
        ),
        pytest.param(
            {'stq_claim_alias': 'eats', 'expected_claim_alias': 'eats'},
            id='eats',
        ),
        pytest.param(
            {
                'stq_claim_alias': 'retail_new',
                'expected_claim_alias': 'retail_new',
            },
            id='retail_new',
        ),
        pytest.param(
            {
                'stq_claim_alias': 'store_new',
                'expected_claim_alias': 'store_new',
            },
            id='store_new',
        ),
        pytest.param(
            {'stq_claim_alias': 'magnit', 'expected_claim_alias': 'magnit'},
            id='magnit',
        ),
        pytest.param(
            {'stq_claim_alias': 'kz_new', 'expected_claim_alias': 'kz_new'},
            id='kz_new',
        ),
    ],
)
async def test_check_stq_couriers(
        mockserver, mock_eats_cargo_claims, stq_runner, pgsql, params,
):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/points-eta',
    )
    def _handler_cargo_claims_points_eta(request):
        mock_response = {
            'code': 'point_not_found',
            'message': 'point not found',
        }
        return mockserver.make_response(json=mock_response, status=404)

    await stq_runner.eats_orders_tracking_couriers.call(
        task_id='all_fields',
        args=[],
        kwargs={
            'order_nr': '000000-000000',
            'courier': {
                'name': 'name',
                'type': 'pedestrian',
                'claim_id': 'claim_id',
                'car_model': 'car_model',
                'car_number': 'car_number',
                'courier_id': 'courier_id_2',
                'claim_alias': params['stq_claim_alias'],
                'personal_phone_id': 'phone_id_1',
                'courier_is_hard_of_hearing': False,
            },
        },
    )
    payload = sql_get_courier_payload(pgsql, '000000-000000')
    assert payload['claim_alias'] == params['expected_claim_alias']


def sql_get_courier_payload(pgsql, order_nr):
    cursor = pgsql['eats_orders_tracking'].cursor()
    cursor.execute(
        f"""
        select payload
        from eats_orders_tracking.couriers
        """,
    )
    return list(cursor)[0][0]
