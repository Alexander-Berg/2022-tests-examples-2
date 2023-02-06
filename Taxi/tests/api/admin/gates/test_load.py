import pytest


async def test_load_nf(tap, api, uuid):
    with tap.plan(4):
        t = await api(role='admin')

        await t.post_ok('api_admin_gates_load',
                        json={'gate_id': uuid()})

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'нет доступа к не нашим полкам')
        t.json_is('message', 'Access denied', 'текст')


async def test_load(tap, api, dataset):
    with tap.plan(6):

        gate = await dataset.gate()
        tap.ok(gate, 'полка сгенерирована')

        t = await api(role='admin')

        await t.post_ok('api_admin_gates_load',
                        json={'gate_id': gate.gate_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'полка получена')

        t.json_is('gate.gate_id', gate.gate_id, 'идентификатор полки')
        t.json_is('gate.title', gate.title, 'название')


@pytest.mark.parametrize('role', ['admin'])
async def test_load_multiple(tap, api, dataset, role):
    with tap.plan(5):
        t = await api(role=role)
        gate1 = await dataset.gate()
        gate2 = await dataset.gate()
        await t.post_ok(
            'api_admin_gates_load',
            json={'gate_id': [gate1.gate_id,
                              gate2.gate_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('gate', 'есть в выдаче')
        res = t.res['json']['gate']
        tap.eq_ok(
            sorted([res[0]['gate_id'], res[1]['gate_id']]),
            sorted([gate1.gate_id,
                    gate2.gate_id]),
            'Пришли правильные объекты'
        )


@pytest.mark.parametrize('role', ['executer', 'barcode_executer',
                                  'expansioner', 'category_manager'])
async def test_load_multiple_fail(tap, api, dataset, uuid, role):
    with tap.plan(2):
        t = await api(role=role)
        gate1 = await dataset.gate()
        await t.post_ok(
            'api_admin_gates_load',
            json={'gate_id': [gate1.gate_id,
                              uuid()]})
        t.status_is(403, diag=True)


async def test_load_multiple_store(tap, api, dataset):
    with tap.plan(5):
        store = await dataset.store()
        gate1 = await dataset.gate(store_id=store.store_id)
        user = await dataset.user(store=store, role='dc_admin')
        t = await api()
        t.set_user(user)
        await t.post_ok(
            'api_admin_gates_load',
            json={'gate_id': [gate1.gate_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('gate', 'есть в выдаче')
        res = t.res['json']['gate']
        tap.eq_ok(
            res[0]['gate_id'],
            gate1.gate_id,
            'Пришли правильные объекты'
        )
