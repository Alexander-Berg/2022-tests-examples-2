import asyncio
from collections import defaultdict

import aiohttp
import pytest
from aiohttp import web

from stall.client.grocery_tags import GroceryTagsClient
from stall.client.grocery_tags import GroceryTagsError
from stall.client.grocery_tags import GroceryTagsUploadItem
from stall.client.grocery_tags import GroceryTagsUploadTag


async def test_common(tap, ext_api):
    _tags_repo = defaultdict(lambda: defaultdict(list))

    async def handle(request):
        data = await request.json()
        append = data.get('append', [])
        remove = data.get('remove', [])

        for tags in append:
            entity_type = tags['entity_type']
            for tag in tags['tags']:
                if tag['entity'] not in _tags_repo[entity_type]:
                    _tags_repo[entity_type][tag['entity']].append(tag)

        for tags in remove:
            entity_type = tags['entity_type']
            for tag in tags['tags']:
                if tag['entity'] in _tags_repo[entity_type]:
                    _tags_repo[entity_type][tag['entity']].remove(tag)
                    if not _tags_repo[entity_type][tag['entity']]:
                        del _tags_repo[entity_type][tag['entity']]
            if not _tags_repo[entity_type]:
                del _tags_repo[entity_type]

        return {'code': 'OK'}

    with tap.plan(2, 'проставляем и удаляем теги'):
        async with await ext_api('grocery_tags', handle) as client:
            client: GroceryTagsClient
            await client.upload(
                provider_id='__provider_id__',
                req_id='__req_id__',
                append=[
                    GroceryTagsUploadItem({
                        'entity_type': 'item_id',
                        'tags': [
                            GroceryTagsUploadTag({
                                'entity': '__item_id__',
                                'name': '__tag_name__',
                            })
                        ]
                    })
                ]
            )

            tap.eq(_tags_repo, {
                'item_id': {
                    '__item_id__': [{
                        'entity': '__item_id__',
                        'name': '__tag_name__',
                    }]
                }
            }, 'tag appended')

            await client.upload(
                provider_id='__provider_id__',
                req_id='__req_id__',
                remove=[
                    GroceryTagsUploadItem({
                        'entity_type': 'item_id',
                        'tags': [
                            GroceryTagsUploadTag({
                                'entity': '__item_id__',
                                'name': '__tag_name__',
                            })
                        ]
                    })
                ]
            )

            tap.eq(_tags_repo, {}, 'tag removed')


@pytest.mark.parametrize('client_error', [
        aiohttp.ClientError,
        asyncio.TimeoutError,
])
async def test_client_error(tap, ext_api, client_error):
    # pylint: disable=unused-argument
    async def handle(request):
        raise client_error

    with tap.plan(1, f'GroceryTagsError при {client_error.__name__}'):
        async with await ext_api('grocery_tags', handle) as client:
            with tap.raises(GroceryTagsError):
                await client.upload(
                    provider_id='__provider_id__',
                    req_id='__req_id__',
                    append=[
                        GroceryTagsUploadItem({
                            'entity_type': 'item_id',
                            'tags': [
                                GroceryTagsUploadTag({
                                    'entity': '__item_id__',
                                    'name': '__tag_name__',
                                })
                            ]
                        })
                    ]
                )


@pytest.mark.parametrize('status', [400, 401, 403, 500, 504])
async def test_response_error(tap, ext_api, status):
    # pylint: disable=unused-argument
    async def handle(request):
        return web.Response(status=status)

    with tap.plan(1, f'GroceryTagsError при status={status}'):
        async with await ext_api('grocery_tags', handle) as client:
            with tap.raises(GroceryTagsError):
                await client.upload(
                    provider_id='__provider_id__',
                    req_id='__req_id__',
                    append=[
                        GroceryTagsUploadItem({
                            'entity_type': 'item_id',
                            'tags': [
                                GroceryTagsUploadTag({
                                    'entity': '__item_id__',
                                    'name': '__tag_name__',
                                })
                            ]
                        })
                    ]
                )
