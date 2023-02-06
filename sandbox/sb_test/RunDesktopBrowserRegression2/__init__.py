# -*- coding: utf-8 -*-
import datetime

from sandbox.projects.browser.autotests_qa_tools.sb_test.BaseDesktopBrowserRegression2 import BaseDesktopBrowserRegression2
from sandbox.projects.browser.autotests_qa_tools.sb_test.ContinueDesktopBrowserRegression2 import ContinueDesktopBrowserRegression2


class RunDesktopBrowserRegression2(BaseDesktopBrowserRegression2):

    MIN_LEEWAY_TIME_FOR_AUTOTESTS = 30
    continue_regression_task = ContinueDesktopBrowserRegression2

    def on_execute(self):

        super(RunDesktopBrowserRegression2, self).on_execute()
        if not self.Context.deadline:
            self.Context.deadline = (datetime.datetime.now() + datetime.timedelta(
                hours=self.Parameters.regression_deadline)).date().isoformat()
        builds = self.get_builds()
        self.wait_builds([build for build in builds.values() if build])
        with self.memoize_stage.check_booking:
            booking_check_state = self.check_booking()
            self.calculate_autotests_timeout(booking_check_state)

        assessors_links = self.upload_files_to_s3(
            builds.get("browser_build"),
            builds.get("fake_build", None),
            distributions=[{"distribution_type": self.Parameters.distribution_type,
                            "distribution_name": self.Parameters.distribution_name}]
        )
        self.Context.assessors_links = assessors_links

        manager = self.regression_manager_class(
            regression_config=self.regression_config,
            task_parameters=self.Parameters,
            task_context=self.Context,
            oauth_vault=self.oauth_vault)

        regression_summary = manager.create_regression()

        if regression_summary["info_message"]:
            self.set_info(regression_summary["info_message"],
                          do_escape=False)

    def launch_autotests_and_continue_regression_tasks(self, automated_info):
        pass
