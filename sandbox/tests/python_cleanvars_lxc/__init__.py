from sandbox.projects.home.infra import python_lxc
from sandbox.projects.home.resources import HomeCleanvarsPythonTestsLxc


CUSTOM_PACKAGES = python_lxc.CUSTOM_PACKAGES + ['yandex-jdk8']

CUSTOM_SCRIPT = python_lxc.CUSTOM_SCRIPT + ['apt-add-repository ppa:qameta/allure -y && apt-get update && apt-get install allure']


class BuildHomePythonCleanvarsLxc(python_lxc.BuildHomePythonLxc):

    class Parameters(python_lxc.BuildHomePythonLxc.Parameters):
        resource_type = python_lxc.BuildHomePythonLxc.Parameters.resource_type(default=HomeCleanvarsPythonTestsLxc.name)
        custom_packages = python_lxc.BuildHomePythonLxc.Parameters.custom_packages(default=' '.join(CUSTOM_PACKAGES))
        custom_script = python_lxc.BuildHomePythonLxc.Parameters.custom_script(default='\n'.join(CUSTOM_SCRIPT))
