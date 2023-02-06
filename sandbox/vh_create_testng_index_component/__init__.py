from sandbox.projects.VideoSearch.platform_helper import ClusterMasterApi
from sandbox.projects.VideoSearch.platform_helper import ClusterMasterResponceStatus
from sandbox.projects.VideoSearch.platform_helper import PlatformDeployer
from sandbox.projects.VideoSearch.video_resource_types import VideoWebscriptsResource as WebscriptsResource
from sandbox.projects.vh.frontend import VhFrontendIndexBinary
from sandbox import sdk2
from sandbox import common
import time
import logging


class VhCreateTestingIndexComponent(sdk2.Task):
    """ Task to create component with testing index """

    class Parameters(sdk2.Task.Parameters):

        yt_prefix = sdk2.parameters.String(
            "Yt prefix where bases will be stored",
            default=None,
            required=True,
        )

        use_test_replica = sdk2.parameters.Bool(
            "Check if you need to use your own replica",
            default=False,
        )

        with use_test_replica.value[True]:
            yt_replica_dir = sdk2.parameters.String(
                "Yt replica directory",
                default=None,
                required=True
            )

        use_new_webscripts = sdk2.parameters.Bool(
            "Check if you need to test new webscripts",
            default=False,
        )

        with use_new_webscripts.value[True]:
            webscripts_resource_id = sdk2.parameters.Resource(
                "Video webscripts resource",
                default=None,
                required=True,
                resource_type=WebscriptsResource,
            )

        use_new_binary = sdk2.parameters.Bool(
            "Check if you need to test new indexvh binary",
            default=False,
        )
        with use_new_binary.value[True]:
            indexvh_binary = sdk2.parameters.Resource(
                "Indexcvh binary",
                default=None,
                required=True,
                resource_type=VhFrontendIndexBinary,
            )

    __ENV_ID = 'robot-video.junk.vh-test-bases'
    __DYN_2_STAT_TEMPLATE_CM_NAME = 'template-component-dyn2stat'
    __INDEXER_TEMPLATE_CM_NAME = 'template-component-indexer'
    __DYN_2_STAT_BASE_NAME = 'dyn2stat'
    __INDEXER_BASE_NAME = 'indexer'
    __CLUSTER_MASTER_URL = 'https://vh-test-bases.common.yandex.net'

    def generate_new_cm_name(self, name_base):
        return 'vh-{}-{}'.format(name_base, int(time.time()))

    def get_deploy_resources(self):
        resources_to_deploy = []
        if self.Parameters.use_new_webscripts:
            resources_to_deploy.append({
                "type": WebscriptsResource,
                "id": self.Parameters.webscripts_resource_id.id,
            })
        if self.Parameters.use_new_binary:
            resources_to_deploy.append({
                "type": VhFrontendIndexBinary,
                "id": self.Parameters.indexvh_binary.id,
            })
        return resources_to_deploy

    @property
    def get_yt_prefix(self):
        _yt_prefix = self.Parameters.yt_prefix
        if not _yt_prefix.endswith('/'):
            _yt_prefix += '/'
        return _yt_prefix

    def create_dyn2stat_component(self):
        component_name = self.generate_new_cm_name(self.__DYN_2_STAT_BASE_NAME)
        variables_to_deploy = {
            "YT_PREFIX": self.get_yt_prefix,
            "VH_YT_REPLICA": self.Parameters.yt_replica_dir,
            "VH_STATIC_TABLES_PREFIX": self.get_yt_prefix,
        }

        dyn2stat_platform_deployer = PlatformDeployer(
            self.__ENV_ID,
            component_name,
            self.__DYN_2_STAT_TEMPLATE_CM_NAME,
            variables_to_deploy=variables_to_deploy,
            resources_to_deploy=self.get_deploy_resources(),
        )

        dyn2stat_platform_deployer.deploy()
        dyn2stat_platform_deployer.wait_for_deploy()
        return component_name

    def create_indexer_component(self):
        component_name = self.generate_new_cm_name(self.__INDEXER_BASE_NAME)
        variables_to_deploy = {
            "YT_PREFIX": self.get_yt_prefix,
        }

        if self.Parameters.use_test_replica:
            variables_to_deploy.update({
                "VH_STATIC_TABLES_PREFIX": self.get_yt_prefix,
            })

        indexer_platform_deployer = PlatformDeployer(
            self.__ENV_ID,
            component_name,
            self.__INDEXER_TEMPLATE_CM_NAME,
            variables_to_deploy=variables_to_deploy,
            resources_to_deploy=self.get_deploy_resources(),
        )

        indexer_platform_deployer.deploy()
        indexer_platform_deployer.wait_for_deploy()
        return component_name

    def get_cm_api_url(self, component_name):
        return '{}/{}/'.format(self.__CLUSTER_MASTER_URL, component_name)

    dyn2stat_cm_name = ""
    indexer_cm_name = ""

    def cluster_master_api(self, cm_name):
        return ClusterMasterApi(self.get_cm_api_url(cm_name))

    def on_execute(self):
        if self.Parameters.use_test_replica:
            with self.memoize_stage.deploy_dyn2stat_stage:
                self.Context.dyn2stat_cm_name = self.create_dyn2stat_component()

            dyn2stat_cluster_master_api = self.cluster_master_api(self.Context.dyn2stat_cm_name)
            dyn2stat_cluster_master_api.run_whole_path('qloud-finish')
            dyn2stat_cluster_master_api.disable_retry_on_success('qloud-finish')
            time.sleep(60)  # wait for statuses to update

            status = dyn2stat_cluster_master_api.check_target_status('qloud-finish')
            if status == ClusterMasterResponceStatus.WAITING:
                logging.info("Dyn2stat stage still in action. Wait for 3 minutes")
                raise sdk2.WaitTime(3 * 60)

            if status == ClusterMasterResponceStatus.FAILURE:
                logging.info("Dyn2stat failed.")
                raise common.errors.TaskFailure("Cant cast dynamic tables to static")

        with self.memoize_stage.deploy_inexer_component:
            self.Context.indexer_cm_name = self.create_indexer_component()
            indexer_cluster_master_api = self.cluster_master_api(self.Context.indexer_cm_name)
            indexer_cluster_master_api.run_whole_path('qloud-finish')
            indexer_cluster_master_api.disable_retry_on_success('qloud-finish')
            time.sleep(60)  # wait for statuses to update

        status = self.cluster_master_api(self.Context.indexer_cm_name).check_target_status('qloud-finish')
        if status == ClusterMasterResponceStatus.WAITING:
            logging.info("Indexer stage still in action. Wait for 3 minutes")
            raise sdk2.WaitTime(3 * 60)

        if status == ClusterMasterResponceStatus.FAILURE:
            logging.info("Index building failed.")
            raise common.errors.TaskFailure("Can't build index")
