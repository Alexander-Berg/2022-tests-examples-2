from stall.model.order_problem import OrderProblem


async def test_problems(tap, dataset):
    with tap.plan(5):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            problems = [
                {
                    'product_id': product.product_id,
                    'count': 227
                }
            ]
        )

        tap.eq(len(order.problems), 1, 'один элемент в problems')
        tap.isa_ok(order.problems[0], OrderProblem, 'Элементы в problems')

        tap.eq(order.problems[0].product_id, product.product_id, 'product_id')
        tap.eq(order.problems[0].count, 227, 'count')


