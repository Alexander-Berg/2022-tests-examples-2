import pytest


@pytest.mark.parametrize('lang', ['ru_RU', 'kk_KZ'])
async def test_get_url_lang(tap, api, dataset, lang):
    user = await dataset.user(role='admin', lang=lang)
    t = await api(user=user)
    with tap:
        await t.post_ok(
            'api_support_url',
            json={},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('url',
                    '^https://help-frontend.taxi.tst.yandex.ru'
                    f'/foodtech/yandex/qbt/{lang.lower()}'
                    r'/lavka_storages\?token=\S+')
