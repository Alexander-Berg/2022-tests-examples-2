import logging

from sandbox.common.errors import TaskError
from sandbox.projects.release_machine.helpers.arcanum_helper import ArcanumApi


class CommentHelper(object):

    def __init__(self, url, token):
        if 'a.yandex-team.ru' in url:
            self.helper = ArcanumCommentHelper(url, token)
        else:
            raise TaskError("Sending report to {} is not supported".format(url))

    def start_task_comment(self, text):
        id = self.helper.create_pr_comment(text)
        logging.info("Start task comment id {}".format(id))
        return id

    def result_comment(self, text, parent_id):
        if parent_id:
            self.helper.create_pr_reply(text, parent_id)
        else:
            raise TaskError("Can't send result comment. Unknown id for parent comment")

    def say_update_version(self):
        id = self.helper.create_pr_comment(
            "You are using an outdated version of the extension. "
            "Because of this, an incorrect run of autotests may start. "
            "Update to the latest version according to the instructions "
            "https://wiki.yandex-team.ru/users/alex98/frankenstein-pr-autotests-runner/#obnovlenie"
        )
        logging.info("Update version comment id {}".format(id))
        return id


class ArcanumCommentHelper(ArcanumApi):

    def __init__(self, url, token):
        self.pr_id = url.split('/')[4]
        super(ArcanumCommentHelper, self).__init__(token)

    def create_pr_comment(self, text):
        response = self._do_post(
            "v1/pull-requests/{}/comments".format(self.pr_id),
            data={"content": text, "issue": True}
        )
        if response:
            return response['data']['id']
        return None

    def create_pr_reply(self, text, parent_id):
        return self._do_post(
            url='v1/review-requests-comments/{}/replies'.format(parent_id),
            data={"content": text, "draft": False}
        )
