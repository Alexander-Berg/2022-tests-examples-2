# -*- coding: utf-8 -*-

import os.path
import logging

from sandbox import sdk2
from sandbox.common.errors import TaskFailure
from sandbox.common.types import resource as ctr
import sandbox.common.types.task as ctt
from sandbox.sandboxsdk.environments import PipEnvironment
import sandbox.sandboxsdk.paths as sdk_paths

from sandbox.projects import resource_types
from sandbox.projects.cvdup import resource_types as resource_types_cvdup
from sandbox.projects.images.cvdupacceptance import resources as cvdupacceptance_resources

from sandbox.projects.images.CvdupAcceptanceTasks import common_functions
from sandbox.projects.images.CvdupAcceptanceTasks.TestCvdupCreateState import TestCvdupCreateState
from sandbox.projects.images.CvdupAcceptanceTasks.TestCvdupMergeStates import TestCvdupMergeStates
from sandbox.projects.images.CvdupAcceptanceTasks.TestCvdupSampleDiff import TestCvdupSampleDiff
from sandbox.projects.images.CvdupAcceptanceTasks.TestCvdupTolokaEstimating import TestCvdupTolokaEstimating
from sandbox.projects.images.CvdupAcceptanceTasks.TestCvdupLoadTolokaEstimates import TestCvdupLoadTolokaEstimates
from sandbox.projects.images.CvdupAcceptanceTasks.TestCvdupCalculateMetrics import TestCvdupCalculateMetrics
from sandbox.projects.images.CvdupAcceptanceTasks.TestCvdupCheckMetrics import TestCvdupCheckMetrics
from sandbox.projects.images.CvdupAcceptanceTasks.TestCvdupCleanOldAllStagesLaunchesData import TestCvdupCleanOldAllStagesLaunchesData
from sandbox.projects.images.CvdupAcceptanceTasks.TestCvdupCleanCache import TestCvdupCleanCache

class TestCvdupAllStages(sdk2.Task):

    class Requirements(sdk2.Task.Requirements):
        environments = (
            PipEnvironment('yandex-yt'),
        )

    class Parameters(sdk2.task.Parameters):
        kill_timeout = 170 * 3600
        dataset_path1 = sdk2.parameters.String('Path on MR cluster for dataset', required=True, default='//home/cvdup/semidups/acceptance_data/source1_small.v7')
        dataset_path2 = sdk2.parameters.String('Path on MR cluster for dataset', required=True, default='//home/cvdup/semidups/acceptance_data/source2_small.v7')

        image_reducer_binary1 = sdk2.parameters.LastReleasedResource('First image reducer binary', required=True, resource_type = resource_types.CVDUP_IMAGEREDUCE, state=(ctr.State.READY, ))
        image_reducer_binary2 = sdk2.parameters.Resource('Second image reducer binary', required=True, resource_type = resource_types.CVDUP_IMAGEREDUCE)
        sampling_tool_binary = sdk2.parameters.Resource('Sampling tool binary', required=True, resource_type = resource_types_cvdup.CvdupSamplingTool)
        images_cvdup_acceptance_util_binary = sdk2.parameters.Resource('Cvdup acceptance util binary', required=True, resource_type = cvdupacceptance_resources.ImagesCvdupAcceptanceUtilExecutable)
        diff_count = sdk2.parameters.Integer('Max number of pairs to sample', required=True, default=10000)
        max_sample_count = sdk2.parameters.Integer('Max sample count from one group', required=True, default=100)
        image_extractor_tool_binary = sdk2.parameters.Resource('Image extractor tool binary', required=True, resource_type = resource_types_cvdup.CvdupImageExtractorTool)

        mr_cluster = sdk2.parameters.String('MR cluster where all jobs will work', required=True, default='arnold.yt.yandex.net')
        mr_path_base = sdk2.parameters.String('Base path on MR cluster for intermediate data', required=True, default='//home/cvdup/semidups/acceptance_states')
        mr_states_cache_path = sdk2.parameters.String('Path on MR cluster for semidups states cache', required=True, default='//home/cvdup/semidups/acceptance_states/cache_small_v7')

        startrack_ticket_id = sdk2.parameters.String('Ticket to write results', required=False)

        mds_api_host = sdk2.parameters.String('API host for MDS', required=False, default='http://avatars-int.mds.yandex.net:13000')
        mds_host = sdk2.parameters.String('MDS host', required=False, default='http://avatars.mds.yandex.net')
        mds_namespace = sdk2.parameters.String('MDS namespace to store intermediate data', required=False, default='images-similar-mturk')

        nirvana_api_host = sdk2.parameters.String('API host for Nirvana', required=False, default='https://nirvana.yandex-team.ru/api/public/v1')
        labeling_nirvana_workflow_id = sdk2.parameters.String('Nirvana workflow id to send results in toloka', required=False, default='df80fb76-d9ef-42fb-8396-053b73155393')
        labeling_nirvana_workflow_instance_id = sdk2.parameters.String('Instance id to clone (send to toloka)', required=False, default='2df5b25f-d96d-4cf6-ade9-2988cd9bf04e')
        load_estimates_nirvana_workflow_id = sdk2.parameters.String('Nirvana workflow id to export toloka estimates to yt', required=False, default='810f49b2-6c92-4342-85e1-fc7a4f404e67')
        load_estimates_nirvana_workflow_instance_id = sdk2.parameters.String('Instance id to clone (export estimates)', required=False, default='1e5f2b16-b06a-42f1-86bc-7bc1503ba770')

    def on_execute(self):

        from yt.wrapper import YtClient, ypath_join, ypath_split

        stdout_path = os.path.join(sdk_paths.get_logs_folder(), 'stdout.log')
        stderr_path = os.path.join(sdk_paths.get_logs_folder(), 'stderr.log')
        stdout_file = open(stdout_path, 'wa')
        stderr_file = open(stderr_path, 'wa')

        with self.memoize_stage.step1:
            logging.info("Creating states")
            self.Context.yt_path = ypath_join(self.Parameters.mr_path_base, "TEST_CVDUP_ALL_STAGES_" + str(self.id))
            self.Context.yt_path_toloka_estimates = ypath_join(self.Context.yt_path, "toloka_estimates")
            self.Context.create_state_subtasks = []

            task1 = TestCvdupCreateState(
                self,
                description='launched from TestCvdupAllStages',
                kill_timeout= 80 * 3600,
                dataset_path = self.Parameters.dataset_path1,
                state_id = 1,
                image_reducer_binary = self.Parameters.image_reducer_binary1,
                mr_cluster = self.Parameters.mr_cluster,
                mr_path = ypath_join(self.Context.yt_path, "dataset1_binary1"),
                mr_states_cache_path = self.Parameters.mr_states_cache_path,
            )
            task1.enqueue()
            self.Context.create_state_subtasks.append(task1.id)

            task2 = TestCvdupCreateState(
                self,
                description='launched from TestCvdupAllStages',
                kill_timeout= 80 * 3600,
                dataset_path = self.Parameters.dataset_path2,
                state_id = 2,
                image_reducer_binary = self.Parameters.image_reducer_binary1,
                mr_cluster = self.Parameters.mr_cluster,
                mr_path = ypath_join(self.Context.yt_path, "dataset2_binary1"),
                mr_states_cache_path = self.Parameters.mr_states_cache_path,
            )
            task2.enqueue()
            self.Context.create_state_subtasks.append(task2.id)

            task3 = TestCvdupCreateState(
                self,
                description='launched from TestCvdupAllStages',
                kill_timeout= 80 * 3600,
                dataset_path = self.Parameters.dataset_path1,
                state_id = 1,
                image_reducer_binary = self.Parameters.image_reducer_binary2,
                mr_cluster = self.Parameters.mr_cluster,
                mr_path = ypath_join(self.Context.yt_path, "dataset1_binary2"),
                mr_states_cache_path = self.Parameters.mr_states_cache_path,
            )
            task3.enqueue()
            self.Context.create_state_subtasks.append(task3.id)

            task4 = TestCvdupCreateState(
                self,
                description='launched from TestCvdupAllStages',
                kill_timeout= 80 * 3600,
                dataset_path = self.Parameters.dataset_path2,
                state_id = 2,
                image_reducer_binary = self.Parameters.image_reducer_binary2,
                mr_cluster = self.Parameters.mr_cluster,
                mr_path = ypath_join(self.Context.yt_path, "dataset2_binary2"),
                mr_states_cache_path = self.Parameters.mr_states_cache_path,
            )

            task4.enqueue()
            self.Context.create_state_subtasks.append(task4.id)

            raise sdk2.WaitTask(self.Context.create_state_subtasks, ctt.Status.Group.FINISH | ctt.Status.Group.BREAK)


        with self.memoize_stage.step2:
            for task_id in self.Context.create_state_subtasks:
                if sdk2.Task[task_id].status not in ctt.Status.Group.SUCCEED:
                    raise TaskFailure("Child task failed")
            logging.info("Merging states")
            self.Context.merge_states_subtasks = []

            task1 = TestCvdupMergeStates(
                self,
                description='launched from TestCvdupAllStages',
                kill_timeout= 80 * 3600,
                image_reducer_binary = self.Parameters.image_reducer_binary1,
                state_id = 2,
                mr_cluster = self.Parameters.mr_cluster,
                mr_path_1 = ypath_join(self.Context.yt_path, "dataset1_binary1"),
                mr_path_2 = ypath_join(self.Context.yt_path, "dataset2_binary1"),
                mr_states_cache_path = self.Parameters.mr_states_cache_path,
            )

            task1.enqueue()
            self.Context.merge_states_subtasks.append(task1.id)

            task2 = TestCvdupMergeStates(
                self,
                description='launched from TestCvdupAllStages',
                kill_timeout= 80 * 3600,
                image_reducer_binary = self.Parameters.image_reducer_binary2,
                state_id = 2,
                mr_cluster = self.Parameters.mr_cluster,
                mr_path_1 = ypath_join(self.Context.yt_path, "dataset1_binary2"),
                mr_path_2 = ypath_join(self.Context.yt_path, "dataset2_binary2"),
                mr_states_cache_path = self.Parameters.mr_states_cache_path,
            )


            task2.enqueue()
            self.Context.merge_states_subtasks.append(task2.id)

            raise sdk2.WaitTask(self.Context.merge_states_subtasks, ctt.Status.Group.FINISH | ctt.Status.Group.BREAK)


        with self.memoize_stage.step3:
            for task_id in self.Context.merge_states_subtasks:
                if sdk2.Task[task_id].status not in ctt.Status.Group.SUCCEED:
                    raise TaskFailure("Child task failed")
            logging.info("Sampling diff")

            task = TestCvdupSampleDiff(
                self,
                description='launched from TestCvdupAllStages',
                kill_timeout= 80 * 3600,
                dataset_path1 = self.Parameters.dataset_path1,
                dataset_path2 = self.Parameters.dataset_path2,
                sampling_tool_binary = self.Parameters.sampling_tool_binary,
                diff_count = self.Parameters.diff_count,
                max_sample_count = self.Parameters.max_sample_count,
                image_extractor_tool_binary = self.Parameters.image_extractor_tool_binary,
                mr_cluster = self.Parameters.mr_cluster,
                mr_path = self.Context.yt_path,
                mr_path_1 = ypath_join(self.Context.yt_path, "dataset2_binary1"),
                mr_path_2 = ypath_join(self.Context.yt_path, "dataset2_binary2"),
                mds_api_host = self.Parameters.mds_api_host,
                mds_host = self.Parameters.mds_host,
                mds_namespace = self.Parameters.mds_namespace,
            )
            task.enqueue()
            self.Context.sample_diff_task_id = task.id
            raise sdk2.WaitTask(task.id, ctt.Status.Group.FINISH | ctt.Status.Group.BREAK)


        with self.memoize_stage.step4:
            if sdk2.Task[self.Context.sample_diff_task_id].status not in ctt.Status.Group.SUCCEED:
                raise TaskFailure("Child task failed")
            self.Context.url_pairs_resource_id = sdk2.Resource.find(task_id=self.Context.sample_diff_task_id, resource_type=resource_types_cvdup.CvdupAcceptanceImageUrlPairsJson, state="READY").first().id

            logging.info("Estimating results in toloka...")

            task = TestCvdupTolokaEstimating(
                self,
                description='launched from TestCvdupAllStages',
                kill_timeout= 80 * 3600,
                nirvana_api_host = self.Parameters.nirvana_api_host,
                nirvana_workflow_id = self.Parameters.labeling_nirvana_workflow_id,
                nirvana_workflow_instance_id = self.Parameters.labeling_nirvana_workflow_instance_id,
                url_pairs_json = self.Context.url_pairs_resource_id
            )
            task.enqueue()
            self.Context.toloka_estimates_task_id = task.id
            raise sdk2.WaitTask(task.id, ctt.Status.Group.FINISH | ctt.Status.Group.BREAK)

        with self.memoize_stage.step5:
            if sdk2.Task[self.Context.toloka_estimates_task_id].status not in ctt.Status.Group.SUCCEED:
                raise TaskFailure("Child task failed")
            self.Context.toloka_estimates_portion_id = sdk2.Resource.find(task_id=self.Context.toloka_estimates_task_id, resource_type=resource_types_cvdup.CvdupAcceptanceTolokaEstimatesJson, state="READY").first().id

            logging.info("Loading toloka estimates to yt table...")

            task = TestCvdupLoadTolokaEstimates(
                self,
                description='launched from TestCvdupAllStages',
                kill_timeout= 8 * 3600,
                nirvana_api_host = self.Parameters.nirvana_api_host,
                nirvana_workflow_id = self.Parameters.load_estimates_nirvana_workflow_id,
                nirvana_workflow_instance_id = self.Parameters.load_estimates_nirvana_workflow_instance_id,
                output_table_path = self.Context.yt_path_toloka_estimates
            )
            task.enqueue()
            self.Context.load_toloka_estimates_task_id = task.id
            raise sdk2.WaitTask(task.id, ctt.Status.Group.FINISH | ctt.Status.Group.BREAK)

        with self.memoize_stage.step6:
            if sdk2.Task[self.Context.load_toloka_estimates_task_id].status not in ctt.Status.Group.SUCCEED:
                raise TaskFailure("Child task failed")

            logging.info("Calculating metrics first...")

            task = TestCvdupCalculateMetrics(
                self,
                description='launched from TestCvdupAllStages',
                kill_timeout= 4 * 3600,
                state_path = ypath_join(self.Context.yt_path, "dataset2_binary1"),
                toloka_estimates_portion_json = self.Context.toloka_estimates_portion_id,
                toloka_estimates_table = self.Context.yt_path_toloka_estimates,
                images_cvdup_acceptance_util_binary = self.Parameters.images_cvdup_acceptance_util_binary,
                mr_cluster = self.Parameters.mr_cluster,
            )
            task.enqueue()
            self.Context.state_metrics_first_task_id = task.id
            raise sdk2.WaitTask(task.id, ctt.Status.Group.FINISH | ctt.Status.Group.BREAK)

        with self.memoize_stage.step7:
            if sdk2.Task[self.Context.state_metrics_first_task_id].status not in ctt.Status.Group.SUCCEED:
                raise TaskFailure("Child task failed")

            logging.info("Calculating metrics second...")

            task = TestCvdupCalculateMetrics(
                self,
                description='launched from TestCvdupAllStages',
                kill_timeout= 4 * 3600,
                state_path = ypath_join(self.Context.yt_path, "dataset2_binary2"),
                toloka_estimates_portion_json = self.Context.toloka_estimates_portion_id,
                toloka_estimates_table = self.Context.yt_path_toloka_estimates,
                images_cvdup_acceptance_util_binary = self.Parameters.images_cvdup_acceptance_util_binary,
                mr_cluster = self.Parameters.mr_cluster,
            )
            task.enqueue()
            self.Context.state_metrics_second_task_id = task.id
            raise sdk2.WaitTask(task.id, ctt.Status.Group.FINISH | ctt.Status.Group.BREAK)

        with self.memoize_stage.step8:
            if sdk2.Task[self.Context.state_metrics_second_task_id].status not in ctt.Status.Group.SUCCEED:
                raise TaskFailure("Child task failed")
            self.Context.state_metrics_first_id = sdk2.Resource.find(task_id=self.Context.state_metrics_first_task_id, resource_type=resource_types_cvdup.CvdupAcceptanceStateMetricsJson, state="READY").first().id
            self.Context.state_metrics_second_id = sdk2.Resource.find(task_id=self.Context.state_metrics_second_task_id, resource_type=resource_types_cvdup.CvdupAcceptanceStateMetricsJson, state="READY").first().id

            logging.info("Estimating results...")

            task = TestCvdupCheckMetrics(
                self,
                description='launched from TestCvdupAllStages',
                kill_timeout= 2 * 3600,
                stable_state_metrics_json = self.Context.state_metrics_first_id,
                branch_state_metrics_json = self.Context.state_metrics_second_id,
                startrack_ticket_id = self.Parameters.startrack_ticket_id
            )
            task.enqueue()
            self.Context.check_metrics_task_id = task.id
            raise sdk2.WaitTask(task.id, ctt.Status.Group.FINISH | ctt.Status.Group.BREAK)

        with self.memoize_stage.step9:
            if sdk2.Task[self.Context.check_metrics_task_id].status not in ctt.Status.Group.SUCCEED:
                raise TaskFailure("Child task failed")

            logging.info("Cleaning data from old launches...")

            task = TestCvdupCleanOldAllStagesLaunchesData(
                self,
                description='launched from TestCvdupAllStages',
                kill_timeout= 2 * 3600,
                mr_path = self.Parameters.mr_path_base,
                num_launches = 8
            )
            task.enqueue()
            self.Context.clean_task_id = task.id
            raise sdk2.WaitTask(task.id, ctt.Status.Group.FINISH | ctt.Status.Group.BREAK)

        with self.memoize_stage.step10:
            if sdk2.Task[self.Context.clean_task_id].status not in ctt.Status.Group.SUCCEED:
                raise TaskFailure("Child task failed")

            logging.info("Cleaning cache...")

            task = TestCvdupCleanCache(
                self,
                description='launched from TestCvdupAllStages',
                kill_timeout= 2 * 3600,
                mr_path = self.Parameters.mr_states_cache_path,
                num_binaries = 15
            )
            task.enqueue()
            self.Context.clean_cache_task_id = task.id
            raise sdk2.WaitTask(task.id, ctt.Status.Group.FINISH | ctt.Status.Group.BREAK)

        with self.memoize_stage.step11:
            logging.info("Checking subtask...")
            if sdk2.Task[self.Context.clean_cache_task_id].status not in ctt.Status.Group.SUCCEED:
                raise TaskFailure("Child task failed")

        logging.info("Finished succesfully")

