# coding: utf-8

from sandbox.projects.common.build.YaMake import YaMakeTask

from sandbox.projects.common.build import parameters as build_params
from sandbox.projects.common.nanny import nanny

import sandbox.projects.tester.resource_types as resource_types


class BuildTesterBinary(nanny.ReleaseToNannyTask, YaMakeTask):
    """
    Build tester
    """
    type = 'BUILD_TESTER'
    resource_type = resource_types.TesterBinary

    input_parameters = [
        build_params.ArcadiaUrl,
        build_params.BuildType,
        build_params.CheckReturnCode,
        build_params.CheckoutModeParameter,
        build_params.CheckoutParameter,
        build_params.UseArcadiaApiFuse,
        build_params.AllowArcadiaApiFallback,
        build_params.ClearBuild
    ]

    execution_space = 30 * 1024  # 10Gb

    def get_resources(self):
        return {
            self.resource_type.name: {
                'description': self.resource_type.description,
                'resource_type': self.resource_type,
                'resource_path': '',
            }
        }

    def get_targets(self):
        return [
            self.resource_type.arcadia_build_path
        ]

    def get_arts(self):
        return [
            {'path': self.resource_type.arcadia_build_path}
        ]
