import os
import sys
import pytest

from sandbox import common


@pytest.fixture(scope="session")
def sandbox_tasks_dir():
    return reduce(lambda p, _: os.path.dirname(p), xrange(3), os.path.abspath(__file__))


@pytest.fixture(scope="session")
def sandbox_dir_in_path(request, sandbox_tasks_dir):
    sandbox_dir = request.config.getoption("--sandbox-dir")
    if not sandbox_dir:
        sandbox_dir = os.path.join(os.path.dirname(sandbox_tasks_dir), "sandbox")
    sys.path.append(str(sandbox_dir))


@pytest.fixture(scope="session")
def run_long_tests(request):
    return request.config.getoption("--run-long-tests")


@pytest.fixture(scope="session")
def run_tests_with_filter(request):
    return request.config.getoption("--tests")


@pytest.fixture(scope="session")
@pytest.mark.usefixtures("sandbox_dir_in_path")
def tasks_modules(sandbox_tasks_dir):
    common.projects_handler.load_project_types(True, force_from_fs=True)
    target_dir = sandbox_tasks_dir
    # force all modules to be imported as "sandbox.projects.*"
    if common.system.inside_the_binary():
        target_dir = os.path.dirname(target_dir)
    return common.projects_handler.get_packages(target_dir)


@pytest.fixture(scope="session")
def project_types():
    return common.projects_handler.load_project_types(True, force_from_fs=True)
