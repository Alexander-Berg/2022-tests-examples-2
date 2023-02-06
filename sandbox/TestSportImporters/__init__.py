# -*- coding: utf-8 -*-
from sandbox import sdk2
from sandbox.projects.sport import resource_types
from sandbox.projects.common.build.YaMake2 import YaMake2


IMPORTERS_REQUESTS_MOCK_PATH_ENV = 'IMPORTERS_REQUESTS_MOCK_PATH'


class SportTestImporters(YaMake2):
    class Parameters(YaMake2.Parameters):
        partners_cache_resource = sdk2.parameters.Resource(
            label='Partners cache resource',
            description='Ресурс, передаваемый в переменную ' + IMPORTERS_REQUESTS_MOCK_PATH_ENV,
            resource_type=resource_types.SPORT_PARTNERS_DATA_CACHE,
            required=False
        )

    class Context(YaMake2.Context):
        partners_cache_resource_path = None

    def on_prepare(self):
        super(SportTestImporters, self).on_prepare()

        partners_cache_resource = self.Parameters.partners_cache_resource
        if partners_cache_resource:
            self.Context.partners_cache_resource_path = str(sdk2.ResourceData(partners_cache_resource).path)

    def get_env_vars(self):
        env_vars = super(SportTestImporters, self).get_env_vars()

        partners_cache_resource_path = self.Context.partners_cache_resource_path
        if partners_cache_resource_path:
            env_vars[IMPORTERS_REQUESTS_MOCK_PATH_ENV] = partners_cache_resource_path

        return env_vars
