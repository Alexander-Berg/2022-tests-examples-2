import pytest

from taxi import translations

from taxi_selfreg.generated.web import web_context as context_module

LANG_RU = 'ru'
LANG_EN = 'en'
LANG_UZ = 'uz'
LANG_KZ = 'kz'

TRANSLATIONS = {'Color': {'ru': 'красный', 'en': 'red', 'uz': ''}}


@pytest.mark.parametrize(
    'language, expect_value',
    [
        (LANG_RU, 'красный'),
        (LANG_EN, 'red'),
        (LANG_UZ, 'красный'),
        (LANG_KZ, 'красный'),
    ],
)
@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
def test_localizer_fallback(
        web_context: context_module.Context, language, expect_value,
):
    localizer = web_context.localizer.driver_messages
    assert expect_value == localizer.translate('Color', language)


@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
def test_localizer_key_not_found(web_context: context_module.Context):
    localizer = web_context.localizer.driver_messages
    with pytest.raises(translations.TranslationNotFoundError):
        localizer.translate('SomeKey', 'ru')


@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
def test_localizer_key_not_found_no_throw(web_context: context_module.Context):
    localizer = web_context.localizer.driver_messages
    assert localizer.translate_no_throw('SomeKey', 'ru') is None


@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
def test_localizer_key_not_found_fallback_to_key(
        web_context: context_module.Context,
):
    localizer = web_context.localizer.driver_messages
    assert localizer.translate_or_get_key('SomeKey', 'ru') == 'SomeKey'
