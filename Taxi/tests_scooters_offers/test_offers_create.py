# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
# pylint: disable=too-many-lines
import base64
import uuid
import zlib

from drive import snapshot_pb2
from google.protobuf import json_format
from metrics_aggregations import helpers as metrics_helpers
import psycopg2
import pytest

from tests_scooters_offers import consts


def parse_offer(b64string):
    message = snapshot_pb2.TOffer()
    gzipped = base64.b64decode(b64string)
    proto = zlib.decompress(gzipped)
    message.ParseFromString(proto)
    return json_format.MessageToDict(message)


def build_request(
        api_version='v2',
        omit_user_position=False,
        omit_user_destination=True,
        offer_type=None,
):
    payload, params = {**consts.DEFAULT_PAYLOAD}, {}
    if api_version == 'v1':
        if not omit_user_position:
            params['user_position'] = '37.4+55.8'
        params['car_number'] = '1234'
    elif api_version == 'v2':
        payload['vehicle_numbers'] = ['1234']
        if not omit_user_position:
            payload['user_position'] = [37.4, 55.8]
        if not omit_user_destination:
            payload['user_destination'] = [37.45, 55.85]

    if offer_type:
        payload['offer_type'] = offer_type

    return {
        'path': f'/scooters-offers/{api_version}/offers-create',
        'json': payload,
        'params': params,
        'headers': consts.DEFAULT_HEADERS,
    }


@pytest.mark.parametrize('api_version', ['v1', 'v2'])
@pytest.mark.experiments3(filename='exp3_scooters_offer_params.json')
@pytest.mark.experiments3(filename='exp3_scooters_currency_rules.json')
async def test_simple(
        taxi_scooters_offers,
        pgsql,
        load,
        load_json,
        mockserver,
        taxi_scooters_offers_monitor,
        get_metrics_by_label_values,
        api_version,
):
    await taxi_scooters_offers.tests_control(reset_metrics=True)
    sensor = 'scooters_offers_creation_metrics'

    offers = [
        {
            'offer_id': '43dadec9-37ea031e-316a3c38-5bcc6103',
            'car_number': '1234',
            'proto': load('minutes_offer_protobuf'),
        },
        {
            'offer_id': 'b2be9ea-65389745-b869115e-4ea9f647',
            'car_number': '1234',
            'proto': load('fix_offer_protobuf'),
        },
    ]

    @mockserver.json_handler('/scooter-backend/api/taxi/offers/create')
    async def scooter_backend_mock(request):
        assert request.query['car_number'] == '1234'
        assert request.query['user_position'] == '37.4 55.8'
        assert request.json['payment_methods'] == [consts.CARD_PAYMENT_METHOD]
        assert request.headers['X-YaTaxi-UserId'] == 'user-id'
        assert request.headers['X-YaTaxi-Pass-Flags'] == 'ya-plus'
        assert request.headers.get('FetchPaymentMethods') == (
            '1' if api_version == 'v1' else None
        )
        return {
            'offers': offers,
            'models': {'ninebot': {'code': 'Ninebot'}},
            'payment_methods': [{'type': 'credit_card'}],
            'cars': consts.CARS,
        }

    response = await taxi_scooters_offers.post(**build_request(api_version))
    assert response.status_code == 200
    assert response.json() == load_json(
        f'{api_version}_offers_create_expected_response.json',
    )

    assert scooter_backend_mock.times_called == 1

    cursor = pgsql['scooter_backend'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute('SELECT * FROM drive_offers')
    assert {record['id'] for record in cursor.fetchall()} == {
        offer['offer_id'] for offer in offers
    }

    metrics = await get_metrics_by_label_values(
        taxi_scooters_offers_monitor, sensor=sensor, labels={'sensor': sensor},
    )
    assert metrics == [
        metrics_helpers.Metric(
            labels={
                'sensor': sensor,
                'offer_type': 'standart_offer',
                'constructor_id': 'scooters_minutes',
                'deposit_in_rub': '100',
                'is_fake': '0',
            },
            value=1,
        ),
        metrics_helpers.Metric(
            labels={
                'sensor': sensor,
                'offer_type': 'fix_point',
                'constructor_id': 'fix_msk',
                'deposit_in_rub': '500',
                'is_fake': '0',
            },
            value=1,
        ),
    ]


@pytest.mark.experiments3(filename='exp3_scooters_offer_params.json')
@pytest.mark.experiments3(filename='exp3_scooters_currency_rules.json')
@pytest.mark.parametrize('api_version', ['v1', 'v2'])
async def test_offers_stored_in_drive(
        taxi_scooters_offers, load, mockserver, api_version, load_json, pgsql,
):
    offers = [
        {
            'offer_id': '43dadec9-37ea031e-316a3c38-5bcc6103',
            'car_number': '1234',
            'proto': load('minutes_offer_protobuf'),
        },
        {
            'offer_id': 'b2be9ea-65389745-b869115e-4ea9f647',
            'car_number': '1234',
            'proto': load('fix_offer_protobuf'),
        },
    ]

    cursor = pgsql['scooter_backend'].cursor()
    cursor.execute(
        f"""INSERT INTO drive_offers
                (id, constructor_id, object_id, user_id, deadline, data)
            VALUES
                ('{offers[0]['offer_id']}', 'any',
                    '{str(uuid.uuid4())}', '{str(uuid.uuid4())}', 0, ''),
                ('{offers[1]['offer_id']}', 'any',
                    '{str(uuid.uuid4())}', '{str(uuid.uuid4())}', 0, '');
        """,
    )

    @mockserver.json_handler('/scooter-backend/api/taxi/offers/create')
    async def scooter_backend_mock(_):
        return {
            'offers': offers,
            'models': {'ninebot': {'code': 'Ninebot'}},
            'payment_methods': [{'type': 'credit_card'}],
            'cars': consts.CARS,
        }

    response = await taxi_scooters_offers.post(**build_request(api_version))
    assert response.status_code == 200
    assert response.json() == load_json(
        f'{api_version}_offers_create_expected_response.json',
    )

    assert scooter_backend_mock.times_called == 1

    cursor = pgsql['scooter_backend'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute('SELECT * FROM drive_offers')
    assert {record['id'] for record in cursor.fetchall()} == {
        offer['offer_id'] for offer in offers
    }


@pytest.mark.experiments3(filename='exp3_scooters_additional_headers.json')
@pytest.mark.parametrize('api_version', ['v1', 'v2'])
async def test_additional_headers(
        taxi_scooters_offers, load, mockserver, api_version,
):
    offers = [
        {
            'offer_id': '43dadec9-37ea031e-316a3c38-5bcc6103',
            'car_number': '1234',
            'proto': load('minutes_offer_protobuf'),
        },
        {
            'offer_id': 'b2be9ea-65389745-b869115e-4ea9f647',
            'car_number': '1234',
            'proto': load('fix_offer_protobuf'),
        },
    ]

    @mockserver.json_handler('/scooter-backend/api/taxi/offers/create')
    async def scooter_backend_mock(request):
        assert request.headers['FullInsuranceSupported'] == '1'
        assert request.headers['FixTariffSupported'] == '1'
        return {
            'offers': offers,
            'models': {'ninebot': {'code': 'Ninebot'}},
            'payment_methods': [{'type': 'credit_card'}],
            'cars': consts.CARS,
        }

    response = await taxi_scooters_offers.post(**build_request(api_version))
    assert response.status_code == 200
    assert scooter_backend_mock.times_called == 1


@pytest.mark.experiments3(filename='exp3_scooters_fetch_courier_state.json')
@pytest.mark.experiments3(
    filename='exp3_scooters_fetch_cargo_courier_state.json',
)
@pytest.mark.parametrize('api_version', ['v1', 'v2'])
@pytest.mark.parametrize(
    [
        'cargo_performer_shift_status_code',
        'cargo_performer_shift_response',
        'api_proxy_performer_shift_status_code',
        'api_proxy_performer_shift_response',
    ],
    [
        pytest.param(500, {}, 500, {}, id='fail request'),
        pytest.param(
            200,
            {'isActive': False},
            200,
            {'isActive': False},
            id='not a courier',
        ),
        pytest.param(
            200,
            {'isActive': False},
            200,
            {'isActive': True, 'shiftService': 'lavka'},
            id='lavka courier',
        ),
        pytest.param(
            200,
            {'isActive': False},
            200,
            {'isActive': True, 'shiftService': 'eda'},
            id='eats courier',
        ),
        pytest.param(
            200,
            {'isActive': False},
            200,
            {'isActive': True, 'shiftService': 'scooter'},
            id='energizer',
        ),
        pytest.param(
            200,
            {'isActive': True},
            200,
            {'isActive': False},
            id='cargo courier',
        ),
    ],
)
@pytest.mark.config(
    API_PROXY_CLIENT_QOS={'__default__': {'attempts': 1, 'timeout-ms': 200}},
)
async def test_b2b_tariffs(
        taxi_scooters_offers,
        load,
        mockserver,
        api_version,
        cargo_performer_shift_status_code,
        cargo_performer_shift_response,
        api_proxy_performer_shift_status_code,
        api_proxy_performer_shift_response,
):
    offers = [
        {
            'offer_id': '43dadec9-37ea031e-316a3c38-5bcc6103',
            'car_number': '1234',
            'proto': load('minutes_offer_protobuf'),
        },
        {
            'offer_id': 'b2be9ea-65389745-b869115e-4ea9f647',
            'car_number': '1234',
            'proto': load('fix_offer_protobuf'),
        },
    ]

    @mockserver.json_handler('/scooter-backend/api/taxi/offers/create')
    async def scooter_backend_mock(request):
        cargo_shift_disabled = (
            cargo_performer_shift_status_code == 500
            or not cargo_performer_shift_response.get('isActive', False)
        )
        api_proxy_shift_disabled = (
            api_proxy_performer_shift_status_code == 500
            or not api_proxy_performer_shift_response.get('isActive', False)
        )
        if cargo_shift_disabled and api_proxy_shift_disabled:
            assert request.headers.get('SuggestB2BTariff') is None
            assert request.headers.get('SuggestServiceTariff') is None

        b2b_tariff_condition = (
            api_proxy_performer_shift_response.get('isActive', False)
            and api_proxy_performer_shift_response.get('shiftService')
            in ('lavka', 'eda')
        ) or cargo_performer_shift_response.get('isActive', False)

        service_tariff_condition = (
            api_proxy_performer_shift_response.get('isActive', False)
            and api_proxy_performer_shift_response.get('shiftService')
            == 'scooter'
        )

        if b2b_tariff_condition:
            assert request.headers.get('SuggestB2BTariff') == '1'
            assert request.headers.get('SuggestServiceTariff') is None
        elif service_tariff_condition:
            assert request.headers.get('SuggestB2BTariff') is None
            assert request.headers.get('SuggestServiceTariff') == '1'
        return {
            'offers': offers,
            'models': {'ninebot': {'code': 'Ninebot'}},
            'payment_methods': [{'type': 'credit_card'}],
            'cars': consts.CARS,
        }

    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/courier/info/'
        'retrieve-by-phone',
    )
    async def cargo_performer_shifts_mock(request):
        assert request.query['personal_phone_id'] == '123345'
        assert request.query['device_id'] == 'DEVICE_ID'
        return mockserver.make_response(
            status=cargo_performer_shift_status_code,
            json=cargo_performer_shift_response,
        )

    @mockserver.json_handler(
        '/api-proxy/driver/v1/courier_timetable/'
        'v1/courier-shifts/state_by_phone',
    )
    async def api_proxy_performer_shifts_mock(request):
        assert request.query['personal_phone_id'] == '123345'
        assert request.query['device_id'] == 'DEVICE_ID'
        return mockserver.make_response(
            status=api_proxy_performer_shift_status_code,
            json=api_proxy_performer_shift_response,
        )

    response = await taxi_scooters_offers.post(**build_request(api_version))
    assert response.status_code == 200
    assert scooter_backend_mock.times_called == 1
    assert api_proxy_performer_shifts_mock.times_called == 1
    assert cargo_performer_shifts_mock.times_called == 1


@pytest.mark.experiments3(filename='exp3_scooters_fetch_courier_state.json')
@pytest.mark.experiments3(filename='exp3_scooters_fetch_user_sessions.json')
@pytest.mark.experiments3(
    filename='exp3_scooters_fetch_cargo_courier_state.json',
)
@pytest.mark.parametrize('api_version', ['v1', 'v2'])
@pytest.mark.parametrize('active_sessions_count', [0, 1])
async def test_unique_courier_tariff(
        taxi_scooters_offers, mockserver, api_version, active_sessions_count,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/offers/create')
    async def scooter_backend_mock(request):
        assert request.headers.get('SuggestB2BTariff') == (
            '1' if active_sessions_count == 0 else None
        )
        return {
            'offers': [],
            'models': {'ninebot': {'code': 'Ninebot'}},
            'payment_methods': [{'type': 'credit_card'}],
            'cars': consts.CARS,
        }

    @mockserver.json_handler('/scooters-misc/scooters-misc/v1/user-sessions')
    async def scooters_misc_mock(request):
        sessions = [
            {'scooter_id': f'SCOOTER_ID_{i}'}
            for i in range(active_sessions_count)
        ]
        return {'sessions': sessions}

    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/courier/info/'
        'retrieve-by-phone',
    )
    async def cargo_performer_shifts_mock(request):
        return {'isActive': False, 'shiftService': 'cargo'}

    @mockserver.json_handler(
        '/api-proxy/driver/v1/courier_timetable/'
        'v1/courier-shifts/state_by_phone',
    )
    async def api_proxy_performer_shifts_mock():
        return {'isActive': True, 'shiftService': 'eda'}

    response = await taxi_scooters_offers.post(**build_request(api_version))
    assert response.status_code == 200
    assert scooter_backend_mock.times_called == 1
    assert cargo_performer_shifts_mock.times_called == 1
    assert api_proxy_performer_shifts_mock.times_called == 1
    assert scooters_misc_mock.times_called == 1


@pytest.mark.experiments3(filename='exp3_scooters_offer_params.json')
@pytest.mark.experiments3(filename='exp3_scooters_currency_rules.json')
@pytest.mark.experiments3(filename='exp3_scooters_cashback.json')
@pytest.mark.parametrize('api_version', ['v1', 'v2'])
@pytest.mark.parametrize(
    [
        'scooters_subscription_status_code',
        'scooters_subscription_response',
        'use_position_from',
        'omit_user_position',
        'fallback',
        'expected_subscription_metrics',
        'expected_features_metric',
        'expected_position',
    ],
    [
        pytest.param(
            500,
            {},
            'user',  # use_position_from
            False,  # omit_user_position
            None,  # fallback
            [
                metrics_helpers.Metric(
                    labels={
                        'sensor': 'scooters_offers_by_subscription',
                        'subscription': 'plus',
                        'purchase': 'none',
                    },
                    value=1,
                ),
            ],
            [],
            '37.400000,55.800000',  # expected_position
            id='fail request',
        ),
        pytest.param(
            500,
            {},
            'user',  # use_position_from
            False,  # omit_user_position
            {
                'features': {'free_unlock': True},
                'purchase': 'fallback',
            },  # fallback
            [
                metrics_helpers.Metric(
                    labels={
                        'sensor': 'scooters_offers_by_subscription',
                        'subscription': 'subscription',
                        'purchase': 'fallback',
                    },
                    value=1,
                ),
            ],
            [
                metrics_helpers.Metric(
                    labels={
                        'sensor': 'scooters_offers_by_feature',
                        'feature': 'free_unlock',
                        'purchase': 'fallback',
                    },
                    value=1,
                ),
            ],
            '37.400000,55.800000',  # expected_position
            id='fail request with fallback',
        ),
        pytest.param(
            200,
            {'features': {}},
            'scooter_or_user',  # use_position_from
            False,  # omit_user_position
            None,  # fallback
            [
                metrics_helpers.Metric(
                    labels={
                        'sensor': 'scooters_offers_by_subscription',
                        'subscription': 'plus',
                        'purchase': 'none',
                    },
                    value=1,
                ),
            ],
            [],
            '39.053330,45.012540',  # expected_position
            id='ok, no features',
        ),
        pytest.param(
            200,
            {'features': {'free_unlock': True}, 'purchase': 'full'},
            'user',  # use_position_from
            False,  # omit_user_position
            None,  # fallback
            [
                metrics_helpers.Metric(
                    labels={
                        'sensor': 'scooters_offers_by_subscription',
                        'subscription': 'subscription',
                        'purchase': 'full',
                    },
                    value=1,
                ),
            ],
            [
                metrics_helpers.Metric(
                    labels={
                        'sensor': 'scooters_offers_by_feature',
                        'feature': 'free_unlock',
                        'purchase': 'full',
                    },
                    value=1,
                ),
            ],
            '37.400000,55.800000',  # expected_position
            id='ok, free unlock',
        ),
        pytest.param(
            200,
            {'features': {'free_parking': True}, 'purchase': 'trial'},
            'user_or_scooter',  # use_position_from
            False,  # omit_user_position
            None,  # fallback
            [
                metrics_helpers.Metric(
                    labels={
                        'sensor': 'scooters_offers_by_subscription',
                        'subscription': 'subscription',
                        'purchase': 'trial',
                    },
                    value=1,
                ),
            ],
            [
                metrics_helpers.Metric(
                    labels={
                        'sensor': 'scooters_offers_by_feature',
                        'feature': 'free_parking',
                        'purchase': 'trial',
                    },
                    value=1,
                ),
            ],
            '37.400000,55.800000',  # expected_position
            id='ok, free parking',
        ),
        pytest.param(
            200,
            {
                'features': {'free_unlock': True, 'free_parking': True},
                'purchase': 'trial',
            },
            'user_or_scooter',  # use_position_from
            True,  # omit_user_position
            None,  # fallback
            [
                metrics_helpers.Metric(
                    labels={
                        'sensor': 'scooters_offers_by_subscription',
                        'subscription': 'subscription',
                        'purchase': 'trial',
                    },
                    value=1,
                ),
            ],
            [
                metrics_helpers.Metric(
                    labels={
                        'sensor': 'scooters_offers_by_feature',
                        'feature': 'free_unlock',
                        'purchase': 'trial',
                    },
                    value=1,
                ),
                metrics_helpers.Metric(
                    labels={
                        'sensor': 'scooters_offers_by_feature',
                        'feature': 'free_parking',
                        'purchase': 'trial',
                    },
                    value=1,
                ),
            ],
            '39.053330,45.012540',  # expected_position
            id='ok, free unlock and parking',
        ),
    ],
)
async def test_subscription(
        taxi_scooters_offers,
        taxi_scooters_offers_monitor,
        get_metrics_by_label_values,
        load,
        load_json,
        experiments3,
        mockserver,
        pgsql,
        api_version,
        scooters_subscription_status_code,
        scooters_subscription_response,
        use_position_from,
        omit_user_position,
        fallback,
        expected_subscription_metrics,
        expected_features_metric,
        expected_position,
):
    exp_offer_params = load_json(
        'exp3_scooters_subscription_offer_params.json',
    )
    exp_value = exp_offer_params['experiments'][0]['clauses'][0]['value']
    exp_value['use_position_from'] = use_position_from
    exp_value['fallback'] = fallback
    experiments3.add_experiments_json(exp_offer_params)

    await taxi_scooters_offers.tests_control(reset_metrics=True)
    offers = [
        {
            'offer_id': '43dadec9-37ea031e-316a3c38-5bcc6103',
            'car_number': '1234',
            'proto': load('minutes_offer_protobuf'),
        },
        {
            'offer_id': 'b2be9ea-65389745-b869115e-4ea9f647',
            'car_number': '1234',
            'proto': load('fix_offer_protobuf'),
        },
    ]
    minutes_id = offers[0]['offer_id']

    @mockserver.json_handler('/scooter-backend/api/taxi/offers/create')
    async def scooter_backend_mock(_):
        return {
            'offers': offers,
            'models': {'ninebot': {'code': 'Ninebot'}},
            'payment_methods': [{'type': 'credit_card'}],
            'cars': consts.CARS,
        }

    @mockserver.json_handler(
        '/scooters-subscription/scooters-subscriptions/'
        'v1/subscriptions/offer-params',
    )
    async def scooters_subscription_mock(request):
        assert request.query['position'] == expected_position
        if api_version == 'v2':
            assert request.headers['X-YaTaxi-TZ'] == '10800'
            assert request.query['screens'] == 'subscription'
            scooters_subscription_response['subscription'] = {
                'some': 'details',
            }
        return mockserver.make_response(
            status=scooters_subscription_status_code,
            json=scooters_subscription_response,
        )

    await taxi_scooters_offers.invalidate_caches(
        cache_names=['scooters-positions-cache'],
    )

    request = build_request(api_version, omit_user_position)
    if api_version == 'v2':
        request['headers'].update({'Timezone-Offset': '10800'})
    response = await taxi_scooters_offers.post(**request)
    assert response.status_code == 200
    expected_json = load_json(
        f'{api_version}_offers_create_expected_response.json',
    )

    expected_correctors = ['base_acceptance_price']
    expected_discounts = [
        {
            'Identifier': 'walking_time',
            'Discount': 0.0,
            'IsPromoCode': False,
            'Visible': False,
            'Details': [
                {
                    'TagName': 'old_state_reservation',
                    'Discount': 0.0,
                    'AdditionalTime': 300,
                },
            ],
        },
    ]
    cashback_percent = 5  # has_plus
    if (scooters_subscription_status_code == 200) or fallback:
        features = (
            scooters_subscription_response['features']
            if not fallback
            else fallback['features']
        )
        free_unlock_enabled = features.get('free_unlock', False)
        free_parking_enabled = features.get('free_parking', False)
        if api_version == 'v1':
            for offer in expected_json['offers']:
                if free_unlock_enabled:
                    if 'pack_price' in offer:
                        offer['pack_price'] -= offer['prices'][
                            'acceptance_cost'
                        ]
                    offer['prices']['acceptance_cost'] = 0
        elif api_version == 'v2':
            if not fallback:
                expected_json['subscription'] = {'some': 'details'}
            for offer in expected_json['offers']:
                if free_unlock_enabled:
                    if 'pack_price' in offer:
                        offer['pack_price'] -= offer['prices']['unlock']
                    offer['prices']['unlock'] = 0
                    if offer['type'] == 'minutes_offer':
                        offer['title'] = 'Title: 6$SIGN$'
                        offer['subtitle'] = 'Subtitle: 0$SIGN$'

        if free_unlock_enabled:
            cashback_percent = 10

        if features.get('free_unlock'):
            expected_correctors.append('pf')
        if fallback:
            expected_correctors.append('fb')
        if free_parking_enabled:
            expected_discounts.append(
                {
                    'Identifier': 'free_parking_time',
                    'Details': [
                        {
                            'TagName': 'old_state_parking',
                            'AdditionalTime': 180,
                        },
                    ],
                },
            )
    else:
        expected_correctors.append('fa')

    cursor = pgsql['scooter_backend'].cursor()
    cursor.execute(f'SELECT data FROM drive_offers WHERE id=\'{minutes_id}\'')
    offer = parse_offer(cursor.fetchone()[0])
    correctors = offer.get('Corrector')
    if scooters_subscription_response.get('purchase') == 'trial':
        expected_correctors.append('tr')
    assert correctors == expected_correctors

    assert offer.get('DiscountsInfo') == {'Discounts': expected_discounts}

    for offer in expected_json['offers']:
        offer['cashback_percent'] = cashback_percent

    assert response.json() == expected_json

    assert scooter_backend_mock.times_called == 1
    assert scooters_subscription_mock.times_called == 1

    metrics = await get_metrics_by_label_values(
        taxi_scooters_offers_monitor,
        sensor='scooters_offers_by_subscription',
        labels={},
    )
    assert metrics == expected_subscription_metrics

    metrics = await get_metrics_by_label_values(
        taxi_scooters_offers_monitor,
        sensor='scooters_offers_by_feature',
        labels={},
    )
    assert sorted(metrics, key=lambda x: x.labels['feature']) == sorted(
        expected_features_metric, key=lambda x: x.labels['feature'],
    )


@pytest.mark.parametrize('api_version', ['v1', 'v2'])
async def test_scooter_backend_error(
        taxi_scooters_offers,
        mockserver,
        api_version,
        taxi_scooters_offers_monitor,
        get_single_metric_by_label_values,
):
    await taxi_scooters_offers.tests_control(reset_metrics=True)
    sensor = 'scooters_offers_creation_errors'

    scooter_backend_response = {
        'error_details': {
            'http_code': 400,
            'special_info': {'error_code': 'incorrect_request'},
        },
    }

    @mockserver.json_handler('/scooter-backend/api/taxi/offers/create')
    async def scooter_backend_mock(_):
        return mockserver.make_response(
            status=400, json=scooter_backend_response,
        )

    response = await taxi_scooters_offers.post(**build_request(api_version))
    assert response.status_code == 400
    assert response.json() == scooter_backend_response
    assert scooter_backend_mock.times_called == 1

    metric = await get_single_metric_by_label_values(
        taxi_scooters_offers_monitor, sensor=sensor, labels={'sensor': sensor},
    )
    assert metric == metrics_helpers.Metric(
        labels={'sensor': sensor, 'error_code': 'incorrect_request'}, value=1,
    )


@pytest.mark.experiments3(filename='exp3_scooters_antifraud_user_scoring.json')
@pytest.mark.experiments3(filename='exp3_scooters_offer_params.json')
@pytest.mark.experiments3(filename='exp3_scooters_currency_rules.json')
@pytest.mark.parametrize('api_version', ['v1', 'v2'])
@pytest.mark.config(
    UANTIFRAUD_CLIENT_QOS={
        '/uantifraud/v1/user/scooters_scoring': {
            'attempts': 1,
            'timeout-ms': 200,
        },
    },
)
@pytest.mark.parametrize(
    'uantifraud_status_code, uantifraud_response',
    [
        pytest.param(500, {}, id='fail request'),
        pytest.param(200, {'deposit': 0}, id='ok, deposit 0'),
        pytest.param(200, {'deposit': 300}, id='ok, deposit 300'),
        pytest.param(200, {'deposit': 500}, id='ok, deposit 500'),
    ],
)
async def test_antifraud(
        taxi_scooters_offers,
        load,
        load_json,
        mockserver,
        pgsql,
        api_version,
        uantifraud_status_code,
        uantifraud_response,
):
    offers = [
        {
            'offer_id': '43dadec9-37ea031e-316a3c38-5bcc6103',
            'car_number': '1234',
            'proto': load('minutes_offer_protobuf'),
        },
        {
            'offer_id': 'b2be9ea-65389745-b869115e-4ea9f647',
            'car_number': '1234',
            'proto': load('fix_offer_protobuf'),
        },
    ]

    @mockserver.json_handler('/scooter-backend/api/taxi/offers/create')
    async def scooter_backend_mock(_):
        return {
            'offers': offers,
            'models': {'ninebot': {'code': 'Ninebot'}},
            'payment_methods': [{'type': 'credit_card'}],
            'cars': consts.CARS,
        }

    @mockserver.json_handler('/uantifraud/v1/user/scooters_scoring')
    async def uantifraud_mock(request):
        assert request.json == {
            'payment_method': 'card',
            'phone_verified': '+78005553535',
            'scooter_number': '1234',
            'device_id': 'DEVICE_ID',
            'card_id': 'x123',
            'user_position': {'lat': 55.8, 'lon': 37.4},
            'scooter_position': {'lat': 45.01254, 'lon': 39.05333},
        }
        return mockserver.make_response(
            status=uantifraud_status_code, json=uantifraud_response,
        )

    response = await taxi_scooters_offers.post(**build_request(api_version))
    assert response.status_code == 200
    expected_json = load_json(
        f'{api_version}_offers_create_expected_response.json',
    )
    assert response.json() == expected_json

    assert scooter_backend_mock.times_called == 1
    assert uantifraud_mock.times_called == 1

    cursor = pgsql['scooter_backend'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute('SELECT * FROM drive_offers')
    for offer in cursor.fetchall():
        expected_deposit = uantifraud_response.get('deposit', 500) * 100
        parsed_offer = parse_offer(offer['data'])
        if parsed_offer.get('InstanceType') == 'fix_point':
            pack_price = parsed_offer.get('PackOffer').get('PackPrice')
            expected_deposit = max(expected_deposit, pack_price)
        standart_offer = parsed_offer.get('StandartOffer')
        assert standart_offer.get('DepositAmount') == expected_deposit
        assert standart_offer.get('UseDeposit') == (expected_deposit != 0)


@pytest.mark.parametrize('api_version', ['v1', 'v2'])
@pytest.mark.parametrize(
    ['request_application', 'expected_origin'],
    [
        pytest.param(None, None, id='Unknown, using default origin'),
        pytest.param(
            'app_brand=turboapp,app_ver3=2,app_ver2=8,'
            'app_name=/yandexgo/turboapp/yamaps/android,app_ver1=10',
            'maps',
            id='Prod maps android',
        ),
        pytest.param(
            'app_brand=turboapp,app_ver3=3,app_ver2=8,'
            'app_name=/yandexgo/turboapp/yamaps/ios,app_ver1=13',
            'maps',
            id='Prod maps ios',
        ),
        pytest.param(
            'app_brand=turboapp,app_ver3=5,app_ver2=8,'
            'app_name=maps_app_android,app_ver1=10',
            'maps',
            id='Testing maps',
        ),
        pytest.param(
            'app_brand=yataxi,app_ver3=0,platform_ver3=0,device_make=huawei,'
            'app_name=android,app_build=release,platform_ver2=1,'
            'device_model=col-l29,app_ver2=79,app_ver1=4,platform_ver1=8',
            'taxi',
            id='Taxi',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_scooters_offer_params.json')
@pytest.mark.experiments3(filename='exp3_scooters_currency_rules.json')
@pytest.mark.experiments3(filename='exp3_scooters_offer_origin.json')
async def test_origin(
        taxi_scooters_offers,
        pgsql,
        load,
        load_json,
        mockserver,
        api_version,
        request_application,
        expected_origin,
):
    offers = [
        {
            'offer_id': '43dadec9-37ea031e-316a3c38-5bcc6103',
            'car_number': '1234',
            'proto': load('minutes_offer_protobuf'),
        },
        {
            'offer_id': 'b2be9ea-65389745-b869115e-4ea9f647',
            'car_number': '1234',
            'proto': load('fix_offer_protobuf'),
        },
    ]

    @mockserver.json_handler('/scooter-backend/api/taxi/offers/create')
    async def scooter_backend_mock(request):
        assert request.query.get('origin', None) == expected_origin
        return {
            'offers': offers,
            'models': {'ninebot': {'code': 'Ninebot'}},
            'payment_methods': [{'type': 'credit_card'}],
            'cars': consts.CARS,
        }

    request = build_request(api_version)
    if request_application is not None:
        request['headers'].update(
            {'X-Request-Application': request_application},
        )
    response = await taxi_scooters_offers.post(**request)
    assert response.status_code == 200
    assert response.json() == load_json(
        f'{api_version}_offers_create_expected_response.json',
    )

    assert scooter_backend_mock.times_called == 1


@pytest.mark.experiments3(filename='exp3_scooters_additional_headers.json')
@pytest.mark.experiments3(filename='exp3_scooters_offer_params.json')
@pytest.mark.experiments3(filename='exp3_scooter_backend_offer_params.json')
@pytest.mark.parametrize('is_point_b_near_parking', [True, False])
@pytest.mark.parametrize('has_fix_offer', [True, False])
async def test_to_destination_offer(
        taxi_scooters_offers,
        load,
        mockserver,
        is_point_b_near_parking,
        has_fix_offer,
):
    offers = [
        {
            'offer_id': '43dadec9-37ea031e-316a3c38-5bcc6103',
            'car_number': '1234',
            'proto': load('minutes_offer_protobuf'),
        },
        {
            'offer_id': 'b2be9ea-65389745-b869115e-4ea9f647',
            'car_number': '1234',
            'proto': load('fix_offer_protobuf'),
        },
    ]

    @mockserver.json_handler('/scooter-backend/api/taxi/offers/create')
    async def scooter_backend_mock(request):
        assert request.headers['FullInsuranceSupported'] == '1'
        assert request.headers['FixTariffSupported'] == '1'
        if is_point_b_near_parking:
            assert request.query['user_destination'] == '37.451 55.851'

        return {
            'offers': (
                offers
                if is_point_b_near_parking and has_fix_offer
                else offers[:1]
            ),
            'models': {'ninebot': {'code': 'Ninebot'}},
            'payment_methods': [{'type': 'credit_card'}],
            'cars': consts.CARS,
        }

    request = build_request(
        'v2', offer_type='to_destination_offer', omit_user_destination=False,
    )
    if not is_point_b_near_parking:
        request['json']['user_destination'] = [37.47, 55.87]
    response = await taxi_scooters_offers.post(**request)

    assert scooter_backend_mock.times_called == 1
    assert response.status_code == 200
    resp_offers = response.json()['offers']
    assert len(resp_offers) == 1
    offer = resp_offers[0]
    if is_point_b_near_parking and has_fix_offer:
        assert offer['type'] == 'fix_offer'
        assert offer['title'] == 'to_destination offer title'
        assert offer['subtitle'] == ''
    else:
        assert offer['type'] == 'minutes_offer'
