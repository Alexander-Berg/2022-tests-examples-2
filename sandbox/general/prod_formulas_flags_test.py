# -*- coding: utf-8 -*-
import os

from sandbox.projects.release_machine.components import configs
from sandbox.projects.release_machine.components.config_core import yappy as yappy_cfg
from sandbox.projects.release_machine.core import const as rm_const


class ProdFormulasFlagsTestCfg(configs.ReferenceTaggedConfig):
    name = "prod_formulas_flags_test"
    responsible = "lucius"

    class Testenv(configs.ReferenceTaggedConfig.Testenv):
        trunk_db = "formulas_flags_test"
        trunk_task_owner = "SEARCH-RELEASERS"

    class Releases(configs.ReferenceTaggedConfig.Releases):
        resources_info = [
            configs.ReleasedResourceInfo(
                name="base_models_res_id",
                resource_type="DYNAMIC_MODELS_ARCHIVE_BASE",
                build_ctx_key="used_prod_models_mapping_url"
            ),
            # Do not filled build ctx key, used for Yappy betas with new config
            configs.ReleasedResourceInfo(
                name="mmeta_models_res_id",
                resource_type="DYNAMIC_MODELS_ARCHIVE",
            ),
            configs.ReleasedResourceInfo(
                name="prod_formulas_flags",
                resource_type="DYNAMIC_MODELS_ALL_FLAGS",
                resource_name="flags_json_res_id",
            ),
        ]

    class Yappy(yappy_cfg.YappyBaseCfg):
        betas = {
            "report-flags-2": yappy_cfg.YappyBetaCfg(
                new_yappy=True,
                beta_name="report-flags-2",
                patches=[
                    yappy_cfg.YappyBetaPatch(
                        patch_file="report-data-flags-2",
                        parent_service="production_report_data_sas_web",
                        resources=[
                            yappy_cfg.YappyParametrizedResource(param_name="flags_json_res_id", local_path="flags.json")
                        ],
                    ),
                    # yappy_cfg.YappyBetaPatch(
                    #     patch_file="fml-models-acceptance-fml-models-acceptance",
                    #     resources=[
                    #         yappy_cfg.YappyParametrizedResource(
                    #             param_name="base_models_res_id", local_path="basesearch.models"
                    #         ),
                    #         yappy_cfg.YappyParametrizedResource(
                    #             param_name="mmeta_models_res_id", local_path="mmeta.models"
                    #         ),
                    #         yappy_cfg.YappyStaticResource(local_path="basesearch.executable", manage_type="BC_DEFAULT"),
                    #         yappy_cfg.YappyStaticResource(local_path="mmeta.executable", manage_type="BC_DEFAULT"),
                    #     ]
                    # ),
                ]
            )
        }

    # Testing acceptance delay notifications (RMDEV-3)
    class Notify(configs.ReferenceTaggedConfig.Notify):
        use_startrek = False

        class Telegram(configs.ReferenceTaggedConfig.Notify.Telegram):
            chats = ['ilyaturuntaev']
            acceptance_delay = {
                rm_const.TaskTypes.LAUNCH_METRICS: 1 * 60 * 60,
                rm_const.TaskTypes.GENERATE_BETA: 5 * 60,
            }
    # ^ Remove after RMDEV-3

    class SvnCfg(configs.ReferenceTaggedConfig.SvnCfg):
        REPO_NAME = "robots"
        tag_name = "production_flags_test"
        tag_folder = "tags/dynamic_ranking_models_test"
        tag_prefix = "stable"
        tag_folder_template = r"{tag_prefix}-{tag_num}"

        @property
        def main_url(self):
            """Root url for branching and tagging operations"""
            return os.path.join(self.repo_base_url, "branches/base/dynamic_ranking_models/production")

    class MetricsCfg(configs.ReferenceTaggedConfig.MetricsCfg):
        limit_s = None

    class ChangelogCfg(configs.ReferenceTaggedConfig.ChangelogCfg):
        dirs = []
        wiki_page = None

    def __init__(self):
        super(ProdFormulasFlagsTestCfg, self).__init__()
        self.yappy_cfg = self.Yappy()
        self.metrics_cfg = self.MetricsCfg()
        self.changelog_cfg = self.ChangelogCfg(self, self.svn_cfg.main_url, self.responsible)
