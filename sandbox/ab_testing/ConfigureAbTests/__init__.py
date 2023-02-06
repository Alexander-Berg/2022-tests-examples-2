# -*- coding: utf-8 -*-

import logging
import os
import six
import yaml

from sandbox import sdk2
from sandbox.projects.common import binary_task
from sandbox.projects.common import error_handlers as eh
from sandbox.projects.common import link_builder as lb
from sandbox.projects.common import gsid_parser
from sandbox.projects.common.decorators import memoized_property as cached_property
from sandbox.projects.release_machine import input_params2 as rm_params
import sandbox.projects.release_machine.components.all as rmc
import sandbox.projects.release_machine.core.task_env as task_env
import sandbox.projects.release_machine.tasks.base_task as rm_bt


class WebMiddleParameters(sdk2.Task.Parameters):
    web__middle__block = sdk2.parameters.Info("Web Middle")
    web__middle__save_eventlog = sdk2.parameters.Bool("Middle save event log", default_value=True)
    web__middle__scraper_pool = sdk2.parameters.String("Middle SOY pool")
    web__middle__new_cgi_param = sdk2.parameters.String("Middle new cgi param")


class WebUpperParameters(sdk2.Task.Parameters):
    web__upper__block = sdk2.parameters.Info("Web Upper")
    web__upper__save_eventlog = sdk2.parameters.Bool("Upper save event log", default_value=True)
    web__upper__scraper_pool = sdk2.parameters.String("Upper SOY pool")
    web__upper__new_cgi_param = sdk2.parameters.String("Upper new cgi param")


class WebTestWebRunnerParameters(sdk2.Task.Parameters):
    web__runner__block = sdk2.parameters.Info("Web Runner")
    web__runner__prod_description = sdk2.parameters.String(
        "AbDeployingTestWeb4ExperimentsReleaseProdProdRunner task description"
    )
    web__runner__dev_description = sdk2.parameters.String(
        "AbDeployingTestWeb4ExperimentsReleaseDevDevRunner task description"
    )
    web__runner__run_flags_mode = sdk2.parameters.Bool(
        "Flag to run task SandboxCiWeb4ExperimentsReleaseRunner",
        default_value=False,
    )


class WebTestAssessorsParameters(sdk2.Task.Parameters):
    web__test_assessors__block = sdk2.parameters.Info("Web TestAssessors")
    web__test_assessors__testpalm_project_suffix = sdk2.parameters.String("TestPalm project suffix")
    web__test_assessors__build_artifacts_resources = sdk2.parameters.Resource("Build artifacts")
    web__test_assessors__test_assesssors_description = sdk2.parameters.String("TestAssessors task description")
    web__test_assessors__run_flags_mode = sdk2.parameters.Bool(
        "Flag to run task SandboxCiTestpalmSuiteRunner",
        default_value=False,
    )


class MetricsParameters(sdk2.Parameters):
    with sdk2.parameters.Group("{group_name}") as group:
        with sdk2.parameters.Group("Metrics") as group_metrics:
            metrics__description = sdk2.parameters.String(
                "LaunchMetrics task description",
            )
            metrics__custom_template_name = sdk2.parameters.String(
                "Metrics template", default_value="experiments.json",
            )
            metrics__scraper_over_yt_pool = sdk2.parameters.String(
                "Metrics SOY pool", default_value="default",
            )
            metrics__sample_beta = sdk2.parameters.String(
                "Sample beta", default_value="hamster",
            )
            metrics__checked_beta = sdk2.parameters.String(
                "Checked beta", default_value="hamster",
            )
            metrics__checked_extra_params = sdk2.parameters.String("Metrics new cgi param")
            metrics__search_subtype = sdk2.parameters.String("Images search subtype")
            metrics__optimistic_expected_launch_time_sec = sdk2.parameters.Integer(
                "Expected optimistic launch time", default_value=2400,  # 40 min
            )
            metrics__enable_autoclicker = sdk2.parameters.Bool(
                "Enable autoclicker", default_value=True,
            )
            metrics__autoclicker_retry_count = sdk2.parameters.Integer(
                "Autoclicker retries", default_value=3,
            )
            metrics__autoclicker_metric_name = sdk2.parameters.String(
                "Autoclicker metric name",
            )


class FijiExperimentsParameters(sdk2.Parameters):
    with sdk2.parameters.Group("{group_name}") as vertical_group:
        with sdk2.parameters.Group("FijiExperiments") as group_fiji_experiments:
            fiji_experiments__description = sdk2.parameters.String(
                "AbDeployingTestFijiExperimentsRelease{group_name}Runner task description"
            )
            fiji_experiments__release = sdk2.parameters.String(
                'Ветка, из которой нужно брать шаблоны',
                default='latest',
            )
            fiji_experiments__tests_source = sdk2.parameters.String(
                'Ветка, из которой нужно брать тесты',
                default='nothing',
            )
            fiji_experiments__platforms = sdk2.parameters.List(u'Платформы')
            fiji_experiments__service = sdk2.parameters.String(u'Сервис')
            fiji_experiments__hermionee2e_base_url = sdk2.parameters.String('Hermione e2e base url')
            fiji_experiments__run_flags_mode = sdk2.parameters.Bool(
                "Flag to run task SandboxCiFijiExperimentsReleaseRunner",
                default_value=False,
            )


WebMetricsParameters = MetricsParameters(prefix="web__", label_substs={"group_name": "Web"})
ImagesMetricsParameters = MetricsParameters(prefix="images__", label_substs={"group_name": "Images"})
VideoMetricsParameters = MetricsParameters(prefix="video__", label_substs={"group_name": "Video"})
ImagesFijiExperimentsParameters = FijiExperimentsParameters(prefix="images__", label_substs={"group_name": "Images"})
VideoFijiExperimentsParameters = FijiExperimentsParameters(prefix="video__", label_substs={"group_name": "Video"})


class MarketParameters(sdk2.Task.Parameters):
    market__report_lite_tests_exp__block = sdk2.parameters.Info("Market")
    market__report_lite_tests_exp__run_tests = sdk2.parameters.Bool("Run tests", default_value=False)
    market__report_lite_tests_exp__rearr_factors = sdk2.parameters.String("Rearr factors")


class AliceParameters(sdk2.Task.Parameters):
    alice__block = sdk2.parameters.Info("Alice")
    alice__dry_run = sdk2.parameters.Bool("Dry run", default_value=True)
    alice__experiment_flags = sdk2.parameters.String("Experiment flags")
    alice__launch_type = sdk2.parameters.String("Launch type")


class ZenParameters(sdk2.Task.Parameters):
    zen__block = sdk2.parameters.Info("Zen")
    zen__experiment_flags = sdk2.parameters.Dict("Experiment flags", default={}, required=True)
    zen__skip_test = sdk2.parameters.Bool("Skip test", default_value=True)


class BigBMainParameters(sdk2.Task.Parameters):
    bigb_main__block = sdk2.parameters.Info("BigB Main")
    bigb_main__dry_run = sdk2.parameters.Bool("Dry run", default_value=True)
    bigb_main__ab_experiment_settings = sdk2.parameters.JSON('AB experiment settings', default_value={})
    bigb_main__ft_meta_modes = sdk2.parameters.List('ft_meta_modes')


class ConfigureAbTests(rm_bt.BaseReleaseMachineTask):
    class Requirements(task_env.TinyRequirements):
        pass

    class Parameters(rm_params.DefaultReleaseMachineParameters):
        kill_timeout = 15 * 60  # 15 min
        _lbrp = binary_task.binary_release_parameters(stable=True)
        test_id_revision = sdk2.parameters.Integer("Revision of committed test-id")
        send_event_data = sdk2.parameters.Bool("Send TicketHistory event")

        with sdk2.parameters.Output:
            experiment_id = sdk2.parameters.String("Experiment id", default_value=0)
            testid = sdk2.parameters.Integer("Testid", default_value=0)
            flagsjson_id = sdk2.parameters.Integer("Flags.json id", default_value=0)
            ups_responsible = sdk2.parameters.String("UPS responsible (duty)")

    class Context(rm_bt.BaseReleaseMachineTask.Context):
        pass

    @cached_property
    def c_info(self):
        return rmc.get_component(self.Parameters.component_name)

    @cached_property
    def exp_config(self):

        try:

            from sandbox.projects.ab_testing.ConfigureAbTests import utils as ab_test_config_utils

            return ab_test_config_utils.get_experiment_config(
                commit_id=self.Parameters.test_id_revision,
            )

        except ImportError as ie:
            eh.log_exception(
                "Cannot load ConfigureAbTests.utils. Are running the task right? Please use binary task launch",
                ie,
            )

        except Exception as e:
            eh.log_exception("New config loading logic failed", e)

        logging.info("Going to fall back to the old config loading logic")

        return self.get_config_of_experiment()

    @cached_property
    def ups_responsible(self):
        return self.c_info.get_responsible_for_component()

    def on_execute(self):
        rm_bt.BaseReleaseMachineTask.on_execute(self)

    def get_config_of_experiment(self):
        test_ids_info = sdk2.svn.Arcadia.log(
            self.c_info.svn_cfg__main_url,
            revision_from=self.Parameters.test_id_revision,
            revision_to=self.Parameters.test_id_revision,
            limit=1,
        )[0]
        # filter folders creation and other not related changes
        yaml_paths = [p for _, p in test_ids_info["paths"] if p.endswith(".yaml")]
        if len(yaml_paths) != 1:
            eh.check_failed("Required only one path for revision log. Got {}:\n{}".format(len(yaml_paths), yaml_paths))
        path = yaml_paths[0]
        local_path = os.path.basename(path)
        remote_path = sdk2.svn.Arcadia.ARCADIA_BASE_URL + path
        sdk2.svn.Arcadia.export(
            remote_path, local_path,
            revision=self.Parameters.test_id_revision,
        )
        with open(local_path) as f:
            exp_config = yaml.safe_load(f)
            logging.info("Got config from path '%s':\n%s", path, exp_config)
        return exp_config

    def _get_rm_proto_event_specific_data(self, rm_proto_events, event_time_utc_iso, status=None):
        gsid = self.Context.__values__.get("__GSID")
        revision = gsid_parser.get_svn_revision_from_gsid(gsid)
        job_name = gsid_parser.get_job_name_from_gsid(gsid)
        if not revision or not job_name:
            return {}

        from release_machine.common_proto import test_results_pb2 as rm_test_results

        if status == "SUCCESS":
            test_result_status = rm_test_results.TestResult.TestStatus.OK
        else:
            test_result_status = rm_test_results.TestResult.TestStatus.CRIT
        return {
            "build_test_data": rm_proto_events.BuildTestData(
                job_name=job_name,
                revision=six.text_type(revision),
                scope_number=six.text_type(revision),  # tag number === trunk revision
                test_result=rm_test_results.TestResult(
                    status=test_result_status,
                    task_link=lb.task_link(self.id, plain=True),
                ),
            ),
        }
