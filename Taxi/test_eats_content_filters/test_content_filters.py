from eats_content_filters.internal import entities


async def test_content_filters(library_context, load_json, patch):
    base_menu = load_json('base_menu.json')
    content_filter_data = [
        entities.ContentFilterData(
            filter='Товары для дома',
            filter_type=entities.FilterType.TYPE_PLACE_CATEGORY_FILTER.value,  # noqa: F401,E501
            place_id='123',
            place_group_id=None,
            brand_id=None,
        ),
        entities.ContentFilterData(
            filter='Товары для дома',
            filter_type=entities.FilterType.TYPE_PLACE_CATEGORY_CONTAINS_FILTER.value,  # noqa: F401,E501
            place_id=None,
            place_group_id='123',
            brand_id=None,
        ),
        entities.ContentFilterData(
            filter='Товары для дома',
            filter_type=entities.FilterType.TYPE_PLACE_CATEGORY_EQUAL_FILTER.value,  # noqa: F401,E501
            place_id=None,
            place_group_id=None,
            brand_id='123',
        ),
        entities.ContentFilterData(
            filter='Насадка SESITIVE для PICOBELLO XL',
            filter_type=entities.FilterType.TYPE_PLACE_ITEM_FILTER.value,
            place_id='123',
            place_group_id=None,
            brand_id=None,
        ),
        entities.ContentFilterData(
            filter='Насадка SESITIVE для PICOBELLO XL',
            filter_type=entities.FilterType.TYPE_PLACE_ITEM_CONTAINS_FILTER.value,  # noqa: F401,E501
            place_id=None,
            place_group_id='123',
            brand_id=None,
        ),
        entities.ContentFilterData(
            filter='Насадка SESITIVE для PICOBELLO XL',
            filter_type=entities.FilterType.TYPE_PLACE_ITEM_EQUAL_FILTER.value,  # noqa: F401,E501
            place_id=None,
            place_group_id=None,
            brand_id='123',
        ),
        entities.ContentFilterData(
            filter='Двигается очень быстро',
            filter_type=entities.FilterType.TYPE_PLACE_OPTION_GROUP_FILTER.value,  # noqa: F401,E501
            place_id='123',
            place_group_id=None,
            brand_id=None,
        ),
        entities.ContentFilterData(
            filter='Двигается очень быстро',
            filter_type=entities.FilterType.TYPE_PLACE_OPTION_GROUP_CONTAINS_FILTER.value,  # noqa: F401,E501
            place_id=None,
            place_group_id='123',
            brand_id=None,
        ),
        entities.ContentFilterData(
            filter='Двигается очень быстро',
            filter_type=entities.FilterType.TYPE_PLACE_OPTION_GROUP_EQUAL_FILTER.value,  # noqa: F401,E501
            place_id=None,
            place_group_id=None,
            brand_id='123',
        ),
        entities.ContentFilterData(
            filter='Фильтруемая опция',
            filter_type=entities.FilterType.TYPE_PLACE_OPTION_CONTAINS_FILTER.value,  # noqa: F401,E501
            place_id=None,
            place_group_id='123',
            brand_id=None,
        ),
    ]
    menu = library_context.content_filters.transform(
        base_menu, content_filter_data,
    )
    assert menu == load_json('base_menu_result.json')
