import pytest

import localization.components as localication
from test_localization import conftest


@pytest.mark.translations(
    keyset_taximetre=conftest.TRANSLATIONS,
    override_aze=conftest.AZ_TRANSLATIONS,
    override_uber=conftest.AZ_TRANSLATIONS,
    override_yango=conftest.YANGO_TRANSLATIONS,
)
@pytest.mark.parametrize(
    'driver_app,key,lang,expected',
    [
        ['Uber', 'company', 'en', 'Uber'],
        ['yango', 'company', 'en', 'Yango'],
        ['yandex', 'company', 'en', 'Yandex'],
        ['yandex', 'company', 'ru', 'Яндекс'],
        ['yango', 'company', 'ru', 'Яндекс'],
        ['yango', 'strange_key', 'ru', 'strange_key'],
    ],
)
async def test_driver_localizer(
        library_context,
        load_json,
        mock_driver_profiles_app,
        driver_app,
        key,
        lang,
        expected,
):
    # arrange
    mock_driver_profiles_app(driver_app, lang)

    localaizer = localication.Localaizer(
        context=library_context,
        settings=None,
        activation_parameters=[['keyset_taximetre']],
    )

    # act
    translate = await localaizer.get_translation_for_driver(
        park_driver='park_driver', keyset='keyset_taximetre', key=key,
    )

    # assert
    assert translate == expected


@pytest.mark.translations(
    keyset_taximetre=conftest.TRANSLATIONS,
    override_aze=conftest.AZ_TRANSLATIONS,
    override_uber=conftest.AZ_TRANSLATIONS,
    override_yango=conftest.YANGO_TRANSLATIONS,
)
@pytest.mark.parametrize(
    'user_agent,key,lang,expected',
    [
        ['Taximeter-Uber 9.05 (1234)', 'company', 'en', 'Uber'],
        ['Taximeter-YanGo 9.05 (1234)', 'company', 'en', 'Yango'],
        ['Taximeter 9.05 (1234)', 'company', 'en', 'Yandex'],
        ['Taximeter 9.05 (1234)', 'company', 'ru', 'Яндекс'],
        ['Taximeter-YanGo 9.05 (1234)', 'company', 'ru', 'Яндекс'],
        ['Taximeter-YanGo 9.05 (1234)', 'strange_key', 'ru', 'strange_key'],
    ],
)
def test_pro_app_localizer(
        library_context, load_json, user_agent, key, lang, expected,
):
    # arrange
    localaizer = localication.Localaizer(
        context=library_context,
        settings=None,
        activation_parameters=[['keyset_taximetre']],
    )

    # act
    translate = localaizer.get_translation_for_pro_app(
        user_agent=user_agent, keyset='keyset_taximetre', key=key, locale=lang,
    )

    # assert
    assert translate == expected
