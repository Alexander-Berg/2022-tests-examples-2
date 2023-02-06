# coding: utf-8
from dmp_suite.py_env.service_setup import resolve_service_by_path


def check_service_name_by_path(path):
    from init_py_env import service as configured_service
    file_service_name = resolve_service_by_path(path).name
    if not configured_service.root:
        assert file_service_name == configured_service.name
