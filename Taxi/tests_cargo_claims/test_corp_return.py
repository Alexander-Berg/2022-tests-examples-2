import pytest


async def test_happy_path(
        taxi_cargo_claims,
        mockserver,
        get_default_headers,
        create_segment_with_performer,
):
    claim_info = await create_segment_with_performer(use_create_v2=True)

    @mockserver.json_handler('/cargo-orders/admin/v1/order/return')
    def cargo_orders_return(request):
        assert request.args['cargo_order_id'] == claim_info.cargo_order_id
        assert request.json == {
            'comment': 'ПРОПУСК ТОЧКИ КОРП. КЛИЕНТОМ: Клиент отменил заказ',
            'last_known_status': 'performer_found',
            'point_id': 2,
            'ticket': '',
        }

        return {'new_status': 'returning'}

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/return',
        params={'claim_id': claim_info.claim_id},
        json={'point_id': 2, 'comment': 'Клиент отменил заказ'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    assert cargo_orders_return.times_called == 1


@pytest.mark.parametrize('need_return_items', [None, False, True])
@pytest.mark.parametrize('last_known_status', ['performer_found', 'pickuped'])
async def test_single_destination_failed(
        taxi_cargo_claims,
        mockserver,
        get_default_headers,
        create_segment_with_performer,
        state_controller,
        need_return_items,
        last_known_status,
):
    claim_info = await create_segment_with_performer()
    await state_controller.apply(
        target_status=last_known_status, fresh_claim=False,
    )

    @mockserver.json_handler('/cargo-orders/admin/v1/order/return')
    def cargo_orders_return(request):
        assert request.args['cargo_order_id'] == claim_info.cargo_order_id
        assert request.json == {
            'comment': 'ПРОПУСК ТОЧКИ КОРП. КЛИЕНТОМ: Клиент отменил заказ',
            'last_known_status': last_known_status,
            'need_return_items': need_return_items,
            'point_id': 2,
            'ticket': '',
        }

        return {'new_status': 'returning'}

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/return',
        params={'claim_id': claim_info.claim_id},
        json={
            'point_id': 2,
            'comment': 'Клиент отменил заказ',
            'need_return_items': need_return_items,
        },
        headers=get_default_headers(),
    )

    if need_return_items is True and last_known_status == 'pickuped':
        assert response.status_code == 200
        assert cargo_orders_return.times_called == 1
    else:
        assert response.status_code == 409
        assert response.json() == {
            'code': 'not_allowed',
            'message': (
                'Недопустимое действие, в заказе всего одна точка назначения'
            ),
        }
        assert cargo_orders_return.times_called == 0


async def test_no_performer(
        taxi_cargo_claims, mockserver, get_default_headers, create_segment,
):
    claim_info = await create_segment(use_create_v2=True)

    @mockserver.json_handler('/cargo-orders/admin/v1/order/return')
    def cargo_orders_return(request):
        return {'new_status': 'returning'}

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/return',
        params={'claim_id': claim_info.claim_id},
        json={'point_id': 2, 'comment': 'Клиент отменил заказ'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert cargo_orders_return.times_called == 0


async def test_unknown_point(
        taxi_cargo_claims,
        mockserver,
        get_default_headers,
        create_segment_with_performer,
):
    claim_info = await create_segment_with_performer(use_create_v2=True)

    @mockserver.json_handler('/cargo-orders/admin/v1/order/return')
    def cargo_orders_return(request):
        return {'new_status': 'returning'}

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/return',
        params={'claim_id': claim_info.claim_id},
        json={'point_id': 100500, 'comment': 'Клиент отменил заказ'},
        headers=get_default_headers(),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'state_mismatch',
        'message': 'Нет точки доставки с таким идентификатором',
    }

    assert cargo_orders_return.times_called == 0


async def test_not_destination_point(
        taxi_cargo_claims,
        mockserver,
        get_default_headers,
        create_segment_with_performer,
):
    claim_info = await create_segment_with_performer(use_create_v2=True)

    @mockserver.json_handler('/cargo-orders/admin/v1/order/return')
    def cargo_orders_return(request):
        return {'new_status': 'returning'}

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/return',
        params={'claim_id': claim_info.claim_id},
        json={'point_id': 1, 'comment': 'Клиент отменил заказ'},
        headers=get_default_headers(),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'state_mismatch',
        'message': 'Нет точки доставки с таким идентификатором',
    }

    assert cargo_orders_return.times_called == 0
