import pytest


@pytest.mark.parametrize(
    'reserve, count, expected', [
        (1, 2, 1),
        (3, 3, 0),
        (0, 0, 0),
    ]
)
async def test_property_left(tap, dataset, reserve, count, expected):
    with tap.plan(1, 'проверяем корректность работы self.left'):
        # всё что меньше 0 или дробное должно ассёртить...
        stock = await dataset.stock(reserve=reserve, count=count)
        tap.eq_ok(stock.left, expected, 'нормально работает')
