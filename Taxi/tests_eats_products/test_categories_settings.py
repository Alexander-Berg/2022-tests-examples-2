# pylint: disable=too-many-lines
import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils

PRODUCTS_BASE_REQUEST = {'shippingType': 'pickup', 'slug': 'slug'}


def make_themed_color(postfix, theme='light'):
    return {'theme': theme, 'value': 'color_' + postfix}


def gallery_config(force_gallery_from_config, has_gallery):
    return {
        'defaults': [
            {
                'id': '1',
                'gallery': (
                    [{'url': 'tile_cfg_url', 'type': 'tile'}]
                    if has_gallery
                    else None
                ),
                'banner_carousel_url': 'banner_cfg_url',
                'categories_carousel_url': 'category_cfg_url',
                'force_gallery_from_config': force_gallery_from_config,
            },
        ],
        'brands': [],
    }


PARAMETRIZE_INTEGRATION_VERSION = pytest.mark.parametrize(
    'nmn_integration_version', ['v1', 'v2'],
)

DEFAULT_BG_COLORS = [make_themed_color('1', 'dark'), make_themed_color('2')]
DEFAULT_TEXT_COLORS = [make_themed_color('3', 'dark'), make_themed_color('4')]
DEFAULT_SUBTITLE_COLORS = [
    make_themed_color('6', 'dark'),
    make_themed_color('6'),
]


@pytest.mark.parametrize(
    'config, expected_properties',
    [
        (
            # точное попадание в бренд + категория
            {
                'defaults': [],
                'brands': [
                    {
                        'slug': 'brand1',
                        'categories': [
                            {
                                'id': '1',
                                'gallery': [
                                    {'url': 'image-url-1', 'type': 'tile'},
                                ],
                                'background_colors': DEFAULT_BG_COLORS,
                                'text_color': DEFAULT_TEXT_COLORS,
                                'subtitle_color': DEFAULT_SUBTITLE_COLORS,
                                'subtitle': 'subtitle',
                            },
                        ],
                    },
                ],
            },
            {
                1: {
                    'gallery': [
                        {'url': 'image-url-1/{w}x{h}', 'type': 'tile'},
                    ],
                    'backgroundColors': DEFAULT_BG_COLORS,
                    'text_color': DEFAULT_TEXT_COLORS,
                    'subtitle_color': DEFAULT_SUBTITLE_COLORS,
                    'subtitle': 'subtitle',
                },
            },
        ),
        (
            # дефолтное значение для бренда
            {
                'defaults': [],
                'brands': [
                    {
                        'slug': 'brand1',
                        'default-category': 'defaults',
                        'categories': [
                            {
                                'id': 'defaults',
                                'gallery': [
                                    {'url': 'image-url-1', 'type': 'tile'},
                                ],
                                'background_colors': [make_themed_color('3')],
                                'text_color': [make_themed_color('3')],
                                'subtitle_color': [make_themed_color('3')],
                                'subtitle': 'subtitle_3',
                            },
                        ],
                    },
                ],
            },
            {
                1: {
                    'gallery': [
                        {'url': 'image-url-1/{w}x{h}', 'type': 'tile'},
                    ],
                    'backgroundColors': [make_themed_color('3')],
                    'text_color': [make_themed_color('3')],
                    'subtitle_color': [make_themed_color('3')],
                    'subtitle': 'subtitle_3',
                },
                2: {
                    'backgroundColors': [make_themed_color('3')],
                    'text_color': [make_themed_color('3')],
                    'subtitle_color': [make_themed_color('3')],
                    'subtitle': 'subtitle_3',
                },
                3: {
                    'backgroundColors': [make_themed_color('3')],
                    'text_color': [make_themed_color('3')],
                    'subtitle_color': [make_themed_color('3')],
                    'subtitle': 'subtitle_3',
                },
            },
        ),
        (
            # дефолтное значение для категории без учёта бренда
            {
                'defaults': [
                    {
                        'id': '1',
                        'gallery': [{'url': 'image-url-1', 'type': 'tile'}],
                        'background_colors': DEFAULT_BG_COLORS,
                        'text_color': DEFAULT_TEXT_COLORS,
                        'subtitle_color': DEFAULT_SUBTITLE_COLORS,
                        'subtitle': 'subtitle',
                    },
                ],
                'brands': [],
            },
            {
                1: {
                    'gallery': [
                        {'url': 'image-url-1/{w}x{h}', 'type': 'tile'},
                    ],
                    'backgroundColors': DEFAULT_BG_COLORS,
                    'text_color': DEFAULT_TEXT_COLORS,
                    'subtitle_color': DEFAULT_SUBTITLE_COLORS,
                    'subtitle': 'subtitle',
                },
            },
        ),
        (
            # существующие не-пустые свойства не переопределяются
            {
                'defaults': [
                    {
                        'id': '2',
                        'gallery': [{'url': 'image-url-1', 'type': 'tile'}],
                        'background_colors': DEFAULT_BG_COLORS,
                        'text_color': DEFAULT_TEXT_COLORS,
                        'subtitle_color': DEFAULT_SUBTITLE_COLORS,
                        'subtitle': 'subtitle',
                    },
                ],
                'brands': [],
            },
            {
                2: {
                    'gallery': [
                        {'url': 'image_url_1/{w}x{h}', 'type': 'tile'},
                    ],
                    'backgroundColors': DEFAULT_BG_COLORS,
                    'text_color': DEFAULT_TEXT_COLORS,
                    'subtitle_color': DEFAULT_SUBTITLE_COLORS,
                    'subtitle': 'subtitle',
                },
            },
        ),
        (
            # при force_gallery_from_config=true gallery из конфига
            # переопределяет изображения номенклатутуры
            {
                'defaults': [
                    {
                        'id': '2',
                        'gallery': [{'url': 'image-url-1', 'type': 'tile'}],
                        'background_colors': DEFAULT_BG_COLORS,
                        'text_color': DEFAULT_TEXT_COLORS,
                        'subtitle_color': DEFAULT_SUBTITLE_COLORS,
                        'subtitle': 'subtitle',
                        'force_gallery_from_config': True,
                    },
                ],
                'brands': [],
            },
            {
                2: {
                    'gallery': [
                        {'url': 'image-url-1/{w}x{h}', 'type': 'tile'},
                    ],
                    'backgroundColors': DEFAULT_BG_COLORS,
                    'text_color': DEFAULT_TEXT_COLORS,
                    'subtitle_color': DEFAULT_SUBTITLE_COLORS,
                    'subtitle': 'subtitle',
                },
            },
        ),
        (
            # проверка приоритетов: точное совпадение бренда + категории
            # имеет наивысший приоритет
            {
                'defaults': [
                    {
                        'id': '1',
                        'gallery': [
                            {'url': 'default-category-image', 'type': 'tile'},
                        ],
                        'background_colors': [make_themed_color('3')],
                        'text_color': [make_themed_color('3')],
                        'subtitle_color': [make_themed_color('3')],
                        'subtitle': 'subtitle_3',
                    },
                ],
                'brands': [
                    {
                        'slug': 'brand1',
                        'default-category': 'defaults',
                        'categories': [
                            {
                                'id': 'defaults',
                                'gallery': [
                                    {
                                        'url': 'default-brand-image-url',
                                        'type': 'tile',
                                    },
                                ],
                                'background_colors': [make_themed_color('4')],
                                'text_color': [make_themed_color('4')],
                                'subtitle_color': [make_themed_color('4')],
                                'subtitle': 'subtitle_4',
                            },
                            {
                                'id': '1',
                                'gallery': [
                                    {'url': 'image-url-1', 'type': 'tile'},
                                ],
                                'background_colors': [make_themed_color('5')],
                                'text_color': [make_themed_color('5')],
                                'subtitle_color': [make_themed_color('5')],
                                'subtitle': 'subtitle_5',
                            },
                        ],
                    },
                ],
            },
            {
                1: {
                    'gallery': [
                        {'url': 'image-url-1/{w}x{h}', 'type': 'tile'},
                    ],
                    'backgroundColors': [make_themed_color('5')],
                    'text_color': [make_themed_color('5')],
                    'subtitle_color': [make_themed_color('5')],
                    'subtitle': 'subtitle_5',
                },
            },
        ),
        (
            # проверка приоритетов: дефолтные настройки бренда
            # имеет больший приоритет чем дефолтные настройки
            # конкретной категории
            {
                'defaults': [
                    {
                        'id': '1',
                        'gallery': [
                            {'url': 'default-category-image', 'type': 'tile'},
                        ],
                        'backgroundColors': [make_themed_color('category')],
                        'text_color': [make_themed_color('category')],
                        'subtitle_color': [make_themed_color('category')],
                        'subtitle': 'subtitle_category',
                    },
                ],
                'brands': [
                    {
                        'slug': 'brand1',
                        'default-category': 'defaults',
                        'categories': [
                            {
                                'id': 'defaults',
                                'gallery': [
                                    {
                                        'url': 'default-brand-image-url',
                                        'type': 'tile',
                                    },
                                ],
                                'background_colors': [
                                    make_themed_color('brand'),
                                ],
                                'text_color': [make_themed_color('brand')],
                                'subtitle_color': [make_themed_color('brand')],
                                'subtitle': 'subtitle_brand',
                            },
                        ],
                    },
                ],
            },
            {
                1: {
                    'gallery': [
                        {
                            'url': 'default-brand-image-url/{w}x{h}',
                            'type': 'tile',
                        },
                    ],
                    'backgroundColors': [make_themed_color('brand')],
                    'text_color': [make_themed_color('brand')],
                    'subtitle_color': [make_themed_color('brand')],
                    'subtitle': 'subtitle_brand',
                },
            },
        ),
        (
            # свойства не найденные на более высоком уровне приоритетов
            # берутся из настроек с меньшим приоритетом
            {
                'defaults': [
                    {
                        'id': '1',
                        'gallery': [
                            {'url': 'default-category-image', 'type': 'tile'},
                        ],
                        'background_colors': [make_themed_color('default')],
                        'text_color': [make_themed_color('default')],
                        'subtitle_color': [make_themed_color('default')],
                        'subtitle': 'subtitle_default',
                    },
                ],
                'brands': [
                    {
                        'slug': 'brand1',
                        'default-category': 'defaults',
                        'categories': [
                            {
                                'id': 'defaults',
                                'gallery': [
                                    {'url': 'default-brand-image-url'},
                                ],
                            },
                        ],
                    },
                ],
            },
            {
                1: {
                    'gallery': [
                        {
                            'url': 'default-brand-image-url/{w}x{h}',
                            'type': 'tile',
                        },
                    ],
                    'backgroundColors': [make_themed_color('default')],
                    'text_color': [make_themed_color('default')],
                    'subtitle_color': [make_themed_color('default')],
                    'subtitle': 'subtitle_default',
                },
            },
        ),
    ],
)
@PARAMETRIZE_INTEGRATION_VERSION
async def test_categories_settings(
        taxi_config,
        config,
        expected_properties,
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
):
    # проверка применения настроек из конфига
    # EATS_PRODUCTS_CATEGORIES_SETTINGS
    taxi_config.set(EATS_PRODUCTS_CATEGORIES_SETTINGS=config)
    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    images = [('image_url_1', 1), ('image_url_1', 0)]
    root_cat_1 = conftest.CategoryMenuGoods(
        public_id='1', name='name', origin_id='category_origin_id',
    )
    root_cat_2 = conftest.CategoryMenuGoods(
        public_id='2',
        name='name',
        origin_id='category_origin_id',
        images=images,
    )
    root_cat_3 = conftest.CategoryMenuGoods(
        public_id='3',
        name='name',
        origin_id='category_origin_id',
        images=images,
    )
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID,
        slug=utils.PLACE_SLUG,
        brand_id=utils.BRAND_ID,
    )
    place.add_root_category(root_cat_1)
    place.add_root_category(root_cat_2)
    place.add_root_category(root_cat_3)
    mock_nomenclature_context.set_place(place)

    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        PRODUCTS_BASE_REQUEST, integration_version=nmn_integration_version,
    )
    assert response.status_code == 200
    categories_index = {
        cat['id']: cat for cat in response.json()['payload']['categories']
    }
    for cat_id in expected_properties:
        assert cat_id in categories_index
        category = categories_index[cat_id]
        for expected_prop in expected_properties[cat_id]:
            assert (
                category[expected_prop]
                == expected_properties[cat_id][expected_prop]
            )


@pytest.mark.parametrize(
    'expected_properties',
    [
        pytest.param(
            # Эксперимент включен.
            # Тест проверяет, что картинка с типом
            # tile добавилась из номенклатуры,
            # а banner_carousel и categories_carousel добавились
            # из дефолтных настроек категории, при включенном эксперименте.
            {
                2: {
                    'gallery': [
                        {
                            'url': 'image_url_1/{w}x{h}',
                            'type': 'tile',
                        },  # из ответа номенклатуры
                        {
                            'url': 'default_banner_image-url-1/{w}x{h}',
                            'type': 'banner_carousel',
                        },  # из конфига
                        {
                            'url': 'default_categories_image-url-1/{w}x{h}',
                            'type': 'categories_carousel',
                        },  # из конфига
                    ],
                },
            },
            marks=(
                experiments.category_picture_type(),
                pytest.mark.config(
                    EATS_PRODUCTS_CATEGORIES_SETTINGS={
                        'defaults': [
                            {
                                'id': '2',
                                'gallery': [
                                    {
                                        'url': 'default_image_url_1',
                                        'type': 'tile',
                                    },
                                ],
                                'background_colors': [
                                    {
                                        'theme': 'dark',
                                        'value': (
                                            'default-category-color-value'
                                        ),
                                    },
                                ],
                                'banner_carousel_url': (
                                    'default_banner_image-url-1'
                                ),
                                'categories_carousel_url': (
                                    'default_categories_image-url-1'
                                ),
                            },
                        ],
                        'brands': [],
                    },
                ),
            ),
            id='exp on, check ok',
        ),
        pytest.param(
            # Эксперимент включен.
            # Тест проверяет, что картника с типом tile не дублируется.
            # Если есть и в номенклатуре и в конфиге,
            # берется из номенклатуры.
            {
                2: {
                    'gallery': [
                        {
                            'url': 'image_url_1/{w}x{h}',
                            'type': 'tile',
                        },  # из ответа номенклатуры
                    ],
                },
            },
            marks=(
                experiments.category_picture_type(),
                pytest.mark.config(
                    EATS_PRODUCTS_CATEGORIES_SETTINGS={
                        'defaults': [],
                        'brands': [
                            {
                                'slug': 'brand1',
                                'categories': [
                                    {
                                        'id': '2',
                                        'gallery': [
                                            {
                                                'url': 'config_image_url_1',
                                                'type': 'tile',
                                            },
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                ),
            ),
            id='exp on, tile is not duplicated',
        ),
        pytest.param(
            # Эксперимент включен.
            # Тест проверяет взятие картинки с типом tile
            # из конфига, если нет в номенклатуре.
            {
                1: {
                    'gallery': [
                        {
                            'url': 'image_url_1/{w}x{h}',
                            'type': 'tile',
                        },  # из конфига
                    ],
                },
            },
            marks=(
                experiments.category_picture_type(),
                pytest.mark.config(
                    EATS_PRODUCTS_CATEGORIES_SETTINGS={
                        'defaults': [],
                        'brands': [
                            {
                                'slug': 'brand1',
                                'categories': [
                                    {
                                        'id': '1',
                                        'gallery': [
                                            {
                                                'url': 'image_url_1',
                                                'type': 'tile',
                                            },
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                ),
            ),
            id='exp on, tile from config',
        ),
        pytest.param(
            # Эксперимент включен.
            # Тест проверяет взятие картинок banner_carousel_url
            # и categories_carousel_url из настроек бренда,
            # если они там есть. Картинка с типом tile берется
            # из дефолтных настроек, т.к в настройках
            # бренда ее нет. Так же тест показывает, что
            # картинка с типом tile приходит на первом месте,
            # хоть и находится в дефолтных настройках
            {
                1: {
                    'gallery': [
                        {'url': 'default_image_url_1/{w}x{h}', 'type': 'tile'},
                        {
                            'url': 'brands_banner_image-url-1/{w}x{h}',
                            'type': 'banner_carousel',
                        },
                        {
                            'url': 'brands_categories_image-url-1/{w}x{h}',
                            'type': 'categories_carousel',
                        },
                    ],
                },
            },
            marks=(
                experiments.category_picture_type(),
                pytest.mark.config(
                    EATS_PRODUCTS_CATEGORIES_SETTINGS={
                        'defaults': [
                            {
                                'id': '1',
                                'gallery': [
                                    {
                                        'url': 'default_image_url_1',
                                        'type': 'tile',
                                    },
                                ],
                                'background_colors': [
                                    {
                                        'theme': 'dark',
                                        'value': (
                                            'default-category-color-value'
                                        ),
                                    },
                                ],
                                'banner_carousel_url': (
                                    'default_banner_image-url-1'
                                ),
                                'categories_carousel_url': (
                                    'default_categories_image-url-1'
                                ),
                            },
                        ],
                        'brands': [
                            {
                                'slug': 'brand1',
                                'categories': [
                                    {
                                        'id': '1',
                                        'banner_carousel_url': (
                                            'brands_banner_image-url-1'
                                        ),
                                        'categories_carousel_url': (
                                            'brands_categories_image-url-1'
                                        ),
                                    },
                                ],
                            },
                        ],
                    },
                ),
            ),
            id='exp on, carousel from brand, tile from config',
        ),
        pytest.param(
            # Эксперимент включен.
            # Тест проверяет взятие картинки из номенклатуры
            {2: {'gallery': [{'url': 'image_url_1/{w}x{h}', 'type': 'tile'}]}},
            marks=(
                experiments.category_picture_type(),
                pytest.mark.config(
                    EATS_PRODUCTS_CATEGORIES_SETTINGS={
                        'defaults': [],
                        'brands': [
                            {
                                'slug': 'brand1',
                                'categories': [{'id': '2', 'gallery': []}],
                            },
                        ],
                    },
                ),
            ),
            id='exp on, tile from nomenclature',
        ),
        pytest.param(
            # Эксперимент включен.
            # Тест на пустые значения в конфиге и номенклатуре
            {1: {'gallery': []}},
            marks=(
                experiments.category_picture_type(),
                pytest.mark.config(
                    EATS_PRODUCTS_CATEGORIES_SETTINGS={
                        'defaults': [],
                        'brands': [
                            {
                                'slug': 'brand1',
                                'categories': [{'id': '1', 'gallery': []}],
                            },
                        ],
                    },
                ),
            ),
            id='exp on, check empty',
        ),
        pytest.param(
            # Эксперимент включен.
            # Тест показывает, что картинка с типом
            # tile приходит на первом месте, а banner_carousel и
            # categories_carousel приходят при включенном эксперименте.
            # Так же проверяет корректность ответа при наличии суффикса
            {
                1: {
                    'gallery': [
                        {'url': 'default_image_url_1/{w}x{h}', 'type': 'tile'},
                        {
                            'url': 'default_banner_image-url-1/{w}x{h}',
                            'type': 'banner_carousel',
                        },
                        {
                            'url': 'default_categories_image-url-1/{w}x{h}',
                            'type': 'categories_carousel',
                        },
                    ],
                },
            },
            marks=(
                experiments.category_picture_type(),
                pytest.mark.config(
                    EATS_PRODUCTS_CATEGORIES_SETTINGS={
                        'defaults': [
                            {
                                'id': '1',
                                'gallery': [
                                    {
                                        'url': 'default_image_url_1/{w}x{h}',
                                        'type': 'tile',
                                    },
                                ],
                                'background_colors': [
                                    {
                                        'theme': 'dark',
                                        'value': (
                                            'default-category-color-value'
                                        ),
                                    },
                                ],
                                'banner_carousel_url': (
                                    'default_banner_image-url-1/{w}x{h}'
                                ),
                                'categories_carousel_url': (
                                    'default_categories_image-url-1/{w}x{h}'
                                ),
                            },
                        ],
                        'brands': [
                            {'slug': 'brand1', 'categories': [{'id': '1'}]},
                        ],
                    },
                ),
            ),
            id='exp on, tile on first place',
        ),
        pytest.param(
            # Эксперимент выключен.
            # Тест проверяет, что картинка с типом
            # tile добавилась из номенклатуры,
            # а banner_carousel и categories_carousel не добавились
            # из дефолтных настроек категории, при выключенном эксперименте.
            {
                2: {
                    'gallery': [
                        {
                            'url': 'image_url_1/{w}x{h}',
                            'type': 'tile',
                        },  # из ответа номенклатуры
                    ],
                },
            },
            marks=(
                experiments.category_picture_type(enabled=False),
                pytest.mark.config(
                    EATS_PRODUCTS_CATEGORIES_SETTINGS={
                        'defaults': [
                            {
                                'id': '2',
                                'gallery': [
                                    {
                                        'url': 'default_image_url_1',
                                        'type': 'tile',
                                    },
                                ],
                                'background_colors': [
                                    {
                                        'theme': 'dark',
                                        'value': (
                                            'default-category-color-value'
                                        ),
                                    },
                                ],
                                'banner_carousel_url': (
                                    'default_banner_image-url-1'
                                ),
                                'categories_carousel_url': (
                                    'default_categories_image-url-1'
                                ),
                            },
                        ],
                        'brands': [],
                    },
                ),
            ),
            id='exp off',
        ),
        pytest.param(
            # Эксперимент отсутствует.
            # Тест проверяет, что картинка с типом
            # tile добавилась из номенклатуры,
            # а banner_carousel и categories_carousel не добавились
            # из дефолтных настроек категории, при отсутствии эксперимента.
            {
                2: {
                    'gallery': [
                        {
                            'url': 'image_url_1/{w}x{h}',
                            'type': 'tile',
                        },  # из ответа номенклатуры
                    ],
                },
            },
            marks=(
                pytest.mark.config(
                    EATS_PRODUCTS_CATEGORIES_SETTINGS={
                        'defaults': [
                            {
                                'id': '2',
                                'gallery': [
                                    {
                                        'url': 'default_image_url_1',
                                        'type': 'tile',
                                    },
                                ],
                                'background_colors': [
                                    {
                                        'theme': 'dark',
                                        'value': (
                                            'default-category-color-value'
                                        ),
                                    },
                                ],
                                'banner_carousel_url': (
                                    'default_banner_image-url-1'
                                ),
                                'categories_carousel_url': (
                                    'default_categories_image-url-1'
                                ),
                            },
                        ],
                        'brands': [],
                    },
                )
            ),
            id='no exp',
        ),
    ],
)
@PARAMETRIZE_INTEGRATION_VERSION
async def test_get_image_banner_and_categories_from_config(
        expected_properties,
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
):
    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    images = [('image_url_1', 1), ('image_url_1', 0)]
    root_cat_1 = conftest.CategoryMenuGoods(
        public_id='1', name='name', origin_id='category_origin_id',
    )
    root_cat_2 = conftest.CategoryMenuGoods(
        public_id='2',
        name='name',
        origin_id='category_origin_id',
        images=images,
    )
    root_cat_3 = conftest.CategoryMenuGoods(
        public_id='3',
        name='name',
        origin_id='category_origin_id',
        images=images,
    )
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID,
        slug=utils.PLACE_SLUG,
        brand_id=utils.BRAND_ID,
    )
    place.add_root_category(root_cat_1)
    place.add_root_category(root_cat_2)
    place.add_root_category(root_cat_3)
    mock_nomenclature_context.set_place(place)

    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        PRODUCTS_BASE_REQUEST, integration_version=nmn_integration_version,
    )
    assert response.status_code == 200
    categories_index = {
        cat['id']: cat for cat in response.json()['payload']['categories']
    }
    for cat_id in expected_properties:
        assert cat_id in categories_index
        category = categories_index[cat_id]
        for expected_prop in expected_properties[cat_id]:
            assert (
                category[expected_prop]
                == expected_properties[cat_id][expected_prop]
            )


@pytest.mark.parametrize(
    'handler',
    [
        utils.Handlers.MENU_GOODS,
        utils.Handlers.MENU_GOODS
        + '/?category='
        + str(utils.REPEAT_CATEGORY_ID),
    ],
)
@experiments.repeat_category()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@PARAMETRIZE_INTEGRATION_VERSION
async def test_categories_settings_repeat_category(
        mockserver,
        load_json,
        taxi_config,
        handler,
        add_place_products_mapping,
        mock_retail_categories_brand_orders_history,
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
):
    # тест проверяет, что настройки категорий применяются
    # к динамической категории «Повторим»
    add_place_products_mapping(
        [conftest.ProductMapping(origin_id='item_id_1', core_id=1)],
    )
    categories_settings = {
        'defaults': [
            {
                'id': str(utils.REPEAT_CATEGORY_ID),
                'gallery': [
                    {'url': 'default-category-image/{w}x{h}', 'type': 'tile'},
                ],
                'background_colors': [
                    {'theme': 'dark', 'value': 'default-category-color-value'},
                ],
            },
        ],
        'brands': [],
    }
    taxi_config.set(EATS_PRODUCTS_CATEGORIES_SETTINGS=categories_settings)
    taxi_config.set(
        EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
            repeat_enabled=True,
        ),
    )

    mock_retail_categories_brand_orders_history.add_default_products()

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        return load_json('v2_place_assortment_details_response.json')

    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    root_cat_1 = conftest.CategoryMenuGoods(
        public_id='1', name='name', origin_id='category_origin_id',
    )
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID,
        slug=utils.PLACE_SLUG,
        brand_id=utils.BRAND_ID,
    )
    place.add_root_category(root_cat_1)
    mock_nomenclature_context.set_place(place)

    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        PRODUCTS_BASE_REQUEST,
        integration_version=nmn_integration_version,
        headers={
            'X-Eats-User': 'user_id=123',
            'X-AppMetrica-DeviceId': 'device_id',
        },
    )
    assert response.status_code == 200
    categories_index = {
        cat['id']: cat for cat in response.json()['payload']['categories']
    }

    expected_settings = categories_settings['defaults'][0]
    assert utils.REPEAT_CATEGORY_ID in categories_index
    repeat_category = categories_index[utils.REPEAT_CATEGORY_ID]
    assert repeat_category['gallery'] == expected_settings['gallery']
    assert (
        repeat_category['backgroundColors']
        == expected_settings['background_colors']
    )
    assert mock_retail_categories_brand_orders_history.times_called == 1


@pytest.mark.parametrize(
    'handler',
    [
        utils.Handlers.MENU_GOODS,
        utils.Handlers.MENU_GOODS
        + '/?category='
        + str(utils.DISCOUNT_CATEGORY_ID),
    ],
)
@experiments.discount_category()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@PARAMETRIZE_INTEGRATION_VERSION
async def test_categories_settings_discount_category(
        mockserver,
        load_json,
        taxi_config,
        handler,
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
):
    # тест проверяет, что настройки категорий применяются
    # к динамической категории «Скидки»
    categories_settings = {
        'defaults': [
            {
                'id': str(utils.DISCOUNT_CATEGORY_ID),
                'gallery': [
                    {'url': 'default-category-image/{w}x{h}', 'type': 'tile'},
                ],
                'background_colors': [
                    {'theme': 'dark', 'value': 'default-category-color-value'},
                ],
            },
        ],
        'brands': [],
    }
    taxi_config.set(EATS_PRODUCTS_CATEGORIES_SETTINGS=categories_settings)
    taxi_config.set(
        EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
            discount_enabled=True,
        ),
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        return load_json('v2_place_assortment_details_response.json')

    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    root_cat_1 = conftest.CategoryMenuGoods(
        public_id='1', name='name', origin_id='category_origin_id',
    )
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID,
        slug=utils.PLACE_SLUG,
        brand_id=utils.BRAND_ID,
    )
    place.add_root_category(root_cat_1)
    mock_nomenclature_context.set_place(place)

    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        PRODUCTS_BASE_REQUEST, integration_version=nmn_integration_version,
    )
    assert response.status_code == 200
    categories_index = {
        cat['id']: cat for cat in response.json()['payload']['categories']
    }

    expected_settings = categories_settings['defaults'][0]
    assert utils.DISCOUNT_CATEGORY_ID in categories_index
    discount_category = categories_index[utils.DISCOUNT_CATEGORY_ID]
    assert discount_category['gallery'] == expected_settings['gallery']
    assert (
        discount_category['backgroundColors']
        == expected_settings['background_colors']
    )


@pytest.mark.parametrize('is_custom', [False, True])
@pytest.mark.parametrize('has_nomenclature_gallery', [False, True])
@pytest.mark.parametrize('force_gallery_from_config', [False, True])
@pytest.mark.parametrize('has_config_gallery', [False, True])
@experiments.INVERT_GALLERY_SOURCES_ENABLED
@experiments.CAROUSEL_PICTURES_TYPE_ENABLED
@PARAMETRIZE_INTEGRATION_VERSION
async def test_get_image_banner_and_categories_from_nomenclature(
        taxi_config,
        force_gallery_from_config,
        has_config_gallery,
        has_nomenclature_gallery,
        is_custom,
        mock_nomenclature_for_v2_menu_goods,
        nmn_integration_version,
):
    taxi_config.set(
        EATS_PRODUCTS_CATEGORIES_SETTINGS=gallery_config(
            force_gallery_from_config=force_gallery_from_config,
            has_gallery=has_config_gallery,
        ),
    )
    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods

    category_type = 'custom_promo' if is_custom else 'partner'
    root_cat_1 = conftest.CategoryMenuGoods(
        public_id='1',
        name='name',
        origin_id='category_origin_id',
        category_type=category_type,
    )
    if has_nomenclature_gallery:
        root_cat_1.images = [('url_nmn', 0)]
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID,
        slug=utils.PLACE_SLUG,
        brand_id=utils.BRAND_ID,
    )
    place.add_root_category(root_cat_1)
    mock_nomenclature_context.set_place(place)

    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        PRODUCTS_BASE_REQUEST, integration_version=nmn_integration_version,
    )
    assert response.status_code == 200

    gallery = {
        item['type']: item['url']
        for item in response.json()['payload']['categories'][0]['gallery']
    }

    if has_config_gallery:
        assert gallery['tile'] == 'tile_cfg_url/{w}x{h}'
    elif has_nomenclature_gallery:
        assert gallery['tile'] == 'url_nmn/{w}x{h}'
    else:
        assert 'tile' not in gallery

    if has_nomenclature_gallery and not force_gallery_from_config:
        assert (
            gallery['banner_carousel' if is_custom else 'categories_carousel']
            == 'url_nmn/{w}x{h}'
        )
        assert (
            'categories_carousel'
            if is_custom
            else 'banner_carousel' not in gallery
        )
    else:
        assert gallery['banner_carousel'] == 'banner_cfg_url/{w}x{h}'
        assert gallery['categories_carousel'] == 'category_cfg_url/{w}x{h}'
