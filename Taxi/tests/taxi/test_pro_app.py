import dataclasses
from typing import Optional

import pytest

from taxi import pro_app


def test_version_to_from_str_ok():
    assert str(pro_app.parse_app_version('8.70 (1133)')) == '8.70 (1133)'


@pytest.mark.parametrize(
    'str_version', ['8 (1133)', '8.1 1133', '8.5 (1133.1)', '', '1'],
)
def test_version_to_from_str_err(str_version):
    with pytest.raises(ValueError):
        pro_app.parse_app_version(str_version)


@pytest.mark.parametrize(
    'user_agent_str, expected_result',
    [
        (
            'Taximeter 8.70 (1133)',
            pro_app.ProApp(
                version=pro_app.AppVersion(8, 70, 1133),
                version_type=pro_app.VersionType.PRODUCTION,
                platform=pro_app.Platform.ANDROID,
                brand=pro_app.Brand.YANDEX,
                build_type=pro_app.BuildType.DEFAULT,
                platform_version=None,
            ),
        ),
        (
            'Taximeter 8.17 (3322) ios',
            pro_app.ProApp(
                version=pro_app.AppVersion(8, 17, 3322),
                version_type=pro_app.VersionType.PRODUCTION,
                platform=pro_app.Platform.IOS,
                brand=pro_app.Brand.YANDEX,
                build_type=pro_app.BuildType.DEFAULT,
                platform_version=None,
            ),
        ),
        (
            'Taximeter-AZ 8.67 (1111)',
            pro_app.ProApp(
                version=pro_app.AppVersion(8, 67, 1111),
                version_type=pro_app.VersionType.AZERBAIJAN,
                platform=pro_app.Platform.ANDROID,
                brand=pro_app.Brand.AZERBAIJAN,
                build_type=pro_app.BuildType.DEFAULT,
                platform_version=None,
            ),
        ),
        (
            'Taximeter-Beta 8.71 (1192)',
            pro_app.ProApp(
                version=pro_app.AppVersion(8, 71, 1192),
                version_type=pro_app.VersionType.BETA,
                platform=pro_app.Platform.ANDROID,
                brand=pro_app.Brand.YANDEX,
                build_type=pro_app.BuildType.BETA,
                platform_version=None,
            ),
        ),
        (
            'Taximeter-X 8.72 (1198)',
            pro_app.ProApp(
                version=pro_app.AppVersion(8, 72, 1198),
                version_type=pro_app.VersionType.EXPERIMENTAL,
                platform=pro_app.Platform.ANDROID,
                brand=pro_app.Brand.YANDEX,
                build_type=pro_app.BuildType.EXPERIMENTAL,
                platform_version=None,
            ),
        ),
        (
            'Taximeter-SDC 8.65 (123)',
            pro_app.ProApp(
                version=pro_app.AppVersion(8, 65, 123),
                version_type=pro_app.VersionType.SDC,
                platform=pro_app.Platform.ANDROID,
                brand=pro_app.Brand.YANDEX,
                build_type=pro_app.BuildType.SDC,
                platform_version=None,
            ),
        ),
        (
            'Taximeter-Uber 9.05 (1234)',
            pro_app.ProApp(
                version=pro_app.AppVersion(9, 5, 1234),
                version_type=pro_app.VersionType.UBER,
                platform=pro_app.Platform.ANDROID,
                brand=pro_app.Brand.UBER,
                build_type=pro_app.BuildType.DEFAULT,
                platform_version=None,
            ),
        ),
        (
            'Taximeter-YanGo 9.10 (1234)',
            pro_app.ProApp(
                version=pro_app.AppVersion(9, 10, 1234),
                version_type=pro_app.VersionType.YANGO,
                platform=pro_app.Platform.ANDROID,
                brand=pro_app.Brand.YANGO,
                build_type=pro_app.BuildType.DEFAULT,
                platform_version=None,
            ),
        ),
        (
            'Taximeter-Vezet 9.10 (1234)',
            pro_app.ProApp(
                version=pro_app.AppVersion(9, 10, 1234),
                version_type=pro_app.VersionType.VEZET,
                platform=pro_app.Platform.ANDROID,
                brand=pro_app.Brand.VEZET,
                build_type=pro_app.BuildType.DEFAULT,
                platform_version=None,
            ),
        ),
        (
            'Taximeter-Embedded 9.10 (1234)',
            pro_app.ProApp(
                version=pro_app.AppVersion(9, 10, 1234),
                version_type=pro_app.VersionType.EMBEDDED,
                platform=pro_app.Platform.ANDROID,
                brand=pro_app.Brand.YANDEX,
                build_type=pro_app.BuildType.DEFAULT,
                platform_version=None,
            ),
        ),
        (
            # User-Agent is case-insensitive
            'tAxImEtEr-eMbEdDeD 9.10 (1234)',
            pro_app.ProApp(
                version=pro_app.AppVersion(9, 10, 1234),
                version_type=pro_app.VersionType.EMBEDDED,
                platform=pro_app.Platform.ANDROID,
                brand=pro_app.Brand.YANDEX,
                build_type=pro_app.BuildType.DEFAULT,
                platform_version=None,
            ),
        ),
        (
            'app:pro version:10.12 brand:yandex build_type:x build:23455 platform:ios platform_version:13.0.1',  # noqa: E501
            pro_app.ProApp(
                version=pro_app.AppVersion(10, 12, 23455),
                version_type=pro_app.VersionType.EXPERIMENTAL,
                platform=pro_app.Platform.IOS,
                brand=pro_app.Brand.YANDEX,
                build_type=pro_app.BuildType.EXPERIMENTAL,
                platform_version=pro_app.PlatformVersion(13, 0, 1),
            ),
        ),
        (
            'app:pro brand:yango version:10.12 build_type:sdc build:23455 platform:ios platform_version:15.0.1',  # noqa: E501
            pro_app.ProApp(
                version=pro_app.AppVersion(10, 12, 23455),
                version_type=pro_app.VersionType.YANGO,
                platform=pro_app.Platform.IOS,
                brand=pro_app.Brand.YANGO,
                build_type=pro_app.BuildType.SDC,
                platform_version=pro_app.PlatformVersion(15, 0, 1),
            ),
        ),
    ],
)
def test_from_useragent_ok(user_agent_str, expected_result):
    assert pro_app.app_from_user_agent(user_agent_str) == expected_result


@pytest.mark.parametrize(
    'user_agent_str',
    (
        'SDC Taximeter 8.65',
        'taximeter-yango\t9.09 (1719)',
        'Taximeter-ajaj 8.70 (1133)',
        'trympyrym 8.70 (1133)',
        'TaXiMeteR-x  9.09    (1719) ',
        'version:10.12 build:23455 platform:ios platform_version:15.0.1',
        'app:taximeter version:11.12 platform:android platform_version:12.0',
        'app:pro version:11.12 platform:ondroid platform_version:12.0',
        'app:pro brand:bad_brand version:10.12 build_type:bad_build_type build:23455 platform:bad_platform platform_version:15.0.1',  # noqa: E501
        'app:pro brant:yango version:10.12 platform:ios',
        'app:pro brand:yandex version:10.12 platform_version:15.0.1',
        'app:pro brand:yandex version:10.12 platform:ios',
    ),
)
def test_from_useragent_error(user_agent_str):
    with pytest.raises((KeyError, ValueError)):
        assert pro_app.app_from_user_agent(user_agent_str)


@dataclasses.dataclass
class MockProAppParams:
    version: str
    platform: str
    version_type: Optional[str] = None
    platform_version: Optional[str] = None
    brand: Optional[str] = None
    build_type: Optional[str] = None


@pytest.mark.parametrize(
    'params,expected_result',
    (
        (
            MockProAppParams(
                version='9.10 (1234)',
                platform='android',
                version_type='vezet',
            ),
            pro_app.ProApp(
                version=pro_app.AppVersion(9, 10, 1234),
                version_type=pro_app.VersionType.VEZET,
                platform=pro_app.Platform.ANDROID,
                brand=pro_app.Brand.VEZET,
                build_type=pro_app.BuildType.DEFAULT,
                platform_version=None,
            ),
        ),
        (
            MockProAppParams(
                version='10.12 (23455)',
                platform='ios',
                platform_version='13.0.1',
                brand='yandex',
                build_type='x',
            ),
            pro_app.ProApp(
                version=pro_app.AppVersion(10, 12, 23455),
                version_type=pro_app.VersionType.EXPERIMENTAL,
                platform=pro_app.Platform.IOS,
                brand=pro_app.Brand.YANDEX,
                build_type=pro_app.BuildType.EXPERIMENTAL,
                platform_version=pro_app.PlatformVersion(13, 0, 1),
            ),
        ),
        (
            MockProAppParams(
                version='13.22 (2121)',
                platform='android',
                platform_version='15.0.1',
                brand='yango',
                build_type='beta',
            ),
            pro_app.ProApp(
                version=pro_app.AppVersion(13, 22, 2121),
                version_type=pro_app.VersionType.YANGO,
                platform=pro_app.Platform.ANDROID,
                brand=pro_app.Brand.YANGO,
                build_type=pro_app.BuildType.BETA,
                platform_version=pro_app.PlatformVersion(15, 0, 1),
            ),
        ),
        (
            MockProAppParams(
                version='0.0 (0)',
                platform='android',
                platform_version='',
                brand='',
                build_type='',
                version_type='',
            ),
            pro_app.ProApp(
                version=pro_app.AppVersion(0, 0, 0),
                version_type=pro_app.VersionType.PRODUCTION,
                platform=pro_app.Platform.ANDROID,
                brand=pro_app.Brand.YANDEX,
                build_type=pro_app.BuildType.DEFAULT,
                platform_version=None,
            ),
        ),
    ),
)
def test_app_from_params_ok(
        params: MockProAppParams, expected_result: pro_app.ProApp,
):
    assert (
        pro_app.app_from_params(**dataclasses.asdict(params))
        == expected_result
    )


@pytest.mark.parametrize(
    'params',
    (
        MockProAppParams(
            version='13.22 (2121)', platform='android', brand='yango',
        ),
        MockProAppParams(
            version='13.22 (2121)',
            platform='android',
            platform_version='15.0.1',
        ),
    ),
)
def test_app_from_params_error(params: MockProAppParams):
    with pytest.raises((KeyError, ValueError)):
        assert pro_app.app_from_params(**dataclasses.asdict(params))
