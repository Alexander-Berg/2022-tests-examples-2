# coding=utf-8

from sandbox import sdk2
from sandbox.projects.common import apihelpers
from sandbox.projects.metrika.core import metrika_core_b2b_scenario_execute
from sandbox.projects.metrika.core.metrika_core_b2b_scenario_execute import tests_helper as scenario_helper
from sandbox.projects.metrika.core.utils import metrika_core_tests_helper


class TestsHelper(metrika_core_tests_helper.MetrikaCoreTestsHelper):

    @staticmethod
    def prepare(task):
        TestsHelper.create_users(task)
        TestsHelper.add_tokens(task)
        TestsHelper.add_metrika_xml(task)
        TestsHelper.install_environment_packages(task)
        TestsHelper.configure_zookeeper(task)
        TestsHelper.configure_clickhouse(task)
        TestsHelper.configure_mysql(task)

    @staticmethod
    def configure_clickhouse(task):
        TestsHelper._configure_clickhouse(task)

    @staticmethod
    def configure_mysql(task):
        metrika_core_tests_helper.MetrikaCoreTestsHelper.configure_mysql(task)

        TestsHelper.add_mysql_user_metrika(task, "localhost")
        TestsHelper.add_mysql_user_metrika(task, "127.0.0.1")
        TestsHelper.add_mysql_user_metrika(task, "::1")
        TestsHelper.add_mysql_user_metrika(task, "*")

        TestsHelper.shell(task, ["mysql", "-u", "root", "-e", "flush privileges;"])

    @classmethod
    def get_packages_versions(cls, task, packages):
        return scenario_helper.TestsHelper.get_packages_versions(task, packages)

    @staticmethod
    def get_input_resources(task):
        pass

    @classmethod
    def try_to_get_tests_output_resource(cls, task, arcadia_url, packages, clickhouse_resource, force, description):
        resource_id = cls.get_last_tests_output_resource_id(
            packages, metrika_core_tests_helper.MetrikaCoreOutputB2bTestData,
            arcadia_b2b=True,
            task_release=cls._get_task_release(task),
        )
        if not resource_id or force:
            return metrika_core_b2b_scenario_execute.MetrikaCoreB2bScenarioExecute, dict(
                description=" ".join([task.Parameters.description, description]),
                arcadia_url=arcadia_url,
                report_ttl=task.Parameters.report_ttl,
                fail_task_on_test_failure=task.Parameters.fail_task_on_test_failure,
                report_startrek=task.Parameters.report_startrek,
                issue_key=task.Parameters.issue_key,
                daemons=packages,
                clickhouse_resource=clickhouse_resource,
                local_daemons=task.Parameters.local_daemons,
                local_configs=task.Parameters.local_configs,
                fast=task.Parameters.fast
            )
        else:
            return resource_id

    @classmethod
    def get_tests_output_resource_id(cls, task_id, resource_type):
        return apihelpers.get_task_resource_id(sdk2.Task[task_id].Context.test_task, resource_type)

    @staticmethod
    def extract_tests_output_resources(task, test_resource_id, stable_resource_id):
        TestsHelper._extract_tests_output_resources(task, test_resource_id, stable_resource_id, mysql=True, files=True)
