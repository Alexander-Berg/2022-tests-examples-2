# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sandbox.projects.release_machine.components import configs
from sandbox.projects.release_machine.components.config_core.jg.preset import basic_build_presets


class ReleaseMachineTestCiCfg(configs.ReferenceCIConfig):
    name = "release_machine_test_ci"
    responsible = configs.Responsible(
        abc=configs.Abc(service_name="releasemachine", component_id=2676),
        login="ilyaturuntaev",
    )

    class ChangelogCfg(configs.ReferenceCIConfig.ChangelogCfg):
        observed_paths = [
            "arcadia/sandbox/projects/release_machine",
            "arcadia/release_machine/release_machine",
        ]
        wiki_page = ""

    class Notify(configs.ReferenceCIConfig.Notify):
        class Startrek(configs.ReferenceCIConfig.Notify.Startrek):
            queue = "RMTEST"
            assignee = "robot-srch-releaser"
            ticket_type = "Release"
            components = "Тесты релизной машины"
            summary_template = "Release machine test CI {}"
            workflow = configs.rm_const.Workflow.BETA_TEST
            add_commiters_as_followers = False
            followers = []

    class JG(basic_build_presets.SingleBuildYaMakeJGCfg):
        build_task = "KOSHER_YA_MAKE"

    class Releases(configs.ReferenceCIConfig.Releases):
        allow_robots_to_release_stable = True
        wait_for_deploy_time_sec = 5 * 60  # 5 min
        deploy_system = configs.rm_const.DeploySystem.sandbox

        @property
        def releasable_items(self):
            return [
                configs.ri.ReleasableItem(
                    name=self.name,
                    data=configs.ri.SandboxResourceData("RELEASE_MACHINE_TEST_CI_BINARY", ttl=3),
                    build_data=configs.ri.BuildData(
                        target="release_machine/release_machine_test_ci/",
                        artifact="release_machine/release_machine_test_ci/release_machine_test_ci",
                    ),
                    deploy_infos=[configs.ri.SandboxKosherReleaseInfo()],
                )
            ]

    class CI(configs.ReferenceCIConfig.CI):
        a_yaml_dir = "release_machine/release_machine_test_ci"
        secret = "sec-01desry8fbgvnkbeybem81ferv"
        sb_owner_group = "RELEASE_MACHINE"

    class SvnCfg(configs.ReferenceCIConfig.SvnCfg):
        arc_tag_folder = "tags/releases/experimental"
        arc_branches_folder = "releases/experimental"
        branch_name = "release_machine/release_machine_test_ci"
        tag_name = "release_machine/release_machine_test_ci"
