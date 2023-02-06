# coding=utf-8

import sys
import logging

import sandbox.sandboxsdk.svn as sdk_svn
import sandbox.sandboxsdk.task as sdk_task
import sandbox.sandboxsdk.parameters as sdk_parameters
import json
import collections


def LoadJSON(path):
    return json.load(file(path, "rt"), object_pairs_hook=collections.OrderedDict)


class Task(sdk_task.SandboxTask):
    """ An empty task, which does nothing except of greets you. """

    class MrLocalOpId(sdk_parameters.ResourceSelector):
        name = 'mr_local_op_id'
        description = 'Train Matrixnet on CPU MR LOCAL Operation id'
        resource_type = 'TRAIN_MATRIXNET_ON_CPU_MR_LOCAL_OP'
        required = True

    class OldMrLocalOpId(sdk_parameters.SandboxStringParameter):
        name = "old_mr_local_op_id"
        description = "Train Matrixnet on CPU MR LOCAL Operation id to be replaced at test"

    class MrLocalTestSnapshot(sdk_parameters.ResourceSelector):
        name = 'mr_local_test_snapshot'
        description = 'Train Matrixnet on CPU MR LOCAL Operation id test workflow snapshot'
        resource_type = 'NIRVANA_WORKFLOW_SNAPSHOT'
        required = True

    class MrMsOpId(sdk_parameters.ResourceSelector):
        name = 'mr_ms_op_id'
        description = 'Train Matrixnet on CPU MR MS Operation id'
        resource_type = 'TRAIN_MATRIXNET_ON_CPU_MR_MS_OP'
        required = True

    class OldMrMsOpId(sdk_parameters.SandboxStringParameter):
        name = "old_mr_ms_op_id"
        description = "Train Matrixnet on CPU MR MS Operation id to be replaced at test"

    class MrMSTestSnapshot(sdk_parameters.ResourceSelector):
        name = 'mr_ms_test_snapshot'
        description = 'Train Matrixnet on CPU MR MS Operation id test workflow snapshot'
        resource_type = 'NIRVANA_WORKFLOW_SNAPSHOT'
        required = True

    class TsvLocalOpId(sdk_parameters.ResourceSelector):
        name = 'tsv_local_op_id'
        description = 'Train Matrixnet on CPU TSV LOCAL Operation id'
        resource_type = 'TRAIN_MATRIXNET_ON_CPU_TSV_LOCAL_OP'
        required = True

    class OldTsvLocalOpId(sdk_parameters.SandboxStringParameter):
        name = "old_tsv_local_op_id"
        description = "Train Matrixnet on CPU TSV LOCAL Operation id to be replaced at test"

    class TsvLocalTestSnapshot(sdk_parameters.ResourceSelector):
        name = 'tsv_local_test_snapshot'
        description = 'Train Matrixnet on CPU TSV LOCAL Operation id test workflow snapshot'
        resource_type = 'NIRVANA_WORKFLOW_SNAPSHOT'
        required = True

    class TsvMsOpId(sdk_parameters.ResourceSelector):
        name = 'tsv_ms_op_id'
        description = 'Train Matrixnet on CPU TSV MS Operation id'
        resource_type = 'TRAIN_MATRIXNET_ON_CPU_TSV_MS_OP'
        required = True

    class OldTsvMsOpId(sdk_parameters.SandboxStringParameter):
        name = "old_tsv_ms_op_id"
        description = "Train Matrixnet on CPU TSV MS Operation id to be replaced at test"

    class TsvMSTestSnapshot(sdk_parameters.ResourceSelector):
        name = 'tsv_ms_test_snapshot'
        description = 'Train Matrixnet on CPU TSV MS Operation id test workflow snapshot'
        resource_type = 'NIRVANA_WORKFLOW_SNAPSHOT'
        required = True

    class NivranaTokenName(sdk_parameters.SandboxStringParameter):
        name = "nirvana_token"
        description = "Vault with Nirvana Token"

    class TestNamePrefix(sdk_parameters.SandboxStringParameter):
        name = "test_name"
        description = "Common name prefix for tests"

    class StartrekTicket(sdk_parameters.SandboxStringParameter):
        name = "startrek_ticket"
        description = "startrek ticket for report generation"

    class StTokenName(sdk_parameters.SandboxStringParameter):
        name = "startrek_token"
        description = "Vault with Startrek Token"

    type = "TEST_TRAIN_MATRIXNET_ON_CPU"
    input_parameters = [
        MrLocalOpId,
        OldMrLocalOpId,
        MrLocalTestSnapshot,
        MrMsOpId,
        OldMrMsOpId,
        MrMSTestSnapshot,
        TsvLocalOpId,
        OldTsvLocalOpId,
        TsvLocalTestSnapshot,
        TsvMsOpId,
        OldTsvMsOpId,
        TsvMSTestSnapshot,
        NivranaTokenName,
        TestNamePrefix,
        StartrekTicket,
        StTokenName,
    ]

    def MakeStartrekComment(
        self,
        startrek_api_token, ticket_id,
        new_mr_ms_op_id, new_mr_local_op_id, new_tsv_ms_op_id, new_tsv_local_op_id,
        mr_ms_wfid, mr_local_wfid, tsv_ms_wfid, tsv_local_wfid
    ):

        import startrack_api
        import get_file_strategy
        import get_file

        operations_table = """
  * MR/MS {mr_ms}
    * {mr_ms_wfid}
  * MR/LOCAL {mr_local}
    * {mr_local_wfid}
  * TSV/MS {tsv_ms}
    * {tsv_ms_wfid}
  * TSV/LOCAL {tsv_local}
    * {tsv_local_wfid}
"""

        def make_url_for_operation(opid):
            return "https://nirvana.yandex-team.ru/operation/{0}/overview".format(opid)

        def make_url_for_wf(wfid):
            return "https://nirvana.yandex-team.ru/flow/{0}/graph".format(wfid)

        op_data = {'mr_ms': make_url_for_operation(new_mr_ms_op_id),
                   'mr_local': make_url_for_operation(new_mr_local_op_id),
                   'tsv_ms': make_url_for_operation(new_tsv_ms_op_id),
                   'tsv_local': make_url_for_operation(new_tsv_local_op_id),
                   'mr_ms_wfid': make_url_for_wf(mr_ms_wfid),
                   'mr_local_wfid': make_url_for_wf(mr_local_wfid),
                   'tsv_ms_wfid': make_url_for_wf(tsv_ms_wfid),
                   'tsv_local_wfid': make_url_for_wf(tsv_local_wfid),
                   }

        logging.info(operations_table.format(**op_data))

        comment_helper = startrack_api.Comments(ticket_id, startrek_api_token, get_file_strategy=get_file_strategy.return_get_file_class(get_file.GetFile))
        logging.info(comment_helper.POST(operations_table.format(**op_data)))

    def on_execute(self):
        sys.path.append(sdk_svn.Arcadia.get_arcadia_src_dir("arcadia:/arc/trunk/arcadia/quality/relev_tools/conveyor_dashboard/commons"))
        # import nirvana_api
        import nirvana_workflow_helper

        nv_token = self.get_vault_data(self.ctx.get(self.NivranaTokenName.name))
        name_prefix = self.ctx.get(self.TestNamePrefix.name)

        def get_new_op_id(param_resource):
            op_path = self.sync_resource(self.ctx[param_resource])
            op_json = LoadJSON(op_path)
            op_id = op_json['op_id']
            return op_id

        def foo(test_snapshot_name, old_op_id_name, new_op_id_name, name_suffix):
            test_snapshot_path = self.sync_resource(self.ctx[test_snapshot_name])
            test_snapshot_json = LoadJSON(test_snapshot_path)
            old_op_id = self.ctx.get(old_op_id_name)
            new_op_id = get_new_op_id(new_op_id_name)
            test_snapshot_helper = nirvana_workflow_helper.NirvanaDumpHelper(test_snapshot_json)
            test_snapshot_helper.ReplaceOpId(old_op_id, new_op_id)
            builder = nirvana_workflow_helper.NirvanaBuilder(nv_token, name_prefix + ' ' + name_suffix, test_snapshot_helper.GetJson())
            builder.Create()
            builder.Run()
            return new_op_id, builder

        logging.info("Building MR LOCAL test...")
        new_mr_local_op_id, mr_local_builder = foo(
            'mr_local_test_snapshot',
            self.OldMrLocalOpId.name,
            'mr_local_op_id',
            "MR LOCAL")

        logging.info("Building MR MS test...")
        new_mr_ms_op_id, mr_ms_builder = foo(
            'mr_ms_test_snapshot',
            self.OldMrMsOpId.name,
            'mr_ms_op_id',
            "MR MS")
        logging.info("Building TSV LOCAL test...")
        new_tsv_local_op_id, tsv_local_builder = foo(
            'tsv_local_test_snapshot',
            self.OldTsvLocalOpId.name,
            'tsv_local_op_id',
            "TSV LOCAL")

        logging.info("Building TSV MS test...")
        new_tsv_ms_op_id, tsv_ms_builder = foo(
            'tsv_ms_test_snapshot',
            self.OldTsvMsOpId.name,
            'tsv_ms_op_id',
            "TSV MS")

        mr_local_builder.Join()
        mr_ms_builder.Join()
        tsv_local_builder.Join()
        tsv_ms_builder.Join()

        st_token = self.get_vault_data(self.ctx[self.StTokenName.name])
        ticket_id = self.ctx[self.StartrekTicket.name]

        self.MakeStartrekComment(
            st_token, ticket_id,
            new_mr_ms_op_id, new_mr_local_op_id, new_tsv_ms_op_id, new_tsv_local_op_id,
            mr_ms_builder.new_api.wfId, mr_local_builder.new_api.wfId, tsv_ms_builder.new_api.wfId, tsv_local_builder.new_api.wfId
        )


__Task__ = Task
