import collections
import os
import os.path
import sys

import pytest

from taxi_tests import utils
from tests_plugins.daemons import service_daemon


pytest_plugins = [
    'taxi_tests.plugins.experiments',
    'taxi_tests.plugins.common',
    'taxi_tests.plugins.nginx',
    'tests_plugins.mockserver',
    'tests_plugins.mongodb_settings',
]


def _postgresql_connections(databases):
    return {
        db_name: (
            'host=/tmp/testsuite-postgresql user=testsuite dbname=%s' % db_name
        )
        for db_name in databases
    }


class Settings:
    INITIAL_DATA_PATH = [
        os.path.join(os.path.dirname(__file__), '../tests/default_fixtures'),
    ]
    # {database_name: connection_string}
    POSTGRESQL_CONNECTIONS = _postgresql_connections(['taximeter'])


def pytest_addoption(parser):
    parser.addoption(
        '--build-dir',
        default=os.path.normpath(
            os.path.join(os.path.dirname(__file__), '../../build'),
        ),
        help='Path to build directory.',
    )
    parser.addoption(
        '--testsuite-dir',
        default=os.path.normpath(
            os.path.join(os.path.dirname(__file__), '..'),
        ),
        help='Path to testsuite directory.',
    )
    parser.addoption(
        '--fastcgi-disable',
        dest='service_disable',
        default=False,
        action='store_true',
        help=(
            'Do not start fastcgi daemon. '
            'Deprecated use --service-disable instead'
        ),
    )
    parser.addoption(
        '--fastcgi-valgrind-enable',
        default=False,
        action='store_true',
        help='Run fastcgi under valgrind.',
    )


def pytest_configure(config):
    build_dir = config.getoption('--build-dir')
    testsuite_dir = config.getoption('--testsuite-dir')

    sys.path.extend(
        [
            os.path.join(testsuite_dir, 'third_party'),
            os.path.join(build_dir, 'python'),
        ],
    )


# Filter out service output, see TAXIDATA-2098
@pytest.mark.tryfirst
def pytest_runtest_logreport(report):
    if report.passed:
        if report.when == 'call':
            report.sections = [
                section
                for section in report.sections
                if not section[0].startswith('Captured std')
            ]


def pytest_runtest_makereport(item, call):
    if call.when == 'call':
        if not call.excinfo:
            item._report_sections = []


@pytest.fixture(scope='session')
def settings(
        build_dir,
        testsuite_dir,
        pytestconfig,
        mongo_host,
        nginx_port,
        worker_id,
        mongodb_settings,
):
    settings = Settings()
    settings.TAXI_BUILD_DIR = build_dir
    settings.TESTSUITE_CONFIGS = os.path.join(build_dir, 'testsuite/configs')
    settings.MANUAL_SECDIST_PATH = os.path.join(
        testsuite_dir, os.pardir, 'manual', 'secdist.json',
    )
    settings.JOBS_SECDIST_PATH = os.path.join(
        settings.TESTSUITE_CONFIGS, 'jobs-secdist_%s.json' % worker_id,
    )
    settings.SURGER_JOBS_SECDIST_PATH = os.path.join(
        settings.TESTSUITE_CONFIGS,
        'yandex-fastcgi-taxi-surger-secdist_%s.json' % worker_id,
    )
    settings.SECDIST_TEMPLATE_PATH = os.path.join(
        testsuite_dir, 'secdist_template.json',
    )
    settings.TVM_SOURCE_DIR = os.path.join(testsuite_dir, 'configs')
    settings.TAXI_JOBS_PATH = os.path.join(
        build_dir, 'jobs/lib/yandex-taxi-jobs-cxx',
    )
    settings.TAXI_SURGER_JOBS_PATH = os.path.join(
        build_dir, 'surger/jobs/lib/yandex-taxi-surger-jobs',
    )
    settings.SECDIST_PATH = os.path.join(
        settings.TESTSUITE_CONFIGS, 'secdist.json',
    )
    settings.TAXI_BASE_URL = 'http://localhost:%d/' % nginx_port

    _configure_fastcgi(settings, pytestconfig)
    _configure_database(settings, mongo_host, mongodb_settings)

    return settings


@pytest.fixture(scope='session')
def jobs_config(settings):
    JOBS_CONFIG = collections.namedtuple(
        'JobsConfig',
        [
            'source_dir',
            'secdist_dev',
            'output_secdist_path',
            'secdist_template',
        ],
    )
    return JOBS_CONFIG(
        source_dir=settings.TVM_SOURCE_DIR,
        secdist_dev=settings.MANUAL_SECDIST_PATH,
        output_secdist_path=settings.JOBS_SECDIST_PATH,
        secdist_template=settings.SECDIST_TEMPLATE_PATH,
    )


@pytest.fixture(scope='session')
def surger_jobs_config(settings):
    SURGER_JOBS_CONFIG = collections.namedtuple(
        'JobsConfig',
        [
            'source_dir',
            'secdist_dev',
            'output_secdist_path',
            'secdist_template',
        ],
    )
    return SURGER_JOBS_CONFIG(
        source_dir=settings.TVM_SOURCE_DIR,
        secdist_dev=settings.MANUAL_SECDIST_PATH,
        output_secdist_path=settings.SURGER_JOBS_SECDIST_PATH,
        secdist_template=settings.SECDIST_TEMPLATE_PATH,
    )


# Enable global redis support for all the projects.
#
# TODO: enable redis based on service.yaml instead.
@pytest.fixture(scope='session', autouse=True)
def global_redis_support(redis_service):
    pass


@pytest.fixture(autouse=True)
def global_enable_redis_store(redis_store):
    pass


@pytest.fixture(scope='session')
def build_dir(request):
    return request.config.getoption('--build-dir')


@pytest.fixture(scope='session')
def testsuite_dir(request):
    return request.config.getoption('--testsuite-dir')


@pytest.fixture(scope='session')
def regenerate_config(worker_id, testsuite_session_context):
    def _regenerate_config(config_path, secdist_path):
        with open(config_path, 'r', encoding='utf-8') as config_file:
            config_template = config_file.read()

        mockserver = testsuite_session_context.mockserver
        config_body = config_template.replace(
            '@@MOCKSERVER@@', f'{mockserver.host}:{mockserver.port}',
        )
        config_body = config_body.replace(
            '@@SERVICE_SECDIST_PATH@@', secdist_path,
        )
        config_body = config_body.replace(
            '@@WORKER_SUFFIX@@',
            '_' + worker_id if worker_id != 'master' else '',
        )

        filename, extension = os.path.splitext(config_path)
        config_path = '%s_%s%s' % (filename, worker_id, extension)

        with open(config_path, 'w', encoding='utf-8') as config_file:
            config_file.write(config_body)

        return config_path

    return _regenerate_config


@pytest.fixture(scope='session')
def exp3_cache_path(worker_id):
    worker_suffix = '_' + worker_id if worker_id != 'master' else ''
    return '/var/tmp/cache/yandex/exp3' + worker_suffix


@pytest.fixture(scope='session')
def tags_cache_path(worker_id):
    worker_suffix = '_' + worker_id if worker_id != 'master' else ''
    return '/var/tmp/cache/yandex/tags' + worker_suffix


@pytest.fixture(scope='session')
def etags_cache_path(worker_id):
    worker_suffix = '_' + worker_id if worker_id != 'master' else ''
    return '/var/tmp/cache/yandex/reposition_etags' + worker_suffix


def _configure_fastcgi(settings, pytestconfig):
    settings.fastcgi = service_daemon.ServiceSettings()

    daemon_path = utils.which(
        'fastcgi-daemon2', extra_path=['/usr/sbin', '/usr/local/sbin'],
    )

    # Disable graceful shutdown as performance optimization
    settings.fastcgi.GRACEFUL_SHUTDOWN = False

    # Required to store coverage data before exit
    if os.getenv('FASTCGI_GRACEFUL_SHUTDOWN') == '1':
        settings.fastcgi.GRACEFUL_SHUTDOWN = True

    if pytestconfig.getoption('--fastcgi-valgrind-enable'):
        print(
            'INFO: Valgrind from Ubuntu\'s repository is limited to 500 '
            'threads. If you get an error like "VG_N_THREADS is too low", '
            'just lower the number of threads in '
            'testsuite/configs/taxi-*.conf.',
        )
        settings.fastcgi.GRACEFUL_SHUTDOWN = True
        settings.fastcgi.POLL_RETRIES = 200 * 1000

        # Valgrind is too slow, fastcgi fails to init in reasonable time
        # with leak-check enabled :-(
        # You can comment out most of background code of taxi (e.g. redis)
        # and uncomment valgrind options below:
        settings.fastcgi.BASE_COMMAND = [
            utils.which('valgrind'),
            # '--track-origins=yes',
            # '--leak-check=full',
            '--error-limit=no',
            '--suppressions='
            + os.path.join(
                settings.TESTSUITE_CONFIGS, 'valgrind-suppressions.conf',
            ),
            '--',
            daemon_path,
        ]
    else:
        settings.fastcgi.BASE_COMMAND = [daemon_path]


def _configure_database(settings, mongo_host, mongodb_settings):
    mongo_connections = {}
    # TODO: It might be a good idea to use connections required by service
    for alias, collection_info in mongodb_settings.items():
        connection_name = collection_info['settings']['connection']
        # TODO: port is hardcoded in mongo startup script
        mongo_connections[connection_name] = mongo_host
    settings.MONGO_CONNECTIONS = mongo_connections
