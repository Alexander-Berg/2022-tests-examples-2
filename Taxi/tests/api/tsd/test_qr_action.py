from libstall.util import token


# pylint: disable=too-many-statements
async def test_store_checkin(tap, api, dataset, cfg, uuid):
    with tap:
        store = await dataset.store(options={'exp_bill_murray': False})
        tap.ok(store, 'store created')

        executer = await dataset.user(company_id=store.company_id,
                                      store_id=None,
                                      role='executer',
                                      provider='internal')
        tap.ok(executer, 'executer created')

        t = await api(user=executer)

        with tap.subtest(desc='отсутствует store_id'):
            await t.post_ok(
                'api_tsd_qr_action',
                json={
                    'sign': token.pack(
                        cfg('web.auth.secret'),
                        qr_action_type='store_checkin',
                        user_id=uuid(),
                    )
                }
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_BAD_REQUEST')

        with tap.subtest(desc='неизвестный store_id'):
            await t.post_ok(
                'api_tsd_qr_action',
                json={
                    'sign': token.pack(
                        cfg('web.auth.secret'),
                        qr_action_type='store_checkin',
                        user_id=uuid(),
                        payload={
                            'store_id': uuid(),
                        }
                    )
                }
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_STORE_NOT_FOUND')

        foreign_store = await dataset.store(options={'exp_bill_murray': True})

        with tap.subtest(desc='лавка из другой компании'):
            await t.post_ok(
                'api_tsd_qr_action',
                json={
                    'sign': token.pack(
                        cfg('web.auth.secret'),
                        qr_action_type='store_checkin',
                        user_id=uuid(),
                        payload={
                            'store_id': foreign_store.store_id,
                        }
                    ),
                    'params': {
                        'confirmed': True,
                    }
                }
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_USER_COMPANY')

            await executer.reload()

            tap.is_ok(executer.store_id, None, 'store_id not changed')

        with tap.subtest(desc='эксперимент отключен'):
            await t.post_ok(
                'api_tsd_qr_action',
                json={
                    'sign': token.pack(
                        cfg('web.auth.secret'),
                        qr_action_type='store_checkin',
                        user_id=uuid(),
                        payload={
                            'store_id': store.store_id,
                        }
                    )
                }
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_STORE_EXP_OFF')

        store.options['exp_bill_murray'] = True
        store.rehashed(options=True)
        await store.save()

        with tap.subtest(desc='без флага confirmed'):
            await t.post_ok(
                'api_tsd_qr_action',
                json={
                    'sign': token.pack(
                        cfg('web.auth.secret'),
                        qr_action_type='store_checkin',
                        user_id=uuid(),
                        payload={
                            'store_id': store.store_id,
                        }
                    )
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('qr_action_type', 'store_checkin')
            t.json_is('result', {
                'user_id': executer.user_id,
                'store_id': store.store_id,
            })

            await executer.reload()

            tap.is_ok(executer.store_id, None, 'store_id not changed')

        with tap.subtest(desc='с флагом confirmed'):
            await t.post_ok(
                'api_tsd_qr_action',
                json={
                    'sign': token.pack(
                        cfg('web.auth.secret'),
                        qr_action_type='store_checkin',
                        user_id=uuid(),
                        payload={
                            'store_id': store.store_id,
                        }
                    ),
                    'params': {
                        'confirmed': True,
                    }
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('qr_action_type', 'store_checkin')
            t.json_is('result', {
                'user_id': executer.user_id,
                'store_id': store.store_id,
            })

            await executer.reload()

            tap.eq(executer.store_id, store.store_id, 'store_id changed')

        new_store = await dataset.store(company_id=store.company_id,
                                        options={'exp_bill_murray': True})

        with tap.subtest(desc='пользователь не откреплен'):
            await t.post_ok(
                'api_tsd_qr_action',
                json={
                    'sign': token.pack(
                        cfg('web.auth.secret'),
                        qr_action_type='store_checkin',
                        user_id=uuid(),
                        payload={
                            'store_id': new_store.store_id,
                        }
                    ),
                    'params': {
                        'confirmed': True,
                    }
                }
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_USER_NOT_EJECTED')

            await executer.reload()

            tap.eq(executer.store_id, store.store_id, 'store_id not changed')


async def test_common(tap, api, cfg, dataset, uuid):
    with tap.plan(17, 'проверки подписи'):
        executer = await dataset.user(role='executer',
                                      provider='internal')
        tap.ok(executer, 'executer created')

        t = await api(user=executer)

        await t.post_ok(
            'api_tsd_qr_action',
            json={
                'sign': uuid()
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'incorrect sign')

        await t.post_ok(
            'api_tsd_qr_action',
            json={
                'sign': token.pack(
                    cfg('web.auth.secret'),
                    qr_action_type='tsd_order_check',
                    payload={}
                )
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'sign does not contain user_id')

        await t.post_ok(
            'api_tsd_qr_action',
            json={
                'sign': token.pack(
                    cfg('web.auth.secret'),
                    user_id=uuid(),
                    payload={}
                )
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'sign does not contain qr_action_type')

        await t.post_ok(
            'api_tsd_qr_action',
            json={
                'sign': token.pack(
                    cfg('web.auth.secret'),
                    user_id=uuid(),
                    qr_action_type='__unknown__',
                    payload={}
                )
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'unknown qr_action_type')
