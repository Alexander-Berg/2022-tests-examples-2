import asynctest
import pytest

from eats_menu_processor.components import menu_processor


@pytest.mark.pgsql('eats_menu_processor', files=['content_filters.sql'])
async def test_content_filters(stq3_context, load_json):
    origin_menu = load_json('menu_category.json')
    filtered_menu = load_json('result_category_all_black_list.json')

    handler = menu_processor.ContentFiltersHandler(
        stq3_context, brand_id=None, place_group_id=None, place_id='123',
    )

    assert filtered_menu == await handler.handle(origin_menu)


async def test_not_raise_exception_if_known_exception(
        stq3_context, mds3_client_mock,
):
    menu_processor.ContentFiltersHandler._handle = (  # pylint: disable=W0212
        asynctest.CoroutineMock(side_effect=KeyError)
    )
    await menu_processor.ContentFiltersHandler(
        stq3_context,
        brand_id='brand_id',
        place_group_id='place_group_id__1',
        place_id='place_id',
    ).handle({})


async def test_raise_exception_if_unknown_exception(
        stq3_context, mds3_client_mock,
):
    menu_processor.ContentFiltersHandler._handle = (  # pylint: disable=W0212
        asynctest.CoroutineMock(side_effect=Exception)
    )
    with pytest.raises(Exception):
        await menu_processor.ContentFiltersHandler(
            stq3_context,
            brand_id='brand_id',
            place_group_id='place_group_id__1',
            place_id='place_id',
        ).handle({})
