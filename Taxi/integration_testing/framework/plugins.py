import os
import pytest
from typing import Callable
import yatest

from taxi.integration_testing.framework import environment


@pytest.fixture(scope='session')
def testenv(image_tag_factory: Callable[[str], str], request):
    testenv = environment.EnvironmentManager(image_tag_factory)
    yield testenv
    testenv.cleanup()


@pytest.fixture(scope='session')
def image_tag_factory() -> Callable[[str], str]:
    tags_map = {
        'elastic': 'latest',
        'kibana': 'latest',
        'memcached': None,
        'mongo': 'latest',
        'postgres': '11',
        'redis': 'latest',
        'redis-sentinel': 'latest'
    }

    default_tag = yatest.common.get_param('image-tag-default')

    if default_tag is None or default_tag == '' or str.isspace(default_tag):
        default_tag = '#BUILD'

    tag_overrides = yatest.common.get_param('image-tag-overrides')

    if tag_overrides is None:
        tag_overrides = ''

    for service_tag in tag_overrides.split(' '):
        if service_tag is None or service_tag == '' or str.isspace(service_tag):
            continue

        try:
            colon_index = service_tag.rindex(':')
        except ValueError:
            raise environment.EnvironmentSetupError(f'Invalid tag override {service_tag}: colon is missing.')

        service = service_tag[:colon_index]
        tag = service_tag[colon_index + 1:]

        if str.isspace(tag):
            tag = None

        tags_map[service] = tag

    def image_tag(service: str):
        return resolve_tag_alias(tags_map.get(service, default_tag))

    return image_tag


def resolve_tag_alias(tag: str):
    if tag == '#BUILD':
        return 'test'
    if tag == '#PROD':
        return 'latest'
    if tag.startswith('#'):
        raise environment.EnvironmentSetupError(f'Invalid tag alias {tag}.')
    return tag


@pytest.fixture(scope='session')
def platform() -> str:
    return os.getenv('PLATFORM', 'xenial')
