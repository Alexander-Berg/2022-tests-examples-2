import pytest

from libstall.util import tzone


@pytest.mark.parametrize('data', [
    {},
    {'fake_key': 'valuable value'},
    {'something': 'else', 'expiry_date': '10-10-2007'},
])
async def test_expire_item_data(dataset, api, tap, now, data):
    with tap.plan(6, 'Изменение expiry_date с разными data экземпляров'):
        tz = 'Europe/Moscow'
        store = await dataset.store(tz=tz)
        item = await dataset.item(store=store, data=data)
        tap.ok(item, 'Экземпляр создан')

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_items_expire',
            json={'item_id': item.item_id}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await item.reload()

        tap.eq(
            item.data('expiry_date'),
            now().astimezone(tzone(tz)).strftime('%F'),
            'Правильная дата выставлена'
        )

        data.pop('expiry_date', None)

        tap.eq(
            {key: item.data[key] for key in data},
            data,
            'Все данные (кроме expiry_date) не изменились'
        )


async def test_expire_item_not_found(tap, api):
    with tap.plan(3, 'Экземпляра нет'):
        t = await api(role='admin')

        fake_item_id = '0' * 12

        await t.post_ok(
            'api_admin_items_expire',
            json={'item_id': fake_item_id}
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


@pytest.mark.parametrize('tz', [
    'Europe/Moscow',
    'US/Hawaii',
    'Europe/Stockholm',
    'Australia/Sydney',
    'Asia/Anadyr',
])
async def test_expire_item_timezones(dataset, api, tap, now, tz):
    with tap.plan(5, 'Изменение expiry_date с разными таймзонами'):
        store = await dataset.store(tz=tz)
        item = await dataset.item(store=store)
        tap.ok(item, 'Экземпляр создан')

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_items_expire',
            json={'item_id': item.item_id}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await item.reload()

        tap.eq(
            item.data('expiry_date'),
            now().astimezone(tzone(tz)).strftime('%F'),
            'Правильная дата выставлена'
        )


@pytest.mark.parametrize('role, expected_code', [
    ('admin', 200),
    ('city_head', 200),
    ('courier', 403),
    ('executer', 403)
])
async def test_expire_item_permit(tap, dataset, api, role, expected_code):
    with tap.plan(3, 'Проверка права с ролью'):
        item = await dataset.item()
        tap.ok(item, 'Экземпляр создан')

        t = await api(role=role)
        await t.post_ok(
            'api_admin_items_expire',
            json={'item_id': item.item_id}
        )
        t.status_is(expected_code, diag=True)
