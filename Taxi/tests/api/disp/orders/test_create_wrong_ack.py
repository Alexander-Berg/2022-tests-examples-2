import pytest


@pytest.mark.parametrize(
    'role_result',
    [
        ['admin', 'ER_WRONG_ACK_USER', 'Ошибка админу'],
        ['store_admin', 'ER_ACCESS', 'Ошибка прочим'],
    ]
)
async def test_create(tap, dataset, api, uuid, role_result):
    with tap.plan(6, role_result[-1]):
        product = await dataset.product()
        store = await dataset.store()

        admin = await dataset.user(role=role_result[0], store=store)
        tap.ok(admin.store_id, 'админ создан')
        tap.eq(admin.role, role_result[0], f'роль {role_result[0]}')

        t = await api(user=admin)

        external_id = uuid()

        executer = await dataset.user()
        tap.ne(executer.store_id,
               admin.store_id,
               'На другом складе создан кладовщик')

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'order',
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 21
                                }
                            ],
                            'approved': True,
                            'ack': executer.user_id,
                        })
        t.status_is(403, diag=True)
        t.json_is('code', role_result[1])
