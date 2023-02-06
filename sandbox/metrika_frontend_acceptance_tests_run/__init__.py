# coding=utf-8
import json
import logging
import os
import shutil

from sandbox import sdk2
from sandbox.common import errors
from sandbox.projects.common import binary_task
from sandbox.projects.metrika import utils
from sandbox.projects.metrika.frontend.metrika_frontend_acceptance_tests_run import view
from sandbox.projects.metrika.utils import parameters, settings, vcs
from sandbox.projects.metrika.utils.base_metrika_task import base_metrika_task as bmt
from sandbox.projects.metrika.utils.mixins import console

TESTS_DIR = "metrika/frontend/tests/bdd"
TESTS_SERVICES_DIR = "project"

SERVICES = [
    "metrika",
    "radar",
    "audience",
    "appmetrica",
    "mediametrika"
]


class TestsReport(sdk2.Resource):
    """ Tests report """


@bmt.with_parents
class MetrikaFrontendAcceptanceTestsRun(bmt.BaseMetrikaLargeTask, console.BaseConsoleMixin):
    """
    Run frontend acceptance tests
    """

    class Parameters(utils.CommonParameters):
        description = "Run Frontend Acceptance Tests"
        container = parameters.LastFrontendTestsContainerResource("Environment container resource", required=True)

        with sdk2.parameters.Group("Main parameters") as main_block:
            arcadia_url = sdk2.parameters.ArcadiaUrl("Arcadia URL", required=False, default="arcadia-arc:/#trunk")
            frontend_url = sdk2.parameters.Url("Frontend URL", required=True)
            api_url = sdk2.parameters.Url("API URL", required=False, default="https://mobmetd-autobeta.test.metrika.yandex.net")

        with sdk2.parameters.Group("Startrek parameters") as st_block:
            comment_issue = sdk2.parameters.Bool("Comment issue with tests report", required=False, default=False)
            with comment_issue.value[True]:
                issue_key = parameters.TrackerIssue("Issue Key", required=True)

        with sdk2.parameters.Group("Testing parameters") as testing_block:
            tested_service = sdk2.parameters.String(
                "Tested service", required=True, default=SERVICES[3], choices=[(item, item) for item in SERVICES]
            )
            env_vars = sdk2.parameters.Dict("Optional environment variables", required=False)
            fail_task_on_test_failure = sdk2.parameters.Bool(
                "Fail task on tests failures", required=False, default=False
            )

        with sdk2.parameters.Group("Secret parameters") as secret_block:
            tus_token = sdk2.parameters.YavSecretWithKey(
                "TUS token", required=False, default="{}#tus-token".format(settings.yav_uuid)
            )
            vault_token = sdk2.parameters.YavSecretWithKey(
                "Vault token", required=False, default="sec-01fyzze5zfvjz1mfq5pz8nr3at#SUPPORT"
            )

        with sdk2.parameters.Output:
            with sdk2.parameters.Group("Results") as output_block:
                report_resource = sdk2.parameters.Resource("Report resource")
                tests_results = sdk2.parameters.JSON("Tests results")
                tests_statistics = sdk2.parameters.Dict("Tests statistics")

        _binary = binary_task.binary_release_parameters_list(stable=True)

    def on_execute(self):
        with sdk2.helpers.ProgressMeter("Checkout"):
            self._checkout_branch()
        with sdk2.helpers.ProgressMeter("Build"):
            self._build()
        with sdk2.helpers.ProgressMeter("Run tests"):
            self._run_tests()
        with sdk2.helpers.ProgressMeter("Generate report"):
            self._generate_report()
        if self.Parameters.comment_issue:
            with sdk2.helpers.ProgressMeter("Comment issue"):
                self._report_startrek()
        if self.Parameters.fail_task_on_test_failure:
            if self.Parameters.tests_statistics["failed"]:
                raise errors.TaskFailure("Tests failed")

    def _checkout_branch(self):
        with vcs.mount_arc(self.Parameters.arcadia_url) as arcadia_root:
            shutil.copytree(str(os.path.join(arcadia_root, TESTS_DIR)), self.wd())

    def _build(self):
        self._execute_shell_and_check(["npm", "run", "build"], cwd=self.wd())

    def _run_tests(self):
        env = os.environ.copy()
        if self.Parameters.env_vars is not None:
            env.update(self.Parameters.env_vars)

        env["TUS_TOKEN"] = self.Parameters.tus_token.value()
        env["VAULT_TOKEN"] = self.Parameters.vault_token.value()
        env["BASE_APPMETRICA_URL"] = self.Parameters.frontend_url
        env["BASE_APPMETRICA_API_URL"] = self.Parameters.api_url

        self._execute_shell([
            "npm",
            "run",
            "test:{}".format(self.Parameters.tested_service)
        ], cwd=self.wd(), env=env)

    def _generate_report(self):
        self._execute_shell(["npm", "run", "generate-report"], cwd=self.wd())
        self.Parameters.report_resource = TestsReport(self, "Tests report", self.wd("report/cucumber_report.html"))

        with open(self.wd("results/results.json"), "r") as json_file:
            results = json.load(json_file)

        self.Parameters.tests_results = results
        self.Parameters.tests_statistics = self._extract_statistics(results)

        self.set_info(self.get_html_comment(), do_escape=False)

    def _report_startrek(self):
        try:
            issue = self.st_client.issues[self.Parameters.issue_key]
            issue.comments.create(text=self.get_wiki_comment())
        except Exception as e:
            self.set_info(e.message)
            logging.warning("Error while sending a comment to Startrek", exc_info=True)

    @property
    def shortcut(self):
        return "Тесты фронтенда {}".format(self.Parameters.tested_service)

    @property
    def report_description(self):
        return "Отчёт о тестировании"

    def get_wiki_comment(self):
        return utils.render("wiki.jinja2", {"view": view.ViewModel(self)})

    def get_html_comment(self):
        return utils.render("html.jinja2", {"view": view.ViewModel(self)})

    def _extract_statistics(self, results):
        suites = {
            "total": 0,
            "success": 0,
            "failed": 0,
        }

        for feature in results:
            for scenario in feature["elements"]:
                suites["total"] += 1
                all_steps_passed = all(step["result"]["status"] == "passed" for step in scenario["steps"])
                if all_steps_passed:
                    suites["success"] += 1
                else:
                    suites["failed"] += 1

        return suites
