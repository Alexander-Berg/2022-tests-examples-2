import pytest


@pytest.mark.parametrize(
    'file_name',
    [
        pytest.param(
            'NannyCubeRemovePodsFromDeploy',
            id='test_cube_request_data_with_regular_flow',
        ),
    ],
)
async def test_nanny_cube_remove_pods_from_deploy(
        load_json,
        call_cube_handle,
        mockserver,
        file_name,
        nanny_yp_mockserver,
):
    json_data = load_json(f'{file_name}.json')

    nanny_yp_mockserver()

    @mockserver.json_handler(
        'client-nanny/v2/services/taxi_kitty_unstable/runtime_attrs/',
    )
    def handler(request):
        if request.method == 'GET':
            return load_json('nanny_service_runtime_attrs.json')

        if request.method == 'PUT':
            data = request.json
            expected = load_json('nanny_service_runtime_attrs_expected.json')
            assert expected['content'] == data['content']
            return expected
        return None

    cube_name = 'NannyCubeRemovePodsFromDeploy'
    await call_cube_handle(cube_name, json_data)
    assert handler.times_called == 2
