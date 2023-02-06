import pytest

import tests_eats_full_text_search_indexer.items_preview as item_preview


SERVICE = 'eats_fts'
PREFIX = 4
RESTMENUITEM = 4

TIME_CALLED = 0

EXPECTED_DOCUMENTS = {
    '/place_slug/items/1111111': {
        'i_pid': {'type': '#ip', 'value': 1},
        's_rest_menu_storage_id': {'type': '#lp', 'value': '1111111'},
        'i_type': {'type': '#ip', 'value': RESTMENUITEM},
        's_place_slug': {'type': '#lp', 'value': 'place_slug'},
        'title': {'type': '#zp', 'value': 'item_name_1'},
        'url': '/place_slug/items/1111111',
    },
    '/place_slug/items/2222222': {
        'i_pid': {'type': '#ip', 'value': 1},
        's_rest_menu_storage_id': {'type': '#lp', 'value': '2222222'},
        'i_type': {'type': '#ip', 'value': RESTMENUITEM},
        's_place_slug': {'type': '#lp', 'value': 'place_slug'},
        'title': {'type': '#zp', 'value': 'item_name_2'},
        'url': '/place_slug/items/2222222',
        'z_category_names': {'type': '#zp', 'value': 'category_1'},
    },
    '/place_slug/items/3333333': {
        'i_pid': {'type': '#ip', 'value': 1},
        's_rest_menu_storage_id': {'type': '#lp', 'value': '3333333'},
        'i_type': {'type': '#ip', 'value': RESTMENUITEM},
        's_place_slug': {'type': '#lp', 'value': 'place_slug'},
        'title': {'type': '#zp', 'value': 'item_name_3'},
        'url': '/place_slug/items/3333333',
        'z_category_names': {'type': '#zp', 'value': 'category_1 category_2'},
    },
}


EXPECTED_MODIFY_PAYLOAD = {'action': 'modify', 'docs': [], 'prefix': PREFIX}

EXPECTED_DELETE_PAYLOAD = {
    'action': 'delete',
    'docs': [{'url': '/place_slug/items/4444444'}],
    'prefix': PREFIX,
}


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_INDEXER_UPDATE_REST_PLACE_SETTINGS={
        'saas_settings': {
            'service_alias': SERVICE,
            'prefix': PREFIX,
            'place_document_batch_size': 1,
        },
        'fail_limit': 1,
    },
)
@pytest.mark.pgsql(
    'eats_full_text_search_indexer', files=['create_place_state.sql'],
)
async def test_rest_indexing_tasks(stq_runner, mockserver):
    tasks_called_type = {
        '/place_slug/items/1111111': '',
        '/place_slug/items/2222222': '',
        '/place_slug/items/3333333': '',
        '/place_slug/items/4444444': '',
    }

    @mockserver.json_handler(
        '/eats-rest-menu-storage/internal/v1/items-preview',
    )
    def items_preview_handler(request):
        expected_ids = ['1111111', '2222222', '3333333', '4444444']
        response_ids = []
        for item in request.json['places'][0]['items']:
            response_ids.append(item)
        assert sorted(expected_ids) == sorted(response_ids)

        assert sorted(request.json['shipping_types']) == sorted(
            ['delivery', 'pickup'],
        )

        response_items = [
            item_preview.ItemPreview(
                id='1111111',
                name='item_name_1',
                adult=False,
                available=True,
                shipping_types=[
                    item_preview.ShippingType.Pickup,
                    item_preview.ShippingType.Delivery,
                ],
                price='100',
            ).as_dict(),
            item_preview.ItemPreview(  # all fields
                id='2222222',
                name='item_name_2',
                adult=False,
                available=True,
                categories=[
                    item_preview.CategoryInfo(id='111111', name='category_1'),
                ],
                shipping_types=[
                    item_preview.ShippingType.Pickup,
                    item_preview.ShippingType.Delivery,
                ],
                legacy_id=100,
                weight_unit='g',
                weight_value='25',
                pictures=[
                    item_preview.Picture(
                        url='https://testing.eda.tst.yandex.net/get-eda/3925/a705aa26d61d164f19e656df96ccac7b',  # noqa: E501
                    ),
                ],
                price='200',
            ).as_dict(),
            item_preview.ItemPreview(
                id='3333333',
                name='item_name_3',
                adult=False,
                available=True,
                shipping_types=[
                    item_preview.ShippingType.Pickup,
                    item_preview.ShippingType.Delivery,
                ],
                price='300',
                categories=[
                    item_preview.CategoryInfo(id='111111', name='category_1'),
                    item_preview.CategoryInfo(id='222222', name='category_2'),
                ],
            ).as_dict(),
        ]

        place_response = item_preview.ItemsPreviewPlaceResponse(
            place_id='1', items=response_items,
        ).as_dict()
        return item_preview.ItemPreviewResponse(
            places=[place_response],
        ).as_dict()

    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=SERVICE),
    )
    def saas_push(request):
        if request.json['action'] == 'modify':
            url = request.json['docs'][0]['url']
            EXPECTED_MODIFY_PAYLOAD['docs'] = [EXPECTED_DOCUMENTS[url]]
            assert request.json == EXPECTED_MODIFY_PAYLOAD
            tasks_called_type[url] = 'modify'
        elif request.json['action'] == 'delete':
            url = request.json['docs'][0]['url']
            assert request.json == EXPECTED_DELETE_PAYLOAD
            tasks_called_type[url] = 'delete'

        return {
            'written': True,
            'attempts': [
                {
                    'comment': 'ok',
                    'written': True,
                    'attempt': 0,
                    'shard': '0-65535',
                },
            ],
            'comment': 'ok',
        }

    await stq_runner.eats_full_text_search_indexer_update_rest_place.call(
        task_id='sample_task',
        args=(),
        kwargs={
            'place_id': '1',
            'updated': [
                '1111111',  # only required fields
                '2222222',  # all fields
            ],
            'deleted': ['3333333', '4444444'],
        },
        # 3333333 is returned by items-preview so there is 3 modify operations
    )

    assert items_preview_handler.times_called == 1
    assert saas_push.times_called == 4

    expected_task_called = {
        '/place_slug/items/1111111': 'modify',
        '/place_slug/items/2222222': 'modify',
        '/place_slug/items/3333333': 'modify',
        '/place_slug/items/4444444': 'delete',
    }

    assert sorted(expected_task_called, key=lambda item: item[0]) == sorted(
        tasks_called_type, key=lambda item: item[0],
    )
