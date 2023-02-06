import pytest

from menu_transformer.content import transformers
from test_menu_transformer import common


async def test_transformers(library_context, load_json, patch):
    menu = library_context.menu_transformer.transform(
        load_json('menu_data.json'), load_json('dev_filter_transformers.json'),
    )

    assert menu == load_json('menu_data_transformers.json')


@pytest.mark.parametrize(
    'arguments, file_name, file_name_transformers, handler_class',
    [
        (
            {
                'arguments': [
                    'html_tags_filter',
                    'capitalize_first_letter_filter',
                ],
                'menu_transformer': common.MenuTransformerFiltersTest,
            },
            'menu_data_name.json',
            'menu_data_name_transformers.json',
            transformers.NameTransformer,
        ),
        (
            {
                'arguments': [],
                'menu_transformer': common.MenuTransformerFiltersTest,
            },
            'menu_data_name.json',
            'menu_data_name.json',
            transformers.NameTransformer,
        ),
        (
            {
                'arguments': [
                    'html_tags_filter',
                    'capitalize_first_letter_filter',
                ],
            },
            'menu_data_name.json',
            'menu_data_name.json',
            transformers.NameTransformer,
        ),
        (
            {
                'arguments': [
                    'html_tags_filter',
                    'capitalize_first_letter_filter',
                ],
                'menu_transformer': common.MenuTransformerFiltersTest,
            },
            'menu_data_category.json',
            'menu_data_category_transformers.json',
            transformers.CategoryNameTransformer,
        ),
        (
            {
                'arguments': [],
                'menu_transformer': common.MenuTransformerFiltersTest,
            },
            'menu_data_category.json',
            'menu_data_category.json',
            transformers.CategoryNameTransformer,
        ),
        (
            {
                'arguments': [
                    'html_tags_filter',
                    'capitalize_first_letter_filter',
                ],
            },
            'menu_data_category.json',
            'menu_data_category.json',
            transformers.CategoryNameTransformer,
        ),
        (
            {
                'arguments': {
                    '412227': (
                        'https://eda.yandex.ru/images/2794391/'
                        'e2251ca0a5066912295f2fd986abc3dd.jpg'
                    ),
                    '412721': (
                        'https://eda.yandex.ru/images/3667559/'
                        '593f377ca7540035008d4dcd285038a1.jpg'
                    ),
                },
            },
            'menu_data_category_images.json',
            'menu_data_category_images_transformers.json',
            transformers.CategoryImageTransformer,
        ),
        (
            {
                'arguments': [
                    'html_tags_filter',
                    'capitalize_first_letter_filter',
                ],
                'menu_transformer': common.MenuTransformerFiltersTest,
            },
            'menu_data_description.json',
            'menu_data_description_transformers.json',
            transformers.DescriptionTransformer,
        ),
        (
            {
                'arguments': [],
                'menu_transformer': common.MenuTransformerFiltersTest,
            },
            'menu_data_description.json',
            'menu_data_description.json',
            transformers.DescriptionTransformer,
        ),
        (
            {
                'arguments': [
                    'html_tags_filter',
                    'capitalize_first_letter_filter',
                ],
            },
            'menu_data_description.json',
            'menu_data_description.json',
            transformers.DescriptionTransformer,
        ),
        (
            {
                'arguments': ['basic_category_name_transformer'],
                'menu_transformer': common.MenuTransformersTest,
            },
            'menu_data_composite.json',
            'menu_data_composite_transformers.json',
            transformers.CompositeTransformer,
        ),
        (
            {
                'arguments': ['html_tags_filter'],
                'menu_transformer': common.MenuTransformerFiltersTest,
            },
            'menu_data_option_name.json',
            'menu_data_option_name_transformers.json',
            transformers.OptionNameTransformer,
        ),
        (
            {
                'arguments': [],
                'menu_transformer': common.MenuTransformerFiltersTest,
            },
            'menu_data_basic.json',
            'menu_data_basic_transformers.json',
            transformers.BasicTransformer,
        ),
        (
            {
                'arguments': [
                    {
                        'Категория 1': 'Префикс1',
                        'Категория 2': 'Префикс2',
                        'Категория 3': 'Префикс3',
                    },
                    False,
                ],
            },
            'menu_data_name_prefix.json',
            'menu_data_name_prefix_transformers.json',
            transformers.NamePrefixTransformer,
        ),
        (
            {
                'arguments': [
                    {
                        'Категория 1': 'Префикс1',
                        'Категория 2': 'префикс2',
                        'Категория 3': 'Префикс3',
                    },
                    True,
                ],
            },
            'menu_data_name_prefix.json',
            'menu_data_name_prefix_2_transformers.json',
            transformers.NamePrefixTransformer,
        ),
        (
            {'arguments': [{}, False]},
            'menu_data_name_prefix.json',
            'menu_data_name_prefix.json',
            transformers.NamePrefixTransformer,
        ),
        (
            {'arguments': [{}, True]},
            'menu_data_name_prefix.json',
            'menu_data_name_prefix.json',
            transformers.NamePrefixTransformer,
        ),
        (
            {
                'arguments': [['Категория 2'], 'html_tags_filter'],
                'menu_transformer': common.MenuTransformerFiltersTest,
            },
            'menu_data_name_by_categories.json',
            'menu_data_name_by_categories_transformers.json',
            transformers.NameByCategoriesTransformer,
        ),
        (
            {
                'arguments': [
                    ['Категория 3', 'Категория 4'],
                    'html_tags_filter',
                ],
                'menu_transformer': common.MenuTransformerFiltersTest,
            },
            'menu_data_description_by_categories.json',
            'menu_data_description_by_categories_transformers.json',
            transformers.DescriptionByCategoriesTransformer,
        ),
        (
            {'arguments': ['/(.*)\\s\\-\\s(\\d+)\\sшт/ui']},
            'menu_data_qty.json',
            'menu_data_qty_transformers.json',
            transformers.QtyTransformer,
        ),
        (
            {'arguments': ['/(.*)\\s\\-\\s(\\d+)pcs/ui']},
            'menu_data_qty.json',
            'menu_data_qty_2_transformers.json',
            transformers.QtyTransformer,
        ),
        (
            {'arguments': []},
            'menu_data_remove_description_if_duplicates_name.json',
            'menu_data_remove_description_if_duplicates_name_transformers.json',  # noqa: E501
            transformers.RemoveDescriptionIfDuplicatesNameTransformer,
        ),
        (
            {'arguments': []},
            'menu_data_remove_description.json',
            'menu_data_remove_description_transformers.json',
            transformers.RemoveDescriptionTransformer,
        ),
        (
            {'arguments': []},
            'menu_data_uppercase_after_dot_description.json',
            'menu_data_uppercase_after_dot_description_transformers.json',
            transformers.UppercaseAfterDotDescriptionTransformer,
        ),
        (
            {'arguments': [False, False]},
            'menu_data_set_retail_measure.json',
            'menu_data_set_retail_measure_ff_transformers.json',
            transformers.SetRetailMeasureTransformer,
        ),
        (
            {'arguments': [False, True]},
            'menu_data_set_retail_measure.json',
            'menu_data_set_retail_measure_ft_transformers.json',
            transformers.SetRetailMeasureTransformer,
        ),
        (
            {'arguments': [True, False]},
            'menu_data_set_retail_measure.json',
            'menu_data_set_retail_measure_tf_transformers.json',
            transformers.SetRetailMeasureTransformer,
        ),
        (
            {'arguments': [True, True]},
            'menu_data_set_retail_measure.json',
            'menu_data_set_retail_measure_tt_transformers.json',
            transformers.SetRetailMeasureTransformer,
        ),
        (
            {'arguments': [{'/\\s20/u': 'pickup', '/ID1/u': 'delivery'}]},
            'menu_data_set_shipping_type.json',
            'menu_data_set_shipping_type_transformers.json',
            transformers.SetShippingTypeTransformer,
        ),
        (
            {'arguments': [{'/111/u': 'pickup', '/Categ/u': 'delivery'}]},
            'menu_data_set_shipping_type_by_categories.json',
            'menu_data_set_shipping_type_by_categories_transformers.json',
            transformers.SetShippingTypeByCategoriesTransformer,
        ),
        (
            {'arguments': []},
            'menu_data_category_id_name.json',
            'menu_data_category_id_name_transformers.json',
            transformers.CategoryIdNameTransformer,
        ),
        (
            {'arguments': {'Категория 1': True, 'Категория 3': False}},
            'menu_data_set_not_choosable_by_category.json',
            'menu_data_set_not_choosable_by_category_transformers.json',
            transformers.SetNotChoosableByCategoryTransformer,
        ),
        (
            {
                'arguments': {
                    'general': 'Общее описание продукта',
                    'vendorCountry': 'Страна изготовления',
                },
            },
            'menu_data_retail_description.json',
            'menu_data_retail_description_transformers.json',
            transformers.RetailDescriptionTransformer,
        ),
    ],
)
async def test_fields_transformer(
        load_json, arguments, file_name, file_name_transformers, handler_class,
):
    menu = load_json(file_name)

    handler = handler_class(**arguments)
    handler.transform(menu)
    assert menu == load_json(file_name_transformers)


@pytest.mark.parametrize(
    'arguments, test_name',
    [
        (
            {'arguments': ['/(\\d+\\s*(?:к?гр?))\\.?/ui', False]},
            'set-weight-from-name',
        ),
        (
            {'arguments': ['/(\\d+\\s*(?:к?гр?))\\.?/ui', False]},
            'set-weight-from-description',
        ),
        (
            {'arguments': ['/(\\d+\\s*(?:к?гр?))\\.?/ui', False]},
            'no-retail-info',
        ),
        ({'arguments': ['', False]}, 'not-set-weight-with-empty-pattern'),
        (
            {
                'arguments': [
                    '/(\\d+\\s*(?:к?гр?))\\.?/ui',
                    False,
                    ['/Тайский Лосось/'],
                ],
            },
            'not-set-weight-with-black-list',
        ),
        (
            {'arguments': ['/(\\d+\\s*(?:к?гр?))\\.?/ui', True]},
            'set-weight-with-skip-weight-check',
        ),
        (
            {'arguments': ['/(\\d+\\s*(?:к?гр?))\\.?/ui', True]},
            'set-weight-with-is-catch-weight-false',
        ),
        (
            {'arguments': ['/(\\d+\\s*(?:к?гр?))\\.?/ui', True]},
            'not-set-weight-with-is-catch-weight-true',
        ),
    ],
)
async def test_extract_weight_transformer(load_json, arguments, test_name):
    menu = load_json('extract_weight_transformer.json')[test_name]
    expected = load_json('extract_weight_transformer_transformed.json')[
        test_name
    ]

    transformer = transformers.ExtractWeightTransformer(**arguments)
    transformer.transform(menu)
    assert menu == expected


@pytest.mark.parametrize(
    'test_name, arguments',
    [
        ('test-00', {}),
        ('test-01', {}),
        ('test-02', {}),
        ('test-03', {}),
        ('test-04', {}),
        ('test-05', {}),
        ('test-06', {}),
        ('test-07', {}),
        ('test-08', {}),
        ('test-09', {}),
        ('test-10', {}),
        ('test-11', {}),
        ('test-12', {}),
        ('test-13', {}),
        ('test-14', {}),
        ('test-15', {}),
        ('test-16', {}),
        ('test-17', {}),
        ('test-18', {}),
        ('test-19', {}),
        ('test-20', {}),
        ('test-21', {}),
        ('test-22', {}),
        ('test-23', {}),
        ('test-24', {}),
        ('test-25', {}),
        ('with-limit-0', {'arguments': [None, 5]}),
        ('with-limit-1', {'arguments': [None, 5]}),
        ('with-limit-2', {'arguments': [None, 5]}),
        (
            'with-round-precision',
            {
                'arguments': [
                    ['Напитки', 'Лимонад', 'Соки', 'Морс', 'Айран', 'Вода'],
                    2,
                    'г',
                    'мл',
                    1,
                ],
            },
        ),
    ],
)
async def test_weight_transformer(load_json, arguments, test_name):
    menu = load_json('weight_transformer.json')[test_name]['menu']
    expected_weight = load_json('weight_transformer.json')[test_name]['weight']

    transformer = transformers.WeightTransformer(**arguments)
    transformer.transform(menu)
    assert menu['menu_items'][0]['weight'] == expected_weight


@pytest.mark.parametrize(
    'test_name',
    [
        'test-00',
        'test-01',
        'test-02',
        'test-03',
        'test-04',
        'test-05',
        'test-06',
    ],
)
async def test_weight_from_text_transformer(load_json, test_name):
    test_data = load_json('weight_from_text_transformer.json')[test_name]
    menu = test_data['menu']
    expected_weight = test_data['weight']

    transformer = transformers.WeightFromTextTransformer(**{})
    transformer.transform(menu)
    assert menu['menu_items'][0]['weight'] == expected_weight
