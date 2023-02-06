import pytest

from tests_blender import shortcuts_grid_helpers as helpers


def cleanup_response_body(body):
    grid = body['grid']
    grid.pop('id')
    for block in grid['blocks']:
        block.pop('id')

    return body


@pytest.mark.experiments3(filename='exp3_scooters_screen_grid_rules.json')
async def test_empty_shortcuts_grid(taxi_blender, load_json):
    req_body = load_json('simple_scooters_request.json')
    req_body['scenario_tops'] = []
    response = await taxi_blender.post(
        'blender/v1/scooters-screen-grid',
        json=req_body,
        headers=helpers.MEANINGLESS_HEADERS,
    )

    assert response.status_code == 200
    assert cleanup_response_body(response.json())['grid'] == {
        'blocks': [],
        'cells': [],
        'width': 6,
    }


@pytest.mark.parametrize(
    'enable_showcases, response_file',
    [
        pytest.param(False, 'scooters_response_showcases_disabled.json'),
        pytest.param(True, 'scooters_response_showcases_enabled.json'),
    ],
)
async def test_scooters_shortcuts_grid_simple(
        taxi_blender, load_json, experiments3, enable_showcases, response_file,
):
    exp3_json = load_json('exp3_scooters_screen_grid_rules.json')
    exp3_json['experiments'][0]['clauses'][0]['value'].update(
        {'enable_showcases': enable_showcases},
    )
    experiments3.add_experiments_json(exp3_json)

    req_body = load_json('simple_scooters_request.json')
    resp_body = load_json(response_file)
    response = await taxi_blender.post(
        'blender/v1/scooters-screen-grid',
        json=req_body,
        headers=helpers.MEANINGLESS_HEADERS,
    )

    assert response.status_code == 200
    assert cleanup_response_body(response.json()) == cleanup_response_body(
        resp_body,
    )


async def test_scooters_shortcuts_grid_buildable_shortcuts(
        taxi_blender, load_json, mockserver, experiments3,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        resp = load_json('promotions_response.json')
        resp['deeplink_shortcuts'][0]['options']['meta_type'] = 'support'
        return resp

    exp3_json = load_json('exp3_scooters_screen_grid_rules.json')
    exp3_json['experiments'][0]['clauses'][0]['value'].update(
        {'enable_showcases': False},
    )
    experiments3.add_experiments_json(exp3_json)

    req_body = load_json('request_to_build_shortcuts.json')
    response = await taxi_blender.post(
        'blender/v1/scooters-screen-grid',
        json=req_body,
        headers=helpers.MEANINGLESS_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['grid']['blocks']
