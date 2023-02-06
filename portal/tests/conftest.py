# -*- coding: utf-8 -*-
import logging
import logging.config
import tempfile

import allure
import pytest
from allure.utils import labels_of

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

pytest_plugins = 'common.monitoring'

logging.getLogger('requests').setLevel(logging.INFO)

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption('--morda_env', action='store', default='production',
                     help='Morda environment')
    parser.addoption('--monitoring', action='store', default='0',
                     help='Is monitoring')
    parser.addoption('--dns_override', action='store', default='',
                     help='Dns override ips')
    parser.addoption('--dns_morda', action='store', default='',
                     help='Morda dns override')


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
