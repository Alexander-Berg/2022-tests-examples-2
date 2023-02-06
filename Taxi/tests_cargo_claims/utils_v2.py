# pylint: disable=cyclic-import
# pylint: disable=protected-access
import datetime
import typing as tp

from . import conftest


def get_request_items(
        item_title_prefix='item title',
        multipoints=True,
        custom_items=None,
        **kwargs,
):
    if custom_items is not None:
        return custom_items
    items = [
        {
            'title': f'{item_title_prefix} 1',
            'extra_id': '1',
            'size': {'length': 20.0, 'width': 5.8, 'height': 0.5},
            'cost_value': '10.40',
            'cost_currency': 'RUB',
            'weight': 10.2,
            'pickup_point': 1,
            'droppof_point': 2,
            'quantity': 2,
        },
    ]
    if multipoints:
        items.append(
            {
                'title': f'{item_title_prefix} 2',
                'extra_id': '2',
                'size': {'length': 10.0, 'width': 5.8, 'height': 0.5},
                'cost_value': '53.00',
                'cost_currency': 'RUB',
                'weight': 3.7,
                'pickup_point': 1,
                'droppof_point': 3,
                'quantity': 2,
            },
        )
    return items


def _get_shifted_timestamp(now, **kwargs):
    timestamp = now + datetime.timedelta(**kwargs)
    return timestamp.strftime(format='%Y-%m-%dT%H:%M:%SZ')


def get_request_points(
        multipoints=True,
        with_return=True,
        skip_confirmation=False,
        leave_under_door=False,
        meet_outside=False,
        no_door_call=False,
        modifier_age_check=False,
        with_time_intervals=False,
        now=None,
        **kwargs,
):
    if now is None:
        now = datetime.datetime.utcnow()
    points = [
        {
            'point_id': 1,
            'visit_order': 1,
            'address': {
                'fullname': '1',
                'coordinates': [37.2, 55.8],
                'country': '1',
                'city': '1',
                'building_name': '1',
                'street': '1',
                'building': '1',
                'door_code': 'door_1',
                'door_code_extra': 'door_1_extra',
                'doorbell_name': '1',
                'comment': 'comment_1',
            },
            'contact': {
                'phone': '+79999999991',
                'name': 'string',
                'email': '1@yandex.ru',
            },
            'type': 'source',
            'skip_confirmation': skip_confirmation,
            'leave_under_door': leave_under_door,
            'meet_outside': meet_outside,
            'no_door_call': no_door_call,
            'modifier_age_check': modifier_age_check,
        },
        {
            'point_id': 2,
            'visit_order': 2,
            'address': {
                'fullname': '2',
                'coordinates': [37.0, 55.8],
                'country': '2',
                'city': '2',
                'building_name': '2',
                'street': '2',
                'building': '2',
                'door_code': 'door_2',
                'door_code_extra': 'door_2_extra',
                'doorbell_name': '2',
                'comment': 'comment_2',
            },
            'contact': {'phone': '+79999999992', 'name': 'string'},
            'type': 'destination',
            'skip_confirmation': skip_confirmation,
            'leave_under_door': leave_under_door,
            'meet_outside': meet_outside,
            'no_door_call': no_door_call,
            'modifier_age_check': modifier_age_check,
            'external_order_id': 'external_order_id_1',
        },
    ]
    if multipoints:
        points.append(
            {
                'point_id': 3,
                'visit_order': 3,
                'address': {
                    'fullname': '3',
                    'coordinates': [37.0, 55.0],
                    'country': '3',
                    'city': '3',
                    'building_name': '3',
                    'street': '3',
                    'building': '3',
                    'door_code': 'door_3',
                    'door_code_extra': 'door_3_extra',
                    'doorbell_name': '3',
                    'comment': 'comment_3',
                },
                'contact': {
                    'phone': '+79999999993',
                    'name': 'string',
                    'email': '3@yandex.ru',
                },
                'type': 'destination',
                'skip_confirmation': skip_confirmation,
                'leave_under_door': leave_under_door,
                'meet_outside': meet_outside,
                'no_door_call': no_door_call,
                'modifier_age_check': modifier_age_check,
                'external_order_id': 'external_order_id_2',
            },
        )
    if with_return:
        points.append(
            {
                'point_id': 4,
                'visit_order': 4 if multipoints else 3,
                'address': {
                    'fullname': '4',
                    'coordinates': [37.0, 55.5],
                    'country': '4',
                    'city': '4',
                    'building_name': '4',
                    'street': '4',
                    'building': '4',
                    'door_code': 'door_4',
                    'door_code_extra': 'door_4_extra',
                    'doorbell_name': '4',
                    'comment': 'comment_4',
                },
                'contact': {
                    'phone': '+79999999994',
                    'name': 'string',
                    'email': '4@yandex.ru',
                },
                'type': 'return',
                'skip_confirmation': skip_confirmation,
                'leave_under_door': leave_under_door,
                'meet_outside': meet_outside,
                'no_door_call': no_door_call,
                'modifier_age_check': modifier_age_check,
            },
        )
    if with_time_intervals:
        points[0]['time_intervals'] = [
            {
                'type': 'strict_match',
                'from': _get_shifted_timestamp(now, minutes=10),
                'to': _get_shifted_timestamp(now, minutes=25),
            },
        ]
        points[1]['time_intervals'] = [
            {
                'type': 'strict_match',
                'from': _get_shifted_timestamp(now, minutes=30),
                'to': _get_shifted_timestamp(now, minutes=35),
            },
            {
                'type': 'perfect_match',
                'from': _get_shifted_timestamp(now, minutes=20),
                'to': _get_shifted_timestamp(now, minutes=45),
            },
        ]
    return points


def get_create_request(optional_return=False, taxi_class='cargo', **kwargs):
    request = {
        'emergency_contact': {
            'name': 'emergency_name',
            'phone': '+79098887777',
        },
        'items': get_request_items(**kwargs),
        'route_points': get_request_points(**kwargs),
        'comment': 'Очень полезный комментарий',
        'custom_context': {
            'some_key1': 'some_value',
            'some_key2': 123,
            'some_dict': {'dict_key_1': 'dict_value_1'},
        },
        'optional_return': optional_return,
        'client_requirements': {
            'taxi_class': taxi_class,
            'cargo_options': ['thermal_bag'],
        },
    }
    if 'features' in kwargs:
        if 'features' not in request:
            request['features'] = []
        request['features'].extend(kwargs['features'])
    return request


def get_default_response_points():
    points = get_request_points()

    for point in points:
        point['skip_confirmation'] = point.get('skip_confirmation', False)
        point['visited_at'] = {}

    return points


def get_response_point(point_id, points=None):
    assert points
    return next((x for x in points if x['id'] == point_id), None)


def get_default_response_items():
    items = get_request_items()

    return items


def convert_point_ids(response, point_id_to_claim_point_id):
    for item in response['items']:
        item['pickup_point'] = point_id_to_claim_point_id[item['pickup_point']]
        item['droppof_point'] = point_id_to_claim_point_id[
            item['droppof_point']
        ]
    for point in response['route_points']:
        claim_point_id = point.pop('point_id', None)
        point['id'] = point_id_to_claim_point_id[claim_point_id]
        point['visit_status'] = 'pending'
    return response


def get_default_response_v2(
        claim_id,
        point_id_to_claim_point_id,
        with_offer=False,
        with_custom_context=False,
):
    response = convert_point_ids(
        {
            'id': claim_id,
            'version': 1,
            'user_request_revision': '1',
            'status': 'new',
            'corp_client_id': '01234567890123456789012345678912',
            'emergency_contact': {
                'name': 'emergency_name',
                'phone': '+79098887777',
            },
            'client_requirements': {
                'taxi_class': 'cargo',
                'cargo_options': ['thermal_bag'],
            },
            'skip_door_to_door': False,
            'skip_client_notify': False,
            'skip_emergency_notify': False,
            'skip_act': False,
            'optional_return': False,
            'pricing': {},
            'comment': 'Очень полезный комментарий',
            'available_cancel_state': 'free',
            'items': get_default_response_items(),
            'route_points': get_default_response_points(),
            'current_point_id': 1,
            'features': [],
        },
        point_id_to_claim_point_id,
    )
    if with_custom_context:
        response['custom_context'] = {
            'some_key1': 'some_value',
            'some_key2': 123,
            'some_dict': {'dict_key_1': 'dict_value_1'},
        }

    if with_offer:
        response['pricing'] = {
            'currency': 'RUB',
            'offer': {
                'offer_id': 'taxi_offer_id_1',
                'price': '1198.8012',
                'price_raw': 999,
            },
        }
        response['taxi_offer'] = {
            'offer_id': 'taxi_offer_id_1',
            'price': '1198.8012',
            'price_raw': 999,
        }
        response['matched_cars'] = [
            {'cargo_loaders': 2, 'cargo_type': 'lcv_m', 'taxi_class': 'cargo'},
        ]
    return response


def convert_to_inner_response(response):
    # update emergency_contact
    phone = response['emergency_contact'].pop('phone', None)
    personal_phone_id = phone + '_id'

    response['emergency_contact']['personal_phone_id'] = personal_phone_id
    response['user_locale'] = 'en'
    # update route_points
    for point in response['route_points']:
        contact = point['contact']
        phone = contact.pop('phone', None)
        email = contact.pop('email', None)
        if phone is not None:
            contact['personal_phone_id'] = phone + '_id'
        if email is not None:
            contact['personal_email_id'] = email + '_id'

    for i, item in enumerate(response['items']):
        item['id'] = i + 1

    response['segments'] = []
    response['features'] = []
    response['customer_ip'] = conftest.REMOTE_IP
    return response


def get_default_response_v2_inner(claim_id, point_id_to_claim_point_id):
    return convert_to_inner_response(
        get_default_response_v2(
            claim_id, point_id_to_claim_point_id, with_custom_context=True,
        ),
    )


def get_claim_db_id(cursor, claim_id):
    cursor.execute(
        f"""
        SELECT id
        FROM cargo_claims.claims
        WHERE uuid_id=\'{claim_id}\'""",
    )
    claim_pks = cursor.fetchall()

    assert len(claim_pks) == 1

    return claim_pks[0][0]


def get_point_id_to_claim_point_id(
        request: tp.Optional[dict], response,
) -> tp.Dict[int, int]:
    point_id_to_claim_point_id: tp.Dict[int, int] = {}

    if request is None:
        return point_id_to_claim_point_id

    if not isinstance(request.get('route_points'), list):
        return point_id_to_claim_point_id

    for i, point in enumerate(request['route_points']):
        point_id_to_claim_point_id[point['point_id']] = response[
            'route_points'
        ][i]['id']

    return point_id_to_claim_point_id


def drop_ts(value, check_exists=True):
    if isinstance(value, list):
        for item in value:
            drop_ts(item)
    else:
        timestamp = value.pop('updated_ts', None)
        if check_exists:
            assert timestamp is not None
        timestamp = value.pop('created_ts', None)
        if check_exists:
            assert timestamp is not None
        revision = value.pop('revision', None)
        if check_exists:
            assert revision is not None


async def create_claim_v2(
        taxi_cargo_claims,
        params=None,
        request=None,
        headers=None,
        expect_failure=False,
        **kwargs,
):
    if not request:
        request = get_create_request(**kwargs)
    if not headers:
        headers = conftest._get_default_headers()(**kwargs)
    if not params:
        params = conftest._get_default_params()(**kwargs)

    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/create',
        params=params,
        json=request,
        headers=headers,
    )

    if expect_failure:
        return response

    assert response.status_code == 200, response.json()

    return response, get_point_id_to_claim_point_id(request, response.json())


async def get_claim(claim_id, taxi_cargo_claims):
    response = await taxi_cargo_claims.get(
        'v2/claims/full', params={'claim_id': claim_id},
    )
    if response.status_code == 404:
        return None

    assert response.status_code == 200
    return response.json()


async def create_claims_for_search(state_controller):
    def _prepare_claim_create(
            state_controller,
            *,
            claim_index,
            request,
            request_id,
            taxi_order_id=None,
            corp_client_id='01234567890123456789012345678912',
            emergency_phone=None,
            phone_on_delivery=None,
    ):
        handlers_context = state_controller.handlers(claim_index=claim_index)

        create = handlers_context.create

        create.version = 'v2'
        create.request = request
        if emergency_phone:
            create.request['emergency_contact']['phone'] = emergency_phone

        if phone_on_delivery:
            for point in create.request['route_points']:
                if point['type'] == 'destination':
                    point['contact']['phone'] = phone_on_delivery

        create.params = {'request_id': request_id}
        create.headers = conftest._get_default_headers()()
        create.headers['X-B2B-Client-Id'] = corp_client_id

        cancel = handlers_context.cancel

        cancel.headers = conftest._get_default_headers()()
        cancel.headers['X-B2B-Client-Id'] = corp_client_id

        if taxi_order_id:
            performer_draft = handlers_context.performer_lookup_drafted
            performer_draft.request = conftest.get_lookup_drafted_request(
                taxi_order_id=taxi_order_id,
            )

    claim_info_by_claim_index = {}
    # 1 claim
    claim_index = 0
    _prepare_claim_create(
        state_controller,
        claim_index=claim_index,
        request=get_create_request(multipoints=True, with_return=False),
        request_id='idempotency_token_2',
        taxi_order_id='taxi_order_id_1',
    )
    claim_info_by_claim_index[claim_index] = await state_controller.apply(
        target_status='pickuped', next_point_order=3, claim_index=claim_index,
    )

    # 2 claim
    claim_index = 1
    _prepare_claim_create(
        state_controller,
        claim_index=claim_index,
        request=get_create_request(multipoints=False, with_return=False),
        request_id='idempotency_token_1_default',
    )
    claim_info_by_claim_index[claim_index] = await state_controller.apply(
        target_status='estimating', claim_index=claim_index,
    )

    # 3 claim
    claim_index = 2
    _prepare_claim_create(
        state_controller,
        claim_index=claim_index,
        request=get_create_request(multipoints=False, with_return=False),
        request_id='idempotency_token_3',
        corp_client_id='77777777777777777777778888888888',
    )
    claim_info_by_claim_index[claim_index] = await state_controller.apply(
        target_status='new', claim_index=claim_index,
    )

    # 4 claim
    claim_index = 3
    _prepare_claim_create(
        state_controller,
        claim_index=claim_index,
        request=get_create_request(multipoints=False, with_return=False),
        request_id='idempotency_token_4',
        taxi_order_id='taxi_order_id_4',
        phone_on_delivery='+70009050404',
    )
    claim_info_by_claim_index[claim_index] = await state_controller.apply(
        target_status='performer_not_found', claim_index=claim_index,
    )

    # 5 claim
    claim_index = 4
    _prepare_claim_create(
        state_controller,
        claim_index=claim_index,
        request=get_create_request(multipoints=False, with_return=False),
        request_id='idempotency_token_5',
        corp_client_id='01234567890123456789012345678913',
        emergency_phone='+79098887778',
    )
    claim_info_by_claim_index[claim_index] = await state_controller.apply(
        target_status='cancelled',
        claim_index=claim_index,
        transition_tags={'free_cancel'},
        next_point_order=1,
    )

    return claim_info_by_claim_index
