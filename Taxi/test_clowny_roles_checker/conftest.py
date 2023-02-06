# pylint: disable=redefined-outer-name
import pytest

import clowny_roles_checker.generated.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['clowny_roles_checker.generated.pytest_plugins']


@pytest.fixture(name='clowny_roles_checker')
def _clowny_roles_checker(library_context):
    return library_context.clowny_roles_checker


@pytest.fixture(autouse=True)
def _clown_cache_mocks_autouse(clown_cache_mocks):
    return clown_cache_mocks
