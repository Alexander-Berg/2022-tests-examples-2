import typing

import pytest

from test_driver_referrals import conftest


@pytest.mark.translations(
    taximeter_backend_driver_referrals=conftest.TRANSLATIONS,
)
@pytest.mark.translations(geoareas=conftest.TRANSLATIONS_GEOAREAS)
@pytest.mark.translations(tariff=conftest.TRANSLATIONS_TARIFF)
@pytest.mark.translations(notify=conftest.TRANSLATIONS_NOTIFY)
@pytest.mark.config(
    DRIVER_REFERRAL_WORDS_FOR_CODES_BY_COUNTRY={'__default__': ['ПРОМОКОД']},
    DRIVER_REFERRALS_PROXY_URLS_COUNTRY={
        '__default__': {'taxi': 'test/?{code}', 'eda': 'test/?{code}'},
    },
)
@pytest.mark.config(DRIVER_REFERRALS_ENABLE_USE_CACHE_REFERRAL_PROFILES=True)
@pytest.mark.now('2019-04-25 15:00:00')
@pytest.mark.parametrize(
    ('nearest_zone', 'expected_json'),
    [('moscow', 'bucket_for_moscow.json'), (None, 'bucket_for_any_zone.json')],
)
async def test_driver_v1_driver_referrals_driver_get(
        web_context,
        nearest_zone: typing.Optional[str],
        expected_json,
        web_app_client,
        mockserver,
        load_json,
        mock_get_query_positions_default,
        mock_get_nearest_zone,
):
    @mockserver.json_handler('/tariffs/v1/tariff_zones')
    async def _tariffs(request):
        return mockserver.make_response(
            json={'zones': [{'name': 'moscow'}]}, status=200,
        )

    mock_get_nearest_zone({}, default_zone=nearest_zone)

    async with conftest.TablesDiffCounts(
            web_context,
            {'referral_profiles': 1, 'cache_referral_profiles': 1},
    ):
        response = await web_app_client.get(
            '/driver/v1/driver-referrals/driver',
            headers={
                **conftest.COMMON_DRIVER_HEADERS,
                'X-YaTaxi-Park-Id': 'p',
                'X-YaTaxi-Driver-Profile-Id': 'd',
            },
        )
    assert response.status == 200

    content = await response.json()
    assert content == load_json(expected_json)

    @mockserver.json_handler('/parks/driver-profiles/list')
    def _(request):
        assert False

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def __(request):
        assert False

    async with conftest.TablesDiffCounts(web_context):
        response = await web_app_client.get(
            '/driver/v1/driver-referrals/driver',
            headers={
                **conftest.COMMON_DRIVER_HEADERS,
                'X-YaTaxi-Park-Id': 'p',
                'X-YaTaxi-Driver-Profile-Id': 'd',
            },
        )
    assert response.status == 200

    content = await response.json()
    assert content == load_json(expected_json)


async def test_experiment_couriers(
        web_app_client,
        client_experiments3,
        mock_driver_profiles_drivers_profiles,
        mock_get_query_positions_default,
        mock_fail_to_get_nearest_zone,
):
    client_experiments3.add_record(
        consumer='driver-referrals/couriers_referral_version',
        config_name='driver-referrals_couriers_referral_version',
        args=[{'name': 'courier_id', 'type': 'string', 'value': 111}],
        value={'taximeter': False},
    )
    mock_driver_profiles_drivers_profiles(eats_keys={'driver': 111})

    response = await web_app_client.get(
        '/driver/v1/driver-referrals/driver',
        headers={
            **conftest.COMMON_DRIVER_HEADERS,
            'X-YaTaxi-Park-Id': 'park',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}
