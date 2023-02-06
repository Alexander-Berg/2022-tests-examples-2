# -*- coding: utf-8 -*-

import sandbox.projects.release_machine.core.const as rm_const
from sandbox.projects.release_machine.components import configs
from sandbox.projects.release_machine.core import releasable_items as ri
import sandbox.projects.release_machine.components.job_graph.presets as jg_presets
import sandbox.projects.release_machine.components.job_graph.utils as jg_utils


RESOURCES = [
    "HORIZON_AGENT_CONFIG_TEST",
    "APP_HOST_STABLE_BRANCH_TEST",
]


class TestingVerticalGraphsCfg(configs.ReferenceBranchedConfig):
    component_group = "apphost_verticals"
    name = "testing_vertical_graphs"
    responsible = "alkapitonov"

    class Testenv(configs.ReferenceBranchedConfig.Testenv):
        """Testenv configuration"""
        trunk_task_owner = "APP_HOST"

        class JobGraph(configs.ReferenceBranchedConfig.Testenv.JobGraph):
            _preset = jg_presets.SingleBuildPreset(
                build_task_name="BUILD_HORIZON_AGENT_CONFIG",
                build_ctx={
                    "vertical": "TEST",
                },
                deploy_system=rm_const.DeploySystem.nanny.name,
                stages=[jg_utils.StageReleaseFrequency(rm_const.ReleaseStatus.stable)],
            )

    class Releases(configs.ReferenceBranchedConfig.Releases):
        """Releases configuration"""
        @property
        def releasable_items(self):
            return [
                ri.ReleasableItem(
                    name=resource.lower(),
                    data=ri.SandboxResourceData(resource, ttl=90),
                    deploy_infos=[
                        ri.NannyDeployInfo(ri.DeployService("production_app_host_sas_test"), dashboards=["apphost_test"]),
                    ],
                ) for resource in RESOURCES
            ]

        allow_robots_to_release_stable = True

    class SvnCfg(configs.ReferenceBranchedConfig.SvnCfg):
        branch_name = "apphost/conf/test"
        tag_name = "apphost/conf/test"

    class Notify(configs.ReferenceBranchedConfig.Notify):
        class Startrek(configs.ReferenceBranchedConfig.Notify.Startrek):
            assignee = "ageraab"
            queue = "APPHOSTGRAPHS"
            summary_template = u"Приемка графов TEST {}"
            add_commiters_as_followers = True
            use_task_author_as_assignee = False
            deadline = 7

    class ChangelogCfg(configs.ReferenceBranchedConfig.ChangelogCfg):
        wiki_page = ""
        observed_paths = [
            "arcadia/apphost/conf/verticals/TEST"
        ]
