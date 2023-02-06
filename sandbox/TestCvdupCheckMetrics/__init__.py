# -*- coding: utf-8 -*-

import json
import logging
import os
import os.path

from sandbox import sdk2
from sandbox.projects.cvdup import resource_types as resource_types_cvdup

from sandbox.sandboxsdk.environments import PipEnvironment
from sandbox.projects.images.CvdupAcceptanceTasks import common_functions

TICKET_MESSAGE_TEMPLATE = (
"""
CVDUP ACCEPTANCE METRICS ({marker}):

Accuracy stable: {accuracy_stable_value:.4f}
Accuracy branch: {accuracy_branch_value:.4f}
Accuracy difference: {accuracy_difference_value:.4f}
Accuracy status: {accuracy_status_value}

Precision stable: {precision_stable_value:.4f}
Precision branch: {precision_branch_value:.4f}
Precision difference: {precision_difference_value:.4f}
Precision status: {precision_status_value}

Recall stable: {recall_stable_value:.4f}
Recall branch: {recall_branch_value:.4f}
Recall difference: {recall_difference_value:.4f}
Recall status: {recall_status_value}

Number of estimates stable: {number_of_estimates_stable_value}
Number of estimates branch: {number_of_estimates_branch_value}

"""
)

class TestCvdupCheckMetrics(sdk2.Task):

    class Requirements(sdk2.Task.Requirements):
        environments = [
            PipEnvironment('startrek_client', custom_parameters=["requests==2.18.4"], use_wheel=True)
        ]

    class Parameters(sdk2.task.Parameters):
        kill_timeout = 3000
        stable_state_metrics_json = sdk2.parameters.Resource('State metrics for stable state', required=True, resource_type = resource_types_cvdup.CvdupAcceptanceStateMetricsJson)
        branch_state_metrics_json = sdk2.parameters.Resource('State metrics for branch state', required=True, resource_type = resource_types_cvdup.CvdupAcceptanceStateMetricsJson)
        startrack_ticket_id = sdk2.parameters.String('Ticket to write results', required=False)
        branch_number_for_tag = sdk2.parameters.String('Release machine integration parameter (leave empty when launching not from rm images_semidups)', required=False)

    def on_execute(self):
        env = dict(os.environ)

        self.stable_state_metrics_json = sdk2.ResourceData(self.Parameters.stable_state_metrics_json).path
        self.branch_state_metrics_json = sdk2.ResourceData(self.Parameters.branch_state_metrics_json).path

        self.startrack_api_token = sdk2.Vault.data('robot-cvdup', 'st_token')
        self.ticket_id = common_functions.find_ticket_by_branch(self.startrack_api_token, self.Parameters.branch_number_for_tag)
        common_functions.log_task_begin_in_ticket(self.startrack_api_token, self.ticket_id, self)

        if not self.ticket_id:
            self.ticket_id = self.Parameters.startrack_ticket_id

        with open(self.stable_state_metrics_json.resolve().as_posix(), "r") as read_file:
            stable_data = json.load(read_file)

        with open(self.branch_state_metrics_json.resolve().as_posix(), "r") as read_file:
            branch_data = json.load(read_file)

        accuracy_stable = float(stable_data["Accuracy"])
        accuracy_branch = float(branch_data["Accuracy"])
        precision_stable = float(stable_data["Precision"])
        precision_branch = float(branch_data["Precision"])
        recall_stable = float(stable_data["Recall"])
        recall_branch = float(branch_data["Recall"])
        number_of_estimates_stable = stable_data["NumberOfEstimates"]
        number_of_estimates_branch = branch_data["NumberOfEstimates"]

        accuracy_stable_portion = float(stable_data["AccuracyPortion"])
        accuracy_branch_portion = float(branch_data["AccuracyPortion"])
        precision_stable_portion = float(stable_data["PrecisionPortion"])
        precision_branch_portion = float(branch_data["PrecisionPortion"])
        recall_stable_portion = float(stable_data["RecallPortion"])
        recall_branch_portion = float(branch_data["RecallPortion"])
        number_of_estimates_stable_portion = stable_data["NumberOfEstimatesPortion"]
        number_of_estimates_branch_portion = branch_data["NumberOfEstimatesPortion"]

        accuracy_status = 'OK'
        accuracy_portion_status = 'OK'
        precision_status = 'OK'
        precision_portion_status = 'OK'
        recall_status = 'OK'
        recall_portion_status = 'OK'

        if 1.01 * accuracy_branch < accuracy_stable :
            accuracy_status = 'WARN'

        if 1.01 * accuracy_branch_portion < accuracy_stable_portion :
            accuracy_portion_status = 'WARN'

        if 1.01 * precision_branch < precision_stable :
            precision_status = 'WARN'

        if 1.01 * precision_branch_portion < precision_stable_portion :
            precision_portion_status = 'WARN'

        if 1.01 * recall_branch < recall_stable :
            recall_status = 'WARN'

        if 1.01 * recall_branch_portion < recall_stable_portion :
            recall_portion_status = 'WARN'

        ticket_message = TICKET_MESSAGE_TEMPLATE.format(
            marker = 'all',
            accuracy_stable_value = accuracy_stable,
            accuracy_branch_value = accuracy_branch,
            accuracy_difference_value = accuracy_branch - accuracy_stable,
            accuracy_status_value = accuracy_status,
            precision_stable_value = precision_stable,
            precision_branch_value = precision_branch,
            precision_difference_value = precision_branch - precision_stable,
            precision_status_value = precision_status,
            recall_stable_value = recall_stable,
            recall_branch_value = recall_branch,
            recall_difference_value = recall_branch - recall_stable,
            recall_status_value = recall_status,
            number_of_estimates_stable_value = str(number_of_estimates_stable),
            number_of_estimates_branch_value = str(number_of_estimates_branch),
        )

        ticket_message_portion = TICKET_MESSAGE_TEMPLATE.format(
            marker = 'portion',
            accuracy_stable_value = accuracy_stable_portion,
            accuracy_branch_value = accuracy_branch_portion,
            accuracy_difference_value = accuracy_branch_portion - accuracy_stable_portion,
            accuracy_status_value = accuracy_portion_status,
            precision_stable_value = precision_stable_portion,
            precision_branch_value = precision_branch_portion,
            precision_difference_value = precision_branch_portion - precision_stable_portion,
            precision_status_value = precision_portion_status,
            recall_stable_value = recall_stable_portion,
            recall_branch_value = recall_branch_portion,
            recall_difference_value = recall_branch_portion - recall_stable_portion,
            recall_status_value = recall_portion_status,
            number_of_estimates_stable_value = str(number_of_estimates_stable_portion),
            number_of_estimates_branch_value = str(number_of_estimates_branch_portion),
        )

        logging.info("Sending metrics to ticket...")

        common_functions.post_comment(self.startrack_api_token, ticket_message, self.ticket_id)
        common_functions.post_comment(self.startrack_api_token, ticket_message_portion, self.ticket_id)

        logging.info("Finished succesfully...")


