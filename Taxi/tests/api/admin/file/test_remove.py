import pytest


@pytest.mark.parametrize(['init_status', 'target_status'], [
    ('new', 'removed'),
    ('uploaded', 'removing'),
    ('removing', 'removing'),
    ('removed', 'removed'),
])
async def test_s3_remove(
        tap, dataset, api, s3_stubber,
        init_status, target_status
):
    with tap.plan(6, 'удаление файла переводит статус'):
        user = await dataset.user()
        file_meta = await dataset.file_meta(
            user_id=user.user_id,
            status=init_status,
        )

        # Обращение к s3 быть не должно
        # Если оно будет, то будет ошибка
        s3_stubber.add_client_error('delete_object', 'InternalError')
        s3_stubber.activate()

        t = await api(user=user)
        await t.post_ok(
            'api_admin_file_remove',
            json={'file_meta_id': file_meta.file_meta_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('file_meta.file_meta_id', file_meta.file_meta_id)
        t.json_is('file_meta.status', target_status)

        await file_meta.reload()

        tap.eq(file_meta.status, target_status, 'status ok')


async def test_s3_remove_foreign(tap, dataset, api):
    with tap.plan(8, 'попытка удаления чужого файла'):
        user = await dataset.user()
        file_meta = await dataset.file_meta(
            user_id=user.user_id,
            status='uploaded',
        )

        t = await api(role='store_admin')
        await t.post_ok(
            'api_admin_file_remove',
            json={'file_meta_id': file_meta.file_meta_id},
        )

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_file_remove',
            json={'file_meta_id': file_meta.file_meta_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('file_meta.file_meta_id', file_meta.file_meta_id)
        t.json_is('file_meta.status', 'removing')
