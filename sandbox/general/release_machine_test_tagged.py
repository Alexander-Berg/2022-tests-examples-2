# -*- coding: utf-8 -*-
from sandbox.projects.release_machine.components import configs
from sandbox.projects.release_machine.core import const as rm_const
from sandbox.projects.release_machine.core import releasable_items as ri
from sandbox.projects.common.constants import constants as common_const
import sandbox.projects.release_machine.components.job_graph.stages.pre_release_stage as jg_prerelease
import sandbox.projects.release_machine.components.job_graph.stages.release_stage as jg_release
import sandbox.projects.release_machine.components.job_graph.stages.build_stage as jg_build
import sandbox.projects.release_machine.components.job_graph.job_data as jg_job_data
import sandbox.projects.release_machine.components.job_graph.job_triggers as jg_job_triggers
import sandbox.projects.release_machine.components.job_graph.utils as jg_utils


class ReleaseMachineTestTaggedCfg(configs.ReferenceTaggedConfig):
    """ Config for RM test component with tagged release cycle """

    name = "release_machine_test_tagged"
    responsible = configs.Responsible(abc=configs.Abc(component_id=2676), login="ilyaturuntaev")

    class Releases(configs.ReferenceBranchedConfig.Releases):
        allow_old_releases = True
        allow_robots_to_release_stable = True
        release_followers_permanent = ["ilyaturuntaev"]
        deploy_system = rm_const.DeploySystem.nanny

        @property
        def releasable_items(self):
            return [
                ri.ReleasableItem(
                    name=self.name,
                    data=ri.SandboxResourceData(
                        "RELEASE_MACHINE_TEST_TAGGED_RELEASE",
                        dst_path="release_machine_test_binary"
                    ),
                    deploy_infos=[ri.single_nanny_service("release_machine_test")],
                ),
                ri.DynamicReleasableItem(
                    name="scheduled_bundle",
                    data=ri.SandboxResourceData("SCHEDULED_RM_RELEASE_DATA"),
                    deploy_infos=[ri.single_nanny_service("release_machine_test")],
                ),
            ]

    class Testenv(configs.ReferenceTaggedConfig.Testenv):
        trunk_task_owner = "RELEASE_MACHINE"

        class JobGraph(configs.ReferenceTaggedConfig.Testenv.JobGraph):

            @property
            def _tag_part(self):
                return super(self.__class__, self)._tag_part + [
                    jg_build.JobGraphElementBuildTagged(
                        task_name="YA_MAKE_2",
                        ctx={
                            common_const.BUILD_SYSTEM_KEY: common_const.SEMI_DISTBUILD_BUILD_SYSTEM,
                            "targets": "release_machine/release_machine_test_binary/",
                            "arts": "release_machine/release_machine_test_binary/release_machine_test_binary",
                            "result_rt": "RELEASE_MACHINE_TEST_TAGGED_RELEASE",
                            "result_rd": "Binary file for release machine test (tagged)",
                            "checkout": True,
                        },
                        out={"RELEASE_MACHINE_TEST_TAGGED_RELEASE": 3},
                    )
                ]

            @property
            def _release(self):
                return super(self.__class__, self)._release + [
                    jg_release.JobGraphElementNewTagTagged(),
                    jg_prerelease.JobGraphElementPreliminaryChangelogTagged(),
                    jg_prerelease.JobGraphElementWikiNoStartrek(),
                    jg_release.JobGraphElementReleaseTagged(
                        task_name="RELEASE_RM_COMPONENT_2",
                        release_to=rm_const.ReleaseStatus.stable,
                        job_params={
                            "ctx": {
                                "deploy_system": rm_const.DeploySystem.nanny_push.name,
                                "comment_in_linked_tickets": False
                            }
                        },
                        job_arrows=(
                            jg_job_triggers.JobTriggerBuild(
                                parent_job_data=(
                                    jg_job_data.ParentDataDict(
                                        "component_resources",
                                        self.name,
                                        "RELEASE_MACHINE_TEST_TAGGED_RELEASE",
                                    )
                                ),
                            ),
                            jg_job_triggers.JobTriggerNewTag(
                                jg_job_data.ParentDataOutput("major_release_num", "new_tag_number")
                            ),
                        ),
                    ),
                    jg_release.JobGraphElementActionReleaseTagged(
                        release_to=rm_const.ReleaseStatus.stable,
                        job_params={
                            "frequency": (jg_utils.TestFrequency.RUN_IF_DELAY_N_MINUTES, 90),
                        },
                        job_arrows=jg_job_triggers.JobTriggerWiki(),
                    ),
                ]

    class Notify(configs.ReferenceTaggedConfig.Notify):
        use_startrek = False

        class Telegram(configs.ReferenceTaggedConfig.Notify.Telegram):
            chats = ["rm_maintainers"]
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

        class Mail(configs.ReferenceTaggedConfig.Notify.Mail):
            mailing_list = ["ilyaturuntaev@yandex-team.ru"]

    class ChangelogCfg(configs.ReferenceTaggedConfig.ChangelogCfg):
        dirs = [
            "arcadia/sandbox/projects/release_machine",
        ]
        wiki_page = "JandeksPoisk/KachestvoPoiska/releasemachinetesttaggedcomponent/releases/"

    class CI(configs.ReferenceBranchedConfig.CI):
        secret = "sec-01desry8fbgvnkbeybem81ferv"
        sb_owner_group = "RELEASE_MACHINE"

    def __init__(self):
        super(ReleaseMachineTestTaggedCfg, self).__init__()
        self.changelog_cfg = self.ChangelogCfg(self, self.svn_cfg.main_url, self.responsible)
