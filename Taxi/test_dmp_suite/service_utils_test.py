import mock
import pytest
from dmp_suite.service_utils import get_service_by_module


def test_get_project_by_module():
    project = get_service_by_module('tst.lvl2.lvl2.lvl3')
    assert project == 'tst'
