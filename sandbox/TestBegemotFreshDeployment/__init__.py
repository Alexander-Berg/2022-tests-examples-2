import os
import json
import time
from datetime import datetime

from sandbox import sdk2
from sandbox.projects.websearch.begemot import parameters as bp
from sandbox.projects.websearch.begemot import resources as br
from sandbox.projects.websearch.begemot.tasks.ReleaseBegemotFresh import build_fast_data_config
from sandbox.projects.common.nanny.client import NannyClient, SandboxFileUpdate, StaticFileUpdate
from sandbox.projects.websearch.upper import resources as upper_resources
from sandbox.projects.websearch.upper.fast_data.DeployFastData import DeployFastData
from sandbox.common.config import Registry
from sandbox.common.errors import TaskFailure
from sandbox.common.types.misc import Installation
from sandbox.common.types.task import Status


NANNY_API_URL = 'http://nanny.yandex-team.ru/'


class TestCases:
    COREDUMP_IN_RUNTIME = 'Coredump in runtime'
    COREDUMP_ON_RELOAD = 'Coredump on reload'


class TestBegemotFreshDeployment(sdk2.Task):
    class Parameters(sdk2.Parameters):
        testing_service = sdk2.parameters.String(
            'Testing service',
            required=True,
            default='begemot_bstr_testing_servant',
        )

        begemot_binary = bp.BegemotExecutableResource()
        fast_build_config = bp.FastBuildConfigResource(required=True)

        bstr_caller = sdk2.parameters.Resource(
            'Bstr caller binary',
            required=True,
            resource_type=br.BEGEMOT_BSTR_CALLER,
        )

        callback = sdk2.parameters.Resource(
            'Callback binary',
            required=True,
            resource_type=br.BEGEMOT_FAST_DATA_CALLBACK,
        )

        deployer = sdk2.parameters.Resource(
            'Deployer binary',
            required=False,
            resource_type=upper_resources.FastDataDeployer,
        )

        nanny_token = sdk2.parameters.String(
            'Nanny token vault name for the owner',
            required=True,
            default='Begemot Nanny token',
        )

        yt_token = sdk2.parameters.String(
            'Yt token vault name for the owner',
            required=True,
            default='yt_token_for_testenv',
        )

        time_to_wait = sdk2.parameters.Integer(
            'Time to wait for service or fresh deployment in each test case, seconds',
            required=True,
            default=600,
        )

        test_stop_deploy = sdk2.parameters.Bool(
            'Check that deployment stops with bad fresh',
            default=False,
        )

        test_restore = sdk2.parameters.Bool(
            'Check that service will be restored after bad fresh',
            default=True,
        )

    class Context(sdk2.Context):
        fail_test = False

    def _wait_for_deployment(self, nanny_client, service):
        time_left = self.Parameters.time_to_wait
        while time_left > 0:
            time.sleep(60)
            time_left -= 60
            state = nanny_client.get_service_current_state(service)['content']['summary']['value']
            if state == 'ONLINE':
                self.set_info('Service {} activated'.format(service))
                return True

        return False

    def update_nanny_service(self, service, nanny_client):
        if Registry().common.installation == Installation.LOCAL:
            # For local sandbox
            sandbox_updates = {
                'bstr_caller':SandboxFileUpdate(
                    local_path='bstr_caller',
                    resource_id='2594345862',
                    resource_type='BEGEMOT_BSTR_CALLER',
                    task_id='1141971273',
                    task_type='RELEASE_BEGEMOT_RESOURCES',
                )
            }
        else:
            resources = {
                'begemot': self.Parameters.begemot_binary,
                'BEGEMOT_FAST_BUILD_CONFIG_FAKE_SHARD': self.Parameters.fast_build_config,
                'bstr_caller': self.Parameters.bstr_caller,
                'fast_data_callback': self.Parameters.callback,
            }
            sandbox_updates = {name : SandboxFileUpdate(
                local_path=name,
                resource_id=str(res.id),
                resource_type=str(res.type),
                task_id=str(res.task.id),
                task_type=str(res.task.type),
            ) for name, res in resources.items()}

        static_updates = {
            'zerodiff': StaticFileUpdate(
                local_path='zerodiff',
                content=str(time.time()),
            )
        }
        comment = 'Updated by TEST_BEGEMOT_FRESH_DEPLOYMENT task #{}'.format(self.id)

        snapshot_id = nanny_client.update_service_files(service, sandbox_updates, static_updates, comment=comment)['runtime_attrs']['_id']
        self.set_info('Created snapshot with id {} for service {}'.format(snapshot_id, service))

        nanny_client.set_snapshot_state(
            service_id=service,
            snapshot_id=snapshot_id,
            state='ACTIVE',
            comment='By task #{}'.format(self.id),
            recipe='default',
            prepare_recipe='default',
            set_as_current=True,
        )

        return self._wait_for_deployment(nanny_client, service)

    def _build_fresh_for_rule(self, rulename, work_path, start_delay_seconds, coredump, runtime_coredump):
        rule_path = os.path.join(work_path, rulename)
        os.mkdir(rule_path)
        with open(os.path.join(rule_path, 'config.pb.txt'), 'w') as f:
            f.write('StartDelaySeconds: {}\n'.format(start_delay_seconds))
            f.write('CoreDump: {}\n'.format(coredump))
            f.write('RuntimeCoreDump: {}\n'.format(runtime_coredump))

        rule_data = br.BEGEMOT_FAST_BUILD_RULE_DATA(
            self,
            '{} fresh with coredump={}, runtime_coredump={}'.format(rulename, coredump, runtime_coredump),
            rule_path
        )
        sdk2.ResourceData(rule_data).ready()
        return rule_data

    def build_fresh_resource(self, start_delay_seconds=5, coredump=False, runtime_coredump=False, with_another_rule=False):
        timestamp = int(time.time())
        work_path = 'data_{}'.format(timestamp)
        os.mkdir(work_path)
        rule_data = self._build_fresh_for_rule('FakeDep2', work_path, start_delay_seconds, coredump, runtime_coredump)
        if with_another_rule:
            another_rule_data = self._build_fresh_for_rule('FakeDep', work_path, start_delay_seconds, coredump, runtime_coredump)

        config_path = os.path.join(work_path, 'fast_build_config.json')
        resources_list = [] if not with_another_rule else [
            {
                'name': 'FakeDep',
                'torrent': another_rule_data.skynet_id,
            }
        ]
        content = {
            'shard_name': 'ALL_SHARDS_FRESH',
            'resources': resources_list + [
                {
                    'name': 'FakeDep2',
                    'torrent': rule_data.skynet_id,
                }
            ],
            'version_info': {
                'ShardName': '"ALL_SHARDS_FRESH"',
                'Task': self.id,
                'GenerationTime': '"{}"'.format(datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')),
                'Revision': str(timestamp),
            }
        }
        with open(config_path, 'w') as f:
            f.write(json.dumps(content))

        fresh_resource = br.BEGEMOT_FAST_BUILD_FRESH_CONFIG(
            self,
            'Fresh from task #{} with coredump={}, runtime_coredump={}'.format(self.id, coredump, runtime_coredump),
            config_path,
            version=timestamp,
        )
        sdk2.ResourceData(fresh_resource).ready()
        return fresh_resource.id

    def deploy_fresh(self, service, resource_id, prepare_dl=None):
        if prepare_dl is None:
            config = build_fast_data_config([service], '//home/search-runtime/fast-data/begemot')  # Use default prepare dl from ReleaseBegemotFresh
        else:
            config = build_fast_data_config([service], '//home/search-runtime/fast-data/begemot', prepare_dl=prepare_dl)

        deployer = self.Parameters.deployer
        if not deployer:
            deployer = sdk2.Resource['FAST_DATA_DEPLOYER'].find(state='READY', attrs={'released': 'stable'}).first()

        task_id = DeployFastData(
            self,
            fast_data_bundle=resource_id,
            deployer_mode='standalone',
            yt_token_name=self.Parameters.yt_token,
            nanny_token_name=self.Parameters.nanny_token,
            deployer=deployer,
            deploy_config=config,
            kill_timeout=self.Parameters.time_to_wait,
        ).enqueue().id
        return task_id

    def check_child_status(self, task_id, expected_status):
        task = sdk2.Task.find(id=task_id, children=True).first()
        return task.status == expected_status

    def on_execute(self):
        if 'prod' in self.Parameters.testing_service or 'hamster' in self.Parameters.testing_service:
            raise 'Task will not run for service with "prod" or "hamster" in its name.'

        nanny_client = NannyClient(NANNY_API_URL, sdk2.Vault.data(self.Parameters.nanny_token))

        for test_case in [TestCases.COREDUMP_ON_RELOAD, TestCases.COREDUMP_IN_RUNTIME]:
            with self.memoize_stage['update_service' + str(test_case)](commit_on_entrance=False):
                self.set_info('Starting test case "{}"'.format(test_case))
                self.Context.good_fresh_id = self.build_fresh_resource(60, False, False)
                task_id = self.deploy_fresh(self.Parameters.testing_service, self.Context.good_fresh_id, prepare_dl=1.0)
                ok = self.update_nanny_service(self.Parameters.testing_service, nanny_client)
                if not ok:
                    raise TaskFailure('Service {} failed to deploy in {} seconds. Input resources are bad or timeout is too small'.format(self.Parameters.testing_service, self.Parameters.time_to_wait))

            with self.memoize_stage['push_bad_fresh' + str(test_case)](commit_on_entrance=False):
                bad_fresh_id = self.build_fresh_resource(60, test_case == TestCases.COREDUMP_ON_RELOAD, test_case == TestCases.COREDUMP_IN_RUNTIME)
                self.Context.bad_task_id = self.deploy_fresh(self.Parameters.testing_service, bad_fresh_id)
                raise sdk2.WaitTask(self.Context.bad_task_id, Status.Group.FINISH | Status.Group.BREAK)

            with self.memoize_stage['check_stop_deploy' + str(test_case)](commit_on_entrance=False):
                ok = self.check_child_status(self.Context.bad_task_id, Status.TIMEOUT)
                if not ok:
                    prefix = '[CRITICAL]' if self.Parameters.test_stop_deploy else '[WARNING]'
                    self.set_info('{} Deploy was not stopped after receiving bad fresh for test case "{}"'.format(prefix, test_case))
                    if self.Parameters.test_stop_deploy:
                        self.Context.fail_test = True

            with self.memoize_stage['push_good_fresh' + str(test_case)](commit_on_entrance=False):
                self.Context.good_task_id = self.deploy_fresh(self.Parameters.testing_service, self.Context.good_fresh_id)
                raise sdk2.WaitTask(self.Context.good_task_id, Status.Group.FINISH | Status.Group.BREAK)

            with self.memoize_stage['check_restore' + str(test_case)](commit_on_entrance=False):
                ok = self.check_child_status(self.Context.good_task_id, Status.SUCCESS)
                if not ok:
                    prefix = '[CRITICAL]' if self.Parameters.test_restore else '[WARNING]'
                    self.set_info('{} Service was not restored after fresh rollback for test case "{}"'.format(prefix, test_case))
                    if self.Parameters.test_restore:
                        self.Context.fail_test = True

        if self.Context.fail_test:
            raise TaskFailure('Some test cases failed')
