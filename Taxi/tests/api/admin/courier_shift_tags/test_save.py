async def test_save(tap, dataset, api, uuid):
    with tap.plan(20, 'Сохранение'):
        user = await dataset.user(role='admin')
        cluster = await dataset.cluster()

        t = await api(user=user)

        external_id     = uuid()
        title1          = uuid()

        await t.post_ok(
            'api_admin_courier_shift_tags_save',
            json={
                'external_id': external_id,
                'title': title1,
                'cluster_id': cluster.cluster_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('courier_shift_tag.updated')
        t.json_has('courier_shift_tag.created')
        t.json_has('courier_shift_tag.courier_shift_tag_id')
        t.json_is('courier_shift_tag.external_id', external_id)
        t.json_is('courier_shift_tag.cluster_id', cluster.cluster_id)
        t.json_is('courier_shift_tag.user_id', user.user_id)
        t.json_is('courier_shift_tag.title', title1)
        t.json_is('courier_shift_tag.status', 'active')

        courier_shift_tag = await dataset.CourierShiftTag.load(
            t.res['json']['courier_shift_tag']['courier_shift_tag_id'])
        tap.ok(courier_shift_tag, 'Объект создан')

        title2          = uuid()

        await t.post_ok(
            'api_admin_courier_shift_tags_save',
            json={
                'courier_shift_tag_id': courier_shift_tag.courier_shift_tag_id,
                'title': title2,
                'status': 'disabled',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is('courier_shift_tag.courier_shift_tag_id',
                  courier_shift_tag.courier_shift_tag_id)
        t.json_is('courier_shift_tag.external_id', external_id)
        t.json_is('courier_shift_tag.user_id', user.user_id)
        t.json_is('courier_shift_tag.title', title2)
        t.json_is('courier_shift_tag.status', 'disabled')


async def test_duplicate(tap, dataset, api, uuid):
    with tap.plan(9, 'нельзя создавать с одним и тем же названием'):
        user = await dataset.user(role='admin')

        t = await api(user=user)

        title = uuid()

        await t.post_ok(
            'api_admin_courier_shift_tags_save',
            json={
                'external_id': uuid(),
                'title': title,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tag_id = t.res['json']['courier_shift_tag']['courier_shift_tag_id']
        await t.post_ok(
            'api_admin_courier_shift_tags_save',
            json={
                'courier_shift_tag_id': tag_id,
                'title': title,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await t.post_ok(
            'api_admin_courier_shift_tags_save',
            json={
                'external_id': uuid(),
                'title': title,
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_DUPLICATE')


async def test_system_tag(tap, dataset, api, uuid):
    with tap.plan(12, 'Нельзя создавать/редактировать системный тег'):
        tag = await dataset.courier_shift_tag(title=f'tag-{uuid()}')
        tag_sys = await dataset.courier_shift_tag(title=f'tag-system-{uuid()}',
                                                  group='system')
        user = await dataset.user(role='admin')
        t = await api(user=user)

        # нельзя создать
        await t.post_ok(
            'api_admin_courier_shift_tags_save',
            json={
                'external_id': uuid(),
                'title': uuid(),
                'group': 'system',
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        # нельзя отредактировать название
        await t.post_ok(
            'api_admin_courier_shift_tags_save',
            json={
                'courier_shift_tag_id': tag_sys.courier_shift_tag_id,
                'title': uuid(),
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        # нельзя убрать из группы системных
        await t.post_ok(
            'api_admin_courier_shift_tags_save',
            json={
                'courier_shift_tag_id': tag_sys.courier_shift_tag_id,
                'title': tag_sys.title,
                'group': 'cluster',
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        # нельзя добавить в группу системных
        await t.post_ok(
            'api_admin_courier_shift_tags_save',
            json={
                'courier_shift_tag_id': tag.courier_shift_tag_id,
                'title': tag_sys.title,
                'group': 'system',
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
