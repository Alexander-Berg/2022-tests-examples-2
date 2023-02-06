# -*- coding: utf-8 -*-
from itertools import chain
import logging


class StartrekClientFacade(object):
    DUPLICATE_TASK_ID = 'duplicates'

    def __init__(self, Startrek, exceptions, token):
        self._st_client = Startrek(useragent='sandbox-task', token=token)
        self._exceptions = exceptions

    def get_linked_tasks_ids(self, task_id, linked_tasks=set()):
        if not self._has_access(task_id):
            return [task_id]
        aliases = self._get_task_aliases(task_id)
        linked_tasks.update(aliases)

        duplicated_task_ids = self._filter_by_access(self._get_duplicate_tasks(task_id) - linked_tasks)

        if not duplicated_task_ids:
            return linked_tasks

        return set(chain(*map(lambda id: self.get_linked_tasks_ids(id, linked_tasks), duplicated_task_ids)))

    def _get_task_aliases(self, task_id):
        st_issue = self._get_st_issue(task_id)

        return self._filter_by_access(set([task_id] + st_issue.aliases))

    def _get_duplicate_tasks(self, task_id):
        issue = self._get_st_issue(task_id)

        duplicates = set()
        for linked_issue in issue.links:
            if linked_issue.type.id == self.DUPLICATE_TASK_ID:
                duplicates.add(linked_issue.object.key)
        return self._filter_by_access(duplicates)

    def _filter_by_access(self, task_ids):
        return set(filter(self._has_access, task_ids))

    def _has_access(self, task_id):
        try:
            self._get_st_issue(task_id)
        except self._exceptions.Forbidden as e:
            logging.warning('Permission denied for issue {}\n{}'.format(task_id, e))
            return False
        return True

    def _get_st_issue(self, task_id):
        return self._st_client.issues[task_id]
