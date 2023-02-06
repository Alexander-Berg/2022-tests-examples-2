import pytest


ORDER_ID = '123456-123456'
INVALID_ORDER_ID = '123456-error'
ORDER_ID_FIELD_NAME = 'order_id'

ORIGINATOR = 'originator'

INCOMPLETE_ROW_ORDER_ID = '1'


@pytest.mark.parametrize(
    'order_id_field_name, order_id, status_code',
    (
        pytest.param(ORDER_ID_FIELD_NAME, ORDER_ID, 200, id='ok'),
        pytest.param(
            ORDER_ID_FIELD_NAME, INVALID_ORDER_ID, 404, id='invalid order id',
        ),
    ),
)
async def test_get_valid_receipts(
        taxi_eats_receipts, pgsql, order_id_field_name, order_id, status_code,
):

    response = await taxi_eats_receipts.post(
        '/api/v1/receipts/', json={order_id_field_name: order_id},
    )
    if status_code == 200:
        assert (
            response.json()['receipts'][0]['ofd_info']['ofd_receipt_url']
            == 'https://ofd.yandex.ru/vaucher/ffffff1/11111/22222'
        )
        assert (
            response.json()['receipts'][1]['ofd_info']['ofd_receipt_url']
            == 'https://ofd.yandex.ru/vaucher/ffffff2/11111/33333'
        )
        assert (
            response.json()['receipts'][2]['ofd_info']['ofd_receipt_url']
            == 'https://ofd.yandex.ru/vaucher/ffffff3/11111/44444'
        )

    assert response.status_code == status_code
