import pytest

from testsuite.utils import matching

from . import conftest


# Check for v2/admin/claims/full response
async def test_full_200_v2(
        taxi_cargo_claims,
        get_internal_claim_response,
        state_controller,
        clear_event_times,
        mockserver,
        get_default_headers,
):
    @mockserver.json_handler('/esignature-issuer/v1/signatures/list')
    def _signature_list(request):
        return {
            'doc_type': request.json['doc_type'],
            'doc_id': request.json['doc_id'],
            'signatures': [
                {
                    'signature_id': 'sender_to_driver_1',
                    'signer_id': '+79999999991_id',
                    'sign_type': 'ya_sms',
                    'code_masked': '12**56',
                },
            ],
        }

    state_controller.handlers().create.headers = get_default_headers()
    state_controller.handlers().create.headers['User-Agent'] = 'Yandex'
    claim_info = await state_controller.apply(
        target_status='new', transition_tags={'by_admin'},
    )
    claim_id = claim_info.claim_id

    expected_response_claim = get_internal_claim_response(
        claim_id, with_custom_context=True,
    )
    expected_response_claim['zone_id'] = 'moscow'
    expected_response_claim['origin_info'] = {
        'origin': 'api',
        'displayed_origin': 'API',
        'user_agent': 'Yandex',
    }
    expected_response_claim['route_points'] = [
        {
            'id': 1,
            'contact': {
                'name': 'string',
                'personal_phone_id': '+71111111111_id',
                'personal_email_id': 'source@yandex.ru_id',
            },
            'address': {
                'fullname': 'БЦ Аврора',
                'coordinates': [37.5, 55.7],
                'country': 'Россия',
                'city': 'Москва',
                'street': 'Садовническая улица',
                'building': '82',
                'porch': '4',
            },
            'type': 'source',
            'visit_order': 1,
            'visit_status': 'pending',
            'skip_confirmation': False,
            'leave_under_door': False,
            'meet_outside': False,
            'no_door_call': False,
            'modifier_age_check': False,
            'visited_at': {},
            'confirmation_code': '12**56',
        },
        {
            'id': 2,
            'contact': {
                'name': 'string',
                'personal_phone_id': '+72222222222_id',
                'phone_additional_code': '123 45 678',
            },
            'address': {
                'fullname': 'Свободы, 30',
                'coordinates': [37.6, 55.6],
                'country': 'Украина',
                'city': 'Киев',
                'street': 'Свободы',
                'building': '30',
                'porch': '2',
                'floor': 12,
                'flat': 87,
                'sfloor': '12',
                'sflat': '87B',
                'door_code': '0к123',
                'comment': 'other_comment',
            },
            'type': 'destination',
            'visit_order': 2,
            'visit_status': 'pending',
            'skip_confirmation': False,
            'leave_under_door': False,
            'meet_outside': False,
            'no_door_call': False,
            'modifier_age_check': False,
            'visited_at': {},
        },
        {
            'id': 3,
            'contact': {
                'name': 'string',
                'personal_phone_id': '+79999999999_id',
                'personal_email_id': 'return@yandex.ru_id',
            },
            'address': {
                'fullname': 'Склад',
                'coordinates': [37.8, 55.4],
                'country': 'Россия',
                'city': 'Москва',
                'street': 'МКАД',
                'building': '50',
            },
            'type': 'return',
            'visit_order': 3,
            'visit_status': 'pending',
            'skip_confirmation': False,
            'leave_under_door': False,
            'meet_outside': False,
            'no_door_call': False,
            'modifier_age_check': False,
            'visited_at': {},
        },
    ]
    expected_response_claim['items'] = [
        {
            'id': 1,
            'pickup_point': 1,
            'droppof_point': 2,
            'title': 'item title 1',
            'size': {'length': 20.0, 'width': 5.8, 'height': 0.5},
            'weight': 10.2,
            'cost_value': '10.40',
            'cost_currency': 'RUB',
            'quantity': 3,
        },
        {
            'id': 2,
            'pickup_point': 1,
            'droppof_point': 2,
            'title': 'item title 2',
            'size': {'length': 2.2, 'width': 5.0, 'height': 1.0},
            'weight': 5.0,
            'cost_value': '0.20',
            'cost_currency': 'RUB',
            'quantity': 1,
        },
    ]
    expected_response_claim['current_point_id'] = 1
    expected_response_claim['segments'] = []
    expected_response_claim['features'] = []
    expected_response_claim['initiator_yandex_uid'] = 'user_id'
    expected_response_claim['initiator_yandex_login'] = 'abacaba'
    expected_response_claim['customer_ip'] = '0.0.0.0'
    response = await taxi_cargo_claims.post(
        'v2/admin/claims/full', params={'claim_id': claim_id},
    )
    assert response.status_code == 200
    json = response.json()
    clear_event_times(json)
    json['claim'].pop('dispatch_flow', None)
    if 'mpc_corrections_count' in json['claim']:
        del json['claim']['mpc_corrections_count']
    assert json['claim'] == expected_response_claim


async def test_visited_at_is_set(
        exchange_confirm,
        get_segment,
        get_claim_v2,
        prepare_state,
        taxi_cargo_claims,
):
    visit_order = 2
    segment_id = await prepare_state(visit_order=visit_order)
    segment = await get_segment(segment_id)
    claim_point_id = conftest.get_claim_point_id_by_order(segment, visit_order)

    response = await exchange_confirm(
        segment_id, claim_point_id=claim_point_id,
    )
    assert response.status_code == 200

    response = await taxi_cargo_claims.post(
        '/v2/admin/claims/full', params={'claim_id': segment['claim_id']},
    )
    assert response.status_code == 200

    for route_point in response.json()['claim']['route_points']:
        if route_point['type'] == 'return':
            continue
        assert route_point['visit_status'] == 'visited'
        assert route_point['visited_at'] == {
            'actual': matching.datetime_string,
        }


async def test_wrong_corp_client_id(taxi_cargo_claims, state_controller):
    claim_info = await state_controller.apply(
        target_status='new', transition_tags={'by_admin'},
    )
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        'v2/admin/claims/full',
        params={
            'claim_id': claim_id,
            'corp_client_id': 'another_corp_client_id',
        },
    )
    assert response.status_code == 404


async def test_dragon_segments(
        taxi_cargo_claims, create_segment_with_performer,
):
    segment = await create_segment_with_performer()
    response = await taxi_cargo_claims.post(
        '/v2/admin/claims/full', params={'claim_id': segment.claim_id},
    )
    assert response.status_code == 200

    assert response.json()['claim']['segments'] == [
        {
            'id': segment.id,
            'provider_order_id': 'taxi_order_id',
            'revision': 2,
        },
    ]


@pytest.fixture
def __create_canceled_claim(
        taxi_cargo_claims,
        build_segment_update_request,
        create_segment,
        get_segment_id,
):
    async def __inner(admin_cancel_reason: str):
        taxi_order_id = 'taxi_order_id_1'

        claim_info = await create_segment()
        claim_id = claim_info.claim_id

        segment_id = await get_segment_id()

        response = await taxi_cargo_claims.post(
            'v1/segments/dispatch/bulk-update-state',
            json={
                'segments': [
                    build_segment_update_request(
                        segment_id,
                        taxi_order_id,
                        with_performer=False,
                        revision=3,
                        resolution='failed',
                        admin_cancel_reason=admin_cancel_reason,
                    ),
                ],
            },
        )
        assert response.status_code == 200
        return claim_id

    return __inner


ADMIN_CANCEL_REASON_MARKS = [
    pytest.mark.config(
        CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
            '__default__': {
                'enabled': True,
                'yt-use-runtime': False,
                'yt-timeout-ms': 10000,
                'ttl-days': 3650,
            },
        },
    ),
]


@pytest.mark.parametrize(
    'admin_cancel_reason',
    [
        'performer_blame.reason_performer_blame',
        None,
        pytest.param(
            'performer_blame.reason_performer_blame',
            marks=ADMIN_CANCEL_REASON_MARKS,
        ),
        pytest.param(None, marks=ADMIN_CANCEL_REASON_MARKS),
    ],
)
async def test_admin_cancel_reason(
        taxi_cargo_claims, __create_canceled_claim, admin_cancel_reason: str,
):
    claim_id = await __create_canceled_claim(admin_cancel_reason)

    response = await taxi_cargo_claims.post(
        '/v2/admin/claims/full', params={'claim_id': claim_id},
    )
    assert response.status_code == 200
    claim = response.json()['claim']

    if admin_cancel_reason:
        assert (
            claim['admin_cancel_reason_info']['origin'] == admin_cancel_reason
        )
        assert not claim['admin_cancel_reason_info']['reason'] == ''
        assert not claim['admin_cancel_reason_info']['details'] == ''
    else:
        assert 'admin_cancel_reason' not in claim


@pytest.mark.parametrize(
    'status,editable',
    (
        pytest.param('new', True, id='editable'),
        pytest.param('cancelled', False, id='not editable'),
    ),
)
async def test_editable(taxi_cargo_claims, state_controller, status, editable):
    claim_info = await state_controller.apply(target_status=status)

    response = await taxi_cargo_claims.post(
        '/v2/admin/claims/full', params={'claim_id': claim_info.claim_id},
    )

    assert response.status_code == 200
    assert response.json()['editable'] == editable
