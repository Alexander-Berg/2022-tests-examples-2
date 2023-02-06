import datetime

import pytest


@pytest.mark.parametrize('increment,new_value', [(300, 310), (7200, 7200)])
@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_prolong_200(
        taxi_manual_dispatch,
        create_order,
        get_order,
        mock_set_order_fields,
        headers,
        increment,
        new_value,
):
    mock_set_order_fields['expected_value'] = {
        '$set': {'order.request.lookup_ttl': new_value},
    }
    create_order(
        lookup_ttl=datetime.timedelta(seconds=10), order_id='order_id_1',
    )
    response = await taxi_manual_dispatch.post(
        '/v1/dispatch/prolong',
        headers=headers,
        json={'order_id': 'order_id_1', 'lookup_ttl_increment': increment},
    )
    assert response.status_code == 200
    assert response.json()['lookup_ttl'] == new_value
    assert mock_set_order_fields['handler'].times_called == 1
    assert get_order('order_id_1')['lookup_ttl'] == datetime.timedelta(
        seconds=new_value,
    )


async def test_not_pending(
        taxi_manual_dispatch, create_order, get_order, headers,
):
    create_order(
        lookup_ttl=datetime.timedelta(seconds=10),
        order_id='order_id_1',
        status='cancelled',
    )
    response = await taxi_manual_dispatch.post(
        '/v1/dispatch/prolong',
        headers=headers,
        json={'order_id': 'order_id_1', 'lookup_ttl_increment': 10},
    )
    assert response.status_code == 404
    assert get_order('order_id_1')['lookup_ttl'] == datetime.timedelta(
        seconds=10,
    )


async def test_404(taxi_manual_dispatch, create_order, get_order, headers):
    response = await taxi_manual_dispatch.post(
        '/v1/dispatch/prolong',
        headers=headers,
        json={'order_id': 'order_id_1', 'lookup_ttl_increment': 10},
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'order_not_found'
