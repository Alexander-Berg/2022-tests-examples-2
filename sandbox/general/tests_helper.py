import os
import re

from sandbox.projects.metrika.core.utils import metrika_core_tests_helper
from sandbox.projects.metrika.java.utils import metrika_java_helper
from sandbox.projects.metrika.utils import vcs


class TestsHelper(metrika_core_tests_helper.MetrikaCoreTestsHelper):

    @classmethod
    def get_packages_versions(cls, arcadia_url, packages):
        daemons = TestsHelper.get_daemons_under_arcadia_b2b(arcadia_url)
        daemons_versions = {}
        for daemon in daemons:
            daemons_versions[daemon] = packages.get(daemon) or metrika_java_helper.MetrikaJavaHelper.get_stable_version(daemon)
        return daemons_versions

    @staticmethod
    def get_daemons_under_arcadia_b2b(arcadia_url="arcadia-arc:/#trunk"):
        with vcs.mount_arc(arcadia_url) as arcadia:
            with open(os.path.join(arcadia, "metrika/core/b2b/app/daemons/ya.make")) as file:
                yamake_text = file.read()
                return re.findall(r"AUTOUPDATED (.+?) ", yamake_text)
