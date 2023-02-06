import pytest


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_set_emergency_recipe_info_attrs(
        call_cube_handle, nanny_yp_mockserver, mockserver, load_json,
):
    nanny_yp_mockserver()
    one_recipe = load_json('info_one_recipe.json')
    two_recipes = load_json('info_two_recipes.json')

    @mockserver.json_handler(
        '/client-nanny/v2/services/taxi_kitty_unstable/info_attrs/',
    )
    async def _info_attrs_handler(request):
        if request.method == 'GET':
            return one_recipe
        data = request.json
        assert two_recipes['content'] == data['content']

    await call_cube_handle(
        'NannySetEmergencyRecipeInfoAttrs',
        {
            'content_expected': {'status': 'success'},
            'data_request': {
                'input_data': {'nanny_name': 'taxi_kitty_unstable'},
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )

    assert _info_attrs_handler.times_called == 2
