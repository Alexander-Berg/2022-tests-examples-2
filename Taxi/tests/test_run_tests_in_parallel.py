import asyncio
import collections
import dataclasses
import pathlib
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence

import git
import pytest
import yaml

import run_tests_in_parallel
from taxi_buildagent import dockertest
from taxi_buildagent import utils
from tests.utils import pytest_wraps
from tests.utils.examples import backend_py3
from tests.utils.examples import uservices

FLAP_TESTS_FILENAME = pathlib.Path('flap_tests_list')
TEST_REPORTS_DIR = pathlib.Path('test-results')
CORES_DIR = pathlib.Path('cores')


@dataclasses.dataclass
class Params(pytest_wraps.Params):
    services: List[str]
    expected_services: List[str]
    init_repo: Callable[..., git.Repo]
    tier0_services: Sequence[str] = ()
    yt_services: Sequence[str] = ()
    dc_service: str = 'taxi-test-service'
    max_workers: int = 2
    exit_codes: Dict[str, int] = dataclasses.field(default_factory=dict)
    test_targets: Optional[List[str]] = None
    base_image: str = 'default-image'
    expected_base_image: Dict[str, str] = dataclasses.field(
        default_factory=dict,
    )
    expected_retries_by_services: collections.Counter = dataclasses.field(
        default_factory=collections.Counter,
    )
    mds_response: List[str] = dataclasses.field(default_factory=list)
    is_mds_request_broken: bool = False
    tc_report_test_problem_calls: List[Dict[str, str]] = dataclasses.field(
        default_factory=list,
    )
    report_changed_dirs: Optional[bool] = None
    bad_environment: bool = False
    core_files: List[str] = dataclasses.field(default_factory=list)
    stderr: Sequence[str] = ()
    max_failed_services: Optional[int] = None
    tc_report_problem: List[Dict[str, Any]] = dataclasses.field(
        default_factory=list,
    )
    command_timeout_exceeded: bool = False


PARAMS = [
    Params(
        pytest_id='uservices_simple_test',
        services=[
            'driver-authorizer',
            'driver-authorizer2',
            'driver-authorizer3',
            'pilorama',
        ],
        expected_services=[
            'driver-authorizer',
            'driver-authorizer2',
            'driver-authorizer3',
            'pilorama',
        ],
        init_repo=uservices.init,
        expected_base_image={
            'driver-authorizer': 'default-image',
            'driver-authorizer2': 'default-image',
            'driver-authorizer3': 'default-image',
            'pilorama': 'default-image',
        },
    ),
    Params(
        pytest_id='uservices_test_with_tier0_service',
        services=[
            'driver-authorizer',
            'driver-authorizer2',
            'driver-authorizer3',
            'pilorama',
        ],
        tier0_services=['driver-authorizer'],
        expected_services=[
            'driver-authorizer2',
            'driver-authorizer3',
            'pilorama',
        ],
        init_repo=uservices.init,
        expected_base_image={
            'driver-authorizer2': 'default-image',
            'driver-authorizer3': 'default-image',
            'pilorama': 'default-image',
        },
    ),
    Params(
        pytest_id='uservices_test_with_yt_services_mixed',
        services=['yt-service1', 'yt-service2', 'example-service'],
        yt_services=['yt-service1', 'yt-service2'],
        expected_services=['yt-service1', 'yt-service2', 'example-service'],
        init_repo=uservices.init,
        expected_base_image={
            'yt-service1': 'default-image',
            'yt-service2': 'default-image',
            'example-service': 'default-image',
        },
    ),
    Params(
        pytest_id='backend_py3_simple_test',
        services=['taxi-adjust', 'taxi-fleet'],
        expected_services=['taxi-adjust', 'taxi-fleet'],
        init_repo=backend_py3.init,
        expected_base_image={
            'taxi-adjust': 'some-image',  # from deps-py3
            'taxi-fleet': 'default-image',
        },
    ),
    Params(
        pytest_id='one_worker_many_services',
        services=[
            'driver-authorizer',
            'driver-authorizer2',
            'driver-authorizer3',
            'pilorama',
        ],
        expected_services=[
            'driver-authorizer',
            'driver-authorizer2',
            'driver-authorizer3',
            'pilorama',
        ],
        max_workers=1,
        init_repo=uservices.init,
        expected_base_image={
            'driver-authorizer': 'default-image',
            'driver-authorizer2': 'default-image',
            'driver-authorizer3': 'default-image',
            'pilorama': 'default-image',
        },
    ),
    Params(
        pytest_id='many_workers_one_service',
        services=['pilorama'],
        expected_services=['pilorama'],
        init_repo=uservices.init,
        max_workers=12,
        expected_base_image={'pilorama': 'default-image'},
    ),
    Params(
        pytest_id='one_failed',
        services=[
            'driver-authorizer',
            'driver-authorizer2',
            'driver-authorizer3',
        ],
        expected_services=[
            'driver-authorizer',
            'driver-authorizer2',
            'driver-authorizer3',
        ],
        init_repo=uservices.init,
        exit_codes={'driver-authorizer2': 8},
        expected_base_image={
            'driver-authorizer': 'default-image',
            'driver-authorizer2': 'default-image',
            'driver-authorizer3': 'default-image',
        },
        stderr=('Tests of `driver-authorizer2` finished with exit code 8',),
    ),
    Params(
        pytest_id='all_failed',
        services=[
            'driver-authorizer',
            'driver-authorizer2',
            'driver-authorizer3',
        ],
        expected_services=[
            'driver-authorizer',
            'driver-authorizer2',
            'driver-authorizer3',
        ],
        init_repo=uservices.init,
        exit_codes={
            'driver-authorizer': 8,
            'driver-authorizer2': 8,
            'driver-authorizer3': 8,
        },
        expected_base_image={
            'driver-authorizer': 'default-image',
            'driver-authorizer2': 'default-image',
            'driver-authorizer3': 'default-image',
        },
        stderr=(
            'Tests of `driver-authorizer` finished with exit code 8',
            'Tests of `driver-authorizer2` finished with exit code 8',
            'Tests of `driver-authorizer3` finished with exit code 8',
        ),
    ),
    Params(
        pytest_id='with_project_sources',
        services=[
            'driver-authorizer',
            'driver-authorizer2',
            'driver-authorizer3',
        ],
        expected_services=[
            'driver-authorizer',
            'driver-authorizer2',
            'driver-authorizer3',
            'some-sources',
        ],
        init_repo=uservices.init,
        test_targets=['some-sources'],
        expected_base_image={
            'driver-authorizer': 'default-image',
            'driver-authorizer2': 'default-image',
            'driver-authorizer3': 'default-image',
            'some-sources': 'default-image',
        },
    ),
    Params(
        pytest_id='without_services_param',
        services=[],
        expected_services=[
            'driver-authorizer',
            'driver-authorizer2',
            'driver-authorizer3',
            'uservice-template',
            'pilorama',
            'some-sources',
        ],
        init_repo=uservices.init,
        test_targets=['some-sources'],
        expected_base_image={
            'driver-authorizer': 'default-image',
            'driver-authorizer2': 'default-image',
            'driver-authorizer3': 'default-image',
            'uservice-template': 'default-image',
            'pilorama': 'default-image',
            'some-sources': 'default-image',
        },
    ),
    Params(
        pytest_id='with_base_image',
        services=[
            'driver-authorizer',
            'driver-authorizer2',
            'driver-authorizer3',
            'pilorama',
        ],
        expected_services=[
            'driver-authorizer',
            'driver-authorizer2',
            'driver-authorizer3',
            'pilorama',
        ],
        init_repo=uservices.init,
        base_image='some-base-image',
        expected_base_image={
            'driver-authorizer': 'some-base-image',
            'driver-authorizer2': 'some-base-image',
            'driver-authorizer3': 'some-base-image',
            'pilorama': 'some-base-image',
        },
    ),
    Params(
        pytest_id='backend_py3_with_base_image',
        services=['taxi-adjust', 'taxi-fleet'],
        expected_services=['taxi-adjust', 'taxi-fleet'],
        init_repo=backend_py3.init,
        base_image='some-base-image',
        expected_base_image={
            'taxi-adjust': 'some-image',  # from deps-py3
            'taxi-fleet': 'some-base-image',
        },
    ),
    Params(
        pytest_id='backend_py3_with_retries',
        services=['taxi-fleet'],
        expected_services=['taxi-fleet'],
        init_repo=backend_py3.init,
        expected_base_image={'taxi-fleet': 'default-image'},
        expected_retries_by_services=collections.Counter({'taxi-fleet': 1}),
    ),
    Params(
        pytest_id='broken_mds3',
        services=['driver-authorizer'],
        expected_services=['driver-authorizer'],
        init_repo=uservices.init,
        expected_base_image={'driver-authorizer': 'default-image'},
        is_mds_request_broken=True,
    ),
    Params(
        pytest_id='flap_tests_mds3',
        services=['driver-authorizer'],
        expected_services=['driver-authorizer'],
        init_repo=uservices.init,
        expected_base_image={'driver-authorizer': 'default-image'},
        mds_response=[
            'test1',
            'test2',
            'service1.test3',
            'service2.test4',
            'service3.tests.test4',
            'service4.tests.test_folder.test5',
            'services.some.testsuite.tests_some.test_some.test_some',
        ],
    ),
    Params(
        pytest_id='bad_docker',
        services=['driver-authorizer', 'driver-authorizer2'],
        expected_services=['driver-authorizer', 'driver-authorizer2'],
        init_repo=uservices.init,
        exit_codes={'driver-authorizer2': 2},
        expected_base_image={
            'driver-authorizer': 'default-image',
            'driver-authorizer2': 'default-image',
        },
        tc_report_test_problem_calls=[
            {
                'problem_message': (
                    'Captured stderr:\n'
                    'Something with docker went wrong...\n'
                    'Oh, sh*t!\n\n'
                ),
                'test_name': 'dockertest errors: driver-authorizer2',
            },
        ],
        stderr=('Tests of `driver-authorizer2` finished with exit code 2',),
    ),
    Params(
        pytest_id='backend_py3_report_changed_dirs',
        services=['services/taxi-fleet', 'libraries/client-solomon'],
        expected_services=['services/taxi-fleet', 'libraries/client-solomon'],
        init_repo=backend_py3.init,
        base_image='some-base-image',
        expected_base_image={
            'services/taxi-fleet': 'some-base-image',
            'libraries/client-solomon': 'some-base-image',
        },
        report_changed_dirs=True,
    ),
    Params(
        pytest_id='backend_py3_report_changed_dirs',
        services=[],
        expected_services=[
            'services/taxi-adjust',
            'services/taxi-corp',
            'services/taxi-corp-data',
            'services/taxi-fleet',
            'services/taximeter',
            'services/example-service',
        ],
        init_repo=backend_py3.init,
        base_image='some-base-image',
        expected_base_image={
            'services/taxi-adjust': 'some-image',
            'services/taxi-corp': 'some-base-image',
            'services/taxi-corp-data': 'some-base-image',
            'services/taxi-fleet': 'some-base-image',
            'services/taximeter': 'some-base-image',
            'services/example-service': 'some-base-image',
        },
        report_changed_dirs=True,
    ),
    Params(
        pytest_id='bad_environment',
        max_workers=1,
        services=['driver-authorizer', 'driver-authorizer2'],
        expected_services=['driver-authorizer', 'driver-authorizer2'],
        init_repo=uservices.init,
        exit_codes={'driver-authorizer': 15},
        expected_base_image={
            'driver-authorizer': 'default-image',
            'driver-authorizer2': 'default-image',
        },
        tc_report_test_problem_calls=[
            {
                'problem_message': (
                    'Captured stderr:\nSome logs of environment\n'
                ),
                'test_name': 'dockertest errors: driver-authorizer',
            },
        ],
        bad_environment=True,
        stderr=('Tests of `driver-authorizer` finished with exit code 15',),
    ),
    Params(
        pytest_id='uservices_many_cores',
        services=['driver-authorizer'],
        expected_services=['driver-authorizer'],
        init_repo=uservices.init,
        expected_base_image={'driver-authorizer': 'default-image'},
        core_files=[f'core-main-wokrer-{i}-backtrace.txt' for i in range(30)],
    ),
    Params(
        pytest_id='cancel_tests',
        services=[
            'services/example-service',
            'services/example-service2',
            'services/example-service3',
            'services/taxi-adjust',
            'services/taxi-corp',
        ],
        max_failed_services=2,
        expected_services=[
            'services/example-service',
            'services/example-service2',
            'services/example-service3',
        ],
        init_repo=backend_py3.init,
        exit_codes={
            'services/example-service': 2,
            'services/example-service2': 2,
            'services/example-service3': 2,
        },
        expected_base_image={
            'services/example-service': 'default-image',
            'services/example-service2': 'default-image',
            'services/example-service3': 'default-image',
        },
        stderr=(
            'Tests of `services/example-service` finished with exit code 2',
            'Tests of `services/example-service2` finished with exit code 2',
            'Tests of `services/example-service3` finished with exit code 2',
        ),
        report_changed_dirs=True,
        tc_report_problem=[
            {
                'description': (
                    'Tests for at least 2 services failed. Abort testing'
                ),
                'identity': None,
            },
        ],
    ),
    Params(
        pytest_id='backend_py3_break_timeout',
        services=['taxi-adjust', 'taxi-fleet'],
        expected_services=[],
        init_repo=backend_py3.init,
        command_timeout_exceeded=True,
        exit_codes={'services/taxi-adjust': 1, 'services/taxi-fleet': 1},
        stderr=(
            'Tests for service "taxi-adjust" exceeded timeout',
            'Tests of `taxi-adjust` finished with exit code 1',
            'Tests for service "taxi-fleet" exceeded timeout',
            'Tests of `taxi-fleet` finished with exit code 1',
        ),
        tc_report_problem=[
            {
                'description': (
                    'Tests for service "taxi-adjust" exceeded timeout'
                ),
                'identity': 'execution-timeout-taxi-adjust',
            },
            {
                'description': (
                    'Tests for service "taxi-fleet" exceeded timeout'
                ),
                'identity': 'execution-timeout-taxi-fleet',
            },
        ],
        tc_report_test_problem_calls=[
            {
                'problem_message': 'Captured stderr:\n',
                'test_name': 'dockertest errors: taxi-adjust',
            },
            {
                'problem_message': 'Captured stderr:\n',
                'test_name': 'dockertest errors: taxi-fleet',
            },
        ],
    ),
]


@pytest_wraps.parametrize(PARAMS)
def test_run_tests_in_parallel(
        monkeypatch,
        commands_mock,
        tmpdir,
        patch_requests,
        params: Params,
        teamcity_report_test_problem,
        teamcity_report_problems,
):
    repo = params.init_repo(tmpdir)

    for tier0_service in params.tier0_services:
        pathlib.Path(
            repo.working_tree_dir, 'services', tier0_service, 'service.yaml',
        ).write_text('ya-make: {enabled: true}')

    for i, yt_service in enumerate(params.yt_services):
        service_path = pathlib.Path(
            repo.working_tree_dir, 'services', yt_service,
        )
        service_path.mkdir(exist_ok=True)
        if i % 2 == 0:
            (service_path / 'service.yaml').write_text(
                'units: [{name: web, yt_wrapper: stuff}]',
            )
        else:
            (service_path / 'local-files-dependencies.txt').write_text(
                'libraries/ydblib',
            )

    monkeypatch.chdir(repo.working_tree_dir)
    monkeypatch.setenv('MAX_TEST_CONTAINERS', str(params.max_workers))
    if params.max_failed_services:
        monkeypatch.setattr(
            'taxi_buildagent.dockertest.DOCKERTEST_MAX_FAILED_SERVICES',
            params.max_failed_services,
        )
    if params.core_files:
        monkeypatch.setenv('TC_CORES_DIR', CORES_DIR.name)
        CORES_DIR.mkdir()
        for core in params.core_files:
            CORES_DIR.joinpath(core).touch()

    @patch_requests('https://s3.mds.yandex.net/common/flap_tests')
    def load_flap_tests_list(method, url, **kwargs):
        assert method.upper() == 'GET'
        if params.is_mds_request_broken:
            return patch_requests.response(status_code=404)
        return patch_requests.response(json=params.mds_response)

    _rewrite_services_yaml(params.test_targets, params.report_changed_dirs)

    n_services = len(params.expected_services)
    n_workers = params.max_workers
    tested_services = []
    used_workers = set()
    logs = []
    expected_logs = []
    downs = []
    image_by_service = {}
    retries_by_services: collections.Counter = collections.Counter()
    ps_workers = []
    expected_ps_workers = []
    worker_by_service = {}

    @commands_mock('docker-compose')
    def docker_compose(args, **kwargs):
        service_name = args[-1]
        worker = args[2]
        subcommand = args[3]
        if params.command_timeout_exceeded and service_name in params.services:
            raise asyncio.TimeoutError('Timeout exceeded')
        if kwargs.get('env') is not None:
            image_by_service[service_name] = kwargs['env'].get('DOCKER_IMAGE')
        exit_code = params.exit_codes.get(service_name, 0)

        if subcommand == 'run':
            worker_by_service[service_name] = worker
            used_workers.add(worker)
            exp_retries = params.expected_retries_by_services[service_name]
            if retries_by_services[service_name] < exp_retries:
                retries_by_services[service_name] += 1
                return commands_mock.result(
                    exit_code=1,
                    message=(
                        'Couldn\'t connect to Docker daemon at '
                        'http+docker://localhost - is it running?\n'
                    ),
                    to_stderr=True,
                )
            tested_services.append(service_name)
            if exit_code != 0:
                expected_ps_workers.append(worker)
                if params.bad_environment:
                    expected_logs.append(worker)
            if exit_code == 2 and not params.max_failed_services:
                return commands_mock.result(
                    exit_code=exit_code,
                    message='Something with docker went wrong...\nOh, sh*t!\n',
                    to_stderr=True,
                )
            esc_name = service_name.replace('/', '-')
            TEST_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            TEST_REPORTS_DIR.joinpath(f'junit-{esc_name}.xml').touch()
            return exit_code

        if subcommand == 'logs':
            logs.append(worker)
            return 'Some logs of environment'

        if subcommand == 'down':
            downs.append(worker)
            return 0

        if subcommand == 'ps':
            ps_workers.append(worker)
            if params.bad_environment:
                return ''
            return 'dockertest-env'

        return 'Unknown command'

    recorded_stderr = []

    def _buffer_stderr_mock(buffer):
        if not buffer.strip():
            return
        recorded_stderr.append(buffer)

    monkeypatch.setattr(
        'taxi_buildagent.dockertest._print_stderr', _buffer_stderr_mock,
    )

    try:
        if params.max_failed_services is not None:
            with pytest.raises(dockertest.MaxFailedServicesError) as excinfo:
                run_tests_in_parallel.main(
                    [
                        '--docker-compose-service',
                        params.dc_service,
                        '--base-image',
                        params.base_image,
                        *params.services,
                    ],
                )
            assert excinfo.value.subject == (
                f'Tests for at least {params.max_failed_services} services '
                f'failed. Abort testing'
            )

        else:
            run_tests_in_parallel.main(
                [
                    '--docker-compose-service',
                    params.dc_service,
                    '--base-image',
                    params.base_image,
                    *params.services,
                ],
            )
    except SystemExit as exc:
        assert exc.code == max(params.exit_codes.values())
    finally:
        dc_calls = docker_compose.calls
        if params.command_timeout_exceeded:
            assert len(dc_calls) == n_workers * 3  # sorry(
        else:
            assert len(dc_calls) == (
                n_services
                + n_workers
                + len(expected_ps_workers)
                + len(expected_logs)
                + sum(params.expected_retries_by_services.values())
            )
        assert len(load_flap_tests_list.calls) == 1
        assert sorted(tested_services) == sorted(params.expected_services)
        assert None not in used_workers
        assert None not in downs
        assert None not in logs
        if not params.yt_services:
            assert len(used_workers) == min(n_services, n_workers)
        assert len(downs) == n_workers
        assert sorted(logs) == sorted(expected_logs)
        assert image_by_service == params.expected_base_image

        if params.yt_services:
            for service in params.yt_services:
                assert worker_by_service[service] == 'dockertest0'

        assert params.expected_retries_by_services == retries_by_services
        if (
                params.max_failed_services is None
                and not params.command_timeout_exceeded
        ):
            assert sorted(ps_workers) == sorted(expected_ps_workers)
        assert _is_saved_flap_tests_list_correct(
            params.mds_response, params.is_mds_request_broken,
        )
        assert (
            teamcity_report_test_problem.calls
            == params.tc_report_test_problem_calls
        )
        assert (
            len(list(CORES_DIR.glob('*'))) <= dockertest.MAX_CORE_FILES_COUNT
        )
        # stderr order is no longer guaranteed to be stable
        assert set(recorded_stderr) == set(params.stderr)
        assert teamcity_report_problems.calls == params.tc_report_problem
        if params.command_timeout_exceeded:
            errors = commands_mock.pop_errors()
            errors = [str(error) for error in errors]
            assert errors == ['Timeout exceeded'] * len(params.services)


def _is_saved_flap_tests_list_correct(mds_response, is_mds_request_broken):
    expected_flap_tests = sorted(mds_response)
    flap_tests = []
    try:
        for testname in FLAP_TESTS_FILENAME.read_text().split():
            flap_tests.append(testname)
        assert not is_mds_request_broken
        return expected_flap_tests == sorted(flap_tests)
    except FileNotFoundError:
        assert is_mds_request_broken
        return True


def _rewrite_services_yaml(test_targets, report_changed_dirs):
    services_yaml = utils.load_yaml('services.yaml')
    if test_targets is not None:
        services_yaml.update({'common': {'test-targets': test_targets}})
    if report_changed_dirs is not None:
        services_yaml.update({'report-changed-dirs': report_changed_dirs})
    with open('services.yaml', 'w') as fstream:
        yaml.dump(services_yaml, fstream)
