from sandbox import sdk2
from sandbox.projects.common.build import parameters as build_parameters


class TestChildTask(sdk2.Task):
    class Requirements(sdk2.Requirements):
        cores = 1
        ram = 1024

        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(sdk2.Parameters):
        resource_id = build_parameters.ParentResourceId()

    def on_execute(self):
        for resource_id in self.Parameters.resource_id:
            with open(str(sdk2.ResourceData(sdk2.Resource[resource_id]).path), 'w') as f:
                f.write('Hello')
