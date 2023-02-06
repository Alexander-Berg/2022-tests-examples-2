from sandbox.projects.release_machine.components import configs
from sandbox.projects.release_machine.components.config_core.jg import base as jg_base
from sandbox.projects.release_machine.components.config_core.jg.cube import base as jg_cube
from sandbox.projects.release_machine.components.config_core.jg import flow as jg_flow

RESPONSIBLE = configs.Responsible(
    abc=configs.Abc(service_name="load_testing_yc"),
    login="ival83",
)


class CloudLoadTesting(configs.ReferenceCIConfig):
    name = "cloud_load_testing"
    responsible = RESPONSIBLE
    robot = "robot-lunapark"

    class JG(jg_base.BaseReleaseMachineJobGraph):
        @jg_flow.release_flow()
        def release(self):
            graph = super(self.__class__, self).release(self)

            build_cube = jg_cube.Cube(
                task="projects/cloud_load_testing/run_teamcity_build",
                needs=[graph.get("main_graph_entry")],
                input=jg_cube.CubeInput(
                    teamcity_api={
                        "url": "https://teamcity.aw.cloud.yandex.net",
                    },
                    build_type={
                        "id": "YcLoadTesting_LoadTestingServerBuild",
                        "properties": {
                            "branch": "${context.branch}",
                        },
                    },
                    secret={
                        "secret_uid": "sec-01fxqjhk6k88pqcqvq2f8hp3ky",
                    },
                    dependency={
                        "id": 0,
                        "url": "",
                    },
                )
            )

            move_cube = jg_cube.Cube(
                task="projects/cloud_load_testing/run_teamcity_build",
                needs=[build_cube],
                input=jg_cube.CubeInput(
                    teamcity_api={
                        "url": "https://teamcity.aw.cloud.yandex.net",
                    },
                    build_type={
                        "id": "YcLoadTesting_LoadTestingServerMvByHopper",
                    },
                    secret={
                        "secret_uid": "sec-01fxqjhk6k88pqcqvq2f8hp3ky",
                    },
                    dependency={
                        "id": build_cube.output.build.id,
                        "url": build_cube.output.build.url,
                    },
                )
            )

            graph.add(build_cube)
            graph.add(move_cube)
            return graph

    class CI(configs.ReferenceCIConfig.CI):
        a_yaml_dir = "load/projects/cloud/loadtesting"
        secret = "sec-01fxqjhk6k88pqcqvq2f8hp3ky"
        sb_owner_group = "LOAD-ROBOT"

        ya_make_abs_paths_glob = [
            "load/projects/cloud/loadtesting/**",
        ]

        grant_config_update_permissions_to_release_machine_robot = False

    class Releases(configs.ReferenceCIConfig.Releases):
        resources_info = []

    class SvnCfg(configs.ReferenceCIConfig.SvnCfg):
        use_arc = True

    class Notify(configs.ReferenceCIConfig.Notify):
        class Startrek(configs.ReferenceCIConfig.Notify.Startrek):
            queue = "CLOUDLOAD"
            summary_template = "CloudLoadTesting Release #{}"
            use_task_author_as_assignee = False
            assignee = RESPONSIBLE

            ticket_type = "Release"
            tags = ["release-rm-task", "cloud-loadtesting-release"]

    class ChangelogCfg(configs.ReferenceCIConfig.ChangelogCfg):
        wiki_page = "load/loadtesing-internal/changelog/"
        dirs = [
            "load/projects/cloud/loadtesting",
            "load/projects/cloud/cloud_helper",
            "load/projects/cloud/env_config",
        ]
        use_previous_branch_as_baseline = True
