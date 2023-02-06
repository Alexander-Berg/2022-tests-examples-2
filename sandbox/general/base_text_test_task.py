# -*- coding: utf-8 -*-
import logging
from sandbox import sdk2
import sandbox.common.types.resource as ctr
import sandbox.common.types.client as ctc

from sandbox.projects.clickhouse.BaseOnCommitTask.base import PostStatuses
from sandbox.projects.clickhouse.BaseOnCommitTask.test_task import BaseOnCommitTestTask
from sandbox.projects.clickhouse.resources import CLICKHOUSE_REPO_NO_SUBMODULES
from sandbox.projects.clickhouse.util.task_helper import decompress_fast


class BaseTextTestTask(BaseOnCommitTestTask):

    class Requirements(BaseOnCommitTestTask.Requirements):
        cores = 1
        ram = 8192  # 8GiB or less
        client_tags = ctc.Tag.MULTISLOT

        class Caches(sdk2.Requirements.Caches):
            pass  # means that task do not use any shared caches

    @classmethod
    def get_resources(cls, commit, repo, pull_request):
        logging.info("Searching for CLICKHOUSE_REPO_NO_SUBMODULES at commit %s", commit.sha)
        resources = sdk2.Resource.find(
            CLICKHOUSE_REPO_NO_SUBMODULES,
            state=ctr.State.READY,
            attrs=dict(commit=commit.sha, pr_number=pull_request.number)
        ).order(-CLICKHOUSE_REPO_NO_SUBMODULES.id).limit(1)
        logging.info("Search finished")
        return resources.first()

    def post_statuses(self):
        return PostStatuses.ALWAYS

    def _save_repo(self, commit, repo, pull_request):
        repo_resource = BaseTextTestTask.get_resources(commit, repo, pull_request)
        logging.info("Downloading resource: {}".format(repo_resource))
        repo_data = sdk2.ResourceData(repo_resource)
        repo_path = str(repo_data.path)
        logging.info("Download finished, archive path %s", repo_path)

        logging.info("Unpacking dowloaded repo")
        decompress_fast(repo_path)

        logging.info("Unpack finished")
        return "./ClickHouse"

    def check(self, repo_path, commit, repo, pull_request):
        raise Exception("Unimplemented")

    def run(self, commit, repo, pull_request):
        logging.info("Start fetching resource with repo")
        repo_path = self._save_repo(commit, repo, pull_request)

        try:
            check_lines, output_path = self.check(repo_path, commit, repo, pull_request)
            if not check_lines:
                self.Parameters.description = self.get_context_name() + " passed"
                return "success", self.Parameters.description, [(self.get_context_name(), "OK")], output_path
            else:
                self.Parameters.description = self.get_context_name() + " Erros:\n" + "\n".join([line[0] for line in check_lines])
                return "failure", "Found {} errors".format(len(check_lines)), check_lines, output_path
        except Exception as ex:
            logging.info("Exception happened %s", ex)
            return "error", "Cannot run " + self.get_context_name(), None, None
