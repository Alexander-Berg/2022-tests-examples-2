import pytest

from promotions.logic import const


URL = '/admin/promotions/list/'


@pytest.mark.parametrize(
    ['promotion_type', 'data_items', 'name'],
    [
        (
            'fullscreen',
            [
                {'id': 'id1', 'name': 'banner 1'},
                {'id': 'id2', 'name': 'banner 12'},
                {'id': 'id5', 'name': 'banner 5'},
            ],
            'ban',
        ),
        ('story', [{'id': 'story_id2', 'name': 'story 2'}], 'stor'),
        (
            'card',
            [
                {'id': 'id3', 'name': 'banner 3'},
                {'id': 'card_2', 'name': 'banner card 2'},
            ],
            'ban',
        ),
        (
            'promo_on_map',
            [
                {'id': 'promo_on_map_id', 'name': 'promo_on_map_name'},
                {
                    'id': 'published_promo_on_map_id',
                    'name': 'published_promo_on_map_name',
                },
                {
                    'id': 'published_by_campaign_promo_on_map_id',
                    'name': 'published_by_campaign_promo_on_map_name',
                },
                {
                    'id': 'published_by_two_campaigns_promo_on_map_id',
                    'name': 'published_by_two_campaigns_promo_on_map_name',
                },
                {
                    'id': 'stopped_promo_on_map_id',
                    'name': 'stopped_promo_on_map_name',
                },
                {
                    'id': 'expired_promo_on_map_id',
                    'name': 'expired_promo_on_map_name',
                },
            ],
            'map_name',
        ),
        (
            'eda_banner',
            [{'id': 'eda_published', 'name': 'eda_banner_published'}],
            'eda',
        ),
        (
            'collection',
            [
                {
                    'id': 'default_collection_id',
                    'name': 'default_collection_name',
                },
                {'id': 'collection_id_1', 'name': 'collection_name_1'},
            ],
            '',
        ),
        (
            'collection',
            [{'id': 'collection_id_1', 'name': 'collection_name_1'}],
            '1',
        ),
        ('collection', [], 'does_not_exist'),
        (
            'showcase',
            [
                {'id': 'default_showcase_id', 'name': 'default_showcase_name'},
                {'id': 'showcase_id_1', 'name': 'showcase_name_1'},
                {
                    'id': 'published_showcase_id',
                    'name': 'published_showcase_name',
                },
                {
                    'id': 'showcase_with_untitled_collection_id',
                    'name': 'showcase_with_untitled_collection_name',
                },
            ],
            '',
        ),
        (
            'showcase',
            [
                {
                    'id': 'published_showcase_id',
                    'name': 'published_showcase_name',
                },
            ],
            'pub',
        ),
        ('showcase', [], 'does_not_exist'),
        (
            'totw_banner',
            [{'id': 'totw_banner_1', 'name': 'totw_banner_name'}],
            'totw_banner',
        ),
        (
            'object_over_map',
            [{'id': 'object_over_map_1', 'name': 'object_over_map_name'}],
            'object_over_map',
        ),
        (
            'grocery_informer',
            [
                {
                    'id': 'grocery_published',
                    'name': 'grocery_informer_published',
                },
            ],
            'grocery',
        ),
    ],
)
@pytest.mark.pgsql(
    'promotions',
    files=[
        'pg_promotions_admin.sql',
        'pg_promotions_promo_on_map.sql',
        'pg_promotions_collections.sql',
        'pg_promotions_showcases.sql',
    ],
)
async def test_list(web_app_client, promotion_type, data_items, name):
    response = await web_app_client.get(
        f'/admin/promotions/list/?type={promotion_type}&name={name}',
    )
    data = await response.json()
    assert response.status == 200
    assert data['items'] == data_items
    assert data['total'] == len(data_items)
    # default values
    assert data['offset'] == 0
    assert data['limit'] == const.DEFAULT_PAGING_LIMIT


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
@pytest.mark.parametrize(
    ['promotion_type', 'name', 'status', 'expected_answer'],
    [
        (
            'fullscreen',
            None,
            None,
            [
                {'id': 'id1', 'name': 'banner 1'},
                {'id': 'id2', 'name': 'banner 12'},
                {'id': 'id5', 'name': 'banner 5'},
            ],
        ),
        (
            'fullscreen',
            '',
            None,
            [
                {'id': 'id1', 'name': 'banner 1'},
                {'id': 'id2', 'name': 'banner 12'},
                {'id': 'id5', 'name': 'banner 5'},
            ],
        ),
        (
            'fullscreen',
            'banner',
            None,
            [
                {'id': 'id1', 'name': 'banner 1'},
                {'id': 'id2', 'name': 'banner 12'},
                {'id': 'id5', 'name': 'banner 5'},
            ],
        ),
        ('fullscreen', '12', None, [{'id': 'id2', 'name': 'banner 12'}]),
        ('fullscreen', '999', None, []),
        (
            'card',
            None,
            None,
            [
                {'id': 'id3', 'name': 'banner 3'},
                {'id': 'card_2', 'name': 'banner card 2'},
            ],
        ),
        (
            'card',
            '',
            None,
            [
                {'id': 'id3', 'name': 'banner 3'},
                {'id': 'card_2', 'name': 'banner card 2'},
            ],
        ),
        ('card', 'er 3', None, []),
        ('card', '42', None, []),
        (
            'notification',
            None,
            None,
            [
                {'id': 'notification_3', 'name': 'banner notification 3'},
                {'id': '6b2ee5529f5b4ffc8fea7008e6913ca6', 'name': '12'},
            ],
        ),
        (
            'notification',
            '',
            None,
            [
                {'id': 'notification_3', 'name': 'banner notification 3'},
                {'id': '6b2ee5529f5b4ffc8fea7008e6913ca6', 'name': '12'},
            ],
        ),
        ('notification', 'banner 4', None, []),
        ('notification', '777', None, []),
        (
            'notification',
            None,
            'archived',
            [{'id': 'id4', 'name': 'banner 4'}],
        ),
        ('notification', '', 'archived', [{'id': 'id4', 'name': 'banner 4'}]),
        (
            'notification',
            'banner 4',
            'archived',
            [{'id': 'id4', 'name': 'banner 4'}],
        ),
        ('notification', '777', 'archived', []),
        (
            'totw_banner',
            'totw_banner_name',
            'published',
            [{'id': 'totw_banner_1', 'name': 'totw_banner_name'}],
        ),
        (
            'object_over_map',
            'object_over_map_name',
            'published',
            [{'id': 'object_over_map_1', 'name': 'object_over_map_name'}],
        ),
        (
            'grocery_informer',
            'grocery_informer_published',
            'published',
            [
                {
                    'id': 'grocery_published',
                    'name': 'grocery_informer_published',
                },
            ],
        ),
    ],
)
async def test_list_filters(
        web_app_client, promotion_type, name, status, expected_answer,
):
    url = f'/admin/promotions/list/?type={promotion_type}'
    if name is not None:
        url += f'&name={name}'
    if status is not None:
        url += f'&status={status}'
    response = await web_app_client.get(url)
    data = await response.json()
    assert response.status == 200
    assert data['items'] == expected_answer
    assert data['total'] == len(expected_answer)
    assert data['offset'] == 0
    assert data['limit'] == const.DEFAULT_PAGING_LIMIT


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
@pytest.mark.parametrize(
    'tag_name,promotion_type,status,expected_answer',
    [
        pytest.param(
            'tag1',
            'fullscreen',
            None,
            [{'id': 'id1', 'name': 'banner 1'}],
            id='one_doc',
        ),
        pytest.param(
            'tag77',
            'deeplink_shortcut',
            'archived',
            [
                {'id': 'deeplink_shortcut_id1', 'name': 'deeplink_shortcut 1'},
                {'id': 'deeplink_shortcut_id2', 'name': 'deeplink_shortcut 2'},
            ],
            id='multiple_docs',
        ),
        pytest.param(
            'nonexistent', 'fullscreen', None, [], id='no_docs_at_all',
        ),
    ],
)
async def test_list_meta_tags_filter(
        web_app_client, tag_name, promotion_type, status, expected_answer,
):
    params = {'meta_tag': tag_name, 'type': promotion_type}
    if status:
        params['status'] = status
    response = await web_app_client.get(URL, params=params)
    data = await response.json()
    assert response.status == 200
    assert data['items'] == expected_answer


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
@pytest.mark.parametrize(
    'meta_type,promotion_type,status,expected_answer',
    [
        pytest.param(
            'promo_block',
            'promo_on_summary',
            None,
            [{'id': 'promo_on_summary1', 'name': 'express'}],
            id='one_doc',
        ),
        pytest.param(
            'meta_type',
            'deeplink_shortcut',
            'archived',
            [
                {'id': 'deeplink_shortcut_id1', 'name': 'deeplink_shortcut 1'},
                {'id': 'deeplink_shortcut_id2', 'name': 'deeplink_shortcut 2'},
            ],
            id='multiple_docs',
        ),
        pytest.param('nonexistent', 'story', None, [], id='no_docs_at_all'),
    ],
)
async def test_list_meta_type_filter(
        web_app_client, meta_type, promotion_type, status, expected_answer,
):
    params = {'meta_type': meta_type, 'type': promotion_type}
    if status:
        params['status'] = status
    response = await web_app_client.get(URL, params=params)
    data = await response.json()
    assert response.status == 200
    assert data['items'] == expected_answer


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
@pytest.mark.parametrize(
    ['offset', 'limit', 'expected_count'],
    [
        (0, 10, 3),
        (0, 2, 2),
        (2, 4, 1),
        (1, 1000, 2),
        (0, 1000, 3),
        (5, 100, 0),
        (100, 1000, 0),
    ],
)
async def test_list_paging(web_app_client, offset, limit, expected_count):
    response = await web_app_client.get(
        f'/admin/promotions/list/?offset={offset}&limit={limit}'
        f'&type=fullscreen',
    )
    data = await response.json()
    assert response.status == 200
    assert len(data['items']) == expected_count
    assert data['total'] == 3
    assert data['offset'] == offset
    assert data['limit'] == min(limit, const.MAX_PAGING_LIMIT)
