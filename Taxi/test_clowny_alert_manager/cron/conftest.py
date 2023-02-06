import collections
import os.path
import pathlib

import pytest
import yaml

from taxi.clients import juggler_api


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'check_broken: [clowny-alert-manager] juggler_alert_generator'
        ' throws exception on loading check file',
    )
    config.addinivalue_line(
        'markers',
        'telegram_opt_broken: [clowny-alert-manager] juggler_alert_generator'
        ' throws exception on loading telegram_options file',
    )
    config.addinivalue_line(
        'markers',
        'template_broken: [clowny-alert-manager] juggler_alert_generator'
        ' throws exception on loading template file',
    )
    config.addinivalue_line(
        'markers',
        'get_alerts: [clowny-alert-manager] solomon_alert_generator'
        ' gets solomon alerts from solomon_client_mock_400',
    )
    config.addinivalue_line('markers', 'with_l7_check')


JugglerApiMocks = collections.namedtuple(
    'JugglerApiMocks',
    [
        'get_checks',
        'checks_add_or_update',
        'checks_remove',
        'set_downtimes',
        'system_config_tree',
    ],
)


@pytest.fixture
def clown_branches(mock_clownductor):
    @mock_clownductor('/v1/branches/')
    def handler(request):
        direct_link = request.query.get('direct_link')
        if direct_link == 'taxi_clownductor_stable':
            return [
                {
                    'id': 1,
                    'service_id': 1,
                    'env': 'stable',
                    'direct_link': 'taxi_clownductor_stable',
                    'name': 'stable',
                },
            ]
        if direct_link == 'taxi_clownductor_pre_stable':
            return [
                {
                    'id': 10,
                    'service_id': 1,
                    'env': 'prestable',
                    'direct_link': 'taxi_clownductor_pre_stable',
                    'name': 'prestable',
                },
            ]
        if direct_link == 'some_host':
            return [
                {
                    'id': 2,
                    'env': 'stable',
                    'service_id': 2,
                    'direct_link': 'some_host',
                    'name': 'stable',
                },
            ]
        if direct_link == 'child_1':
            return [
                {
                    'id': 222,
                    'env': 'stable',
                    'service_id': 2,
                    'direct_link': 'child_1',
                    'name': 'stable',
                },
            ]
        if direct_link == 'taxi-clowny-balancer_stable':
            return [
                {
                    'id': 3,
                    'service_id': 5,
                    'direct_link': 'taxi-clowny-balancer_stable',
                    'env': 'stable',
                    'name': 'stable',
                },
            ]
        if direct_link == 'branch_to_direct_commit':
            return [
                {
                    'id': 100500,
                    'service_id': 100500,
                    'direct_link': 'branch_to_direct_commit',
                    'env': 'stable',
                    'name': 'branch_to_direct_commit',
                },
            ]
        return None

    return handler


@pytest.fixture
def clown_hosts(mock_clownductor):
    @mock_clownductor('/v1/hosts/')
    def handler(request):
        branch_id = request.query.get('branch_id')
        if branch_id == 222:
            return [
                {
                    'branch_id': 222,
                    'name': 'clown-stable-sas',
                    'datacenter': 'sas',
                },
                {
                    'branch_id': 222,
                    'name': 'clown-stable-vla',
                    'datacenter': 'vla',
                },
                {
                    'branch_id': 222,
                    'name': 'clown-stable-man',
                    'datacenter': 'man',
                },
            ]
        return None

    return handler


@pytest.fixture
def clown_parameters(mock_clownductor):
    @mock_clownductor('/v1/parameters/remote_values/')
    def handler(request):
        if request.query['service_id'] == '2':
            return {
                'subsystems': [
                    {
                        'subsystem_name': 'service_info',
                        'parameters': [
                            {'name': 'some', 'value': 'abc'},
                            {
                                'name': 'duty_group_id',
                                'value': 'some_duty_group_id',
                            },
                        ],
                    },
                ],
            }
        return {'subsystems': []}

    return handler


@pytest.fixture
def duty_api_mocks(mockserver):
    @mockserver.json_handler('/duty-api/api/duty_group', prefix=True)
    def handler(request):
        if request.query['group_id'] == 'some_duty_group_id':
            return {
                'result': {
                    'data': {
                        'staffGroups': [],
                        'suggestedEvents': [{'user': 'next-duty-user'}],
                        'currentEvent': {'user': 'current-duty-user'},
                    },
                    'ok': True,
                },
            }
        if request.query['group_id'] == 'other_duty':
            return {
                'result': {
                    'data': {
                        'staffGroups': [],
                        'suggestedEvents': [{'user': 'next-other_duty-devop'}],
                        'currentEvent': {'user': 'current-other_duty-devop'},
                    },
                    'ok': True,
                },
            }
        return {
            'result': {
                'data': {
                    'staffGroups': [],
                    'suggestedEvents': [],
                    'currentEvent': {
                        'user': f'duty-user-{request.query["group_id"]}',
                    },
                },
                'ok': True,
            },
        }

    return handler


def _check_limits(limit):
    for field in ['warn', 'crit']:
        _limit = limit[field]
        msg = f'bad limit {field}: {_limit!r}'
        assert isinstance(_limit, (int, str)), msg
        if isinstance(_limit, str):
            if _limit.isnumeric():
                assert int(_limit) >= 0, msg
            else:
                assert _limit.endswith('%'), msg
        else:
            assert _limit >= 0, msg
    for field in ['time_start', 'time_end']:
        _limit = limit[field]
        msg = f'bad limit {field}: {_limit!r}'
        assert isinstance(_limit, str), msg
        assert _limit.isnumeric(), msg
        assert 0 <= int(_limit) <= 24, msg
    for field in ['day_start', 'day_end']:
        _limit = limit[field]
        msg = f'bad limit {field}: {_limit!r}'
        assert isinstance(_limit, int), msg
        assert 1 <= _limit <= 7


@pytest.fixture
def juggler_api_mocks(
        patch_aiohttp_session,
        response_mock,
        load_json,
        mock_juggler_get_checks,
) -> JugglerApiMocks:
    @patch_aiohttp_session(
        juggler_api.JUGGLER_API_URL + '/api/checks/add_or_update', 'POST',
    )
    def checks_add_or_update(method, url, **kwargs):
        assert 'Authorization' in kwargs['headers']
        assert kwargs['params']['do'] == 1
        data = kwargs['json']
        if data['aggregator_kwargs']:
            for limit in data['aggregator_kwargs']['limits']:
                _check_limits(limit)
        if data.get('notifications'):
            for _notification in data['notifications']:
                assert _notification['template_name'] in {
                    'on_status_change',
                    'phone_escalation',
                    'solomon',
                    'startrek',
                }
                if _notification['template_name'] == 'on_status_change':
                    assert (
                        _notification['template_kwargs']['method']
                        == 'telegram'
                    )
                    assert _notification['template_kwargs'].keys() == {
                        'method',
                        'login',
                        'status',
                    }

        return response_mock(json={})

    @patch_aiohttp_session(
        juggler_api.JUGGLER_API_URL + '/api/checks/remove_check', 'POST',
    )
    def checks_remove(method, url, **kwargs):
        assert 'Authorization' in kwargs['headers']
        assert kwargs['params']['do'] == 1
        return response_mock(json={})

    get_checks = mock_juggler_get_checks(
        load_json('server_check.json'), ignore_filters=True,
    )

    @patch_aiohttp_session(
        juggler_api.JUGGLER_API_URL + '/v2/downtimes/set_downtimes', 'POST',
    )
    def set_downtimes(method, url, **kwargs):
        assert 'Authorization' in kwargs['headers']
        return response_mock(json={})

    @patch_aiohttp_session(
        juggler_api.JUGGLER_API_URL + '/api/system/config_tree', 'GET',
    )
    def system_config_tree(method, url, **kwargs):
        assert kwargs['params']['do'] == 1
        return response_mock(
            json={
                'jctl': {'new_check_downtime': 1200},
                'main': {
                    'default_check_ttl': 900,
                    'default_check_refresh_time': 90,
                },
            },
        )

    return JugglerApiMocks(
        get_checks,
        checks_add_or_update,
        checks_remove,
        set_downtimes,
        system_config_tree,
    )


@pytest.fixture
def juggler_alert_generator_mocks(
        request,
        monkeypatch,
        mockserver,
        patch,
        load_yaml,
        load_json,
        clownductor_mock,
):
    monkeypatch.setattr(
        'clowny_alert_manager.caches.infra_cfg_juggler.CONF_PATH_TO_CLONE',
        None,
    )

    @mockserver.json_handler('/duty-api/api/duty_group', prefix=True)
    def _duty_handler(req):
        assert 'Authorization' in req.headers
        duty_name = req.path.split('/')[-1]
        return {
            'result': {
                'data': {
                    'staffGroups': [],
                    'suggestedEvents': [],
                    'currentEvent': {'user': f'duty-user-{duty_name}'},
                },
                'ok': True,
            },
        }

    @mockserver.json_handler('/client-abc/v4/duty/shifts/')
    def _duty_abc_handler(req):
        assert 'Authorization' in req.headers
        duty_name = req.query['service']
        return {
            'results': [{'person': {'login': f'abc_duty_user_{duty_name}'}}],
        }

    repo_path = None

    @patch('git.Repo.clone_from')
    def _patch_git(repo, path):
        assert repo.find('bitbucket_oauth') != -1

        nonlocal repo_path
        repo_path = pathlib.Path(path)

        repo_path.mkdir(parents=True, exist_ok=True)
        templates_dir = repo_path / 'templates'
        templates_dir.mkdir()
        if not request.node.get_closest_marker('template_broken'):
            (templates_dir / 'some_service').write_text(
                yaml.dump(load_yaml('templates/some_service.yaml')),
            )
        (templates_dir / 'pkgver').write_text(
            yaml.dump(load_yaml('templates/pkgver.yaml')),
        )
        if not request.node.get_closest_marker('telegram_opt_broken'):
            (repo_path / 'telegram_options').write_text(
                yaml.dump(load_yaml('telegram.yaml')),
            )
        if request.node.get_closest_marker('with_l7_check'):
            (templates_dir / 'l7-monitorings').write_text(
                yaml.dump(load_yaml('templates/l7-monitorings.yaml')),
            )

    @patch('clowny_alert_manager.caches.infra_cfg_juggler._list_dir_dir_names')
    def _patch_list_dir_dir_names(path):
        return []

    check = 'check'
    balancer_check = 'balancer_check'

    @patch(
        'clowny_alert_manager.caches.infra_cfg_juggler._discover_checkfiles',
    )
    def _patch_list_dir_files(path, root_only):
        nonlocal repo_path

        if path == os.path.join(repo_path, 'checks/'):
            _checks = [os.path.join(path, check)]
            if request.node.get_closest_marker('with_l7_check'):
                _checks.append(os.path.join(path, balancer_check))
            return _checks
        return []

    @patch('clowny_alert_manager.internal.common.load_yaml')
    def _patch_load_yaml(path: str):
        filename = path.split('/')[-1]
        if filename == check:
            if request.node.get_closest_marker('check_broken'):
                raise yaml.YAMLError(f'Cannot read YAML {path}')
            return load_yaml('check.yaml')
        if filename == 'pkgver':
            if request.node.get_closest_marker('template_broken'):
                raise yaml.YAMLError(f'Cannot read YAML {path}')
            return load_yaml('templates/pkgver.yaml')
        if filename == balancer_check:
            return load_yaml('balancer_check.yaml')
        raise ValueError(f'Loading unexpected file {path}')


@pytest.fixture(autouse=True)
def _setup_repo(patch, pack_repo):
    repo_tarball = pack_repo('infra-cfg-juggler_empty')

    @patch('clowny_alert_manager.internal.utils.repo._get_tarball_path')
    async def _patch_get_tarball_path(_):
        return str(repo_tarball)
