# -*- coding: utf-8 -*-

import logging

from sandbox import common
from sandbox import sdk2
from sandbox.common.types.client import Tag
from sandbox.projects.vh.frontend.vh_base_test import VhBaseTest
from sandbox.projects.vh.frontend.count_diff import VhFrontendCountDiff
from sandbox.projects.vh.frontend.vh_dolbilka_shooter import VhDolbilkaShooter
import sandbox.common.types.task as ctt


class VhInitTest(VhBaseTest):
    """
        Diff test
    """

    class Requirements(VhBaseTest.Requirements):
        privileged = True
        client_tags = Tag.INTEL_E5_2650 & Tag.LXC & Tag.GENERIC
        execution_space = 10 * 1024
        required_ram = 16 * 1024

    class Parameters(VhBaseTest.Parameters):
        pass

    def compare_shooting_result(self, stable_shooting_result, test_shooting_result, dolbilka_plan_creator_stable, dolbilka_plan_creator_test, raw_requests):
        with self.memoize_stage.compare_shooting_result:
            compare = VhFrontendCountDiff(
                self,
                stable_responses=stable_shooting_result.Parameters.shooting_dump,
                test_responses=test_shooting_result.Parameters.shooting_dump,
                stable_plan_creator=dolbilka_plan_creator_stable,
                test_plan_creator=dolbilka_plan_creator_test
            ).enqueue()
            self.Context.compare_task_id = compare.id
            raise sdk2.WaitTask(
                [compare],
                set(common.utils.chain(ctt.Status.Group.FINISH, ctt.Status.Group.BREAK))
            )
        logging.info("compare_task_id: %s" % self.Context.compare_task_id)
        logging.info(sdk2.Task[self.Context.compare_task_id].Parameters.is_test_success)

        if sdk2.Task[self.Context.compare_task_id].Parameters.is_test_success is False:
            raise common.errors.TaskFailure("Diff is not empty! Check log1/index.html in Count_Diff child task")

    def start_shoot(self, plan_creator, host, port, additional_query_params, prefix, task_name):
        logging.info(task_name)

        shooter = VhDolbilkaShooter(
            self,
            plan_creator=plan_creator,
            additional_query_params=additional_query_params,
            prefix=prefix,
            custom_host=host,
            custom_port=port,
        ).enqueue()

        if task_name == "stable_shooting":
            self.Context.stable_shooting = shooter.id
        else:
            self.Context.test_shooting = shooter.id

        logging.info("shooting_task.id: %s" % shooter.id)

        return shooter
