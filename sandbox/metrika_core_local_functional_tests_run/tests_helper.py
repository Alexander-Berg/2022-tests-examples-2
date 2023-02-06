# coding=utf-8
import logging

from sandbox.projects.common import apihelpers
from sandbox.projects.geobase.IpregLayoutStable import resource
from sandbox.projects.metrika.core.utils import metrika_core_tests_helper

logger = logging.getLogger("tests-helper")


class TestsHelper(metrika_core_tests_helper.MetrikaCoreTestsHelper):

    @staticmethod
    def prepare(task, packages, hostname=None):
        TestsHelper.create_users(task, hostname)
        TestsHelper.add_metrika_xml(task, hostname)
        TestsHelper.add_tokens(task, hostname)
        TestsHelper.load_resources(task, hostname)
        TestsHelper.install_environment_packages(task, hostname)
        TestsHelper.configure_zookeeper(task, hostname)
        TestsHelper.configure_mysql(task, hostname)
        TestsHelper.configure_counters_server(task, hostname)
        TestsHelper.configure_goals_server(task, hostname)
        TestsHelper.configure_user_attr_server(task, hostname)
        TestsHelper.configure_clickhouse(task, hostname)
        TestsHelper.configure_ydb(task, hostname)
        TestsHelper.install_test_packages(task, packages, hostname)

    @staticmethod
    def load_resources(task, hostname=None):
        TestsHelper.load_resource(task, apihelpers.get_last_resource_with_attribute(resource.IPREG_LAYOUT_STABLE, "released", "stable").id, "/opt/ipreg", "ipreg_layout.json", hostname=hostname)

    @staticmethod
    def install_environment_packages(task, hostname=None):
        metrika_core_tests_helper.MetrikaCoreTestsHelper.install_environment_packages(task, hostname)
        TestsHelper.install_packages(task,
                                     {
                                         "mongodb": "1:2.6.9.yandex1",
                                         "percona-server-client-5.7": "5.7.25-28-1.trusty",
                                         "percona-server-common-5.7": "5.7.25-28-1.trusty",
                                         "percona-server-server-5.7": "5.7.25-28-1.trusty"
                                     },
                                     hostname)

    @staticmethod
    def configure_clickhouse(task, hostname=None):
        TestsHelper._configure_clickhouse(task, hostname=hostname)

    @staticmethod
    def configure_mysql(task, hostname=None):
        metrika_core_tests_helper.MetrikaCoreTestsHelper.configure_mysql(task, hostname)

        TestsHelper.add_mysql_user_metrika(task, "localhost", hostname)
        TestsHelper.add_mysql_user_metrika(task, "127.0.0.1", hostname)
        TestsHelper.add_mysql_user_metrika(task, "::1", hostname)
        TestsHelper.add_mysql_user_metrika(task, "*", hostname)
        TestsHelper.add_mysql_user_metrika(task, "2a02:6b8:%", hostname)

        TestsHelper.script(task, 'mysql -u root -e "flush privileges;"', hostname)
        TestsHelper.script(task, 'mysql -u root -e "SELECT @@version; SELECT @@SESSION.sql_mode;"', hostname)

    @staticmethod
    def install_test_packages(task, packages, hostname=None):
        stable_packages = [package for package, version in packages.items() if not version and TestsHelper.is_package(package)]
        stable_programs = [package for package, version in packages.items() if not version and not TestsHelper.is_package(package)]
        versioned_packages = dict((package, version) for package, version in packages.items() if version and TestsHelper.is_package(package))
        versioned_programs = dict((package, version) for package, version in packages.items() if version and not TestsHelper.is_package(package))
        TestsHelper.install_stable_packages(task, stable_packages, hostname)
        TestsHelper.install_stable_tarballs(task, stable_programs, hostname)
        TestsHelper.install_packages(task, versioned_packages, hostname)
        TestsHelper.install_tarballs(task, versioned_programs, hostname)

    @staticmethod
    def is_package(name):
        return "-metrika-yandex" in name or "clickhouse" in name
