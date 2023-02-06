async def test_list_empty(api, tap, uuid, dataset):
    with tap.plan(4, 'Список активных тегов пуст'):
        t = await api(role='admin')

        cluster = await dataset.cluster()
        await t.post_ok(
            'api_admin_courier_shift_tags_active',
            json={
                'group': 'courier',
                'cluster_id': cluster.cluster_id,
                'title': uuid()
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('courier_shift_tags', [])


async def test_list(api, dataset, tap, uuid):
    with tap.plan(6, 'Список активных локальных тегов'):
        title = uuid()

        cluster = await dataset.cluster()

        # Активный тег в кластере
        tag1 = await dataset.courier_shift_tag(
            group='courier',
            cluster=cluster,
            title=title,
        )

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_courier_shift_tags_active',
            json={
                'group': 'courier',
                'cluster_id': cluster.cluster_id,
                'title': title,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('courier_shift_tags')
        t.json_is(
            'courier_shift_tags.0.courier_shift_tag_id',
            tag1.courier_shift_tag_id,
        )
        t.json_hasnt('courier_shift_tags.1')


async def test_list_global(api, dataset, tap, uuid):
    with tap.plan(6, 'Список активных глобальных тегов'):
        title = uuid()

        cluster = await dataset.cluster()

        # Активный тег
        tag1 = await dataset.courier_shift_tag(
            group='courier',
            title=title,
        )

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_courier_shift_tags_active',
            json={
                'group': 'courier',
                'cluster_id': cluster.cluster_id,
                'title': title,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('courier_shift_tags')
        t.json_is(
            'courier_shift_tags.0.courier_shift_tag_id',
            tag1.courier_shift_tag_id,
        )
        t.json_hasnt('courier_shift_tags.1')


async def test_list_disabled(api, dataset, tap, uuid):
    with tap.plan(5, 'Отключенных тегов нет'):
        title = uuid()

        cluster = await dataset.cluster()

        # Активный тег
        await dataset.courier_shift_tag(
            group='courier',
            title=title,
            status='disabled',
        )

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_courier_shift_tags_active',
            json={
                'group': 'courier',
                'cluster_id': cluster.cluster_id,
                'title': title,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('courier_shift_tags')
        t.json_hasnt('courier_shift_tags.0')


async def test_list_no_cluster(api, dataset, tap, uuid):
    with tap.plan(6, 'Список без передачи кластера доступен логистам'):
        title = uuid()

        cluster = await dataset.cluster()
        user = await dataset.user()

        # Активный тег
        tag1 = await dataset.courier_shift_tag(
            group='courier',
            title=title,
            cluster=cluster,
        )

        with user.role as role:
            role.add_permit('out_of_store', True)

            t = await api(user=user)

            await t.post_ok(
                'api_admin_courier_shift_tags_active',
                json={
                    'group': 'courier',
                    'title': title,
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('courier_shift_tags')
            t.json_is(
                'courier_shift_tags.0.courier_shift_tag_id',
                tag1.courier_shift_tag_id,
            )
            t.json_hasnt('courier_shift_tags.1')


async def test_list_no_cluster_fail(api, dataset, tap, uuid):
    with tap.plan(3, 'Список без передачи кластера не доступен директорам'):
        title = uuid()

        user = await dataset.user()

        with user.role as role:
            role.remove_permit('out_of_store')

            t = await api(user=user)

            await t.post_ok(
                'api_admin_courier_shift_tags_active',
                json={
                    'group': 'courier',
                    'title': title,
                }
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')


async def test_list_group(api, dataset, tap):
    with tap.plan(9, 'Список активных тегов из разных групп'):
        cluster = await dataset.cluster()
        tag_1 = await dataset.courier_shift_tag(group='store', cluster=cluster)
        tag_2 = await dataset.courier_shift_tag(group='system', cluster=cluster)
        await dataset.courier_shift_tag(group='courier', cluster=cluster)

        t = await api(role='admin')

        # выбираем как строку
        await t.post_ok(
            'api_admin_courier_shift_tags_active',
            json={
                'cluster_id': cluster.cluster_id,
                'group': 'system',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is(
            'courier_shift_tags.0.courier_shift_tag_id',
            tag_2.courier_shift_tag_id,
            'системный тег найден'
        )
        t.json_hasnt('courier_shift_tags.1')

        # выбираем как список
        await t.post_ok(
            'api_admin_courier_shift_tags_active',
            json={
                'cluster_id': cluster.cluster_id,
                'group': ['system', 'store'],
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        titles = [tag['title'] for tag in t.res['json']['courier_shift_tags']]
        tap.eq(
            sorted(titles),
            sorted([tag_1.title, tag_2.title]),
            'все теги найдены'
        )
