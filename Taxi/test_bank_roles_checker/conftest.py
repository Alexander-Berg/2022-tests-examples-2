# pylint: disable=redefined-outer-name
import pytest

import bank_roles_checker.generated.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['bank_roles_checker.generated.pytest_plugins']


@pytest.fixture(name='bank_roles_checker')
def _bank_roles_checker(library_context):
    return library_context.bank_roles_checker
