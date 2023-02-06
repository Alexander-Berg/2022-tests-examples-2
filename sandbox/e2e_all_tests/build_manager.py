# coding: utf-8

from datetime import datetime

from sandbox import sdk2

from sandbox.projects.partner.tasks.build_docker import BuildDockerImage
from sandbox.projects.partner.tasks.build_frontend import BuildFrontend
from sandbox.projects.partner.tasks.build_java_docker import PartnerBuildJavaDocker
from sandbox.projects.partner.tasks.misc.partner_front_task_base import \
    PartnerFrontTaskBase

from sandbox.projects.partner.tasks.misc import \
    parse_docker_image_name

from sandbox.projects.partner.settings import \
    BUILD_TYPE_BETA, \
    FRONTEND_DOCKER_IMAGE_NAME, \
    PARTNER_SSH_VAULT_NAME, \
    PARTNER_SSH_VAULT_OWNER, \
    ROBOT_PARTNER_YAV_SECRET, \
    ROBOT_PARTNER_YAV_SECRET_KEY, \
    ROBOT_PARTNER_SECRET, \
    ROBOT_PARTNER_SECRET_KEY


class BuildManager(PartnerFrontTaskBase):
    """
    Builder manager for autotests
    """

    @property
    def frontend_task_name(self):
        return 'pi_frontend_build'

    @property
    def backend_task_name(self):
        return 'pi_backend_docker_build'

    @property
    def java_task_name(self):
        return 'pi_java_build'

    class Context(PartnerFrontTaskBase.Context):
        tasks = dict()

    class Parameters(PartnerFrontTaskBase.Parameters):

        st_issue = sdk2.parameters.String(
            'Release ticket',
            description='PI-NNNNN',
            required=True
        )

        with sdk2.parameters.Group('Build parameters') as build_params:

            yharnam_source = sdk2.parameters.String(
                'PI frontend arc ref',
                description='Branch, tag, or commit hash at yharnam arc repository',
                default='trunk',
                required=True
            )

            retry_on_error = sdk2.parameters.Bool('Retry request on error', default=False)

            adfox_branch = sdk2.parameters.String(
                'ADFOX git branch',
                description='Branch at ADFOX git repository',
                default='master'
            )

            partner_branch = sdk2.parameters.String(
                'PI Backend branch',
                description='Branch at partner2 git repository',
                default='master',
                required=True,
            )

            java_branch = sdk2.parameters.String(
                'Source of PI java code in arc',
                description='Url to branch that will concatenate with arcadia:/arc/',
                default='trunk/arcadia',
                required=True,
            )

            java_revision_commit = sdk2.parameters.String(
                'Java arcadia revision',
                required=False,
            )

            use_custom_frontend_image = sdk2.parameters.Bool(
                'Use custom fronted docker image',
                default=False,
            )

            with use_custom_frontend_image.value[True]:
                frontend_image = sdk2.parameters.String(
                    'Custom frontend docker image tag',
                    required=True,
                )

            use_custom_deb_version = sdk2.parameters.Bool(
                'Use custom backend deb version',
                default=False,
            )

            with use_custom_deb_version.value[True]:
                backend_deb_version = sdk2.parameters.String(
                    'Custom deb version',
                    required=True,
                )

            use_custom_java = sdk2.parameters.Bool(
                'Use custom java build',
                default=False,
            )

            with use_custom_java.value[True]:
                java_docker_images = sdk2.parameters.String(
                    'Custom java docker images',
                    required=True,
                )

            is_release = sdk2.parameters.Bool(
                'Test in release pipeline',
                default=False
            )

        with sdk2.parameters.Group('Access parameters') as access_params:

            ssh_key_vault_owner = sdk2.parameters.String(
                'SSH key vault OWNER',
                required=True,
                default_value=PARTNER_SSH_VAULT_OWNER
            )

            ssh_key_vault_name = sdk2.parameters.String(
                'SSH key vault NAME',
                required=True,
                default_value=PARTNER_SSH_VAULT_NAME
            )

            yav_token_secret_id = sdk2.parameters.String(
                'YAV_TOKEN secret id',
                required=True,
                default_value=ROBOT_PARTNER_YAV_SECRET
            )

            yav_token_secret_key = sdk2.parameters.String(
                'YAV_TOKEN secret key',
                required=True,
                default_value=ROBOT_PARTNER_YAV_SECRET_KEY
            )

            dctl_yp_token_secret_id = sdk2.parameters.String(
                'DCTL_YP_TOKEN secret id',
                required=True,
                default_value=ROBOT_PARTNER_SECRET
            )

            dctl_yp_token_secret_key = sdk2.parameters.String(
                'DCTL_YP_TOKEN secret key',
                required=True,
                default_value=ROBOT_PARTNER_SECRET_KEY
            )

    def build_frontend(self):
        if self.Parameters.use_custom_frontend_image:
            _, tag, _ = parse_docker_image_name(self.Parameters.frontend_image, FRONTEND_DOCKER_IMAGE_NAME)
            self.Context.frontend_image_tag = tag
            self.Context.save()
            return None
        build_type = BUILD_TYPE_BETA
        arc_ref = self.Parameters.yharnam_source
        retry_on_error = self.Parameters.retry_on_error
        task = BuildFrontend(
            self,
            priority=self.Parameters.priority,
            build_type=build_type,
            arc_ref=arc_ref,
            retry_on_error=retry_on_error
        )
        task.enqueue()
        return task

    def post_build_frontend(self, task):
        image_name = task.Parameters.image_name
        _, tag, _ = parse_docker_image_name(image_name, FRONTEND_DOCKER_IMAGE_NAME)
        self.Context.frontend_image_tag = tag
        self.Context.save()

    def build_java(self):
        if self.Parameters.use_custom_java:
            return None
        branch = self.Parameters.java_branch
        revision_commit = self.Parameters.java_revision_commit
        task = PartnerBuildJavaDocker(
            self,
            branch=branch,
            revision_commit=revision_commit
        )
        task.enqueue()
        return task

    def post_build_java(self, task):
        self.Context.java_docker_images = task.Parameters.java_docker_images
        self.Context.save()

    def build_backend(self):
        if self.Parameters.use_custom_deb_version:
            self.Context.backend_deb_version = self.Parameters.backend_deb_version
            self.Context.save()
            return None
        task = BuildDockerImage(
            self,
            priority=self.Parameters.priority,
            version="arc_test_{}".format(datetime.now().strftime("%Y%m%d%H%M%S")),
            branch=self.Parameters.partner_branch
        )
        task.enqueue()
        return task

    def post_build_backend(self, task):
        # It is arbitrary docker image tag set instead of regular DEB version
        self.Context.backend_deb_version = task.Parameters.version
        self.Context.save()
