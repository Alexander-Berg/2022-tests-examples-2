async def test_tsd_order_check(tap, api, dataset, now):
    with tap.plan(13, 'генерируем и применяем qr-код tsd_order_check'):
        admin = await dataset.user()
        tap.ok(admin, 'admin created')

        executer = await dataset.user(company=admin.company_id,
                                      store_id=admin.store_id,
                                      role='executer',
                                      provider='internal')
        tap.ok(executer, 'executer created')

        order = await dataset.order(company_id=admin.company_id,
                                    store_id=admin.store_id,
                                    status='complete',
                                    estatus='done',
                                    type='acceptance',
                                    vars={'all_children_done': now()})
        tap.ok(order, 'order created')

        t = await api(
            user=admin,
            spec='doc/api/admin/qr_actions.yaml',
        )

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'tsd_order_check',
                'generator_params': {
                    'order_id': order.order_id,
                },
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('qr_data')
        t.json_has('qr_data.sign')

        sign = t.res['json']['qr_data']['sign']

        t = await api(
            user=executer,
            spec='doc/api/tsd.yaml',
        )

        await t.post_ok(
            'api_tsd_qr_action',
            json={'sign': sign}
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('result')
        t.json_is('result', {
            'parent_id': order.order_id,
            'action': 'tsd_order_check',
            'mode': 'check_product_on_shelf',
        })


async def test_tsd_order_check_closed(tap, api, dataset, now):
    with tap.plan(4, 'приемка уже подтверждена директором'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        order = await dataset.order(
            type='acceptance',
            store=store,
            status='complete',
            estatus='done',
            vars={'all_children_done': now(), 'closed': now()},
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'tsd_order_check',
                'generator_params': {
                    'order_id': order.order_id,
                },
            }
        )

        t.status_is(410)
        t.json_is('code', 'ER_GONE')
        t.json_is('message', 'Order is approved, no checks allowed')


async def test_tsd_order_check_stowages(tap, api, dataset):
    with tap.plan(4, 'не завершены основные размещения'):
        store = await dataset.store(options={'exp_agutin': True})
        user = await dataset.user(store=store)
        order = await dataset.order(
            type='acceptance',
            store=store,
            status='complete',
            estatus='done',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'tsd_order_check',
                'generator_params': {
                    'order_id': order.order_id,
                },
            }
        )

        t.status_is(409)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'Children are not completed')


async def test_tsd_order_check_access(tap, api, dataset, uuid):
    with tap.plan(8, 'доступ к ордеру при tsd_order_check'):
        admin = await dataset.user(role='store_admin')
        tap.ok(admin, 'store_admin created')

        t = await api(user=admin)

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'tsd_order_check',
                'generator_params': {
                    'order_id': uuid(),
                },
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        foreign_order = await dataset.order(company_id=admin.company_id,
                                            status='complete',
                                            estatus='done',
                                            type='acceptance')
        tap.ok(foreign_order, 'foreign_order created')

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'tsd_order_check',
                'generator_params': {
                    'order_id': foreign_order.order_id,
                },
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_tsd_order_check_badreq(tap, api, dataset, time_mock, now):
    with tap.plan(17, 'правильность входных параметров при tsd_order_check'):
        admin = await dataset.user()
        tap.ok(admin, 'admin created')

        order = await dataset.order(company_id=admin.company_id,
                                    store_id=admin.store_id)
        tap.ok(order, 'order created')

        t = await api(user=admin)

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'tsd_order_check',
                'generator_params': {
                    'order_id': order.order_id,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_ORDER_IS_NOT_DONE')

        order.rehash(status='complete')
        await order.save()

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'tsd_order_check',
                'generator_params': {
                    'order_id': order.order_id,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_ORDER_IS_NOT_DONE')

        order.rehash(estatus='done')
        await order.save()

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'tsd_order_check',
                'generator_params': {
                    'order_id': order.order_id,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_ORDER_NOT_ACCEPTANCE')

        order.rehash(type='acceptance')
        order.vars['all_children_done'] = now()
        await order.save()

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'tsd_order_check',
                'generator_params': {
                    'order_id': order.order_id,
                },
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        time_mock.sleep(days=5)

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'tsd_order_check',
                'generator_params': {
                    'order_id': order.order_id,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_ORDER_IS_TOO_OLD')


async def test_trusted_acceptance(tap, api, dataset, uuid):
    with tap.plan(14, 'генерируем и применяем qr-код trusted_acceptance'):
        store = await dataset.store(options={'exp_lightman': True})
        tap.ok(store, 'store created')

        admin = await dataset.user(company=store.company_id,
                                   store_id=store.store_id)
        tap.ok(admin, 'admin created')

        executer = await dataset.user(company=store.company_id,
                                      store_id=store.store_id,
                                      role='executer',
                                      provider='internal')
        tap.ok(executer, 'executer created')

        order = await dataset.order(company_id=admin.company_id,
                                    store_id=admin.store_id,
                                    type='acceptance',
                                    attr={'trust_code': uuid()})
        tap.ok(order, 'order created')

        t = await api(
            user=admin,
            spec='doc/api/admin/qr_actions.yaml',
        )

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'trusted_acceptance',
                'generator_params': {
                    'order_id': order.order_id,
                },
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('qr_data')
        t.json_has('qr_data.sign')

        sign = t.res['json']['qr_data']['sign']

        t = await api(
            user=executer,
            spec='doc/api/tsd.yaml',
        )

        await t.post_ok(
            'api_tsd_qr_action',
            json={'sign': sign}
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('result')
        t.json_is('result', {
            'trust_code': order.attr['trust_code']
        })


async def test_trusted_acceptance_access(tap, api, dataset, uuid):
    with tap.plan(9, 'доступ к ордеру при trusted_acceptance'):
        store = await dataset.store()
        tap.ok(store, 'store created')

        admin = await dataset.user(company_id=store.company_id,
                                   store_id=store.store_id,
                                   role='store_admin')
        tap.ok(admin, 'store_admin created')

        t = await api(user=admin)

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'trusted_acceptance',
                'generator_params': {
                    'order_id': uuid(),
                },
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        foreign_order = await dataset.order(company_id=store.company_id,
                                            type='acceptance',
                                            attr={'trust_code': uuid()})
        tap.ok(foreign_order, 'foreign_order created')

        t = await api(user=admin)

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'trusted_acceptance',
                'generator_params': {
                    'order_id': foreign_order.order_id,
                },
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_trusted_acceptance_badreq(tap, api, dataset, uuid):
    with tap.plan(15, 'правильность входных данных при trusted_acceptance'):
        store = await dataset.store()
        tap.ok(store, 'store created')

        admin = await dataset.user(company_id=store.company_id,
                                   store_id=store.store_id)
        tap.ok(admin, 'admin created')

        order = await dataset.order(company_id=admin.company_id,
                                    store_id=admin.store_id)
        tap.ok(order, 'order created')

        t = await api(user=admin)

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'trusted_acceptance',
                'generator_params': {
                    'order_id': order.order_id,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_ORDER_NOT_ACCEPTANCE')

        order.rehash(type='acceptance')
        await order.save()

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'trusted_acceptance',
                'generator_params': {
                    'order_id': order.order_id,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_ORDER_HAS_NO_TRUST_CODE')

        order.rehash(attr={'trust_code': uuid()})
        await order.save()

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'trusted_acceptance',
                'generator_params': {
                    'order_id': order.order_id,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_STORE_EXP_OFF')

        store.rehash(options={'exp_lightman': True})
        await store.save()

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'trusted_acceptance',
                'generator_params': {
                    'order_id': order.order_id,
                },
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


async def test_store_checkin(tap, api, dataset):
    with tap.plan(24, 'генерируем и применяем qr-код по чекину на лавке. '
                      'чекин происходит только при переданном confirmed. '
                      'иначе только получаем данные из qr-кода'):
        store = await dataset.store(options={'exp_bill_murray': True})
        tap.ok(store, 'store created')

        admin = await dataset.user(company_id=store.company_id,
                                   store_id=store.store_id)
        tap.ok(admin, 'admin created')

        executer = await dataset.user(company=store.company_id,
                                      store_id=None,
                                      role='executer',
                                      provider='internal')
        tap.ok(executer, 'executer created')

        t = await api(
            user=admin,
            spec='doc/api/admin/qr_actions.yaml',
        )

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'store_checkin',
                'generator_params': {
                    'store_id': store.store_id,
                },
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('qr_data')
        t.json_has('qr_data.sign')

        sign = t.res['json']['qr_data']['sign']

        t = await api(
            user=executer,
            spec='doc/api/tsd.yaml',
        )

        await t.post_ok(
            'api_tsd_qr_action',
            json={'sign': sign}
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('result')
        t.json_is('result.user_id', executer.user_id)
        t.json_is('result.store_id', store.store_id)

        await executer.reload()

        tap.is_ok(executer.store_id, None, 'store_id not changed')
        tap.is_ok(executer.get_store_checkin_time_interval(store.store_id),
                  None, 'store checkin time not saved')

        await t.post_ok(
            'api_tsd_qr_action',
            json={'sign': sign, 'params': {'confirmed': True}}
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('result')
        t.json_is('result.user_id', executer.user_id)
        t.json_is('result.store_id', store.store_id)

        await executer.reload()

        tap.eq(executer.store_id, store.store_id, 'store_id changed')
        tap.isnt_ok(executer.get_store_checkin_time_interval(store.store_id),
                    None, 'store checkin time saved')


async def test_store_checkin_access(tap, api, dataset, uuid):
    with tap.plan(9, 'доступ к лавке при store_checkin'):
        store = await dataset.store()
        tap.ok(store, 'store created')

        admin = await dataset.user(company_id=store.company_id,
                                   store_id=store.store_id,
                                   role='store_admin')
        tap.ok(admin, 'store_admin created')

        t = await api(user=admin)

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'store_checkin',
                'generator_params': {
                    'store_id': uuid(),
                },
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        foreign_store = await dataset.store(company_id=store.company_id)
        tap.ok(foreign_store, 'foreign_store created')

        t = await api(user=admin)

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'store_checkin',
                'generator_params': {
                    'store_id': foreign_store.store_id,
                },
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_store_checkin_badreq(tap, api, dataset):
    with tap.plan(5, 'правильность входных данных при store_checkin'):
        store = await dataset.store(options={'exp_bill_murray': False})
        tap.ok(store, 'store created')

        admin = await dataset.user(company_id=store.company_id,
                                   store_id=store.store_id)
        tap.ok(admin, 'admin created')

        t = await api(user=admin)

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={
                'qr_action_type': 'store_checkin',
                'generator_params': {
                    'store_id': store.store_id,
                },
            }
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_STORE_EXP_OFF')


async def test_bad_request(tap, api):
    with tap.plan(9, 'правильность общих входных данных'):
        t = await api(role='admin')

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={'qr_action_type': '__unknown__',
                  'generator_params': {}}
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={'qr_action_type': 'tsd_order_check'}
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')

        await t.post_ok(
            'api_admin_qr_actions_generate',
            json={'qr_action_type': 'tsd_order_check',
                  'generator_params': {}}
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')
