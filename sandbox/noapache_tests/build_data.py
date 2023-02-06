from sandbox.projects.release_machine.components.config_core.jg.cube.lib.build import YaMake2
from sandbox.projects.release_machine.components.config_core.jg.cube.lib.internal import TYPE_TEST


class BuildNoapacheupperData(YaMake2):
    TYPE = TYPE_TEST

    def __init__(self, new_tag_cube):
        targets = [
            "search/web/rearrs_upper/rearrange.dynamic",
            "search/web/rearrs_upper/rearrange",
            "search/web/rearrs_upper/rearrange.fast",
        ]

        super(BuildNoapacheupperData, self).__init__(
            targets=targets,
            artifacts=targets,
            resource_types="NOAPACHEUPPER_DATA",
            name="build_noapacheupper_data",
            needs=[new_tag_cube],
            attributes={
                "requirements": {
                    "sandbox": {
                        "platform": "linux"
                    },
                },
            },
        )
