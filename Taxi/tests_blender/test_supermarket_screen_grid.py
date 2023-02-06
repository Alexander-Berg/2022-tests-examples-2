import copy

import pytest

from tests_blender import shortcuts_grid_helpers as helpers


def cleanup_response_body(response_body):
    body = copy.deepcopy(response_body)
    grid = body['grid']
    grid.pop('id')
    for block in grid['blocks']:
        block.pop('id')

    return body


@pytest.mark.experiments3(
    filename='experiments3_supermarket_screen_market_categories_grid_rules.json',  # noqa: E501 pylint: disable=line-too-long
)
@pytest.mark.experiments3(
    filename='experiments3_supermarket_screen_shops_grid_rules.json',
)
async def test_baseline_shortcuts_grid(taxi_blender, load_json):
    req_body = load_json('simple_supermarket_request.json')
    resp_body = load_json('simple_supermarket_response.json')
    response = await taxi_blender.post(
        'blender/v1/supermarket-screen-grid',
        json=req_body,
        headers=helpers.MEANINGLESS_HEADERS,
    )

    assert response.status_code == 200
    assert cleanup_response_body(response.json()) == cleanup_response_body(
        resp_body,
    )


@pytest.mark.experiments3(
    filename='experiments3_supermarket_screen_market_categories_grid_rules.json',  # noqa: E501 pylint: disable=line-too-long
)
@pytest.mark.experiments3(
    filename='experiments3_supermarket_screen_shops_grid_rules.json',
)
async def test_shortcuts_grid_buildable_shortcuts(
        taxi_blender, load_json, mockserver,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        resp = load_json('promotions_response.json')
        resp['deeplink_shortcuts'][0]['options'][
            'meta_type'
        ] = 'market_category'
        resp['stories'][0]['options']['meta_type'] = 'market_category'
        return resp

    req_body = load_json('simple_supermarket_request.json')
    req_body['scenario_tops'] = [
        {
            'scenario': 'market_category',
            'shortcuts': [],
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
    ]
    response = await taxi_blender.post(
        'blender/v1/supermarket-screen-grid',
        json=req_body,
        headers=helpers.MEANINGLESS_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['grid']['blocks']
