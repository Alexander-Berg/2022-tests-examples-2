import pytest

from taxi.util import useragent


@pytest.mark.parametrize('ua_str,application,app_version,platform_version', [
    (
        'yandex-taxi/3.7.2.5434 Android/5.1.1 (samsung; SM-G920F)',
        'android',
        (3, 7, 2),
        (5, 1, 1)
    ),

    (
        'ru.yandex.ytaxi/3.32.3572 (iPhone; iPhone7,1; iOS 9.1; Darwin)',
        'iphone',
        (3, 32, 3572),
        (9, 1)
    ),

    (
        'yandex-taxi/3.7.1 Android/6.0.0 (asus; some-model)',
        'android',
        (3, 7, 1),
        (6, 0, 0)
    ),

    (
        'ru.yandex.ytaxi/3.33.2245.1 (iPhone; iPhone7,1; iOS 8.0.2; Darwin)',
        'iphone',
        (3, 33, 2245),
        (8, 0, 2)
    ),

    # Future versions
    (
        'yandex-taxi/3.7.3 Android/10.11.12 (asus; some-model)',
        'android',
        (3, 7, 3),
        (10, 11, 12)
    ),

    (
        'ru.yandex.ytaxi/3.50.100 (iPhone; iPhone7,1; iOS 10.15; Darwin)',
        'iphone',
        (3, 50, 100),
        (10, 15)
    ),

    # Broken versions
    # TAXIBACKEND-8521
    (
        'pull-742/ru.yandex.ytaxi/3.91.8035 (iPhone; iPhone9,4; iOS 10.3.3; Darwin)',
        'iphone',
        (3, 91, 8035),
        (10, 3, 3)
    ),
])
def test_version_parsing(ua_str, application,
                         app_version, platform_version):
    ua = useragent.ClientApp(ua_str)
    assert ua.application == application
    assert ua.version == app_version
    assert ua.platform_version == platform_version
