# -*- coding: utf-8 -*-

from sandbox.common.types import task as ctt

from sandbox import common
from sandbox import sdk2

from sandbox.common.errors import TaskFailure
from sandbox.projects.sandbox_ci.pulse.pulse_regular_pr_test.validator import Validator
from sandbox.projects.sandbox_ci.pulse.pulse_regular_pr_test.config import Config

from sandbox.projects.sandbox_ci.pulse.pulse_shooter import PulseShooter
from sandbox.projects.sandbox_ci.pulse.pulse_static import PulseStatic
from sandbox.projects.sandbox_ci.sandbox_ci_web4 import SandboxCiWeb4
from sandbox.projects.sandbox_ci.task.binary_task import TasksResourceRequirement


class PulseRegularPrTest(TasksResourceRequirement, sdk2.Task):
    projects_config = {
        'web4': {
            'ci_task': SandboxCiWeb4,
            'pulse_shooting_task': PulseShooter,
            'pulse_static_task': PulseStatic,
            'owner': 'serp',
            'repo': 'web4',
        }
    }

    class Parameters(sdk2.Parameters):
        with sdk2.parameters.String('Project', required=True) as project:
            project.values['web4'] = project.Value('web4', default=True)

        pull = sdk2.parameters.Integer('Pull Request number', required=True)
        arc_ref = sdk2.parameters.String('Arc ref', required=True)
        limits = sdk2.parameters.String('Limits described with YAML', required=True, multiline=True)

    @property
    def _ci_task(self):
        return self.projects_config[self.Parameters.project]['ci_task']

    @property
    def _pulse_shooting_task(self):
        return self.projects_config[self.Parameters.project]['pulse_shooting_task']

    @property
    def _pulse_static_task(self):
        return self.projects_config[self.Parameters.project]['pulse_static_task']

    @property
    def _github_owner(self):
        return self.projects_config[self.Parameters.project]['owner']

    @property
    def _github_repo(self):
        return self.projects_config[self.Parameters.project]['repo']

    def on_execute(self):
        with self.memoize_stage.ci_task_stage():
            self._start_ci_task()

        with self.memoize_stage.validate_pulse_tasks_stage():
            config = Config(self.Parameters.limits)
            self._validator = Validator(self, config)

            self._validate_pulse_tasks()

    def _start_ci_task(self):
        ci_task = self._ci_task(
            self,
            description='Pulse regular self checking',
            tags=['PULSE_SELF_CHECK'],
            project_github_owner=self._github_owner,
            project_github_repo=self._github_repo,
            project_git_base_ref='dev',
            project_git_merge_ref='review/{}'.format(self.Parameters.pull),
            project_build_context='pulse-regular-test',
            arc_ref=self.Parameters.arc_ref,
            selective_checks=False,
            reuse_artifacts_cache=True,
            report_github_statuses=True,
            use_arc=True
        ).enqueue()

        raise sdk2.WaitTask(
            tasks=[ci_task],
            statuses=tuple(ctt.Status.Group.FINISH) + tuple(ctt.Status.Group.BREAK),
            wait_all=True,
        )

    def _find_tasks(self, parent=None, task_type=None):
        parent = parent or self
        tasks = (parent.find(
            type=task_type, statuses=tuple(ctt.Status.Group.FINISH) + tuple(ctt.Status.Group.BREAK),
        ).limit(0))

        return list(tasks)

    @common.utils.singleton
    def _find_ci_subtask(self):
        tasks = self._find_tasks(task_type=self._ci_task.type)

        if not tasks:
            raise TaskFailure('Unable to find CI subtask in current task')

        return tasks[0]

    def _find_shooting_tasks(self):
        ci_task = self._find_ci_subtask()
        tasks = self._find_tasks(parent=ci_task, task_type=self._pulse_shooting_task.type)

        if not tasks:
            raise TaskFailure('Unable to find any shooting tasks within CI task #{}'.format(ci_task.id))

        return tasks

    def _find_static_task(self):
        ci_task = self._find_ci_subtask()
        tasks = self._find_tasks(parent=ci_task, task_type=self._pulse_static_task.type)

        if not tasks:
            raise TaskFailure('Unable to find static task within CI task #{}'.format(ci_task.id))

        return tasks[0]

    def _validate_static(self):
        task = self._find_static_task()
        if task.status in ctt.Status.Group.BREAK:
            return ['Static task #{} has broken'.format(task.id)]

        return self._validator.check_static_task(task)

    def _validate_shootings(self):
        shooting_tasks = self._find_shooting_tasks()
        errors = []

        for task in shooting_tasks:
            if task.status in ctt.Status.Group.BREAK:
                errors.append(['Shooting task #{} has broken'.format(task.id)])
                continue

            errors += self._validator.check_shooting_task(task)

        return errors

    def _validate_pulse_tasks(self):
        shooting_errors = self._validate_shootings()
        static_errors = self._validate_static()
        errors = []

        if shooting_errors:
            errors += ['Shooting:'] + shooting_errors

        if static_errors:
            errors += ['Static:'] + static_errors

        if errors:
            raise TaskFailure('\n' + '\n'.join(errors))
