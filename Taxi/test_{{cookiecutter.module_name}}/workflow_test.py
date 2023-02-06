import pytest

from dmp_suite.py_env.service_setup import resolve_service_by_path
from tests.workflow_test import base_workflow_checks

file_service = resolve_service_by_path(__file__)


@pytest.mark.parametrize('check', base_workflow_checks.get())
def test_all_case(check):
    check(file_service)
