import pytest


@pytest.mark.parametrize(
    'file_name',
    [
        pytest.param('datacenters_diff'),
        pytest.param('full_downgrade'),
        pytest.param('resize_reallocate'),
        pytest.param('reallocate_resize'),
        pytest.param('reallocate_only'),
        pytest.param('resize_only'),
        # сравнение не должно задеть persistent_volumes
        pytest.param('change_persistent_only'),
    ],
)
async def test_flow_change_resources(call_cube_handle, load_json, file_name):

    await call_cube_handle(
        'MakeFlowChangeServiceResources', load_json(f'{file_name}.json'),
    )
