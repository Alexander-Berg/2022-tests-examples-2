import pytest


@pytest.mark.now('2020-06-21T15:00:00')
@pytest.mark.parametrize(
    ['use_arc'],
    [
        pytest.param(True, marks=pytest.mark.features_on('use_arc')),
        pytest.param(False),
    ],
)
async def test_happy_path(
        cron_runner,
        testpoint,
        load_json,
        mockserver,
        mock_yasm,
        mock_juggler_api,
        pack_repo,
        copy_repo,
        use_arc,
):
    @mock_yasm('/srvambry/alerts/replace/background')
    def _yasm_replace_mock(request):
        assert request.json == load_json('expected_yasm_replace_hp.json')

        return {'response': {'result': {'operation_id': '666'}}}

    @mock_yasm('/srvambry/alerts/replace/status')
    def _yasm_status_mock(request):
        assert request.json == {'operation_id': '666'}

        return {
            'response': {'result': {'failed': False, 'status': 'finished'}},
        }

    @mock_juggler_api('/api/checks/checks', prefix=True)
    def _juggler_checks_mock(request):
        assert request.query['service_name'] == 'vhost-500'
        assert request.query['include_notifications'] == '1'
        assert request.query['do'] == '1'

        return {
            'taxi_lbs-cloud-proxy_stable': {
                'vhost-500': {'notifications': {'some': 'notification'}},
            },
        }

    @mockserver.json_handler(
        '/duty_abc/api/v4/duty/shifts/service', prefix=True,
    )
    def _duty_abc_mock(request):
        return {'results': []}

    @mockserver.json_handler('/duty/api/duty_group/group_id', prefix=True)
    def _duty_mock(request):
        return {
            'result': {
                'data': {
                    'currentEvent': {'user': 'some_user'},
                    'suggestedEvents': [],
                },
            },
        }

    @testpoint('repo_tarball_path')
    def _tp_repo_tarball_path(data):
        repo_tarball = pack_repo('infra-cfg-yasm_simple')

        return {'infra-cfg-yasm.tar.gz': str(repo_tarball)}

    @testpoint('git_clone')
    def _tp_git_clone(data):
        assert data['url'] == 'arc_oauth:privet'
        copy_repo('infra-cfg-yasm_simple', data['repo_path'])

        return True

    await cron_runner.yasm_alert_generator()

    assert _yasm_replace_mock.times_called == 1
    assert _yasm_status_mock.times_called == 1
    assert _juggler_checks_mock.times_called == 1
    assert _duty_abc_mock.times_called == 0
    assert _duty_mock.times_called == 1
    assert _tp_repo_tarball_path.times_called == int(use_arc)
    assert _tp_git_clone.times_called == int(not use_arc)
