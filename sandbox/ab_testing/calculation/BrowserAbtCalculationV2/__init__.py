# coding: utf-8
import json
import logging
import os

from sandbox import sdk2
from sandbox.common.utils import classproperty
from sandbox.sdk2.helpers import subprocess as sp
from sandbox.projects.common import file_utils as fu
import sandbox.common.types.resource as ctr
import sandbox.common.types.task as ctt
import sandbox.common.types.notification as ctn
from sandbox.common.errors import TaskFailure
from sandbox.projects.geobase.GeodataTreeLingStable.resource import GEODATA_TREE_LING_STABLE


class AbTestingBrowserYaPackageV2(sdk2.Resource):
    pass


class AbTestingBrowserYaPackageBetaV2(sdk2.Resource):
    pass


class LastCalculationBinaryResource(sdk2.parameters.Resource):
    resource_type = AbTestingBrowserYaPackageV2
    state = (ctr.State.READY,)
    required = True

    @classproperty
    def default_value(cls):
        return sdk2.Resource.find(
            cls.resource_type,
            state=cls.state
        ).first()


class LastCalculationBinaryBetaResource(sdk2.parameters.Resource):
    resource_type = AbTestingBrowserYaPackageBetaV2
    state = (ctr.State.READY,)
    required = False

    @classproperty
    def default_value(cls):
        return sdk2.Resource.find(
            cls.resource_type,
            state=cls.state
        ).first()


class LastGeobaseResource(sdk2.parameters.Resource):
    resource_type = GEODATA_TREE_LING_STABLE
    state = (ctr.State.READY,)
    required = False

    @classproperty
    def default_value(cls):
        return sdk2.Resource.find(
            cls.resource_type,
            state=cls.state
        ).first()


class BrowserAbtCalculationResultV2(sdk2.Resource):
    key = sdk2.parameters.String(
        'Calculation key',
        description='Calculation key',
        required=True,
        hint=True,
    )


class BrowserAbtCalculationV2(sdk2.Task):
    """Browser ABT calculation V2"""
    class Requirements(sdk2.Task.Requirements):
        cores = 1
        ram = 2048
        disk_space = 4096

        class Caches(sdk2.Requirements.Caches):
            pass  # means that task do not use any shared caches

    class Parameters(sdk2.Task.Parameters):
        kill_timeout = 3 * 60 * 60
        notifications = [
            sdk2.Notification(
                [ctt.Status.FAILURE, ctt.Status.EXCEPTION, ctt.Status.NO_RES, ctt.Status.TIMEOUT],
                ['baza'],
                ctn.Transport.EMAIL
            )
        ]

        key = sdk2.parameters.String(
            'Calculation key',
            description='Calculation key',
            required=True,
            hint=True,
        )

        author = sdk2.parameters.String(
            'Author'
        )

        resource = LastCalculationBinaryResource(
            'Resource with browser abt binary v2',
        )

        resource_beta = LastCalculationBinaryBetaResource(
            'Resource with browser abt binary beta v2',
        )

        geobase_resource = LastGeobaseResource(
            'Geobase resource',
        )

        yt_token = sdk2.parameters.Vault(
            "YT token",
            description="'name' or 'owner:name' for extracting from Vault",
            required=True
        )

        yt_pool = sdk2.parameters.String(
            "YT pool",
            default="robot-bro-analytics"
        )

        config = sdk2.parameters.JSON(
            "Config",
            required=True,
            default=[]
        )

        server = sdk2.parameters.String(
            "MR Server",
            required=True,
            default="hahn"
        )

        calc_version = sdk2.parameters.String(
            "Calculation version",
            required=True,
            default="prod",
            choices=[
                ('prod', 'prod'),
                ('beta', 'beta')]
        )

    class Context(sdk2.Task.Context):
        shell_commands = []
        files = {}

    def on_execute(self):
        logging.info('Getting binary resource')
        if self.Parameters.calc_version == 'prod':
            resource_path = str(sdk2.ResourceData(self.Parameters.resource).path)
        elif self.Parameters.calc_version == 'beta':
            resource_path = str(sdk2.ResourceData(self.Parameters.resource_beta).path)
        else:
            raise TaskFailure('Unknown calculation version: {}'.format(self.Parameters.calc_version))

        logging.info('Browser_abt resource path: %s', resource_path)

        if self.Parameters.geobase_resource:
            logging.info('Getting geobase resource')
            geobase_resource_path = str(sdk2.ResourceData(self.Parameters.geobase_resource).path)
            logging.info('Geobase resource path: %s', geobase_resource_path)

        logging.info('Saving config')
        config_path = os.path.abspath("config.json")
        with open(config_path, 'w') as config:
            json.dump(self.Parameters.config, config)
        self.Context.files['config'] = str(config_path)
        logging.info('Config saved')

        logging.info('Setting env vars')
        os.environ['MR_RUNTIME'] = 'YT'
        os.environ['YT_PROXY'] = self.Parameters.server
        os.environ["YT_TOKEN"] = self.Parameters.yt_token.data()

        if self.Parameters.yt_pool:
            os.environ['YT_POOL'] = self.Parameters.yt_pool

        self.Context.files['res'] = os.path.abspath('res')

        shell_command = [
            resource_path,
            '-c', self.Context.files['config'],
            '-o', self.Context.files['res'],
        ]
        if self.Parameters.geobase_resource:
            shell_command.extend(['-g', geobase_resource_path])

        self.Context.shell_command = " ".join(shell_command)

        with sdk2.helpers.ProcessLog(self, logger=logging.getLogger('shell_1')) as pl:
            return_code = sp.Popen(self.Context.shell_command, shell=True, stdout=pl.stdout, stderr=sp.STDOUT).wait()
            if return_code != 0:
                raise sp.CalledProcessError(return_code, self.Context.shell_command)

        if not os.path.exists(self.Context.files['res']):
            raise TaskFailure('Result file not exists')

        logging.info('Create resource')
        resource_data = sdk2.ResourceData(BrowserAbtCalculationResultV2(
            self, 'Result json', 'res', key=self.Parameters.key
        ))
        resource_data.path.write_bytes(fu.read_file(self.Context.files['res']))
        resource_data.ready()
