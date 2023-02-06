# -*- coding: utf-8 -*-
import os
import sys
import logging

from sandbox import (
    sdk2,
    common,
)

import sandbox.sandboxsdk.svn

import sandbox.projects.release_machine.core.const as rm_const
import sandbox.projects.release_machine.components.all as rm_comp

import sandbox.projects.release_machine.core.task_env as rm_task_env
from sandbox.projects.release_machine.helpers.startrek_helper import STHelper

from sandbox.projects.ab_testing import (
    RUN_ABT_METRICS_REPORT,
    ABT_METRICS_DIFF_REPORT_TEXT,
)


class ReportDiffMetricsABT(sdk2.Task):
    class Requirements(rm_task_env.StartrekRequirements):
        ram = 4096

    class Parameters(sdk2.Task.Parameters):
        metrics_prev = sdk2.parameters.Resource(
            "First metrics and features calc result for diff",
            required=True,
            resource_type=RUN_ABT_METRICS_REPORT,
        )
        metrics_next = sdk2.parameters.Resource(
            "Second metrics and features calc result for diff",
            required=True,
            resource_type=RUN_ABT_METRICS_REPORT,
        )

        sample_path = sdk2.parameters.String(
            "Sample path from the metrics resources",
            required=True,
        )

        component_name = sdk2.parameters.String(
            "Release machine component name for startrek ticket update",
            default=None,
        )
        release_number = sdk2.parameters.Integer(
            "Release number for startrek ticket update",
            default=None,
        )

    def on_execute(self):
        # RUN_ABT_METRICS_REPORT store metrics or (metrics and features) according to version resource
        metrics_prev = sdk2.ResourceData(self.Parameters.metrics_prev)
        metrics_next = sdk2.ResourceData(self.Parameters.metrics_next)

        if common.system.inside_the_binary():
            import quality.ab_testing.scripts.shellabt as shellabt
        else:
            # shellabt_path = sandbox.sandboxsdk.svn.Arcadia.get_arcadia_src_dir(
            #     "arcadia:/arc/trunk/arcadia/quality/ab_testing/scripts/shellabt/"
            # )
            checkout_dir = os.path.abspath("shellabt")
            os.mkdir(checkout_dir)

            shellabt_path = sandbox.sandboxsdk.svn.Arcadia.checkout(
                url="arcadia:/arc/trunk/arcadia/quality/ab_testing/scripts/shellabt/",
                path=checkout_dir,
            )

            sys.path.append(shellabt_path)
            import shellabt

        diff_report = shellabt.diff_suite_files(str(metrics_prev.path), str(metrics_next.path))

        raw_report_text = diff_report.format_raw()

        report_filename = "report.txt"
        with open(report_filename, "w") as report_file:
            report_file.write(raw_report_text.encode("utf-8"))

        sdk2.ResourceData(
            ABT_METRICS_DIFF_REPORT_TEXT(
                task=self,
                description="ABT metrics diff raw text report",
                path=report_filename,
            )
        ).ready()

        component_name = self.Parameters.component_name
        release_number = self.Parameters.release_number
        if component_name:
            st_helper = STHelper(sdk2.Vault.data(rm_const.COMMON_TOKEN_OWNER, rm_const.COMMON_TOKEN_NAME))
            c_info = rm_comp.COMPONENTS[component_name]()

            if not release_number:
                release_number = c_info.last_scope_num

            logging.info("Component name '{}', release_number '{}'".format(component_name, release_number))

            message = self.format_comment_st(
                self.Parameters.metrics_prev.id,
                self.Parameters.metrics_next.id,
                raw_report_text
            )
            logging.info("Startrek message is:\n{}".format(message))

            st_helper.comment(release_number, message, c_info)

    def format_comment_st(self, prev_resource_id, next_resource_id, raw_report_text):
        message = "\n".join([
            "Prev run metrics result: {}".format(common.utils.get_resource_link(prev_resource_id)),
            "Next run metrics result: {}".format(common.utils.get_resource_link(next_resource_id)),
            "",
            "Trunk diffs history: https://testenv.yandex-team.ru/?screen=problems&database=abt_metrics_trunk",
            ""
            "<{{DIFF\n%%\n{diff}%%\n}}>".format(diff=raw_report_text),
        ])

        return message
