# coding=utf-8
import logging
import os
import pkgutil

import jinja2
import sandbox.common.types.notification as ctn
import sandbox.common.types.task as ctt
from sandbox import sdk2
from sandbox.common.errors import TaskFailure

from sandbox.projects.metrika.mobile.sdk.generics.generic_launcher import GenericLauncher
from sandbox.projects.metrika.mobile.sdk.generics.pull_request_tests_launcher.CommentHelper import CommentHelper
from sandbox.projects.metrika.mobile.sdk.generics.pull_request_tests_launcher.ResultCommentContextProvider import \
    get_result_comment_context
from sandbox.projects.metrika.mobile.sdk.generics.pull_request_tests_launcher.StartTaskCommentContextProvider import \
    get_start_task_comment_context


class PullRequestTestsLauncher(GenericLauncher):
    """
    Запускает тесты из PR
    """

    class Requirements(GenericLauncher.Requirements):
        pass

    class Parameters(GenericLauncher.Parameters):
        with sdk2.parameters.Group("Extension") as extension_group:
            extension_version = sdk2.parameters.String("Версия расширения",
                                                       description="Версия расширения браузера для запуска тестов")
            token = sdk2.parameters.String("Токен в yav",
                                           description="Используется для комментариев в bitbucket/arcadia")
            url = sdk2.parameters.String("Url пулл реквеста",
                                         description="Из него достается project, repo, pr_id, для комментариев")
            extension_config = sdk2.parameters.String("Параметры из расширения",
                                                      description="Нужны для комментария в bitbucket/arcadia")

    class Utils(GenericLauncher.Utils):
        comment_helper = None

    class Context(GenericLauncher.Context):
        children = {}  # key: task_id; value: task_name
        comment_parent_id = None

    def on_save(self):
        super(PullRequestTestsLauncher, self).on_save()
        # https://docs.yandex-team.ru/sandbox/dev/notification#upravlenie-notifikaciyami
        already_notified = any(n.recipients == ["alex98"] for n in self.Parameters.notifications)
        if not already_notified:
            self.Parameters.notifications += [
                sdk2.Notification(
                    [ctt.Status.EXCEPTION, ctt.Status.NO_RES, ctt.Status.TIMEOUT, ctt.Status.EXPIRED],
                    ["alex98"],
                    ctn.Transport.EMAIL
                ),
            ]

    def on_execute(self):
        if self.Parameters.url and self.Parameters.token:
            token = sdk2.Vault.data(self.Parameters.token)
            self.Utils.comment_helper = CommentHelper(self.Parameters.url, token)
        self._check_extension_version()
        super(PullRequestTestsLauncher, self).on_execute()

    def _check_extension_version(self):
        if not self._is_version(0, 6):
            self.Utils.comment_helper.say_update_version()
            raise TaskFailure("An outdated version of the extension is used")

    def _run_and_wait_tasks(self):
        with self.memoize_stage.launch_tasks(commit_on_entrance=False):
            for task_id, task_info in self._get_tasks().iteritems():
                task_info["task"].enqueue()
                self.Context.children.update({task_info["task"].id: task_info["name"]})

            if self.Utils.comment_helper:
                self.Context.comment_parent_id = self.Utils.comment_helper.start_task_comment(
                    self._get_start_task_comment_text())
                logging.info("Comment parent id {}".format(self.Context.comment_parent_id))
            raise sdk2.WaitTask(self.Context.children.keys(),
                                tuple(ctt.Status.Group.FINISH) + tuple(ctt.Status.Group.BREAK))

        with self.memoize_stage.send_result_comment(commit_on_entrance=False):
            if self.Utils.comment_helper:
                self.Utils.comment_helper.result_comment(
                    self._get_result_comment_text(),
                    self.Context.comment_parent_id
                )

        with self.memoize_stage.check_children(commit_on_entrance=False):
            self._check_children()

    def _get_start_task_comment_text(self):
        return self._render_jinja(
            "start_task_comment.jinja",
            get_start_task_comment_context(
                self.author,
                self.Parameters.branch,
                self.Context.commit_hash or self.Parameters.commit,
                self.Context.children,
                self.Parameters.extension_config,
            )
        )

    def _get_result_comment_text(self):
        return self._render_jinja(
            "result_comment.jinja",
            get_result_comment_context(self.Context.children)
        )

    @staticmethod
    def _render_jinja(template, context):
        return jinja2.Environment(
            loader=jinja2.ChoiceLoader([
                jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__))),  # for sandbox task
                jinja2.FunctionLoader(lambda name: pkgutil.get_data(__package__, name)),  # for bin task
            ]),
            extensions=["jinja2.ext.do"]
        ).get_template(template).render(context)

    def _is_version(self, major, minor=0, path=0):
        if not self.Parameters.extension_version or self.Parameters.extension_version == "dev":
            return True
        cur_major, cur_minor, cur_path = [int(_) for _ in self.Parameters.extension_version.split(".")]
        if cur_major == major:
            if cur_minor == minor:
                return cur_path >= path
            return cur_minor > minor
        return cur_major > major
