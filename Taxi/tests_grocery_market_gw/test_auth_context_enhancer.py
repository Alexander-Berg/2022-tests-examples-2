import pytest


async def test_adjusted_auth_context(
        taxi_grocery_market_gw, mockserver, personal, testpoint,
):
    """ auth_context should be adjusted from headers
    and personal service """

    phone_number = '+78005553535'
    personal_phone_id = 'some-personal-phone-id'
    ip_address = '192.168.0.1'
    appmetrica_device_id = '12345678910'
    yandex_uid = '4065912996'
    taxi_user_id = 'b5e79418cc524c799d6584523587ab9b'
    app_ver1 = '600'
    app_ver2 = '32'
    app_ver3 = '0'
    platform_ver1 = '14'
    platform_ver2 = '4'
    platform_ver3 = '2'

    personal.check_request(
        personal_phone_id=personal_phone_id, phone=phone_number,
    )

    @testpoint('adjusted_auth_context')
    def adjusted_auth_context_callback(auth_context):
        assert auth_context['session'] == 'taxi:' + taxi_user_id
        assert auth_context['domain'] == 'taxi'
        assert auth_context['taxi_user_id'] == taxi_user_id
        assert auth_context['ip'] == ip_address
        assert auth_context['locale'] == 'ru'
        app_vars = {}
        for app_var in auth_context['app_vars'].split(','):
            key, value = app_var.split('=')
            app_vars[key] = value
        assert app_vars == {
            'app_brand': 'yataxi',
            'app_build': 'release',
            'app_name': 'mobileweb_iphone',
            'app_ver1': app_ver1,
            'app_ver2': app_ver2,
            'app_ver3': app_ver3,
            'platform_ver1': platform_ver1,
            'platform_ver2': platform_ver2,
            'platform_ver3': platform_ver3,
        }
        assert (
            auth_context['personal']
            == 'personal_phone_id=some-personal-phone-id'
        )
        assert auth_context['uid'] == yandex_uid
        assert auth_context['authorized'] is True
        assert auth_context['appmetrica_device_id'] == appmetrica_device_id
        assert auth_context['personal_phone_id'] == personal_phone_id

    @mockserver.json_handler('/grocery-api/lavka/v1/api/v1/startup')
    def _mock_startup(request):
        return mockserver.make_response(
            status=200, json={'exists': True, 'available': True},
        )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/startup',
        headers={
            'User-Agent': (
                'Mozilla/5.0 (iPhone; CPU iPhone OS '
                f'{platform_ver1}_{platform_ver2}_{platform_ver3} like Mac '
                'OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                f'yandex-taxi/{app_ver1}.{app_ver2}.{app_ver3}.125308 '
                'YandexEatsKit/1.17.28 Superapp/Grocery'
            ),
            'X-YaTaxi-UserId': taxi_user_id,
            'X-Yandex-UID': yandex_uid,
            'X-AppMetrica-DeviceId': appmetrica_device_id,
            'X-Remote-IP': ip_address,
            'Accept-Language': 'ru_RU',
            'Phone-Number': phone_number,
        },
    )
    assert response.status == 200
    assert personal.times_phones_store_called() == 1
    assert adjusted_auth_context_callback.times_called == 1


@pytest.mark.parametrize('valid_cache', [True, False])
async def test_phone_id_cache(
        taxi_grocery_market_gw, mockserver, personal, valid_cache,
):
    phone_number = '+78005553535'
    personal_phone_id = 'some-personal-phone-id'

    personal.check_request(
        personal_phone_id=personal_phone_id, phone=phone_number,
    )

    @mockserver.json_handler('/grocery-api/lavka/v1/api/v1/startup')
    def _mock_startup(request):
        return mockserver.make_response(
            status=200, json={'exists': True, 'available': True},
        )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/startup',
        headers={'Phone-Number': phone_number},
    )

    if not valid_cache:
        await taxi_grocery_market_gw.invalidate_caches()

    response = await taxi_grocery_market_gw.post(
        'lavka/v1/market-gw/v1/startup',
        headers={'Phone-Number': phone_number},
    )

    assert response.status == 200
    assert personal.times_phones_store_called() == (1 if valid_cache else 2)
