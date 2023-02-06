# -*- coding: utf-8 -*-
import os

from sandbox.projects.ab_testing import rm_test_config as abrtc
from sandbox.projects.release_machine.core import const as rm_const
from sandbox.projects.release_machine.components import configs
import sandbox.projects.release_machine.components.config_core.release_block as release_block
import sandbox.projects.release_machine.components.config_core.statistics_page as statistics_page
import sandbox.projects.release_machine.components.job_graph.stages.build_stage as jg_build
import sandbox.projects.release_machine.components.job_graph.stages.release_stage as jg_release
import sandbox.projects.release_machine.components.job_graph.stages.test_stage as jg_test
import sandbox.projects.release_machine.components.job_graph.job_arrows as jg_job_arrows
import sandbox.projects.release_machine.components.job_graph.job_data as jg_job_data
import sandbox.projects.release_machine.components.job_graph.job_triggers as jg_job_triggers


# TODO: generalize
def test_results_message(x, params):
    return "Test results of testid (({}component/ab_flags_testids/manage?tag={}&scopes=1 {}))".format(
        rm_const.Urls.RM_URL, params.revision, x
    )


class AbFlagsTestidsCfg(configs.ReferenceTaggedConfig):
    name = "ab_flags_testids"
    responsible = "mvel"

    class Releases(configs.ReferenceTaggedConfig.Releases):
        resources_info = []

        @property
        def block_on_test_results(self):
            return [
                release_block.block_conf(
                    name_filter=rm_const.JobTypes.rm_job_name(rm_const.JobTypes.TEST, self.name, "WEB*"),
                    accept_result_threshold=release_block.CRIT,
                    ignore_empty=False,
                ),
                release_block.block_conf(
                    name_filter=rm_const.JobTypes.rm_job_name(rm_const.JobTypes.TEST, self.name, "FIJI_EXPERIMENTS*"),
                    accept_result_threshold=release_block.CRIT,
                    ignore_empty=False,
                ),
                release_block.block_conf(
                    name_filter=rm_const.JobTypes.rm_job_name(rm_const.JobTypes.TEST, self.name, "METRICS*"),
                    accept_result_threshold=release_block.CRIT,
                    ignore_empty=False,
                ),
            ]

    class Testenv(configs.ReferenceTaggedConfig.Testenv):
        trunk_task_owner = "EXPERIMENTS"
        trunk_db = "ab_flags_testids"

        class JobGraph(configs.ReferenceTaggedConfig.Testenv.JobGraph):
            @property
            def _tag_part(self):
                test_job_triggers = (
                    jg_job_triggers.JobTriggerTestBranchCommon(job_name_parameter="WEB_PROD"),
                    jg_job_triggers.JobTriggerTestBranchCommon(job_name_parameter="METRICS_WEB"),
                    jg_job_triggers.JobTriggerTestBranchCommon(job_name_parameter="METRICS_IMAGES"),
                    jg_job_triggers.JobTriggerTestBranchCommon(job_name_parameter="METRICS_VIDEO"),
                    jg_job_triggers.JobTriggerTestBranchCommon(job_name_parameter="FIJI_EXPERIMENTS_VIDEO"),
                    jg_job_triggers.JobTriggerTestBranchCommon(job_name_parameter="FIJI_EXPERIMENTS_IMAGES"),
                )
                result = [
                    jg_build.JobGraphElementBuildTagged(
                        task_name="CONFIGURE_AB_FLAGS_TESTS",
                        ctx={
                            "run_type": "TESTID_TESTS",
                            "send_event_data": True,
                        },
                        job_params=abrtc.job_params(),
                        job_arrows=jg_job_arrows.ParamsData(
                            input_key="test_id_revision",
                            transform=lambda params, rm_config: params.revision,
                        ),
                    ),
                    jg_release.JobGraphElementNewTagTagged(
                        job_params=abrtc.job_params(
                            # FIXME(mvel): `fail_on_existing_tag` should be named arg of the element
                            ctx={
                                "fail_on_existing_tag": False,
                            },
                        ),
                        job_arrows=(
                            jg_job_arrows.ParamsData("custom_tag_number", lambda params, rm_config: params.revision),
                        ),
                    ),
                    jg_test.JobGraphElementTestTagCommon(
                        task_name="SANDBOX_CI_WEB4_EXPERIMENTS_RELEASE_RUNNER",
                        ctx={
                            "allow_data_flags": True,
                            "release": "latest",
                            "hermionee2e_base_url": "https://yandex.ru",
                            "tests_source": "nothing",
                            "release_machine_mode": True,
                        },
                        job_params=abrtc.job_params(
                            job_name_parameter="WEB_PROD",
                        ),
                        job_arrows=jg_job_triggers.JobTriggerBuild(
                            parent_job_data=(
                                jg_job_data.ParentDataOutput("test_id", "testid"),
                                jg_job_data.ParentDataOutput("description", "web__runner__prod_description"),
                                jg_job_data.ParentDataOutput("run_flags_mode", "web__runner__run_flags_mode"),
                            ),
                        ),
                    ),
                    jg_test.JobGraphElementActionRunAcceptanceTagged(
                        job_params=abrtc.job_params(
                            ignore_parent_job_error=True,
                            required_parent_tests_to_run=[i.this_job_name(self.name) for i in test_job_triggers],
                            ctx={
                                "autotesting_ok": False,
                            },
                        ),
                        job_arrows=(
                            jg_job_arrows.ParamsData(
                                input_key="release_num",
                                transform=lambda params, rm_config: params.revision,
                            ),
                            jg_job_triggers.JobTriggerNewTag(),
                            jg_job_triggers.JobTriggerBuild(
                                parent_job_data=(
                                    jg_job_data.ParentDataOutput("notify_ticket", "experiment_id"),
                                    jg_job_data.ParentDataOutput(
                                        "notify_message",
                                        "testid",
                                        test_results_message,
                                    ),
                                ),
                            ),
                        ) + test_job_triggers
                    )
                ]
                metrics_params = [
                    "description",
                    "custom_template_name",
                    "scraper_over_yt_pool",
                    "sample_beta",
                    "checked_beta",
                    "checked_extra_params",
                ]
                fiji_experiments_params = [
                    "description",
                    "release",
                    "tests_source",
                    "platforms",
                    "service",
                    "hermionee2e_base_url",
                    "run_flags_mode",
                ]
                for search_subtype in [
                    rm_const.SearchSubtypes.IMAGES,
                    rm_const.SearchSubtypes.VIDEO,
                    rm_const.SearchSubtypes.WEB,
                ]:
                    result.append(jg_test.JobGraphElementTestTagCommon(
                        task_name="LAUNCH_METRICS",
                        ctx={
                            "search_subtype": search_subtype,
                            "metrics_mode_type": "release_machine",
                            "template_source": "last_released",
                        },
                        job_params=abrtc.job_params(
                            job_name_parameter="METRICS_{}".format(search_subtype.upper()),
                        ),
                        job_arrows=(
                            jg_job_arrows.ParamsData("release_number", transform=lambda x, _: x.revision),
                            jg_job_triggers.JobTriggerBuild(
                                parent_job_data=[
                                    jg_job_data.ParentDataOutput(i, "{}__metrics__{}".format(search_subtype, i))
                                    for i in metrics_params
                                ],
                            ),
                        )
                    ))
                    if search_subtype != rm_const.SearchSubtypes.WEB:
                        result.append(jg_test.JobGraphElementTestTagCommon(
                            task_name="SANDBOX_CI_FIJI_EXPERIMENTS_RELEASE_RUNNER",
                            ctx={
                                "metrics_mode_type": "release_machine",
                                "release_machine_mode": True,
                            },
                            job_params=abrtc.job_params(
                                job_name_parameter="FIJI_EXPERIMENTS_{}".format(search_subtype.upper()),
                            ),
                            job_arrows=(
                                jg_job_arrows.ParamsData("release_number", transform=lambda x, _: x.revision),
                                jg_job_triggers.JobTriggerBuild(
                                    parent_job_data=[
                                        jg_job_data.ParentDataOutput(
                                            i, "{}__fiji_experiments__{}".format(search_subtype, i)
                                        )
                                        for i in fiji_experiments_params
                                    ] + [jg_job_data.ParentDataOutput("test_id", "testid")],
                                ),
                            )
                        ))
                return result

            @property
            def _release(self):
                return []  # no release here

    class SvnCfg(configs.ReferenceTaggedConfig.SvnCfg):
        tag_prefix = "r"
        tag_name = "flags_testids"

        @property
        def main_url(self):
            return os.path.join(
                self.repo_base_url, "trunk", "arcadia", "quality", "robots", "ab_testing", "flags_testids",
            )

    class Notify(configs.ReferenceTaggedConfig.Notify):
        use_startrek = False

    class ChangelogCfg(configs.ReferenceTaggedConfig.ChangelogCfg):
        dirs = ["."]  # all changes in main url
        wiki_page = ""

    class MetricsCfg(object):
        limit_s = 10800  # 3 hours

    class ReleaseViewer(configs.ReferenceTaggedConfig.ReleaseViewer):
        statistics_page_charts = [statistics_page.PredefinedCharts.TIMESPECTRE_METRICS]

    def __init__(self):
        super(AbFlagsTestidsCfg, self).__init__()
        self.changelog_cfg = self.ChangelogCfg(self, self.svn_cfg.main_url, self.responsible)
