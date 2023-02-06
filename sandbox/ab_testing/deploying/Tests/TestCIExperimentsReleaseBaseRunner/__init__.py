# -*- coding: utf-8 -*-
import logging

from sandbox import sdk2
from sandbox.common import errors
import sandbox.common.types.task as ctt

from sandbox.projects.ab_testing.deploying.Tests.BaseTestRunner import AbDeployingBaseTestRunner


class AbDeployingTestCIExperimentsReleaseBaseRunner(AbDeployingBaseTestRunner):
    '''
        AB deployment E2E and FIJI Test
    '''

    class Parameters(AbDeployingBaseTestRunner.Parameters):
        max_restarts = 0  # USEREXP-6436

    def get_ci_task(self):
        raise NotImplementedError()

    def create_subtask(self):
        task = self.get_ci_task()
        task.enqueue()
        logging.info('Started child task {} [{}]'.format(task.type, task.id))
        self.Context.subtask = task.id
        logging.info('Waiting task')
        raise sdk2.WaitTask(task.id, ctt.Status.Group.FINISH | ctt.Status.Group.BREAK, wait_all=True)

    def on_execute(self):
        if self.Context.subtask:
            task = sdk2.Task[self.Context.subtask]

            msg = 'Subtask {} [{}] finished with status {}'.format(task.type, task.id, task.status)

            if task.status != ctt.Status.SUCCESS:
                logging.warning(msg)
                logging.warning('Try to restart.')

                if self.Context.restarts == self.Parameters.max_restarts:
                    logging.error('No restarts left.')
                    raise errors.TaskFailure(msg)

                self.Context.restarts += 1
                self.create_subtask()

            logging.info(msg)
        else:
            self.Context.restarts = 0
            self.create_subtask()
