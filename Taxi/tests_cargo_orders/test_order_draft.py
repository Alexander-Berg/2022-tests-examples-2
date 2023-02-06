# pylint: disable=C0302
import copy
import itertools
import typing

import pytest

from . import utils


PROFILE_REQUEST = {
    'user': {'personal_phone_id': 'personal_phone_id_1'},
    'name': 'Насруло',
    'sourceid': 'cargo',
}

LOGISTIC_DISPATCH = 'logistic-dispatch'
UNITED_DISPATCH = 'united-dispatch'


def create_draft_request(
        claims: int = 1,
        taxi_requirements_json: dict = None,
        lookup_extra: dict = None,
        taxi_classes: typing.Optional[typing.List[str]] = None,
        due: str = None,
):
    sources: typing.List[dict] = []
    destinations: typing.List[dict] = []
    returns: typing.List[dict] = []
    segments: typing.List[dict] = []

    claim_point_seq = itertools.count(1)
    for idx in range(claims):
        segment_point_seq = itertools.count(1)
        segment_id = f'seg_{idx}'
        segments.append(
            {'claim_id': f'test_claim{idx}', 'segment_id': segment_id},
        )

        for point_id, point_list in zip(
                claim_point_seq, (sources, destinations, returns),
        ):
            point_list.append(
                {
                    'segment_id': segment_id,
                    'claim_point_id': point_id,
                    'waybill_point_id': (
                        f'{segment_id}_point_{next(segment_point_seq)}'
                    ),
                },
            )

    path = []
    for visit_order, point in enumerate(
            itertools.chain(sources, destinations, returns), 1,
    ):
        point['visit_order'] = visit_order
        path.append(point)

    if taxi_classes is None:
        taxi_classes = ['cargo', 'courier']
    reqs: typing.Dict[str, typing.Any] = {
        'taxi_classes': taxi_classes,
        'cargo_type': 'lcv_l',
    }
    if taxi_requirements_json:
        reqs.update(taxi_requirements_json)
    if lookup_extra:
        reqs.update({'lookup_extra': lookup_extra})

    request = {
        'waybill_ref': 'waybill-ref',
        'segments': segments,
        'path': path,
        'requirements': reqs,
    }

    return request


@pytest.fixture(name='assert_intapi_request')
def _assert_intapi_request(fetch_order):
    def run_assertions(
            expected_dispatch_type,
            response,
            intapi_draft_request,
            mock_intapi_orders_draft,
            expected_use_cargo_pricing=False,
    ):
        intapi_draft_request['cargo_ref_id'] = utils.OrderCargoRefId()

        actual_response = mock_intapi_orders_draft.handler.next_call()[
            'request'
        ].json
        assert actual_response == intapi_draft_request

        response_body = response.json()
        assert response_body == {
            'order_id': utils.UuidDashedString(),
            'provider_order_id': 'taxi_orderid',
        }

        order_doc = fetch_order(response_body['order_id'])
        assert order_doc.waybill_ref == 'waybill-ref'
        assert order_doc.provider_order_id == 'taxi_orderid'
        assert order_doc.use_cargo_pricing is expected_use_cargo_pricing

    return run_assertions


@pytest.fixture(autouse=True)
def mock_profile(mockserver):
    @mockserver.json_handler('/int-authproxy/v1/profile')
    def _profile(request):
        assert request.json == PROFILE_REQUEST
        return {
            'dont_ask_name': False,
            'experiments': [],
            'name': 'Насруло',
            'personal_phone_id': 'personal_phone_id_1',
            'user_id': 'taxi_user_id_1',
        }


@pytest.fixture(name='mock_intapi_nearestzone', autouse=True)
def _mock_intapi_nearestzone(mockserver):
    @mockserver.json_handler('/int-authproxy/v1/nearestzone')
    def mock(request):
        return {'nearest_zone': 'moscow'}

    return mock


@pytest.fixture(name='mock_personal_phones_retrieve', autouse=True)
def _mock_personal_phones_retrieve(mockserver):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def mock(request):
        assert request.json['id'] == 'receiver_phone_id'
        return {'id': request.json['id'], 'value': '+1234567890'}

    return mock


@pytest.fixture(name='mock_claims_full')
def _mock_claims_full(mockserver, load_json):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def mock(request):
        return load_json('cargo-claims/default.json')

    return mock


@pytest.fixture(name='mock_claims_full_delayed')
def _mock_claims_full_delayed(mockserver, load_json):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def mock(request):
        return load_json('cargo-claims/delayed.json')

    return mock


@pytest.fixture(name='mock_claims_full_new_offer_id')
def _mock_claims_full_new_offer_id(mockserver, load_json):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def mock(request):
        json_data = load_json('cargo-claims/default.json')
        json_data['taxi_offer']['offer_id'] = (
            'cargo-pricing/' + json_data['taxi_offer']['offer_id']
        )
        return json_data

    return mock


@pytest.fixture(name='mock_intapi_orders_draft')
def _mock_intapi_orders_draft(mockserver):
    @mockserver.json_handler('/int-authproxy/v1/orders/draft')
    def mock(request):
        if context.no_offer:
            assert 'offer' not in request.json
        if context.status_code == 200:
            return {'orderid': 'taxi_orderid'}
        return mockserver.make_response(
            status=context.status_code,
            json={'message': 'something', 'code': 'test_error'},
        )

    class Context:
        def __init__(self):
            self.status_code = 200
            self.handler = mock
            self.no_offer = False

    context = Context()

    return context


@pytest.fixture(name='mock_intapi_orders_draft_no_offer_id')
def _mock_intapi_orders_draft_no_offer_id(mock_intapi_orders_draft):
    mock_intapi_orders_draft.no_offer = True
    return mock_intapi_orders_draft


@pytest.fixture(name='control_lookup_ttl_config')
def _control_lookup_ttl_config(experiments3):
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_control_lookup_ttl',
        consumers=['cargo-dispatch/draft_taxi_order'],
        clauses=[
            {
                'title': 'has_special_requirements',
                'predicate': {
                    'type': 'contains',
                    'init': {
                        'value': 'courier_req1',
                        'arg_name': 'special_requirements',
                        'set_elem_type': 'string',
                    },
                },
                'value': {'lookup_ttl_sec': 123},
            },
            {
                'title': 'no_special_requirements',
                'predicate': {'type': 'true'},
                'value': {'lookup_ttl_sec': 17},
            },
        ],
        default_value={'lookup_ttl_sec': 22},
    )


def courier_spec_requirements():
    return {
        'class': 'courier',
        'special_requirements': [
            {'id': 'courier_req1'},
            {'id': 'courier_req2'},
        ],
    }


@pytest.fixture(name='waybill_with_courier_spec_requirements')
def _waybill_with_courier_spec_requirements(my_waybill_info):
    waybill = my_waybill_info['waybill']
    waybill['special_requirements']['virtual_tariffs'].append(
        courier_spec_requirements(),
    )


@pytest.fixture(name='intapi_draft_request_with_lookup_ttl')
def _intapi_draft_request_with_lookup_ttl(load_json):
    def _wrapper(lookup_ttl, classes, requirements):
        intapi_draft_request = load_json('intapi_draft_request.json')
        intapi_draft_request['virtual_tariffs'].append(
            courier_spec_requirements(),
        )
        intapi_draft_request['lookup_ttl'] = lookup_ttl
        intapi_draft_request['class'] = classes
        intapi_draft_request['requirements'] = requirements
        return intapi_draft_request

    return _wrapper


@pytest.mark.parametrize(
    ('router_id', 'expected_dispatch_type'),
    (
        ('logistic-dispatch', 'logistic-dispatcher'),
        ('fallback_router', None),
        ('grocery_manual_dispatch_cargo_router', 'forced_performer'),
        ('cargo_same_day_delivery_router', 'forced_performer'),
        ('united-dispatch', None),
        pytest.param('united-dispatch', 'united-dispatch'),
    ),
)
@pytest.mark.parametrize('claims_count', [1, 2])
@pytest.mark.parametrize(
    'new_dispatch_classes, new_dispatch_requirements',
    [
        pytest.param(
            False,
            True,
            id='new_dispatch_requirements',
            marks=pytest.mark.config(
                CARGO_DRAGON_DISPATCH_REQUIREMENTS_ENABLED={
                    'dispatch-taxi-classes': False,
                    'dispatch-taxi-requirements': True,
                },
            ),
        ),
        pytest.param(
            True,
            False,
            id='new_dispatch_classes',
            marks=pytest.mark.config(
                CARGO_DRAGON_DISPATCH_REQUIREMENTS_ENABLED={
                    'dispatch-taxi-classes': True,
                    'dispatch-taxi-requirements': False,
                },
            ),
        ),
        pytest.param(False, False, id='old_claims_requirements'),
    ],
)
@pytest.mark.parametrize(
    'lookup_extra',
    [None, {'intent': 'grocery-manual', 'performer_id': 'dbid_uuid'}],
)
async def test_basic(
        taxi_cargo_orders,
        mock_intapi_nearestzone,
        mock_personal_phones_retrieve,
        mock_claims_full,
        mock_intapi_orders_draft,
        assert_intapi_request,
        load_json,
        fetch_order,
        default_order_id,
        router_id,
        expected_dispatch_type,
        claims_count,
        my_waybill_info,
        new_dispatch_requirements: bool,
        new_dispatch_classes: bool,
        mock_waybill_info,
        lookup_extra,
):
    taxi_requirements_json = None
    if new_dispatch_requirements:
        taxi_requirements_json = {'some_requirement': 'requirement'}

    draft_request = create_draft_request(
        claims=claims_count,
        taxi_requirements_json=taxi_requirements_json,
        lookup_extra=lookup_extra,
    )
    if router_id:
        draft_request['router_id'] = router_id

    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=draft_request,
    )
    assert response.status_code == 200

    assert mock_waybill_info.times_called == 1
    assert mock_claims_full.times_called == 1
    assert mock_intapi_orders_draft.handler.times_called == 1
    assert mock_personal_phones_retrieve.times_called == 1

    intapi_draft_request = load_json('intapi_draft_request.json')
    if expected_dispatch_type:
        intapi_draft_request['dispatch_type'] = expected_dispatch_type
    if new_dispatch_requirements:
        intapi_draft_request['requirements'].update(taxi_requirements_json)
    if lookup_extra:
        intapi_draft_request['lookup_extra'] = lookup_extra

    # request points are the same for each claim
    route_for_claim = copy.deepcopy(intapi_draft_request['route'])
    intapi_draft_request['route'] = []
    for point in route_for_claim:
        for _ in range(claims_count):
            intapi_draft_request['route'].append(point)

    # check requirements source (fix in CARGODEV-2055)
    if not new_dispatch_classes:
        intapi_draft_request['class'] = ['cargo']
    if not new_dispatch_requirements:
        intapi_draft_request['requirements'] = {'cargo_type': 'lcv_m'}

    intapi_draft_request['cargo_ref_id'] = utils.OrderCargoRefId()
    assert_intapi_request(
        expected_dispatch_type,
        response,
        intapi_draft_request,
        mock_intapi_orders_draft,
    )


@pytest.mark.parametrize(
    ('router_id', 'expected_dispatch_type'),
    (('fallback_router', 'forced_performer'),),
)
@pytest.mark.parametrize(
    'lookup_extra', [{'intent': 'scooters_ops', 'performer_id': 'dbid_uuid'}],
)
async def test_scooters(
        taxi_cargo_orders,
        mock_waybill_info,
        mock_personal_phones_retrieve,
        mock_claims_full_new_offer_id,
        mock_intapi_orders_draft,
        assert_intapi_request,
        expected_dispatch_type,
        router_id,
        load_json,
        lookup_extra,
):
    draft_request = create_draft_request(lookup_extra=lookup_extra)
    draft_request['router_id'] = router_id

    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=draft_request,
    )
    assert response.status_code == 200

    assert mock_waybill_info.times_called == 1
    assert mock_claims_full_new_offer_id.times_called == 1
    assert mock_intapi_orders_draft.handler.times_called == 1
    assert mock_personal_phones_retrieve.times_called == 1

    intapi_draft_request = load_json('intapi_draft_request.json')
    intapi_draft_request['dispatch_type'] = expected_dispatch_type
    intapi_draft_request['lookup_extra'] = lookup_extra
    intapi_draft_request['requirements'] = {'cargo_type': 'lcv_m'}
    intapi_draft_request['class'] = ['cargo']
    intapi_draft_request['cargo_ref_id'] = utils.OrderCargoRefId()

    assert_intapi_request(
        expected_dispatch_type,
        response,
        intapi_draft_request,
        mock_intapi_orders_draft,
        expected_use_cargo_pricing=True,
    )


@pytest.mark.parametrize(
    ('router_id', 'expected_dispatch_type'),
    (('default_router', 'logistic-dispatcher'), ('fallback_router', None)),
)
@pytest.mark.config(
    CARGO_DRAGON_DISPATCH_REQUIREMENTS_ENABLED={
        'dispatch-taxi-classes': True,
        'dispatch-taxi-requirements': True,
    },
)
async def test_basic_no_offer(
        taxi_cargo_orders,
        mock_waybill_info,
        mock_intapi_nearestzone,
        mock_personal_phones_retrieve,
        mock_claims_full_new_offer_id,
        mock_intapi_orders_draft_no_offer_id,
        assert_intapi_request,
        load_json,
        fetch_order,
        router_id,
        expected_dispatch_type,
        my_waybill_info,
):
    draft_request = create_draft_request().copy()
    if router_id:
        draft_request['router_id'] = router_id

    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=draft_request,
    )
    assert response.status_code == 200

    assert mock_waybill_info.times_called == 1
    assert mock_claims_full_new_offer_id.times_called == 1
    assert mock_intapi_orders_draft_no_offer_id.handler.times_called == 1
    assert mock_personal_phones_retrieve.times_called == 1

    intapi_draft_request = load_json('intapi_draft_request.json')
    assert_intapi_request(
        expected_dispatch_type,
        response,
        intapi_draft_request,
        mock_intapi_orders_draft_no_offer_id,
        expected_use_cargo_pricing=True,
    )


async def test_called_twice(
        taxi_cargo_orders,
        mock_waybill_info,
        mock_intapi_nearestzone,
        mock_personal_phones_retrieve,
        mock_claims_full,
        mock_intapi_orders_draft,
        my_waybill_info,
):
    draft_request = create_draft_request()
    for _ in range(2):
        response = await taxi_cargo_orders.post(
            '/v1/order/draft', json=draft_request,
        )
        assert response.status_code == 200

    assert mock_waybill_info.times_called == 1
    assert mock_claims_full.times_called == 1
    assert mock_intapi_orders_draft.handler.times_called == 1
    assert mock_personal_phones_retrieve.times_called == 1
    assert mock_intapi_orders_draft.handler.times_called == 1


async def test_duplicate_order_draft(
        taxi_cargo_orders,
        mock_waybill_info,
        mock_intapi_nearestzone,
        mock_personal_phones_retrieve,
        mock_claims_full,
        mock_intapi_orders_draft,
        my_waybill_info,
):
    for _ in range(1, 3):
        draft_request = create_draft_request()

        response = await taxi_cargo_orders.post(
            '/v1/order/draft', json=draft_request,
        )
        assert response.status_code == 200

    assert mock_waybill_info.times_called == 1
    assert mock_claims_full.times_called == 1
    assert mock_intapi_orders_draft.handler.times_called == 1
    assert mock_personal_phones_retrieve.times_called == 1
    assert mock_intapi_orders_draft.handler.times_called == 1


@pytest.mark.config(CARGO_DRAGON_OPTIONAL_TAXI_OFFER=False)
async def test_optional_offer(
        taxi_cargo_orders,
        mock_intapi_nearestzone,
        mock_personal_phones_retrieve,
        mock_claims_full,
        mock_intapi_orders_draft,
        my_waybill_info,
):
    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(),
    )
    assert response.status_code == 200

    assert (
        'offer'
        not in mock_intapi_orders_draft.handler.next_call()['request'].json
    )


@pytest.mark.config(CARGO_DRAGON_OPTIONAL_TAXI_OFFER=False)
async def test_just_partners_payment(
        taxi_cargo_orders,
        mock_intapi_orders_draft,
        mockserver,
        load_json,
        my_waybill_info,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _mock(request):
        claim = load_json('cargo-claims/default.json')
        claim['just_client_payment'] = True
        claim['is_new_logistic_contract'] = True
        return claim

    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(),
    )
    assert response.status_code == 200

    result = mock_intapi_orders_draft.handler.next_call()['request'].json
    assert result['just_partner_payments']
    assert result['check_new_logistic_contract']


def param_expect_offer(allow_offer):
    return pytest.param(
        allow_offer,
        marks=pytest.mark.experiments3(
            is_config=True,
            name='cargo_orders_dragon_draft',
            consumers=['cargo-orders/dragon-draft'],
            clauses=[],
            default_value={'allow_offer': allow_offer},
        ),
    )


@pytest.mark.now('2020-01-27T15:45:00+00:00')
async def test_ld_waybill_delayed(
        taxi_cargo_orders,
        mock_intapi_nearestzone,
        mock_personal_phones_retrieve,
        mock_claims_full_delayed,
        mock_intapi_orders_draft,
        my_waybill_info,
):
    """
    Config CARGO_ORDERS_FORCE_SKIP_DUE_FOR_LD_WAYBILLS with default value
    (disabled)
    """
    my_waybill_info['waybill']['router_id'] = LOGISTIC_DISPATCH
    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(),
    )
    assert response.status_code == 200

    order_draft = mock_intapi_orders_draft.handler.next_call()['request'].json
    assert order_draft['due'] == '2020-01-27T19:40:00+00:00'
    assert order_draft['is_delayed']


@pytest.mark.config(CARGO_ORDERS_FORCE_SKIP_DUE_FOR_LD_WAYBILLS=True)
@pytest.mark.now('2020-01-27T15:45:00+00:00')
async def test_ld_waybill_soon(
        taxi_cargo_orders,
        mock_intapi_nearestzone,
        mock_personal_phones_retrieve,
        mock_claims_full_delayed,
        mock_intapi_orders_draft,
        my_waybill_info,
):
    """
    Config CARGO_ORDERS_FORCE_SKIP_DUE_FOR_LD_WAYBILLS enabled
    Force create soon taxi order
    """
    my_waybill_info['waybill']['router_id'] = LOGISTIC_DISPATCH
    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(),
    )
    assert response.status_code == 200

    order_draft = mock_intapi_orders_draft.handler.next_call()['request'].json
    assert 'due' not in order_draft
    assert not order_draft['is_delayed']


async def test_error_stored(
        taxi_cargo_orders,
        mock_waybill_info,
        mock_intapi_nearestzone,
        mock_personal_phones_retrieve,
        mock_claims_full,
        mock_intapi_orders_draft,
        my_waybill_info,
        fetch_taxi_order_error,
):
    mock_intapi_orders_draft.status_code = 406
    draft_request = create_draft_request()
    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=draft_request,
    )
    assert response.status_code != 200

    error = fetch_taxi_order_error()
    assert error['message'] == 'test_error'
    assert error['reason'] == 'DRAFT_ERROR'


async def test_429_draft(
        taxi_cargo_orders,
        mock_waybill_info,
        mock_intapi_nearestzone,
        mock_personal_phones_retrieve,
        mock_claims_full,
        mock_intapi_orders_draft,
        my_waybill_info,
):
    mock_intapi_orders_draft.status_code = 429
    draft_request = create_draft_request()
    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=draft_request,
    )
    assert response.status_code == 429


@pytest.mark.parametrize(
    'payment_type, payment_method_id, enable_client_driver_preset_calc_differ',
    [
        ('corp', 'corp-123', True),
        ('card', 'card-123', True),
        ('corp', 'corp-123', False),
        ('card', 'card-123', False),
    ],
)
async def test_cargo_c2c_order(
        taxi_cargo_orders,
        mockserver,
        load_json,
        mock_intapi_nearestzone,
        mock_personal_phones_retrieve,
        mock_intapi_orders_draft,
        my_waybill_info,
        fetch_order,
        payment_type,
        payment_method_id,
        taxi_config,
        enable_client_driver_preset_calc_differ,
):
    taxi_config.set_values(
        {
            'CARGO_ORDERS_ENABLE_NONDECOUPLING_OFFER_PRICES_DIFFERENCE': (
                enable_client_driver_preset_calc_differ
            ),
        },
    )
    await taxi_cargo_orders.invalidate_caches()

    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _mock_cargo_claims(request):
        response = load_json('cargo-claims/default.json')
        response.pop('corp_client_id')
        response['yandex_uid'] = 'some_yandex_uid'
        response['origin_info'] = {'origin': 'yandexgo'}
        response['c2c_data'] = {
            'payment_method_id': payment_method_id,
            'payment_type': payment_type,
            'cargo_c2c_order_id': 'cargo_c2c_order_id_1',
        }

        return response

    @mockserver.json_handler('/cargo-c2c/v1/intiator-client-order')
    def _mosck_c2c(request):
        assert request.json == {'cargo_c2c_order_id': 'cargo_c2c_order_id_1'}
        return {'user_id': 'some_user_id', 'user_agent': 'some_user_agent'}

    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(),
    )
    assert response.status_code == 200

    order = fetch_order(response.json()['order_id'])
    is_decoupling = payment_type == 'corp'
    if enable_client_driver_preset_calc_differ or is_decoupling:
        assert not order.presetcar_calc_id
    else:
        # oldway (same calc for client and driver for c2c orders)
        assert order.presetcar_calc_id == 'taxi_offer_id_1'
    assert order.nondecoupling_client_offer_calc_id == 'taxi_offer_id_1'

    draft_request = mock_intapi_orders_draft.handler.next_call()['request']
    assert draft_request.json['id'] == 'some_user_id'
    assert draft_request.headers['User-Agent'] == 'some_user_agent'


async def test_cargo_phoenix_order(
        taxi_cargo_orders,
        mockserver,
        load_json,
        mock_intapi_nearestzone,
        mock_personal_phones_retrieve,
        mock_intapi_orders_draft,
        my_waybill_info,
        fetch_order,
):
    card_id = 'card-xxx'

    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _mock_cargo_claims(request):
        response = load_json('cargo-claims/default.json')
        response['features'] = [{'id': 'phoenix_claim'}]
        response['pricing_payment_methods'] = {
            'card': {
                'cardstorage_id': card_id,
                'owner_yandex_uid': 'yandex_uid-yyy',
            },
        }
        return response

    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(),
    )
    assert response.status_code == 200

    draft_request = mock_intapi_orders_draft.handler.next_call()['request']
    assert draft_request.json['payment'] == {
        'payment_method_id': card_id,
        'type': 'card',
    }
    assert draft_request.json['delivery']['is_phoenix_payment_flow'] is True


@pytest.mark.parametrize(
    'payment_scheme, payment_method_id',
    [
        ('agent', 'cargocorp:{}:card:{}:{}'),
        ('decoupling', 'cargocorp:{}:balance:123:contract:456'),
    ],
)
async def test_cargo_c2c_phoenix_order(
        taxi_cargo_orders,
        mockserver,
        load_json,
        mock_intapi_nearestzone,
        mock_personal_phones_retrieve,
        mock_intapi_orders_draft,
        my_waybill_info,
        fetch_order,
        payment_scheme,
        payment_method_id,
):
    yandex_uid = 'some_yandex_uid'
    claims_full_response = load_json('cargo-claims/default.json')
    corp_client_id = claims_full_response['corp_client_id']
    if payment_scheme == 'agent':
        card_id = 'card-xxx'
        payment_method_id = payment_method_id.format(
            corp_client_id, yandex_uid, card_id,
        )
        expected_taxi_payment_method_id = card_id
        expected_taxi_payment_type = 'card'
    else:
        payment_method_id = payment_method_id.format(corp_client_id)
        expected_taxi_payment_method_id = 'corp-' + corp_client_id
        expected_taxi_payment_type = 'corp'
    c2c_data = {
        'payment_method_id': payment_method_id,
        'payment_type': 'cargocorp',
        'cargo_c2c_order_id': 'cargo_c2c_order_id_1',
    }

    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _mock_cargo_claims(request):
        response = claims_full_response
        response['yandex_uid'] = yandex_uid
        response['origin_info'] = {'origin': 'yandexgo'}
        response['c2c_data'] = c2c_data
        if payment_scheme == 'agent':
            response['features'] = [{'id': 'phoenix_claim'}]
            response['pricing_payment_methods'] = {
                'card': {
                    'cardstorage_id': card_id,
                    'owner_yandex_uid': yandex_uid,
                },
            }
        return response

    @mockserver.json_handler('/cargo-c2c/v1/intiator-client-order')
    def _mock_c2c(request):
        assert request.json == {'cargo_c2c_order_id': 'cargo_c2c_order_id_1'}
        return {'user_id': 'some_user_id', 'user_agent': 'some_user_agent'}

    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(),
    )
    assert response.status_code == 200

    draft_request = mock_intapi_orders_draft.handler.next_call()['request']
    assert draft_request.json['payment'] == {
        'payment_method_id': expected_taxi_payment_method_id,
        'type': expected_taxi_payment_type,
    }
    if payment_scheme == 'agent':
        assert (
            draft_request.json['delivery']['is_phoenix_payment_flow'] is True
        )
    else:
        assert 'is_phoenix_payment_flow' not in draft_request.json['delivery']
    assert _mock_c2c.times_called == 1


@pytest.mark.config(CARGO_DISPATCH_ENABLE_LOOKUP_TTL_CONTROL=True)
@pytest.mark.config(
    CARGO_DRAGON_DISPATCH_REQUIREMENTS_ENABLED={
        'dispatch-taxi-classes': False,
        'dispatch-taxi-requirements': True,
    },
)
async def test_no_matched_spec_requirements_in_lookup_ttl_config(
        taxi_cargo_orders,
        mock_intapi_orders_draft,
        mock_claims_full,
        assert_intapi_request,
        intapi_draft_request_with_lookup_ttl,
        waybill_with_courier_spec_requirements,
        control_lookup_ttl_config,
        experiments3,
):
    exp3_recorder = experiments3.record_match_tries('cargo_control_lookup_ttl')

    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(),
    )
    assert response.status_code == 200
    assert mock_intapi_orders_draft.handler.times_called == 1

    intapi_draft_request = intapi_draft_request_with_lookup_ttl(
        lookup_ttl=17, classes=['cargo'], requirements={'cargo_type': 'lcv_l'},
    )

    assert_intapi_request(
        '', response, intapi_draft_request, mock_intapi_orders_draft,
    )

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    assert match_tries[0].kwargs['special_requirements'] == ['cargo_eds']


@pytest.mark.config(CARGO_DISPATCH_ENABLE_LOOKUP_TTL_CONTROL=True)
@pytest.mark.config(
    CARGO_DRAGON_DISPATCH_REQUIREMENTS_ENABLED={
        'dispatch-taxi-classes': True,
        'dispatch-taxi-requirements': False,
    },
)
async def test_matched_spec_requirements_in_lookup_ttl_config(
        taxi_cargo_orders,
        mock_intapi_orders_draft,
        mock_claims_full,
        assert_intapi_request,
        intapi_draft_request_with_lookup_ttl,
        waybill_with_courier_spec_requirements,
        control_lookup_ttl_config,
        experiments3,
):
    exp3_recorder = experiments3.record_match_tries('cargo_control_lookup_ttl')

    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(),
    )
    assert response.status_code == 200
    assert mock_intapi_orders_draft.handler.times_called == 1

    intapi_draft_request = intapi_draft_request_with_lookup_ttl(
        lookup_ttl=123,
        classes=['cargo', 'courier'],
        requirements={'cargo_type': 'lcv_m'},
    )

    assert_intapi_request(
        '', response, intapi_draft_request, mock_intapi_orders_draft,
    )

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    assert set(match_tries[0].kwargs['special_requirements']) == set(
        ['cargo_eds', 'courier_req1', 'courier_req2'],
    )


async def test_post_payment_comment(
        taxi_cargo_orders,
        mock_intapi_nearestzone,
        mock_personal_phones_retrieve,
        mock_claims_full,
        mock_intapi_orders_draft,
        waybill_state,
        exp_cargo_orders_post_payment_flow,
):
    """
        Check post_payment reminder is passed on order/draft.
    """
    waybill_state.set_post_payment()

    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(),
    )
    assert response.status_code == 200

    order_draft = mock_intapi_orders_draft.handler.next_call()['request'].json
    assert (
        order_draft['comment']
        == 'Заказ с наложенным платежом.\nЗаказ с подтверждением по СМС.'
    )


@pytest.mark.parametrize(
    ('intapi_code', 'metric_name'),
    (
        (400, 'response-400'),
        (401, 'response-401'),
        (429, 'response-429'),
        (406, 'response-406'),
        (500, 'unexpected-exception'),
    ),
)
async def test_error_metrics(
        taxi_cargo_orders,
        taxi_cargo_orders_monitor,
        mockserver,
        load_json,
        intapi_code: int,
        metric_name: str,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        return load_json('cargo-claims/default.json')

    @mockserver.json_handler('/int-authproxy/v1/orders/draft')
    def _intapi_orders_draft(request):
        return mockserver.make_response(
            status=intapi_code, json={'code': 'test_error'},
        )

    await taxi_cargo_orders.tests_control(reset_metrics=True)
    await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(),
    )
    statistics = await taxi_cargo_orders_monitor.get_metric(
        'cargo-orders-client',
    )

    assert statistics['int-authproxy']['orders-draft'][metric_name] == 1


@pytest.mark.config(CARGO_ORDERS_PROCESSING_ORDER_DRAFT_403=True)
@pytest.mark.parametrize(
    ('status_code', 'blocked'), ((400, True), (500, False)),
)
async def test_draft_403(
        taxi_cargo_orders,
        taxi_cargo_orders_monitor,
        mockserver,
        load_json,
        status_code: int,
        blocked: bool,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        return load_json('cargo-claims/default.json')

    @mockserver.json_handler('/int-authproxy/v1/orders/draft')
    def _intapi_orders_draft(request):
        json = {'type': ''}
        if blocked:
            json['blocked'] = '2022-07-24T15:19:17+0000'
        return mockserver.make_response(status=403, json=json)

    await taxi_cargo_orders.tests_control(reset_metrics=True)
    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(),
    )

    assert response.status_code == status_code
    statistics = await taxi_cargo_orders_monitor.get_metric(
        'cargo-orders-client',
    )

    assert statistics['int-authproxy']['orders-draft']['response-403'] == (
        status_code == 400
    )


async def test_response_200_metric(
        taxi_cargo_orders, taxi_cargo_orders_monitor, mockserver, load_json,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        return load_json('cargo-claims/default.json')

    @mockserver.json_handler('/int-authproxy/v1/orders/draft')
    def _intapi_orders_draft(request):
        return mockserver.make_response(
            status=200, json={'orderid': 'some_id'},
        )

    await taxi_cargo_orders.tests_control(reset_metrics=True)
    await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(),
    )
    statistics = await taxi_cargo_orders_monitor.get_metric(
        'cargo-orders-client',
    )

    assert statistics['int-authproxy']['orders-draft']['response-200'] == 1


@pytest.mark.parametrize(
    'logistic_group, performers_restriction_type, zone_group',
    (
        ('28', 'group_only', {'required_ids': ['28'], 'allow_missing': False}),
        (
            '28',
            'no_restrictions',
            {'required_ids': ['28'], 'allow_missing': True},
        ),
        ('28', None, {'required_ids': ['28'], 'allow_missing': True}),
        (None, 'group_only', None),
        (None, 'no_restrictions', {'required_ids': [], 'allow_missing': True}),
        (None, None, {'required_ids': [], 'allow_missing': True}),
    ),
)
@pytest.mark.config(
    CARGO_ORDERS_SHIFT_CLASSES={'shift_classes': ['eda']},
    CARGO_ORDERS_DRAFT_ENABLE_SHIFT=True,
    CARGO_DRAGON_DISPATCH_REQUIREMENTS_ENABLED={
        'dispatch-taxi-classes': True,
        'dispatch-taxi-requirements': True,
    },
)
async def test_shifts_and_logistic_groups(
        taxi_cargo_orders,
        mock_intapi_orders_draft,
        mock_waybill_info,
        assert_intapi_request,
        mock_claims_full,
        load_json,
        mock_segments_bulk_info,
        logistic_group: str,
        performers_restriction_type: str,
        zone_group: dict,
):
    soft_requirements = [
        {
            'performers_restriction_type': performers_restriction_type,
            'logistic_group': logistic_group,
            'shift_type': 'eats',
            'type': 'performer_group',
        },
    ]
    mock_segments_bulk_info.set_taxi_classes(['eda'])
    mock_segments_bulk_info.set_soft_requirements(soft_requirements)
    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(taxi_classes=['eda']),
    )
    assert response.status_code == 200
    assert mock_intapi_orders_draft.handler.times_called == 1

    request = mock_intapi_orders_draft.handler.next_call()['request'].json
    if zone_group is not None:
        assert request['shift']['zone_group'] == zone_group
    else:
        assert request['shift'] == {'type': 'eats'}


@pytest.mark.config(
    CARGO_ORDERS_SHIFT_CLASSES={'shift_classes': ['eda']},
    CARGO_ORDERS_DRAFT_ENABLE_SHIFT=True,
    CARGO_DRAGON_DISPATCH_REQUIREMENTS_ENABLED={
        'dispatch-taxi-classes': True,
        'dispatch-taxi-requirements': True,
    },
)
async def test_default_shift_type(
        taxi_cargo_orders,
        mock_intapi_orders_draft,
        mock_waybill_info,
        assert_intapi_request,
        mock_claims_full,
        load_json,
        mock_segments_bulk_info,
):
    soft_requirements = [
        {
            'logistic_group': '2032',
            'meta_group': 'lavka',
            'performers_restriction_type': 'group_only',
            'type': 'performer_group',
        },
    ]
    mock_segments_bulk_info.set_taxi_classes(['eda'])
    mock_segments_bulk_info.set_soft_requirements(soft_requirements)
    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(taxi_classes=['eda']),
    )
    assert response.status_code == 200
    assert mock_intapi_orders_draft.handler.times_called == 1

    request = mock_intapi_orders_draft.handler.next_call()['request'].json
    assert 'shift' in request
    assert request['shift'] == {
        'type': 'eats',
        'zone_group': {'allow_missing': False, 'required_ids': ['2032']},
    }


@pytest.mark.config(
    CARGO_ORDERS_SHIFT_CLASSES={'shift_classes': ['eda', 'scooters']},
    CARGO_DRAGON_DISPATCH_REQUIREMENTS_ENABLED={
        'dispatch-taxi-classes': True,
        'dispatch-taxi-requirements': True,
    },
    CARGO_ORDERS_DRAFT_ENABLE_SHIFT=True,
)
@pytest.mark.parametrize(
    'shift_type, taxi_class, should_fill_shift',
    (
        ('eats', 'eda', True),
        ('grocery', 'lavka', False),
        ('grocery', 'eda', True),
    ),
)
async def test_fill_shift(
        taxi_cargo_orders,
        mock_intapi_orders_draft,
        mock_waybill_info,
        assert_intapi_request,
        mock_claims_full,
        load_json,
        mock_segments_bulk_info,
        shift_type: str,
        taxi_class: str,
        should_fill_shift: bool,
):
    soft_requirements = [
        {
            'performers_restriction_type': 'group_only',
            'logistic_group': '28',
            'shift_type': shift_type,
            'type': 'performer_group',
        },
    ]
    mock_segments_bulk_info.set_taxi_classes([taxi_class])
    mock_segments_bulk_info.set_soft_requirements(soft_requirements)
    response = await taxi_cargo_orders.post(
        '/v1/order/draft',
        json=create_draft_request(taxi_classes=[taxi_class]),
    )
    assert response.status_code == 200
    assert mock_intapi_orders_draft.handler.times_called == 1

    request = mock_intapi_orders_draft.handler.next_call()['request'].json
    if should_fill_shift:
        assert request['shift'] == {
            'type': shift_type,
            'zone_group': {'allow_missing': False, 'required_ids': ['28']},
        }
    else:
        assert 'shift' not in request


@pytest.mark.config(
    CARGO_DRAGON_DISPATCH_REQUIREMENTS_ENABLED={
        'dispatch-taxi-classes': True,
        'dispatch-taxi-requirements': True,
    },
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={
        'corp_client_id_1_______32symbols': 'eats',
    },
    CARGO_ORDERS_EATS_ORDER_DETAILS_TRANSFER_ENABLED=True,
)
async def test_eats_fallback_order_data_transferred(
        taxi_cargo_orders,
        mock_intapi_orders_draft,
        mock_waybill_info,
        mock_claims_full,
        load_json,
        mock_segments_bulk_info,
):
    soft_requirements = [
        {
            'performers_restriction_type': 'group_only',
            'logistic_group': 'test_logistic_group',
            'shift_type': 'eats',
            'type': 'performer_group',
        },
    ]
    mock_segments_bulk_info.set_custom_context(
        load_json('cargo-claims/eats_custom_context.json'),
    )
    mock_segments_bulk_info.set_taxi_classes(['eda'])
    mock_segments_bulk_info.set_soft_requirements(soft_requirements)
    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(taxi_classes=['eda']),
    )
    assert response.status_code == 200
    assert mock_intapi_orders_draft.handler.times_called == 1

    request = mock_intapi_orders_draft.handler.next_call()['request'].json
    assert request['eats_batch'] == [
        {
            'context': {
                'cooking_time': 10,
                'items_cost': {'currency': 'USD', 'value': '150.5'},
                'delivery_cost': {'currency': 'RUB', 'value': '129'},
                'delivery_flow_type': 'courier',
                'device_id': 'test_device_id',
                'has_slot': True,
                'is_asap': True,
                'is_fast_food': False,
                'logistic_group': soft_requirements[0]['logistic_group'],
                'order_confirmed_at': '2021-10-29T08:00:57+00:00',
                'order_flow_type': 'native',
                'order_id': 123,
                'order_must_be_delivered_at': '2021-10-29T09:00:57+00:00',
                'promise_max_at': '2021-10-29T10:00:57+00:00',
                'promise_min_at': '2021-10-29T11:00:57+00:00',
                'region_id': 111,
                'send_to_place_at': '2021-10-29T12:00:57+00:00',
                'order_cancel_at': '2021-10-29T07:00:57+00:00',
                'weight': '3.5',
                'sender_is_picker': False,
                'place_id': 999,
                'route_to_client': {
                    'auto': {'distance': 243, 'is_precise': False, 'time': 50},
                    'pedestrian': {
                        'distance': 123,
                        'is_precise': True,
                        'time': 120,
                    },
                    'transit': {
                        'distance': 153,
                        'is_precise': True,
                        'time': 100,
                    },
                },
            },
        },
    ]


@pytest.mark.config(
    CARGO_DRAGON_DISPATCH_REQUIREMENTS_ENABLED={
        'dispatch-taxi-classes': True,
        'dispatch-taxi-requirements': True,
    },
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={
        'corp_client_id_1_______32symbols': 'eats',
    },
    CARGO_ORDERS_EATS_ORDER_DETAILS_TRANSFER_ENABLED=False,
)
async def test_eats_fallback_order_data_not_transferred_by_config(
        taxi_cargo_orders,
        mock_intapi_orders_draft,
        mock_waybill_info,
        mock_claims_full,
        load_json,
        mock_segments_bulk_info,
):
    soft_requirements = [
        {
            'performers_restriction_type': 'group_only',
            'logistic_group': 'test_logistic_group',
            'shift_type': 'eats',
            'type': 'performer_group',
        },
    ]
    mock_segments_bulk_info.set_custom_context(
        load_json('cargo-claims/eats_custom_context.json'),
    )
    mock_segments_bulk_info.set_taxi_classes(['eda'])
    mock_segments_bulk_info.set_soft_requirements(soft_requirements)
    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(taxi_classes=['eda']),
    )
    assert response.status_code == 200
    assert mock_intapi_orders_draft.handler.times_called == 1

    request = mock_intapi_orders_draft.handler.next_call()['request'].json
    assert 'eats_batch' not in request


@pytest.mark.config(
    CARGO_DRAGON_DISPATCH_REQUIREMENTS_ENABLED={
        'dispatch-taxi-classes': True,
        'dispatch-taxi-requirements': True,
    },
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={
        'corp_client_id_1_______32symbols': 'not_eats',
    },
)
async def test_eats_fallback_order_data_not_transferred_for_corp_id(
        taxi_cargo_orders,
        mock_intapi_orders_draft,
        mock_waybill_info,
        mock_claims_full,
        load_json,
        mock_segments_bulk_info,
):
    soft_requirements = [
        {
            'performers_restriction_type': 'group_only',
            'logistic_group': 'test_logistic_group',
            'shift_type': 'eats',
            'type': 'performer_group',
        },
    ]
    mock_segments_bulk_info.set_custom_context(
        load_json('cargo-claims/eats_custom_context.json'),
    )
    mock_segments_bulk_info.set_taxi_classes(['eda'])
    mock_segments_bulk_info.set_soft_requirements(soft_requirements)
    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(taxi_classes=['eda']),
    )
    assert response.status_code == 200
    assert mock_intapi_orders_draft.handler.times_called == 1

    request = mock_intapi_orders_draft.handler.next_call()['request'].json
    assert 'eats_batch' not in request


@pytest.mark.parametrize('forced_soon', [False, True])
@pytest.mark.now('2020-01-27T15:45:00+00:00')
async def test_forced_soon(
        taxi_cargo_orders,
        mock_intapi_nearestzone,
        mock_personal_phones_retrieve,
        mock_claims_full_delayed,
        mock_intapi_orders_draft,
        my_waybill_info,
        forced_soon,
):
    my_waybill_info['waybill']['router_id'] = UNITED_DISPATCH
    my_waybill_info['waybill']['taxi_order_requirements'][
        'forced_soon'
    ] = forced_soon
    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(),
    )
    assert response.status_code == 200

    order_draft = mock_intapi_orders_draft.handler.next_call()['request'].json
    if not forced_soon:
        assert order_draft['due'] == '2020-01-27T19:40:00+00:00'
        assert order_draft['is_delayed']
    else:
        assert 'due' not in order_draft
        assert not order_draft['is_delayed']


@pytest.mark.parametrize(
    'custom_context_assign_rover'
    ',client_requirements_assign_robot'
    ',expected_include_rovers',
    [
        (None, None, False),
        (None, False, False),
        (False, None, False),
        (None, True, True),
        (True, None, True),
        (False, False, False),
        (False, True, True),
        (True, False, True),
        (True, True, True),
    ],
)
async def test_delivery_include_rovers(
        custom_context_assign_rover,
        client_requirements_assign_robot,
        expected_include_rovers,
        taxi_cargo_orders,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        claim = load_json('cargo-claims/default.json')
        if custom_context_assign_rover is not None:
            if 'custom_context' not in claim:
                claim['custom_context'] = {}
            if 'delivery_flags' not in claim['custom_context']:
                claim['custom_context']['delivery_flags'] = {}
            claim['custom_context']['delivery_flags'][
                'assign_rover'
            ] = custom_context_assign_rover
        if client_requirements_assign_robot is not None:
            if 'client_requirements' not in claim:
                claim['client_requirements'] = {}
            claim['client_requirements'] = {
                'assign_robot': client_requirements_assign_robot,
                'taxi_class': 'cargo',
            }
        return claim

    @mockserver.json_handler('/int-authproxy/v1/orders/draft')
    def orders_draft(request):
        assert request.json
        assert (
            request.json['delivery']['include_rovers']
            == expected_include_rovers
        )
        return {'orderid': 'taxi_order_id_1'}

    await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(),
    )

    assert orders_draft.has_calls


@pytest.mark.parametrize('is_same_day', [False, True])
@pytest.mark.config(CARGO_DISPATCH_ENABLE_LOOKUP_TTL_CONTROL=True)
async def test_same_day_ttl_control(
        taxi_cargo_orders,
        mock_intapi_orders_draft,
        control_lookup_ttl_config,
        experiments3,
        mockserver,
        load_json,
        is_same_day,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _mock_claims_full(request):
        return load_json('cargo-claims/default.json')

    exp3_recorder = experiments3.record_match_tries('cargo_control_lookup_ttl')

    draft_request = create_draft_request()
    if is_same_day:
        draft_request['router_id'] = 'cargo_same_day_delivery_router'

    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=draft_request,
    )
    assert response.status_code == 200
    assert _mock_claims_full.times_called == 1
    assert mock_intapi_orders_draft.handler.times_called == 1

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    assert match_tries[0].kwargs['is_same_day_order'] == is_same_day


async def test_c2c_alternative_type(
        taxi_cargo_orders, mock_intapi_orders_draft, mockserver, load_json,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _mock_cargo_claims(request):
        response = load_json('cargo-claims/default.json')
        response['features'] = [{'id': 'combo_order'}]
        return response

    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(),
    )
    assert response.status_code == 200

    draft_request = mock_intapi_orders_draft.handler.next_call()['request']
    assert draft_request.json['alternative_type'] == 'combo_order'


@pytest.mark.parametrize('due', ['2020-01-27T19:55:00+00:00', None])
@pytest.mark.now('2020-01-27T15:45:00+00:00')
async def test_dispatch_due(
        taxi_cargo_orders, mock_intapi_orders_draft, mock_claims_full, due,
):
    request = (
        create_draft_request(lookup_extra={'due': due})
        if due is not None
        else create_draft_request()
    )
    response = await taxi_cargo_orders.post('/v1/order/draft', json=request)
    assert response.status_code == 200
    assert mock_intapi_orders_draft.handler.times_called == 1

    order_draft = mock_intapi_orders_draft.handler.next_call()['request'].json
    assert order_draft.get('due') == due
    if due:
        assert order_draft['is_delayed']


@pytest.mark.parametrize(
    'claim_status',
    [
        'new',
        'estimating',
        'estimating_failed',
        'ready_for_approval',
        'accepted',
    ],
)
async def test_wrong_claim_status(
        claim_status,
        taxi_cargo_orders,
        mock_intapi_orders_draft,
        mockserver,
        load_json,
):
    """
    Tests case with races in cargo claims
    """

    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _mock_claim_full(request):
        claim = load_json('cargo-claims/default.json')
        claim['status'] = claim_status
        return claim

    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=create_draft_request(),
    )
    assert response.status_code == 425
    assert response.json()['code'] == 'too_early'

    assert _mock_claim_full.times_called
    assert not mock_intapi_orders_draft.handler.times_called


@pytest.mark.experiments3(
    is_config=True,
    name='cargo_orders_add_sdd_comment',
    consumers=['cargo-orders/add-sdd-comment'],
    default_value={
        'enabled': True,
        'tanker_key': 'comment.sdd_extra_pay_comment',
    },
)
@pytest.mark.translations(
    cargo={'comment.sdd_extra_pay_comment': {'ru': 'СДД КОММЕНТ'}},
)
async def test_sdd_comment(
        taxi_cargo_orders,
        mock_intapi_nearestzone,
        mock_personal_phones_retrieve,
        mock_claims_full,
        mock_intapi_orders_draft,
        waybill_state,
        exp_cargo_orders_post_payment_flow,
):
    draft_request = create_draft_request()
    draft_request['router_id'] = 'cargo_same_day_delivery_router'

    response = await taxi_cargo_orders.post(
        '/v1/order/draft', json=draft_request,
    )
    assert response.status_code == 200

    order_draft = mock_intapi_orders_draft.handler.next_call()['request'].json
    assert (
        order_draft['comment'] == 'СДД КОММЕНТ\nЗаказ с наложенным платежом.\n'
        'Заказ с подтверждением по СМС.'
    )
