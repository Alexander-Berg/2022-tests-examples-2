# pylint: disable=W0612,C0103,C5521

import pytest

from menu_transformer.content import filters
from menu_transformer.content.filters.base_filter import BaseFilter
from test_menu_transformer import common


def _test_base(_filter: BaseFilter, _input: str, result: str):
    text = _filter.filter(_input)
    return text == result


@pytest.mark.parametrize(
    'arguments, filtered_string, normalized_string',
    [
        (
            {
                'arguments': {
                    '/\\s+Б\\.\\sЮ\\.\\s+/ui': ' Б.Ю. ',
                    '/\\s+Нежныйс\\s+/ui': ' Нежный с ',
                    '/\\s+вяз(\\.)?\\s+/ui': ' вязкий ',
                },
            },
            ' вяз.  нежныйс кремом     Б. Ю.  Александров',
            ' вязкий Нежный с кремом Б.Ю. Александров',
        ),
        ({'arguments': {}}, 'Не изменится строка', 'Не изменится строка'),
        (
            {'arguments': {'/\\s+Нежныйс\\s+/ui': ' Нежный с '}},
            'Не изменится строка, так как не нашелся паттерн',
            'Не изменится строка, так как не нашелся паттерн',
        ),
        (
            {
                'arguments': {
                    '/(вода\\s+.+)\\s+газ(\\.)?\\s+(.+)/ui': (
                        '$1 газированная $3'
                    ),
                    '/([\\.\\,])/ui': '$1 ',
                },
            },
            'Тест с точкой.Вот',
            'Тест с точкой. Вот',
        ),
        (
            {
                'arguments': {
                    '/([\\.\\,])/ui': '$1 ',
                    '/(вода\\s+.+)\\s+газ(\\.)?\\s+(.+)/ui': (
                        '$1 газированная $3'
                    ),
                },
            },
            'вода .газ.в бутылке',
            'вода . газированная в бутылке',
        ),
        (
            {
                'arguments': {
                    '/(вода\\s+.+)\\s+газ(\\.)?\\s+(.+)/ui': (
                        '$1 газированная $3'
                    ),
                    '/([\\.\\,])/ui': '$1 ',
                },
            },
            'вода .газ.в бутылке',
            'вода . газ. в бутылке',
        ),
        (
            {'arguments': {'/([\\.\\,])/ui': '$1 '}},
            'Вода минеральная Нарзан лечебно-столовая газированная 1.',
            'Вода минеральная Нарзан лечебно-столовая газированная 1. ',
        ),
        (
            {'arguments': {'/(?<!\\-)\\d{2,}\\s*(?:г|мл)\\.?/ui': ''}},
            'Название',
            'Название',
        ),
        (
            {'arguments': {r'/(к)олг\W/ui': '$1олготки$2'}},
            'Название',
            'Название',
        ),
        (
            {'arguments': {r'/_?ВЕС(?:\s|$)/ui': ''}},
            'Цыпленок LaFerme Фермерский, вес',
            'Цыпленок LaFerme Фермерский, ',
        ),
        (
            {'arguments': {r'/_?ВЕС(?:\s|$)/u': ' '}},
            'Цыпленок LaFerme Фермерский, вес',
            'Цыпленок LaFerme Фермерский, вес',
        ),
        (
            {'arguments': {'/в асс(\\.)?\\s+/ui': 'в ассортименте '}},
            'Конструктор Ausini в асс Ост-ком :5/300',
            'Конструктор Ausini в ассортименте Ост-ком :5/300',
        ),
    ],
)
async def test_replacement_filter(
        arguments, filtered_string, normalized_string,
):
    replacement_filter = filters.ReplacementFilter(**arguments)
    text = replacement_filter.filter(filtered_string)
    assert text == normalized_string


@pytest.mark.parametrize(
    'filtered_string, normalized_string',
    [
        ('   Проверка пробелов до и после  ', 'Проверка пробелов до и после'),
        ('неизвестаня строка', 'неизвестаня строка'),
        ('   пробелы спереди', 'пробелы спереди'),
        ('пробелы сзади     ', 'пробелы сзади'),
    ],
)
async def test_punctuation_filter(filtered_string, normalized_string):
    punctuation_filter = filters.PunctuationFilter()
    text = punctuation_filter.filter(filtered_string)
    assert text == normalized_string


@pytest.mark.parametrize(
    'filtered_string, normalized_string',
    [
        ('<br>Какой-то текст</br>', 'Какой-то текст'),
        ('<H1>Какой-то<br> текст</H1>', 'Какой-то текст'),
        ('какой-то текст', 'какой-то текст'),
        ('какой-то <br />текст', 'какой-то текст'),
        ('<span class=_Xbe>Московская обл', 'Московская обл'),
        ('122 < 123', '122 < 123'),
        ('122 < 123, а 122 > 121', '122 < 123, а 122 > 121'),
    ],
)
async def test_html_tags_filter(filtered_string, normalized_string):
    html_tags_filter = filters.HtmlTagsFilter()
    text = html_tags_filter.filter(filtered_string)
    assert text == normalized_string


@pytest.mark.parametrize(
    'filtered_string, normalized_string',
    [
        ('кАкой-То Текст', 'КАкой-То Текст'),
        ('какой-то текст', 'Какой-то текст'),
        ('КАКОЙ-ТО ТЕКСТ', 'КАКОЙ-ТО ТЕКСТ'),
        ('1) текст', '1) текст'),
        ('1) ТЕКСТ', '1) ТЕКСТ'),
    ],
)
async def test_capitalize_first_letter_filter(
        filtered_string, normalized_string,
):
    capitalize_first_letter_filter = filters.CapitalizeFirstLetterFilter()
    text = capitalize_first_letter_filter.filter(filtered_string)
    assert text == normalized_string


@pytest.mark.parametrize(
    'filtered_string, normalized_string',
    [
        ('кАкой-То Текст. и Тут', 'Какой-то текст. И тут'),
        ('кАкой-То Текст', 'Какой-то текст'),
        ('1) кАкой-То Текст', '1) какой-то текст'),
        ('1. кАкой-То Текст', '1. Какой-то текст'),
        ('1.кАкой-То Текст', '1.какой-то текст'),
    ],
)
async def test_capitalize_first_letter_by_sentence_filter(
        filtered_string, normalized_string,
):
    capitalize_first_letter_by_sentence_filter = (
        filters.CapitalizeFirstLetterBySentenceFilter()
    )
    text = capitalize_first_letter_by_sentence_filter.filter(filtered_string)
    assert text == normalized_string


@pytest.mark.parametrize(
    'arguments, filtered_string, normalized_string',
    [
        (
            {
                'arguments': [
                    'replacement_filter',
                    'html_tags_filter',
                    'punctuation_filter',
                ],
                'menu_transformer': common.MenuTransformerFiltersTest,
            },
            '<br>   вяз.  нежныйс кремом     Б. Ю.  Александров   </br>',
            'вязкий Нежный с кремом Б.Ю. Александров',
        ),
        (
            {
                'arguments': [
                    'replacement_filter',
                    'html_tags_filter',
                    'punctuation_filter',
                ],
                'menu_transformer': common.MenuTransformerFiltersTest,
            },
            'текст без изменений',
            'текст без изменений',
        ),
        (
            {
                'arguments': ['capitalize_first_letter_by_sentence_filter'],
                'menu_transformer': common.MenuTransformerFiltersTest,
            },
            'текст',
            'Текст',
        ),
        (
            {
                'arguments': [
                    'capitalize_first_letter_by_sentence_filter',
                    'html_tags_filter',
                ],
            },
            'текст',
            'текст',
        ),
        (
            {
                'arguments': [],
                'menu_transformer': common.MenuTransformerFiltersTest,
            },
            'текст',
            'текст',
        ),
    ],
)
async def test_composite_filter(arguments, filtered_string, normalized_string):
    composite_filter = filters.CompositeFilter(**arguments)
    text = composite_filter.filter(filtered_string)
    assert text == normalized_string


@pytest.mark.parametrize(
    'arguments, filtered_string, normalized_string',
    [
        ({'arguments': {'ЕДТА', 'СВЧ'}}, 'тест ТЕСТ ТеСт', 'тест Тест ТеСт'),
        ({'arguments': {'ЕДТА', 'СВЧ'}}, 'тест ТЕСТ ТЕСТ', 'тест Тест тест'),
        ({'arguments': {'ЕДТА', 'СВЧ'}}, 'СВЧ', 'СВЧ'),
        ({'arguments': {'ЕДТА', 'СВЧ'}}, 'СВЧ-печь', 'СВЧ-печь'),
        (
            {'arguments': {'ЕДТА', 'СВЧ'}},
            'ТУТ ЕСТЬ СВЧ-печь НОВАЯ!',
            'Тут есть СВЧ-печь Новая!',
        ),
        (
            {'arguments': {'ЕДТА', 'СВЧ'}},
            'ТУТ ЕСТЬ СВЧ, НОВАЯ!',
            'Тут есть СВЧ, Новая!',
        ),
        (
            {'arguments': {}},
            'Мини фигурка динозавр Коллекция 1 СЛ Гулливер',
            'Мини фигурка динозавр Коллекция 1 сл Гулливер',
        ),
        (
            {'arguments': {}},
            'НАБОР 6 СТОЛОВЫХ ВИЛОК НЕРЖ СТАЛЬ 1,3 ММ',
            'Набор 6 столовых вилок нерж сталь 1,3 мм',
        ),
        (
            {'arguments': {}},
            'НАБОР 6 СТОЛОВЫХ 3К НЕРЖ СТАЛЬ',
            'Набор 6 столовых 3к нерж сталь',
        ),
        (
            {'arguments': {}},
            'НАБОР 6 СТОЛОВЫХ 3к НЕРЖ СТАЛЬ',
            'Набор 6 столовых 3к Нерж сталь',
        ),
        (
            {'arguments': {}},
            'ПАКЕТ С ПЛАСТМАС РУЧКАМИ 38*35+10 МИКС',
            'Пакет с пластмас ручками 38*35+10 микс',
        ),
        (
            {'arguments': {'БЮ'}},
            'Сырок глазированный Б.Ю. Александров Суфле '
            'в тёмном шоколаде с ванилью 15%',
            'Сырок глазированный Б.Ю. Александров Суфле '
            'в тёмном шоколаде с ванилью 15%',
        ),
    ],
)
async def test_uppercase_filter(arguments, filtered_string, normalized_string):
    replacement_filter = filters.UppercaseFilter(**arguments)
    text = replacement_filter.filter(filtered_string)
    assert text == normalized_string


@pytest.mark.parametrize(
    'filtered_string, normalized_string',
    [
        ('Книга `орайли', 'Книга Орайли'),
        ('5’-монофосфат', '5-монофосфат'),
        ('5 ’-монофосфат', '5 -монофосфат'),
        (
            '"Угорь", \'креветка\', «краб», `сливочный сыр´, '
            'омлет ‘Тамаго’, соус ‚сырный‛',
            'Угорь, Креветка, Краб, Сливочный сыр, '
            'омлет Тамаго, соус Сырный',
        ),
        (
            'Курица ′жареная′, сыр ″сливочный″, перец “сладкий”, рис, укроп, '
            'соус ‹Сырный-Пармезан›',
            'Курица Жареная, сыр Сливочный, перец Сладкий, рис, укроп, '
            'соус Сырный-Пармезан',
        ),
    ],
)
async def test_quotes_filter(filtered_string, normalized_string):
    quotes_filter = filters.QuotesFilter()
    text = quotes_filter.filter(filtered_string)
    assert text == normalized_string


@pytest.mark.parametrize(
    'arguments, input_string, result_string',
    [
        (
            {'arguments': {'СТРОКА': 'Что-то рандомное 1'}},
            'СТРОКА',
            'Что-то рандомное 1',
        ),
        (
            {'arguments': {'строка': 'Что-то рандомное 2'}},
            'строка',
            'Что-то рандомное 2',
        ),
        (
            {'arguments': {'Строка': 'Что-то рандомное 3'}},
            'Строка',
            'Что-то рандомное 3',
        ),
        (
            {'arguments': {'СТРОКА': 'Что-то рандомное 1'}},
            'Не содержит substring 1',
            'Не содержит substring 1',
        ),
        (
            {'arguments': {'строка': 'Что-то рандомное 2'}},
            'Не содержит substring 2',
            'Не содержит substring 2',
        ),
        (
            {'arguments': {'Cтрока': 'Что-то рандомное 3'}},
            'Не содержит substring 3',
            'Не содержит substring 3',
        ),
        (
            {'arguments': {}},
            'Не содержит substring 4',
            'Не содержит substring 4',
        ),
        ({'arguments': {'Строка': None}}, 'Строка', None),
    ],
)
async def test_replacement_name_filter(arguments, input_string, result_string):
    replacement_name_filter = filters.ReplacementNameFilter(**arguments)
    assert _test_base(replacement_name_filter, input_string, result_string)


@pytest.mark.parametrize(
    'arguments, input_string, result_string',
    [
        (
            {
                'arguments': {
                    '/\\s+Б\\.\\sЮ\\.\\s+/ui': 'Сырок',
                    '/\\s+Нежныйс\\s+/ui': ' Нежный с ',
                    '/\\s+вяз(\\.)?\\s+/ui': ' вязкий ',
                },
            },
            ' вяз.  нежныйс кремом     Б. Ю.  Александров',
            'Сырок',
        ),
        ({'arguments': {}}, 'Не изменится строка', 'Не изменится строка'),
        (
            {'arguments': {'/\\s+Нежныйс\\s+/ui': ' Нежный с '}},
            'Не изменится строка, так как не нашелся паттерн',
            'Не изменится строка, так как не нашелся паттерн',
        ),
        (
            {
                'arguments': {
                    '/(вода\\s+.+)\\s+газ(\\.)?\\s+(.+)/ui': (
                        '$1 газированная $3'
                    ),
                    '/([\\.\\,])/ui': 'Нашли точку',
                },
            },
            'Тест с точкой.Вот',
            'Нашли точку',
        ),
        (
            {
                'arguments': {
                    '/([\\.\\,])/ui': 'нашли точку',
                    '/(вода\\s+.+)\\s+газ(\\.)?\\s+(.+)/ui': 'газированная',
                },
            },
            'вода .газ.в бутылке',
            'нашли точку',
        ),
        (
            {
                'arguments': {
                    '/(вода\\s+.+)\\s+газ(\\.)?\\s+(.+)/ui': 'газированная',
                    '/([\\.\\,])/ui': 'нашли точку',
                },
            },
            'вода .газ.в бутылке',
            'нашли точку',
        ),
        (
            {
                'arguments': {
                    '/(вода\\s+.+)\\s+газ(\\.)?\\s+(.+)/ui': 'газированная',
                    '/([\\.\\,])/ui': 'нашли точку',
                },
            },
            'вода . газ. в бутылке',
            'газированная',
        ),
        (
            {'arguments': {'/([\\.\\,])/ui': 'Ещё одна точка'}},
            'Вода минеральная Нарзан лечебно-столовая газированная 1.',
            'Ещё одна точка',
        ),
        (
            {'arguments': {'/(?<!\\-)\\d{2,}\\s*(?:г|мл)\\.?/ui': ''}},
            'Название',
            'Название',
        ),
        (
            {'arguments': {r'/(к)олг\W/ui': '$1олготки$2'}},
            'Название',
            'Название',
        ),
        (
            {'arguments': {r'/_?ВЕС(?:\s|$)/ui': ''}},
            'Цыпленок LaFerme Фермерский, вес',
            '',
        ),
        (
            {'arguments': {r'/_?ВЕС(?:\s|$)/u': ' '}},
            'Цыпленок LaFerme Фермерский, вес',
            'Цыпленок LaFerme Фермерский, вес',
        ),
        (
            {'arguments': {'/в асс(\\.)?\\s+/ui': 'в ассортименте'}},
            'Конструктор Ausini в асс Ост-ком :5/300',
            'в ассортименте',
        ),
    ],
)
async def test_full_replacement_by_condition_filter(
        arguments, input_string, result_string,
):
    full_replacement_by_condition_filter = (
        filters.FullReplacementByConditionFilter(**arguments)
    )
    assert _test_base(
        full_replacement_by_condition_filter, input_string, result_string,
    )


@pytest.mark.parametrize(
    'input_string, result_string',
    [
        ('', ''),
        (None, None),
        ('‐‑‒–—―⁻₋−⸺⸻﹘﹣－', '--------------'),
        ('	              ​‌‍⁠ ', '                    '),
    ],
)
async def test_special_chars_filter(input_string, result_string):
    special_chars_filter = filters.SpecialCharsFilter()
    assert _test_base(special_chars_filter, input_string, result_string)
