# -*- coding: utf-8 -*-

import json

from sandbox import sdk2


class ArcadiaUidComparer(sdk2.Task):
    class Parameters(sdk2.Parameters):
        task_1 = sdk2.parameters.Task('task 1', task_type='ARCADIA_UID_BUILDER')
        task_2 = sdk2.parameters.Task('task 2', task_type='ARCADIA_UID_BUILDER')

    def on_execute(self):
        task_1_uids = json.loads(self.Parameters.task_1.Context.uids)
        task_2_uids = json.loads(self.Parameters.task_2.Context.uids)
        if (
                len(task_1_uids) != len(task_2_uids)
                or set(task_1_uids).symmetric_difference(set(task_2_uids))
        ):
            self.Context.has_diff = True
        else:
            self.Context.has_diff = False
        self.Context.save()
