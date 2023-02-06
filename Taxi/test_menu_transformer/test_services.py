import pytest

from menu_transformer.content import services


async def test_services(library_context, load_json, patch):
    menu = library_context.menu_transformer.transform(
        load_json('menu_data.json'), load_json('dev_filter_services.json'),
    )
    assert menu == load_json('menu_data_services.json')


@pytest.mark.parametrize(
    'arguments, file_name, file_name_transformers, handler_class',
    [
        (
            {
                'arguments': {
                    'move': {
                        'Категория для перемещения': 'Категорию переместили',
                    },
                },
            },
            'menu_rebuild_categories_service_move.json',
            'menu_rebuild_categories_service_move_transform.json',
            services.RebuildCategoriesService,
        ),
        (
            {
                'arguments': {
                    'order': {
                        'Безалкогольные напитки': 18,
                        'Продукты без глютена': 10,
                        'Рыба, икра, морепродукты': 28,
                    },
                },
            },
            'menu_rebuild_categories_service_order.json',
            'menu_rebuild_categories_service_order_transform.json',
            services.RebuildCategoriesService,
        ),
        (
            {
                'arguments': {
                    'rename': {
                        'Категория для переименования': 'Новое имя категории',
                    },
                },
            },
            'menu_rebuild_categories_service_rename.json',
            'menu_rebuild_categories_service_rename_transform.json',
            services.RebuildCategoriesService,
        ),
        (
            {'arguments': {'skip': ['Категория для пропуска']}},
            'menu_rebuild_categories_service_skip.json',
            'menu_rebuild_categories_service_skip_transform.json',
            services.RebuildCategoriesService,
        ),
        (
            {
                'arguments': {
                    'blacklist': [
                        '/(?<!\\w)вино(?!\\w)/ui',
                        '/(?<!\\w)джин(?!\\w)/ui',
                        '/(?<!\\w)пиво(?!\\w)/ui',
                        '/(?<!\\w)текила(?!\\w)/ui',
                        '/(?<!\\w)водка(?!\\w)/ui',
                        '/(?<!\\w)виски(?!\\w)/ui',
                        '/(?<!\\w)шампанское(?!\\w)/ui',
                        '/(?<!\\w)настойка(?!\\w)/ui',
                        '/(?<!\\w)мартини(?!\\w)/ui',
                        '/(?<!\\w)ликер(?!\\w)/ui',
                        '/(?<!\\w)глинтвейн(?!\\w)/ui',
                        '/(?<!\\w)сидр(?!\\w)/ui',
                        '/(?<!\\w)сангрия(?!\\w)/ui',
                    ],
                    'whitelist': [
                        '/(?:ассорти|безалкогольное|соус|деликатесы|закус|комбо\\sпод|креветк|миди|моллюск|набор|сет|смузи|снэк|сыр|тарелка|уксус|хлеб|десерт|картофель|доска)[\\s\\w,\\-]+вино/ui',  # noqa: F401,E501
                        '/(?:торт)[\\s\\w,\\-]+джин/ui',
                        '/(?:пирог)[\\s\\w,\\-]+джин/ui',
                        '/(?:безалкогольное|б\\/а|под|лимонад|макарон|мидии|сет)[\\s\\w,\\-\\(\\)\\.]+пиво/ui',  # noqa: F401,E501
                        '/пиво[\\s\\w]+безалкогольное/ui',
                        '/(?:пенне|пицца)[\\s\\w]+водка/ui',
                        '/(?:пудинг|бургер|ребра|горчица|ножки|закуска|соус|карпаччо|комбо|маринад|набор|паштет|стейк|сет|карамель|барбекю»?|стакан|тартар|тартита|филе|шоколад|мак)[\\s\\w,]+виски/ui',  # noqa: F401,E501
                        '/(?:детское|торт|под|рулет|равиоли)[\\s\\w,\\-]+шампанское/ui',  # noqa: F401,E501
                        '/(?:суп|под|соус|семга)[\\s\\w,\\-]+мартини/ui',
                        '/(?:десерт|мороженое|мясной|пирог|сироп)[\\s\\w,\\-]+ликер/ui',  # noqa: F401,E501
                        '/(?:безалкогольный|соус|салат)[\\s\\w,\\-]+глинтвейн|глинтвейн[\\s\\w\\(\\)]+безалкогольный/ui',  # noqa: F401,E501
                        '/(?:безалкогольный|мидии)[\\s\\w,\\-]+сидр|сидр[\\s\\w\\(\\)]+б\\/а/ui',  # noqa: F401,E501
                    ],
                },
            },
            'menu_skip_items_by_pattern_service.json',
            'menu_skip_items_by_pattern_service_transform.json',
            services.SkipItemsByPatternService,
        ),
        (
            {'arguments': ['412721', '654321']},
            'menu_categories_origin_id_white_list_service.json',
            'menu_categories_origin_id_white_list_service_skip.json',
            services.CategoriesOriginIdWhiteListService,
        ),
        (
            {'arguments': ['1', '3']},
            'menu_items_origin_id_white_list_service.json',
            'menu_items_origin_id_white_list_service_skip.json',
            services.MenuItemsOriginIdWhiteListService,
        ),
        (
            {
                'arguments': {
                    'same_dishes_names': {
                        'Напитки': [
                            'Фреш',
                            'Сок Я',
                            {'name': 'Напиток', 'remove_description': True},
                        ],
                        'Десерты': ['Чизкейк'],
                    },
                },
            },
            'menu_combine_dishes_service.json',
            'menu_combine_dishes_service_answer.json',
            services.CombineDishesService,
        ),
        (
            {
                'arguments': {
                    'same_dishes_names': {
                        'Напитки': [
                            'Фреш',
                            'Сок Я',
                            {'name': 'Напиток', 'remove_description': True},
                        ],
                        'Десерты': ['Чизкейк'],
                    },
                },
            },
            'menu_combine_dishes_service_filtered_item.json',
            'menu_combine_dishes_service_filtered_item_answer.json',
            services.CombineDishesService,
        ),
        (
            {
                'arguments': {
                    'same_dishes_names': {
                        'Напитки': {
                            'name': 'Какой-то напиток',
                            'remove_description': True,
                        },
                        'Десерты': 'Чизкейк',
                    },
                },
            },
            'menu_combine_all_dishes_by_category_service.json',
            'menu_combine_all_dishes_by_category_service_answer.json',
            services.CombineAllDishesByCategoryService,
        ),
        (
            {
                'arguments': {
                    'same_dishes_names': {
                        'Напитки': [
                            'Фреш',
                            'Сок Я',
                            {'name': 'Напиток', 'remove_description': True},
                        ],
                        'Десерты': ['Чизкейк'],
                    },
                },
            },
            'menu_combine_dishes_with_same_description_service.json',
            'menu_combine_dishes_with_same_description_service_answer.json',
            services.CombineDishesWithSameDescriptionService,
        ),
        (
            {'arguments': {'blacklist': [2, 3]}},
            'menu_skip_items_by_origin_id_service.json',
            'menu_skip_items_by_origin_id_service_answer.json',
            services.SkipItemsByOriginIdService,
        ),
        (
            {'arguments': [r'/\s*\b0\sг/u', r'/^0\sмл/u']},
            'remove_menu_items_without_weight_service.json',
            'remove_menu_items_without_weight_service_answer.json',
            services.RemoveMenuItemsWithoutWeightService,
        ),
        (
            {'arguments': [10]},
            'menu_skip_items_with_short_names_service.json',
            'menu_skip_items_with_short_names_service_answer.json',
            services.SkipItemsWithShortNamesService,
        ),
        (
            {'arguments': [r'\.*[Нн]апитки\.*']},
            'menu_skip_categories_by_pattern_service.json',
            'menu_skip_categories_by_pattern_service_answer.json',
            services.SkipCategoriesByPatternService,
        ),
        (
            {'arguments': ['Пиво', 'Вино']},
            'menu_skip_items_with_stop_words_service.json',
            'menu_skip_items_with_stop_words_service_answer.json',
            services.SkipItemsWithStopWordsService,
        ),
        (
            {'arguments': {'1': ['101', '103'], '2': ['103'], '3': '102102'}},
            'menu_remove_options_from_non_required_option_group_service.json',
            'menu_remove_options_from_non_required_option_group_service_answer.json',  # noqa: E501
            services.RemoveOptionsFromNonRequiredOptionGroupService,
        ),
    ],
)
async def test_services_transform(
        load_json, arguments, file_name, file_name_transformers, handler_class,
):
    menu = load_json(file_name)

    handler = handler_class(**arguments)
    handler.transform(menu)
    assert menu == load_json(file_name_transformers)
