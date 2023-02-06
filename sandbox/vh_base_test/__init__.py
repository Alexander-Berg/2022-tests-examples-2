# -*- coding: utf-8 -*-

import logging

from sandbox import common
from sandbox import sdk2
from sandbox.common.types.client import Tag
from sandbox.projects.vh.frontend.dolbilka_plan_creator import VhDolbilkaPlanCreator
from sandbox.projects.vh.frontend.generate_requests_from_yt_logs import VhGenerateRequestsFromYt
from sandbox.projects.vh.frontend.vh_dolbilka_shooter import VhDolbilkaShooter
import sandbox.common.types.task as ctt
# from sandbox.projects.vh.frontend import (
#     VH_DOLBILKA_REQUESTS,
#     VhDolbilkaShootingStats
# )


class VhBaseTest(sdk2.Task):
    """
        Base test
    """

    class Requirements(sdk2.Requirements):
        privileged = True
        client_tags = Tag.INTEL_E5_2650 & Tag.LXC & Tag.GENERIC
        execution_space = 10 * 1024
        required_ram = 16 * 1024

    class Parameters(sdk2.Parameters):
        use_prepared_plan = sdk2.parameters.Bool(
            "use_prepared_plan",
            name="use_prepared_plan",
            default=False
        )

        with use_prepared_plan.value[True]:
            stable_plan_creator = sdk2.parameters.Task(
                "Task that created shooting plan for stable stand",
                task_type=VhDolbilkaPlanCreator,
                default="",
                required=True
            )
            test_plan_creator = sdk2.parameters.Task(
                "Task that created shooting plan for test stand",
                task_type=VhDolbilkaPlanCreator,
                default="",
                required=True
            )

        with use_prepared_plan.value[False]:
            with sdk2.parameters.Group("Parameters for requests plan") as planner_params:
                yt_cluster = sdk2.parameters.String(
                    "YT cluster (i.e. hahn)",
                    name="yt_cluster",
                    default="hahn",
                    required=True,
                )
                yt_token_vault = sdk2.parameters.String(
                    "YT_TOKEN vault name",
                    name="yt_token_vault",
                    default="yt_token_for_testenv",
                    required=True,
                )
                request_log_path = sdk2.parameters.String(
                    "Request logs path in YT",
                    name="request_log_path",
                    default="//logs/frontend-vh-balancer-access-log/1d",
                    required=True,
                )
                max_request_number = sdk2.parameters.String(
                    "maximum requests number",
                    name="max_request_number",
                    default="10000"
                )
                yt_logs_limit = sdk2.parameters.String(
                    "number of rows in YT table with logs to read",
                    name="yt_logs_limit",
                    default="1000000"
                )
                handlers_whitelist = sdk2.parameters.List(
                    "handlers from whitelist. If not empty only handlers from whitelist will be shot, handlers should start with /",
                )
                handlers_blacklist = sdk2.parameters.List(
                    "handlers from blacklist will not be shot, handlers should start with /",
                )
                headers = sdk2.parameters.List(
                    "headers for shooting",
                    default="X-region-by-ip: 131028",
                )
                percentage_use_of_headers = sdk2.parameters.Integer(
                    "percentage use of headers for shooting",
                    name="percentage_use_of_headers",
                    default="100",
                )

        with sdk2.parameters.Group("Test stand") as test_stand:
            test_host = sdk2.parameters.String(
                "host for shooting",
                name="host",
                default="localhost",
            )
            test_port = sdk2.parameters.String(
                "port for shooting",
                name="port",
                default="80",
            )
            test_shooting_delay = sdk2.parameters.String(
                "delay of shooting in microseconds",
                name="shooting_delay",
                default="1000",
            )
            test_additional_query_params = sdk2.parameters.List(
                "Additional query params, will be added in every request as &param1&param2",
                default={}
            )
            test_prefix = sdk2.parameters.String(
                "Prefix, will be added in every request",
                default=""
            )

        with sdk2.parameters.Group("Stable stand") as stable_stand:
            stable_host = sdk2.parameters.String(
                "host for shooting",
                name="host",
                default="localhost",
            )
            stable_port = sdk2.parameters.String(
                "port for shooting",
                name="port",
                default="80",
            )
            stable_shooting_delay = sdk2.parameters.String(
                "delay of shooting in microseconds",
                name="shooting_delay",
                default="1000",
            )
            stable_additional_query_params = sdk2.parameters.List(
                "Additional query params, will be added in every request as &param1&param2",
            )
            stable_prefix = sdk2.parameters.String(
                "Prefix, will be added in every request",
                default=""
            )
        # with sdk2.parameters.Output():
        #     test_shooting_requests = sdk2.parameters.Resource(
        #         "test shooting requests",
        #         resource_type=VH_DOLBILKA_REQUESTS,
        #     )
        #     test_shooting_stats = sdk2.parameters.Resource(
        #         "test shooting result",
        #         resource_type=VhDolbilkaShootingStats,
        #     )
        #     stable_shooting_requests = sdk2.parameters.Resource(
        #         "stable shooting requests",
        #         resource_type=VH_DOLBILKA_REQUESTS,
        #     )
        #     stable_shooting_stats = sdk2.parameters.Resource(
        #         "stable shooting result",
        #         resource_type=VhDolbilkaShootingStats,
        #     )

    def on_execute(self):
        raw_requests = None
        dolbilka_plan_creator_stable = None
        dolbilka_plan_creator_test = None
        if self.Parameters.use_prepared_plan is False:
            raw_requests = self.create_raw_requests()

            with self.memoize_stage["dolbilka_plan_creator"]:
                stable_plan_creator = self.create_dolbilka_plan(
                    raw_requests_resource=raw_requests.Parameters.raw_requests,
                    request_number_input=raw_requests.Parameters.request_number,
                    host=self.Parameters.stable_host,
                    port=self.Parameters.stable_port,
                    additional_query_params=self.Parameters.stable_additional_query_params,
                    prefix=self.Parameters.stable_prefix,
                    task_name="dolbilka_plan_creator_stable")

                test_plan_creator = self.create_dolbilka_plan(
                    raw_requests_resource=raw_requests.Parameters.raw_requests,
                    request_number_input=raw_requests.Parameters.request_number,
                    host=self.Parameters.test_host,
                    port=self.Parameters.test_port,
                    additional_query_params=self.Parameters.test_additional_query_params,
                    prefix=self.Parameters.test_prefix,
                    task_name="dolbilka_plan_creator_test")

                raise sdk2.WaitTask(
                    [stable_plan_creator, test_plan_creator],
                    set(common.utils.chain(ctt.Status.Group.FINISH, ctt.Status.Group.BREAK))
                )

            dolbilka_plan_creator_stable = sdk2.Task[self.Context.dolbilka_plan_creator_stable]
            dolbilka_plan_creator_test = sdk2.Task[self.Context.dolbilka_plan_creator_test]
        else:
            dolbilka_plan_creator_stable = self.Parameters.stable_plan_creator
            dolbilka_plan_creator_test = self.Parameters.test_plan_creator

        with self.memoize_stage["shooting"]:
            stable_shooting = self.start_shoot(
                plan_creator=dolbilka_plan_creator_stable,
                host=self.Parameters.stable_host,
                port=self.Parameters.stable_port,
                additional_query_params=self.Parameters.stable_additional_query_params,
                prefix=self.Parameters.stable_prefix,
                task_name="stable_shooting")

            test_shooting = self.start_shoot(
                plan_creator=dolbilka_plan_creator_test,
                host=self.Parameters.test_host,
                port=self.Parameters.test_port,
                additional_query_params=self.Parameters.test_additional_query_params,
                prefix=self.Parameters.test_prefix,
                task_name="test_shooting")

            raise sdk2.WaitTask(
                [stable_shooting, test_shooting],
                set(common.utils.chain(ctt.Status.Group.FINISH, ctt.Status.Group.BREAK))
            )

        stable_shooting_result = sdk2.Task[self.Context.stable_shooting]
        logging.info("stable_shooting_result id: ")
        logging.info(stable_shooting_result.id)

        test_shooting_result = sdk2.Task[self.Context.test_shooting]
        logging.info("test_shooting_result id: ")
        logging.info(test_shooting_result.id)

        self.compare_shooting_result(stable_shooting_result, test_shooting_result, dolbilka_plan_creator_stable, dolbilka_plan_creator_test, raw_requests)

    def create_raw_requests(self):
        with self.memoize_stage.create_child_raw_requests:
            requests_generator = VhGenerateRequestsFromYt(
                self,
                yt_cluster=self.Parameters.yt_cluster,
                yt_token_vault=self.Parameters.yt_token_vault,
                request_log_path=self.Parameters.request_log_path,
                max_request_number=self.Parameters.max_request_number,
                yt_logs_limit=self.Parameters.yt_logs_limit,
                handlers_whitelist=self.Parameters.handlers_whitelist,
                handlers_blacklist=self.Parameters.handlers_blacklist,
                headers=self.Parameters.headers,
                percentage_use_of_headers=self.Parameters.percentage_use_of_headers
            ).enqueue()
            self.Context.requests_generator_task_id = requests_generator.id
            raise sdk2.WaitTask(
                [requests_generator],
                set(common.utils.chain(ctt.Status.Group.FINISH, ctt.Status.Group.BREAK))
            )
        logging.info("requests_generator.id: %s" % self.Context.requests_generator_task_id)
        self.Context.request_number = sdk2.Task[self.Context.requests_generator_task_id].Parameters.request_number
        return sdk2.Task[self.Context.requests_generator_task_id]

    def create_dolbilka_plan(self, raw_requests_resource, request_number_input, host, port, additional_query_params, prefix, task_name):
        plan_creator = VhDolbilkaPlanCreator(
            self,
            should_generate_requests=False,
            raw_requests=raw_requests_resource,
            request_number_input=request_number_input,
            host=host,
            port=port,
            additional_query_params=additional_query_params,
            prefix=prefix,
        ).enqueue()

        if task_name == "dolbilka_plan_creator_stable":
            self.Context.dolbilka_plan_creator_stable = plan_creator.id
        else:
            self.Context.dolbilka_plan_creator_test = plan_creator.id

        logging.info("plan_creator.id: %s" % plan_creator.id)

        return plan_creator

    def start_shoot(self, plan_creator, host, port, additional_query_params, prefix, task_name):
        logging.info(task_name)

        shooter = VhDolbilkaShooter(
            self,
            plan_creator=plan_creator,
            additional_query_params=additional_query_params,
            prefix=prefix,
            custom_host=host,
            custom_port=port
        ).enqueue()

        if task_name == "stable_shooting":
            self.Context.stable_shooting = shooter.id
        else:
            self.Context.test_shooting = shooter.id

        logging.info("shooting_task.id: %s" % shooter.id)

        return shooter

    def compare_shooting_result(self, stable_shooting_result, test_shooting_result, dolbilka_plan_creator_stable, dolbilka_plan_creator_test, raw_requests):
        logging.info("Start compare_shooting_result in base class")
        pass
