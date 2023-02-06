import textwrap

from sandbox import sdk2
import sandbox.common.types.resource as ctr
from sandbox.sandboxsdk import environments

from sandbox.projects.common import binary_task
from sandbox.projects.resource_types import CACHE_DAEMON
from sandbox.projects.common.dolbilka.resources import DPLANNER_EXECUTABLE

from sandbox.projects.yql.RunYQL2 import RunYQL2
from sandbox.projects.yabs.qa.tasks.BuildAmmoAndStubsFromYT import BuildAmmoAndStubsFromYT, GenAmmoAndStubFromYtBinary

from sandbox.projects.common.yabs.server.util.general import check_tasks, try_get_from_vault

import queries


DEFAULT_NAME = "hit_models"
DEFAULT_LIMITS = [
    {
        "name": DEFAULT_NAME,
        "handler": {
            "lower": {
                "RANDOM": 1000,
                "OTHER": 0,
            },
            "upper": {},
        },
    }
]


class YabsHitModelsGetYtRequestData(sdk2.Task, binary_task.LastBinaryTaskRelease):
    class Requirements(sdk2.Task.Requirements):
        environments = (environments.PipEnvironment("yandex-yt"),)

    class Parameters(sdk2.Parameters):
        description = "Generate hit models service ammo from bs-proto-extstat-log"
        max_restarts = 3
        kill_timeout = 60 * 60 * 1

        gen_ammo_and_stub_from_yt_binary = sdk2.parameters.LastReleasedResource(
            "Stub and ammo generator binary",
            resource_type=GenAmmoAndStubFromYtBinary,
            state=(ctr.State.READY, ctr.State.NOT_READY),
            required=True,
        )

        cache_daemon_resource = sdk2.parameters.LastReleasedResource(
            "Cache daemon binary",
            resource_type=CACHE_DAEMON,
            state=(ctr.State.READY, ctr.State.NOT_READY),
            required=True,
        )

        d_planner_resource = sdk2.parameters.LastReleasedResource(
            "Dolbilka planner binary",
            resource_type=DPLANNER_EXECUTABLE,
            state=(ctr.State.READY, ctr.State.NOT_READY),
            required=True,
        )

        testenv_switch_trigger = sdk2.parameters.Bool("Switch Testenv to generated resources", default=False)

        spec = sdk2.parameters.JSON("Spec with limits and names of different ammo", default=DEFAULT_LIMITS)

        user_subquery_example = textwrap.dedent(
            """
            SELECT ... as GraphID FROM RANGE("table/prefix/", $begin, $end) ...;
        """
        )
        user_subquery_description = "Custom subquery for limiting request ids. Example: \n" + user_subquery_example
        user_subquery = sdk2.parameters.String(user_subquery_description)

        yt_token_vault_name = sdk2.parameters.String("Vault name to get YT token from", default="yt-token")
        yql_token_vault_name = sdk2.parameters.String(
            "Vault name to get YQL token from", default="yql-token"
        )
        logs_interval_type = sdk2.parameters.String("Logs interval type: 1d or 1h", default="1h", required=True)
        interval_size = sdk2.parameters.Integer(
            "Number of intervals (1d or 1h) used to get requests", default=3, required=True
        )

        with sdk2.parameters.Output:
            result_spec = sdk2.parameters.JSON("Output generated ammo spec", default={})

    class Context(sdk2.Context):
        aggregation_subtask_id = None
        select_subtask_ids = None
        resource_generation_subtask_id = None

    def on_execute(self):
        yt_work_prefix = "//tmp/aleosi/{}".format(self.id)

        if self.Context.aggregation_subtask_id is None:
            query = queries.make_aggregation_query(
                work_prefix=yt_work_prefix,
                user_subquery=self.Parameters.user_subquery,
                logs_interval_type=self.Parameters.logs_interval_type,
                interval_size=self.Parameters.interval_size,
            )
            self.Context.aggregation_subtask_id = self.launch_run_yql2(query, 15, "aggregation")

        if self.Context.select_subtask_ids is None:
            check_tasks(self, [self.Context.aggregation_subtask_id])

            self.Context.select_subtask_ids = []
            for limit_spec in self.Parameters.spec:
                name = limit_spec.get("name", DEFAULT_NAME)
                query = queries.make_select_query(
                    work_prefix=yt_work_prefix,
                    handler_limits=limit_spec.get("handler", {}).get("lower", {}),
                    logs_interval_type=self.Parameters.logs_interval_type,
                    had_user_subquery=bool(self.Parameters.user_subquery),
                    output_suffix="_{}".format(name),
                )
                self.Context.select_subtask_ids.append(self.launch_run_yql2(query, 180, "select_{}".format(name)))

        if self.Context.resource_generation_subtask_id is None:
            check_tasks(self, self.Context.select_subtask_ids)

            spec = {
                limit_spec.get("name", DEFAULT_NAME): {
                    "make_load": False,
                    "limits": [
                        {"lower": {k: int(v) for k, v in limit_spec.get("handler", {}).get("lower", {}).iteritems()}},
                        {"upper": {k: int(v) for k, v in limit_spec.get("handler", {}).get("upper", {}).iteritems()}},
                    ],
                }
                for limit_spec in self.Parameters.spec
            }

            input_tables = {
                limit_spec.get("name", DEFAULT_NAME): [
                    yt_work_prefix + "/output_{}".format(limit_spec.get("name", DEFAULT_NAME)),
                ]
                for limit_spec in self.Parameters.spec
            }
            self.set_tables_attrs(input_tables)

            print "YtWorkPrefix", yt_work_prefix
            resource_generation_subtask = BuildAmmoAndStubsFromYT(
                self,
                description="Hit models service ammo generation",
                gen_ammo_and_stub_from_yt_binary=self.Parameters.gen_ammo_and_stub_from_yt_binary,
                cache_daemon_resource=self.Parameters.cache_daemon_resource,
                d_planner_resource=self.Parameters.d_planner_resource,
                input_tables=input_tables,
                spec=spec,
                yt_token_vault_name=self.Parameters.yt_token_vault_name,
                yt_work_prefix=yt_work_prefix,
                legacy_mode=False,
                testenv_switch_trigger=self.Parameters.testenv_switch_trigger,
            )
            resource_generation_subtask.enqueue()
            self.Context.resource_generation_subtask_id = resource_generation_subtask.id

        check_tasks(self, [self.Context.resource_generation_subtask_id])

        result_spec = sdk2.Task[self.Context.resource_generation_subtask_id].Parameters.result_spec
        self.Parameters.result_spec = result_spec

    def launch_run_yql2(self, query, retry_period, subdescr):
        subtask = RunYQL2(
            self,
            description="Hit models ammo generation: {}".format(subdescr),
            query=query,
            yql_token_vault_name=self.Parameters.yql_token_vault_name,
            trace_query=True,
            retry_period=retry_period,
            publish_query=True,
            use_v1_syntax=True,
        )
        subtask.enqueue()
        return subtask.id

    def set_tables_attrs(self, input_tables):
        import yt.wrapper as yt

        yt.config["token"] = try_get_from_vault(self, self.Parameters.yt_token_vault_name)
        yt.config["proxy"]["url"] = "hahn"
        for table_list in input_tables.itervalues():
            for table_path in table_list:
                yt.set(table_path + "/@request_key_headers", ["X-Yabs-HitModels-Req-Id"])
                yt.set(table_path + "/@cachedaemon_key_headers", ["X-Yabs-HitModels-Req-Id"])
