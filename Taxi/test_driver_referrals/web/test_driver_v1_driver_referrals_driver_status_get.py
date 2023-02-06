import pytest

from test_driver_referrals import conftest


@pytest.mark.translations(
    taximeter_backend_driver_referrals=conftest.TRANSLATIONS,
)
@pytest.mark.config(
    DRIVER_REFERRAL_WORDS_FOR_CODES_BY_COUNTRY={'__default__': ['ПРОМОКОД']},
)
async def test_driver_v1_driver_referrals_driver_status_get(
        web_app_client,
        mock_get_query_positions_default,
        mock_fail_to_get_nearest_zone,
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


@pytest.mark.translations(
    taximeter_backend_driver_referrals=conftest.TRANSLATIONS,
)
@pytest.mark.config(
    DRIVER_REFERRAL_WORDS_FOR_CODES_BY_COUNTRY={'__default__': ['ПРОМОКОД']},
)
@pytest.mark.pgsql('driver_referrals', files=['disabled.sql'])
@pytest.mark.now('2019-04-25 15:00:00')
async def test_status_disabled(
        web_app_client,
        mock_get_query_positions_default,
        mock_fail_to_get_nearest_zone,
):
    park_id = 'p'
    response = await web_app_client.get(
        '/driver/v1/driver-referrals/driver/status',
        headers={
            **conftest.COMMON_DRIVER_HEADERS,
            'X-YaTaxi-Park-Id': park_id,
            'X-YaTaxi-Driver-Profile-Id': 'd',
        },
    )
    assert response.status == 200

    content = await response.json()
    assert content == {}


@pytest.mark.now('2019-04-25 15:00:00')
@pytest.mark.translations(
    taximeter_backend_driver_referrals=conftest.TRANSLATIONS,
)
@pytest.mark.config(
    DRIVER_REFERRAL_WORDS_FOR_CODES_BY_COUNTRY={'__default__': ['ПРОМОКОД']},
)
@pytest.mark.pgsql(
    'driver_referrals', files=['disabled_generate_promocodes.sql'],
)
@pytest.mark.parametrize(
    ('park_id', 'driver_id', 'expected_answer'),
    [
        ['p2', 'd2', {}],
        [
            'p1',
            'd1',
            {
                'invite_friend': {
                    'title': 'Пригласи друга',
                    'subtitle': 'Стать водителем',
                    'show': True,
                },
            },
        ],
    ],
)
async def test_status_disabled_codegen(
        web_app_client,
        park_id,
        driver_id,
        expected_answer,
        mock_get_query_positions_default,
        mock_fail_to_get_nearest_zone,
):
    response = await web_app_client.get(
        '/driver/v1/driver-referrals/driver/status',
        headers={
            **conftest.COMMON_DRIVER_HEADERS,
            'X-YaTaxi-Park-Id': park_id,
            'X-YaTaxi-Driver-Profile-Id': driver_id,
        },
    )
    assert response.status == 200

    content = await response.json()
    assert content == expected_answer


@pytest.mark.translations(
    taximeter_backend_driver_referrals=conftest.TRANSLATIONS,
)
@pytest.mark.config(
    DRIVER_REFERRAL_WORDS_FOR_CODES_BY_COUNTRY={'__default__': ['ПРОМОКОД']},
)
@pytest.mark.config(
    DRIVER_REFERRALS_NOTIFICATIONS_BY_COUNTRIES={
        '__default__': {'taxi': ['create_new_account']},
    },
)
@pytest.mark.now('2019-04-25 15:00:00')
async def test_status_etag(
        web_context,
        web_app_client,
        mock_get_query_positions_default,
        mock_fail_to_get_nearest_zone,
):
    async with conftest.TablesDiffCounts(
            web_context, {'referral_profiles': 1, 'notifications': 1},
    ):
        response = await web_app_client.get(
            '/driver/v1/driver-referrals/driver/status',
            headers={
                **conftest.COMMON_DRIVER_HEADERS,
                'X-YaTaxi-Park-Id': 'p',
                'X-YaTaxi-Driver-Profile-Id': 'd',
            },
        )
    assert response.status == 200
    content = await response.json()
    assert content != {}

    etag = response.headers['ETag']
    async with conftest.TablesDiffCounts(web_context):
        response = await web_app_client.get(
            '/driver/v1/driver-referrals/driver/status',
            headers={
                **conftest.COMMON_DRIVER_HEADERS,
                'X-YaTaxi-Park-Id': 'p',
                'X-YaTaxi-Driver-Profile-Id': 'd',
                'If-None-Match': etag,
            },
        )
    assert response.status == 304


@pytest.mark.now('2019-04-25 15:00:00')
async def test_status_etag_changes(web_context):
    settings_cache = web_context.referral_settings_cache

    await settings_cache.refresh_cache()
    old_etag = settings_cache.get_etag('ru')

    await settings_cache.refresh_cache()
    assert old_etag == settings_cache.get_etag('ru')

    async with web_context.pg.master_pool.acquire() as conn:
        await conn.execute('DELETE FROM rules;')
    await settings_cache.refresh_cache()
    assert old_etag != settings_cache.get_etag('ru')
