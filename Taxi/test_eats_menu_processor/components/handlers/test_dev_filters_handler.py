import json

import asynctest
import pytest

import menu_transformer

from eats_menu_processor.components import menu_processor


async def test_dev_filters(stq3_context, load_json, emp_filters_factory):

    origin_menu = load_json('origin_menu.json')
    processed_menu = load_json('processed_menu.json')

    place_group_id = 'place_group_id__1'

    handler = menu_processor.DevFiltersHandler(stq3_context, place_group_id)
    emp_filters_factory(
        schema=json.dumps(load_json('filters.json')),
        place_group_id=place_group_id,
    )

    assert processed_menu == await handler.handle(origin_menu)


async def test_not_raise_exception_if_known_exception(
        stq3_context, mds3_client_mock,
):
    menu_processor.DevFiltersHandler._handle = (  # pylint: disable=W0212
        asynctest.CoroutineMock(
            side_effect=menu_transformer.DevFilterException,
        )
    )
    await menu_processor.DevFiltersHandler(
        stq3_context, place_group_id='place_group_id__1',
    ).handle({})


async def test_raise_exception_if_unknown_exception(
        stq3_context, mds3_client_mock,
):
    menu_processor.DevFiltersHandler._handle = (  # pylint: disable=W0212
        asynctest.CoroutineMock(side_effect=Exception)
    )
    with pytest.raises(Exception):
        await menu_processor.DevFiltersHandler(
            stq3_context, place_group_id='place_group_id__1',
        ).handle({})
