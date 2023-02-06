# -*- coding: utf-8 -*-

import logging
from sandbox import sdk2
from sandbox.common.types import task as ctt

from sandbox.projects.sandbox_ci.constants import TAGS
from sandbox.projects.sandbox_ci.utils import prioritizer
from sandbox.projects.sandbox_ci.infrastats.simple import InfratestInfrastats
from sandbox.projects.sandbox_ci.managers.reports import Reports
from sandbox.projects.sandbox_ci.managers.artifacts import ArtifactsManager
from sandbox.projects.sandbox_ci.task.binary_task import TasksResourceRequirement

MAX_TIMES = 30


class SandboxCiTestRepeater(TasksResourceRequirement, sdk2.Task):
    class Parameters(sdk2.Parameters):
        ref_task = sdk2.parameters.Integer('Reference task', required=True)
        times = sdk2.parameters.Integer(
            'Times to repeat (0—{0} only, Why? Read: https://wiki.yandex-team.ru/search-interfaces/infra/quota/)'.format(MAX_TIMES),
            default=10,
            description='Any number greater than {0} will be treated as {0}. Sandbox Quota and Selenium Grid resources are very expensive.'.format(MAX_TIMES)
        )

    class Requirements(sdk2.Requirements):
        cores = 1

        class Caches(sdk2.Requirements.Caches):
            pass  # means that task do not use any shared caches

    def on_save(self):
        super(SandboxCiTestRepeater, self).on_save()
        self.Parameters.priority = prioritizer.get_priority(self)

    def on_execute(self):
        with self.memoize_stage.make_subtasks(commit_on_entrance=False):
            raise sdk2.WaitTask(
                tasks=self.start_subtasks(self.make_test_tasks()),
                statuses=ctt.Status.Group.FINISH | ctt.Status.Group.BREAK
            )

        postponed_tasks = self.get_postponed_tasks()
        if postponed_tasks:
            raise sdk2.WaitTask(
                tasks=self.start_subtasks(self.remake_postponed_tasks(postponed_tasks)),
                statuses=ctt.Status.Group.FINISH | ctt.Status.Group.BREAK
            )

        with self.memoize_stage.make_infrastats_subtask(commit_on_entrance=False):
            raise sdk2.WaitTask(
                tasks=self.start_subtasks([self.make_infrastats_task(self.Context.test_tasks)]),
                statuses=ctt.Status.Group.FINISH | ctt.Status.Group.BREAK
            )

        with self.memoize_stage.make_report():
            self.Context.report = self.make_report()

    def test_task_factory(self, tags=None):
        if not tags:
            tags = []

        ref_task = sdk2.Task.find(id=[self.Parameters.ref_task], children=True).first()
        params = dict(ref_task.Parameters)
        params.update(
            priority=self.Parameters.priority,
            reuse_task_cache=False,
            reuse_subtasks_cache=False,
            report_github_statuses=False,
            send_statistic=False,
            tags=ref_task.Parameters.tags + [TAGS.REPEATER.value] + tags,
            external_config={'*.tests.limited_grid': True}
        )

        # FIXME(white): remove this when patch for empty client tags in SANDBOX-6008 is deployed
        logging.info('Subtasks params {}'.format(params))
        if not params.get("overwrite_client_tags_flag"):
            params.pop("overwritten_client_tags", None)

        def factory():
            return ref_task.type(self, **params)

        return factory

    def make_test_tasks(self):
        build_test_task = self.test_task_factory()

        times = min(self.Parameters.times, MAX_TIMES)

        test_tasks = [build_test_task() for _ in range(0, times)]
        self.Context.test_tasks = map(int, test_tasks)

        return test_tasks

    def remake_postponed_tasks(self, postponed_tasks):
        build_test_task = self.test_task_factory(tags=[TAGS.RESTARTED.value])
        restart_tasks = [build_test_task() for _ in range(len(postponed_tasks))]

        for t in postponed_tasks:
            t.Parameters.tags = [tag for tag in t.Parameters.tags if tag != TAGS.POSTPONED.value]

        test_task_ids = self.Context.test_tasks
        postponed_task_ids = map(int, postponed_tasks)
        restart_task_ids = map(int, restart_tasks)
        self.Context.test_tasks = [t for t in test_task_ids if t not in postponed_task_ids] + restart_task_ids

        return restart_tasks

    def make_infrastats_task(self, test_tasks):
        test_task_ids = map(int, test_tasks)

        return InfratestInfrastats(
            self,
            tasks=[self.Parameters.ref_task] + test_task_ids,
            wait_tasks=test_task_ids
        )

    def start_subtasks(self, subtasks):
        subtasks_ids = map(int, subtasks)
        result = self.server.batch.tasks.start.update(subtasks_ids)
        logging.info('Subtasks start result {}'.format(result))

        return subtasks

    def get_postponed_tasks(self):
        return list(sdk2.Task.find(
            id=self.Context.test_tasks,
            tags=TAGS.POSTPONED.value,
            status=(ctt.Status.STOPPING, ctt.Status.STOPPED),
        ).limit(0))

    def make_report(self):
        infrastats_task = self.find(InfratestInfrastats).first()
        stats_resource = ArtifactsManager(self).get_infrastats_resource(
            attrs={
                'type': 'infrastats-custom',
                'task_id': infrastats_task.id
            }
        )

        return Reports(self).reports_artifacts([stats_resource.id])

    @sdk2.header()
    def report(self):
        return self.Context.report or "No report. See child tasks for details."
