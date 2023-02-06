# -*- coding: utf-8 -*-
from sandbox import sdk2
import sandbox.projects.common.search.bugbanner2 as bb2
import sandbox.projects.common.task_env as task_env


class AbDeployingBaseTestRunner(bb2.BugBannerTask):
    '''
        Base task for AB deployment tests
    '''
    class Parameters(sdk2.Task.Parameters):
        testid = sdk2.parameters.Integer("TestId", required=True)
        flagsjson_id = sdk2.parameters.Integer("Flags.json id")

    class Requirements(task_env.TinyRequirements):
        pass

    def on_execute(self):
        raise NotImplementedError()
