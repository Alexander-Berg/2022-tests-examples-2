import sandbox.common.types.task as ctt
from sandbox import common
from sandbox import sdk2
from sandbox.projects.vh.frontend.perf_resource_creator import VhPerfResourceCreator
from sandbox.projects.vh.frontend import (
    YABS_VH_FRONTEND_RELEASE,
)
from sandbox.projects.resource_types import (
    VH_MESSAGE_TEMPLATES,
    VH_LUA_TEMPLATES,
)
from sandbox.projects.vh.frontend.stand_builder import VhStandBuilder


def median(x):
    return sorted(x)[int(len(x)/2)]


def hodges_lehmann_median(a):
    return median([(x + y)/2 for n, x in enumerate(a) for y in a[n:]])


class VhPerfTask(sdk2.Task):
    """ Video hosting performance tests"""

    @property
    def get_token_owner(self):
        return self.Parameters.yt_token_owner if self.Parameters.yt_token_owner else self.owner

    def on_execute(self):
        with self.memoize_stage.create_children:
            self._start_shooting()

        if self.find(VhStandBuilder, status=ctt.Status.Group.SUCCEED).count != len(self.Context.subtasks):
            raise common.errors.TaskFailure("One of the builds failed")
        stands = list(self.find(VhStandBuilder, status=ctt.Status.Group.SUCCEED))
        med = hodges_lehmann_median([stand.Parameters.max_rps for stand in stands])

        self.Parameters.perf_parrot = self.Parameters.resource_creator.Parameters.coefficient * float(med)

    def _start_shooting(self):
        stands = []
        for i in range(5):
            stand = VhStandBuilder(
                self,
                description='perf stand {}'.format(i),
                mysql_tables=self.Parameters.resource_creator.Parameters.mysql_tables,
                plan_creator=self.Parameters.resource_creator.Parameters.plan_creator,
                prebuilt_package=self.Parameters.prebuilt_package,
                yt_index_table_path=self.Parameters.resource_creator.Context.index_table,
                template_resource=self.Parameters.template_resource,
                template_resource_lua=self.Parameters.template_resource_lua,
                use_prebuilt_package=True,
                perf_run=True,
                yt_token_name=self.Parameters.yt_token_name,
                yt_token_owner=self.get_token_owner,
            ).enqueue()
            stands.append(stand)

        tasks_to_wait = stands
        self.Context.subtasks = list([s.id for s in stands])
        # enable this task shaytanama
        waited_statuses = set(common.utils.chain(ctt.Status.Group.FINISH, ctt.Status.Group.BREAK))
        raise sdk2.WaitTask(
            tasks_to_wait,
            waited_statuses,
            wait_all=True
        )

    class Parameters(sdk2.Task.Parameters):

        resource_creator = sdk2.parameters.Task(
            "Task that created perf resources",
            task_type=VhPerfResourceCreator,
            required=True,
        )

        prebuilt_package = sdk2.parameters.Resource(
            "Prebuilt package",
            resource_type=YABS_VH_FRONTEND_RELEASE,
            required=True,
        )

        template_resource = sdk2.parameters.Resource(
            "Message templates resource",
            resource_type=VH_MESSAGE_TEMPLATES,
            required=True
        )

        template_resource_lua = sdk2.parameters.Resource(
            "Lua templates resource",
            resource_type=VH_LUA_TEMPLATES,
            required=True
        )

        yt_token_name = sdk2.parameters.String(
            "YT token name in sandbox vault",
            default="yt_token",
        )

        yt_token_owner = sdk2.parameters.String(
            "YT token owner in sandbox vault",
            default='ROBOT-VH-MASTER',
        )

        with sdk2.parameters.Output():
            perf_parrot = sdk2.parameters.Float(
                "Perf parrots coefficient",
            )
