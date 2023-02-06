import json
import logging

from sandbox.common import rest
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk import sandboxapi

from sandbox.projects.common import link_builder as lb
from sandbox.projects.common import utils
from sandbox.projects.common.search import bugbanner
from sandbox.projects.common.search.components import DefaultBasesearchParams
from sandbox.projects import GenerateSlowPlan as gsp
from sandbox.projects.websearch.basesearch import TestBasesearchPerformanceTank as tbpt


class ProfileBinary(DefaultBasesearchParams.Binary):
    description = "Binary to profile"


class TestBasesearchPerformanceSlow(bugbanner.BugBannerTask):
    type = "TEST_BASESEARCH_PERFORMANCE_SLOW"
    execution_space = 2 * 1024  # 2 Gb

    input_parameters = (ProfileBinary,) + gsp.GenerateSlowPlan.input_parameters

    @property
    def footer(self):
        client = rest.Client()
        get_plan_task_id = self.ctx.get("get_slow_plan_task_id")
        shoot_task_id = self.ctx.get("shoot_slow_plan_task_id")
        foot = []
        if get_plan_task_id:
            stats_res = channel.sandbox.get_resource(client.task[get_plan_task_id].context.read()["stats_res_id"])
            foot.append({
                'helperName': '',
                'content': "<h3>Slow queries: {}</h3>".format(
                    lb.HREF_TO_ITEM.format(
                        link=stats_res.proxy_url + "/total_stats.html",
                        name=stats_res.id,
                    )
                )
            })
        if shoot_task_id:
            foot.extend(client.task[shoot_task_id].custom.footer.read())
        return foot

    def on_execute(self):
        if "get_slow_plan_task_id" not in self.ctx:
            self.add_bugbanner(bugbanner.Banners.SearchTests)
            self.get_slow_plan()
        else:
            self.shoot_slow_plan()
            utils.check_subtasks_fails(fail_on_first_failure=True)

    def get_slow_plan(self):
        if "get_slow_plan_task_id" in self.ctx:
            logging.info("Task with slow plan already exists: %s", self.ctx["get_slow_plan_task_id"])
            return
        get_slow_plan_params = {
            "task_type": "GENERATE_SLOW_PLAN",
            "input_parameters": {
                "notify_via": "",
                gsp.PerformanceTask.name: self.ctx[gsp.PerformanceTask.name],
                gsp.NumSlow.name: self.ctx[gsp.NumSlow.name],
                gsp.Detailed.name: self.ctx[gsp.Detailed.name],
            },
            "description": "Get slow plan, {}".format(self.descr),
            "arch": sandboxapi.ARCH_LINUX,
        }
        logging.info("Get slow plan using subtask:\n%s", json.dumps(get_slow_plan_params))
        self.ctx["get_slow_plan_task_id"] = self.create_subtask(**get_slow_plan_params).id
        utils.wait_all_subtasks_stop()

    def shoot_slow_plan(self):
        if "shoot_slow_plan_task_id" in self.ctx:
            logging.info("Shoot task already exists: %s", self.ctx["shoot_slow_plan_task_id"])
            return
        shoot_slow_plan_params = {
            "task_type": "TEST_BASESEARCH_PERFORMANCE_TANK",
            "input_parameters": self._fill_shoot_params(),
            "description": "Shoot slow plan, {}".format(self.descr),
            "arch": sandboxapi.ARCH_LINUX,
        }
        logging.info("Shoot slow plan using subtask:\n%s", json.dumps(shoot_slow_plan_params))
        self.ctx["shoot_slow_plan_task_id"] = self.create_subtask(**shoot_slow_plan_params).id

    def _fill_shoot_params(self):
        perf_task = channel.sandbox.get_task(self.ctx[gsp.PerformanceTask.name])
        if perf_task.type == "TEST_BASESEARCH_PERFORMANCE_BEST":
            # choose last child in umbrella task
            perf_task = sorted(channel.sandbox.list_tasks(parent_id=perf_task.id), reverse=True)[0]
        slow_plan_task = channel.sandbox.get_task(self.ctx["get_slow_plan_task_id"])
        params = {p.name: perf_task.ctx.get(p.name) for p in tbpt.TestBasesearchPerformanceTank.input_parameters}
        params.update({
            "notify_via": "",
            "basesearch_executable_resource_id": self.ctx.get(ProfileBinary.name),
            "dolbilka_executor_sessions": 3,
            "dolbilo_plan_resource_id": slow_plan_task.ctx[gsp.OUT_PLAN_RES_ID],
            "profiling_type": "on_cpu",
            # slow requests are really slow, 100k leads to 3h-timeout
            "dolbilka_executor_requests_limit": 25000,

            # Slow requests are chosen from very small set, and some of them can produce errors sometimes.
            # It is another question why erroneous request is slow, maybe should be investigated.
            "fail_rate_threshold": 0.3,
        })
        return params


__Task__ = TestBasesearchPerformanceSlow
