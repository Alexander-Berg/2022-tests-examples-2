import asynctest
import pytest

from eats_menu_processor.components.menu_processor import exceptions
from eats_menu_processor.components.menu_processor import (  # noqa: E501 pylint: disable=C5521
    MenuProcessor,
)


async def test_raise_exception_if_s3_file_not_exists(
        stq3_context, mds3_client_mock,
):
    mds3_client_mock.get_object = asynctest.CoroutineMock(return_value=None)
    with pytest.raises(exceptions.EMPMenuNotFound):
        await MenuProcessor(stq3_context).process(
            s3_link='/s3/key/file.json',
            brand_id='brand_id__1',
            place_group_id='place_group_id__1',
            place_id='place_id__1',
        )


async def test_menu_processor_get_menu(
        stq3_context, mds3_client_mock, mds3_menu_object,
):
    s3_key = '/s3/key/file.json'
    as_json = [{'name': 'position_1', 'value': 123}]
    as_bytes = b'[{"name": "position_1", "value": 123}]'

    mds3_menu_object._body = as_bytes  # pylint: disable=W0212
    mds3_client_mock.get_object.return_value = mds3_menu_object

    res = await MenuProcessor(stq3_context).get_menu(s3_key)
    assert res == as_json

    args, _ = mds3_client_mock.get_object.call_args
    assert args == (s3_key,)


async def test_menu_processor_put_menu(stq3_context, mds3_client_mock):
    s3_key = '/s3/key/file.txt'
    as_json = [{'name': 'позиция_1', 'value': 123}]
    as_str = '[{"name": "позиция_1", "value": 123}]'
    await MenuProcessor(stq3_context).put_menu(s3_key, as_json)

    args, _ = mds3_client_mock.upload_content.call_args
    assert args == (s3_key, as_str)


async def test_processor_processing_menu(
        stq3_context,
        mds3_client_mock,
        emp_filters_factory,
        patch,
        mds3_menu_object,
        load_json,
):

    origin_key = '/s3/file/origin_menu.json'
    processed_key = '/s3/file/origin_menu_processed.json'
    filtered_key = '/s3/file/origin_menu_filtered.csv'

    menu = load_json('menu.json')

    menu_processor = MenuProcessor(stq3_context)
    menu_processor.get_menu = asynctest.CoroutineMock(return_value=menu)

    @patch(
        'eats_menu_processor.components.menu_processor.'
        'DevFiltersHandler.handle',
    )
    async def _dev_filters_handle(menu):
        return menu

    @patch(
        'eats_menu_processor.components.menu_processor.'
        'FilteredCategoriesHandler.handle',
    )
    async def _filtered_categories_handle(menu):
        return menu

    @patch(
        'eats_menu_processor.components.menu_processor.'
        'ContentFiltersHandler.handle',
    )
    async def _content_filters_handle(menu):
        return menu

    @patch(
        'eats_menu_processor.components.menu_logging.'
        'CsvPushHandler.put_filtered_menu',
    )
    async def _log_handle(filtered_menu_s3_key, data):
        assert filtered_menu_s3_key == filtered_key
        assert data == load_json('log_menu.json')
        return

    menu_processor.put_menu = asynctest.CoroutineMock()

    result_key = await menu_processor.process(
        s3_link=origin_key,
        brand_id='brand_id',
        place_group_id='place_group_id__1',
        place_id='place_id',
    )

    assert result_key == processed_key

    args, _ = menu_processor.put_menu.call_args
    assert menu_processor.put_menu.called
    assert args == (processed_key, menu)


async def test_processor_verify_identical_menu(
        stq3_context,
        mds3_client_mock,
        emp_filters_factory,
        patch,
        mds3_menu_object,
        load_json,
):

    origin_key = '/s3/file/origin_menu.json'
    processed_key = '/s3/file/origin_menu_processed.json'

    menu = load_json('menu.json')

    menu_processor = MenuProcessor(stq3_context)
    menu_processor.get_menu = asynctest.CoroutineMock(return_value=menu)
    menu_processor.put_menu = asynctest.CoroutineMock()

    result_key = await menu_processor.process(
        s3_link=origin_key,
        brand_id='brand_id',
        place_group_id='place_group_id__1',
        place_id='place_id',
        is_identical=True,
    )

    assert result_key == processed_key

    assert not menu_processor.put_menu.called


async def test_processor_verify_identical_menu_404(
        stq3_context,
        mds3_client_mock,
        emp_filters_factory,
        patch,
        mds3_menu_object,
        load_json,
):
    mds3_client_mock.head_object = asynctest.CoroutineMock(return_value=None)

    origin_key = '/s3/file/origin_menu.json'
    processed_key = '/s3/file/origin_menu_processed.json'

    menu = load_json('menu.json')

    menu_processor = MenuProcessor(stq3_context)
    menu_processor.get_menu = asynctest.CoroutineMock(return_value=menu)
    menu_processor.put_menu = asynctest.CoroutineMock()

    result_key = await menu_processor.process(
        s3_link=origin_key,
        brand_id='brand_id',
        place_group_id='place_group_id__1',
        place_id='place_id',
        is_identical=True,
    )

    assert result_key == processed_key

    assert menu_processor.put_menu.called
