import pytest


def eats_full_test_search(data: dict):
    """
    Задает данные для кейсета eats-full-text-search
    """
    return pytest.mark.translations(**{'eats-full-text-search': data})


def eats_full_test_search_ru(data: dict):
    """
    Задает данные для кейсета eats-catalog
    и ru локали
    """
    result = {}
    for key, value in data.items():
        result[key] = {'ru': value}
    return eats_full_test_search(result)


_DEFAULT_TRANSLATIONS_DATA = {
    'menu.products_title': 'Товары',
    'menu.categories_title': 'Категории',
    'menu.other_categories_title': 'Другие категории',
    'menu.other_products_title': 'Совпадения в других категориях',
    'menu.no_items_in_category': (
        'В категории "%(category)s" ничего не найдено'
    ),
    'catalog.show_more': 'Показать еще',
    'common.empty_response_header': 'Увы, ничего не найдено',
}


DEFAULT = eats_full_test_search_ru(_DEFAULT_TRANSLATIONS_DATA)
