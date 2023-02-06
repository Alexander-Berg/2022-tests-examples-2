import logging

from sandbox import sdk2
from sandbox.projects import resource_types
from sandbox.projects.ab_testing import check_exp
from sandbox.projects.common import file_utils as fu
from sandbox.projects.common import network
from sandbox.projects.common import resource_selectors
from sandbox.projects.common import error_handlers as eh
from sandbox.projects.common import requests_wrapper
from sandbox.projects.websearch.upper import components as upper_comp
from sandbox.projects.websearch.upper import resources as upper_resources


TOO_MANY_REQUESTS = 429


class CheckUpperExp(check_exp.CheckExp):
    class Requirements(check_exp.CheckExp.Requirements):
        pass

    class Parameters(check_exp.CheckExp.Parameters):
        with sdk2.parameters.Group("Upper parameters") as upper_params:
            executable = sdk2.parameters.Resource(
                "Upper executable", resource_type=upper_resources.NoapacheUpper, required=False,
            )
            rearrange_data = sdk2.parameters.Resource(
                "Rearrange data", resource_type=resource_types.REARRANGE_DATA, required=False,
            )
            rearrange_dynamic_data = sdk2.parameters.Resource(
                "Rearrange dynamic data", resource_type=resource_types.REARRANGE_DYNAMIC_DATA, required=False,
            )
            rearrange_data_fast = sdk2.parameters.Resource(
                "Rearrange data fast", resource_type=upper_resources.RearrangeDataFast, required=False,
            )
            config_source = sdk2.parameters.String(
                'config_source', default='upper-hamster.hamster.yandex.ru', required=True
            )

    def prepare_config(self):
        with self.memoize_stage.get_upper_config(6):
            msg = None
            try:
                upper_cfg = requests_wrapper.get_r(
                    "https://{}/viewconfig?stoker-quota=flags_testing".format(self.Parameters.config_source),
                    no_retry_on_http_codes=[TOO_MANY_REQUESTS],
                    timeout=5,
                )
            except Exception as e:
                msg = str(e)  # UPS-141
            else:
                if int(upper_cfg.status_code) == TOO_MANY_REQUESTS:
                    msg = "Hamster is busy"
                elif "Server" not in upper_cfg.text:
                    msg = "'Server' section not found in config"
                elif "Collection" not in upper_cfg.text:
                    msg = "'Collection' section not found in config"
            if msg is not None:
                self.set_info(
                    "Cannot download correct upper config from {}, let us wait for a while (300s). Reason: {}".format(
                        self.Parameters.config_source, msg
                    )
                )
                # we've downloaded something strange
                raise sdk2.WaitTime(300)

            upper_cfg_path = "upper.cfg"
            logging.debug("Config found:\n%s", upper_cfg.text)
            fu.write_file(upper_cfg_path, upper_cfg.text)
            config = resource_types.NOAPACHEUPPER_CONFIG(self, "Upper hamster config", upper_cfg_path)
            sdk2.ResourceData(config).ready()
            return config
        eh.check_failed("Unable to get upper config")

    def init_daemon(self):
        config = self.prepare_config()
        return upper_comp.Noapacheupper(
            self,
            binary=(
                self.Parameters.executable or
                self._prepare_resource(resource_selectors.by_last_released_task(upper_resources.NoapacheUpper)[0])
            ),
            config=config,
            rearrange_data=(
                self.Parameters.rearrange_data or
                self._prepare_resource(resource_selectors.by_last_released_task(resource_types.REARRANGE_DATA)[0])
            ),
            rearrange_dynamic_data=(
                self.Parameters.rearrange_dynamic_data or
                self._prepare_resource(
                    resource_selectors.by_last_released_task(resource_types.REARRANGE_DYNAMIC_DATA)[0]
                )
            ),
            rearrange_data_fast=(
                self.Parameters.rearrange_data_fast or
                self._prepare_resource(resource_selectors.by_last_released_task(upper_resources.RearrangeDataFast)[0])
            ),
        )

    def get_host(self):
        return self.Parameters.config_source

    def create_batch_id(self):
        return "check-upper-exp-{}".format(self.id)

    def _get_additional_cgi_params(self, daemon):
        return "&{}&srcrwr=UPPER:[{}]:{}:5000&reqinfo=check_upper_exp_{}".format(
            self.Parameters.new_cgi_param, network.get_my_ipv6(), self._get_port(daemon), self.id
        )

    def _get_auto_port(self, daemon):
        return daemon.apphost_port
