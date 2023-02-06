import pytest

from eda_etl.layer.yt.ods.lavka_backend.order.impl import application_platform_extractor


@pytest.mark.parametrize(
    'expected_app, raw_value',
    [
        ('eda_webview_android', {
            'app_info': 'app_brand=yataxi,app_name=web,app_ver1=2',
            'user_agent': 'Mozilla/5.0 (Linux; Android 9; vivo 1906 Build/PKQ1.190616.001; wv) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.198 Mobile Safari/537.36 '
                          'EatsApp_Android/2.36.1 EatsKit/1.12.0'
        }),
        ('eda_webview_ios', {
            'app_info': 'app_brand=yataxi,app_name=web,app_ver1=2',
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/605.1.15 '
                          '(KHTML, like Gecko) YandexEatsKit/1.7.18 EatsApp_iOS/5.6.0'
        }),
        ('lavka_android', {
            'app_info': 'app_brand=lavka,app_build=release,app_ver3=2,device_make=sony,app_name=lavka_android,'
                        'device_model=h4213,app_ver2=2,platform_ver1=9,app_ver1=1',
            'user_agent': 'Mozilla/5.0 (Linux; Android 9; H4213 Build/50.2.A.3.77; wv) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.101 Mobile Safari/537.36 '
                          'com.yandex.lavka/1.2.2.1035590 Android/9 (Sony; H4213) Lavka/Standalone EatsKit/1.24.0'
        }),
        ('lavka_ios', {
            'app_info': 'app_brand=lavka,app_ver3=3,app_name=lavka_iphone,app_build=release,platform_ver2=2,'
                        'platform_ver1=14,app_ver1=1,app_ver2=1',
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 '
                          '(KHTML, like Gecko) yandex-lavka/1.1.3.78497 YandexEatsKit/1.7.12 Lavka/Standalone'
        }),
        ('mbro_android', {
            'app_info': 'app_brand=turboapp,app_name=mbro_android,app_ver1=1',
            'user_agent': 'Mozilla/5.0 (Linux; arm_64; Android 9; SM-G950F) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/87.0.4280.141 YaBrowser/20.12.2.68.00 SA/3 Mobile Safari/537.36'
        }),
        ('mbro_ios', {
            'app_info': 'app_brand=turboapp,app_name=mbro_iphone,app_ver1=1',
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 '
                          '(KHTML, like Gecko) Version/14.0 YaBrowser/20.11.1.253.10 SA/3 Mobile/15E148 Safari/604.1'
        }),
        ('mobileweb_android', {
            'app_info': 'app_brand=yataxi,app_name=web,app_ver1=2',
            'user_agent': 'Mozilla/5.0 (Linux; Android 9; SM-J610FN Build/PPR1.180610.011; wv) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.93 Mobile Safari/537.36 '
                          'Beru/2.87 (Android/9; SM-J610FN/samsung)'
        }),
        ('mobileweb_ios', {
            'app_info': 'app_brand=yataxi,app_name=web,app_ver1=2',
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 '
                          '(KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1'
        }),
        ('mobileweb_yango_android', {
            'app_info': 'app_brand=yango,app_ver3=0,device_make=xiaomi,app_name=mobileweb_yango_android,'
                        'app_build=release,device_model=m2002j9g,app_ver2=23,app_ver1=4,platform_ver1=11',
            'user_agent': 'Mozilla/5.0 (Linux; Android 11; M2002J9G Build/RKQ1.200826.002; wv) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.181 '
                          'Mobile Safari/537.36 yango/4.23.0.121836 Android/11 (Xiaomi; M2002J9G) '
                          'Yango/Grocery EatsKit/1.25.0'
        }),
        ('mobileweb_yango_ios', {
            'app_info': 'app_brand=yango,app_ver3=0,device_make=apple,app_name=mobileweb_yango_iphone,'
                        'platform_ver2=3,app_build=release,app_ver2=20,app_ver1=600,platform_ver1=14',
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 '
                          '(KHTML, like Gecko) yango/600.20.0.99167 YandexEatsKit/1.17.24 Yango/Grocery'
        }),
        ('search_app_android', {
            'app_info': 'app_brand=turboapp,app_name=search_app_android,app_ver1=1',
            'user_agent': 'Mozilla/5.0 (Linux; arm; Android 9; JAT-LX1) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/87.0.4280.141 YaApp_Android/20.122.0 YaSearchBrowser/20.122.0 BroPP/1.0 SA/3 '
                          'Mobile Safari/537.36'
        }),
        ('search_app_ios', {
            'app_info': 'app_brand=turboapp,app_name=search_app_iphone,app_ver1=1',
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 '
                          '(KHTML, like Gecko) Mobile/15E148 YaBrowser/19.5.2.38.10 YaApp_iOS/49.00 '
                          'YaApp_iOS_Browser/49.00 Safari/604.1 SA/3'
        }),
        ('superapp_android', {
            'app_info': 'app_brand=yataxi,app_ver3=0,device_make=samsung,app_name=mobileweb_android,app_build=release,'
                        'device_model=sm-g960f,app_ver2=16,app_ver1=4,platform_ver1=10',
            'user_agent': 'Mozilla/5.0 (Linux; Android 10; SM-G960F Build/QP1A.190711.020; wv) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.101 Mobile Safari/537.36 '
                          'yandex-taxi/4.16.0.121761 Android/10 (samsung; SM-G960F) Superapp/Grocery EatsKit/1.24.0'
        }),
        ('superapp_ios', {
            'app_info': 'app_brand=yataxi,app_ver3=0,device_make=apple,app_name=mobileweb_iphone,platform_ver2=5,'
                        'app_build=release,app_ver2=26,app_ver1=600,platform_ver1=13',
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 '
                          '(KHTML, like Gecko) yandex-taxi/600.26.0.112307 YandexEatsKit/1.17.27 Superapp/Grocery'
        }),
        ('web', {
            'app_info': 'app_brand=yataxi,app_name=web,app_ver1=2',
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 '
                          '(KHTML, like Gecko) Version/14.0.2 Safari/605.1.15'
        }),
        ('yangodeli_android', {
            'app_info': 'app_brand=yangodeli,app_build=release,app_ver3=2,device_make=huawei,'
                        'app_name=yangodeli_android,device_model=lya-l29,app_ver2=2,platform_ver1=10,app_ver1=1',
            'user_agent': 'Mozilla/5.0 (Linux; Android 10; LYA-L29 Build/HUAWEILYA-L29; wv) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.181 Mobile Safari/537.36 '
                          'com.yandex.yangodeli/1.2.2.1035590 Android/10 (HUAWEI; LYA-L29) '
                          'YangoDeli/Standalone EatsKit/1.24.0'
        }),
        ('yangodeli_ios', {
            'app_info': 'app_brand=yangodeli,device_make=apple,app_name=yangodeli_iphone,platform_ver2=3,'
                        'app_build=release,platform_ver1=14',
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 '
                          '(KHTML, like Gecko) yango-deli/1.2.5.102579 YandexEatsKit/1.17.23 YangoDeli/Standalone'
        }),
    ]
)
def test_lavka_backend_normal_apps(expected_app, raw_value):
    assert application_platform_extractor('app_info', 'user_agent')(raw_value) == expected_app
