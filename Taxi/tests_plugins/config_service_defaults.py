import pytest

from taxi_tests import json_util

FALLBACK_PATH = '/common/generated/fallback/configs.json'


@pytest.fixture(scope='session')
def config_service_defaults(settings, testsuite_session_context):
    fallback_path = settings.TAXI_BUILD_DIR + FALLBACK_PATH
    with open(fallback_path, 'r', encoding='utf-8') as fallback_file:
        raw_data = fallback_file.read()
    fallback = json_util.loads(
        raw_data, mockserver=testsuite_session_context.mockserver,
    )
    return fallback['configs']
