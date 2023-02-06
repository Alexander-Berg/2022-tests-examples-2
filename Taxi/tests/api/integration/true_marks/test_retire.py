async def test_success(tap, dataset, api):
    with tap.plan(9, 'Несколько марок погасили'):
        company = await dataset.company()
        true_marks = [
            await dataset.true_mark_object(
                order=await dataset.order(company_id=company.company_id),
                status='sold'
            ) for _ in range(3)
        ]

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_integration_true_marks_retire',
            json={
                'company_id': company.company_id,
                'true_marks': [
                    {
                        'true_mark_id': true_marks[0].true_mark_id,
                        'status': 'sold'
                    },
                    {
                        'true_mark_id': true_marks[1].true_mark_id,
                        'status': 'sold'
                    },
                ]
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        first_mark = true_marks[0]
        tap.ok(await first_mark.reload(), 'Перезабрали первую марку')
        tap.eq(first_mark.status, 'sold_retired', 'Статус погашения')
        second_mark = true_marks[1]
        tap.ok(await second_mark.reload(), 'Перезабрали вторую марку')
        tap.eq(second_mark.status, 'sold_retired', 'Статус погашения')
        third_mark = true_marks[2]
        tap.ok(await third_mark.reload(), 'Перезабрали третью марку')
        tap.eq(third_mark.status, 'sold', 'Статус не погасили')


async def test_fail_diff_companies(tap, dataset, api):
    with tap.plan(3, 'Разные компании'):
        company_one = await dataset.company()
        company_two = await dataset.company()
        mark_one = await dataset.true_mark_object(
            order=await dataset.order(company_id=company_one.company_id),
            status='sold'
        )
        mark_two = await dataset.true_mark_object(
            order=await dataset.order(company_id=company_two.company_id),
            status='sold'
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_integration_true_marks_retire',
            json={
                'company_id': company_one.company_id,
                'true_marks': [
                    {
                        'true_mark_id': mark_one.true_mark_id,
                        'status': 'sold'
                    },
                    {
                        'true_mark_id': mark_two.true_mark_id,
                        'status': 'sold'
                    },
                ]
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_missing_mark(tap, dataset, uuid, api):
    with tap.plan(3, 'Неизвестная марка'):
        company = await dataset.company()
        true_mark = await dataset.true_mark_object(
            order=await dataset.order(company_id=company.company_id),
            status='sold'
        )
        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_integration_true_marks_retire',
            json={
                'company_id': company.company_id,
                'true_marks': [
                    {
                        'true_mark_id': true_mark.true_mark_id,
                        'status': 'sold'
                    },
                    {
                        'true_mark_id': uuid(),
                        'status': 'sold'
                    },
                ]
            }
        )
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND')
