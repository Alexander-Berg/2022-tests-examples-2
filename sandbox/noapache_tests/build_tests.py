from sandbox.projects.release_machine.components.config_core.jg.cube.lib.build import YaMake2
from sandbox.projects.release_machine.components.config_core.jg.cube.lib.internal import TYPE_TEST
from sandbox.projects.common.constants import constants as common_const


class BuildNoapacheupperTest(YaMake2):
    TYPE = TYPE_TEST

    def __init__(self, new_tag_cube, name=None):
        targets = {
            "NOAPACHE_UPPER": "search/daemons/noapacheupper",
            "EVLOGDUMP_EXECUTABLE": "search/tools/evlogdump",
            "APP_HOST_TOOL_CONVERTER_EXECUTABLE": "apphost/tools/converter",
        }

        super(BuildNoapacheupperTest, self).__init__(
            targets=targets.values(),
            artifacts=["{}/{}".format(v, v.split("/")[-1]) for v in targets.values()],
            resource_types=targets.keys(),
            name=name,
            needs=[new_tag_cube],
        )

    @property
    def attributes(self):
        return {
            "requirements": {
                "ram": 64 * 1024 ** 3,  # 64 Gb
                "cores": 1,
                "disk": "80GB",
                "sandbox": {
                    "platform": "linux"
                },
            },
        }


class BuildNoapacheupperWithSanitizer(BuildNoapacheupperTest):
    def __init__(self, new_tag_cube, sanitizer):
        self._sanitizer = sanitizer

        super(BuildNoapacheupperWithSanitizer, self).__init__(
            new_tag_cube,
            name="build_noapacheupper_{}san".format(sanitizer[0]) if sanitizer else "build_noapacheupper_undefined",
        )

    @property
    def input_override(self):
        override = super(BuildNoapacheupperWithSanitizer, self).input_override
        override.update({
            "sanitize": self._sanitizer,
        })

        return override


class BuildNoapacheupperDebugLinux(BuildNoapacheupperTest):
    def __init__(self, new_tag_cube):
        super(BuildNoapacheupperDebugLinux, self).__init__(
            new_tag_cube,
            name="build_noapacheupper_debug_linux",
        )

    @property
    def input_override(self):
        override = super(BuildNoapacheupperDebugLinux, self).input_override
        override.update({
            common_const.BUILD_TYPE_KEY: common_const.DEBUG_BUILD_TYPE,
        })

        return override


class BuildNoapacheupperReleaseLinux(BuildNoapacheupperTest):  # TODO: add dependent compare test cube
    def __init__(self, new_tag_cube):
        super(BuildNoapacheupperReleaseLinux, self).__init__(
            new_tag_cube,
            name="build_noapacheupper_release_linux",
        )

    @property
    def input_override(self):
        override = super(BuildNoapacheupperReleaseLinux, self).input_override
        override.update({
            "check_dependencies": True,
            "banned_dependencies": ",".join([
                "contrib/restricted/boost",  # WIZARD-10298
                "maps/libs/mms",
            ]),
            common_const.THINLTO: True,
            common_const.DEFINITION_FLAGS_KEY: '-DNN_NO_OPENMP',
        })

        return override
