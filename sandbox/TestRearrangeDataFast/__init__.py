# -*- coding: utf-8 -*-

import json
import requests

from sandbox import sdk2

from sandbox.common import errors
from sandbox.common.types.task import ReleaseStatus
from sandbox.common.types.task import Status

from sandbox.projects import resource_types as resources
from sandbox.projects.common import constants as consts
from sandbox.projects.common import decorators
from sandbox.projects.common import link_builder as lb
import sandbox.projects.common.betas.beta_api as beta_api
from sandbox.projects.common.noapacheupper.request import ResourceParam as RequestsParam
from sandbox.projects.common.noapacheupper.search_component import Params as NoapacheParams
from sandbox.projects.common.noapacheupper.standalone import Params as NoapacheStandaloneParams
from sandbox.projects.common.noapacheupper.standalone import ToolConverter
from sandbox.projects.common.noapacheupper.standalone import UseLastStableGrpcClient
from sandbox.projects.common.search.requester import Params as RequesterParams

from sandbox.projects.websearch.params import ResourceWithDefaultByAttr
from sandbox.projects.websearch.params import ResourceWithLastReleasedValueByDefault
from sandbox.projects.websearch.upper import resources as upper_resources

from sandbox.projects.common.build.YaMake import YaMakeTask
from sandbox.projects.websearch.upper.GetStandaloneNoapacheupperResponses import GetStandaloneNoapacheupperResponses
from sandbox.projects.websearch.upper.fast_data.ExecutionTimeTracker import ExecutionTimeTracker
from sandbox.projects.websearch.upper.fast_data.TestRearrangeDataFastOnYappyBeta import TestRearrangeDataFastOnYappyBeta


class TestRearrangeDataFast(ExecutionTimeTracker):
    """
        Тест быстрых данных верхнего метапоиска.
        - Стреляет запросами в ноапач и проверяет, что он не упал.
        - Запускает аркадийные тесты (search/web/rearrs_upper/tests/rearrange.fast)
    """

    ARC_TEST_DIRS = [
        'search/web/rearrs_upper/tests/rearrange.fast',
    ]

    class Requirements(sdk2.Task.Requirements):
        cores = 1
        disk_space = 500  # Mb

        class Caches(sdk2.Requirements.Caches):
            pass  # do not use any shared caches

    class Parameters(sdk2.Task.Parameters):
        kill_timeout = 60 * 60  # 60 min

        run_arc = sdk2.parameters.Bool("Arcadia tests", default=False)
        run_noapache = sdk2.parameters.Bool("Shoot local noapache with data", default=False)
        run_yappy_beta = sdk2.parameters.Bool("Shoot noapache on yappy beta", default=False)

        with run_arc.value[True]:
            arcadia_url = sdk2.parameters.ArcadiaUrl("Svn url for arcadia", required=True)
            yt_store_token_owner = sdk2.parameters.String("YT_STORE_TOKEN owner")

        with run_noapache.value[True]:
            binary = ResourceWithLastReleasedValueByDefault(
                'Noapacheupper executable',
                resource_type=upper_resources.NoapacheUpper,
                required=True,
            )
            config = ResourceWithDefaultByAttr(
                'Noapacheupper config',
                resource_type=resources.NOAPACHEUPPER_CONFIG,
                default_attr_name='autoupdate_resources_noapacheupper_web_kubr_trunk_task_id',
                required=True,
            )
            rearrange_data = ResourceWithLastReleasedValueByDefault(
                'Noapacheupper rearrange data',
                resource_type=resources.REARRANGE_DATA,
                required=True,
            )
            rearrange_dynamic = ResourceWithLastReleasedValueByDefault(
                'Noapacheupper rearrange.dynamic',
                resource_type=resources.REARRANGE_DYNAMIC_DATA,
                required=True,
            )
            fast_data = sdk2.parameters.Resource(
                'Rearrange Data Fast',
                resource_type=upper_resources.RearrangeDataFast,
                required=True,
            )
            requests = ResourceWithDefaultByAttr(
                'Noapache binary requests',
                resource_type=upper_resources.BlenderGrpcClientPlan,
                default_attr_name='autoupdate_resources_noapacheupper_request_sampler_web_fast_data_trunk_task_id',
                required=True,
            )
            requests_limit = sdk2.parameters.Integer('Limit requests number (0 = all)', default=1000)

        with run_yappy_beta.value[True]:
            beta_name = sdk2.parameters.String(
                'Yappy beta name',
                default='noapache-web-fast-data',
                required=True
            )
            with sdk2.parameters.Group('Parameters for beta creation'):
                template_name = sdk2.parameters.String('Template name', default='noapache-web')
                suffix = sdk2.parameters.String('Suffix', default='fast-data')
                parent_id = sdk2.parameters.String('Beta parent id', default='hamster_noapache_vla_web_yp')
            fast_data_bundle = sdk2.parameters.Resource(
                'Rearrange Data Fast Bundle',
                resource_type=upper_resources.RearrangeDataFastBundle,
                required=True,
            )
            yappy_requests = ResourceWithDefaultByAttr(
                'Noapache binary requests',
                resource_type=upper_resources.BlenderGrpcClientPlan,
                default_attr_name='autoupdate_resources_noapacheupper_request_sampler_web_fast_data_trunk_task_id',
                required=True,
            )
            yappy_requests_limit = sdk2.parameters.Integer('Limit requests number (0 = all)', default=1000)
            max_fail_rate = sdk2.parameters.Float('Max acceptable fail rate (value in [0, 1])', default=0.01)
            rps = sdk2.parameters.Integer('Requests per second', default=10)
            use_new_deployer = sdk2.parameters.Bool("Use new deployer", default=False)
            with sdk2.parameters.Group('Vault'):
                yt_token_name = sdk2.parameters.String('YT token name', required=True)
                nanny_token_name = sdk2.parameters.String('Nanny token name', required=True)
                yappy_token_owner = sdk2.parameters.String('YAPPY_TOKEN owner', required=True)

    class Context(ExecutionTimeTracker.Context):
        pass

    @property
    def stage_name(self):
        return 'test'

    def on_enqueue(self):
        super(TestRearrangeDataFast, self).on_enqueue()

        if self.Parameters.run_noapache:
            app_host_tool_converter = sdk2.Resource.find(
                type=resources.APP_HOST_TOOL_CONVERTER_EXECUTABLE,
                attrs={'released': ReleaseStatus.STABLE},
            ).order(-sdk2.Resource.accessed).first()
            self.Context.resources = {
                NoapacheParams.Binary.name: self.Parameters.binary.id,
                NoapacheParams.Config.name: self.Parameters.config.id,
                NoapacheParams.RearrangeData.name: self.Parameters.rearrange_data.id,
                NoapacheParams.RearrangeDynamicData.name: self.Parameters.rearrange_dynamic.id,
                NoapacheParams.RearrangeDataFast.name: self.Parameters.fast_data.id,
                RequestsParam.name: self.Parameters.requests.id,
                RequesterParams.RequestsLimit.name: self.Parameters.requests_limit,
                ToolConverter.name: app_host_tool_converter.id,
                UseLastStableGrpcClient.name: True,
                NoapacheStandaloneParams.IgnoreNehCacheErrors.name: True,
            }

    def on_execute(self):
        with self.memoize_stage.test:
            self.Context.task_ids = []
            if self.Parameters.run_noapache:
                self.Context.local_shoot_task_id = sdk2.Task[GetStandaloneNoapacheupperResponses.type](
                    self,
                    description='Shoot local noapache with {}'.format(
                        lb.resource_link(self.Parameters.fast_data.id, self.Parameters.fast_data.description)
                    ),
                    **self.Context.resources
                ).enqueue().id
                self.Context.task_ids.append(self.Context.local_shoot_task_id)

            if self.Parameters.run_arc:
                self.Context.arc_tests_task_id = sdk2.Task[YaMakeTask.type](
                    self,
                    description='Arcadia tests',
                    checkout_arcadia_from_url=self.Parameters.arcadia_url,
                    targets=';'.join(self.ARC_TEST_DIRS),
                    use_aapi_fuse=True,
                    use_arc_instead_of_aapi=True,
                    aapi_fallback=True,
                    build_system=consts.SEMI_DISTBUILD_BUILD_SYSTEM,
                    test=True,
                    report_tests_only=True,
                    disable_test_timeout=False,
                    cache_test_results=False,
                    ya_yt_store=True,
                    ya_yt_proxy="arnold",
                    ya_yt_dir="//home/search-runtime/fast-data/cache",
                    ya_yt_put=True,
                    ya_yt_token_vault_owner=self.Parameters.yt_store_token_owner,
                    ya_yt_max_cache_size=536870912000,
                    kill_timeout=60 * 60,  # 60 min
                ).enqueue().id
                self.Context.task_ids.append(self.Context.arc_tests_task_id)

            if self.Parameters.run_yappy_beta:
                self.start_beta(self.Parameters.beta_name)
                self.Context.shoot_yappy_beta_task_id = sdk2.Task[TestRearrangeDataFastOnYappyBeta.type](
                    self,
                    description='Shoot noapache on {} with {}'.format(
                        self.Parameters.beta_name,
                        lb.resource_link(self.Parameters.fast_data_bundle.id, self.Parameters.fast_data_bundle.description)
                    ),
                    beta_name=self.Parameters.beta_name,
                    fast_data_bundle=self.Parameters.fast_data_bundle,
                    requests=self.Parameters.yappy_requests,
                    requests_limit=self.Parameters.yappy_requests_limit,
                    max_fail_rate=self.Parameters.max_fail_rate,
                    rps=self.Parameters.rps,
                    use_new_deployer=self.Parameters.use_new_deployer,
                    yt_token_name=self.Parameters.yt_token_name,
                    nanny_token_name=self.Parameters.nanny_token_name,
                    app_host_grpc_client=1832049857,
                ).enqueue().id
                self.Context.task_ids.append(self.Context.shoot_yappy_beta_task_id)

            raise sdk2.WaitTask(self.Context.task_ids, Status.Group.FINISH | Status.Group.BREAK)

        with self.memoize_stage.check_tests:
            has_errors = False
            error_messages = {
                self.Context.arc_tests_task_id: 'Arcadia tests failed: {}'.format(self.Context.arc_tests_task_id),
                self.Context.local_shoot_task_id: 'Failed to run noapache on localhost with this fast data: {}',
                self.Context.shoot_yappy_beta_task_id: 'Failed to run noapache on yappy beta with this fast data: {}',
            }
            for task_id in self.Context.task_ids:
                if sdk2.Task[task_id].status != Status.SUCCESS:
                    self.set_info(error_messages[task_id].format(
                        lb.task_link(task_id)
                    ), do_escape=False)
                    has_errors = True

            if has_errors:
                raise errors.TaskFailure

    @decorators.retries(5, delay=15, backoff=1)  # 5 min
    def _check_beta(self, api, beta_name):
        errmsg = ""
        response = requests.post('{}/api/yappy.services.Model/retrieveBeta'.format(beta_api.YAPPY_URL), data=json.dumps({'name': beta_name}), timeout=30, verify=False)
        if response.status_code != requests.codes.ok:
            errmsg = 'retrieveBeta request failed with code {}'.format(response.status_code)
        else:
            for component in response.json()['components']:
                if component['type']['name'] == 'noapache':
                    service = component['slot']['id']
                    if not all(check.get('success', False) for check in component['checks']):
                        errmsg = 'Failed checks for {}'.format(service)
                        break
                    break
        if errmsg:
            raise errors.TaskFailure(errmsg)

    def start_beta(self, beta_name):
        api = beta_api.BetaApi.fromurl(token=sdk2.Vault.data(self.Parameters.yappy_token_owner, name='YAPPY_TOKEN'))
        if not api.beta_exists(beta_name):
            self.set_info('Beta {} does not exist; start beta creation'.format(beta_name))
            patch_map = {self.Parameters.template_name: {'ignoreParentInstanceSpec': True, 'parentExternalId': self.Parameters.parent_id}}
            api.create_beta_from_template(template_name=self.Parameters.template_name, suffix=self.Parameters.suffix, patches=patch_map)
        try:
            self.set_info('Start beta {}'.format(beta_name))
            api.start_beta(beta_name)
        except RuntimeError as e:
            raise errors.TaskFailure('Beta {} allocation failed with status {}.\nError: {}'.format(
                beta_name,
                api.get_beta_state(beta_name).get('status'),
                str(e)
            ))
        self._check_beta(api, beta_name)
        self.set_info('Beta {} status is {}'.format(beta_name, api.get_beta_state(beta_name).get('status')))

    def cleanup(self):
        for task_id in self.Context.task_ids:
            try:
                sdk2.Task[task_id].stop()
            except:
                pass

    def on_timeout(self, prev_status):
        self.cleanup()

    def on_break(self, prev_status, status):
        self.cleanup()

    def on_failure(self, prev_status):
        self.cleanup()
