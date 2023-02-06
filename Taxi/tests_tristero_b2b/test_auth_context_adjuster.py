async def test_adjusted_auth_context(
        taxi_tristero_b2b, mockserver, testpoint, taxi_config,
):
    """ auth_context should be adjusted from headers """

    app_ver1 = '600'
    app_ver2 = '32'
    app_ver3 = '0'
    platform_ver1 = '14'
    platform_ver2 = '4'
    platform_ver3 = '2'
    locale = 'ru'

    taxi_config.set(
        TRISTERO_B2B_DEFAULT_USER_AGENT=(
            'Mozilla/5.0 (iPhone; CPU iPhone OS '
            f'{platform_ver1}_{platform_ver2}_{platform_ver3} like Mac '
            'OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) '
            f'yandex-taxi/{app_ver1}.{app_ver2}.{app_ver3}.125308 '
            'YandexEatsKit/1.17.28 Superapp/Grocery'
        ),
    )

    @testpoint('adjusted_auth_context')
    def adjusted_auth_context_callback(auth_context):
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
        assert auth_context['locale'] == locale

    await taxi_tristero_b2b.post(
        '/tristero/v1/availability?vendor=beru',
        json={
            'position': {'location': [33.1, 55.1]},
            'delivery_date': '2020-09-09T13:16:00+00:00',
        },
    )
    assert adjusted_auth_context_callback.times_called == 1
