import pytest

from .. import conftest
from .. import utils


@pytest.mark.now('2020-07-20T11:00:00.00')
async def test_simple(
        taxi_cargo_claims, exchange_confirm, prepare_state, get_segment,
):
    segment_id = await prepare_state(visit_order=2, use_create_v2=True)

    segment = await get_segment(segment_id)
    claim_point_id = conftest.get_claim_point_id_by_order(segment, 2)

    response = await taxi_cargo_claims.post(
        '/v2/claims/exchange/act',
        params={'claim_id': segment['claim_id'], 'point_id': claim_point_id},
        json={
            'items': [{'extra_id': '1', 'quantity': 1}],
            'idempotency_token': '6d8508ae-7a7b-11eb-9439-0242ac130002',
        },
    )
    assert response.status_code == 200

    response = await exchange_confirm(
        segment_id, claim_point_id=claim_point_id,
    )
    assert response.status_code == 200

    segment = await get_segment(segment_id)
    for point in segment['points']:
        if point['claim_point_id'] == claim_point_id:
            assert point['visit_status'] == 'partial_delivery'
            assert point['resolution']['is_visited']


@pytest.mark.now('2020-07-20T11:00:00.00')
async def test_last_point(
        taxi_cargo_claims, exchange_confirm, prepare_state, get_segment,
):
    segment_id = await prepare_state(visit_order=3, use_create_v2=True)

    segment = await get_segment(segment_id)
    claim_point_id = conftest.get_claim_point_id_by_order(segment, 3)

    response = await taxi_cargo_claims.post(
        '/v2/claims/exchange/act',
        params={'claim_id': segment['claim_id'], 'point_id': claim_point_id},
        json={
            'items': [{'extra_id': '2', 'quantity': 1}],
            'idempotency_token': '6d8508ae-7a7b-11eb-9439-0242ac130002',
        },
    )
    assert response.status_code == 200

    response = await exchange_confirm(
        segment_id, claim_point_id=claim_point_id,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['new_status'] == 'returning'

    segment = await get_segment(segment_id)
    assert segment['status'] == 'returning'
    for point in segment['points']:
        if point['claim_point_id'] == claim_point_id:
            assert point['visit_status'] == 'partial_delivery'
            assert point['resolution']['is_visited']


async def test_post_payment_basic(
        taxi_cargo_claims,
        create_segment_with_payment,
        mock_payment_create,
        mock_payment_update,
        exp_cargo_payment_virtual_clients,
):
    """
        Check cargo-payments was notified on partial delivery items update.
    """
    claim_info = await create_segment_with_payment(payment_method='card')
    point_with_postpayment = claim_info.get_point_by_order(2).api_id

    response = await taxi_cargo_claims.post(
        '/v2/claims/exchange/act',
        params={
            'claim_id': claim_info.claim_id,
            'point_id': point_with_postpayment,
        },
        json={
            'items': [{'extra_id': '1', 'quantity': 1}],
            'idempotency_token': '6d8508ae-7a7b-11eb-9439-0242ac130002',
        },
    )
    assert response.status_code == 200

    assert mock_payment_update.requests == [
        {
            'idempotency_token': '6d8508ae-7a7b-11eb-9439-0242ac130002',
            'items': [
                {
                    'article': 'article of item title 1',
                    'count': 1,
                    'currency': 'RUB',
                    'nds': 'nds_10',
                    'price': '10.4',
                    'supplier_inn': '0123456788',
                    'title': 'item title 1',
                },
            ],
            'payment_id': utils.UuidDashedString(),
        },
    ]


async def test_post_payment_external_flow(
        taxi_cargo_claims,
        create_segment_with_payment,
        mock_payment_create,
        mock_payment_update,
        exp_cargo_payment_virtual_clients,
):
    """
        Check cargo-payments wasn't notified for external_payment flow.
    """
    claim_info = await create_segment_with_payment(
        payment_method='card', external_postpayment_flow=True,
    )
    point_with_postpayment = claim_info.get_point_by_order(2).api_id

    response = await taxi_cargo_claims.post(
        '/v2/claims/exchange/act',
        params={
            'claim_id': claim_info.claim_id,
            'point_id': point_with_postpayment,
        },
        json={
            'items': [{'extra_id': '1', 'quantity': 1}],
            'idempotency_token': '6d8508ae-7a7b-11eb-9439-0242ac130002',
        },
    )
    assert response.status_code == 200

    assert mock_payment_update.handler.times_called == 0
