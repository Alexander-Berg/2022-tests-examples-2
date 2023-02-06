from libstall.util import time2time


async def test_success(tap, dataset, api):
    with tap.plan(7, 'Получения списка марок'):
        company_one = await dataset.company()
        company_two = await dataset.company()

        few_marks = [
            await dataset.true_mark_object(
                status='sold',
                order=await dataset.order(company_id=company_one.company_id),
            )
            for _ in range(5)
        ]
        await dataset.true_mark_object(
            order=await dataset.order(company_id=company_one.company_id),
            status='in_order'
        )
        for _ in range(2):
            await dataset.true_mark_object(company_id=company_two.company_id)

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_integration_true_marks_list',
            json={
                'company_id': company_one.company_id,
                'status': ['sold'],
                'subscribe': True,
                'limit': 10
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        cursor = t.res['json']['cursor']
        tap.ok(cursor, 'Непустой курсор')
        response_marks = t.res['json']['true_marks']
        tap.eq(len(response_marks), 5, 'Пять марок')
        tap.ok(
            all(
                mark['company_id'] == company_one.company_id
                for mark in response_marks
            ),
            'Все марки из одной компании'
        )
        tap.eq(
            {mark['true_mark_id'] for mark in response_marks},
            {mark.true_mark_id for mark in few_marks},
            'Ожидаемые id марок'
        )


async def test_fields(tap, dataset, api):
    with tap.plan(12, 'Проверяем поля полученной марки'):
        order = await dataset.order()
        true_mark = await dataset.true_mark_object(
            order=order,
            status='in_order',
            vars={'order_created': time2time('2020-02-03T10:11:33+03:00')}
        )
        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_integration_true_marks_list',
            json={
                'company_id': true_mark.company_id,
                'status': ['in_order'],
                'subscribe': True,
                'limit': 10
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('true_marks.0')
        t.json_hasnt('true_marks.1')
        t.json_is('true_marks.0.true_mark_id', true_mark.true_mark_id)
        t.json_is('true_marks.0.value', true_mark.value)
        t.json_is('true_marks.0.product_id', true_mark.product_id)
        t.json_is('true_marks.0.status', 'in_order')
        t.json_is('true_marks.0.order_id', order.order_id)
        t.json_is('true_marks.0.truncated_mark', true_mark.value[:24])
        t.json_is('true_marks.0.order_created', '2020-02-03T07:11:00.000Z')
