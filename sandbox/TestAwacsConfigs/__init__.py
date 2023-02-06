# -*- coding: utf-8 -*-
import os
import urlparse
import sandbox.sandboxsdk.process as sdk_process
from sandbox.sandboxsdk.parameters import SandboxStringParameter
from sandbox.projects.common.balancer.task import BaseTestBalancerTask


class Target(SandboxStringParameter):
    name = 'target'
    description = 'Target'
    required = True


class BackendsJsonUrl(SandboxStringParameter):
    name = 'backends_json_url'
    description = 'backends.json url'
    default_value = ''
    required = False


class BalancerConfigUrl(SandboxStringParameter):
    name = 'balancer_config_url'
    description = 'Balancer config url'
    default_value = ''
    required = False


class TestAwacsConfigs(BaseTestBalancerTask):
    type = 'TEST_AWACS_CONFIGS'

    input_parameters = BaseTestBalancerTask.input_parameters + [
        Target,
        BackendsJsonUrl,
        BalancerConfigUrl,
    ]

    def get_targets(self):
        return [self.ctx[Target.name]]

    @property
    def __res_dir(self):
        path = self.get_path('res_dir')
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def __wget_res(self, param):
        url = self.ctx.get(param.name)
        if not url:
            return None
        url_path = urlparse.urlparse(url).path
        file_name = os.path.basename(url_path)
        sdk_process.run_process(
            ['wget', '-q', url],
            log_prefix='get_{}'.format(param.name),
        )
        src_path = './' + file_name
        dst_path = os.path.join(self.__res_dir, file_name)
        os.rename(src_path, dst_path)
        return dst_path

    def test_params(self):
        backends_json = self.__wget_res(BackendsJsonUrl)
        balancer_config = self.__wget_res(BalancerConfigUrl)
        return [('backends_json', backends_json), ('balancer_config', balancer_config)]


__Task__ = TestAwacsConfigs
