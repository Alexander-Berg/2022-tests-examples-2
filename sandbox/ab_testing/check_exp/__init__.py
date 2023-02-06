from __future__ import division

import logging
import itertools
import os
import six
import time

from sandbox import sdk2
import sandbox.common.errors as cerr
import sandbox.common.types.resource as ctr

from sandbox.projects import resource_types
from sandbox.projects.common import binary_task
from sandbox.projects.common import decorators
from sandbox.projects.common import gsid_parser
from sandbox.projects.common import link_builder as lb
from sandbox.projects.common import error_handlers as eh
from sandbox.projects.common import utils
from sandbox.projects.common import task_env
from sandbox.projects.common.search import bugbanner2 as bb2
from sandbox.projects.release_machine import input_params2 as rm_params
from sandbox.projects.release_machine.components.configs.ab_experiments import AbExperimentsCfg
from sandbox.projects.release_machine.helpers import soy_helper
from sandbox.projects.release_machine.tasks import base_task as rm_bt
from sandbox.projects.release_machine.tasks.ScrapeRequests2 import scraper_over_yt as soy


class CheckExp(rm_bt.BaseReleaseMachineTask):
    class Requirements(task_env.TinyRequirements):
        ram = 63 * 1024  # 63 Gb
        disk_space = 75 * 1024  # 75 Gb
        cores = 16

    class Parameters(rm_params.ComponentName2):
        _lbrp = binary_task.binary_release_parameters(stable=True)
        kill_timeout = 5 * 60 * 60  # 5 hours
        new_cgi_param = sdk2.parameters.String("New cgi params (must be encoded)")
        scraper_pool = sdk2.parameters.String("Scraper pool name", default_value="default")
        yt_server = sdk2.parameters.String("YT server", default_value="arnold")
        number_of_queries = sdk2.parameters.Integer("Number of queries (< 2000)", default_value=300)
        with sdk2.parameters.String("Port type") as daemon_port_type:
            daemon_port_type.values.auto = daemon_port_type.Value(value="auto", default=True)
            daemon_port_type.values.grpc = daemon_port_type.Value(value="grpc")
            daemon_port_type.values.apphost = daemon_port_type.Value(value="apphost")
            daemon_port_type.values.http = daemon_port_type.Value(value="http")
        ab_experiment_id = sdk2.parameters.String("AB Experiment ID (for A/B Adminka-spawned jobs)", default="")

    def on_execute(self):
        rm_bt.BaseReleaseMachineTask.on_execute(self)
        self.add_bugbanner(bb2.Banners.UPS)
        with self.memoize_stage.send_start_task_event:
            self.send_rm_proto_event()

        if self.Parameters.component_name == AbExperimentsCfg.name and not self.Parameters.new_cgi_param:
            self.set_info("No cgi param specified. Nothing to check")
            return

        if self.Context.soy_id:  # RMDEV-1504
            existing_batch_info = self._get_existing_batch_info()

            status = existing_batch_info[0] if existing_batch_info else "UNKNOWN"

            logging.info(
                "Existing (previous) batch info: %s. Going to re-launch SOY batch since we cannot trust"
                "previous launch",
                existing_batch_info,
            )

            self.set_info(
                "Task has been restarted. "
                "We cannot trust previous launch so we're going to restart everything (RMDEV-2252). "
                "Previous SOY batch ID: {}, status: {}".format(self.Context.soy_id, status)
            )

            # RMDEV-2252
            self.Context.soy_id = None
            self.Context.save()

        queries = self.prepare_queries()
        daemon = self.init_daemon()
        os.environ["YT_TOKEN"] = self._yt_token
        os.environ["SOY_TOKEN"] = self._soy_token

        # This try-except block is a workaround UPS-111
        with self.memoize_stage.try_to_run(3):
            try:

                with daemon:
                    self.run_soy(daemon, queries)
                    event_log = resource_types.EVENTLOG_DUMP(self, "Event log", daemon.eventlog_path)
                    sdk2.ResourceData(event_log).ready()
                return

            except Exception as e:
                if "Failed to connect to endpoints" in str(e):
                    raise cerr.TemporaryError(str(e))
                raise  # re-throw all other exceptions
        raise cerr.TaskFailure("Failed to connect to endpoints")

    @decorators.memoized_property
    def _yt_token(self):
        return sdk2.Vault.data("SEARCH-RELEASERS", "yt_token")

    @decorators.memoized_property
    def _soy_token(self):
        return sdk2.Vault.data("EXPERIMENTS", "soy_token")

    def _prepare_resource(self, resource_id):
        resource = sdk2.Resource[resource_id]
        self.set_info("Got {}".format(resource))
        return resource

    def _get_existing_batch_info(self):
        try:
            return soy.ScraperOverYtWrapper.get_batch_status_via_api(self.Parameters.yt_server, self.Context.soy_id)
        except Exception:
            self.set_info("No batch found in SOY with id '{}'. Will retry once again".format(self.Context.soy_id))

    def prepare_queries(self):
        queries_resource = self.server.resource.read(
            type=resource_types.USERS_QUERIES.name,
            state=ctr.State.READY,
            attrs={
                "random_requests": "2000",
            },
            limit=1,
        )["items"]
        if not queries_resource:
            raise cerr.TaskError("Resource with users queries not found")
        queries_resource_path = str(sdk2.ResourceData(sdk2.Resource[queries_resource[0]["id"]]).path)
        queries = itertools.islice(
            utils.yield_user_queries(queries_resource_path),
            int(self.Parameters.number_of_queries)
        )
        return [i[0:2] for i in queries]

    def init_daemon(self):
        raise NotImplementedError

    def get_host(self):
        raise NotImplementedError

    def create_batch_id(self):
        raise NotImplementedError

    def run_soy(self, daemon, queries):
        cgi = self._get_additional_cgi_params(daemon)
        # extremely useful logging, please do not delete
        logging.info('Additional cgi params: `%s`', cgi)

        soy_queries = soy.ScraperOverYtWrapper.get_queries(
            queries_list=queries,
            host=self.get_host(),
            platform="search",
            cgi=cgi,
            id_prefix="id",
            region_prefix="reg",
            uids=None,
        )
        batch_id = self.Context.soy_id = self.create_batch_id()
        self.Context.save()
        input_table = "//tmp/check_exp/{}".format(batch_id)
        try:
            soy.ScraperOverYtWrapper.launch_scraper(
                soy_queries,
                server=self.Parameters.yt_server,
                input_table=input_table,
                guid=batch_id,
                pool=self.Parameters.scraper_pool,
                use_api=True,
            )
        except Exception as e:
            raise cerr.TemporaryError("Failed to create batch: {}".format(e))
        self.set_info("Launched SoY batch: {}".format(batch_id))
        self.wait_batch(batch_id)

    def wait_batch(self, batch_id):
        start_time = time.time()
        sleep_time_sec = 60
        for checks_count in itertools.count():
            try:
                delay = time.time() - start_time
                status, status_api_response = soy.ScraperOverYtWrapper.get_batch_status_via_api(
                    self.Parameters.yt_server, batch_id
                )
                logging.info("%s seconds of active waiting, got status %s", delay, status)
                if (checks_count * sleep_time_sec) % 600 == 0:  # print status every 10 minutes
                    soy_status = soy_helper.SOY_API.format(self.Parameters.yt_server) + "status?id={}".format(batch_id)
                    self.set_info(
                        "Current status: {}".format(
                            lb.HREF_TO_ITEM.format(link=soy_status, name=soy.BatchStatus.STATUS_NAME[status])
                        ),
                        do_escape=False
                    )
                eh.verify(status != soy.BatchStatus.FAILED, "Soy batch failed to download")
                if status == soy.BatchStatus.COMPLETED:
                    self._show_batch_results(status_api_response)
                    self._check_batch_results(status_api_response)
                    return
            except cerr.SandboxException as e:
                raise e
            except Exception as e:
                logging.exception(e)
            time.sleep(sleep_time_sec)

    def _check_batch_results(self, status_info):
        import yt.wrapper as yt
        error_percent_threshold = 10
        yt_client = yt.YtClient(self.Parameters.yt_server, self._yt_token)
        error_count = yt.row_count(status_info["error_path"], yt_client)
        error_percent = 100.0 * error_count / self.Parameters.number_of_queries
        self.set_info("Errors: {}%".format(error_percent))
        if error_percent > error_percent_threshold:
            eh.check_failed("Too much errors found: {}% > {}%".format(error_percent, error_percent_threshold))

    def _show_batch_results(self, status_info):
        url_to_results = "https://yt.yandex-team.ru/{}/navigation?path={}".format(
            self.Parameters.yt_server, status_info["output_path"]
        )
        self.set_info(lb.HREF_TO_ITEM.format(link=url_to_results, name="Results"), do_escape=False)

    def _get_additional_cgi_params(self, daemon):
        raise NotImplementedError

    def _get_auto_port(self, daemon):
        raise NotImplementedError

    def _get_port(self, daemon):
        mapping = {
            "grpc": daemon.grpc_port,
            "apphost": daemon.apphost_port,
            "http": daemon.port,
            "auto": self._get_auto_port(daemon),
        }
        return mapping[self.Parameters.daemon_port_type]

    def on_break(self, *args, **kwargs):
        self._abort_batch()
        rm_bt.BaseReleaseMachineTask.on_break(self, *args, **kwargs)

    def on_failure(self, prev_status):
        self._abort_batch()
        super(CheckExp, self).on_failure(prev_status)

    def on_terminate(self):
        self._abort_batch()
        super(CheckExp, self).on_terminate()

    def _abort_batch(self):
        if self.Context.soy_id:
            logging.info("Task is broken, aborting soy batch: {}".format(self.Context.soy_id))
            soy_api = soy_helper.SoyApi(token=self._soy_token, server=self.Parameters.yt_server)
            res = soy_api.abort(self.Context.soy_id)
            logging.info("Abortion status: {}".format(res.get("status")))
            if "error_msg" in res:
                logging.error(res["error_msg"])

    def _get_rm_proto_event_specific_data(self, rm_proto_events, event_time_utc_iso, status=None):

        if self.is_ci_launch and self.ci_context:
            scope_number = self.ci_context.launch_number
            revision = self.ci_context.target_commit.revision.hash
        else:
            revision = gsid_parser.get_svn_revision_from_gsid(self.Context.__values__.get("__GSID"))
            scope_number = revision

        job_name = self.job_name

        if not scope_number or not job_name:
            return {}

        from release_machine.common_proto import test_results_pb2 as rm_test_results

        status = status or self.status
        test_result = rm_test_results.TestResult.TestStatus.ONGOING
        if status == "SUCCESS":
            test_result = rm_test_results.TestResult.TestStatus.OK
        elif status in frozenset(["FAILURE", "TIMEOUT", "EXCEPTION"]):
            test_result = rm_test_results.TestResult.TestStatus.CRIT
        elif status in frozenset(["STOPPED"]):
            test_result = rm_test_results.TestResult.TestStatus.UB
        return {
            "acceptance_test_data": rm_proto_events.AcceptanceTestData(
                acceptance_type=rm_proto_events.AcceptanceTestData.AcceptanceType.UNDEFINED,
                job_name=job_name,
                revision=six.text_type(revision or ""),
                scope_number=six.text_type(scope_number or ""),
                experiment_id=self.Parameters.ab_experiment_id,
                test_result=rm_test_results.TestResult(
                    status=test_result,
                    task_link=lb.task_link(self.id, plain=True),
                ),
            ),
        }
