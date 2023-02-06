REAL_IP = '1.2.3.4'
USER_AGENT = (
    'ru.yandex.ytaxi/550.13.0.70417 (iPhone; iPhone8,4; iOS 12.1.4; Darwin)'
)
REQUEST_APPLICATION = set(
    (
        'app_ver3=0,app_brand=yataxi,app_ver2=13,platform_ver2=1,'
        'app_build=release,platform_ver1=12,app_ver1=550,'
        'platform_ver3=4,app_name=iphone'
    ).split(','),
)
ACCEPT_LANGUAGE = 'ru'


def assert_remote_headers(
        remote_request,
        expected_uid: str = None,
        expected_pass_flags: list = None,
):
    headers = remote_request.headers
    assert headers['X-Remote-IP'] == REAL_IP

    assert (
        set(headers['X-Request-Application'].split(',')) == REQUEST_APPLICATION
    )
    assert headers['X-Request-Language'] == ACCEPT_LANGUAGE

    if expected_uid is not None:
        assert headers['X-Yandex-UID'] == expected_uid
        assert headers['X-Yandex-Login'] == 'login'
    else:
        assert 'X-Yandex-UID' not in headers
        assert 'X-Yandex-Login' not in headers

    if expected_pass_flags is not None:
        _validate_flags(headers['X-YaTaxi-Pass-Flags'], expected_pass_flags)


def _validate_flags(pass_flags: str, expected: list):
    assert set(pass_flags.split(',')) == set(expected)
