import pytest
from stall.model.order_required import OrderRequired


@pytest.mark.parametrize('params', [
    {'count': 100},
    {'weight': 10, 'result_weight': 0},
])
def test_instance(tap, uuid, params):
    with tap:
        required = OrderRequired({
            'product_id': uuid(),
            **params
        })
        tap.ok(required, 'запись лога инстанцирована')


def test_diff(tap):
    with tap.plan(1, 'Проверка получения diff-а'):

        required1 = OrderRequired({'product_id': '111', 'count': 10})
        required2 = OrderRequired({'product_id': '222', 'count': 20})
        required3 = OrderRequired({'product_id': '333', 'count': 30})
        required4_1 = OrderRequired({'product_id': '111', 'count': 11})
        required4_2 = OrderRequired({'product_id': '111', 'count': 12})

        old = [required1, required2, required4_1]
        new = [required1, required3, required4_2]

        tap.eq(
            OrderRequired.diff(old, new),
            [
                (required4_1, 11, 0),
                (required4_2, 0, 12),
                (required2, 20, 0),
                (required3, 0, 30)
            ],
            'Изменения получены'
        )
