import pytest


DISABLE_NANNY_SNAPSHOT_ACTIVATE = {
    '__default__': {},
    'test_project': {
        'test_service': {'disable_nanny_snapshot_activate': True},
        '__default__': {},
    },
}


@pytest.mark.parametrize(
    'data, expected_info_attrs_times_called, expected_events_times_called',
    [
        pytest.param(
            {
                'name': 'taxi_kitty_unstable',
                'snapshot_id': '5c26609053b7c34a9ad5a283f48ae03c79853d58',
                'comment': 'goodies and bugfixes',
            },
            1,
            1,
            id='happy path',
        ),
        pytest.param(
            {
                'name': 'taxi_kitty_unstable',
                'snapshot_id': '5c26609053b7c34a9ad5a283f48ae03c79853d58',
                'comment': 'goodies and bugfixes',
                'emergency_deploy': True,
            },
            1,
            1,
            id='emergency_deploy',
        ),
        pytest.param(
            {
                'name': 'taxi_kitty_unstable',
                'snapshot_id': '5c26609053b7c34a9ad5a283f48ae03c79853d58',
                'comment': 'goodies and bugfixes',
                'project_name': 'test_project',
                'service_name': 'test_service',
            },
            1,
            1,
            id=(
                'service_name/project_name present, '
                'disable_nanny_snaphot_activate=false, '
                'set_target_state triggered'
            ),
        ),
        pytest.param(
            {
                'name': 'taxi_kitty_unstable',
                'snapshot_id': '5c26609053b7c34a9ad5a283f48ae03c79853d58',
                'comment': 'goodies and bugfixes',
            },
            1,
            1,
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES_PER_SERVICE=(
                    DISABLE_NANNY_SNAPSHOT_ACTIVATE
                ),
            ),
            id=(
                'service_name/project_name absent, '
                'disable_nanny_snaphot_activate=true, '
                'set_target_state triggered'
            ),
        ),
        pytest.param(
            {
                'name': 'taxi_kitty_unstable',
                'snapshot_id': '5c26609053b7c34a9ad5a283f48ae03c79853d58',
                'comment': 'goodies and bugfixes',
                'project_name': 'test_project',
                'service_name': 'test_service',
            },
            0,
            0,
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES_PER_SERVICE=(
                    DISABLE_NANNY_SNAPSHOT_ACTIVATE
                ),
            ),
            id=(
                'service_name/project_name present, '
                'disable_nanny_snaphot_activate=true, '
                'cube exits without performing any actions'
            ),
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_nanny_cube_deploy_snapshot(
        call_cube_handle,
        nanny_yp_mockserver,
        mockserver,
        load_json,
        data,
        expected_info_attrs_times_called,
        expected_events_times_called,
):
    nanny_yp_mockserver()
    one_recipe = load_json('info_one_recipe.json')

    @mockserver.json_handler(
        '/client-nanny/v2/services/taxi_kitty_unstable/info_attrs/',
    )
    async def _info_attrs_handler(request):
        if request.method == 'GET':
            return one_recipe

    @mockserver.json_handler(
        '/client-nanny/v2/services/taxi_kitty_unstable/events/',
    )
    async def _events_handler(request):
        request_data = request.json
        emergency = data.get('emergency_deploy', False)
        recipe = 'custom_dangerous_degrade_level' if emergency else 'default'
        assert recipe == request_data['content']['recipe']
        assert recipe == request_data['content']['prepare_recipe']

    await call_cube_handle(
        'NannyCubeDeploySnapshot',
        {
            'content_expected': {'status': 'success'},
            'data_request': {
                'input_data': data,
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )

    assert _info_attrs_handler.times_called == expected_info_attrs_times_called
    assert _events_handler.times_called == expected_events_times_called
