# -*- coding: utf-8 -*-

import json
import os
import os.path
import logging

from sandbox.projects.cvdup import resource_types as resource_types_cvdup
from sandbox.projects.images.cvdupacceptance import resources as cvdupacceptance_resources

from sandbox import sdk2

from sandbox.sandboxsdk import process
from sandbox.sandboxsdk.environments import PipEnvironment
import sandbox.sandboxsdk.paths as sdk_paths

from sandbox.projects.images.CvdupAcceptanceTasks import common_functions

class TestCvdupCalculateMetrics(sdk2.Task):

    class Requirements(sdk2.Task.Requirements):
        ram = 16 * 1024
        disk_space = 32 * 1024
        environments = (
            PipEnvironment('yandex-yt'),
            PipEnvironment('startrek_client', custom_parameters=["requests==2.18.4"], use_wheel=True)
        )

    class Parameters(sdk2.task.Parameters):
        kill_timeout = 24 * 3600
        state_path = sdk2.parameters.String('Path on MR cluster for semidups state', required=True)
        toloka_estimates_portion_json = sdk2.parameters.Resource('Portion of toloka estimates', required=True, resource_type = resource_types_cvdup.CvdupAcceptanceTolokaEstimatesJson)
        toloka_estimates_table = sdk2.parameters.String('Path on MR cluster with all toloka estimates', required=True)
        images_cvdup_acceptance_util_binary = sdk2.parameters.Resource('Cvdup acceptance util binary', required=True, resource_type = cvdupacceptance_resources.ImagesCvdupAcceptanceUtilExecutable)
        mr_cluster = sdk2.parameters.String('MR cluster where all jobs will work', required=True, default='arnold.yt.yandex.net')
        branch_number_for_tag = sdk2.parameters.String('Release machine integration parameter (leave empty when launching not from rm images_semidups)', required=False)

    def generate_prepare_commands(self):
        commands = [
            '{cvdup_acceptance_util_tool} TolokaEstimatesToJson --server {server_name} --input-table {estimates_table} --output-file {output_file}'.format(
                cvdup_acceptance_util_tool=self.images_cvdup_acceptance_util_binary,
                server_name=self.Parameters.mr_cluster,
                estimates_table=self.Parameters.toloka_estimates_table,
                output_file=self.toloka_estimates_all_json
            ),
            '{cvdup_acceptance_util_tool} ExtractCrcsFromUrls --input-file {input_file} --output-file {output_file}'.format(
                cvdup_acceptance_util_tool=self.images_cvdup_acceptance_util_binary,
                input_file=self.toloka_estimates_all_json,
                output_file=self.toloka_estimates_all_json
            ),
            '{cvdup_acceptance_util_tool} ExtractCrcsFromUrls --input-file {input_file} --output-file {output_file}'.format(
                cvdup_acceptance_util_tool=self.images_cvdup_acceptance_util_binary,
                input_file=self.toloka_estimates_portion_converted_json,
                output_file=self.toloka_estimates_portion_converted_json
            ),
        ]
        return commands

    def generate_calculate_metrics_commands(self):
        commands = [
            '{cvdup_acceptance_util_tool} SemidupsPublicStateDumpCrcs --server {server_name} --semidups-prefix {prefix} --semidups-state {state}  --input-file {input_file} --output-file {output_file}'.format(
                cvdup_acceptance_util_tool=self.images_cvdup_acceptance_util_binary,
                server_name=self.Parameters.mr_cluster,
                prefix=self.state_prefix,
                state=self.state_suffix,
                input_file=self.crcs_all_json,
                output_file=self.state_dumped_json
            ),
             '{cvdup_acceptance_util_tool} SemidupsPublicStateCalculateMetrics --toloka-estimates-file {estimates_file} --semidups-state-filtered-file {state_file} --output-file {output_file}'.format(
                cvdup_acceptance_util_tool=self.images_cvdup_acceptance_util_binary,
                estimates_file=self.toloka_estimates_all_json,
                state_file=self.state_dumped_json,
                output_file=self.metrics_all_json
            ),
             '{cvdup_acceptance_util_tool} SemidupsPublicStateCalculateMetrics --toloka-estimates-file {estimates_file} --semidups-state-filtered-file {state_file} --output-file {output_file}'.format(
                cvdup_acceptance_util_tool=self.images_cvdup_acceptance_util_binary,
                estimates_file=self.toloka_estimates_portion_converted_json,
                state_file=self.state_dumped_json,
                output_file=self.metrics_portion_json
            ),
        ]
        return commands

    def on_execute(self):

        from yt.wrapper import YtClient, ypath_join, ypath_split

        self.startrack_api_token = sdk2.Vault.data('robot-cvdup', 'st_token')
        self.ticket_id = common_functions.find_ticket_by_branch(self.startrack_api_token, self.Parameters.branch_number_for_tag)
        common_functions.log_task_begin_in_ticket(self.startrack_api_token, self.ticket_id, self)

        path_splitted = ypath_split(self.Parameters.state_path)
        self.state_suffix = path_splitted[-1]
        self.state_prefix = path_splitted[0]

        for item in path_splitted[1:-1] :
            self.state_prefix = ypath_join(self.state_prefix, item)

        stdout_path = os.path.join(sdk_paths.get_logs_folder(), 'stdout.log')
        stderr_path = os.path.join(sdk_paths.get_logs_folder(), 'stderr.log')
        stdout_file = open(stdout_path, 'wa')
        stderr_file = open(stderr_path, 'wa')

        env = dict(os.environ)
        env['MR_RUNTIME'] = 'YT'
        env['YT_USE_YAMR_STYLE_PREFIX'] = '1'
        env['YT_POOL'] = 'cvdup'
        env['YT_SPEC'] = '{"job_io": {"table_writer": {"max_row_weight": 67108864}}, "map_job_io": {"table_writer": {"max_row_weight": 67108864}}, "reduce_job_io": {"table_writer": {"max_row_weight": 67108864}}, "sort_job_io": {"table_writer": {"max_row_weight": 67108864}}, "partition_job_io": {"table_writer": {"max_row_weight": 67108864}}, "merge_job_io": {"table_writer": {"max_row_weight": 67108864}}}'
        env['YT_TOKEN'] = sdk2.Vault.data('robot-cvdup', 'yt_token')

        self.images_cvdup_acceptance_util_binary = sdk2.ResourceData(self.Parameters.images_cvdup_acceptance_util_binary).path
        self.toloka_estimates_portion_json = sdk2.ResourceData(self.Parameters.toloka_estimates_portion_json).path
        self.toloka_estimates_portion_converted_json = 'toloka_estimates_portion_converted.json'
        self.toloka_estimates_all_json = 'toloka_estimates_all.json'
        self.crcs_all_json = 'crcs_all.json'
        self.state_dumped_json = 'state_dumped.json'
        self.metrics_portion_json = 'metrics_portion.json'
        self.metrics_all_json = 'metrics_all.json'
        self.metrics_united_json = 'metrics_united.json'

        logging.info("Converting toloka estimates json...")

        with open(self.toloka_estimates_portion_json.resolve().as_posix(), "r") as read_file:
            self.toloka_estimates_portion_data = json.load(read_file)
        self.toloka_estimates_portion_converted_data = json.loads("""{"data": []}""")

        self.toloka_estimates_portion_converted_data["data"] = self.toloka_estimates_portion_data

        with open(self.toloka_estimates_portion_converted_json, "w") as write_file:
            json.dump(self.toloka_estimates_portion_converted_data, write_file, indent = True)

        result_resource_data1 = sdk2.ResourceData(resource_types_cvdup.CvdupAcceptanceJson(
            self, "", "toloka_estimates_portion_converted.json", ttl=1
        ))
        result_resource_data2 = sdk2.ResourceData(resource_types_cvdup.CvdupAcceptanceJson(
            self, "", "toloka_estimates_all.json", ttl=1
        ))
        result_resource_data3 = sdk2.ResourceData(resource_types_cvdup.CvdupAcceptanceJson(
            self, "", "crcs_all.json", ttl=1
        ))
        result_resource_data4 = sdk2.ResourceData(resource_types_cvdup.CvdupAcceptanceJson(
            self, "", "state_dumped.json", ttl=1
        ))

        result_resource_data_metrics_all = sdk2.ResourceData(resource_types_cvdup.CvdupAcceptanceJson(
            self, "State metrics calculated by all estimates", self.metrics_all_json
        ))
        result_resource_data_metrics_portion = sdk2.ResourceData(resource_types_cvdup.CvdupAcceptanceJson(
            self, "State metrics calculated by portion of estimates", self.metrics_portion_json
        ))
        result_resource_data_metrics_united = sdk2.ResourceData(resource_types_cvdup.CvdupAcceptanceStateMetricsJson(
            self, "State metrics calculated by estimates", self.metrics_united_json
        ))

        logging.info("Executing prepare commands...")

        for cmd in self.generate_prepare_commands():
            logging.info("Start command %s", cmd)
            process.run_process(
                [cmd], work_dir="./", timeout=24*3600, shell=True, check=True, stdout=stdout_file, stderr=stderr_file, environment=env
            )

        with open(self.toloka_estimates_all_json, "r") as read_file:
            self.toloka_estimates_all_data = json.load(read_file)

        crc_set = set()
        for x in self.toloka_estimates_all_data["data"]:
            crc_set.add(x["crc1"])
            crc_set.add(x["crc2"])

        with open(self.crcs_all_json, 'w') as f:
            f.write(json.dumps({'Data': [{'CrcHex': x} for x in crc_set]}))
        del crc_set

        logging.info("Executing calculate metrics commands...")

        for cmd in self.generate_calculate_metrics_commands():
            logging.info("Start command %s", cmd)
            process.run_process(
                [cmd], work_dir="./", timeout=24*3600, shell=True, check=True, stdout=stdout_file, stderr=stderr_file, environment=env
            )

        with open(self.metrics_portion_json, "r") as read_file:
            self.metrics_portion_data = json.load(read_file)

        with open(self.metrics_all_json, "r") as read_file:
            self.metrics_all_data = json.load(read_file)

        self.metrics_all_data['AccuracyPortion'] = self.metrics_portion_data['Accuracy']
        self.metrics_all_data['PrecisionPortion'] = self.metrics_portion_data['Precision']
        self.metrics_all_data['RecallPortion'] = self.metrics_portion_data['Recall']
        self.metrics_all_data['NumberOfEstimatesPortion'] = self.metrics_portion_data['NumberOfEstimates']
        self.metrics_all_data['CounterNotSemidupsBothPortion'] = self.metrics_portion_data['CounterNotSemidupsBoth']
        self.metrics_all_data['CounterSemidupsOnlyInTolokaPortion'] = self.metrics_portion_data['CounterSemidupsOnlyInToloka']
        self.metrics_all_data['CounterSemidupsOnlyInStatePortion'] = self.metrics_portion_data['CounterSemidupsOnlyInState']
        self.metrics_all_data['CounterSemidupsBothPortion'] = self.metrics_portion_data['CounterSemidupsBoth']

        with open(self.metrics_united_json, "w") as write_file:
            json.dump(self.metrics_all_data, write_file, indent = True, sort_keys=True)

        logging.info("Finished succesfully...")


