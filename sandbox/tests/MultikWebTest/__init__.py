import os

from sandbox import sdk2
from sandbox.common.errors import TaskFailure
from sandbox.common.types.misc import DnsType
from sandbox.projects.common import link_builder as lb
from sandbox.projects.common import binary_task
from sandbox.projects.common import gsid_parser
from sandbox.sandboxsdk import environments
import sandbox.projects.release_machine.tasks.base_task as rm_bt
import sandbox.projects.release_machine.input_params2 as rm_params


class MultikWebTest(rm_bt.BaseReleaseMachineTask):
    class Requirements(sdk2.Task.Requirements):
        dns = DnsType.DNS64

        environments = [
            environments.NodeJS('10.20.1'),
            environments.GCCEnvironment(version='5.3.0'),
        ]

    class Context(rm_bt.BaseReleaseMachineTask.Context):
        test_status = None
        report_keys = []
        report_header = {}
        report = []

    class Parameters(rm_params.ComponentName2):
        with sdk2.parameters.RadioGroup('Logging level') as log_level:
            log_level.values['INFO'] = log_level.Value(value='INFO', default=True)
            log_level.values['ERROR'] = log_level.Value(value='ERROR')
            log_level.values['DEBUG'] = log_level.Value(value='DEBUG')

        result_revision = sdk2.parameters.String('Arcadia revision', default=None, required=False)
        checkout_arcadia_from_url = sdk2.parameters.String(
            'Svn url for arc with revision', default=sdk2.svn.Arcadia.ARCADIA_TRUNK_URL, required=True
        )

        ext_params = binary_task.binary_release_parameters(stable=True)

        arcadia_patch = sdk2.parameters.String('Apply patch (text diff or rbtorrent)', multiline=True, default='')

    def _prepare_env(self):
        """
        Calling prepare for environments

        :return:
        """
        for env in self.Requirements.environments:
            env.prepare()

    def on_execute(self):
        rm_bt.BaseReleaseMachineTask.on_execute(self)
        self._prepare_env()

        os.environ['MULTIK_LOG_LEVEL'] = self.Parameters.log_level
        os.environ['YENV_TYPE'] = 'testing'

        import april.multik.stand.integration_tests.precommit as precommit_test
        import april.multik.stand.integration_tests.lib as integration_tests

        test = precommit_test.PrecommitTest(self.Parameters.checkout_arcadia_from_url, self.Parameters.arcadia_patch)
        test.run()
        self.Context.report_keys, self.Context.report_header, self.Context.report = test.report
        self.set_info(test.html(), do_escape=False)
        self.Context.test_status = test.status.name

        if test.status != integration_tests.TestStatus.OK and test.status != integration_tests.TestStatus.WARN:
            raise TaskFailure('Test failed')

    def _get_rm_proto_event_specific_data(self, rm_proto_events, event_time_utc_iso, status=None):
        from release_machine.common_proto import test_results_pb2 as rm_test_results
        from integration_tests import TestStatus
        import irt.utils

        test_result_status = {
            TestStatus.OK.name: rm_test_results.TestResult.TestStatus.OK,
            TestStatus.WARN.name: rm_test_results.TestResult.TestStatus.WARN,
            TestStatus.CRIT.name: rm_test_results.TestResult.TestStatus.CRIT,
            TestStatus.UB.name: rm_test_results.TestResult.TestStatus.UB,
            TestStatus.ONGOING.name: rm_test_results.TestResult.TestStatus.ONGOING,
        }.get(self.Context.test_status, rm_test_results.TestResult.TestStatus.ONGOING)

        return {
            "generic_test_data": rm_proto_events.GenericTestData(
                job_name=unicode(self.get_job_name_from_gsid()),
                scope_number=u'0',
                revision=unicode(gsid_parser.get_svn_revision_from_gsid(self.Context.__GSID) or "0"),
                test_result=rm_test_results.TestResult(
                    status=test_result_status,
                    task_link=lb.task_link(self.id, plain=True),
                    report_table=rm_test_results.Table(
                        header=rm_test_results.TableRow(
                            cells=[rm_test_results.TableCell(content=unicode(self.Context.report_header[key])) for key in self.Context.report_keys]
                        ),
                        rows=[
                            rm_test_results.TableRow(
                                cells=[rm_test_results.TableCell(
                                    content=unicode(irt.utils.strip_html(row[key]))
                                ) for key in self.Context.report_keys]
                            ) for row in self.Context.report
                        ]
                    )
                )
            )
        }
