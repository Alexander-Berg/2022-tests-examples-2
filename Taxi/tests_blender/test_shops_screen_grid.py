import pytest


HEADERS = {
    'X-Yandex-UID': '12345',
    'X-YaTaxi-UserId': '50b3bc6b41a4484384e34f5360962d12',
}


def check_grid(response, expected_grid, shops_shortcuts):
    cells = response['cells']
    blocks = response['blocks']
    num_cells = len(cells)
    assert num_cells == len(expected_grid)

    shortcut_ids = []

    for i in range(num_cells):
        assert cells[i] == {
            'shortcut': shops_shortcuts[i],
            'width': expected_grid[i][0],
            'height': expected_grid[i][1],
        }, f'Checking cells failed for cell with index {i}'
        shortcut_ids.append(shops_shortcuts[i]['id'])

    assert len(blocks) == 1
    assert blocks[0]['id'] != ''
    assert blocks[0]['shortcut_ids'] == shortcut_ids
    assert blocks[0]['slug'] == 'eats_shops'


async def check_layout(taxi_blender, load_json, num_shops):
    base_body = load_json('base_request.json')
    shops_list = load_json('shop_shortcuts_list.json')
    expected_grids = load_json('expected_grids.json')

    base_scenario_tops = base_body['scenario_tops']

    shops_shortcuts = shops_list[:num_shops]
    req_body = {
        **base_body,
        'scenario_tops': base_scenario_tops + [
            {'scenario': 'eats_shop', 'shortcuts': shops_shortcuts},
        ],
    }

    response = await taxi_blender.post(
        'blender/v1/shops-screen-grid', json=req_body, headers=HEADERS,
    )

    assert response.status_code == 200
    resp_body = response.json()

    expected_grid = expected_grids[num_shops - 1]
    check_grid(resp_body['grid'], expected_grid, shops_shortcuts)


@pytest.mark.experiments3(filename='experiments3.json')
async def test_grid_params(taxi_blender, load_json):
    req_body = load_json('base_request.json')
    response = await taxi_blender.post(
        'blender/v1/shops-screen-grid', json=req_body, headers=HEADERS,
    )

    assert response.status_code == 200
    resp_body = response.json()
    assert 'grid' in resp_body

    assert resp_body['grid']['id'] != ''
    assert resp_body['grid']['width'] == 6


@pytest.mark.experiments3(filename='experiments3.json')
async def test_grid_buildable_shortcuts(taxi_blender, load_json, mockserver):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        resp = load_json('promotions_response.json')
        resp['deeplink_shortcuts'][0]['options']['meta_type'] = 'eats_shop'
        resp['stories'][0]['options']['meta_type'] = 'eats_shop'
        return resp

    req_body = load_json('base_request.json')
    req_body['scenario_tops'][0]['scenario'] = 'eats_shop'
    req_body['scenario_tops'][0]['shortcuts'] = []
    req_body['scenario_tops'][0].update(
        {
            'building_context': {
                'promo_ids_order': [
                    'deeplink_shortcut2_promo_id',
                    'media_story2_promo_id',
                ],
                'shortcuts_promo_ids_to_build': [
                    'deeplink_shortcut2_promo_id',
                    'media_story2_promo_id',
                ],
            },
        },
    )
    response = await taxi_blender.post(
        'blender/v1/shops-screen-grid', json=req_body, headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['grid']['blocks']


@pytest.mark.parametrize('num_shops', [1, 2, 3, 4, 5, 6])
@pytest.mark.experiments3(filename='experiments3.json')
async def test_fixed_layouts(taxi_blender, load_json, num_shops):
    await check_layout(taxi_blender, load_json, num_shops)


@pytest.mark.parametrize('num_shops', [7, 8])
@pytest.mark.experiments3(filename='experiments3.json')
async def test_arbitrary_layouts(taxi_blender, load_json, num_shops):
    await check_layout(taxi_blender, load_json, num_shops)


@pytest.mark.experiments3(filename='experiments3.json')
async def test_zero_shops(taxi_blender, load_json):
    req_body = load_json('base_request.json')
    response = await taxi_blender.post(
        'blender/v1/shops-screen-grid', json=req_body, headers=HEADERS,
    )

    assert response.status_code == 200
    resp_body = response.json()

    assert resp_body['grid']['blocks'] == []
    assert resp_body['grid']['cells'] == []


@pytest.mark.experiments3(filename='experiments3.json')
async def test_invalid_scenario_tops(taxi_blender, load_json):
    base_body = load_json('base_request.json')
    shops_list = load_json('shop_shortcuts_list.json')

    base_scenario_tops = base_body['scenario_tops']

    shops_shortcuts = shops_list[:3]
    req_body = {
        **base_body,
        'scenario_tops': base_scenario_tops + [
            {'scenario': 'eats_place', 'shortcuts': shops_shortcuts},
        ],
    }

    response = await taxi_blender.post(
        'blender/v1/shops-screen-grid', json=req_body, headers=HEADERS,
    )

    assert response.status_code == 200
    resp_body = response.json()

    assert resp_body['grid']['blocks'] == []
    assert resp_body['grid']['cells'] == []
