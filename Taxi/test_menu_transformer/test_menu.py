import json

import pytest


# pylint: disable=W0612,C5521


async def test_services_calls(library_context, load_json, patch):
    calls = []

    @patch(
        'menu_transformer.content.services.'
        'rebuild_categories_service.RebuildCategoriesService.transform',
    )
    def rebuild_categories_service(menu):
        calls.append('rebuild_categories_service')

    @patch(
        'menu_transformer.content.services.'
        'transform_menu_service.TransformMenuService.transform',
    )
    def transform_menu_service(menu):
        calls.append('transform_menu_service')

    @patch(
        'menu_transformer.content.services.'
        'skip_items_by_pattern_service.SkipItemsByPatternService.transform',
    )
    def skip_items_by_pattern_service(menu):
        calls.append('skip_items_by_pattern_service')

    library_context.menu_transformer.transform(
        load_json('menu_data.json'), load_json('dev_filter.json'),
    )

    assert calls == [
        'rebuild_categories_service',
        'skip_items_by_pattern_service',
        'transform_menu_service',
    ]


async def test_transformers_calls(library_context, load_json, patch):
    calls = []

    @patch(
        'menu_transformer.content.transformers.'
        'category_image_transformer.CategoryImageTransformer.transform',
    )
    def category_image_transformer(menu):
        calls.append('category_image_transformer')

    @patch(
        'menu_transformer.content.transformers.'
        'category_name_transformer.CategoryNameTransformer.transform',
    )
    def category_name_transformer(menu):
        calls.append('category_name_transformer')

    @patch(
        'menu_transformer.content.transformers.'
        'description_transformer.DescriptionTransformer.transform',
    )
    def description_transformer(menu):
        calls.append('description_transformer')

    @patch(
        'menu_transformer.content.transformers.'
        'name_transformer.NameTransformer.transform',
    )
    def name_transformer(menu):
        calls.append('name_transformer')

    library_context.menu_transformer.transform(
        load_json('menu_data.json'), load_json('dev_filter.json'),
    )

    assert calls == [
        'name_transformer',
        'category_name_transformer',
        'name_transformer',
        'description_transformer',
        'category_name_transformer',
        'category_image_transformer',
    ]


async def test_filters_calls(library_context, load_json, patch):
    calls = []

    @patch(
        'menu_transformer.content.filters.'
        'capitalize_first_letter_filter.CapitalizeFirstLetterFilter.filter',
    )
    def capitalize_first_letter_filter(text):
        calls.append('capitalize_first_letter_filter')

    @patch(
        'menu_transformer.content.filters.'
        'html_tags_filter.HtmlTagsFilter.filter',
    )
    def html_tags_filter(text):
        calls.append('html_tags_filter')

    @patch(
        'menu_transformer.content.filters.'
        'punctuation_filter.PunctuationFilter.filter',
    )
    def punctuation_filter(text):
        calls.append('punctuation_filter')

    @patch(
        'menu_transformer.content.filters.'
        'replacement_filter.ReplacementFilter.filter',
    )
    def replacement_filter(text):
        calls.append('replacement_filter')

    @patch(
        'menu_transformer.content.filters.'
        'uppercase_filter.UppercaseFilter.filter',
    )
    def uppercase_filter(text):
        calls.append('uppercase_filter')

    library_context.menu_transformer.transform(
        load_json('menu_data.json'), load_json('dev_filter.json'),
    )

    assert calls == [
        'uppercase_filter',
        'punctuation_filter',
        'html_tags_filter',
        'replacement_filter',
        'replacement_filter',
        'replacement_filter',
        'replacement_filter',
        'uppercase_filter',
        'punctuation_filter',
        'capitalize_first_letter_filter',
        'replacement_filter',
        'uppercase_filter',
        'punctuation_filter',
        'capitalize_first_letter_filter',
        'replacement_filter',
        'uppercase_filter',
        'punctuation_filter',
        'capitalize_first_letter_filter',
    ]


@pytest.mark.parametrize(
    'type_exception, dev_filter',
    [
        (type(None), 'dev_filter_null.json'),
        (type(None), 'dev_filter_correct.json'),
        (type(None), 'dev_filter_correct_str.json'),
        (json.JSONDecodeError, 'dev_filter_incorrect_str.json'),
        (type(None), 'dev_filter_incorrect_content.json'),
        (type(None), 'dev_filter_incorrect_service.json'),
        (type(None), 'dev_filter_incorrect_transform.json'),
        (type(None), 'dev_filter_incorrect_filter.json'),
        (type(None), 'dev_filter_incorrect_filter_type.json'),
        (type(None), 'dev_filter_incorrect_service_type.json'),
        (type(None), 'dev_filter_incorrect_transform_type.json'),
    ],
)
async def test_dev_filter_valid(
        library_context, load_json, type_exception, dev_filter,
):
    exception_result = None

    try:
        library_context.menu_transformer.transform(
            load_json('menu_data.json'), load_json(dev_filter)['data'],
        )
    except Exception as exc:  # pylint: disable = W0703
        exception_result = exc

    assert isinstance(exception_result, type_exception)

    if isinstance(exception_result, type(None)):
        assert (
            load_json('dev_filter_correct_valid_result.json')
            == library_context.menu_transformer.valid_dev_filter(
                load_json(dev_filter)['data'],
            )
        )
