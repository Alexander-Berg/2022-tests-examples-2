import pytest


async def test_get_url(tap, api, cfg):
    cfg.set(
        'support_chat.url',
        {
            'local': 'http://example.com/path',
            'testing': 'http://example.com/path',
        }
    )
    t = await api(role='admin')
    with tap:
        await t.post_ok(
            'api_tsd_support_url',
            json={},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('url', r'^http://example.com/path\?token=\S+$')


async def test_get_url_no_store(tap, api, dataset):
    user = await dataset.user(store_id=None, role='admin')
    t = await api(user=user)
    with tap:
        await t.post_ok(
            'api_tsd_support_url',
            json={},
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_NO_STORE')
        t.json_is('message', 'No store')


@pytest.mark.parametrize('lang', ['ru_RU', 'kk_KZ'])
async def test_get_url_lang(tap, api, dataset, lang):
    user = await dataset.user(role='admin', lang=lang)
    t = await api(user=user)
    with tap:
        await t.post_ok(
            'api_tsd_support_url',
            json={},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('url',
                    '^https://help-frontend.taxi.tst.yandex.ru'
                    f'/foodtech/yandex/qbt/{lang.lower()}'
                    r'/lavka_storages\?token=\S+')
