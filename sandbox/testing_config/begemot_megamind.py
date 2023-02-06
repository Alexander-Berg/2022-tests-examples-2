# -*- coding: utf-8 -*-
import copy
import itertools
import signal

from sandbox.projects.release_machine.components import configs as cfg
from sandbox.projects.release_machine.components.config_core import yappy as yappy_cfg
from sandbox.projects.release_machine.components.config_core.jg import flow as jg_flow
from sandbox.projects.release_machine.components.config_core.jg.cube import CubeInput
from sandbox.projects.release_machine.components.config_core.jg.cube import base as jg_cube_base
from sandbox.projects.release_machine.components.config_core.jg.cube.lib import (
    dummy as dummy_cubes,
    release as release_cubes,
    yappy as yappy_cubes,
)
from sandbox.projects.release_machine.components.config_core.jg.preset import basic_build_presets
from sandbox.projects.release_machine.core import releasable_items as ri

from sandbox.projects.release_machine.components.config_core.jg.cube.lib.alice.begemot import (
    BegemotMegamindEvoContext,
    BuildBeggins,
    MakeBegemotAmmo,
    ReleaseBegemotMegamindResources,
)
import sandbox.projects.release_machine.components.config_core.jg.cube.lib.alice.begemot.dummy as megabegemot_dummy
from sandbox.projects.release_machine.components.config_core.jg.cube.lib.alice.evo import (
    AliceEvoIntegrationTestsWrapper,
    AliceEvoUe2e,
)
from sandbox.projects.release_machine.components.config_core.jg.cube.lib.begemot.tasks import (
    BegemotTankLoadTest,
    CheckBetaCoredumps,
)


def _update_with_copy(d1, d2):
    d1 = copy.deepcopy(d1)
    d1.update(d2)
    return d1


MEGAMIND_RESOURCES = {
    "args": "BEGEMOT_ARGUMENTS_PARSER",
    "bstr": "BEGEMOT_BSTR",
    "bstr_caller": "BEGEMOT_BSTR_CALLER",
    "eventlog_uploader": "BEGEMOT_EVLOG_UPLOADER",
    "evlogdump": "BEGEMOT_EVLOGDUMP",
    "fast_build_data_downloader": "BEGEMOT_FAST_BUILD_DOWNLOADER",
    "fast_data_callback": "BEGEMOT_FAST_DATA_CALLBACK",
    "instancectl.conf": "BEGEMOT_INSTANCECTL_CONF",
    "worker.cfg": "BEGEMOT_CONFIG",
    "begemot": "BEGEMOT_MEGAMIND_EXECUTABLE",
    "fast_build_config.json": "BEGEMOT_FAST_BUILD_CONFIG_MEGAMIND",
}

BEGGINS_RESOURCES = _update_with_copy(
    MEGAMIND_RESOURCES,
    {
        "begemot": "BEGEMOT_BEGGINS_EXECUTABLE",
        "fast_build_config.json": "BEGEMOT_FAST_BUILD_CONFIG_BEGGINS",
    }
)


CHANGELOG_DIRS = [
    "alice/begemot",
    "alice/nlu",
    "search/begemot/rules",
    "search/wizard/data/wizard",
]


PERMANENT_FOLLOWERS = [  # TODO(@yagafarov) add old followers
    "yagafarov",
]
PERF_MAIL_RECEPIENTS = [
    "yagafarov",
]


BRANCH_BETA_CONFIG_NAME = "beta"
CI_BETA_CONFIG_NAME = "ci_beta"

BEGEMOT_MEGAMIND_SERVICE_NAME = "debug_megabegemot"

HACK_CUBES = 6

RELEASE_BEGGINS_CUBE_NAME = "release_beggins_stable_nanny"


def _generate_beta_cube_name(beta_config):
    return "generate_beta__{}__{}".format(BEGEMOT_MEGAMIND_SERVICE_NAME, beta_config)


def _generate_perf_task_name(is_new):
    return "begemot_tank_load_test_{}".format("new" if is_new else "old")


def _generate_hack_stages_and_cubes():
    #  Hack cubeы to allow testing multible tags
    previous = None
    stages_and_cubes = []
    for i in range(HACK_CUBES):
        name = "hack_{}".format(i)
        stage = jg_flow.ReleaseActionStageData(
            name,
            cube_names=[name],
        )
        cube = dummy_cubes.Dummy(name=name)
        if previous:
            cube.add_requirement(previous)
        stages_and_cubes.append((stage, cube))
        previous = cube
    return stages_and_cubes


class BegemotMegamindCfg(cfg.ReferenceCIConfig):
    name = BEGEMOT_MEGAMIND_SERVICE_NAME
    display_name = "DEBUG megabegemot"
    responsible = cfg.Responsible(abc=cfg.Abc(component_id=5846, role_id=21), login="yagafarov")
    robot = "robot-megabegemoter"

    class MergesCfg(cfg.ReferenceCIConfig.MergesCfg):
        never_merge_to_released_branches = False

    class CI(cfg.ReferenceCIConfig.CI):
        a_yaml_dir = "alice/begemot/testing_config"
        secret = "sec-01g44v6fp7gbq9s1tye6x44w2m"
        sb_owner_group = "BASS"
        ya_make_abs_paths_glob = ["{}/**".format(changelog_dir) for changelog_dir in CHANGELOG_DIRS]
        grant_config_update_permissions_to_release_machine_robot = False

    class JG(basic_build_presets.SingleBuildGeneralJGCfg):
        @property
        def add_beta_generator(self):
            return BRANCH_BETA_CONFIG_NAME

        def _get_build_cube(self, graph):
            return ReleaseBegemotMegamindResources(
                needs=[graph.get(dummy_cubes.RMMainGraphEntry.NAME)],
            )

        @jg_flow.release_flow(
            stages=[
                basic_build_presets.DEFAULT_STAGE_NEW_TAG,
                basic_build_presets.DEFAULT_STAGE_BUILD,
                jg_flow.ReleaseActionStageData(
                    "test",
                    cube_names=[
                        dummy_cubes.TestStageEntry.NAME,
                        _generate_beta_cube_name(BRANCH_BETA_CONFIG_NAME),
                        _generate_perf_task_name(is_new=False),
                        _generate_perf_task_name(is_new=True),
                        AliceEvoUe2e.NAME,
                        AliceEvoIntegrationTestsWrapper.NAME,
                        CheckBetaCoredumps.NAME,
                        megabegemot_dummy.TestStageFinish.NAME,
                    ],
                    cube_types=[
                        "test",
                    ],
                ),
            ]
            + [stage_and_cube[0] for stage_and_cube in _generate_hack_stages_and_cubes()]
            + [
                jg_flow.ReleaseActionStageData(
                    "release",
                    cube_names=[
                        dummy_cubes.ReleaseStageEntry.NAME,
                        _generate_beta_cube_name(CI_BETA_CONFIG_NAME),
                        RELEASE_BEGGINS_CUBE_NAME,
                    ],
                    cube_types=[
                        release_cubes.TYPE_RELEASE,
                    ],
                ),
            ]
        )
        def release(self):
            graph = super(self.__class__, self).release(self)

            build_megamind = graph.get(ReleaseBegemotMegamindResources.NAME)

            build_beggins = BuildBeggins(
                needs=[graph.get(dummy_cubes.RMMainGraphEntry.NAME)],
            )
            graph.add(build_beggins)

            test_stage_entry = graph.get(dummy_cubes.TestStageEntry.NAME)
            test_stage_entry.add_requirement(build_beggins)

            generate_beta = graph.get(_generate_beta_cube_name(BRANCH_BETA_CONFIG_NAME))

            generate_beta.input.merge(
                CubeInput(
                    force_start_beta=True,
                )
            )

            evo_context = BegemotMegamindEvoContext(
                generate_beta,
                component_name=BEGEMOT_MEGAMIND_SERVICE_NAME,
            )
            graph.add(evo_context)

            check_beta_coredumps = self._add_check_beta_coredumps(graph, evo_context)

            perf_finish = self._add_perf_tasks(graph, evo_context)

            evo_tests = AliceEvoIntegrationTestsWrapper(
                CubeInput(
                    megamind_url=evo_context.megamind_url,
                    repeat_failed_test=True,
                    run_call_owner_subtask=True,
                    fail_threshold=10000,  # never fail
                ),
                evo_context=evo_context,
            )
            evo_tests.add_requirement(perf_finish)
            graph.add(evo_tests)

            ue2e = AliceEvoUe2e(
                CubeInput(
                    megamind_url=evo_context.megamind_url,
                    first_tag_num=0,
                    component_name="begemot_megamind",
                ),
                evo_context=evo_context,
            )
            ue2e.add_requirement(perf_finish)
            graph.add(ue2e)

            test_stage_finish = megabegemot_dummy.TestStageFinish()
            test_stage_finish.add_requirement(ue2e)
            test_stage_finish.add_requirement(evo_tests)
            test_stage_finish.add_requirement(check_beta_coredumps)
            graph.add(test_stage_finish)

            release_stage_entry = graph.get("release_stage_entry")
            release_stage_entry.add_requirement(test_stage_finish)

            for _, cube in _generate_hack_stages_and_cubes():
                cube.add_requirement(test_stage_finish)
                release_stage_entry.add_requirement(cube)
                graph.add(cube)

            generate_testing_instance = yappy_cubes.GenerateYappyBeta(
                component_name=self.component_name,
                beta_conf_type=CI_BETA_CONFIG_NAME,
                input=CubeInput(
                    component_resources={
                        res_key: build_megamind.output.resources[res_type].first().id
                        for res_key, res_type in MEGAMIND_RESOURCES.items()
                    },
                    get_beta_names_from_state=True,
                    force_start_beta=True,
                    patch_name="0-0",
                    beta_name_source="STRING",
                ),
                needs=[release_stage_entry],
                manual=True,
            )
            graph.add(generate_testing_instance)

            release_beggins = release_cubes.ReleaseRmComponent2(
                name=RELEASE_BEGGINS_CUBE_NAME,
                component_name=self.component_name,
                task=self.release_task,
                where_to_release="stable",
                input=CubeInput(
                    component_resources={
                        res_key: build_beggins.output.resources[res_type].first().id
                        for res_key, res_type in BEGGINS_RESOURCES.items()
                    },
                    deploy_system="nanny",
                ),
                manual=True,
                needs=[release_stage_entry],
            )
            graph.add(release_beggins)

            return graph

        def _add_check_beta_coredumps(self, graph, evo_context):
            check_beta_coredumps = CheckBetaCoredumps(
                CubeInput(
                    name=evo_context.beta_name,
                    itype="begemot",
                    signals=[
                        "instancectl-exit_signal_{}_mmmm".format(num)
                        for num in [signal.SIGKILL, signal.SIGSEGV, signal.SIGTERM, signal.SIGABRT]
                    ],
                    exclude_substrings=["mmeta"],
                )
            )
            graph.add(check_beta_coredumps)
            return check_beta_coredumps

        def _add_perf_tasks(self, graph, evo_context):
            test_stage_entry = graph.get(dummy_cubes.TestStageEntry.NAME)
            make_ammo = MakeBegemotAmmo(
                CubeInput(
                    yt_token_vault_key="robot-megabegemoter-yt-token",
                    remote_temp_tables_directory="//home/alice/begemot/tmp/tables",
                    remote_temp_files_directory="//home/alice/begemot/tmp/files",
                ),
                needs=[test_stage_entry],
            )
            graph.add(make_ammo)

            def get_load_task(name, title_suffix, beta_name, report_to_ticket=False, benchmark_task=None):
                return BegemotTankLoadTest(
                    name=name,
                    title="PerfTest{}".format(title_suffix),
                    input=CubeInput(
                        tank_names=[
                            "megabegemot-tank-yp-{}.{}.yp-c.yandex.net:8083".format(i, geo)
                            for i, geo in itertools.product([1], ["sas", "vla"])
                        ],
                        type_or_quota="alice-begemot-megamind",
                        queries_prefix="/wizard?",
                        load_plan="line(1, 150, 200s)",
                        rps_to_survive=145,
                        time_threshold=80,
                        retries=3,
                        report_to_release_ticket=report_to_ticket,
                        rm_component=BEGEMOT_MEGAMIND_SERVICE_NAME,
                        make_yasm_panel=True,
                        yasm_panel_type="megamind",
                        report_to_mail=True,
                        force_same_dc=True,
                        mail_recepients=PERF_MAIL_RECEPIENTS,
                        ah_queries=make_ammo.ammo_resource,
                        ticket=evo_context.release_ticket,
                        default_release_ticket=evo_context.release_ticket,
                        beta=beta_name,
                        benchmark_task=benchmark_task,
                        shard="MEGAMIND",
                    ),
                )

            perf_old = get_load_task(
                name=_generate_perf_task_name(is_new=False),
                title_suffix="Old",
                beta_name=evo_context.last_released_beta_name,
            )
            graph.add(perf_old)

            perf_new = get_load_task(
                name=_generate_perf_task_name(is_new=True),
                title_suffix="New",
                beta_name=evo_context.beta_name,
                report_to_ticket=True,
                benchmark_task=perf_old.output.resources["TASK_LOGS"][0].task_id,
            )
            graph.add(perf_new)

            perf_fail = megabegemot_dummy.PerfStageFail(
                needs=[perf_old, perf_new, make_ammo], needs_type=jg_cube_base.CubeNeedsType.FAIL
            )
            graph.add(perf_fail)
            perf_success = megabegemot_dummy.PerfStageSuccess(needs=[perf_old, perf_new, make_ammo])
            graph.add(perf_success)
            perf_finish = megabegemot_dummy.PerfStageFinish(
                needs=[perf_fail, perf_success], needs_type=jg_cube_base.CubeNeedsType.ANY
            )
            graph.add(perf_finish)
            return perf_finish

    class Notify(cfg.ReferenceCIConfig.Notify):
        class Mail(cfg.ReferenceCIConfig.Notify.Mail):
            mailing_list = [
                "begemot-megamind-releases@yandex-team.ru",
            ]

        class Startrek(cfg.ReferenceCIConfig.Notify.Startrek):
            assignee = cfg.Responsible(login="yagafarov")

            queue = "ALICERELEASEDBG"

            summary_template = u"DEBUG ticket megabegemot{}"

            add_commiters_as_followers = False
            deadline = 14
            hide_commits_under_cut = True
            important_changes_limit = 1000

            workflow = {
                "open": "autoTesting",
                "fixProblems": "accepting",
                "production": "close",
                "closed": "reopen",
                "qualityOK": "deploying",
                "accepting": "qualityOK",
                "autoTesting": "autoTestsOK",
                "autoTestsOK": "accepting",
                "deploying": "production",
            }
            followers = PERMANENT_FOLLOWERS

            use_task_author_as_assignee = False
            nanny_reports = True
            write_merges_in_table = True
            ticket_description_prefix = "DEBUG megabegemot"

    class ChangelogCfg(cfg.ReferenceCIConfig.ChangelogCfg):
        wiki_page = ""
        dirs = ["arcadia/{}".format(changelog_dir) for changelog_dir in CHANGELOG_DIRS]
        use_previous_branch_as_baseline = True

    class SvnCfg(cfg.ReferenceCIConfig.SvnCfg):
        max_active_branches = 8
        use_arc = True
        arc_tag_folder = "tags/releases/alice"
        arc_branches_folder = "releases/alice"
        start_version = 28

    class Releases(cfg.ReferenceCIConfig.Releases):

        main_release_flow_independent_stages = True

        @property
        def releasable_items(self):
            return [
                ri.ReleasableItem(
                    name=resource_name,
                    data=ri.SandboxResourceData(resource_type, ttl=90),
                    deploy_infos=[
                        ri.single_nanny_service("begemot_megamind_yp_production_prestable"),
                        ri.single_nanny_service("begemot_megamind_yp_production_sas"),
                        ri.single_nanny_service("begemot_megamind_yp_production_vla"),
                    ],
                )
                for resource_name, resource_type in MEGAMIND_RESOURCES.items()
            ]

        release_followers_permanent = PERMANENT_FOLLOWERS
        wait_for_deploy_time_sec = 4 * 60 * 60
        allow_robots_to_release_stable = True
        allow_old_releases = True

    class Yappy(yappy_cfg.YappyBaseCfg):
        """Config to generate yappy betas"""

        betas = {
            "dev-beta": yappy_cfg.YappyTemplateCfg(
                template_name="alice-begemot-megamind",
                new_yappy=True,
                patches=[
                    yappy_cfg.YappyTemplatePatch(
                        patch_dir="alice-begemot-megamind-custom",
                        resources=[
                            yappy_cfg.YappyParametrizedResource(
                                param_name="args",
                                local_path="args",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="begemot",
                                local_path="begemot",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="bstr_caller",
                                local_path="bstr_caller",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="bstr",
                                local_path="bstr",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="eventlog_uploader",
                                local_path="eventlog_uploader",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="evlogdump",
                                local_path="evlogdump",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="fast_build_config.json",
                                local_path="fast_build_config.json",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="fast_build_data_downloader",
                                local_path="fast_build_data_downloader",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="fast_data_callback",
                                local_path="fast_data_callback",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="instancectl.conf",
                                local_path="instancectl.conf",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="worker.cfg",
                                local_path="worker.cfg",
                            ),
                        ],
                        parent_service="begemot_megamind_hamster",
                    )
                ],
            ),
            BRANCH_BETA_CONFIG_NAME: yappy_cfg.YappyTemplateCfg(
                template_name="begemot-megamind",
                new_yappy=True,
                patches=[
                    yappy_cfg.YappyTemplatePatch(
                        patch_dir="begemot-megamind",
                        resources=[
                            yappy_cfg.YappyParametrizedResource(
                                param_name="args",
                                local_path="args",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="begemot",
                                local_path="begemot",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="bstr_caller",
                                local_path="bstr_caller",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="bstr",
                                local_path="bstr",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="eventlog_uploader",
                                local_path="eventlog_uploader",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="evlogdump",
                                local_path="evlogdump",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="fast_build_config.json",
                                local_path="fast_build_config.json",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="fast_build_data_downloader",
                                local_path="fast_build_data_downloader",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="fast_data_callback",
                                local_path="fast_data_callback",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="instancectl.conf",
                                local_path="instancectl.conf",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="worker.cfg",
                                local_path="worker.cfg",
                            ),
                        ],
                        parent_service="begemot_megamind_hamster",
                    )
                ],
                stop_betas_gap=3,
            ),
            CI_BETA_CONFIG_NAME: yappy_cfg.YappyTemplateCfg(
                template_name="ci-begemot-megamind",
                new_yappy=True,
                patches=[
                    yappy_cfg.YappyTemplatePatch(
                        patch_dir="ci-begemot-megamind",
                        resources=[
                            yappy_cfg.YappyParametrizedResource(
                                param_name="args",
                                local_path="args",
                                storage="/ssd",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="begemot",
                                local_path="begemot",
                                storage="/ssd",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="bstr_caller",
                                local_path="bstr_caller",
                                storage="/ssd",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="bstr",
                                local_path="bstr",
                                storage="/ssd",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="eventlog_uploader",
                                local_path="eventlog_uploader",
                                storage="/ssd",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="evlogdump",
                                local_path="evlogdump",
                                storage="/ssd",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="fast_build_config.json",
                                local_path="fast_build_config.json",
                                storage="/ssd",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="fast_build_data_downloader",
                                local_path="fast_build_data_downloader",
                                storage="/ssd",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="fast_data_callback",
                                local_path="fast_data_callback",
                                storage="/ssd",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="instancectl.conf",
                                local_path="instancectl.conf",
                                storage="/ssd",
                            ),
                            yappy_cfg.YappyParametrizedResource(
                                param_name="worker.cfg",
                                local_path="worker.cfg",
                                storage="/ssd",
                            ),
                        ],
                        parent_service="begemot_megamind_hamster",
                    )
                ],
                stop_betas_gap=3,
            ),
        }
        working_betas_limit = 5
        wait_for_deploy_time_sec = 4 * 60 * 60
