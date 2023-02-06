# -*- coding: utf-8 -*-

import exceptions
import logging
import json
import os
import os.path
import requests
import time
import traceback

from sandbox import sdk2
import sandbox.common
from sandbox.common.errors import TaskFailure
from sandbox.common.types import resource as ctr

from sandbox.projects import resource_types
from sandbox.projects.cvdup import resource_types as resource_types_cvdup
from sandbox.projects.release_machine.components import all as rmc
from sandbox.projects.release_machine.helpers.startrek_helper import STHelper

from sandbox.sandboxsdk import process
from sandbox.sandboxsdk.environments import PipEnvironment
import sandbox.sandboxsdk.paths as sdk_paths

from sandbox.projects.images.CvdupAcceptanceTasks import common_functions


def upload_image(url_put_base, url_get_base, namespace, image_name, content):
    files = {'file': content}
    url_put = url_put_base + '/put-%s/%s' % (namespace, image_name)
    retry_count = 3
    for try_no in range(retry_count):
        try:
            res = requests.post(url_put, files=files)
            if res.status_code == 200:
                value = json.loads(res.content)
                return url_get_base + value['sizes']['orig']['path']
            if res.status_code == 403:
                value = json.loads(res.content)
                return url_get_base + value['attrs']['sizes']['orig']['path']
            raise TaskFailure('Mds upload failed ' + str(res.status_code) + ' '  + str(res.content))
        except:
            print traceback.format_exc()
            time.sleep(2**try_no)

    raise TaskFailure('Mds uploading failed')


class TestCvdupSampleDiff(sdk2.Task):

    class Requirements(sdk2.Task.Requirements):
        ram = 16 * 1024
        disk_space = 32 * 1024
        environments = (
            PipEnvironment('yandex-yt'),
            PipEnvironment('startrek_client', use_wheel=True)
        )

    class Parameters(sdk2.task.Parameters):
        kill_timeout = 100 * 3600
        dataset_path1 = sdk2.parameters.String('Path on MR cluster for dataset', required=True, default='//home/cvdup/semidups/acceptance_data/source1_small.v7')
        dataset_path2 = sdk2.parameters.String('Path on MR cluster for dataset', required=True, default='//home/cvdup/semidups/acceptance_data/source2_small.v7')
        sampling_tool_binary = sdk2.parameters.Resource('Sampling tool binary', required=True, resource_type = resource_types_cvdup.CvdupSamplingTool)
        diff_count = sdk2.parameters.Integer('Max number of pairs to sample', required=True, default=5000)
        max_sample_count = sdk2.parameters.Integer('Max sample count from one group', required=True, default=100)
        image_extractor_tool_binary = sdk2.parameters.Resource('Image extractor tool binary', required=True, resource_type = resource_types_cvdup.CvdupImageExtractorTool)
        mr_cluster = sdk2.parameters.String('MR cluster where all jobs will work', required=True, default='arnold.yt.yandex.net')
        mr_path = sdk2.parameters.String('Path on MR cluster to store intermediate data', required=True, default='//home/cvdup/sample_diff')
        mr_path_1 = sdk2.parameters.String('Path on MR cluster for first state', required=True)
        mr_path_2 = sdk2.parameters.String('Path on MR cluster for second state', required=True)
        mds_api_host = sdk2.parameters.String('API host for MDS', required=False, default='http://avatars-int.mds.yandex.net:13000')
        mds_host = sdk2.parameters.String('MDS host', required=False, default='http://avatars.mds.yandex.net')
        mds_namespace = sdk2.parameters.String('MDS namespace to store intermediate data', required=False, default='images-similar-mturk')
        timestamp = sdk2.parameters.String('Release machine integration parameter (leave empty when launching not from rm images_semidups)', required=False, default='')
        branch_number_for_tag = sdk2.parameters.String('Release machine integration parameter (leave empty when launching not from rm images_semidups)', required=False)

    def generate_commands(self):
        commands = [
            '{sampling_tool} sample-diff-pairs --server {mr_cluster} --diff-count {dcount} --max-sample-count {mscount} --same-additive 1  --state1 {first} --state2 {second} --output {result} --format pairs_binary --info info.json'.format(
                sampling_tool=self.sampling_tool_binary,
                mr_cluster=self.Parameters.mr_cluster,
                dcount=self.Parameters.diff_count,
                mscount=self.Parameters.max_sample_count,
                first=self.Parameters.mr_path_1,
                second=self.Parameters.mr_path_2,
                result=self.Parameters.mr_path + "/diff_table",
            ),
            '{image_extractor_tool} extract-thumbs-pairs -o images -c {mr_cluster} -f {first_dataset} -s {second_dataset} -k {sampled_pairs} -j'.format(
                image_extractor_tool=self.image_extractor_tool_binary,
                mr_cluster=self.Parameters.mr_cluster,
                first_dataset=self.Parameters.dataset_path1,
                second_dataset=self.Parameters.dataset_path2,
                sampled_pairs=self.Parameters.mr_path + "/diff_table",
            )
        ]
        return commands

    def on_execute(self):
        import yt.wrapper as yt
        from yt.wrapper.ypath import ypath_join

        self.startrack_api_token = sdk2.Vault.data('robot-cvdup', 'st_token')
        self.ticket_id = common_functions.find_ticket_by_branch(self.startrack_api_token, self.Parameters.branch_number_for_tag)
        common_functions.log_task_begin_in_ticket(self.startrack_api_token, self.ticket_id, self)

        env = dict(os.environ)

        env['MR_RUNTIME'] = 'YT'
        env['YT_USE_YAMR_STYLE_PREFIX'] = '1'
        env['YT_POOL'] = 'cvdup'
        env['YT_SPEC'] = '{"job_io": {"table_writer": {"max_row_weight": 67108864}}, "map_job_io": {"table_writer": {"max_row_weight": 67108864}}, "reduce_job_io": {"table_writer": {"max_row_weight": 67108864}}, "sort_job_io": {"table_writer": {"max_row_weight": 67108864}}, "partition_job_io": {"table_writer": {"max_row_weight": 67108864}}, "merge_job_io": {"table_writer": {"max_row_weight": 67108864}}}'
        env['YT_TOKEN'] = sdk2.Vault.data('robot-cvdup', 'yt_token')

        try:
            os.mkdir("images")
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                raise

        result_resource_data = sdk2.ResourceData(resource_types_cvdup.CvdupAcceptanceImageUrlPairsJson(
            self, "Url pairs for toloka semidups checking", "images/toloka_estimating_input.json", ttl=30
        ))

        result_resource_data_sampler = sdk2.ResourceData(resource_types_cvdup.CvdupAcceptanceSamplerLaunchStatsJson(
            self, "Sampler launch stats", "info.json", ttl=30
        ))

        self.sampling_tool_binary = sdk2.ResourceData(self.Parameters.sampling_tool_binary).path
        self.image_extractor_tool_binary = sdk2.ResourceData(self.Parameters.image_extractor_tool_binary).path

        stdout_path = os.path.join(sdk_paths.get_logs_folder(), 'stdout.log')
        stderr_path = os.path.join(sdk_paths.get_logs_folder(), 'stderr.log')
        stdout_file = open(stdout_path, 'wa')
        stderr_file = open(stderr_path, 'wa')

        yt_client = yt.YtClient(proxy=self.Parameters.mr_cluster, token=sdk2.Vault.data('robot-cvdup', 'yt_token'))

        logging.info("Executing sampling and images extracting commands...")

        for cmd in self.generate_commands():
            logging.info("Start command %s", cmd)
            process.run_process(
                [cmd], work_dir="./", timeout=100*3600, shell=True, check=True, stdout=stdout_file, stderr=stderr_file, environment=env
            )

        logging.info('Uploading images to mds...')

        urls_uploaded = []
        current_timestamp = time.strftime("%m%d%Y_%H%M%S", time.gmtime())
        with open("./images/diff_pairs", "r") as pairs_file:
            for files_pair in pairs_file :
                for file_path in files_pair.split():
                    if not os.path.isfile('./images/' + file_path):
                        raise TaskFailure("Can not find file " + file_path + " in images folder")

                for file_path in files_pair.split():
                    content = open('./images/' + file_path, 'rb').read()
                    file_key = "cvdup_acceptance_" + current_timestamp + "_" + file_path.split('.')[0]
                    avatars_url = upload_image(self.Parameters.mds_api_host, self.Parameters.mds_host, self.Parameters.mds_namespace, file_key, content)
                    urls_uploaded.append(avatars_url)

        result_json_object = []
        i = 0
        while i < len(urls_uploaded):
            result_json_object.append({'image_url1' : urls_uploaded[i], 'image_url2' : urls_uploaded[i+1]})
            i += 2

        with open("./images/toloka_estimating_input.json", "w") as result_file:
            result_file.write(json.dumps(result_json_object, indent=2))

        logging.info("Finished succesfully...")


