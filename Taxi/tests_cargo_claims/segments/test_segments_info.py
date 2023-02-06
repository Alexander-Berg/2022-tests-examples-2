# pylint: disable=C0302
import datetime

import pytest

from testsuite.utils import matching


def _is_feature_present(segment, expected_feature):
    claim_features = set(
        feature['id'] for feature in segment['claim_features']
    )
    return expected_feature in claim_features


@pytest.mark.experiments3(filename='exp3_just_client_payment.json')
@pytest.mark.config(
    CARGO_CLAIMS_CORP_CLIENTS_WITH_LOGISTIC_CONTRACTS={'__default__': True},
)
async def test_logistic_contract(
        taxi_cargo_claims, create_segment, get_db_segment_ids,
):
    await create_segment()
    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )

    assert response.status_code == 200
    segment = response.json()
    assert segment['is_new_logistic_contract']


@pytest.mark.parametrize(
    'test_params',
    [
        pytest.param(
            {},
            marks=pytest.mark.config(
                CARGO_CLAIMS_FETCH_SEGMENTS_EXPERIMENT={
                    'query_type': 'fetch_segments_denorm_json',
                },
            ),
        ),
        pytest.param(
            {},
            marks=pytest.mark.config(
                CARGO_CLAIMS_FETCH_SEGMENTS_EXPERIMENT={
                    'query_type': 'fetch_segments_denorm',
                },
            ),
        ),
        pytest.param(
            {},
            marks=pytest.mark.config(
                CARGO_CLAIMS_FETCH_SEGMENTS_EXPERIMENT={
                    'query_type': 'fetch_segments_denorm_json_strip_nulls',
                },
            ),
        ),
    ],
)
async def test_info_success(
        taxi_cargo_claims,
        create_segment,
        get_db_segment_ids,
        get_default_corp_client_id,
        test_params,
):
    claim_info = await create_segment()
    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )

    assert response.status_code == 200
    segment = response.json()
    assert segment['id'] == segment_id
    assert segment['performer_requirements'] == {
        'cargo_loaders': 2,
        'cargo_type': 'lcv_m',
        'taxi_classes': ['cargo'],
        'dispatch_requirements': {
            'soft_requirements': [
                {
                    'type': 'performer_group',
                    'logistic_group': 'lavka',
                    'performers_restriction_type': 'group_only',
                },
            ],
        },
        'special_requirements': {
            'virtual_tariffs': [
                {
                    'class': 'express',
                    'special_requirements': [{'id': 'food_delivery'}],
                },
                {
                    'class': 'cargo',
                    'special_requirements': [{'id': 'cargo_etn'}],
                },
            ],
        },
    }
    assert segment['allow_batch'] is False
    assert segment['corp_client_id'] == get_default_corp_client_id
    assert segment['zone_id'] == 'moscow'
    assert segment['claim_id'] == claim_info.claim_id
    assert segment['claim_comment'] == 'Очень полезный комментарий'
    assert segment['emergency_phone_id'] == '+79098887777_id'
    assert segment['client_info']['user_locale'] == 'en'
    assert len(segment['points']) == 3
    assert segment['pricing'] == {'offer_id': 'taxi_offer_id_1'}

    contacts = [p['contact'] for p in segment['points']]
    assert contacts == [
        {'name': 'string', 'personal_phone_id': '+71111111111_id'},
        {
            'name': 'string',
            'personal_phone_id': '+72222222222_id',
            'phone_additional_code': '123 45 678',
        },
        {'name': 'string', 'personal_phone_id': '+79999999999_id'},
    ]


@pytest.mark.parametrize(
    'expected_allow_batch',
    (
        pytest.param(False),
        pytest.param(
            True,
            marks=(
                pytest.mark.experiments3(
                    name='cargo_claims_segment_creator',
                    consumers=['cargo-claims/segment-creator'],
                    default_value={'allow_batch': True},
                    is_config=True,
                )
            ),
        ),
        pytest.param(
            False,
            marks=(
                pytest.mark.experiments3(
                    name='cargo_claims_segment_creator',
                    consumers=['cargo-claims/segment-creator'],
                    default_value={'allow_batch': False},
                    is_config=True,
                )
            ),
        ),
    ),
)
async def test_info_allow_batch(
        taxi_cargo_claims,
        create_segment,
        get_db_segment_ids,
        expected_allow_batch,
):
    await create_segment()
    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )

    assert response.status_code == 200
    segment = response.json()
    assert segment['allow_batch'] == expected_allow_batch


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={
        '01234567890123456789012345678912': 'test_client',
    },
)
async def test_employer(taxi_cargo_claims, create_segment, get_db_segment_ids):
    await create_segment()
    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200
    segment = response.json()
    assert segment['employer'] == 'test_client'


async def test_bulk_info_success(
        taxi_cargo_claims, create_segment, get_db_segment_ids,
):

    await create_segment()
    segment_ids = await get_db_segment_ids()

    response = await taxi_cargo_claims.post(
        '/v1/segments/bulk-info',
        json={
            'segment_ids': [
                {'segment_id': value}
                for value in (segment_ids + ['bad_segment_id'])
            ],
        },
    )

    assert response.status_code == 200
    # TODO: real fetch many segments
    assert len(response.json()['segments']) == 1
    assert [
        segment['id'] for segment in response.json()['segments']
    ] == segment_ids


@pytest.mark.parametrize(
    'test_params',
    [
        pytest.param(
            {
                'min_revision': 1,
                'master_called': True,
                'slave_called': False,
                'get_from_master': True,
            },
            marks=pytest.mark.config(
                CARGO_CLAIMS_USE_SLAVE_FOR_FETCH_SEGMENT_WITH_REVISION=False,
            ),
        ),
        pytest.param(
            {
                'min_revision': 2,
                'master_called': True,
                'slave_called': False,
                'get_from_master': True,
            },
            marks=pytest.mark.config(
                CARGO_CLAIMS_USE_SLAVE_FOR_FETCH_SEGMENT_WITH_REVISION=False,
            ),
        ),
        pytest.param(
            {
                'min_revision': 1,
                'master_called': False,
                'slave_called': True,
                'get_from_master': False,
            },
            marks=pytest.mark.config(
                CARGO_CLAIMS_USE_SLAVE_FOR_FETCH_SEGMENT_WITH_REVISION=True,
            ),
        ),
        pytest.param(
            {
                'min_revision': 2,
                'master_called': True,
                'slave_called': True,
                'get_from_master': True,
            },
            marks=pytest.mark.config(
                CARGO_CLAIMS_USE_SLAVE_FOR_FETCH_SEGMENT_WITH_REVISION=True,
            ),
        ),
    ],
)
async def test_bulk_info_master_slave(
        taxi_cargo_claims,
        testpoint,
        create_segment,
        get_db_segment_ids,
        test_params: dict,
):
    @testpoint('fetch-segments-from-slave')
    def slave(data):
        return data

    @testpoint('fetch-segments-from-master')
    def master(data):
        return data

    await create_segment()
    segment_ids = await get_db_segment_ids()

    response = await taxi_cargo_claims.post(
        '/v1/segments/bulk-info',
        json={
            'segment_ids': [
                {
                    'segment_id': value,
                    'min_revision': test_params['min_revision'],
                }
                for value in segment_ids
            ],
        },
    )

    if test_params['master_called']:
        result = await master.wait_call()
        if test_params['get_from_master']:
            assert result == {'data': {'ids': segment_ids}}
    if test_params['slave_called']:
        result = await slave.wait_call()
        if not test_params['get_from_master']:
            assert result == {'data': {'ids': segment_ids}}

    assert response.status_code == 200
    segments = response.json()['segments']
    assert len(segments) == 1
    assert [segment['id'] for segment in segments] == segment_ids


async def test_bulk_info_cut_success(
        taxi_cargo_claims, create_segment, get_db_segment_ids,
):

    await create_segment()
    segment_ids = await get_db_segment_ids()

    response = await taxi_cargo_claims.post(
        '/v1/segments/bulk-info/cut',
        json={
            'segment_ids': [
                {'segment_id': value}
                for value in (segment_ids + ['bad_segment_id'])
            ],
        },
    )

    assert response.status_code == 200
    # TODO: real fetch many segments
    assert len(response.json()['segments']) == 1
    assert [
        segment['id'] for segment in response.json()['segments']
    ] == segment_ids


async def test_items_without_size(
        taxi_cargo_claims, create_segment, get_db_segment_ids,
):
    await create_segment(drop_item_size=True)
    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200
    assert 'size' not in response.json()['items'][0]


async def test_with_due(taxi_cargo_claims, create_segment, get_db_segment_ids):
    due = '2020-08-14T18:37:00+00:00'
    await create_segment(due=due)
    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200
    assert response.json()['due'] == due


async def test_with_lookup_ttl(
        taxi_cargo_claims, create_segment, get_db_segment_ids,
):
    lookup_ttl = '2020-08-14T18:37:00+00:00'
    await create_segment(lookup_ttl=lookup_ttl, use_create_v2=True)
    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200
    json = response.json()
    assert 'lookup_ttl' in json
    assert json['lookup_ttl'] == lookup_ttl


async def test_points_info(
        taxi_cargo_claims,
        create_segment,
        get_db_segment_ids,
        get_default_corp_client_id,
):
    await create_segment()
    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200
    segment = response.json()
    points = sorted(segment['points'], key=lambda point: point['visit_order'])
    first_point = points[0]

    assert first_point['claim_point_id'] == 1
    assert first_point['visit_order'] == 1
    assert first_point['visit_status'] == 'pending'
    assert first_point['label'] == 'source'
    assert 'is_return_required' in first_point
    assert first_point['phones'] == [
        {'label': 'phone_label.source', 'type': 'source', 'view': 'main'},
        {
            'label': 'phone_label.emergency',
            'type': 'emergency',
            'view': 'extra',
        },
    ]
    assert first_point['need_confirmation']
    assert first_point['segment_point_type'] == 'source'


async def test_points_external_order_id(
        taxi_cargo_claims,
        create_segment,
        get_db_segment_ids,
        get_default_corp_client_id,
):
    await create_segment(use_create_v2=True)
    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200
    segment = response.json()

    points = sorted(segment['points'], key=lambda point: point['visit_order'])
    external_order_ids = [p.get('external_order_id') for p in points]

    assert external_order_ids == [
        None,
        'external_order_id_1',
        'external_order_id_2',
        None,
    ]


async def test_locations_info(
        taxi_cargo_claims,
        create_segment,
        get_db_segment_ids,
        get_default_corp_client_id,
):
    await create_segment()
    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200
    segment = response.json()
    locations = segment['locations']
    flats = [loc.get('flat') for loc in locations]
    assert '87B' in flats


@pytest.mark.now('2020-09-01T00:11:00+0300')
async def test_claim_points_time_intervals(
        taxi_cargo_claims,
        create_segment,
        get_db_segment_ids,
        get_default_corp_client_id,
):

    now = datetime.datetime(2020, 9, 1, 8)
    await create_segment(with_time_intervals=True, now=now)
    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )

    assert response.status_code == 200
    segment = response.json()
    assert segment['id'] == segment_id
    assert segment['performer_requirements'] == {
        'cargo_loaders': 2,
        'cargo_type': 'lcv_m',
        'taxi_classes': ['cargo'],
        'dispatch_requirements': {
            'soft_requirements': [
                {
                    'type': 'performer_group',
                    'logistic_group': 'lavka',
                    'performers_restriction_type': 'group_only',
                },
            ],
        },
        'special_requirements': {
            'virtual_tariffs': [
                {
                    'class': 'express',
                    'special_requirements': [{'id': 'food_delivery'}],
                },
                {
                    'class': 'cargo',
                    'special_requirements': [{'id': 'cargo_etn'}],
                },
            ],
        },
    }
    assert segment['allow_batch'] is False
    assert segment['corp_client_id'] == get_default_corp_client_id
    assert segment['zone_id'] == 'moscow'
    assert segment['emergency_phone_id'] == '+79098887777_id'
    assert len(segment['points']) == 4
    assert segment['points'][0]['time_intervals'] == [
        {
            'type': 'strict_match',
            'from': '2020-09-01T08:10:00+00:00',
            'to': '2020-09-01T08:25:00+00:00',
        },
    ]
    assert segment['points'][1]['time_intervals'] == [
        {
            'type': 'strict_match',
            'from': '2020-09-01T08:30:00+00:00',
            'to': '2020-09-01T08:35:00+00:00',
        },
        {
            'type': 'perfect_match',
            'from': '2020-09-01T08:20:00+00:00',
            'to': '2020-09-01T08:45:00+00:00',
        },
    ]
    assert 'time_intervals' not in segment['points'][2]
    assert 'time_intervals' not in segment['points'][3]


async def test_requirements(taxi_cargo_claims, create_segment, get_segment_id):
    await create_segment(fake_middle_points=True)
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200
    assert response.json()['performer_requirements'] == {
        'cargo_loaders': 2,
        'fake_middle_point_express': [2, 2],
        'cargo_type': 'lcv_m',
        'dispatch_requirements': {
            'soft_requirements': [
                {
                    'logistic_group': 'lavka',
                    'type': 'performer_group',
                    'performers_restriction_type': 'group_only',
                },
            ],
        },
        'special_requirements': {
            'virtual_tariffs': [
                {
                    'class': 'express',
                    'special_requirements': [{'id': 'food_delivery'}],
                },
                {
                    'class': 'cargo',
                    'special_requirements': [{'id': 'cargo_etn'}],
                },
            ],
        },
        'taxi_classes': ['cargo'],
    }


async def test_tariffs_substitution(
        taxi_cargo_claims,
        create_claim_segment_matched_car_taxi_class,
        get_default_corp_client_id,
        get_segment_id,
):
    _, segment_id = await create_claim_segment_matched_car_taxi_class(
        get_default_corp_client_id, taxi_class='courier',
    )
    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200
    assert response.json()['tariffs_substitution'] == ['courier']


@pytest.mark.parametrize('custom_context', [{'region_id': 123}, None])
async def test_custom_context_field(
        taxi_cargo_claims,
        create_segment,
        get_segment_id,
        get_default_corp_client_id,
        custom_context: dict,
):
    await create_segment(custom_context=custom_context)
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200

    segment = response.json()
    if custom_context is None:
        custom_context = {}
    assert segment['custom_context'] == custom_context


async def test_delayed_tariffs_soon(
        taxi_cargo_claims,
        create_segment,
        get_segment_id,
        get_default_corp_client_id,
        set_up_tariff_substitution_exp,
):
    await create_segment()
    segment_id = await get_segment_id()

    await set_up_tariff_substitution_exp(
        corp_client_id=get_default_corp_client_id,
    )
    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200
    segment = response.json()

    delayed_tariffs = sorted(
        segment['delayed_tariffs']['tariffs'], key=lambda x: x['taxi_class'],
    )
    assert delayed_tariffs == [
        {'delay_since_lookup': 200, 'taxi_class': 'courier'},
        {'delay_since_lookup': 100, 'taxi_class': 'express'},
    ]


async def test_delayed_tariffs_due(
        taxi_cargo_claims,
        create_segment,
        get_segment_id,
        get_default_corp_client_id,
        set_up_tariff_substitution_exp,
):
    due = (datetime.datetime.utcnow() + datetime.timedelta(hours=2)).strftime(
        '%Y-%m-%dT%H:%M:%SZ',
    )
    await create_segment(due=due)
    segment_id = await get_segment_id()

    await set_up_tariff_substitution_exp(
        corp_client_id=get_default_corp_client_id,
    )
    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200
    segment = response.json()

    delayed_tariffs = sorted(
        segment['delayed_tariffs']['tariffs'], key=lambda x: x['taxi_class'],
    )

    assert delayed_tariffs == [
        {'delay_by_due': -150, 'taxi_class': 'courier'},
        {'delay_by_due': -250, 'taxi_class': 'express'},
    ]


async def test_payment_method(
        taxi_cargo_claims,
        create_segment_with_payment,
        get_segment_id,
        mock_payment_create,
        payment_method='card',
):
    await create_segment_with_payment(payment_method=payment_method)
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200

    segment = response.json()
    for point in segment['points']:
        if point['type'] == 'dropoff':
            assert point['post_payment']['id'] == matching.AnyString()
            assert point['post_payment']['method'] == payment_method
        else:
            assert 'post_payment' not in point


async def test_due_ignorable_special_requirements(
        taxi_cargo_claims,
        create_segment,
        get_segment_id,
        set_tariffs_exp_with_fallback,
        experiments3,
):
    exp3_ignored_thermobag_recorder = experiments3.record_match_tries(
        'cargo_ignored_thermobag',
    )
    due = (datetime.datetime.utcnow() + datetime.timedelta(hours=2)).strftime(
        '%Y-%m-%dT%H:%M:%SZ',
    )
    await create_segment(due=due)
    segment_id = await get_segment_id()

    await set_tariffs_exp_with_fallback()

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200
    segment = response.json()

    delayed_tariffs = sorted(
        segment['delayed_tariffs']['tariffs'], key=lambda x: x['taxi_class'],
    )
    assert delayed_tariffs == [{'delay_by_due': -300, 'taxi_class': 'express'}]

    ignorable_special_requirements = sorted(
        segment['delayed_tariffs']['ignorable_special_requirements'],
        key=lambda x: x['taxi_class'],
    )
    assert ignorable_special_requirements == [
        {
            'delay_by_due': -600,
            'requirements': ['thermobag_confirmed'],
            'taxi_class': 'courier',
        },
        {
            'delay_by_due': -300,
            'requirements': ['thermobag_confirmed'],
            'taxi_class': 'express',
        },
    ]
    match_tries = await exp3_ignored_thermobag_recorder.get_match_tries(
        ensure_ntries=1,
    )
    kwargs_requirements = match_tries[0].kwargs['special_requirements']
    assert sorted(kwargs_requirements) == ['cargo_etn', 'food_delivery']


async def test_soon_ignorable_special_requirements(
        taxi_cargo_claims,
        create_segment,
        get_segment_id,
        get_default_corp_client_id,
        set_tariffs_exp_with_fallback,
):
    await create_segment()
    segment_id = await get_segment_id()

    await set_tariffs_exp_with_fallback()

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200
    segment = response.json()

    delayed_tariffs = sorted(
        segment['delayed_tariffs']['tariffs'], key=lambda x: x['taxi_class'],
    )
    assert delayed_tariffs == [
        {'delay_since_lookup': 600, 'taxi_class': 'express'},
    ]

    ignorable_special_requirements = sorted(
        segment['delayed_tariffs']['ignorable_special_requirements'],
        key=lambda x: x['taxi_class'],
    )
    assert ignorable_special_requirements == [
        {
            'delay_since_lookup': 60,
            'requirements': ['thermobag_confirmed'],
            'taxi_class': 'courier',
        },
        {
            'delay_since_lookup': 600,
            'requirements': ['thermobag_confirmed'],
            'taxi_class': 'express',
        },
    ]


async def test_assign_robot(
        taxi_cargo_claims,
        create_segment,
        get_segment_id,
        get_default_corp_client_id,
        mock_robot_points_search,
):
    await create_segment(assign_robot=True)
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200

    segment = response.json()
    assert segment['custom_context'] == {
        'delivery_flags': {'assign_rover': True},
    }


async def test_cargo_c2c_order_id(
        taxi_cargo_claims,
        create_segment,
        get_segment_id,
        state_controller,
        mock_create_event,
):
    mock_create_event()

    state_controller.use_create_version('v2_cargo_c2c')
    await state_controller.apply(target_status='performer_found')
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )

    assert response.status_code == 200
    segment = response.json()
    assert segment['cargo_c2c_order_id'] == 'cargo_c2c_order_id'


async def test_c2c_origin(
        taxi_cargo_claims,
        create_segment,
        get_segment_id,
        state_controller,
        mock_create_event,
):
    mock_create_event()

    state_controller.use_create_version('v2_cargo_c2c')
    await state_controller.apply(target_status='performer_found')
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )

    assert response.status_code == 200
    segment = response.json()
    assert segment['claim_origin_info'] == {
        'origin': 'yandexgo',
        'displayed_origin': 'Яндекс GO',
        'user_agent': 'Mozilla',
    }
    assert 'corp_client_id' not in segment


@pytest.mark.parametrize(
    'payment_type, payment_method_id,'
    'expected_segment_payment_type, expected_segment_method_id',
    [
        ('card', 'card-xxx', 'card', 'card-xxx'),
        ('cargocorp', 'cargocorp:123:card:456:card-xxx', 'card', 'card-xxx'),
        (
            'cargocorp',
            'cargocorp:123:balance:456:contract:789',
            'corp',
            'corp-123',
        ),
    ],
)
async def test_c2c_phoenix(
        taxi_cargo_claims,
        create_segment,
        get_segment_id,
        state_controller,
        mock_create_event,
        mock_cargo_corp_up,
        mock_cargo_finance,
        payment_type,
        payment_method_id,
        expected_segment_payment_type,
        expected_segment_method_id,
):
    mock_cargo_finance.method_id = payment_method_id
    if expected_segment_payment_type == 'corp':
        mock_cargo_corp_up.is_agent_scheme = False
    mock_create_event()

    state_controller.use_create_version('v2_cargo_c2c')
    state_controller.set_options(payment_type=payment_type)
    state_controller.set_options(payment_method_id=payment_method_id)
    await state_controller.apply(target_status='performer_found')
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )

    assert response.status_code == 200
    segment = response.json()
    assert segment['claim_origin_info'] == {
        'origin': 'yandexgo',
        'displayed_origin': 'Яндекс GO',
        'user_agent': 'Mozilla',
    }
    if payment_type == 'cargocorp':
        assert segment['corp_client_id'] == '123'
    else:
        assert 'corp_client_id' not in segment
    assert segment['yandex_uid'] == 'user_id'

    if payment_type == 'cargocorp':
        assert _is_feature_present(segment, 'phoenix_corp')
        if expected_segment_payment_type == 'card':
            assert _is_feature_present(segment, 'phoenix_claim')
            assert _is_feature_present(segment, 'agent_scheme')
        else:
            assert not _is_feature_present(segment, 'phoenix_claim')
            assert not _is_feature_present(segment, 'agent_scheme')
    else:
        assert _is_feature_present(segment, 'agent_scheme')
        assert not _is_feature_present(segment, 'phoenix_claim')
        assert not _is_feature_present(segment, 'phoenix_corp')

    assert segment['client_info']['payment_info'] == {
        'type': expected_segment_payment_type,
        'method_id': expected_segment_method_id,
    }


async def test_estimations(
        taxi_cargo_claims,
        create_segment,
        get_segment_id,
        get_default_corp_client_id,
):
    await create_segment()
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200

    segment = response.json()
    assert segment['estimations'] == [
        {
            'offer_id': 'taxi_offer_id_1',
            'offer_price': matching.RegexString('\\d+.\\d+'),
            'offer_price_mult': matching.RegexString('\\d+.\\d+'),
            'tariff_class': 'cargo',
        },
    ]


async def test_same_day_data(
        taxi_cargo_claims,
        create_segment,
        get_segment_id,
        get_default_corp_client_id,
        mock_sdd_delivery_intervals,
):
    interval = mock_sdd_delivery_intervals.response['available_intervals'][0]

    await create_segment(
        use_create_v2=True,
        same_day_data={'delivery_interval': interval},
        skip_client_requirements=True,
    )
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200

    segment = response.json()
    assert segment['same_day_data'] == {'delivery_interval': interval}


async def test_pickuped_time(
        taxi_cargo_claims, state_controller, get_db_segment_ids,
):
    await state_controller.apply(target_status='pickuped')

    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )

    pickuped_time = 'unknown'
    segment = response.json()
    for point in segment['points']:
        if point['label'] == 'source':
            for changelog in point['changelog']:
                if changelog['status'] == 'visited':
                    pickuped_time = changelog['timestamp']

    assert segment['pickuped_time'] == pickuped_time
