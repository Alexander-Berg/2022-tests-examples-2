import json

import aiohttp
import pytest

from eats_integration_offline_orders.generated.cron import run_cron


IMAGE_ID = 'img_id'
GROUP_ID = 1
IMAGE_PNG = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x01\x03\x00\x00\x00%\xdbV\xca\x00\x00\x00\x01sRGB\x01\xd9\xc9\x7f\x00'
    b'\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00'
    b'\x00\x00\x03PLTE\xff\xff\xff\xa7\xc4\x1b\xc8\x00\x00\x00\nIDATx\x9cc`'
    b'\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
)


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'restaurants_options.sql', 'menu.sql'],
)
async def test_fetch_new_menu(
        cron_context,
        patch_aiohttp_session,
        load_binary,
        response_mock,
        patch,
        mockserver,
        load_json,
        place_id,
        restaurant_slug,
):
    deleted_counter = 0

    @patch('taxi.clients.mds_avatars.MDSAvatarsClient.delete')
    async def _mds_avatars_delete_mock(*args, **kwargs):
        nonlocal deleted_counter
        deleted_counter += 1
        return 200

    @patch(
        'eats_integration_offline_orders.components.avatars.'
        'check_content_is_image',
    )
    def _check_content_is_image(*args, **kwargs):
        return True

    @patch('taxi.clients.mds_avatars.MDSAvatarsClient.upload')
    async def _mds_avatars_upload_mock(*args, **kwargs):
        return GROUP_ID, {}

    @patch(
        'eats_integration_offline_orders.components.avatars.'
        'generate_image_id',
    )
    def _generate_image_id(*args, **kwargs):
        return IMAGE_ID

    @mockserver.handler(
        f'/rkeeper-cloud/api/menu/{restaurant_slug}/composition',
    )
    def _get_menu(request):
        return mockserver.make_response(
            json=load_json('rkeeper_response_data.json'),
        )

    @mockserver.handler('/image/', prefix=True)
    def _image_download_handler(request):
        if request.path_qs.endswith('utka.png'):
            return aiohttp.web.Response(
                status=200, body=load_binary('utka.png'),
            )
        if request.path_qs.endswith('qr.jpg'):
            return mockserver.make_response(IMAGE_PNG)
        return mockserver.make_response(status=404)

    await run_cron.main(
        ['eats_integration_offline_orders.crontasks.fetch_menu', '-t', '0'],
    )

    updated_menu = await cron_context.queries.menu.get_by_place_id(place_id)
    updated_menu.apply_update()

    assert updated_menu
    assert not updated_menu.updates
    assert not updated_menu.stop_list
    assert len(updated_menu.menu.items) == 4
    assert deleted_counter == 2

    in_db_menu = await cron_context.pg.master.fetchval(
        'SELECT menu FROM menu where place_id=$1;', str(place_id),
    )

    assert json.loads(in_db_menu) == {
        'items': {
            # new image, overwritten
            'menu_item_id__1': {
                'id': 'menu_item_id__1',
                'price': 100.0,
                'title': 'Булочка',
                'volume': '50 г',
                'weight': None,
                'category_id': 'menu_category_id__1',
                'description': 'с изюмом',
                'refresh_image_hash': '1',
                'original_avatar_image_id': '1/img_id',
            },
            # old image, same hash
            'menu_item_id__2': {
                'id': 'menu_item_id__2',
                'price': 200.0,
                'title': 'Ватрушка',
                'volume': '70',
                'weight': None,
                'category_id': 'menu_category_id__1',
                'description': 'оч вкусная',
                'refresh_image_hash': '2',
                'original_avatar_image_id': '1/img_id0',
            },
            # old image - new failed to download
            'menu_item_id__3': {
                'id': 'menu_item_id__3',
                'price': 200.0,
                'title': 'что-то с чем-то',
                'volume': '70',
                'weight': None,
                'category_id': 'menu_category_id__1',
                'description': 'ничто без никто',
                'refresh_image_hash': '0',
                'original_avatar_image_id': '2/img_id3',
            },
            # new image
            'menu_item_id__4': {
                'id': 'menu_item_id__4',
                'price': 300.0,
                'title': 'черте что',
                'volume': '700 гр',
                'weight': None,
                'category_id': 'menu_category_id__1',
                'description': 'мешанина всего',
                'refresh_image_hash': '4',
                'original_avatar_image_id': '1/img_id',
            },
            # item 5 deleted with his image
        },
        'revision': None,
        'categories': {
            'menu_category_id__1': {
                'id': 'menu_category_id__1',
                'title': 'Выпечка',
            },
        },
    }


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql', 'menu.sql'],
)
async def test_fetch_menu_same_menu(
        cron_context,
        patch_aiohttp_session,
        response_mock,
        patch,
        mockserver,
        load_json,
        restaurant_slug,
):
    place_id = 'place_id__3'

    @mockserver.handler(
        f'/rkeeper-cloud/api/menu/{restaurant_slug}/composition',
    )
    def _get_menu(request):
        return mockserver.make_response(
            json=load_json('rkeeper_response_data_same_menu.json'),
        )

    menu_before = await cron_context.queries.menu.get_by_place_id(place_id)

    await run_cron.main(
        ['eats_integration_offline_orders.crontasks.fetch_menu', '-t', '0'],
    )

    menu_after = await cron_context.queries.menu.get_by_place_id(place_id)

    assert menu_before == menu_after
