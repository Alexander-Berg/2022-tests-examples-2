async def test_success(api, dataset, tap):
    with tap.plan(5, 'Успешно сменили статус марки'):
        order = await dataset.order()
        true_mark = await dataset.true_mark_object(
            order=order,
            status='for_sale'
        )
        user = await dataset.user(company_id=true_mark.company_id)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_true_marks_change_status',
            json={
                'true_mark_id': true_mark.true_mark_id,
                'status': 'sold',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.ok(await true_mark.reload(), 'Перезабрали марку')
        tap.eq(true_mark.status, 'sold', 'Сменился статус марки')
