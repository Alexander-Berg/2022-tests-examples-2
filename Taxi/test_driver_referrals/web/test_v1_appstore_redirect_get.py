import pytest

from test_driver_referrals import conftest


@pytest.mark.translations(
    taximeter_backend_driver_referrals=conftest.TRANSLATIONS,
)
@pytest.mark.parametrize(
    'code,user_agent,is_share_preview_enabled,expected',
    [
        [
            'ПРОМОКОД1',
            (
                'Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_3 like Mac OS X) '
                'AppleWebKit/536.26 (KHTML, like Gecko) Mobile/10B329'
            ),
            False,
            'https://apps.apple.com/app/id1496904594',
        ],
        [
            'ПРОМОКОД1',
            'user_agent Android 6.0',
            False,
            (
                'https://play.google.com/store/apps/details'
                '?id=ru.yandex.taximeter'
                '&utm_source=referral'
                '&utm_content=ПРОМОКОД1'
            ),
        ],
        pytest.param(
            'ПРОМОКОД1',
            'user_agent Android 6.0',
            True,
            """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Яндекс.Про</title>

    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="Подключайся к Яндекс.Про" />
    <meta name="twitter:description" content="С кодом ПРОМОКОД1" />
    <meta name="twitter:image" content="https://s3.yandex.net/image.jpg" />

    <meta property="og:title"					content="Подключайся к Яндекс.Про" />
    <meta property="og:description"				content="С кодом ПРОМОКОД1" />
    <meta property="og:image"					content="https://s3.yandex.net/image.jpg" />
    <meta property="og:url" content="https://play.google.com/store/apps/details?id=ru.yandex.taximeter&utm_source=referral&utm_content=ПРОМОКОД1" />
    <meta property="og:site_name" content="Яндекс.Про" />
    <meta property="og:locale" content="ru" />

    <script>
        window.location = "https://play.google.com/store/apps/details?id=ru.yandex.taximeter&utm_source=referral&utm_content=ПРОМОКОД1";
    </script>
</head>
<body>
<p>Please wait, you are being redirected...</p>
</body>""",  # noqa: E501 line too long
            marks=pytest.mark.config(
                DRIVER_REFERRALS_SHARE_PREVIEW_IS_ENABLED=True,
                DRIVER_REFERRALS_SHARE_SETTINGS={
                    '__default__': {
                        '__default__': {
                            'preview_image': '',
                            'description_key': 'share_description_default',
                            'title_key': 'share_title_default',
                            'site_title_key': 'share_site_title_default',
                        },
                    },
                    'rus': {
                        '__default__': {
                            'preview_image': '',
                            'description_key': 'share_description_default',
                            'title_key': 'share_title_default',
                            'site_title_key': 'share_site_title_default',
                        },
                        'Москва': {
                            'preview_image': 'https://s3.yandex.net/image.jpg',
                            'description_key': 'share_description_default',
                            'title_key': 'share_title_default',
                            'site_title_key': 'share_site_title_default',
                        },
                    },
                },
            ),
        ),
    ],
)
async def test_v1_appstore_redirect_get(
        web_app_client,
        code,
        user_agent,
        is_share_preview_enabled,
        expected,
        mock_get_query_positions_default,
        mock_fail_to_get_nearest_zone,
):
    response = await web_app_client.get(
        '/v1/appstore/redirect',
        params={'code': code},
        headers={'User-Agent': user_agent},
        allow_redirects=False,
    )
    if is_share_preview_enabled:
        assert response.status == 200
        assert (await response.text()) == expected
    else:
        assert response.status == 302
        assert 'Location' in response.headers
        assert response.headers['Location'] == expected
