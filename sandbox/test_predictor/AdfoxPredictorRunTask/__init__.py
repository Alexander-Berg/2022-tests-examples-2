import os
import logging
import tarfile
import time
import requests
from sandbox import sdk2
from sandbox.projects.common import network
from sandbox.projects.adfox.resource_types import AdfoxEngineBinaryLayer, AdfoxEngineConfigurationLayer, AdfoxEngineDataLayer
from sandbox.projects.resource_types import OTHER_RESOURCE as OtherResource


class AdfoxPredictorRunTask(sdk2.Task):

    class Requirements(sdk2.Requirements):
        cpu = 32
        ram = 126
        privileged = True

    class Parameters(sdk2.Task.Parameters):
        adfox_engine_binary_layer = sdk2.parameters.Resource('AdfoxEngineBinaryLayer', resource_type=AdfoxEngineBinaryLayer, required=True)
        adfox_engine_configuration_layer = sdk2.parameters.Resource('AdfoxEngineConfigurationLayer', resource_type=AdfoxEngineConfigurationLayer, required=True)
        adfox_engine_data_layer = sdk2.parameters.Resource('AdfoxEngineDataLayer', resource_type=AdfoxEngineDataLayer, required=True)
        cache_amacs = sdk2.parameters.Resource("Cache", resource_type=OtherResource, required=True)
        smooth_coefficients = sdk2.parameters.Resource("Smooth Coefficients", resource_type=OtherResource, required=True)

        yt_token_yav = sdk2.parameters.YavSecret("YAV secret with yt_token", required=True)

        with sdk2.parameters.Output():
            network_ipv6 = sdk2.parameters.String("ipv6 of predictor instance")

    def on_prepare(self):
        self.engine_binary = self._unpack_tar_gz(self._get_path(self.Parameters.adfox_engine_binary_layer))
        self.engine_configuration = self._unpack_tar_gz(self._get_path(self.Parameters.adfox_engine_configuration_layer), "adfox/lua.d")
        self.engine_data = self._unpack_tar_gz(self._get_path(self.Parameters.adfox_engine_data_layer))
        self.cache_amacs = self._get_path(self.Parameters.cache_amacs)
        self.smooth_coefficients = self._unpack_tar_gz(self._get_path(self.Parameters.smooth_coefficients))

        os.symlink("adfox/engine/lua", "lua")

    def on_execute(self):
        with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("AMACS")) as pl:
            amacs = self._run_amacs(pl)
            is_reachable = self._is_amacs_reachable()

            if is_reachable:
                self.Parameters.network_ipv6 = network.get_my_ipv6()
            else:
                raise Exception("Can't start predictor")

            amacs.wait()

    @staticmethod
    def _unpack_tar_gz(tar_gz_file_path, dest_path='.'):
        if dest_path != '.':
            sdk2.helpers.subprocess.Popen(["mkdir", "-p", dest_path]).wait()
        with tarfile.open(tar_gz_file_path, 'r:gz') as tar:
            tar.extractall(dest_path)
        return os.path.join(dest_path, os.path.basename(tar_gz_file_path.replace('tar.gz', '')))

    @staticmethod
    def _get_path(resource):
        return str(sdk2.ResourceData(resource).path)

    def _is_amacs_reachable(self):
        request = "http://localhost:4445/samples"
        while True:
            try:
                time.sleep(60)
                get = requests.get(request)
                logging.info(get)

                if get.status_code == 200:
                    return True
                else:
                    return False
            except requests.exceptions.RequestException:
                continue

    def _run_amacs(self, pl):
        cmd = [
            "./adfox/engine/amacs",
            "--slave",
            "--file", self.cache_amacs,
            "--lua-d-path", "adfox/lua.d",
            "--stderr"
        ]
        os.environ["STAGE_TYPE"] = "PREDICTOR"
        os.environ["YT_TOKEN"] = self.Parameters.yt_token_yav.data()["yt_token"]

        amacs = sdk2.helpers.subprocess.Popen(
            cmd,
            stdout=pl.stdout,
            stderr=pl.stderr
        )

        return amacs
