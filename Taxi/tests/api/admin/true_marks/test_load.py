async def test_success(api, dataset, tap):
    with tap.plan(13, 'Успешная загрузка марки'):
        true_mark = await dataset.true_mark_object()
        user = await dataset.user(company_id=true_mark.company_id)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_true_marks_load',
            json={'true_mark_id': true_mark.true_mark_id},
        )
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')

        await t.post_ok(
            'api_admin_true_marks_load',
            json={'true_mark_id': [true_mark.true_mark_id]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('true_marks.0')
        t.json_hasnt('true_marks.1')
        t.json_is('true_marks.0.store_id', true_mark.store_id)
        t.json_is('true_marks.0.company_id', true_mark.company_id)
        t.json_is('true_marks.0.order_id', true_mark.order_id)
        t.json_is('true_marks.0.value', true_mark.value)
        t.json_is('true_marks.0.product_id', true_mark.product_id)
