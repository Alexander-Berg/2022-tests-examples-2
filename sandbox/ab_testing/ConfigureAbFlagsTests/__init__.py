# -*- coding: utf-8 -*-

import json
import logging
import os

from sandbox import sdk2
from sandbox.projects.ab_testing import ConfigureAbTests as configure_ab_tests
from sandbox.projects.common import file_utils as fu
from sandbox.projects.common.arcadia import sdk as asdk
from sandbox.projects.common.string import all_to_str
from sandbox.projects.sandbox_ci.resources import SANDBOX_CI_ARTIFACT
from sandbox.projects.ab_testing.ConfigureAbFlagsTests import service_duty

import sandbox.projects.common.time_utils as tu
import sandbox.projects.release_machine.helpers.events_helper as events_helper
import sandbox.projects.release_machine.helpers.startrek_helper as rm_st
import sandbox.projects.release_machine.security as rm_sec


WEB4_ASSESSORS_CONFIG_PATH = "frontend/projects/web4/.config/assessors/release.tsr.json"
TESTID_TESTS = "TESTID_TESTS"
BULK_TESTS = "BULK_TESTS"


class ConfigureAbFlagsTests(configure_ab_tests.ConfigureAbTests):
    class Parameters(configure_ab_tests.ConfigureAbTests.Parameters):
        run_type = sdk2.parameters.String(
            "Test type",
            choices=[(TESTID_TESTS, TESTID_TESTS), (BULK_TESTS, BULK_TESTS)],
            default=BULK_TESTS,
        )

        with sdk2.parameters.Output:
            web_runner = configure_ab_tests.WebTestWebRunnerParameters()
            web_assessors = configure_ab_tests.WebTestAssessorsParameters()
            web_metrics = configure_ab_tests.WebMetricsParameters()
            video_fiji = configure_ab_tests.VideoFijiExperimentsParameters()
            video_metrics = configure_ab_tests.VideoMetricsParameters()
            images_fiji = configure_ab_tests.ImagesFijiExperimentsParameters()
            images_metrics = configure_ab_tests.ImagesMetricsParameters()

            service_responsibles = sdk2.parameters.String("Space-separated list of service responsibles")

    def create_testsuites_resource(self, testsuites, filename="test-suites.json", archive="test-suites.tar.gz"):
        """
        Тест-сьюты сохраняет в файл, архивирует и из архива варит ресурс.

        :param testsuites: Тест-сьюты
        :type testsuites: dict
        :param filename: Название json файла с конфигом
        :type filename: str
        :param archive: Название архива
        :type archive: str
        :rtype: sdk2.Resource
        """

        fu.json_dump_to_tar(archive_name=archive, file_name=filename, contents=testsuites)
        logging.debug("Adding to %s testsuites: %s", archive, testsuites)
        resource = SANDBOX_CI_ARTIFACT(
            task=self,
            description="{} with testsuites configs".format(archive),
            path=archive,
        )
        logging.debug("Resource with %s: %s", archive, resource)

        sdk2.ResourceData(resource).ready()
        return resource

    def get_testsuites(self):
        with asdk.mount_arc_path("arcadia-arc:/#trunk") as mount_point:
            with open(os.path.join(mount_point, WEB4_ASSESSORS_CONFIG_PATH), "r") as f:
                config = json.load(f)
                testsuites = config.get("suites", [])
                new_testsuites = []
                for item in testsuites:
                    if item.get("release_exp_flags", False):
                        item["release_exp_flags_testid"] = self.exp_config["testid"]
                        item["tags"].append(self.exp_config["experiment_id"])
                        new_testsuites.append(item)
                config["suites"] = new_testsuites
        return config

    def set_check_web_experiment_params(self):
        if "web" in self.exp_config["services"]:
            child_description_template = (
                "Running automatic ab deployment {test_type}-{test_type} test by {parent_type} [{parent_id}]"
            )

            if self.Parameters.run_type == BULK_TESTS:
                self.Parameters.web_assessors.web__test_assessors__testpalm_project_suffix = "issue-{}".format(
                    self.exp_config["experiment_id"]
                ).lower()
                sandbox_ci_resource = self.create_testsuites_resource(testsuites=self.get_testsuites())
                self.Parameters.web_assessors.web__test_assessors__build_artifacts_resources = (
                    sandbox_ci_resource.id
                )
                self.Parameters.web_assessors.web__test_assessors__test_assesssors_description = (
                    "running automatic ab deployment test by {} [{}]".format(
                        self.type, self.id,
                    )
                )
                self.Parameters.web_assessors.web__test_assessors__run_flags_mode = True
                self.Parameters.web_runner.web__runner__dev_description = child_description_template.format(
                    test_type="dev",
                    parent_type=self.type,
                    parent_id=self.id,
                )

            self.Parameters.web_runner.web__runner__prod_description = child_description_template.format(
                test_type="prod",
                parent_type=self.type,
                parent_id=self.id,
            )
            self.Parameters.web_runner.web__runner__run_flags_mode = True

    def set_images_and_video_experiment_params(self):
        if "video" in self.exp_config["services"]:
            self.Parameters.video_metrics.video__metrics__description = (
                "Running automatic ab deployment test by {} [{}]".format(self.type, self.id)
            )
            self.Parameters.video_metrics.video__metrics__custom_template_name = "experiments.json"
            self.Parameters.video_metrics.video__metrics__sample_beta = "hamster"
            self.Parameters.video_metrics.video__metrics__checked_beta = "hamster"
            self.Parameters.video_metrics.video__metrics__checked_extra_params = "test-id={}".format(
                self.exp_config["testid"],
            )
            self.Parameters.video_metrics.video__metrics__scraper_over_yt_pool = "experiments_flags"

            self.Parameters.video_fiji.video__fiji_experiments__description = (
                "Running automatic ab deployment fiji video test by {} [{}]".format(self.type, self.id)
            )
            self.Parameters.video_fiji.video__fiji_experiments__release = "latest"
            self.Parameters.video_fiji.video__fiji_experiments__tests_source = "dev"
            self.Parameters.video_fiji.video__fiji_experiments__platforms = ["desktop", "touch-phone"]
            self.Parameters.video_fiji.video__fiji_experiments__service = "video"
            self.Parameters.video_fiji.video__fiji_experiments__hermionee2e_base_url = "https://yandex.ru"
            self.Parameters.video_fiji.video__fiji_experiments__run_flags_mode = True

        if "images" in self.exp_config["services"]:
            self.Parameters.images_metrics.images__metrics__description = (
                "Running automatic ab deployment test by {} [{}]".format(self.type, self.id)
            )
            self.Parameters.images_metrics.images__metrics__custom_template_name = "experiments.json"
            self.Parameters.images_metrics.images__metrics__sample_beta = "hamster"
            self.Parameters.images_metrics.images__metrics__checked_beta = "hamster"
            self.Parameters.images_metrics.images__metrics__checked_extra_params = "test-id={}".format(
                self.exp_config["testid"],
            )
            self.Parameters.images_metrics.images__metrics__scraper_over_yt_pool = "experiments_flags"

            self.Parameters.images_fiji.images__fiji_experiments__description = (
                "Running automatic ab deployment fiji images test by {} [{}]".format(self.type, self.id)
            )
            self.Parameters.images_fiji.images__fiji_experiments__release = "latest"
            self.Parameters.images_fiji.images__fiji_experiments__tests_source = "dev"
            self.Parameters.images_fiji.images__fiji_experiments__platforms = ["desktop", "touch-pad", "touch-phone"]
            self.Parameters.images_fiji.images__fiji_experiments__service = "images"
            self.Parameters.images_fiji.images__fiji_experiments__hermionee2e_base_url = "https://yandex.ru"
            self.Parameters.images_fiji.images__fiji_experiments__run_flags_mode = True

        if "web" in self.exp_config["services"]:
            self.Parameters.web_metrics.web__metrics__description = (
                "Running automatic ab deployment test by {} [{}]".format(self.type, self.id)
            )
            self.Parameters.web_metrics.web__metrics__custom_template_name = "experiments.json"
            self.Parameters.web_metrics.web__metrics__sample_beta = "hamster"
            self.Parameters.web_metrics.web__metrics__checked_beta = "hamster"
            self.Parameters.web_metrics.web__metrics__checked_extra_params = "test-id={}".format(
                self.exp_config["testid"],
            )
            self.Parameters.web_metrics.web__metrics__scraper_over_yt_pool = "experiments_flags"

    def send_ticket_history_event(self):
        if not self.Parameters.send_event_data:
            return

        from release_machine.common_proto import events_pb2 as rm_proto_events

        event_time_utc_iso = tu.datetime_utc_iso()

        st_auth_token = rm_sec.get_rm_token(self)
        st_helper = rm_st.STHelper(st_auth_token)
        issue = st_helper.get_ticket_by_key(self.Parameters.experiment_id)
        issue_start_time = tu.to_unixtime(issue.createdAt)
        issue_status = all_to_str(issue.status.name).lower()

        ticket_history_data = rm_proto_events.TicketHistoryData(
            ticket_key=self.Parameters.experiment_id,
            scope_number=str(self.Parameters.test_id_revision),
            job_name=self.get_job_name_from_gsid(),
            ticket_history_latest_status=issue_status,
        )

        ticket_history_data.items.extend([rm_proto_events.TicketHistoryDataItem(
            status=issue_status,
            start_timestamp=issue_start_time,
        )])

        events_helper.post_proto_events([rm_proto_events.EventData(
            general_data=self._get_rm_proto_event_general_data(
                event_time_utc_iso=event_time_utc_iso,
            ),
            task_data=self._get_rm_proto_event_task_data(
                event_time_utc_iso=event_time_utc_iso,
            ),
            ticket_history_data=ticket_history_data,
        )])

    def set_service_responsibles(self):

        services = self.exp_config["services"]

        people = service_duty.get_service_duty(
            web=("web" in services),
            images=("images" in services),
            video=("video" in services),
        )

        self.Parameters.service_responsibles = " ".join(set(people)).strip()

    def on_execute(self):
        configure_ab_tests.ConfigureAbTests.on_execute(self)
        self.Parameters.testid = self.exp_config["testid"]
        self.Parameters.experiment_id = self.exp_config["experiment_id"]
        self.Parameters.flagsjson_id = self.exp_config["flagsjson_id"]
        self.set_check_web_experiment_params()
        self.set_images_and_video_experiment_params()
        self.send_ticket_history_event()
        self.set_service_responsibles()
