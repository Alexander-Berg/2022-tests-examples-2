from driver_lessons.generated.web import web_context as context_module

EXPECT_CITIES = {
    'Москва': 'rus',
    'Санкт-Петербург': 'rus',
    'Хельсинки': 'fin',
    'Минск': 'blr',
    'Гомель': 'blr',
    'Таллин': 'est',
}

EXPECT_COUNTRIES = {'rus', 'fin', 'blr', 'est'}


async def test_cities_cache(web_app, web_context: context_module.Context):
    cities_cache = web_context.cities_cache
    cities_storage = cities_cache._data  # pylint: disable=W0212
    assert cities_storage == EXPECT_CITIES

    countries_set = cities_cache.get_countries()
    assert countries_set == EXPECT_COUNTRIES

    assert cities_cache.get_country_id('Москва') == 'rus'
    assert cities_cache.get_country_id('Нью-Йорк') is None
