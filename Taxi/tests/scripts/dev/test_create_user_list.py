from scripts.dev.create_list_users import FIELDS, get_users_data


async def test_one_user(tap, dataset):
    with tap.plan(2, 'Тест списка пользователей из 1 юзера'):
        company = await dataset.company()
        await dataset.user(company=company,
                           role='admin')

        data = await get_users_data(company_id=company.company_id, role='admin')

        tap.eq(len(data), 1, 'Юзер приехал')
        tap.eq(len(data[0]), len(FIELDS), 'Количество полей правильное')


async def test_several_user(tap, dataset):
    with tap.plan(2, 'Тест списка пользователей из нескольких юзеров'):
        company_1 = await dataset.company()
        await dataset.company()

        await dataset.user(company=company_1,
                           role='admin')
        await dataset.user(company=company_1,
                           role='admin')

        data = await get_users_data(company_id=company_1.company_id,
                                    role='admin')

        tap.eq(len(data), 2, 'Юзер приехал')
        tap.eq(len(data[0]), len(FIELDS), 'Количество полей правильное')


async def test_user_with_status(tap, dataset):
    with tap.plan(2, 'Тест списка пользователей'
                     ' из нескольких юзеров со статусом'):
        company_1 = await dataset.company()
        await dataset.company()

        await dataset.user(company=company_1,
                           role='admin',
                           status='disabled')
        await dataset.user(company=company_1,
                           role='admin',
                           status='active')

        data = await get_users_data(company_id=company_1.company_id,
                                    role='admin',
                                    status='active')

        tap.eq(len(data), 1, 'Юзер приехал')
        tap.eq(len(data[0]), len(FIELDS), 'Количество полей правильное')


async def test_zero_users(tap, dataset):
    with tap.plan(1, 'Тест списка пользователей'
                     ' из нескольких юзеров со статусом'):
        company = await dataset.company()

        data = await get_users_data(company_id=company.company_id,
                                    role='admin',
                                    status='active')

        tap.eq(len(data), 0, 'Нет юзеров')
