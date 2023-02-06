from typing import List

import pytest

from . import utils_v2


# pylint: disable=invalid-name
pytestmark = [pytest.mark.usefixtures('yt_apply')]


@pytest.mark.parametrize(
    'corp_client_id, request_body, expected_claim_indexes',
    [
        (
            None,
            {
                'offset': 0,
                'limit': 5,
                'criterias': {
                    'corp_client_id': '01234567890123456789012345678912',
                },
            },
            {0, 1, 3},
        ),
        (
            None,
            {
                'offset': 0,
                'limit': 1,
                'criterias': {
                    'corp_client_id': '01234567890123456789012345678912',
                },
            },
            {3},
        ),
        (
            None,
            {
                'offset': 0,
                'limit': 1,
                'criterias': {
                    'created_from': '2020-01-27T15:37:00+00:00',
                    'created_to': '2040-01-27T15:47:00+00:00',
                    'corp_client_id': '01234567890123456789012345678912',
                },
            },
            {3},
        ),
        (None, {'criterias': {'phone': '+79098887778'}}, set()),
        (None, {'criterias': {'phone': '+70009050404'}}, {3}),
        (
            None,
            {
                'criterias': {'claim_index': 3},
            },  # this is substituted with claim_id in test
            {3},
        ),
        # TODO: fix in CARGODEV-11356
        # (
        #     None,
        #     {
        #         'criterias': {
        #             'offset': 0,
        #             'limit': 5,
        #             'performer_phone': '+71234567890',
        #         },
        #     },
        #     {0},
        # ),
        (None, {'criterias': {'phone': '+70001112323'}}, set()),
    ],
)
async def test_admin_search(
        taxi_cargo_claims,
        state_controller,
        corp_client_id: str,
        request_body: dict,
        expected_claim_indexes: List[int],
):
    claim_info_by_claim_index = await utils_v2.create_claims_for_search(
        state_controller,
    )
    claim_indexes_by_claim_id = {
        claim_info.claim_id: claim_index
        for claim_index, claim_info in claim_info_by_claim_index.items()
    }

    criterias = request_body['criterias']
    if 'claim_index' in criterias:
        claim_id = claim_info_by_claim_index[criterias['claim_index']].claim_id
        criterias['claim_id'] = claim_id
        criterias.pop('claim_index')

    uri = 'v2/admin/claims/search'
    if corp_client_id:
        uri = f'{uri}?corp_client_id={corp_client_id}'

    response = await taxi_cargo_claims.post(uri, json=request_body)
    assert response.status_code == 200

    response_data = response.json()
    found_claim_ids_v2 = {claim['id'] for claim in response_data['claims']}
    found_claim_indexes_v2 = {
        claim_indexes_by_claim_id[claim_id] for claim_id in found_claim_ids_v2
    }

    assert found_claim_indexes_v2 == expected_claim_indexes


async def test_admin_search_check_tariff(
        taxi_cargo_claims, create_segment_with_performer,
):
    await create_segment_with_performer(taxi_class='eda')
    response = await taxi_cargo_claims.post(
        '/v2/admin/claims/search',
        json={'criterias': {'offset': 0, 'limit': 5}},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['claims']) == 1
    assert data['claims'][-1]['taxi_class'] == 'eda'


@pytest.mark.parametrize(
    'phone,expected_status,validated_phone',
    [
        ('not a phone', 400, None),
        ('+7(123)1231231', 200, '+71231231231'),
        ('+7 (123) 456-78-90', 200, '+71234567890'),
        ('7(123)456-78-90', 200, '+71234567890'),
        ('+7000', 400, None),
        ('', 400, None),
    ],
)
async def test_admin_search_phone_validation(
        mockserver, taxi_cargo_claims, phone, expected_status, validated_phone,
):
    def is_valid(phone):
        return (
            phone
            and phone[0] == '+'
            and phone[1:].isdigit()
            and len(phone) == 12
        )

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _phones_store(request):
        assert len(request.json['items']) == 1
        request_phone = request.json['items'][0]['value']
        if validated_phone:
            assert request_phone == validated_phone
        if is_valid(request_phone):
            return {
                'items': [
                    {'id': validated_phone + '_id', 'value': validated_phone},
                ],
            }

        return mockserver.make_response(
            status=400, json={'code': 'not-found', 'message': 'error'},
        )

    response = await taxi_cargo_claims.post(
        'v2/admin/claims/search',
        json={'offset': 0, 'limit': 1, 'criterias': {'phone': phone}},
    )
    assert _phones_store.times_called == 1
    assert response.status_code == expected_status


async def test_admin_search_c2c(
        taxi_cargo_claims, create_default_cargo_c2c_order, mock_create_event,
):
    mock_create_event()
    claim = await create_default_cargo_c2c_order()

    response = await taxi_cargo_claims.post(
        '/v2/admin/claims/search',
        json={'offset': 0, 'limit': 10, 'criterias': {}},
    )
    assert response.status_code == 200
    claim_resp = response.json()['claims'][0]
    claim_resp.pop('created_ts')
    claim_resp.pop('finished_ts')
    assert claim_resp == {
        'id': claim.claim_id,
        'order': {'cost': {'currency': '', 'value': ''}, 'tariff': ''},
        'route_points': [
            {
                'fullname': '1',
                'type': 'source',
                'visit_order': 1,
                'visit_status': 'pending',
            },
            {
                'fullname': '2',
                'type': 'destination',
                'visit_order': 2,
                'visit_status': 'pending',
            },
            {
                'fullname': '3',
                'type': 'destination',
                'visit_order': 3,
                'visit_status': 'pending',
            },
            {
                'fullname': '4',
                'type': 'return',
                'visit_order': 4,
                'visit_status': 'pending',
            },
        ],
        'status': 'accepted',
        'taxi_offer': {
            'offer_id': 'cargo-pricing/v1/123',
            'price': '999.0010',
            'price_raw': 999,
        },
        'pricing': {},
        'cargo_options': ['thermal_bag'],
    }


async def test_cursor_same_result(
        taxi_cargo_claims, state_controller, encode_cursor,
):
    await utils_v2.create_claims_for_search(state_controller)

    request_json = {
        'offset': 0,
        'limit': 5,
        'criterias': {'corp_client_id': '01234567890123456789012345678912'},
    }

    response = await taxi_cargo_claims.post(
        'v2/admin/claims/search', json=request_json,
    )
    assert response.status_code == 200
    first_response = response.json()

    response = await taxi_cargo_claims.post(
        'v2/admin/claims/search', json={'cursor': encode_cursor(request_json)},
    )
    assert response.status_code == 200
    second_response = response.json()

    assert first_response == second_response


async def test_full_response_by_cursors(taxi_cargo_claims, state_controller):
    await utils_v2.create_claims_for_search(state_controller)
    response = await taxi_cargo_claims.post(
        'v2/admin/claims/search',
        json={
            'offset': 0,
            'limit': 5,
            'criterias': {
                'corp_client_id': '01234567890123456789012345678912',
            },
        },
    )
    assert response.status_code == 200
    expected_claims = response.json()['claims']
    assert len(expected_claims) == 3

    response = await taxi_cargo_claims.post(
        'v2/admin/claims/search',
        json={
            'offset': 0,
            'limit': 1,
            'criterias': {
                'corp_client_id': '01234567890123456789012345678912',
            },
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    claims_by_cursor = response_json['claims']
    cursor = response_json['cursor']
    while cursor is not None:
        response = await taxi_cargo_claims.post(
            'v2/admin/claims/search', json={'cursor': cursor},
        )
        assert response.status_code == 200
        response_json = response.json()
        claims_by_cursor += response_json['claims']
        cursor = response_json.get('cursor')
    assert expected_claims == claims_by_cursor
