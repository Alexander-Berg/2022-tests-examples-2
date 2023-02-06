import pytest

from clowny_alert_manager.generated.cron import run_cron

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.features_on('enable_clownductor_cache', 'use_arc'),
]


@pytest.fixture(name='get_updated_check')
def get_updated_check_fixture(juggler_api_mocks):
    def _impl(juggler_host: str, juggler_service: str):
        for call in juggler_api_mocks.checks_add_or_update.calls:
            request = call['kwargs']['json']
            if (
                    request['host'] == juggler_host
                    and request['service'] == juggler_service
            ):
                return request

        return None

    return _impl


async def test_hejmdal_aggregation_type(
        taxi_clowny_alert_manager_web,
        patch,
        juggler_api_mocks,
        clown_parameters,
        clown_branches,
        duty_api_mocks,
        pack_repo,
        get_updated_check,
):
    repo_tarball = pack_repo('infra-cfg-juggler')

    # use patch instead of testpoint('repo_tarball_path') as cron is run
    # manually, not with testsuite
    @patch('clowny_alert_manager.internal.utils.repo._get_tarball_path')
    async def _patch_get_tarball_path(_):
        return str(repo_tarball)

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    assert get_updated_check('some_host', 'hjmdl-aggr')['children'] == [
        {
            'type': 'HOST',
            'host': 'some_host_host',
            'service': 'hjmdl-aggr',
            'instance': '',
        },
    ]


@pytest.mark.parametrize(
    [
        'cb_service_resp',
        'cb_service_not_found',
        'get_checks_resp',
        'expect_children_built',
        'exp_cb_namespace_tc',
    ],
    [
        pytest.param(
            'service_get_resp_simple.json',
            False,
            'get_checks_resp_simple.json',
            True,
            1,
            id='happy path',
        ),
        pytest.param(
            'service_get_resp_empty.json',
            False,
            'get_checks_resp_simple.json',
            False,
            0,
            id='clowny-balancer returned empty namespace list',
        ),
        pytest.param(
            None,
            True,
            'get_checks_resp_simple.json',
            False,
            0,
            id='clowny-balancer /balancers/v1/service/get returned 404',
        ),
        pytest.param(
            'service_get_resp_wrong_env.json',
            False,
            'get_checks_resp_simple.json',
            False,
            0,
            id='service has only testing namespaces',
        ),
        pytest.param(
            'service_get_resp_simple.json',
            False,
            'get_checks_resp_wrong_service.json',
            False,
            1,
            id=(
                'awacs hasn\'t created aggregates for juggler_service '
                'stated in checkfile'
            ),
        ),
    ],
)
async def test_l7_balancer_type(
        mockserver,
        juggler_api_mocks,
        load_json,
        patch,
        pack_repo,
        duty_api_mocks,
        clownductor_mock,
        get_updated_check,
        mock_clowny_balancer,
        mock_juggler_get_checks,
        cb_service_resp,
        cb_service_not_found,
        get_checks_resp,
        expect_children_built,
        exp_cb_namespace_tc,
):
    repo_tarball = pack_repo('infra-cfg-juggler_l7_balancer')

    @patch('clowny_alert_manager.internal.utils.repo._get_tarball_path')
    async def _patch_get_tarball_path(_):
        return str(repo_tarball)

    @mock_clowny_balancer('/balancers/v1/service/get/')
    def _mock_cb_service(request):
        assert request.query['service_id'] == '1'

        if cb_service_not_found:
            return mockserver.make_response(
                status=404, json={'code': 'code', 'message': 'message'},
            )

        return load_json(cb_service_resp)

    @mock_clowny_balancer('/v1/namespaces/item/')
    def _mock_cb_namespace(request):
        assert request.query['id'] == '228'

        return {'alerting_config': {'juggler_namespace': 'a-b-c'}}

    _mock_get_checks = mock_juggler_get_checks(load_json(get_checks_resp))

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    check = get_updated_check('some_host', 'l7_balancer_cpu_usage')

    if expect_children_built:
        assert check['children'] == [
            {
                'host': 'awacs.a-b-c.man',
                'instance': '',
                'service': 'cpu_usage',
                'type': 'HOST',
            },
            {
                'host': 'awacs.a-b-c.sas',
                'instance': '',
                'service': 'cpu_usage',
                'type': 'HOST',
            },
        ]
    else:
        assert check is None

    assert _mock_cb_service.times_called == 1
    assert _mock_cb_namespace.times_called == exp_cb_namespace_tc
    assert (
        len(_mock_get_checks.calls) == exp_cb_namespace_tc + 1
    )  # +1 is for getting all juggler project checks by tag


async def test_postgres_type(
        patch, pack_repo, duty_api_mocks, get_updated_check,
):
    repo_tarball = pack_repo('infra-cfg-juggler_postgres')

    @patch('clowny_alert_manager.internal.utils.repo._get_tarball_path')
    async def _patch_get_tarball_path(_):
        return str(repo_tarball)

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    check = get_updated_check(
        'pg_taxi-infra_clownductor_stable', 'hejmdal-pg-cpu-usage',
    )

    assert check['children'] == [
        {
            'host': 'db_child_1',
            'instance': '',
            'service': 'hejmdal-pg-cpu-usage',
            'type': 'CGROUP',
        },
        {
            'host': 'db_some_host',
            'instance': '',
            'service': 'hejmdal-pg-cpu-usage',
            'type': 'CGROUP',
        },
    ]
