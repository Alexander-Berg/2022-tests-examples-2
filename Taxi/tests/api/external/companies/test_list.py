import pytest


async def test_list_subscribe(tap, api, uuid, dataset):
    with tap.plan(18, 'Тесты на подписку'):
        companies = []
        for _ in range(3):
            company = await dataset.company(title='Организация %s' % uuid())
            companies.append(company)

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_companies_list',
                        json={'cursor': None, 'subscribe': True})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ответ получен')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_has('companies', 'Список присутствует')
        t.json_has('companies.0', 'элементы есть')
        t.json_has('companies.0.company_id')
        t.json_has('companies.0.title')
        t.json_has('companies.0.ownership')

        with tap.subtest(None, 'Дочитываем до конца') as taps:
            t.tap = taps

            while True:
                if not t.res['json']['companies']:
                    break

                cursor = t.res['json']['cursor']
                await t.post_ok('api_external_companies_list',
                                json={'cursor': cursor})
                t.status_is(200, diag=True)
                t.json_is('code', 'OK', 'ответ получен')
                t.json_has('cursor', 'Курсор присутствует')
                cursor = t.res['json']['cursor']
        t.tap = tap

        t.json_has('cursor', 'Курсор присутствует')

        companies[0].title = uuid()
        company_id = companies[0].company_id
        tap.ok(await companies[0].save(), 'Сохранили один')

        await t.post_ok('api_external_companies_list',
                        json={'cursor': cursor})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ответ получен')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_has('companies.0', 'Есть организации в ответе')
        tap.ok([s for s in t.res['json']['companies']
                if s['company_id'] == company_id],
               'Изменённая организация есть в выдаче')


@pytest.mark.parametrize('cursor_start', [None, 'abc'])
async def test_list_once(tap, api, uuid, dataset, cursor_start):
    with tap.plan(7):
        companies = []
        for _ in range(3):
            company = await dataset.company(title='Организация %s' % uuid())
            companies.append(company)

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_companies_list',
                        json={'cursor': cursor_start, 'subscribe': False})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ответ получен')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_has('companies', 'Список присутствует')

        with tap.subtest(None, 'Дочитываем до конца') as taps:
            t.tap = taps

            while True:
                if not t.res['json']['companies']:
                    break

                cursor = t.res['json']['cursor']
                if not cursor:
                    break

                await t.post_ok('api_external_companies_list',
                                json={'cursor': cursor})
                t.status_is(200, diag=True)
                t.json_is('code', 'OK', 'ответ получен')
                t.json_has('cursor', 'Курсор присутствует')
        t.tap = tap

        t.json_is('cursor', None, 'Курсор пустой говорит что все забрали')
