import json
import logging

from sandbox import sdk2
from sandbox.projects.ab_testing import ConfigureAbTests as configure_ab_tests
from sandbox.projects.common import error_handlers as eh


_EXPERIMENTS_RM_POOL = "experiments_rm"  # RMDEV-2617

# all good people should use this name for experiments testing
_TEMPLATE_NAME = "experiments.json"
_AUTOCLICKER_METRIC_NAME = "diff-2-serps-empty-or-failed-5"


class RunAbTests(configure_ab_tests.ConfigureAbTests):
    class Parameters(configure_ab_tests.ConfigureAbTests.Parameters):
        with sdk2.parameters.Output:
            number_of_tests = sdk2.parameters.Integer("Number of tests", default_value=0)
            web_middle = configure_ab_tests.WebMiddleParameters()
            web_upper = configure_ab_tests.WebUpperParameters()
            web_metrics = configure_ab_tests.WebMetricsParameters()
            images_metrics = configure_ab_tests.ImagesMetricsParameters()
            video_metrics = configure_ab_tests.VideoMetricsParameters()
            market = configure_ab_tests.MarketParameters()
            alice = configure_ab_tests.AliceParameters()
            zen = configure_ab_tests.ZenParameters()
            bigb_main = configure_ab_tests.BigBMainParameters()

    def on_execute(self):
        configure_ab_tests.ConfigureAbTests.on_execute(self)
        self._number_of_tests = {i: 0 for i in ["web", "images", "video", "market", "alice", "zen", "bigb_main"]}
        self.prepare_ab_tests(self.exp_config)
        self.Parameters.number_of_tests = sum(i for i in self._number_of_tests.values())

    def prepare_ab_tests(self, exp_config):
        self.Parameters.testid = int(exp_config["testid"])
        self.Parameters.experiment_id = exp_config["experiment_id"]
        self.Parameters.ups_responsible = self.ups_responsible
        self.set_check_middle_experiment_params(exp_config)
        self.set_check_upper_experiment_params(exp_config)
        self.set_launch_metrics_params(exp_config)
        self.set_market_test_params(exp_config)
        self.set_alice_test_params(exp_config)
        self.set_zen_test_params(exp_config)
        self.set_bigb_main_test_params(exp_config)

    @staticmethod
    def get_handler_flags(params_json, lookfor_handlers):
        params = json.loads(params_json)

        for item in params:
            handler = item.get("HANDLER")
            if handler in lookfor_handlers:
                logging.info('[get_handler_] Found matching handler: %s', handler)
                context = item.get("CONTEXT", {})
                logging.debug('[get_handler_flags] Context:\n%s\n\n', json.dumps(context, indent=4))
                main_context = context.get("MAIN", {}).get(handler, {})
                logging.debug('[get_handler_flags] MAIN Context:\n%s\n\n', json.dumps(main_context, indent=4))
                return main_context

        logging.warning('[get_handler_flags] No matching handler: `%s`', lookfor_handlers)
        return {}

    @staticmethod
    def get_field_noexcept(data, path):
        for field_name in path:
            data = data.get(field_name)
            if not isinstance(data, dict):
                return
        return data

    def set_check_middle_experiment_params(self, test_id_info):
        if "web" in test_id_info["services"]:
            self._number_of_tests["web"] += 1
            self.Parameters.web_middle.web__middle__save_eventlog = True
            self.Parameters.web_middle.web__middle__scraper_pool = _EXPERIMENTS_RM_POOL
            self.Parameters.web_middle.web__middle__new_cgi_param = "&exp_confs=testing&test-id={}".format(
                test_id_info["testid"]
            )

    def set_check_upper_experiment_params(self, test_id_info):
        if "web" in test_id_info["services"]:
            self._number_of_tests["web"] += 1
            self.Parameters.web_upper.web__upper__save_eventlog = True
            self.Parameters.web_upper.web__upper__scraper_pool = _EXPERIMENTS_RM_POOL
            self.Parameters.web_upper.web__upper__new_cgi_param = "&exp_confs=testing&test-id={}".format(
                test_id_info["testid"]
            )

    def set_launch_metrics_params(self, test_id_info):
        if "web" in test_id_info["services"]:
            self._number_of_tests["web"] += 1
            self.Parameters.web_metrics.web__metrics__custom_template_name = _TEMPLATE_NAME
            self.Parameters.web_metrics.web__metrics__scraper_over_yt_pool = _EXPERIMENTS_RM_POOL
            self.Parameters.web_metrics.web__metrics__optimistic_expected_launch_time_sec = 1500  # 25 min
            self.Parameters.web_metrics.web__metrics__sample_beta = "hamster"
            self.Parameters.web_metrics.web__metrics__checked_beta = "hamster"
            self.Parameters.web_metrics.web__metrics__checked_extra_params = "test-id={}".format(test_id_info["testid"])
            self.Parameters.web_metrics.web__metrics__enable_autoclicker = True
            self.Parameters.web_metrics.web__metrics__autoclicker_retry_count = 1
            self.Parameters.web_metrics.web__metrics__autoclicker_metric_name = _AUTOCLICKER_METRIC_NAME
        if "images" in test_id_info["services"]:
            self._number_of_tests["images"] += 1
            self.Parameters.images_metrics.images__metrics__custom_template_name = _TEMPLATE_NAME
            self.Parameters.images_metrics.images__metrics__scraper_over_yt_pool = _EXPERIMENTS_RM_POOL
            self.Parameters.images_metrics.images__metrics__optimistic_expected_launch_time_sec = 1800  # 30 min
            self.Parameters.images_metrics.images__metrics__sample_beta = "hamster"
            self.Parameters.images_metrics.images__metrics__checked_beta = "hamster"
            self.Parameters.images_metrics.images__metrics__checked_extra_params = "test-id={}".format(
                test_id_info["testid"]
            )
            self.Parameters.images_metrics.images__metrics__enable_autoclicker = True
            self.Parameters.images_metrics.images__metrics__autoclicker_retry_count = 1
            self.Parameters.images_metrics.images__metrics__autoclicker_metric_name = _AUTOCLICKER_METRIC_NAME
        if "video" in test_id_info["services"]:
            self._number_of_tests["video"] += 1
            self.Parameters.video_metrics.video__metrics__custom_template_name = _TEMPLATE_NAME
            self.Parameters.video_metrics.video__metrics__scraper_over_yt_pool = _EXPERIMENTS_RM_POOL
            self.Parameters.video_metrics.video__metrics__optimistic_expected_launch_time_sec = 2100  # 35 min
            self.Parameters.video_metrics.video__metrics__sample_beta = "hamster"
            self.Parameters.video_metrics.video__metrics__checked_beta = "hamster"
            self.Parameters.video_metrics.video__metrics__checked_extra_params = "test-id={}".format(
                test_id_info["testid"]
            )
            self.Parameters.video_metrics.video__metrics__enable_autoclicker = True
            self.Parameters.video_metrics.video__metrics__autoclicker_retry_count = 1
            self.Parameters.video_metrics.video__metrics__autoclicker_metric_name = _AUTOCLICKER_METRIC_NAME

    def set_market_test_params(self, test_id_info):
        run_tests = False
        try:
            rearr_factors = set()
            market_handlers = ("MARKET", "MARKETAPPS")
            params = json.loads(test_id_info["params"])
            for item in params:
                handler = item.get("HANDLER")
                context = item.get("CONTEXT", {})
                if handler in market_handlers:
                    for context_params in context.values():
                        rearr = context_params.get("rearr")
                        if rearr:
                            rearr_factors.update(rearr)
                else:
                    rearr = context.get("MAIN", {}).get("MARKET", {}).get("rearr-factors")
                    if rearr:
                        rearr_factors.update(rearr)
            if rearr_factors:
                run_tests = True
                self._number_of_tests["market"] += 1
                self.Parameters.market.market__report_lite_tests_exp__rearr_factors = ";".join(rearr_factors)
        except Exception as exc:
            eh.log_exception('[set_market_test_params]', exc, info=True)
        # sandbox params can be set only once
        self.Parameters.market.market__report_lite_tests_exp__run_tests = run_tests

    def set_alice_test_params(self, test_id_info):
        dry_run = True
        try:
            flags = RunAbTests.get_handler_flags(test_id_info["params"], {"VOICE"}).get("flags", [])
            if flags:
                dry_run = False
                self._number_of_tests["alice"] += 1
                self.Parameters.alice.alice__experiment_flags = ", ".join(flags)
                self.Parameters.alice.alice__launch_type = "ab_experiments"
        except Exception as exc:
            eh.log_exception('[set_alice_test_params]', exc, info=True)
        self.Parameters.alice.alice__dry_run = dry_run  # sandbox params can be set only once

    def set_zen_test_params(self, test_id_info):
        skip_test = True
        # we should run tests if for any of our services, those handlers not empty
        zen_recommender_services = {
            "zen-recommender",
            "zen-blender",
            "zen-galleries",
            "zen-knn",
            "zen-lives",
            "zen-middle",
            "zen-onboarding",
            "zen-promo",
            "zen-showcases",
            "zen-trends",
            "zen-upper",
            "zen-urls",
            "zen-videos",
            "zen-web",
        }
        zen_recommender_handlers = {
            "ZEN_RECOMMENDER",
            "ZEN_BLENDER",
            "ZEN_GALLERIES",
            "ZEN_KNN",
            "ZEN_LIVES",
            "ZEN_MIDDLE",
            "ZEN_ONBOARDING",
            "ZEN_PROMO",
            "ZEN_SHOWCASES",
            "ZEN_TRENDS",
            "ZEN_UPPER",
            "ZEN_URLS",
            "ZEN_VIDEOS",
            "ZEN_WEB",
        }
        try:
            # zen_recommender_services and test_id_info["services"] intersects
            if not zen_recommender_services.isdisjoint(test_id_info["services"]):
                flags = RunAbTests.get_handler_flags(test_id_info["params"], zen_recommender_handlers)

                if flags:
                    skip_test = False
                    self._number_of_tests["zen"] += 1
                    self.Parameters.zen.zen__experiment_flags = flags
        except Exception as exc:
            eh.log_exception('[set_zen_test_params]', exc, info=True)
        self.Parameters.zen.zen__skip_test = skip_test  # sandbox params can be set only once

    def set_bigb_main_test_params(self, test_id_info):
        dry_run = True
        self.Parameters.bigb_main.bigb_main__ft_meta_modes = ["bs", "yabs"]
        try:
            exps_parameters = json.loads(test_id_info["params"])
            an_iterator = filter(lambda item: item.get("HANDLER") == "BIGB_MAIN", exps_parameters)
            params = list(an_iterator)
            path = ['CONTEXT', 'MAIN', 'BIGB_MAIN']
            launch = ['BSParameters', 'AutobudgetSettings']
            bigb_main_exp_settings = list()
            for param in params:
                data = RunAbTests.get_field_noexcept(param, path)
                if not data:
                    continue
                for settings in launch:
                    if data.get(settings):
                        bigb_main_exp_settings.append(param)
                        break
            if bigb_main_exp_settings:
                self._number_of_tests["bigb_main"] += 1
                self.Parameters.bigb_main.bigb_main__ab_experiment_settings = bigb_main_exp_settings
        except Exception as exc:
            eh.log_exception('[set_bigb_main_test_params]', exc, info=True)
        self.Parameters.bigb_main.bigb_main__dry_run = dry_run
