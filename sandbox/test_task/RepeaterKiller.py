# -*- coding: utf-8 -*-

import logging

from sandbox import sdk2
from sandbox.common.rest import Client as RestClient
from sandbox.common.types import task as ctt
from sandbox.common.utils import singleton_property

from sandbox.projects.sandbox_ci.constants import TAGS

SEM_LIMIT = 1000
DEFAULT_LOAD_FACTOR_THRESHOLD = 0.75
MAX_KILLS = 4


class RepeaterKiller(object):
    def __init__(self, task, required_semaphores):
        """
        :param task: task that requires semaphores
        :type task: sandbox.sdk2.Task
        :param required_semaphores: semaphores
        :type required_semaphores: list of sandbox.common.types.Semaphores.Acquire
        """
        self.task = task
        self.required_semaphores = dict([[s.name, s.weight] for s in required_semaphores])

    def maybe_free_semaphores(self):
        """
        Stops repeater tasks that holds required semaphores, if necessary.
        """
        if TAGS.REPEATER.value in self.task.Parameters.tags:
            return

        kills_left = MAX_KILLS

        for sem in self._get_semaphores():
            if self._is_semaphore_enough(sem):
                continue

            while kills_left > 0 and not self._is_semaphore_freed(sem):
                repeater_task = self._get_last_repeater_task(sem)
                if not repeater_task:
                    break

                if self._try_to_free_semaphores(repeater_task):
                    kills_left -= 1

    def _get_semaphores(self):
        """
        :return: semaphores
        :rtype: list of dict
        """
        sem_names_to_check = self.required_semaphores.keys()
        semaphores = self.task.server.semaphore.read(owner=self.task.owner, limit=SEM_LIMIT)['items']

        return filter(lambda s: s['name'] in sem_names_to_check, semaphores)

    def _is_semaphore_enough(self, sem):
        """
        :param sem: semaphore
        :type sem: dict
        :return: whether semaphore have enough room
        :rtype: bool
        """
        return sem['value'] < (sem['capacity'] * self._load_factor_threshold)

    def _is_semaphore_freed(self, sem):
        """
        :param sem: semaphore
        :type sem: dict
        :return: whether semaphore was freed to meet task requirements
        :rtype: bool
        """
        return self.required_semaphores[sem['name']] == 0

    def _try_to_free_semaphores(self, task):
        """
        :param task: repeater task to sacrifice
        :type task: sandbox.sdk2.Task
        :return: whether repeater task was stopped and semaphores were freed
        :rtype: bool
        """
        if not self._kill_repeater_task(task):
            logging.debug('Unable to kill repeater task %s', task.id)
            return False

        logging.debug('Repeater task %s killed', task.id)

        return True

    def _free_semaphores_from_tasks(self, tasks):
        """
        :param tasks
        :type tasks: list of sandbox.sdk2.Task
        """
        for t in tasks:
            # Reduce required semaphores for freed semaphores' weights.
            for s in t.Requirements.semaphores.acquires:
                rem_weight = self.required_semaphores.get(s.name, 0)

                if rem_weight > 0:
                    self.required_semaphores[s.name] -= max(0, rem_weight - s.weight)

    def _get_last_repeater_task(self, sem):
        """
        :param sem: semaphore
        :type sem: dict
        :return: last executed (or so) repeater task that holds specified semaphore
        :rtype: sandbox.sdk2.Task
        """
        return sdk2.Task.find(
            id=self._get_semaphore_task_ids(sem),
            tags=TAGS.REPEATER.value,
            status=(ctt.Status.ASSIGNED, ctt.Status.PREPARING, ctt.Status.EXECUTING),
        ).order(-sdk2.Resource.id).first()

    def _get_semaphore_task_ids(self, sem):
        """
        :param sem: semaphore
        :type sem: dict
        :return: ids of tasks that holds semaphore
        :rtype: list of int
        """
        sem_tasks = self.task.server.semaphore[sem['id']].read()['tasks']

        return map(lambda t: t['task_id'], sem_tasks)

    def _get_victim_subtasks(self, task, subtasks=None):
        """
        :param task
        :type task: sandbox.sdk2.Task
        :param subtasks
        :type subtasks: List of sandbox.sdk2.Task
        :return: plain list of sandbox.sdk2.Task
        :rtype: list of sandbox.sdk2.Task
        """
        if subtasks is None:
            subtasks = set()

        subtasks.add(task)
        if hasattr(task, 'subtasks'):
            for t in task.subtasks:
                subtasks.add(t)
                self._get_victim_subtasks(t, subtasks)

        return subtasks

    def _get_root_repeater_task(self, task):
        """
        :param task: task (usually child of test repeater)
        :type task: sandbox.sdk2.Task
        :return: root of chain test tasks
        :rtype: sandbox.sdk2.Task
        """
        parent_task = sdk2.Task[task.parent] if task.parent else None

        if parent_task and TAGS.REPEATER.value in parent_task.Parameters.tags:
            return self._get_root_repeater_task(parent_task)

        return task

    def _kill_repeater_task(self, task):
        # TODO: Make sure that the repeater task was stopped by `self.task`.
        root_task = self._get_root_repeater_task(task)
        active_tasks = filter(lambda t: t.status in ctt.Status.Group.EXECUTE, self._get_victim_subtasks(root_task))

        stopped = root_task.stop()
        if stopped:
            self._free_semaphores_from_tasks(active_tasks)
            # `task.Parameters.tags += [TAGS.POSTPONED.value]` is not working for tasks in `EXECUTE` status group.
            self._rest_client.task[root_task.id].tags([TAGS.POSTPONED.value])

        return stopped

    @singleton_property
    def _load_factor_threshold(self):
        return float(self.task.config.get_deep_value(['tests', 'repeater_killer', 'load_factor_threshold'], DEFAULT_LOAD_FACTOR_THRESHOLD))

    @singleton_property
    def _rest_client(self):
        # FIXME: `task.server` rest client is jailed and unable to update tasks.
        return RestClient(auth=self.task.vault.read('env.SANDBOX_AUTH_TOKEN'))
