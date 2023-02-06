# -*- coding: utf-8 -*-

import logging
from sandbox import sdk2

from sandbox.sandboxsdk.errors import SandboxTaskFailureError
import sandbox.common.types.resource as ctr
import sandbox.common.types.task as ctt
import sandbox.common.types.client as ctc

import differ
from report_requester import ReportRequester
from report_requester import line_requests_iterator
from get_noapacheupper import get_noapacheupper
from sandbox.projects.websearch import release_setup


class WizardsResource(sdk2.Resource):
    """Resource with responds on queries"""


class TestNoapacheupper2(sdk2.Task):
    """
        **Описание**
         Тест обстрела noapache через репорт (пользовательскими запросами)
         Переписанный TestNoapacheupper под sdk2
    """
    descr = "TestNoapacheupper2"

    class Requirements(sdk2.Requirements):
        client_tags = release_setup.WEBSEARCH_TAGS_P0 & ~ctc.Tag.LXC

    class Parameters(sdk2.Parameters):
        description = "Test Noapacheupper2"
        max_restarts = 10
        kill_timeout = 3600

        use_arcadia = sdk2.parameters.Bool('Build from arcadia', default_value=False)

        with use_arcadia.value[True]:
            with sdk2.parameters.Group("Arcadia parameters") as arcadia_block:
                arcadia_url = sdk2.parameters.ArcadiaUrl('arcadia url')
                rearrange_data_url = sdk2.parameters.String('Svn url for branch with rearrange data',
                                                            default_value='arcadia:/arc/trunk/')
                noapache_config_url = sdk2.parameters.String('Svn url for branch with current config options',
                                                             default_value='arcadia:/arc/trunk/')

        # with use_arcadia.value[False]:
        with sdk2.parameters.Group("Build parameters") as component_block:
            noapache_binary = sdk2.parameters.Resource(
                'Noapacheupper executable', resource_type=sdk2.Resource["NOAPACHE_UPPER"])
            noapache_config = sdk2.parameters.Resource(
                'Noapacheupper config')  # , resource_type=sd)
            noapache_data = sdk2.parameters.Resource(
                'Noapacheupper data')  # , resource_type=sdk2.Resource["NOAPACHEUPPER_DATA"].type)
            noapache_rearrange_data = sdk2.parameters.Resource(
                'Rearrange data')  # , resource_type=sdk2.Resource["REARRANGE_DATA"])
            noapache_rearrange_dynamic_data = sdk2.parameters.Resource(
                'Rearrange dynamic data')  # , resource_type=sdk2.Resource["REARRANGE_DYNAMIC_DATA"])

        with sdk2.parameters.Group("Noapacheupper parameters") as mode_block:
            apphost_mode = sdk2.parameters.Bool('Use apphost mode', default_value=True)
            start_timeout = sdk2.parameters.Integer('Start timeout (sec)', default_value=600)
            shutdown_timeout = sdk2.parameters.Integer('Shutdown timeout (sec)', default_value=60)
            server_input_deadline = sdk2.parameters.String(
                'DDoS protection (read input data timeout, empty_string == not change)', default_value='')

        with sdk2.parameters.Group("Requester parameters") as request_block:
            limit_requests = sdk2.parameters.Integer('Limit number of used requests (0 = all)', default_value=0)
            use_workers = sdk2.parameters.Integer('Use workers (processes) for sending requests', default_value=5)
            report_url = sdk2.parameters.String('report_url',
                                                description='Report url (default: https://hamster.yandex.ru/search?)',
                                                default_value='https://hamster.yandex.ru/search?', multiline=True)
            users_queries = sdk2.parameters.LastReleasedResource(
                'Users queries')  # , resource_type=sdk2.Resource["USERS_QUERIES"])
            additional_cgi_params = sdk2.parameters.String('Additional cgi params', default_value='')
            method = sdk2.parameters.String('Method for grabber', default_value='xpath_get')
            additional_method_arguments = sdk2.parameters.String('Additional method params', default_value='')

    def init_search_component(self, component):
        pass

    '''
    @classmethod
    def filter_default_host(cls, client_info):
        """
            Limit to precise to avoid GLIBC_2.14 linking bug
        """
        if client_info['hostname'].startswith('sandbox117'):
            return False  # skip bad luck host (samething troubles with memory allocation)
        if client_info['arch'] == 'linux':
            return 'precise' in client_info['platform']
        return True'''

    def set_up_and_use(self, build_values):
        logging.info("set up noapache for requests")
        responds = {}
        rr = ReportRequester(
            self.Parameters.report_url,
            self.Parameters.additional_cgi_params,
            self.Parameters.method, responds,
            self.Parameters.additional_method_arguments
        )

        search_component = get_noapacheupper(self, build_values, use_verify_stderr=False)
        self.init_search_component(search_component)  # hook for patching run command (use valgrind, etc...)

        rr.use(
            line_requests_iterator(str(sdk2.ResourceData(self.Parameters.users_queries).path)),
            search_component,
            process_count=self.Parameters.use_workers,
            requests_limit=self.Parameters.limit_requests
        )

        if rr.error:
            logging.info("errors!!!")
            raise SandboxTaskFailureError(rr.error)
        return responds

    def set_up_parameters_from_arcadia(self):
        subtasks = {}
        if not self.Parameters.noapache_config:
            general_config = sdk2.Resource["NOAPACHEUPPER_CONFIG"].find(state=ctr.State.READY).first()
            Build_config_task = sdk2.Task["BUILD_NOAPACHEUPPER_CONFIG"]  # SDK1-task
            build_config_task = Build_config_task(self, description="Created from SDK2-task",
                                                  new_options_svn_url=self.Parameters.rearrange_data_url,
                                                  sample_config_resource_id=general_config.id).enqueue()
            subtasks["config"] = build_config_task.id

        if not self.Parameters.noapache_data:
            Build_data_task = sdk2.Task["BUILD_NOAPACHEUPPER_DATA"]
            build_data_task = Build_data_task(self, description="Created from SDK2-task",
                                              checkout_arcadia_from_url=self.Parameters.arcadia_url).enqueue()
            subtasks["data"] = build_data_task.id

        if not self.Parameters.noapache_binary:
            Build_noapache_task = sdk2.Task["BUILD_NOAPACHE_UPPER"]  # SDK1-task
            build_noapache_task = Build_noapache_task(self, description="Created from SDK2-task",
                                                      checkout_arcadia_from_url=self.Parameters.arcadia_url).enqueue()
            subtasks["noapache"] = build_noapache_task.id

        # Save ids to context to process them after waking up
        self.Context.subtasks_ids = subtasks

        raise sdk2.WaitTask(list(subtasks.values()), ctt.Status.Group.FINISH, wait_all=True)

    def get_build_values(self):
        params = self.Parameters
        child_tasks = self.Context.subtasks_ids
        logging.info("child_tasks " + str(child_tasks))

        build_values = dict()
        build_values["config"] = params.noapache_config if params.noapache_config else sdk2.Resource[
            "NOAPACHEUPPER_CONFIG"].find(task_id=child_tasks["config"]).first()
        build_values["binary"] = params.noapache_binary if params.noapache_binary else sdk2.Resource[
            "NOAPACHE_UPPER"].find(task_id=child_tasks["noapache"]).first()
        build_values["data"] = params.noapache_data if params.noapache_data else sdk2.Resource[
            "NOAPACHEUPPER_DATA"].find(task_id=child_tasks["data"]).first()

        logging.info(build_values)
        return build_values

    def on_execute(self):
        with self.memoize_stage.create_children:
            self.set_up_parameters_from_arcadia()

        build_values = self.get_build_values()
        wizards = self.set_up_and_use(build_values)

        resource = WizardsResource(self, "My resource", "resource_directory", ttl=30)
        resource_data = sdk2.ResourceData(resource)
        differ.print_to_file(wizards, str(resource_data.path))
        resource_data.ready()
