# -*- coding: utf-8 -*-

from sandbox import sdk2
from sandbox.common.types.task import Priority


class JudTierMarkFMLFilesForTestenv(sdk2.Task):
    """
        Помечает FML-ресурсы указанной задачи MAKE_ESTIMATED_POOL атрибутом автоапдейта TestEnv
    """

    class Parameters(sdk2.Task.Parameters):
        main_task = sdk2.parameters.Task('Pool collection task', task_type="MAKE_ESTIMATED_POOL", required=True)

    class Requirements(sdk2.Task.Requirements):
        cores = 1

        class Caches(sdk2.Requirements.Caches):
            pass

    def on_execute(self):
        main_task = self.Parameters.main_task
        self.mark(main_task.Context.ratings_resource_id, 'ratings')
        self.mark(main_task.Context.requests_resource_id, 'requests')

    def mark(self, resource_id, name):
        child = sdk2.Task["MODIFY_RESOURCE"](
            self,
            description=self.Parameters.description + ", clone " + name,
            owner=self.Parameters.owner,
            priority=Priority(Priority.Class.SERVICE, Priority.Subclass.NORMAL),
            cmdline_kind='clone',
            set_attrs={"TE_prod_JudTier": "#"+str(self.Parameters.main_task.id)},
            src_resource=resource_id,
        )
        sdk2.Task.server.task[child.id].update({'requirements': {'disk_space': 10 << 30}})
        child.enqueue()
