from tests_grocery_menu.plugins import pigeon_layout as pigeon


def format_menu_group(group_id):
    return {
        'category_group_id': pigeon.GROUP_LEGACY_ID.format(group_id),
        'title_tanker_key': pigeon.LONG_TITLE.format(group_id),
        'short_title_tanker_key': pigeon.SHORT_TITLE.format(group_id),
        'item_meta': pigeon.DEFAULT_META,
    }


async def test_groups(taxi_grocery_menu, mockserver):
    test_id = 1

    @mockserver.json_handler('/pigeon/internal/catalog/v1/groups')
    def _mock_groups(request):
        return {'cursor': 0, 'items': [pigeon.format_pigeon_group(test_id)]}

    response = await taxi_grocery_menu.post(
        '/internal/v1/menu/v1/groups-data', json={'limit': 1, 'cursor': 0},
    )
    assert response.status_code == 200
    assert response.json()['groups'] == [format_menu_group(test_id)]


async def test_groups_data_chunked(taxi_grocery_menu, mockserver):
    @mockserver.json_handler('/pigeon/internal/catalog/v1/groups')
    def _mock_groups(request):
        return {
            'cursor': 0,
            'items': [pigeon.format_pigeon_group(i) for i in range(3)],
        }

    response_len = [2, 1, 0]
    groups = []
    limit = 2
    cursor = 0
    for length in response_len:
        response = await taxi_grocery_menu.post(
            '/internal/v1/menu/v1/groups-data',
            json={'limit': limit, 'cursor': cursor},
        )

        assert response.status_code == 200
        if length == 0:
            assert cursor == response.json()['cursor']
        else:
            cursor = response.json()['cursor']
        assert len(response.json()['groups']) == length
        groups.extend(response.json()['groups'])

    groups_ids_set = set()
    prev_group_id = None
    for item in groups:
        group_id = item['category_group_id']
        groups_ids_set.add(group_id)
        if prev_group_id:
            assert group_id > prev_group_id
        prev_group_id = group_id

    assert len(groups) == len(groups_ids_set)
    assert len(groups) == sum(response_len)
