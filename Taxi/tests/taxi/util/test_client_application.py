import pytest

from taxi.util import client_application


@pytest.mark.parametrize(
    'app_header, expected_verion',
    [
        (
            'app_brand=turboapp,app_name=search_app_android_beta,'
            'app_ver1=1',
            (1, 0, 0),
        ),
        (
            'app_brand=yataxi,app_name=iphone,'
            'app_ver2=43,app_ver1=5,app_ver3=57433',
            (5, 43, 57433),
        ),
        (
            'ru.yandex.ytaxi/5.43.57433 '
            '(iPhone; iPhone10,4; iOS 13.5.1; Darwin)',
            None,
        ),
    ],
)
def test_version_default(app_header, expected_verion):
    app = client_application.get_client_application(app_header)

    if expected_verion:
        assert expected_verion == (app.major, app.minor, app.build)
    else:
        assert app is None
