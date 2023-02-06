# coding=utf-8
import time
import yaml

import sandbox.common.errors as errors
import sandbox.sdk2 as sdk2
import sandbox.projects.common.binary_task as binary_task
import sandbox.common.types.task as ctt

import sandbox.projects.metrika.utils as utils
import sandbox.projects.metrika.utils.resource_types as rt
import sandbox.projects.metrika.utils.base_metrika_task as base_metrika_task

import sandbox.projects.metrika.utils.settings as settings
import sandbox.projects.metrika.core.resources.keys_xml as keys_xml


DEFAULT_BISHOP_ENV = 'metrika.deploy.core.testing.phantom2d.load-test'


@base_metrika_task.with_parents
class MetrikaCorePhantom2dLoadTestStandCreate(binary_task.LastRefreshableBinary, sdk2.Task):
    class Parameters(utils.CommonParameters):
        with sdk2.parameters.Group('Stage parameters') as stage_parameters:
            phantom2d_version = sdk2.parameters.String(
                'phantom2d version',
                required=True,
            )
            stage_id = sdk2.parameters.String(
                'Stage ID',
                required=True,
            )
            with sdk2.parameters.RadioGroup('Stage datacenter') as stage_dc:
                stage_dc.values['vla'] = stage_dc.Value(default=True)
                stage_dc.values['sas'] = None
                stage_dc.values['iva'] = None

            stage_project_name = sdk2.parameters.String(
                'Project name',
                required=True,
                default='metrika-load-testing',
            )
            stage_vcpu_limit = sdk2.parameters.Integer(
                'VCPU limit',
                required=True,
                default=20000,
            )
            stage_memory_limit = sdk2.parameters.Integer(
                'Memory limit',
                required=True,
                default=68719476736,  # ~64 gb
            )
            stage_disk_capacity = sdk2.parameters.Integer(
                'Disk capacity',
                required=True,
                default=32212254720,  # ~30gb
            )
            stage_network_macro = sdk2.parameters.String(
                'Network macro',
                required=True,
                default='_YMETRICTESTNETS_',
            )
            stage_abc_service_id = sdk2.parameters.Integer(
                'ABC Service id',
                required=True,
                default=30740,  # metrika-ci
            )

        with sdk2.parameters.Group('Layers') as layers:
            layer_base_url = sdk2.parameters.String(
                'Base layer URL',
                required=True,
                default='rbtorrent:9ff4155d55abecaaa493b015c8acae58256679e8',
            )
            layer_nginx_url = sdk2.parameters.String(
                'nginx layer URL',
                required=True,
                default='rbtorrent:203934481f22594dba9351a14f4feada81dd1b9d',
            )
            st_res_keys_xml_url = sdk2.parameters.Resource(
                'keys.xml static resource',
                required=False,
                resource_type=keys_xml.MetrikaKeysXML,
                description='Latest stable {} by default'.format(keys_xml.MetrikaKeysXML.name),
            )
            layer_get_bishop_config_url = sdk2.parameters.String(
                'get_bishop_config layer URL',
                required=True,
                default='sbr:2228990657',
            )

        with sdk2.parameters.Group('Static resources') as static_resources:
            st_res_unifined_agent_url = sdk2.parameters.String(
                'unified agent static resource URL',
                required=True,
                default='rbtorrent:9f73edbba859863d7ba09737d0f379c59c3b338b',
            )
            st_res_geodata_url = sdk2.parameters.String(
                'geodata static resource URL',
                required=True,
                default='rbtorrent:113ef0b900ef4d503c1f4eeb12505e22d0d695e6',
            )
            st_res_informer_url = sdk2.parameters.String(
                'informer static resource URL',
                required=True,
                default='rbtorrent:2ebb1f90dea705286435e7e41cb4aa5296bc6313',
            )
            st_res_keys_xml_url = sdk2.parameters.Resource(
                'keys.xml static resource',
                required=False,
                resource_type=keys_xml.MetrikaKeysXML,
            )
            st_res_uatraits_url = sdk2.parameters.String(
                'uatraits static resource URL',
                required=True,
                default='rbtorrent:59e88769dfa7da6406adc42791b35355c9264abe',
            )

        with sdk2.parameters.Group('nginx config parameters') as nginx_config_parameters:
            nginx_bishop_program = sdk2.parameters.String(
                'nginx bishop program',
                required=True,
                default='nginx-phantom2d',
            )
            nginx_bishop_environment = sdk2.parameters.String(
                'nginx bishop environment',
                required=True,
                default=DEFAULT_BISHOP_ENV,
            )

        with sdk2.parameters.Group('unifined agent config parameters') as unifined_agent_config_parameters:
            ua_bishop_program = sdk2.parameters.String(
                'unifined agent bishop program',
                required=True,
                default='unified-agent-stub',
            )
            ua_bishop_environment = sdk2.parameters.String(
                'unifined agent bishop environment',
                required=True,
                default=DEFAULT_BISHOP_ENV,
            )

        with sdk2.parameters.Group('phantom2d config parameters') as phantom2d_config_parameters:
            phantom2d_bishop_program = sdk2.parameters.String(
                'phantom2d bishop program',
                required=True,
                default='phantom2d',
            )
            phantom2d_bishop_environment = sdk2.parameters.String(
                'phantom2d bishop environment',
                required=True,
                default=DEFAULT_BISHOP_ENV,
            )

        with sdk2.parameters.Group('Secrets parameters') as secrets_parameters:
            deploy_token_yav_secret = sdk2.parameters.YavSecret(
                'YP access secret',
                required=True,
                default=settings.yav_uuid,
                description='Used in requests to yp api',
            )
            deploy_token_yav_secret_key = sdk2.parameters.String(
                'YP access secret key',
                required=True,
                default='deploy-token',
            )

        with sdk2.parameters.Output:
            output_host = sdk2.parameters.String("Host")
            output_port = sdk2.parameters.Integer("Port")

        _binary = binary_task.binary_release_parameters_list(stable=True)

    class Context(sdk2.Task.Context):
        spec = None

    @property
    def deploy_client(self):
        import metrika.pylib.deploy.client

        secret = self.Parameters.deploy_token_yav_secret.data()
        token = secret[self.Parameters.deploy_token_yav_secret_key]

        return metrika.pylib.deploy.client.DeployAPI(token=token)

    @property
    def endpoint_set_id(self):
        return '%s.phantom2d' % self.Parameters.stage_id

    @property
    def st_res_keys_xml_url(self):
        url = self.Parameters.st_res_keys_xml_url
        if not url:
            keys_xml_resource = sdk2.Resource.find(
                type=keys_xml.MetrikaKeysXML,
                attrs={'released': ctt.ReleaseStatus.STABLE},
                limit=1,
            ).first()
            url = 'sbr:{}'.format(keys_xml_resource.id)
        return url

    @property
    def layer_phantom2d_url(self):
        phantom2d_resource = sdk2.Resource.find(
            type=rt.BaseMetrikaBinaryResource,
            attrs={
                'resource_name': 'phantom2d',
                'resource_version': self.Parameters.phantom2d_version,
            },
            limit=1,
        ).first()

        if not phantom2d_resource:
            raise ValueError("Failed to found phantom2d resource")

        return 'sbr:{}'.format(phantom2d_resource.id)

    def on_execute(self):
        spec_text = utils.render(
            'resources/phantom2d-stage-spec.j2',
            context={
                'stage_id': self.Parameters.stage_id,
                'stage_dc': self.Parameters.stage_dc,
                'stage_project_name': self.Parameters.stage_project_name,
                'stage_abc_service_id': self.Parameters.stage_abc_service_id,
                'stage_disk_capacity': self.Parameters.stage_disk_capacity,
                'stage_network_macro': self.Parameters.stage_network_macro,
                'stage_vcpu_limit': self.Parameters.stage_vcpu_limit,
                'stage_memory_limit': self.Parameters.stage_memory_limit,
                'layer_base_url': self.Parameters.layer_base_url,
                'layer_nginx_url': self.Parameters.layer_nginx_url,
                'layer_get_bishop_config_url': self.Parameters.layer_get_bishop_config_url,
                'layer_phantom2d_url': self.layer_phantom2d_url,
                'st_res_unifined_agent_url': self.Parameters.st_res_unifined_agent_url,
                'st_res_geodata_url': self.Parameters.st_res_geodata_url,
                'st_res_informer_url': self.Parameters.st_res_informer_url,
                'st_res_keys_xml_url': self.st_res_keys_xml_url,
                'st_res_uatraits_url': self.Parameters.st_res_uatraits_url,
                'nginx_bishop_program': self.Parameters.nginx_bishop_program,
                'nginx_bishop_environment': self.Parameters.nginx_bishop_environment,
                'ua_bishop_program': self.Parameters.ua_bishop_program,
                'ua_bishop_environment': self.Parameters.ua_bishop_environment,
                'phantom2d_bishop_program': self.Parameters.phantom2d_bishop_program,
                'phantom2d_bishop_environment': self.Parameters.phantom2d_bishop_environment,
            },
        )
        self.Context.spec = spec_text
        spec = yaml.safe_load(spec_text)

        self.deploy_client.stage.deploy_stage(
            spec,
            remove_if_exists=True,
            wait=True,
            wait_kwargs={'timeout': 60 * 30},
        )

        host, port = self.get_phantom2d_address()
        self.Parameters.output_host = host
        self.Parameters.output_port = port

    def get_phantom2d_address(self):
        import metrika.pylib.deploy.resolver as mpdr
        resolver = mpdr.Resolver(
            client_name=self.__class__.__name__,
        )

        timeout = 60 * 5
        poll_period = 15

        host = None
        port = None

        start_ts = time.time()
        current_ts = time.time()

        while True:
            if (current_ts - start_ts) > timeout:
                raise errors.TaskError('Failed to resolve phantom2d endpoints: timeout reached ({}s)'.format(timeout))

            endpoints = resolver.resolve_endpoints(
                endpoint_set_id=self.endpoint_set_id,
                datacenter=self.Parameters.stage_dc,
            )
            if endpoints:
                host = endpoints[0].fqdn
                port = endpoints[0].port
                break

            time.sleep(poll_period)
            current_ts = time.time()

        return host, port
