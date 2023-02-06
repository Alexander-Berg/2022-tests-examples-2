# pylint: disable=redefined-outer-name
import pytest

import access_control_roles_checker.generated.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['access_control_roles_checker.generated.pytest_plugins']


@pytest.fixture(name='access_control_roles_checker')
def _access_control_checker(library_context):
    return library_context.access_control_roles_checker
