# -*- coding: utf-8 -*-
from sandbox.projects.release_machine.components import configs
from sandbox.projects.release_machine.core import const as rm_const
from sandbox.projects.release_machine.core import releasable_items as ri
from sandbox.projects.release_machine.components.config_core import notifications
import sandbox.projects.release_machine.components.job_graph.presets as jg_presets
import sandbox.projects.release_machine.components.job_graph.job_arrows as jg_arrows
import sandbox.projects.release_machine.components.job_graph.job_data as jg_data
import sandbox.projects.release_machine.components.job_graph.job_triggers as jg_triggers
import sandbox.projects.release_machine.components.job_graph.stages.test_stage as jg_test
import sandbox.projects.release_machine.components.job_graph.stages.pre_release_stage as jg_prerelease
import sandbox.projects.release_machine.components.job_graph.utils as jg_utils


class ReleaseMachineTestCfg(configs.ReferenceBranchedConfig):
    name = "release_machine_test"
    display_name = u"Release Machine Integration Test"
    responsible = configs.Responsible(
        abc=configs.Abc(service_name="releasemachine", component_id=2676),
        login="ilyaturuntaev",
    )

    class ChangelogCfg(configs.ReferenceBranchedConfig.ChangelogCfg):
        observed_paths = [
            "arcadia/testenv/jobs/release_machine",
            "arcadia/sandbox/projects/release_machine",
        ]
        wiki_page = "JandeksPoisk/KachestvoPoiska/releasemachinetestcomponent/releases/"

    class Releases(configs.ReferenceBranchedConfig.Releases):
        allow_old_releases = True
        allow_robots_to_release_stable = True
        release_followers_permanent = ["mvel"]
        wait_for_deploy_time_sec = 5 * 60  # 5 min
        deploy_system = rm_const.DeploySystem.ya_deploy
        use_release_task_as_ti_task_type = True

        @property
        def releasable_items(self):
            return [
                ri.ReleasableItem(
                    name=self.name,
                    data=ri.SandboxResourceData("RELEASE_MACHINE_INTEGRATION_TEST_RELEASE", ttl=3),
                    deploy_infos=[ri.YaDeployInfo(ri.DeployService("release_machine-deploy-test-stage"))],
                )
            ]

    class Testenv(configs.ReferenceBranchedConfig.Testenv):
        trunk_db = "rm-test-trunk"
        trunk_task_owner = "RELEASE_MACHINE"
        branch_db_template = "rm-test-{testenv_db_num}"

        class JobGraph(configs.ReferenceBranchedConfig.Testenv.JobGraph):

            @property
            def _prerelease(self):

                check_st_release_ticket_jge = jg_test.JobGraphElementTestTrunkCommon(
                    task_name="CHECK_STARTREK_RELEASE_TICKET",
                    job_arrows=[
                        jg_triggers.JobTriggerStartrek(
                            parent_job_data=[
                                jg_data.ParentDataOutput(
                                    input_key="startrek_ticket",
                                    output_key="startrek_issue"
                                ),
                            ],
                        ),
                        jg_triggers.JobTriggerNewBranch(
                            parent_job_data=[
                                jg_data.ParentDataOutput(
                                    input_key="release_number",
                                    output_key="new_branch_number",
                                ),
                            ],
                        ),
                    ],
                    job_params={
                        "job_name_parameter": "CHECK_STARTREK_RELEASE_TICKET",
                    },
                )

                return [
                    jg_prerelease.JobGraphElementNewBranch(),
                    jg_prerelease.JobGraphElementPreliminaryChangelogBranched(),
                    jg_prerelease.JobGraphElementCloneDb(),
                    jg_prerelease.JobGraphElementStartrek(),
                    jg_prerelease.JobGraphElementWiki(),
                    check_st_release_ticket_jge,
                    jg_prerelease.JobGraphElementActionPreReleaseStartrekWiki(
                        job_arrows=[
                            jg_arrows.JobTrigger(
                                job_type=check_st_release_ticket_jge.job_type,
                                job_name_parameter=check_st_release_ticket_jge.job_name_parameter,
                            ),
                        ],
                        use_arc=self._use_arc,
                    ),
                ]

            _preset = jg_presets.SingleBuildPreset(
                build_ctx={
                    "targets": "release_machine/release_machine_test_binary/",
                    "arts": "release_machine/release_machine_test_binary/release_machine_test_binary",
                    "result_rt": "RELEASE_MACHINE_INTEGRATION_TEST_RELEASE",
                    "result_rd": "Binary file for release machine integration test",
                },
                deploy_system=rm_const.DeploySystem.ya_deploy.name,
                stages=[
                    jg_utils.StageReleaseFrequency(rm_const.ReleaseStatus.stable, jg_utils.RunIfDelayNMinutes(10)),
                ],
            )

        class JobPatch(configs.ReferenceBranchedConfig.Testenv.JobPatch):
            @property
            def change_frequency(self):
                return {}

            @property
            def ignore_match(self):
                return super(ReleaseMachineTestCfg.Testenv.JobPatch, self).ignore_match + [
                    "MERGE_FUNCTIONAL",
                    "ROLLBACK_TRUNK_AND_MERGE_FUNCTIONAL",
                    "ROLLBACK_TRUNK_FUNCTIONAL",
                    "BUILD_SANDBOX_TASKS_WITH_OUTPUT_RESOURCE",
                    "RELEASE_MACHINE_FUNCTIONAL",
                    "RELEASE_RM_FUNCTIONAL",
                    "_LAUNCH_METRICS_RELEASE_MACHINE_TEST_WEB",
                    "_TEST__RELEASE_MACHINE_TEST__CHECK_STARTREK_RELEASE_TICKET",
                ]

    class Notify(configs.ReferenceBranchedConfig.Notify):

        notifications = [
            notifications.Notification(
                event_type='NewTag',
                chat_name='RM isturunt',
                conditions=notifications.NotificationCondition(
                    conditions=[
                        notifications.NotificationConditionItem(
                            field='task_data.status',
                            operator='TEXT_EXACTLY_IS',
                            value='FAILURE',
                        ),
                        notifications.NotificationConditionItem(
                            field='new_tag_data.tag_number',
                            operator='EQ',
                            value='1',
                            negate=True,
                        ),
                    ],
                    join_strategy='OR',
                ),
            )
        ]

        class Startrek(configs.ReferenceBranchedConfig.Notify.Startrek):
            queue = "RMTEST"
            assignee = "robot-srch-releaser"
            ticket_type = "Release"
            components = u"Тесты релизной машины"
            summary_template = u"Release machine integration test {}"
            workflow = rm_const.Workflow.BETA_TEST
            add_commiters_as_followers = False
            followers = []
            notify_on_component_versions_change_to_feature_tickets = frozenset(["RMDEV"])

        class Telegram(configs.ReferenceBranchedConfig.Notify.Telegram):
            chats = ["release_machine_test"]
            config = configs.RmTelegramNotifyConfig(chats=configs.NotifyOn(
                task_success=[],
                task_break=[],
                task_failure=[
                    rm_const.TaskTypes.CREATE_BRANCH_OR_TAG.name,
                    rm_const.TaskTypes.RELEASE_RM_COMPONENT.name,
                    rm_const.TaskTypes.ALL_RM_TASKS.name,
                    rm_const.TaskTypes.BUILD.name,
                ],
                custom=[],
            ))

    class SvnCfg(configs.ReferenceBranchedConfig.SvnCfg):
        use_arc = True
        use_zipatch_only = True

        arc_branches_folder = "releases"
        arc_tag_folder = "tags/releases"
        branch_name = "release_machine/release_machine_test"
        tag_name = "release_machine/release_machine_test"

    class CI(configs.ReferenceBranchedConfig.CI):
        a_yaml_dir = "release_machine/release_machine_test_binary"
        secret = "sec-01desry8fbgvnkbeybem81ferv"
        sb_owner_group = "RELEASE_MACHINE"
