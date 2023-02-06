# coding=utf-8
import logging

from sandbox import sdk2
from sandbox.common import errors
from sandbox.common.types import task as ctt

from sandbox.projects.common import link_builder
from sandbox.projects.release_machine.core import const as rm_const
from sandbox.projects.sandbox_ci.sandbox_ci_web4_hermione_e2e import SandboxCiWeb4HermioneE2E
from sandbox.projects.EntitySearch.release_machine_helpers import BetaAcceptingTask, StarTrekReportingTask


ORIGINAL_TASKS_ENV_TAGS = ['DEV', 'SERP/WEB4', 'HERMIONE-E2E']
PLATFORM_TAGS_TO_TEST = ['desktop', 'touch-phone', 'touch-pad']
SANDBOX_CI_SEARCH_INTERFACES_GROUP = 'SANDBOX_CI_SEARCH_INTERFACES'


class EntitySearchEndToEndTesting(BetaAcceptingTask, StarTrekReportingTask, sdk2.Task):
    """ Task for running e2e tests (https://wiki.yandex-team.ru/users/dindikovans/e2eInBackendRelease/) """

    class Parameters(sdk2.Parameters):
        kill_timeout = 3600

        beta_parameters = BetaAcceptingTask.Parameters()
        star_trek_parameters = StarTrekReportingTask.Parameters()

        with sdk2.parameters.Output:
            created_task = sdk2.parameters.Task('Created task', task_type=SandboxCiWeb4HermioneE2E)

    def find_task_to_copy(self):
        return sdk2.Task.find(
            SandboxCiWeb4HermioneE2E,
            status=ctt.Status.Group.FINISH - {ctt.Status.DELETED},
            tags=ORIGINAL_TASKS_ENV_TAGS,
            all_tags=True,
            children=True,
            hidden=True,
        ).limit(10).first()

    @staticmethod
    def _update_parameters(parameters, beta_url):
        parameters.update(
            {
                SandboxCiWeb4HermioneE2E.Parameters.reuse_subtasks_cache.name: False,
                SandboxCiWeb4HermioneE2E.Parameters.reuse_task_cache.name: False,
                SandboxCiWeb4HermioneE2E.Parameters.send_comment_to_searel.name: False,
                SandboxCiWeb4HermioneE2E.Parameters.report_github_statuses.name: False,
                SandboxCiWeb4HermioneE2E.Parameters.send_statistic.name: False,
                SandboxCiWeb4HermioneE2E.Parameters.beta_domain.name: beta_url,
                SandboxCiWeb4HermioneE2E.Parameters.hermione_base_url.name: beta_url,
                SandboxCiWeb4HermioneE2E.Parameters.platforms.name: PLATFORM_TAGS_TO_TEST,
            }
        )

    @staticmethod
    def _copy_parameters(original_task):
        task_type = type(original_task)

        return {
            k: v
            for k, v in original_task.Parameters
            if not getattr(task_type.Parameters, k).__output__
        }

    def on_execute(self):
        with self.memoize_stage.init_sub_tasks():
            self.ensure_stable_beta()
            self.report_start()
            self.init_sub_tasks()

        self.check_children_tasks_status()

    def ensure_stable_beta(self):
        if self.need_to_check_yappy_beta_status():
            self.check_yappy_beta_status(self.Parameters.beta_url)

    def report_start(self):
        if self.need_to_comment_tickets():
            self.add_to_star_trek_grouped_comment(
                status='STARTED',
                content='',
            )

    def init_sub_tasks(self):
        sub_task = self.get_sub_task()

        if not sub_task:
            original_task = self.find_task_to_copy()
            if original_task is None:
                raise errors.TaskFailure('No tasks to clone')

            logging.info('Found task to clone %s' % link_builder.task_link(original_task.id, plain=True))

            sub_task = self.create_sub_task(original_task)
            self.save_sub_task_in_parameters(sub_task)

        raise sdk2.WaitTask(sub_task, ctt.Status.Group.FINISH | ctt.Status.Group.BREAK, wait_all=True)

    def create_sub_task(self, original_task):
        parameters = self._copy_parameters(original_task)

        self._update_parameters(
            parameters,
            beta_url=self.Parameters.beta_url,
        )

        task_description = 'Running e2e tests on {beta}<br>Copied from {cloned_task}'.format(
            beta=self._build_beta_href_element(),
            cloned_task=link_builder.task_link(task_id=original_task.id)
        )
        parameters['description'] = task_description
        parameters['tags'] = ORIGINAL_TASKS_ENV_TAGS
        parameters['owner'] = SANDBOX_CI_SEARCH_INTERFACES_GROUP

        sub_task = SandboxCiWeb4HermioneE2E(self, **parameters).enqueue()
        return sub_task

    def _build_beta_href_element(self):
        href_link = ('' if '//' in self.Parameters.beta_url else '//') + self.Parameters.beta_url

        return link_builder.HREF_TO_ITEM.format(
            link=href_link,
            name=self.Parameters.beta_url
        )

    def save_sub_task_in_parameters(self, sub_task):
        setattr(self.Parameters, "created_task", sub_task)

    def get_sub_task(self):
        return getattr(self.Parameters, "created_task", None)

    @staticmethod
    def make_out_task_parameter(platform_tag):
        return platform_tag.lower().replace('-', '_') + '_task'

    def check_children_tasks_status(self):
        sub_task = getattr(self.Parameters, "created_task")

        self.report_result(sub_task)
        if sub_task.status not in ctt.Status.Group.SUCCEED:
            raise errors.TaskFailure("Sub_task haven't finished successfully: " + str(sub_task.id))

    @property
    def ticket_message_title(self):
        return 'E2E tests over {e2e_base_url}'.format(e2e_base_url=self.Parameters.beta_url)

    @property
    def ticket_group_name(self):
        return rm_const.TicketGroups.E2ETest

    def report_result(self, sub_task):
        if not self.need_to_comment_tickets():
            return

        message = link_builder.task_link(task_id=sub_task.id, plain=True)

        self.add_to_star_trek_grouped_comment(
            status='FAILED' if sub_task.status not in ctt.Status.Group.SUCCEED else 'SUCCESS',
            content=message,
        )
