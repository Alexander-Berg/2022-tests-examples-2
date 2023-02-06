import pytest


@pytest.fixture(name='increment_state_version')
def _increment_state_version(taxi_cargo_dispatch):
    async def _wrapper(cargo_order_id, idempotency_token='1234'):
        response = await taxi_cargo_dispatch.post(
            '/v1/waybill/state-version/increment',
            json={'cargo_order_id': cargo_order_id},
            headers={'X-Idempotency-Token': idempotency_token},
        )
        assert response.status_code == 200
        return response

    return _wrapper


async def test_happy_path(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        mock_segments_bulk_info_cut,
        increment_state_version,
        read_waybill_info,
        waybill_ref='waybill_fb_3',
):
    waybill = await read_waybill_info(waybill_ref)
    cargo_order_id = waybill['diagnostics']['order_id']

    response = await increment_state_version(cargo_order_id)
    assert response.json() == {'state_version': 'v1_w_2_s_0'}


async def test_order_not_found(
        taxi_cargo_dispatch,
        cargo_order_id='11111111-2222-3333-4444-555555555555',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/state-version/increment',
        json={'cargo_order_id': cargo_order_id},
        headers={'X-Idempotency-Token': '1234'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'order_not_found',
        'message': f'Order {cargo_order_id} is not found',
    }


async def test_idempotency(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        mock_segments_bulk_info_cut,
        increment_state_version,
        read_waybill_info,
        waybill_ref='waybill_fb_3',
):
    waybill = await read_waybill_info(waybill_ref)
    cargo_order_id = waybill['diagnostics']['order_id']

    response = await increment_state_version(
        cargo_order_id, 'idempotency_token1',
    )
    assert response.json() == {'state_version': 'v1_w_2_s_0'}

    response = await increment_state_version(
        cargo_order_id, 'idempotency_token1',
    )
    assert response.json() == {'state_version': 'v1_w_2_s_0'}

    response = await increment_state_version(
        cargo_order_id, 'idempotency_token2',
    )
    assert response.json() == {'state_version': 'v1_w_3_s_0'}
