from sandbox.projects import resource_types
from sandbox.projects.ab_testing import check_exp
from sandbox.projects.common import network
from sandbox.projects.common import resource_selectors
from sandbox.projects.common.search import settings as cs_settings
from sandbox.projects.websearch.middlesearch.base_tasks import components as ms_comp, params as ms_params


class CheckMiddleExp(check_exp.CheckExp):
    class Parameters(check_exp.CheckExp.Parameters):
        middlesearch = ms_params.SingleMiddlesearchParametersOptional

    def _get_event_log_path(self):
        if self.Parameters.middlesearch.save_event_log:
            event_log_dump_resource = resource_types.EVENTLOG_DUMP(
                self, "Middlesearch event log, {}".format(self.Parameters.description.encode("utf-8")),
                "middlesearch_event.log"
            )
            return str(event_log_dump_resource.path)

    def init_daemon(self):
        return ms_comp.WebMiddlesearch(
            self,
            binary=self._prepare_resource(resource_selectors.by_last_released_task(
                ms_params.SingleMiddlesearchParametersOptional.executable.resource_type
            )[0]),
            config=self._prepare_resource(resource_selectors.by_max_attr_value(
                ms_params.SingleMiddlesearchParametersOptional.config.resource_type,
                cs_settings.WebSettings.testenv_middle_cfg_attr_name(middle_type="jupiter_mmeta", hamster_cfg=True),
            )),
            models=self._prepare_resource(resource_selectors.by_last_released_task(
                ms_params.SingleMiddlesearchParametersOptional.models_archive.resource_type
            )[0]),
            rearr=self._prepare_resource(resource_selectors.by_max_attr_value(
                ms_params.SingleMiddlesearchParametersOptional.data.resource_type,
                "TE_web_production_mmeta_data",
            )),
            eventlog_path=self._get_event_log_path(),
            start_timeout=900,  # UPS-111
        )

    def get_host(self):
        return "hamster.yandex.ru"

    def create_batch_id(self):
        return "check-middle-exp-{}".format(self.id)

    def _get_additional_cgi_params(self, daemon):
        port = self._get_port(daemon)
        ip = network.get_my_ipv6()
        srcrwrs = "".join("&srcrwr={}:[{}]:{}:5000".format(i, ip, port) for i in ["WEB", "WEB_MISSPELL"])

        return "&{}{}&reqinfo=check_middle_exp_{}".format(self.Parameters.new_cgi_param, srcrwrs, self.id)

    def _get_auto_port(self, daemon):
        return daemon.grpc_port
