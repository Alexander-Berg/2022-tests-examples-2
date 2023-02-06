import pytest

SECOND_ORDER_ID = 'b65ad669-e067-406d-aac7-79fec6381f4a'


def build_kwargs(
        order_id,
        chain_taxi_order_id: str = '',
        lookup_version: int = 1,
        is_manual_dispatch: bool = None,
        chain_taxi_order_left_dist: int = None,
        dist_from_point_a: int = 100,
        tariff_class: str = None,
        driver_id: str = None,
):
    kwargs = {
        'claim_id': f'order/{order_id}',
        'order_id': 'taxi-order',
        'order_alias_id': '1234',
        'phone_pd_id': 'phone_pd_id',
        'name': 'Kostya',
        'driver_id': '789',
        'park_id': '456',
        'park_clid': '100500',
        'car_id': '123',
        'car_number': 'А001АА77',
        'car_model': 'KAMAZ',
        'lookup_version': lookup_version,
        'dist_from_point_a': dist_from_point_a,
        'eta_to_point_a': {'$date': '2020-06-17T22:40:00+0300'},
        'chain_taxi_order_id': chain_taxi_order_id,
        'chain_taxi_order_left_dist': chain_taxi_order_left_dist,
    }
    if is_manual_dispatch is not None:
        kwargs['is_manual_dispatch'] = is_manual_dispatch
    if tariff_class is not None:
        kwargs['tariff_class'] = tariff_class
    if driver_id is not None:
        kwargs['driver_id'] = driver_id
    return kwargs.copy()


@pytest.fixture(name='mock_cargo_dispatch')
def _mock_cargo_dispatch(mockserver):
    @mockserver.json_handler(
        '/cargo-dispatch/v1/waybill/mark/taxi-order-performer-found',
    )
    def _mock_cargo_dispatch(request):
        return {'id': 'waybill-ref', 'status': 'processing'}

    return _mock_cargo_dispatch


@pytest.fixture(name='mock_cargo_pricing_confirm_usage')
def _mock_cargo_pricing_confirm_usage(mockserver):
    class Context:
        mock = None
        request = None

    ctx = Context()

    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc/confirm-usage')
    def _mock(request):
        ctx.request = request.json
        return {}

    ctx.mock = _mock
    return ctx


@pytest.fixture(name='mock_driver_profiles')
def _mock_driver_profiles(mockserver):
    class Context:
        profiles_park_driver_profile_id = 'park_1_789'
        profiles_data = {'is_deaf': True}
        mock = None

    ctx = Context()

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': (
                        ctx.profiles_park_driver_profile_id
                    ),
                    'data': ctx.profiles_data,
                },
            ],
        }

    ctx.mock = _mock

    return ctx


@pytest.fixture(name='call_stq_cargo_taxi_order_performer_found')
def _call_stq_cargo_taxi_order_performer_found(stq_runner, default_order_id):
    async def _call(
            tariff_class='mock_tariff_class',
            driver_id=None,
            expect_fail=False,
    ):
        await stq_runner.cargo_taxi_order_performer_found.call(
            task_id='test_stq',
            kwargs=build_kwargs(
                order_id=default_order_id,
                tariff_class=tariff_class,
                driver_id=driver_id,
            ),
            expect_fail=expect_fail,
        )

    return _call


@pytest.mark.parametrize('park_clid', [None, '', 'clid_1'])
async def test_cargo_taxi_order_performer_found_waybill(
        taxi_cargo_orders,
        mockserver,
        stq_runner,
        order_id_without_performer,
        fetch_performer,
        park_clid,
        mock_driver_profiles,
):
    @mockserver.json_handler(
        '/cargo-dispatch/v1/waybill/mark/taxi-order-performer-found',
    )
    def mock_cargo_dispatch(request):
        assert request.json['waybill_id'] == 'waybill-ref-no-performer'
        assert request.json['order_id'] == order_id_without_performer
        assert request.json['tariff_class'] == 'cargo'
        if park_clid is None:
            assert 'park_clid' not in request.json
        else:
            assert request.json['park_clid'] == park_clid
        return {'id': 'waybill-ref', 'status': 'processing'}

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks_list(request):
        return {'parks': []}

    # INSERT
    kwargs = {
        'claim_id': f'order/{order_id_without_performer}',
        'order_id': 'taxi-order',
        'order_alias_id': '1234',
        'phone_pd_id': 'phone_pd_id',
        'name': 'Kostya',
        'driver_id': '789',
        'park_id': 'park_1',
        'car_id': '123',
        'car_number': 'А001АА77',
        'car_model': 'KAMAZ',
        'car_color': 'красный',
        'car_color_hex': 'FF0000',
        'transport_type': 'car',
        'lookup_version': 1,
        'tariff_class': 'cargo',
        'dist_from_point_a': 100,
        'eta_to_point_a': {'$date': '2020-06-17T22:40:00+0300'},
    }
    if park_clid is not None:
        kwargs['park_clid'] = park_clid
    await stq_runner.cargo_taxi_order_performer_found.call(
        task_id='test_stq', kwargs=kwargs,
    )
    assert mock_cargo_dispatch.times_called == 1
    response = await taxi_cargo_orders.post(
        '/v1/performers/bulk-info',
        json={'orders_ids': [order_id_without_performer]},
    )
    assert response.status_code == 200
    performer = {
        'car_id': '123',
        'car_model': 'KAMAZ',
        'car_number': 'А001АА77',
        'car_color': 'красный',
        'car_color_hex': 'FF0000',
        'transport_type': 'car',
        'dist_from_point_a': 100,
        'driver_id': '789',
        'is_deaf': True,
        'eta_to_point_a': '2020-06-17T19:40:00+00:00',
        'lookup_version': 1,
        'name': 'Kostya',
        'order_alias_id': '1234',
        'order_id': order_id_without_performer,
        'park_id': 'park_1',
        'phone_pd_id': 'phone_pd_id',
        'tariff_class': 'cargo',
        'revision': 1,
        'manual_dispatch': False,
    }
    if park_clid is not None:
        performer['park_clid'] = park_clid
    assert response.json() == {'performers': [performer]}
    performer = fetch_performer(order_id_without_performer)
    assert performer.dist_from_point_a == 100
    assert str(performer.eta_to_point_a) == '2020-06-17 22:40:00+03:00'
    # UPDATE
    kwargs = {
        'claim_id': f'order/{order_id_without_performer}',
        'order_id': 'taxi-order',
        'order_alias_id': '1234',
        'phone_pd_id': 'phone_pd_id',
        'name': 'Kostya',
        'driver_id': '789',
        'park_id': 'park_1',
        'car_id': '123',
        'car_number': 'А999АА77',
        'car_model': 'KAMAZ',
        'lookup_version': 1,
        'tariff_class': 'cargo',
        'dist_from_point_a': 100,
        'eta_to_point_a': {'$date': '2020-06-17T22:40:00+0300'},
    }
    if park_clid is not None:
        kwargs['park_clid'] = park_clid
    await stq_runner.cargo_taxi_order_performer_found.call(
        task_id='test_stq', kwargs=kwargs,
    )
    assert mock_cargo_dispatch.times_called == 2
    response = await taxi_cargo_orders.post(
        '/v1/performers/bulk-info',
        json={'orders_ids': [order_id_without_performer]},
    )
    assert response.status_code == 200
    response_performer = {
        'car_id': '123',
        'car_model': 'KAMAZ',
        'car_number': 'А999АА77',
        'dist_from_point_a': 100,
        'driver_id': '789',
        'is_deaf': True,
        'eta_to_point_a': '2020-06-17T19:40:00+00:00',
        'lookup_version': 1,
        'name': 'Kostya',
        'order_alias_id': '1234',
        'order_id': order_id_without_performer,
        'park_id': 'park_1',
        'phone_pd_id': 'phone_pd_id',
        'tariff_class': 'cargo',
        'revision': 2,
        'manual_dispatch': False,
    }
    if park_clid is not None:
        response_performer['park_clid'] = park_clid
    assert response.json() == {'performers': [response_performer]}


@pytest.mark.parametrize(
    'dispatch_response, stq_expect_fail',
    [
        pytest.param(
            {
                'json': {'code': 'waybill_not_found', 'message': 'not found'},
                'status': 404,
            },
            False,
            id='Waybill not found',
        ),
        pytest.param(
            {
                'json': {
                    'code': 'state_mismatch',
                    'message': 'state mismatch',
                },
                'status': 409,
            },
            False,
            id='State mismatch',
        ),
        pytest.param(
            {'json': None, 'status': 500}, True, id='Internal server error',
        ),
    ],
)
async def test_dispatch_mark_parformer_found_errors(
        taxi_cargo_orders,
        mockserver,
        stq_runner,
        order_id_without_performer,
        fetch_performer,
        dispatch_response,
        stq_expect_fail,
        mock_driver_profiles,
):
    @mockserver.json_handler(
        '/cargo-dispatch/v1/waybill/mark/taxi-order-performer-found',
    )
    def mock_cargo_dispatch(request):
        assert request.json['waybill_id'] == 'waybill-ref-no-performer'
        assert request.json['order_id'] == order_id_without_performer
        assert request.json['tariff_class'] == 'cargo'
        return mockserver.make_response(**dispatch_response)

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks_list(request):
        return {'parks': []}

    # INSERT
    kwargs = {
        'claim_id': f'order/{order_id_without_performer}',
        'order_id': 'taxi-order',
        'order_alias_id': '1234',
        'phone_pd_id': 'phone_pd_id',
        'name': 'Kostya',
        'driver_id': '789',
        'park_id': 'park_1',
        'car_id': '123',
        'car_number': 'А001АА77',
        'car_model': 'KAMAZ',
        'car_color': 'красный',
        'car_color_hex': 'FF0000',
        'transport_type': 'car',
        'lookup_version': 1,
        'tariff_class': 'cargo',
        'dist_from_point_a': 100,
        'eta_to_point_a': {'$date': '2020-06-17T22:40:00+0300'},
    }

    await stq_runner.cargo_taxi_order_performer_found.call(
        task_id='test_stq', kwargs=kwargs, expect_fail=stq_expect_fail,
    )

    assert mock_cargo_dispatch.times_called > 0


@pytest.mark.config(CARGO_ORDERS_CONFIRM_CALCULATION_ENABLED=True)
async def test_cargo_taxi_order_performer_found_usage_confrim(
        stq_runner,
        happy_path_park_list,
        happy_path_calc_price_handler,
        default_order_id,
        mock_cargo_dispatch,
        mock_driver_profiles,
        mock_cargo_pricing_confirm_usage,
):
    mock_driver_profiles.profiles_park_driver_profile_id = '456_789'

    await stq_runner.cargo_taxi_order_performer_found.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'order_alias_id': '1234',
            'phone_pd_id': 'phone_pd_id',
            'name': 'Kostya',
            'driver_id': '789',
            'park_id': '456',
            'car_id': '123',
            'car_number': 'А001АА77',
            'car_model': 'KAMAZ',
            'lookup_version': 1,
            'dist_from_point_a': 100,
            'eta_to_point_a': {'$date': '2020-06-17T22:40:00+0300'},
        },
        expect_fail=False,
    )

    assert mock_cargo_dispatch.times_called == 1
    assert mock_cargo_pricing_confirm_usage.mock.times_called == 1


async def test_cargo_taxi_order_performer_found_orders_bulk_info(
        mockserver,
        stq_runner,
        taxi_cargo_orders,
        happy_path_park_list,
        happy_path_calc_price_handler,
        default_order_id,
        mock_cargo_dispatch,
        mock_driver_profiles,
):
    mock_driver_profiles.profiles_park_driver_profile_id = '456_789'

    await stq_runner.cargo_taxi_order_performer_found.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'order_alias_id': '1234',
            'phone_pd_id': 'phone_pd_id',
            'name': 'Kostya',
            'driver_id': '789',
            'park_id': '456',
            'car_id': '123',
            'car_number': 'А001АА77',
            'car_model': 'KAMAZ',
            'lookup_version': 1,
            'dist_from_point_a': 100,
            'eta_to_point_a': {'$date': '2020-06-17T22:40:00+0300'},
        },
        expect_fail=False,
    )
    assert mock_cargo_dispatch.times_called == 1

    response = await taxi_cargo_orders.post(
        '/v1/orders/bulk-info', json={'cargo_orders_ids': [default_order_id]},
    )
    assert response.status_code == 200
    response_orders = response.json()
    for order in response_orders['orders']:
        order.pop('order_updated')
    assert response_orders == {
        'orders': [
            {
                'order': {
                    'order_id': default_order_id,
                    'presetcar_calc_id': (
                        'cargo-pricing/v1/f6e1661746e34f8c8234832e1d718d85'
                    ),
                    'use_cargo_pricing': True,
                    'provider_order_id': 'taxi-order',
                },
                'performer_info': {
                    'car_id': '123',
                    'car_model': 'KAMAZ',
                    'car_number': 'А001АА77',
                    'dist_from_point_a': 100,
                    'driver_id': '789',
                    'is_deaf': True,
                    'eta_to_point_a': '2020-06-17T19:40:00+00:00',
                    'lookup_version': 1,
                    'name': 'Kostya',
                    'order_alias_id': '1234',
                    'order_id': default_order_id,
                    'park_id': '456',
                    'park_name': 'some park name',
                    'park_org_name': 'some park org name',
                    'phone_pd_id': 'phone_pd_id',
                    'revision': 2,
                    'manual_dispatch': False,
                },
            },
        ],
    }


@pytest.mark.pgsql('cargo_orders', files=['state_two_orders.sql'])
@pytest.mark.parametrize('subtract_left_dist', [False, True])
async def test_performer_found_chain_info(
        mockserver,
        stq_runner,
        fetch_performer,
        experiments3,
        taxi_cargo_orders,
        subtract_left_dist,
        happy_path_park_list,
        happy_path_calc_price_handler,
        mock_driver_profiles,
        default_order_id,
        prev_taxi_order_id='taxi-order-2',
        expected_cargo_order_id=SECOND_ORDER_ID,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_point_a_calc',
        consumers=['cargo-orders/stq_cargo_taxi_order_performer_found'],
        clauses=[],
        default_value={'subtract_chain_order_left_dist': subtract_left_dist},
    )
    await taxi_cargo_orders.invalidate_caches()

    mock_driver_profiles.profiles_park_driver_profile_id = '789'

    @mockserver.json_handler(
        '/cargo-dispatch/v1/waybill/mark/taxi-order-performer-found',
    )
    def mock_cargo_dispatch(request):
        assert (
            request.json.get('chain_parent_cargo_order_id')
            == expected_cargo_order_id
        )
        return {'id': 'waybill-ref', 'status': 'processing'}

    await stq_runner.cargo_taxi_order_performer_found.call(
        task_id='test_stq',
        kwargs=build_kwargs(
            default_order_id,
            chain_taxi_order_id=prev_taxi_order_id,
            dist_from_point_a=1200,
            chain_taxi_order_left_dist=1000,
        ),
        expect_fail=False,
    )
    assert mock_cargo_dispatch.times_called == 1
    expected_dist = 200 if subtract_left_dist else 1200
    assert fetch_performer(default_order_id).dist_from_point_a == expected_dist

    # check no chain info on reorders
    expected_cargo_order_id = None
    await stq_runner.cargo_taxi_order_performer_found.call(
        task_id='test_stq',
        kwargs=build_kwargs(
            default_order_id, lookup_version=2, dist_from_point_a=1200,
        ),
        expect_fail=False,
    )
    assert mock_cargo_dispatch.times_called == 2
    assert fetch_performer(default_order_id).dist_from_point_a == 1200


@pytest.mark.pgsql('cargo_orders', files=['state_two_orders.sql'])
@pytest.mark.parametrize(
    'is_manual_dispatch, expected_manual_dispatch',
    [(None, False), (False, False), (True, True)],
)
async def test_performer_found_manual_dispatch(
        mockserver,
        stq_runner,
        taxi_cargo_orders,
        happy_path_park_list,
        happy_path_calc_price_handler,
        default_order_id,
        is_manual_dispatch: bool,
        expected_manual_dispatch: bool,
        mock_cargo_dispatch,
        mock_driver_profiles,
):
    mock_driver_profiles.profiles_park_driver_profile_id = '789'

    await stq_runner.cargo_taxi_order_performer_found.call(
        task_id='test_stq',
        kwargs=build_kwargs(
            default_order_id, is_manual_dispatch=is_manual_dispatch,
        ),
        expect_fail=False,
    )
    assert mock_cargo_dispatch.times_called == 1

    response = await taxi_cargo_orders.post(
        '/v1/orders/bulk-info', json={'cargo_orders_ids': [default_order_id]},
    )
    assert response.status_code == 200
    assert (
        response.json()['orders'][0]['performer_info']['manual_dispatch']
        == expected_manual_dispatch
    )


@pytest.mark.parametrize(
    'does_driver_profile_exist, does_driver_profiles_fail,'
    ' driver_profiles_status, profile_retrieve_enabled',
    [
        (False, False, 200, True),
        (True, True, 400, True),
        (True, True, 500, True),
        (True, False, 200, True),
        pytest.param(
            True,
            False,
            200,
            False,
            marks=pytest.mark.config(
                CARGO_ORDERS_PROFILE_RETRIEVE_ENABLED=False,
            ),
        ),
    ],
)
async def test_performer_found_without_name(
        default_order_id,
        mockserver,
        stq_runner,
        taxi_cargo_orders,
        does_driver_profile_exist,
        does_driver_profiles_fail,
        driver_profiles_status,
        profile_retrieve_enabled,
        mock_cargo_dispatch,
):
    park_id = '456'
    park_name = 'some park name'
    park_org_name = 'some park org name'

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def mock_parks_list(request):
        assert request.json['query'] == {'park': {'ids': [park_id]}}
        return {
            'parks': [
                {
                    'id': 'park_id',
                    'login': 'login',
                    'is_active': True,
                    'city_id': 'city',
                    'locale': 'locale',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'demo_mode': False,
                    'country_id': 'country_id',
                    'name': park_name,
                    'org_name': park_org_name,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    driver_id = 'driver_id1'
    first_name = 'Василий'
    middle_name = 'Петрович'
    last_name = 'Гавриков'

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def mock_driver_profiles(request):
        return mockserver.make_response(
            json={
                'profiles': [
                    {
                        'park_driver_profile_id': park_id + '_' + driver_id,
                        'data': (
                            {
                                'is_deaf': True,
                                'full_name': {
                                    'first_name': first_name,
                                    'middle_name': middle_name,
                                    'last_name': last_name,
                                },
                            }
                            if does_driver_profile_exist
                            else {}
                        ),
                    },
                ],
            }
            if not does_driver_profiles_fail
            else {},
            status=driver_profiles_status,
        )

    await stq_runner.cargo_taxi_order_performer_found.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'order_alias_id': '1234',
            'phone_pd_id': 'phone_pd_id',
            'driver_id': driver_id,
            'park_id': park_id,
            'car_id': '123',
            'car_number': 'А001АА77',
            'car_model': 'KAMAZ',
            'lookup_version': 1,
            'dist_from_point_a': 100,
            'eta_to_point_a': {'$date': '2020-06-17T22:40:00+0300'},
        },
        expect_fail=False,
    )
    assert mock_parks_list.times_called == 1
    assert (
        mock_driver_profiles.times_called == 0
        if not profile_retrieve_enabled
        else 1
        if not does_driver_profiles_fail
        else 3
    )
    assert mock_cargo_dispatch.times_called == 1

    response = await taxi_cargo_orders.post(
        '/v1/orders/bulk-info', json={'cargo_orders_ids': [default_order_id]},
    )
    assert response.status_code == 200
    assert response.json()['orders'][0]['performer_info']['name'] == (
        f'{last_name} {first_name} {middle_name}'
        if profile_retrieve_enabled
        and not does_driver_profiles_fail
        and does_driver_profile_exist
        else ''
    )


@pytest.mark.config(CARGO_ORDERS_CALC_OFFER_PRICE_ON_PERFORMER_ASSIGNED=True)
async def test_cargo_taxi_order_performer_found_calc_offer_price_calc_request(
        call_stq_cargo_taxi_order_performer_found,
        happy_path_park_list,
        mock_cargo_dispatch,
        mock_driver_profiles,
        mock_cargo_pricing_calc,
        mock_cargo_pricing_calc_retrieve,
):
    await call_stq_cargo_taxi_order_performer_found()

    assert mock_cargo_pricing_calc.mock.times_called == 1
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 0
    assert mock_cargo_pricing_calc.request == {
        'cargo_items': [],
        'clients': [
            {
                'corp_client_id': '5e36732e2bc54e088b1466e08e31c486',
                'user_id': 'taxi_user_id_1',
            },
        ],
        'entity_id': 'order/taxi-order',
        'external_ref': 'meta_order_id/taxi-order',
        'homezone': 'moscow',
        'is_usage_confirmed': True,
        'idempotency_token': 'presetcar-order-taxi-order-performer-789',
        'origin_uri': 'stq/cargo_taxi_order_performer_found',
        'payment_info': {
            'method_id': 'corp-5e36732e2bc54e088b1466e08e31c486',
            'type': 'corp',
        },
        'performer': {
            'assigned_at': '2020-01-01T00:00:00+00:00',
            'driver_id': '789',
            'park_db_id': '456',
        },
        'price_for': 'performer',
        'special_requirements': [],
        'tariff_class': 'mock_tariff_class',
        'taxi_requirements': {},
        'waypoints': [
            {
                'claim_id': 'claim_uuid_1',
                'id': 'seg_1_point_1',
                'position': [37.642979, 55.734977],
                'type': 'pickup',
            },
            {
                'claim_id': 'claim_uuid_1',
                'id': 'seg_1_point_2',
                'position': [37.583, 55.9873],
                'type': 'dropoff',
            },
            {
                'claim_id': 'claim_uuid_1',
                'id': 'seg_1_point_3',
                'position': [37.583, 55.8873],
                'type': 'return',
            },
        ],
        'make_processing_create_event': True,
        'calc_kind': 'offer',
    }


@pytest.mark.config(CARGO_ORDERS_CALC_OFFER_PRICE_ON_PERFORMER_ASSIGNED=True)
async def test_cargo_taxi_order_performer_found_calc_offer_price_retrieve(
        call_stq_cargo_taxi_order_performer_found,
        happy_path_park_list,
        mock_cargo_dispatch,
        mock_driver_profiles,
        mock_cargo_pricing_calc,
        mock_cargo_pricing_calc_retrieve,
):
    await call_stq_cargo_taxi_order_performer_found()

    assert mock_cargo_pricing_calc.mock.times_called == 1
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 0

    await call_stq_cargo_taxi_order_performer_found()

    assert mock_cargo_pricing_calc.mock.times_called == 1
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 1
    assert mock_cargo_pricing_calc_retrieve.request == {
        'calc_id': 'cargo-pricing/v1/f6e1661746e34f8c8234832e1d718d85',
        'reading_mode': 'master',
    }


@pytest.mark.config(CARGO_ORDERS_CALC_OFFER_PRICE_ON_PERFORMER_ASSIGNED=True)
async def test_cargo_taxi_order_performer_found_calc_price_on_no_tariff_class(
        call_stq_cargo_taxi_order_performer_found,
        happy_path_park_list,
        mock_cargo_dispatch,
        mock_driver_profiles,
        mock_cargo_pricing_calc,
):
    await call_stq_cargo_taxi_order_performer_found(
        tariff_class=None, expect_fail=True,
    )

    assert mock_cargo_pricing_calc.mock.times_called == 0


@pytest.mark.config(
    CARGO_ORDERS_CONFIRM_CALCULATION_ENABLED=True,
    CARGO_ORDERS_CALC_OFFER_PRICE_ON_PERFORMER_ASSIGNED=True,
)
async def test_cargo_taxi_order_performer_found_confrim_existing_price(
        call_stq_cargo_taxi_order_performer_found,
        happy_path_park_list,
        happy_path_calc_price_handler,
        mock_cargo_dispatch,
        mock_driver_profiles,
        mock_cargo_pricing_confirm_usage,
        mock_cargo_pricing_calc_retrieve,
):
    # using same driver_id as in happy_path_calc_price_handler
    await call_stq_cargo_taxi_order_performer_found(driver_id='mock-driver')

    assert mock_cargo_pricing_confirm_usage.mock.times_called == 1
    assert mock_cargo_pricing_confirm_usage.request == {
        'calc_id': 'cargo-pricing/v1/f6e1661746e34f8c8234832e1d718d85',
        'external_ref': 'meta_order_id/taxi-order',
    }


async def test_driver_loyalty(
        stq_runner,
        happy_path_park_list,
        happy_path_calc_price_handler,
        default_order_id,
        mock_cargo_dispatch,
        mock_driver_profiles,
        mockserver,
        performers_loyalties,
):
    mock_driver_profiles.profiles_park_driver_profile_id = '456_789'

    @mockserver.json_handler('/loyalty/service/loyalty/v1/rewards')
    def mock_loyaly(request):
        assert request.json == {
            'driver_rewards': ['point_b'],
            'data': {
                'unique_driver_id': 'unique_driver_id_1',
                'zone_name': 'zone_name_1',
            },
        }
        return {
            'matched_driver_rewards': {
                'point_b': {'show_point_b': True, 'lock_reasons': {}},
            },
        }

    await stq_runner.cargo_taxi_order_performer_found.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'order_alias_id': '1234',
            'phone_pd_id': 'phone_pd_id',
            'name': 'Kostya',
            'driver_id': '789',
            'park_id': '456',
            'car_id': '123',
            'car_number': 'А001АА77',
            'car_model': 'KAMAZ',
            'lookup_version': 1,
            'dist_from_point_a': 100,
            'eta_to_point_a': {'$date': '2020-06-17T22:40:00+0300'},
            'unique_driver_id': 'unique_driver_id_1',
            'zone_name': 'zone_name_1',
        },
        expect_fail=False,
    )
    assert mock_loyaly.times_called == 1
    assert performers_loyalties() == [
        (
            {
                'matched_driver_rewards': {
                    'point_b': {'lock_reasons': {}, 'show_point_b': True},
                },
            },
        ),
    ]
