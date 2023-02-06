# -*- coding: utf-8 -*-

import logging
import requests
import time
import json

from sandbox import sdk2

from sandbox.common import errors
from sandbox.common.types.task import Status
from sandbox.common.types.task import Semaphores
from sandbox.sandboxsdk import process
from sandbox.sandboxsdk.errors import SandboxSubprocessError

from sandbox.projects.app_host.resources import AppHostGrpcClientExecutable
from sandbox.projects.common import decorators
from sandbox.projects.common import link_builder as lb
import sandbox.projects.common.betas.beta_api as beta_api
from sandbox.projects.websearch.params import ResourceWithDefaultByAttr
from sandbox.projects.websearch.params import ResourceWithLastReleasedValueByDefault
from sandbox.projects.websearch.upper import resources as upper_resources
from sandbox.projects.websearch.upper.fast_data.DeployFastData import DeployFastData
from sandbox.projects.websearch.upper.fast_data.DeployRearrangeDataFastWithBstr import DeployRearrangeDataFastWithBstr
from sandbox.projects.websearch.upper.fast_data.ExecutionTimeTracker import ExecutionTimeTracker

EPSILON = 1e-6


class TestRearrangeDataFastOnYappyBeta(ExecutionTimeTracker):
    """
        Тест быстрых данных верхнего метапоиска на yappy-бете.
    """

    class Requirements(sdk2.Task.Requirements):
        cores = 1
        # 25 Gb for requests + 5 Gb for grpc_client binary and reserve
        disk_space = 30 * 1024  # 30 Gb
        ram = 30 * 1024  # 30 Gb

        class Caches(sdk2.Requirements.Caches):
            pass  # do not use any shared caches

    class Parameters(sdk2.Task.Parameters):
        kill_timeout = 30 * 60  # 30 min

        beta_name = sdk2.parameters.String(
            'Yappy beta name',
            default='noapache-web-fast-data',
            required=True
        )

        fast_data_bundle = sdk2.parameters.Resource(
            'Rearrange Data Fast Bundle',
            resource_type=upper_resources.RearrangeDataFastBundle,
            required=True,
        )
        requests = ResourceWithDefaultByAttr(
            'Noapache binary requests',
            resource_type=upper_resources.BlenderGrpcClientPlan,
            default_attr_name='autoupdate_resources_noapacheupper_request_sampler_web_fast_data_trunk_task_id',
            required=True,
        )
        requests_limit = sdk2.parameters.Integer('Limit requests number (0 = all)', default=1000)
        max_fail_rate = sdk2.parameters.Float('Max acceptable fail rate (value in [0, 1])', default=0.01)
        rps = sdk2.parameters.Integer('Requests per second', default=10)
        app_host_grpc_client = ResourceWithLastReleasedValueByDefault(
            'Apphost grpc client executable',
            resource_type=AppHostGrpcClientExecutable,
            required=True,
        )

        use_new_deployer = sdk2.parameters.Bool("Use new deployer", default=False)
        with use_new_deployer.value[True]:
            blank_fast_data_bundle = ResourceWithLastReleasedValueByDefault(
                'Blank Rearrange Data Fast Bundle',
                resource_type=upper_resources.RearrangeDataFastBundleBlank,
            )

        with sdk2.parameters.Group('Vault'):
            yt_token_name = sdk2.parameters.String('YT token name', required=True)
            nanny_token_name = sdk2.parameters.String('Nanny token name', required=True)

    class Context(ExecutionTimeTracker.Context):
        pass

    @property
    def stage_name(self):
        return 'test_on_yappy_beta'

    def on_enqueue(self):
        super(TestRearrangeDataFastOnYappyBeta, self).on_enqueue()
        self.check_beta_consistency()
        self.Requirements.semaphores = Semaphores(
            acquires=[
                Semaphores.Acquire(
                    name='lock-{}'.format(self.Context.service),
                    weight=1,
                    capacity=2
                ),
            ],
        )

    def on_execute(self):
        with self.memoize_stage.deploy:
            if self.Parameters.use_new_deployer:
                deployment_task = DeployFastData(
                    self,
                    description='Rearrange Data Fast ({vertical}) auto-release for {services}'.format(
                        vertical=self.Parameters.fast_data_bundle.vertical.upper(),
                        services=self.Parameters.beta_name,
                    ),
                    fast_data_bundle=self.Parameters.fast_data_bundle,
                    blank_fast_data_bundle=self.Parameters.blank_fast_data_bundle,
                    use_testing_deployer=False,
                    deploy_config={
                        "communication": {
                            "cluster": "locke",
                            "cypress_dir": "//home/search-runtime/fast-data"
                        },
                        "services": {
                            self.Context.service: {
                                "prepare": {
                                    "degrade_level": 1.0,
                                    "retry_delay": 120,
                                    "failed_retry_delay": 120,
                                },
                                "activate": {
                                    "degrade_level": 1.0,
                                    "retry_delay": 60,
                                    "failed_retry_delay": 60,
                                }
                            }
                        },
                    },
                    yt_token_name=self.Parameters.yt_token_name,
                    nanny_token_name=self.Parameters.nanny_token_name,
                )
            else:
                deployment_task = DeployRearrangeDataFastWithBstr(
                    self,
                    description='Rearrange Data Fast ({vertical}) auto-release for {services}'.format(
                        vertical=self.Parameters.fast_data_bundle.vertical.upper(),
                        services=self.Parameters.beta_name,
                    ),
                    fast_data_bundle=self.Parameters.fast_data_bundle,
                    cypress_dir='//home/search-runtime/fast-data',
                    rollback_mode=False,
                    force_mode=False,
                    operating_degrade_level=1.0,
                    nanny_services=[self.Context.service],
                    yt_token_name=self.Parameters.yt_token_name,
                    nanny_token_name=self.Parameters.nanny_token_name,
                )
            deployment_task.Requirements.semaphores = Semaphores(
                acquires=[
                    Semaphores.Acquire(
                        name='lock-{}'.format(self.Context.service),
                        weight=1,
                        capacity=2
                    ),
                ],
            )
            deployment_task.save()
            self.Context.deployment_task_id = deployment_task.enqueue().id
            self.set_info('Deployment to yappy beta started on {}'.format(
                lb.task_link(self.Context.deployment_task_id)
            ), do_escape=False)
            self.Context.save()

        with self.memoize_stage.load_resources:
            self.Context.grpc_client_path = str(sdk2.ResourceData(self.Parameters.app_host_grpc_client).path)
            self.Context.requests_path = str(sdk2.ResourceData(self.Parameters.requests).path)

        with self.memoize_stage.wait_deploy:
            while True:
                self.Context.deployment_status = self.server.task[self.Context.deployment_task_id].read()['status']
                if self.Context.deployment_status in Status.Group.FINISH | Status.Group.BREAK:
                    break
                time.sleep(15)

        with self.memoize_stage.check_deploy:
            self.Context.successfully_deployed = self.Context.deployment_status in Status.Group.SUCCEED and self.check_version(self.Context.instances)
            if self.Context.successfully_deployed:
                self.set_info('Deployment to yappy beta successfully finished on {}'.format(
                    lb.task_link(self.Context.deployment_task_id)
                ), do_escape=False)
            else:
                self.set_info('Deployment to yappy beta failed on {} with status {}'.format(
                    lb.task_link(self.Context.deployment_task_id),
                    self.Context.deployment_status
                ), do_escape=False)
                raise errors.TaskFailure('Failed to deploy new fast data to yappy beta.')

        with self.memoize_stage.shoot:
            with open(self.Context.requests_path) as f:
                requests_number = sum(1 for _ in f)
            requests_number = min(requests_number, self.Parameters.requests_limit)
            self.processes = {}
            for instance in self.Context.instances:
                host, port = instance.split(':')
                port = int(port)
                cmd = [
                    self.Context.grpc_client_path,
                    '--address', '{}:{}'.format(host, port + 2),
                    '--plan', self.Context.requests_path,
                    '--format', 'bin',
                    '--sessions-per-second', str(self.Parameters.rps),
                    '--request-count', str(requests_number),
                    '--connection-timeout', '100',
                ]
                self.processes[instance] = process.run_process(cmd, wait=False, log_prefix='grpc_client_shoot_{}_{}'.format(host, port))
                self.set_info('Start shooting {}'.format(instance), do_escape=False)

        with self.memoize_stage.check_shoot:
            self.Context.failed_instances = []
            for instance, proc in self.processes.items():
                try:
                    proc.wait()
                    process.check_process_return_code(proc)
                except SandboxSubprocessError:
                    self.Context.failed_instances.append(instance)
                    continue
                requests_stats_line = ''
                with open(proc.stdout_path) as instance_log:
                    for line in instance_log:
                        if line.startswith('sessions'):
                            requests_stats_line = line
                if not requests_stats_line:
                    raise errors.TaskFailure('Something wrong with logs for {}'.format(instance))
                sessions = None
                successes = None
                inProgress = None
                for assignment in requests_stats_line.split():
                    exec(assignment)
                requests_finished = sessions - inProgress
                self.Context.success_rate = float(successes) / requests_finished
                self.Context.fail_rate = 1. - self.Context.success_rate
                self.set_info('Instance {} success rate: {:.2f}%, fail rate: {:.2f}%'.format(instance, self.Context.success_rate * 100, self.Context.fail_rate * 100))
                self.set_info(requests_stats_line)
            if self.Context.failed_instances:
                raise errors.TaskFailure('Failed to shoot instances: {}'.format(', '.join(self.Context.failed_instances)))
            elif not self.check_version(self.Context.instances):
                raise errors.TaskFailure('Incorrect fast data version after shooting')
            elif self.Context.fail_rate > self.Parameters.max_fail_rate + EPSILON:
                raise errors.TaskFailure('High fail rate')

    @decorators.retries(20, delay=15, backoff=1)  # 5 min
    def get_fast_data_version(self, instance):
        response = requests.get('http://{}/yandsearch'.format(instance), params={'info': 'getrearrangeversion'}, timeout=30, verify=False)
        for line in response.text.splitlines():
            field = 'fast_data_version: '
            if line.startswith(field):
                return int(line[len(field):])

    def check_version(self, instances):
        right_versions = True
        for instance in instances:
            try:
                instance_fast_data_version = self.get_fast_data_version(instance)
            except:
                raise errors.TaskFailure("Can't read fast data version from instance {}".format(instance))
            if instance_fast_data_version != self.Parameters.fast_data_bundle.version:
                self.set_info('Incorrect fast data version on {}: v.{} deployed, v.{} read'.format(
                    instance,
                    self.Parameters.fast_data_bundle.version,
                    instance_fast_data_version
                ))
                right_versions = False
        return right_versions

    def check_beta_consistency(self):
        api = beta_api.BetaApi.fromurl()
        self.set_info('Checking beta consistency')
        if not api.beta_exists(self.Parameters.beta_name):
            raise errors.TaskFailure('Beta {} not exists'.format(self.Parameters.beta_name))
        self._check_beta(api, self.Parameters.beta_name)
        self.set_info('Beta {} status is {}'.format(self.Parameters.beta_name, api.get_beta_state(self.Parameters.beta_name).get('status')))

    @decorators.retries(5, delay=15, backoff=1)  # 5 min
    def _check_beta(self, api, beta_name):
        errmsg = ""
        response = requests.post('{}/api/yappy.services.Model/retrieveBeta'.format(beta_api.YAPPY_URL), data=json.dumps({'name': beta_name}), timeout=30, verify=False)
        if response.status_code != requests.codes.ok:
            errmsg = 'retrieveBeta request failed with code {}'.format(response.status_code)
        else:
            for component in response.json()['components']:
                if component['type']['name'] == 'noapache':
                    self.Context.instances = component['slot']['instances']
                    self.Context.service = component['slot']['id']
                    if not all(check.get('success', False) for check in component['checks']):
                        errmsg = 'Failed checks for {}'.format(self.Context.service)
                        break
                    break
        if errmsg:
            raise errors.TaskFailure(errmsg)

    def cleanup(self):
        try:
            logging.info('Stop subtask {}'.format(self.Context.deployment_task_id))
            sdk2.Task[self.Context.deployment_task_id].stop()
        except Exception as e:
            logging.exception(e)

    def on_timeout(self, prev_status):
        logging.debug('on_timeout')
        self.cleanup()

    def on_break(self, prev_status, status):
        logging.debug('on_break')
        self.cleanup()

    def on_failure(self, prev_status):
        logging.debug('on_failure')
        self.cleanup()
