async def test_success(api, dataset, tap):
    with tap.plan(19, 'Успешный поиск марок'):
        order = await dataset.order()
        true_mark_one = await dataset.true_mark_object(
            order=order, status='sold')
        true_mark_two = await dataset.true_mark_object(
            order=order, status='for_sale')
        user = await dataset.user(
            company_id=true_mark_one.company_id, role='admin')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_true_marks_list',
            json={'company_id': true_mark_one.company_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('true_marks.0')
        t.json_has('true_marks.1')
        t.json_hasnt('true_marks.2')
        tap.eq(
            {mark['true_mark_id'] for mark in t.res['json']['true_marks']},
            {true_mark_one.true_mark_id, true_mark_two.true_mark_id},
            'Марки правильные в ответе'
        )

        await t.post_ok(
            'api_admin_true_marks_list',
            json={
                'company_id': true_mark_one.company_id,
                'status': 'for_sale'
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('true_marks.0')
        t.json_hasnt('true_marks.1')
        t.json_is('true_marks.0.true_mark_id', true_mark_two.true_mark_id)

        await t.post_ok(
            'api_admin_true_marks_list',
            json={'true_mark_value': true_mark_one.value},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('true_marks.0')
        t.json_hasnt('true_marks.1')
        t.json_is('true_marks.0.true_mark_id', true_mark_one.true_mark_id)
