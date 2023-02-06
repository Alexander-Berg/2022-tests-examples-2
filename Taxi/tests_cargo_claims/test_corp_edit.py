import copy
import datetime

import pytest


def get_edit_body():
    return {
        'corp_client_id': '01234567890123456789012345678912',
        'emergency_contact': {
            'name': 'emergency_name',
            'phone': '+79098887777',
        },
        # TODO: return with other additional info
        # 'recipient_info': {
        #     'is_individual': False,
        #     'name': 'Some Name',
        #     'address': 'Some address',
        #     'phone_number': '+71234567891',
        # },
        # 'shipment_info': {'details': 'some details', 'name': 'some name'},
        # 'delivery_instructions': {
        #     'vehicle_requirements': 'some vehicle_requirements',
        # },
        'items': [
            {
                'title': 'string',
                'size': {'length': 1.0, 'width': 0.1, 'height': 0.5},
                'weight': 10,
                'quantity': 1,
                'cost_currency': 'RUB',
                'cost_value': '20.53',
            },
        ],
        'route_points': {
            'source': {
                'address': {
                    'fullname': 'source place',
                    'coordinates': [37.2, 55.19],
                    'country': 'russia',
                    'city': 'moscow',
                    'door_code': 'string',
                    'comment': 'my_comment',
                },
                'contact': {
                    'phone': '+79999999992',
                    'name': 'Loader',
                    'email': 'source@yandex.ru',
                },
                'skip_confirmation': False,
            },
            'destination': {
                'address': {
                    'fullname': 'string',
                    'coordinates': [37.3, 55.32],
                    'country': 'russia',
                    'city': 'moscow',
                    'street': 'prospekt Lenina',
                    'building': '2c',
                    'porch': 'A',
                    'floor': 23,
                    'flat': 87,
                    'door_code': 'string',
                    'comment': 'my_comment',
                },
                'contact': {
                    'phone': '+79999999991',
                    'name': 'Client',
                    'phone_additional_code': '333 33 333',
                },
                'skip_confirmation': False,
            },
        },
    }


def get_expected_response(claim_id):
    return {
        'id': claim_id,
        'version': 2,
        'user_request_revision': '2',
        'status': 'new',
        'available_cancel_state': 'free',
        'corp_client_id': '01234567890123456789012345678912',
        'emergency_contact': {
            'name': 'emergency_name',
            'phone': '+79098887777',
        },
        'skip_door_to_door': False,
        'skip_client_notify': False,
        'skip_emergency_notify': False,
        'skip_act': False,
        'optional_return': False,
        'pricing': {},
        # TODO: return with other additional info
        # 'recipient_info': {
        #     'is_individual': False,
        #     'name': 'Some Name',
        #     'address': 'Some address',
        #     'phone_number': '+71234567891',
        # },
        # 'shipment_info': {'details': 'some details', 'name': 'some name'},
        # 'delivery_instructions': {
        #     'vehicle_requirements': 'some vehicle_requirements',
        # },
        'items': [
            {
                'title': 'string',
                'size': {'length': 1.0, 'width': 0.1, 'height': 0.5},
                'weight': 10,
                'quantity': 1,
                'cost_currency': 'RUB',
                'cost_value': '20.53',
            },
        ],
        'route_points': {
            'source': {
                'address': {
                    'fullname': 'source place',
                    'coordinates': [37.2, 55.19],
                    'country': 'russia',
                    'city': 'moscow',
                    'door_code': 'string',
                    'comment': 'my_comment',
                },
                'contact': {
                    'phone': '+79999999992',
                    'name': 'Loader',
                    'email': 'source@yandex.ru',
                },
                'skip_confirmation': False,
            },
            'destination': {
                'address': {
                    'fullname': 'string',
                    'coordinates': [37.3, 55.32],
                    'country': 'russia',
                    'city': 'moscow',
                    'street': 'prospekt Lenina',
                    'building': '2c',
                    'porch': 'A',
                    'floor': 23,
                    'flat': 87,
                    'sfloor': '23',
                    'sflat': '87',
                    'door_code': 'string',
                    'comment': 'my_comment',
                },
                'contact': {
                    'phone': '+79999999991',
                    'name': 'Client',
                    'phone_additional_code': '333 33 333',
                },
                'skip_confirmation': False,
            },
            'return': {
                'address': {
                    'fullname': 'source place',
                    'coordinates': [37.2, 55.19],
                    'country': 'russia',
                    'city': 'moscow',
                    'door_code': 'string',
                    'comment': 'my_comment',
                },
                'contact': {
                    'phone': '+79999999992',
                    'name': 'Loader',
                    'email': 'source@yandex.ru',
                },
                'skip_confirmation': False,
            },
        },
    }


async def test_edit(
        taxi_cargo_claims,
        create_default_claim,
        get_default_headers,
        clear_event_times,
):

    body = get_edit_body()
    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/edit?claim_id='
        f'{create_default_claim.claim_id}&version=1',
        json=body,
        headers=get_default_headers(),
    )

    assert response.status_code == 200
    json = response.json()
    assert json['created_ts'] != '1970-01-01T00:00:00+00:00'
    assert json['updated_ts'] != json['created_ts']
    clear_event_times(json)
    assert json == get_expected_response(create_default_claim.claim_id)


async def test_edit_client_requirements(
        taxi_cargo_claims, create_default_claim, get_default_headers,
):
    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/edit?claim_id='
        f'{create_default_claim.claim_id}&version=1',
        json=dict(
            get_edit_body(),
            **{
                'client_requirements': {
                    'taxi_class': 'cargo',
                    'cargo_type': 'van',
                    'cargo_loaders': 3,
                    'cargo_options': ['thermal_bag'],
                },
            },
        ),
        headers=get_default_headers(),
    )

    assert response.status_code == 200

    assert response.json()['client_requirements'] == {
        'taxi_class': 'cargo',
        'cargo_type': 'van',
        'cargo_loaders': 3,
        'cargo_options': ['thermal_bag'],
    }


async def test_edit_client_requirements_pro_courier(
        taxi_cargo_claims, create_default_claim, get_default_headers,
):
    # pro_courier switched on
    response1 = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/edit?claim_id='
        f'{create_default_claim.claim_id}&version=1',
        json=dict(
            get_edit_body(),
            **{
                'client_requirements': {
                    'taxi_class': 'cargo',
                    'pro_courier': True,
                },
            },
        ),
        headers=get_default_headers(),
    )

    assert response1.status_code == 200

    assert response1.json()['client_requirements'] == {
        'taxi_class': 'cargo',
        'pro_courier': True,
    }

    # pro_courier switched off
    response2 = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/edit?claim_id='
        f'{create_default_claim.claim_id}&version=2',
        json=dict(
            get_edit_body(),
            **{
                'client_requirements': {
                    'taxi_class': 'cargo',
                    'pro_courier': False,
                },
            },
        ),
        headers=get_default_headers(),
    )

    assert response2.status_code == 200

    assert response2.json()['client_requirements'] == {
        'taxi_class': 'cargo',
        'pro_courier': False,
    }


async def test_edit_client_requirements_no_weights(
        taxi_cargo_claims, create_default_claim, get_default_headers,
):
    request = dict(
        get_edit_body(),
        **{
            'client_requirements': {
                'taxi_class': 'cargo',
                'cargo_type': 'van',
                'cargo_loaders': 3,
            },
        },
    )
    del request['items'][0]['size']
    del request['items'][0]['weight']

    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/edit?claim_id='
        f'{create_default_claim.claim_id}&version=1',
        json=request,
        headers=get_default_headers(),
    )

    assert response.status_code == 200

    del request['client_requirements']

    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/edit?claim_id='
        f'{create_default_claim.claim_id}&version=2',
        json=request,
        headers=get_default_headers(),
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'items_without_parameters_forbidden',
        'message': (
            'Грузы без параметров недопустимы, '
            'если отсутствуют требования на тип машины'
        ),
    }


async def test_edit_not_found(
        taxi_cargo_claims, create_default_claim, get_default_headers,
):
    response = await taxi_cargo_claims.post(
        'api/integration/v1/claims/edit?claim_id=some_id&version=1',
        json=get_edit_body(),
        headers=get_default_headers(),
    )
    assert response.status_code == 404


# test should return 400, because method forbidden,
# except corp_clients from config
# CARGO_CLAIMS_COPR_CLIENTS_LIST_ALLOWED_TO_USE_V1
async def test_edit_bad_corp_client_id(
        taxi_cargo_claims, create_default_claim, get_default_headers,
):
    body = get_edit_body()
    # actually changed by headers
    response = await taxi_cargo_claims.post(
        'api/integration/v1/claims/edit?claim_id={}&version=1'.format(
            create_default_claim.claim_id,
        ),
        json=body,
        headers=get_default_headers('other_corp_id0123456789012345678'),
    )
    assert response.status_code == 400


async def test_edit_bad_version(
        taxi_cargo_claims, create_default_claim, get_default_headers,
):
    body = get_edit_body()
    response = await taxi_cargo_claims.post(
        'api/integration/v1/claims/edit?claim_id={}&version=10'.format(
            create_default_claim.claim_id,
        ),
        json=body,
        headers=get_default_headers(),
    )
    assert response.status_code == 409


@pytest.mark.parametrize('new_url', ['https://new.example.com/?', None])
async def test_can_change_callback_url(
        taxi_cargo_claims,
        state_new_claim_with_callback_url,
        get_default_request,
        get_default_headers,
        get_claim,
        new_url,
):  # pylint: disable=redefined-outer-name
    # inserted claim has some different callback_url
    claim = await get_claim(state_new_claim_with_callback_url.claim_id)
    assert claim['callback_properties']['callback_url'] != new_url

    # update claim
    request_data = copy.deepcopy(get_default_request())
    if new_url is not None:
        request_data.update({'callback_properties': {'callback_url': new_url}})
    response = await taxi_cargo_claims.post(
        'api/integration/v1/claims/edit',
        params={
            'claim_id': state_new_claim_with_callback_url.claim_id,
            'version': claim['version'],
        },
        headers=get_default_headers(),
        json=request_data,
    )
    assert response.status_code == 200

    # callback_url has been updated to the new value
    new_claim = await get_claim(state_new_claim_with_callback_url.claim_id)
    if new_url is not None:
        assert new_claim['callback_properties']['callback_url'] == new_url
    else:
        assert 'callback_properties' not in new_claim


@pytest.mark.parametrize('new_delta', [datetime.timedelta(hours=1), None])
async def test_can_change_due(
        taxi_cargo_claims,
        state_new_claim_with_due,
        get_default_request,
        get_default_headers,
        now,
        get_claim,
        to_iso8601,
        from_iso8601,
        close_datetimes,
        new_delta,
):  # pylint: disable=redefined-outer-name
    new_due = None
    if new_delta is not None:
        new_due = now + new_delta
    assert state_new_claim_with_due.due != new_due

    # update claim
    request_data = copy.deepcopy(get_default_request())
    if new_due is not None:
        request_data['due'] = to_iso8601(new_due)
    response = await taxi_cargo_claims.post(
        'api/integration/v1/claims/edit',
        params={
            'claim_id': state_new_claim_with_due.claim_id,
            'version': state_new_claim_with_due.version,
        },
        headers=get_default_headers(),
        json=request_data,
    )
    assert response.status_code == 200

    new_claim = await get_claim(state_new_claim_with_due.claim_id)
    if new_due is not None:
        assert close_datetimes(from_iso8601(new_claim['due']), new_due)
    else:
        assert 'due' not in new_claim


@pytest.mark.parametrize(
    'option_name',
    ['skip_client_notify', 'skip_emergency_notify', 'optional_return'],
)
async def test_edit_skip_options(
        taxi_cargo_claims,
        create_default_claim,
        get_default_headers,
        option_name: str,
):
    request = dict(get_edit_body(), **{option_name: True})

    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/edit?claim_id='
        f'{create_default_claim.claim_id}&version=1',
        json=request,
        headers=get_default_headers(),
    )

    assert response.status_code == 200
    assert response.json()[option_name]

    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/info?claim_id='
        f'{create_default_claim.claim_id}',
        headers=get_default_headers(),
    )

    assert response.status_code == 200
    assert response.json()[option_name]


@pytest.mark.config(CARGO_CLAIMS_ACT_COUNTRY_LIST=[])
async def test_edit_skip_act(
        taxi_cargo_claims,
        create_default_claim,
        get_default_headers,
        clear_event_times,
        pgsql,
):
    body = get_edit_body()
    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/edit',
        params={'claim_id': create_default_claim.claim_id, 'version': 1},
        json=body,
        headers=get_default_headers(),
    )

    json = response.json()
    assert response.status_code == 200
    assert json['skip_act']

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
            SELECT skip_act
            FROM cargo_claims.claims
            WHERE uuid_id ='{json['id']}'
        """,
    )
    assert list(cursor)[0][0]
