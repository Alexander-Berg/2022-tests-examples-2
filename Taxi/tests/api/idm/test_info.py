from stall.model.role import PERMITS, Role


async def test_info(tap, api, dataset):
    with tap:
        await dataset.company()

        t = await api(role='token:web.idm.tokens.0')

        await t.get_ok('api_idm_info')

        t.status_is(200, diag=True)
        t.json_is('code', 0)
        t.json_is('roles.slug', 'role')
        t.json_is('roles.name.ru', 'роль')
        t.json_is('roles.name.en', 'role')

        t.json_hasnt('roles.values.guest')
        t.json_hasnt('roles.values.authen_guest')
        t.json_hasnt('roles.values.courier')
        t.json_hasnt('roles.values.executer')
        t.json_hasnt('roles.values.stocktaker')
        t.json_hasnt('roles.values.barcode_executer')
        t.json_hasnt('roles.values.free_device')

        for k, v in PERMITS['roles'].items():
            if k in {'guest', 'authen_guest'}:
                continue
            if v.get('internal'):
                continue
            if v.get('virtual'):
                continue
            t.json_is(f'roles.values.{k}.name', v['description'])

            if Role(k).has_permit('join_company'):
                t.json_hasnt(f'roles.values.{k}.fields')
            else:
                t.json_has(f'roles.values.{k}.fields.0.slug', 'company')
                t.json_is(f'roles.values.{k}.fields.0.name.ru', 'Компания')
                t.json_is(f'roles.values.{k}.fields.0.name.en', 'Company')
                t.json_is(f'roles.values.{k}.fields.0.type', 'choicefield')
                t.json_has(f'roles.values.{k}.fields.0.required', True)
                t.json_is(
                    f'roles.values.{k}.fields.0.options.widget', 'select')
                t.json_has(
                    f'roles.values.{k}.fields.0.options.choices.0.value')
                t.json_has(f'roles.values.{k}.fields.0.options.choices.0.name')
