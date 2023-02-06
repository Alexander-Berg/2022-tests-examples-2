# -*- coding: utf-8 -*-
import sandbox
from sandbox import sdk2
from sandbox.projects.browser.autotests_qa_tools.sb_test.BaseDesktopBrowserRegression2 import BaseDesktopBrowserRegression2


class ContinueDesktopBrowserRegression2(BaseDesktopBrowserRegression2):

    class Parameters(BaseDesktopBrowserRegression2.Parameters):
        run_regression_task = sdk2.parameters.Task("run regression task")
        autotests_task = sdk2.parameters.Task("autotests_task")
        issues_filter = sdk2.parameters.String(
            'Issues filter',
            default="",
            description="Comma-separated list of issues id for processing. If the list is empty, all tickets will be processed"
        )

    @property
    @sandbox.common.utils.singleton
    def regression_config(self):
        return self.initial_regression_state["initial_config"]

    def on_execute(self):
        self.continue_regression()
