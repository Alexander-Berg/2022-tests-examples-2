# -*- coding: utf-8 -*-
import logging
import logging.config
import tempfile
import os.path
import allure
import pytest
import tarfile
from allure.utils import labels_of

from portal.function_tests.util.common.env import morda_env
from portal.function_tests.util.common.params import PytestConfig
import yatest

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,  # this fixes the problem
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
})

pytest_plugins = 'portal.function_tests.util.common.monitoring'

logging.getLogger('requests').setLevel(logging.INFO)

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption('--morda_env', action='store', default='production',
                     help='Morda environment')
    parser.addoption('--monitoring', action='store', default='0',
                     help='Is monitoring')
    parser.addoption('--retry_count', action='store', default='0',
                     help='Retry count')
    parser.addoption('--dns_override', action='store', default='',
                     help='Dns override ips')
    parser.addoption('--dns_morda', action='store', default='',
                     help='Morda dns override')
    parser.addoption('--rate_limit', action='store', type=int, default=10,
                     help='Rate limit for HTTP requests (rps)')
    parser.addoption('--tests_path', action='store', default='',
                     help='Paths for tests in new framework')


@pytest.yield_fixture(scope='function', autouse=True)
def record_logs():
    logger = logging.getLogger()

    temp_file = tempfile.NamedTemporaryFile()
    file_handler = logging.FileHandler(temp_file.name)
    file_handler.setFormatter(logging.Formatter('%(levelname)s\t%(asctime)s\t%(name)s:%(lineno)s\t%(message)s'))
    logger.addHandler(file_handler)

    yield

    logger.removeHandler(file_handler)
    temp_file.seek(0)
    allure.attach('test.log', temp_file.read())


def pytest_configure(config):
    PytestConfig(config)

    schema_path = yatest.common.work_path('schema')
    tar = tarfile.open(yatest.common.runtime.work_path(os.path.join(schema_path, 'resource.tar.gz')))
    tar.extractall(path=schema_path)
    tar.close()


def get_list_of_broken_tests():
    def parse_file(path):
        temp = []
        with open(path, 'r') as f:
            for line in f:
                if "'value' => " in line and " tests" in line:
                    line = line.lstrip()[:-2].replace("'value' => '", "")
                    line = line[line.rfind(' ') + 1:] + '.' + line[:line.rfind(' ')]
                    if line.endswith('_yaml]'):
                        line = '{}.yaml]'.format(line[:-6])
                    temp.append(line)
        return temp
    madm_prod = '/opt/www/bases/madm/production/disabled_tests'
    madm_dev = '/opt/www/bases/madm/-{}/testing/disabled_tests'.format(morda_env().split('.')[0])
    if os.path.isfile(madm_dev):
        return parse_file(madm_dev)
    elif os.path.isfile(madm_prod):
        return parse_file(madm_prod)
    return []


def pytest_collection_modifyitems(session, config, items):
    """ called after collection has been performed, may filter or re-order
    the items in-place."""
    def f(item):
        item_labels = set((l.name, l.value) for l in labels_of(item))  # see label_type
        arg_labels = set().union(item.config.option.allurefeatures,
                                 item.config.option.allurestories,
                                 item.config.option.allureseverities)

        return not (arg_labels and not item_labels & arg_labels)

    items[:] = [e for e in items if f(e)]
    # тут помечаем поломанные тесты
    broken_tests = get_list_of_broken_tests()
    skip = pytest.mark.skip(reason='broken functional test')
    for item in items:
        if '{}{}'.format(item.location[0][:-2], item.location[2]).replace('/', '.') in broken_tests:
            item.add_marker(skip)
