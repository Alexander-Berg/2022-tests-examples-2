# pylint: disable=redefined-outer-name
# pylint: disable=unused-variable

import pytest
import yaml

from clowny_alert_manager.crontasks import solomon_alert_generator
from clowny_alert_manager.generated.cron import run_cron


class SolomonApiCalls:
    def __init__(self, handler):
        self.solomon_handler = handler
        self.get_all_alerts_called = 0
        self.create_alert_called = 0
        self.get_alert_called = 0
        self.update_alert_called = 0
        self.delete_alert_called = 0


GROUP_NAME = 'group_name.yaml'
BROKEN_GROUP = 'broken_group.yaml'
INCOMPLETE_GROUP = 'incomplete_group.yaml'


@pytest.fixture
def solomon_alert_generator_mocks(patch, monkeypatch, load_yaml):
    monkeypatch.setattr(
        'clowny_alert_manager.crontasks.solomon_alert_generator.CLONE_DIR',
        None,
    )

    @patch('git.Repo.clone_from')
    def patch_git(repo, path):
        pass

    @patch('clowny_alert_manager.crontasks.solomon_alert_generator.walk_dir')
    def patch_os_walk(path):
        yield '', '', [GROUP_NAME]

    @patch('clowny_alert_manager.internal.common.load_yaml')
    def patch_get_yaml(path: str):
        filename = path.split('/')[-1]
        if filename == GROUP_NAME:
            return load_yaml('alert_group.yaml')
        if filename == BROKEN_GROUP:
            raise yaml.YAMLError(f'Cannot read YAML {path}')
        if filename == INCOMPLETE_GROUP:
            return load_yaml('alert_group_incomplete.yaml')
        if filename == 'solomon_alert_def.yaml':
            return {'type': 'object', 'additionalProperties': True}
        raise ValueError(f'Loading unexpected file {path}')


@pytest.fixture()
def solomon_client_mock(load_yaml, mock_solomon, mockserver):
    @mock_solomon('/api/v2/projects/taxi/alerts', prefix=True)
    def solomon_handler(req):
        nonlocal solomon_api_calls
        if req.path.endswith('/alerts'):
            if req.method == 'GET':
                solomon_api_calls.get_all_alerts_called += 1
                return load_yaml('alert_list.yaml')
            if req.method == 'POST':
                solomon_api_calls.create_alert_called += 1
                assert req.json['name'].find('new') != -1
                check_request_alert(req.json)
                return req.json
        else:
            alert_id = req.path.split('/')[-1]
            existing_alert = load_yaml('existing_alert.yaml')
            if req.method == 'GET':
                solomon_api_calls.get_alert_called += 1
                assert alert_id == existing_alert['id']
                return existing_alert
            if req.method == 'PUT':
                solomon_api_calls.update_alert_called += 1
                assert alert_id == req.json['id']
                check_request_alert(req.json)
                return req.json
            if req.method == 'DELETE':
                solomon_api_calls.delete_alert_called += 1
                assert alert_id != existing_alert['id']
                return mockserver.make_response(status=204)
        raise ValueError('Unexpected Solomon Api call')

    def check_request_alert(alert):
        if (
                alert['name'].find('service-one') != -1
                or alert['name'].find('new-service-two') != -1
        ):
            assert alert['groupByLabels'] == ['group']
        else:
            assert (
                alert['groupByLabels']
                == solomon_alert_generator.SOL_DEFAULT_GROUP_BY_LABELS
            )
        if (
                'juggler_service_and_host_from_annotations'
                in alert['notificationChannels']
        ):
            assert alert['annotations'].get('host')
        if alert['name'].find('new-service-with-no-metrics-policy') != -1:
            assert alert['resolvedEmptyPolicy'] == 'RESOLVED_EMPTY_MANUAL'
            assert alert['noPointsPolicy'] == 'NO_POINTS_MANUAL'

    solomon_api_calls = SolomonApiCalls(solomon_handler)

    return solomon_api_calls


@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_SOLOMON_GROUP_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
)
async def test_solomon_alert_generator(
        solomon_alert_generator_mocks, solomon_client_mock,
):
    await run_cron.main(
        ['clowny_alert_manager.crontasks.solomon_alert_generator', '-t', '0'],
    )

    assert solomon_client_mock.solomon_handler.times_called == 9
    assert solomon_client_mock.get_all_alerts_called == 1
    assert solomon_client_mock.create_alert_called == 5
    assert solomon_client_mock.get_alert_called == 1
    assert solomon_client_mock.update_alert_called == 1
    assert solomon_client_mock.delete_alert_called == 1


@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_SOLOMON_GROUP_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
)
async def test_solomon_alert_generator_group_broken(
        solomon_alert_generator_mocks, solomon_client_mock, patch,
):
    @patch('clowny_alert_manager.crontasks.solomon_alert_generator.walk_dir')
    def patch_os_walk(path):
        yield '', '', [BROKEN_GROUP]

    await run_cron.main(
        ['clowny_alert_manager.crontasks.solomon_alert_generator', '-t', '0'],
    )

    assert solomon_client_mock.delete_alert_called == 0


@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_SOLOMON_GROUP_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
)
async def test_solomon_alert_generator_group_incomplete(
        solomon_alert_generator_mocks, solomon_client_mock, patch,
):
    @patch('clowny_alert_manager.crontasks.solomon_alert_generator.walk_dir')
    def patch_os_walk(path):
        yield '', '', [INCOMPLETE_GROUP]

    await run_cron.main(
        ['clowny_alert_manager.crontasks.solomon_alert_generator', '-t', '0'],
    )

    assert solomon_client_mock.delete_alert_called == 0


@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_SOLOMON_GROUP_SETTINGS=[
        {'name': '__default__', 'dry_run': True},
    ],
)
async def test_solomon_alert_generator_dry_run(
        solomon_alert_generator_mocks, solomon_client_mock,
):
    await run_cron.main(
        ['clowny_alert_manager.crontasks.solomon_alert_generator', '-t', '0'],
    )

    assert solomon_client_mock.solomon_handler.times_called == 1
    assert solomon_client_mock.get_all_alerts_called == 1


@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_SOLOMON_GROUP_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
    CLOWNY_ALERT_MANAGER_SOLOMON_SETTINGS={
        'repo_url': '',
        'project': 'taxi',
        'autopurge': False,
    },
)
async def test_solomon_alert_generator_no_autopurge(
        solomon_alert_generator_mocks, solomon_client_mock,
):
    await run_cron.main(
        ['clowny_alert_manager.crontasks.solomon_alert_generator', '-t', '0'],
    )

    assert solomon_client_mock.solomon_handler.times_called == 8
    assert solomon_client_mock.get_all_alerts_called == 1
    assert solomon_client_mock.get_all_alerts_called == 1
    assert solomon_client_mock.create_alert_called == 5
    assert solomon_client_mock.get_alert_called == 1
    assert solomon_client_mock.update_alert_called == 1
    assert solomon_client_mock.delete_alert_called == 0


@pytest.fixture()
def solomon_client_mock_400(request, load_yaml, mock_solomon, mockserver):
    @mock_solomon('/api/v2/projects/taxi/alerts', prefix=True)
    def solomon_handler_400(req):
        nonlocal solomon_api_calls
        if req.path.endswith('/alerts'):
            if req.method == 'GET':
                solomon_api_calls.get_all_alerts_called += 1
                if request.node.get_closest_marker('get_alerts'):
                    return load_yaml('alert_list.yaml')
            if req.method == 'POST':
                solomon_api_calls.create_alert_called += 1
        else:
            if req.method == 'GET':
                solomon_api_calls.get_alert_called += 1
            if req.method == 'PUT':
                solomon_api_calls.update_alert_called += 1
            if req.method == 'DELETE':
                solomon_api_calls.delete_alert_called += 1
        return mockserver.make_response(status=400)

    solomon_api_calls = SolomonApiCalls(solomon_handler_400)

    return solomon_api_calls


@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_SOLOMON_GROUP_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
)
async def test_solomon_alert_generator_400(
        solomon_alert_generator_mocks, solomon_client_mock_400,
):
    await run_cron.main(
        ['clowny_alert_manager.crontasks.solomon_alert_generator', '-t', '0'],
    )

    assert solomon_client_mock_400.solomon_handler.times_called == 7
    assert solomon_client_mock_400.get_all_alerts_called == 1
    assert solomon_client_mock_400.create_alert_called == 6
    assert solomon_client_mock_400.get_alert_called == 0
    assert solomon_client_mock_400.update_alert_called == 0
    assert solomon_client_mock_400.delete_alert_called == 0


@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_SOLOMON_GROUP_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
)
@pytest.mark.get_alerts()
async def test_solomon_alert_generator_400_alerts(
        solomon_alert_generator_mocks, solomon_client_mock_400,
):
    await run_cron.main(
        ['clowny_alert_manager.crontasks.solomon_alert_generator', '-t', '0'],
    )

    assert solomon_client_mock_400.solomon_handler.times_called == 9
    assert solomon_client_mock_400.get_all_alerts_called == 1
    assert solomon_client_mock_400.create_alert_called == 5
    assert solomon_client_mock_400.get_alert_called == 1
    assert solomon_client_mock_400.update_alert_called == 1
    assert solomon_client_mock_400.delete_alert_called == 1


@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_SOLOMON_GROUP_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
)
@pytest.mark.features_on('use_arc')
async def test_solomon_alert_generator_repo_from_tarball(
        solomon_client_mock, load, testpoint, pack_repo, cron_runner,
):
    repo_tarball = pack_repo('infra-cfg-juggler')

    @testpoint('repo_tarball_path')
    def _tp_repo_tarball_path(data):
        return {'infra-cfg-juggler.tar.gz': str(repo_tarball)}

    await cron_runner.solomon_alert_generator()

    assert solomon_client_mock.solomon_handler.times_called == 8
    assert solomon_client_mock.get_all_alerts_called == 1
    assert solomon_client_mock.create_alert_called == 4
    assert solomon_client_mock.get_alert_called == 1
    assert solomon_client_mock.update_alert_called == 1
    assert solomon_client_mock.delete_alert_called == 1
