async def test_instance(tap, dataset):
    with tap.plan(4, 'Создание и сохранение инстанса ЧЗ'):
        order = await dataset.order()
        product = await dataset.product(true_mark=True)
        suggest = await dataset.suggest(
            order=order,
            product_id=product.product_id,
        )
        true_mark = dataset.TrueMark(
            company_id=order.company_id,
            store_id=order.store_id,
            order_id=order.order_id,
            suggest_id=suggest.suggest_id,
            product_id=product.product_id,
            value=await dataset.true_mark_value(product=product),
        )
        tap.ok(true_mark, 'Честный знак')
        tap.ok(not true_mark.true_mark_id, 'Нет ключа')

        tap.ok(await true_mark.save(), 'Смогли сохранить')
        tap.ok(true_mark.true_mark_id, 'Ключ появился')


async def test_dataset(tap, dataset):
    with tap.plan(9, 'Датасет объекта марки честного знака'):
        true_mark = await dataset.true_mark_object()
        tap.ok(true_mark, 'Что-то создали')
        tap.isa_ok(true_mark, dataset.TrueMark, 'Это честный знак')
        db_mark = await dataset.TrueMark.load(true_mark.true_mark_id)
        tap.ok(db_mark, 'Из базы достали по айдишнику')

        order = await dataset.order()
        product = await dataset.product(true_mark=True)
        true_mark = await dataset.true_mark_object(
            product=product,
            order=order,
            status='writeoff',
        )
        tap.ok(true_mark, 'марка получилась')
        tap.eq(true_mark.company_id, order.company_id, 'Компания из ордера')
        tap.eq(true_mark.store_id, order.store_id, 'Склад из ордера')
        tap.eq(true_mark.order_id, order.order_id, 'Ордера ID тот')
        tap.eq(true_mark.product_id, product.product_id, 'Продукт тот')
        tap.eq(true_mark.status, 'writeoff', 'Статус "списан"')
