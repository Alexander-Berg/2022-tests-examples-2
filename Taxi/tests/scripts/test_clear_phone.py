import argparse
from scripts.dev.clear_phone import main


async def test_changes_pass_company_id(tap, dataset):
    with tap.plan(11, 'Изменение номера при переданной компании'):
        company = await dataset.company()
        store = await dataset.store(company_id=company.company_id)

        user_change = await dataset.user(
            store_id=store.store_id,
            company_id=company.company_id,
            status='active',
            provider='internal',
            phone='+07855421333'
        )
        tap.ok(user_change, 'Пользователь с корявым телефоном')
        user_no_changes = await dataset.user(
            store_id=store.store_id,
            company_id=company.company_id,
            status='active',
            provider='internal',
            phone='+447855421333'
        )
        tap.ok(user_no_changes, 'Пользователь с правильным телефоном')
        user_not_active = await dataset.user(
            store_id=store.store_id,
            company_id=company.company_id,
            status='disabled',
            provider='internal',
            phone='+447855421333'
        )
        tap.eq(
            user_not_active.status,
            'disabled',
            'Неактивный пользователь'
        )
        user_pattern_not_at_beginning = await dataset.user(
            store_id=store.store_id,
            company_id=company.company_id,
            status='active',
            provider='internal',
            phone='47+0855421333'
        )
        tap.ok(user_pattern_not_at_beginning,
               'Пользователь с паттерном не в начале'
               )

        user_pattern_not_at_company = await dataset.user(
            status='active',
            provider='internal',
            phone='+447855421333'
        )
        tap.ne(user_pattern_not_at_company.company_id,
               company.company_id,
               'Комапния у пользователя другая'
               )
        args = argparse.Namespace(
            company=company.company_id,
            apply=True,
            pattern='+0',
            replace='+44',
            store=None,
        )

        await main(args)

        await user_change.reload()
        tap.eq(user_change.phone, '+447855421333', 'Телефон успешно изменен')
        tap.eq(user_change.vars.get('old_phone'),
               '+07855421333',
               'Телефон записан на подстраховку')

        await user_no_changes.reload()
        tap.eq(user_no_changes.phone,
               '+447855421333',
               'Телефон не изменился так как не совпао паттер')

        await user_not_active.reload()
        tap.eq(user_not_active.phone,
               '+447855421333',
               'Телефон не изменился так как не активный пользователь')

        await user_pattern_not_at_beginning.reload()
        tap.eq(user_pattern_not_at_beginning.phone,
               '47+0855421333',
               'Телефон не изменился так как паттер и есть но он не в начале')

        await user_pattern_not_at_company.reload()
        tap.eq(user_pattern_not_at_company.phone,
               '+447855421333',
               'Телефон не изменился так как другая компания')


async def test_changes_pass_store_id(tap, dataset):
    with tap.plan(11, 'Изменение номера при переданной лавке'):
        store = await dataset.store()

        user_change = await dataset.user(
            store_id=store.store_id,
            status='active',
            provider='internal',
            phone='+07855421333'
        )
        tap.ok(user_change, 'Пользователь с корявым телефоном')
        user_no_changes = await dataset.user(
            store_id=store.store_id,
            status='active',
            provider='internal',
            phone='+447855421333'
        )
        tap.ok(user_no_changes, 'Пользователь с правильным телефоном')
        user_not_active = await dataset.user(
            store_id=store.store_id,
            status='disabled',
            provider='internal',
            phone='+447855421333'
        )
        tap.eq(
            user_not_active.status,
            'disabled',
            'Неактивный пользователь'
        )
        user_pattern_not_at_beginning = await dataset.user(
            store_id=store.store_id,
            status='active',
            provider='internal',
            phone='47+0855421333'
        )
        tap.ok(user_pattern_not_at_beginning,
               'Пользователь с паттерном не в начале'
               )

        user_pattern_not_at_store = await dataset.user(
            status='active',
            provider='internal',
            phone='+447855421333'
        )
        tap.ne(user_pattern_not_at_store.store_id,
               store.store_id,
               'Комапния у пользователя другая'
               )
        args = argparse.Namespace(
            company=None,
            apply=True,
            pattern='+0',
            replace='+44',
            store=store.store_id,
        )

        await main(args)

        await user_change.reload()
        tap.eq(user_change.phone, '+447855421333', 'Телефон успешно изменен')
        tap.eq(user_change.vars.get('old_phone'),
               '+07855421333',
               'Телефон записан на подстраховку')

        await user_no_changes.reload()
        tap.eq(user_no_changes.phone,
               '+447855421333',
               'Телефон не изменился так как не совпао паттер')

        await user_not_active.reload()
        tap.eq(user_not_active.phone,
               '+447855421333',
               'Телефон не изменился так как не активный пользователь')

        await user_pattern_not_at_beginning.reload()
        tap.eq(user_pattern_not_at_beginning.phone,
               '47+0855421333',
               'Телефон не изменился так как паттер и есть но он не в начале')

        await user_pattern_not_at_store.reload()
        tap.eq(user_pattern_not_at_store.phone,
               '+447855421333',
               'Телефон не изменился так как другая компания')
