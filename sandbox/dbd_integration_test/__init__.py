# coding=utf-8

import sys
import time
import logging

import sandbox.sandboxsdk.svn as sdk_svn
import sandbox.sandboxsdk.environments as sdk_environments
from sandbox import sdk2


class RunDbdIntegrationTest(sdk2.Task):
    class Requirements(sdk2.Task.Requirements):
        environments = (
            sdk_environments.PipEnvironment('graphviz'),
            sdk_environments.PipEnvironment('enum'),
            sdk_environments.PipEnvironment('ujson'),
        )

    class Parameters(sdk2.Task.Parameters):
        nirvana_token = sdk2.parameters.String("Vault with Nirvana Token", required=True)
        nirvana_quota = sdk2.parameters.String("Nirvana quota", default_value="default", required=True)

        fake = sdk2.parameters.Bool(
            "fake",
            required=True,
            default=True,
        )

        fake_screenshot = sdk2.parameters.Bool(
            "fake_screenshot",
            required=True,
            default=True,
        )

        epoch_prefix = sdk2.parameters.String(
            "epoch_prefix",
            required=True,
            default='test_epoch',
        )

        queries_group_prefix = sdk2.parameters.String(
            "queries_group_prefix",
            required=True,
            default="test_queries_group",
        )

        tags_prefix = sdk2.parameters.String(
            "tags_prefix",
            required=True,
            default="integration_test_tag",
        )

        hitman_job_id_prefix = sdk2.parameters.String(
            "hitman_job_id_prefix",
            required=True,
            default="sandbox_driven_dbd_integration_test",
        )

        requester = sdk2.parameters.String(
            "requester",
            required=True,
            default="ibrishat",
        )

        create_control_points_workflow_id = sdk2.parameters.String(
            "DbD Create Control Points Nirvana workflow id",
            description="New workflow will be copied from this one",
            required=True,
        )

        create_control_points_input_block = sdk2.parameters.String(
            "Create Control Point graph entry block",
            required=True,
        )

        create_control_points_input = sdk2.parameters.String(
            "Create Control Point graph entry block input",
            required=True,
        )

        create_control_points_global_params = sdk2.parameters.Dict(
            "Create Control Point graph global options",
        )

        create_control_points_input_data_id = sdk2.parameters.String(
            "Create Control Point graph input data",
            required=True,
        )

        evaluate_bt_scores_workflow_id = sdk2.parameters.String(
            "DbD Evaluate BT scores Nirvana workflow id",
            description="New workflow will be copied from this one",
            required=True,
        )

        evaluate_bt_scores_input_block = sdk2.parameters.String(
            "Evaluate BT scores graph entry block",
            required=True,
        )

        evaluate_bt_scores_input = sdk2.parameters.String(
            "Evaluate BT scores graph entry block input",
            required=True,
        )

        evaluate_bt_scores_global_params = sdk2.parameters.Dict(
            "Evaluate BT scores graph global options",
        )

        evaluate_bt_scores_input_data_id = sdk2.parameters.String(
            "Evaluate BT scores graph input data",
            required=True,
        )

        with sdk2.parameters.Output:
            executed_create_control_points_workflow_id = sdk2.parameters.String(
                "Executed Create Control Points workflow id",
            )
            executed_create_control_points_workflow_url = sdk2.parameters.Url(
                "Executed Create Control Points workflow",
            )
            executed_evaluate_bt_score_workflow_id = sdk2.parameters.String(
                "Executed Evaluate BT Score workflow id",
            )
            executed_evaluate_bt_score_workflow_url = sdk2.parameters.Url(
                "Executed Evaluate BT Score workflow",
            )

    @staticmethod
    def build_workflow_url(workflow_id):
        return "https://nirvana.yandex-team.ru/flow/{}/graph".format(workflow_id) if workflow_id else None

    def run_test_workflow(
            self,
            nirvana,
            template_workflow_id,
            nirvana_workflow_name,
            nirvana_quota,
            global_params,
            input_data_id,
            input_block,
            dest_input,
            is_create_control_points,
            ts_str,
    ):
        from utils.nirvana_api import NirvanaFlowResult

        wf_id = nirvana.clone_workflow(src_workflow_id=template_workflow_id, new_name=nirvana_workflow_name,
                                       new_quota_project_id=nirvana_quota)
        nirvana.update_workflow(workflow_id=wf_id)
        if is_create_control_points:
            self.Parameters.executed_create_control_points_workflow_id = wf_id
            self.Parameters.executed_create_control_points_workflow_url = RunDbdIntegrationTest.build_workflow_url(wf_id)
        else:
            self.Parameters.executed_evaluate_bt_score_workflow_id = wf_id
            self.Parameters.executed_evaluate_bt_score_workflow_url = RunDbdIntegrationTest.build_workflow_url(wf_id)

        params = {
            "fake": self.Parameters.fake,
            "fake_screenshot": self.Parameters.fake_screenshot,
            "queriesGroupIds": '["{0}_{1}"]'.format(self.Parameters.queries_group_prefix, ts_str),
            "tags": '["{0}_{1}"]'.format(self.Parameters.tags_prefix, ts_str),
            "hitman_job_id": '{0}'.format(ts_str),
            "epoch": '{0}_{1}'.format(self.Parameters.epoch_prefix, ts_str),
            "ts_cache": ts_str,
            "requester": self.Parameters.requester
        }
        if global_params:
            for key, value in global_params.iteritems():
                if key == 'fake':
                    value = value == 'True' or value == 'true'
                if key in {'metrics_priority', 'pool-priority', 'priority_for_tellurium'}:
                    value = int(value)
                params[key] = value

        nirvana.set_global_parameters(workflow_id=wf_id, global_parameters=params)

        data_block_code = "INPUT_DATA"
        nirvana.add_data_block(workflow_id=wf_id, data_id=input_data_id, block_code=data_block_code)
        nirvana.connect_data_blocks(workflow_id=wf_id, source_block_codes=[data_block_code], dest_block_codes=[input_block],
                                    dest_inputs=[dest_input])
        nirvana.start_workflow(workflow_id=wf_id)
        result, full_state = nirvana.wait_for_workflow_completion(workflow_id=wf_id, wait_timeout=4 * 3600)
        logging.info("Workflow result = %s", result)
        logging.info("Workflow state = %s", full_state)
        if result != NirvanaFlowResult.SUCCESS:
            raise Exception("Workflow {} failed [{}]".format(wf_id, full_state["details"]))

    def on_execute(self):
        sys.path.append(
            sdk_svn.Arcadia.get_arcadia_src_dir("arcadia:/arc/trunk/arcadia/quality/yaqlib")
        )
        from utils.nirvana_api import NirvanaProxy
        nirvana = NirvanaProxy(token=sdk2.Vault.data(self.Parameters.nirvana_token))

        ts_str = str(int(time.time()) * 1000)

        # run create control points graph
        self.run_test_workflow(
            nirvana,
            self.Parameters.create_control_points_workflow_id,
            'DbD Create control point Integration test',
            self.Parameters.nirvana_quota,
            self.Parameters.create_control_points_global_params,
            self.Parameters.create_control_points_input_data_id,
            self.Parameters.create_control_points_input_block,
            self.Parameters.create_control_points_input,
            True,
            ts_str,
        )

        # run evaluate BT scores graph
        self.run_test_workflow(
            nirvana,
            self.Parameters.evaluate_bt_scores_workflow_id,
            'DbD Evaluate BT scores Integration test',
            self.Parameters.nirvana_quota,
            self.Parameters.evaluate_bt_scores_global_params,
            self.Parameters.evaluate_bt_scores_input_data_id,
            self.Parameters.evaluate_bt_scores_input_block,
            self.Parameters.evaluate_bt_scores_input,
            False,
            ts_str,
        )
