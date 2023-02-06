import pytest

from . import consts
from . import helpers

ITEMS = [
    helpers.make_payment_items(
        [
            helpers.make_item('item-1', '100'),
            helpers.make_item('item-2', '200', product_id='product_id_2'),
        ],
    ),
]


@pytest.fixture(name='grocery_user_debts_retrieve')
def _grocery_user_debts_retrieve(taxi_grocery_user_debts):
    async def _inner(debt_id, status_code=200):
        response = await taxi_grocery_user_debts.post(
            '/internal/debts/v1/retrieve',
            json={'debt_id': debt_id, 'order_id': consts.ORDER_ID},
        )

        assert response.status_code == status_code
        return response.json()

    return _inner


async def test_basic(
        grocery_user_debts_retrieve, debt_collector, default_debt,
):
    debt_collector.by_id.check(service=consts.SERVICE, ids=[consts.DEBT_ID])

    debt_collector.by_id.mock_response(
        items_by_payment_type=helpers.to_debt_collector_items(ITEMS),
        created_at=consts.NOW,
        version=2,
    )

    response = await grocery_user_debts_retrieve(debt_id=consts.DEBT_ID)

    _check_response(
        response,
        debt_id=consts.DEBT_ID,
        created=consts.NOW,
        items=ITEMS,
        version=2,
    )


async def test_404_pgsql(grocery_user_debts_retrieve):
    await grocery_user_debts_retrieve(debt_id=consts.DEBT_ID, status_code=404)


async def test_404_debt_collector(
        grocery_user_debts_retrieve, debt_collector, default_debt,
):
    debt_collector.by_id.response = None

    await grocery_user_debts_retrieve(debt_id=consts.DEBT_ID, status_code=404)


def _check_response(response, **kwargs):
    for key, value in kwargs.items():
        assert response[key] == value, key
