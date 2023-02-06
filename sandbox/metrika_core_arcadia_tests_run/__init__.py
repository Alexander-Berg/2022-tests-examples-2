# coding=utf-8
import logging

from lxml import etree

from sandbox import sdk2
from sandbox.projects.common import binary_task, constants
from sandbox.projects.common.build import parameters as build_parameters
from sandbox.projects.metrika.admins import base_metrika_tests
from sandbox.projects.metrika.core.metrika_core_arcadia_tests_run import view
from sandbox.projects.metrika.utils import settings
from sandbox.projects.metrika.utils.task_types import ya_make, PrivateYtStoreParameters
from sandbox.sdk2 import parameters


class MetrikaCoreArcadiaTestsRun(ya_make.MetrikaYaMake, base_metrika_tests.BaseMetrikaTests):
    """
    Запуск аркадийных тестов Движка Метрики
    """

    class Parameters(ya_make.MetrikaYaMake.Parameters):
        owner = settings.owner
        description = "Запуск аркадийных тестов Движка Метрики"
        build_system = build_parameters.BuildSystem(default_value=constants.YA_MAKE_FORCE_BUILD_SYSTEM)  # https://st.yandex-team.ru/DEVTOOLSSUPPORT-751
        yt_store_parameters = PrivateYtStoreParameters()
        build_type = build_parameters.BuildType(default_value=build_parameters.consts.PROFILE_BUILD_TYPE)  # should be in private YT-store
        test = build_parameters.TestParameter(default_value=True)
        allure_report = build_parameters.TestAllureReport(default_value=True)
        allure_report_ttl = build_parameters.TestAllureReportTTL(default_value=30)
        tests_retries = build_parameters.TestsRetriesCount(default_value=1)
        check_return_code = build_parameters.CheckReturnCode(default_value=True)
        failed_tests_cause_error = build_parameters.FailedTestsCauseError(default_value=False)
        create_html_results_resource = build_parameters.CreateHtmlResultsParameter(default_value=True)
        junit_report = build_parameters.JUnitReport(default_value=True)

        tests_type = parameters.String("Тип запускаемых тестов", required=True, default="FT", choices=[("FT", "FT"), ("B2B", "B2B")])

        base_metrika_parameters = base_metrika_tests.BaseMetrikaTests.Parameters()

        _binary = binary_task.binary_release_parameters_list(stable=True)

    def shortcut(self):
        return "Аркадийные {} {}".format(self.Parameters.tests_type, self.Parameters.targets)

    def report_description(self):
        return "Протокол аркадийных {} {}".format(self.Parameters.tests_type, self.Parameters.targets)

    def _get_view_model(self):
        return view.ViewModel(self)

    def get_targets(self):
        return super(MetrikaCoreArcadiaTestsRun, self).get_targets()

    def post_build(self, source_dir, output_dir, pack_dir):
        logging.info("Post build - processing report and result")
        try:
            super(MetrikaCoreArcadiaTestsRun, self).post_build(source_dir, output_dir, pack_dir)
            self.Parameters.report_resource = sdk2.Resource['ALLURE_REPORT'].find(task=self).first()
            self.Parameters.test_results = self._parse_test_results(self.log_path("junit_report.xml"))
            if self.Parameters.report_startrek:
                logging.info("Reporting to tracker")
                self._report_startrek()

            logging.info("Analyze results")
            self._analyze_results()
        except:
            logging.exception("Exception in post-build. Defer.")
            self.Context.exceptions = True

    def _parse_test_results(self, junit_file_path):
        suites = {
            "suites": [],
            "failed_suites": [],
            "total": 0,
            "success": 0,
            "failed": 0,
        }

        def parset_junit_suite(junit_suite):
            suite = {}
            suite["name"] = junit_suite.attrib.get("name").encode('utf-8', errors='replace')
            suite["total"] = int(junit_suite.attrib.get("tests"))
            suite["failures"] = int(junit_suite.attrib.get("failures"))
            suite["cancelled"] = int(junit_suite.attrib.get("skipped"))
            suite["success"] = max(suite["total"] - suite["failures"] - suite["cancelled"], 0)
            return suite

        logging.info("Parsing file: {}".format(junit_file_path.as_posix()))
        junit_suites = etree.parse(junit_file_path.as_posix(), parser=etree.XMLParser(recover=True)).getroot()
        for junit_suite in junit_suites:
            suite = parset_junit_suite(junit_suite)
            suites["suites"].append(suite)
            suites["total"] += 1
            if suite["failures"] > 0:
                suites["failed_suites"].append(suite["name"])
                suites["failed"] += 1
            else:
                suites["success"] += 1

        return suites
