import pytest


@pytest.mark.parametrize(
    'app_str, version, version_type, platform, '
    'brand, build_type, platform_version',
    [
        ('vezet', '1.2 (3)', 'vezet', 'ios', '', '', ''),
        ('taximeter', '9.24 (999)', '', 'android', '', '', ''),
        ('taximeter', '9.24 (999)', '', '', '', '', ''),
        ('taximeter', '9.24 (999)', 'beta', 'android', '', '', ''),
        ('taximeter', '9.24 (999)', 'beta', 'ios', '', '', ''),
        ('taximeter', '9.24 (999)', 'embedded', 'android', '', '', ''),
        ('taximeter', '9.24 (999)', 'beta', 'ios', 'yandex', 'beta', '15.0.1'),
        (
            'uberdriver',
            '9.24 (999)',
            'uber',
            'android',
            'uber',
            'beta',
            '15.0.1',
        ),
        ('taximeter', '9.24 (999)', 'yango', 'android', 'yango', '', '15.0.1'),
        ('vezet', '9.24 (999)', 'vezet', 'ios', 'vezet', 'x', '15.0.1'),
    ],
)
async def test_auth_ok(
        taxi_userver_sample,
        app_str,
        version,
        version_type,
        platform,
        brand,
        build_type,
        platform_version,
):
    response = await taxi_userver_sample.post(
        'driver/v1/userver-sample/v1/test',
        headers={
            'X-YaTaxi-Park-Id': 'test-park-it1',
            'X-YaTaxi-Driver-Profile-Id': 'test-profile-id1',
            'X-Request-Application-Version': version,
            'X-Request-Version-Type': version_type,
            'X-Request-Platform': platform,
            'X-Request-Application': app_str,
            'X-Request-Application-Brand': brand,
            'X-Request-Application-Build-Type': build_type,
            'X-Request-Platform-Version': platform_version,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'park-id': 'test-park-it1',
        'driver-profile-id': 'test-profile-id1',
        'application': app_str,
        'version-type': version_type,
        'version': version,
        'platform': platform if platform else 'android',
        'brand': brand,
        'build_type': build_type,
        'platform_version': platform_version,
    }


async def test_auth_fail(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'driver/v1/userver-sample/v1/test',
        headers={
            'X-Request-Application-Version': '1.2 (3)',
            'X-Request-Version-Type': 'vezet',
            'X-Request-Platform': 'ios',
            'X-Request-Application': 'vezet',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'park-id': 'none',
        'driver-profile-id': 'none',
        'application': 'none',
        'version-type': 'none',
        'version': 'none',
        'platform': 'none',
        'brand': 'none',
        'build_type': 'none',
        'platform_version': 'none',
    }


async def test_auth_passport(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'driver/v1/userver-sample/v1/test',
        headers={
            'X-Yandex-UID': 'passport_uid',
            'X-Request-Application-Version': '1.2 (3)',
            'X-Request-Version-Type': '',
            'X-Request-Platform': 'ios',
            'X-Request-Application': 'taximeter',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'park-id': 'none',
        'driver-profile-id': 'none',
        'application': 'taximeter',
        'version-type': '',
        'version': '1.2 (3)',
        'platform': 'ios',
        'brand': '',
        'build_type': '',
        'platform_version': '',
        'passport_uid': 'passport_uid',
    }
