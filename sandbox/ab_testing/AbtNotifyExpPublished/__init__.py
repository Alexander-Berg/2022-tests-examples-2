import os
import sys
import logging
import json

from sandbox.common.types import task as ctt
from sandbox import sdk2
from sandbox.projects.common import time_utils
from sandbox.projects.common import error_handlers
from sandbox.projects.common import binary_task

from sandbox.projects.release_machine.core import task_env
# from sandbox.projects.release_machine.core import const as rm_const
from sandbox.projects.release_machine.helpers import svn_helper as rm_svn

from sandbox.sdk2.vcs import svn

if sys.version_info[0:2] >= (3, 8):  # python 3.8 or higher
    from functools import cached_property
else:
    from sandbox.projects.common.decorators import memoized_property as cached_property

DEFAULT_BASE_PATH = "quality/robots/ab_testing/experiments_publishing"
ARCADIA_KEY_OWNER = 'AB-TESTING'
ARCADIA_KEY_NAME = 'sec-01dx1bdkxjy6h3yn85wfdbx3wp[ssh_key]'


class AbtNotifyExpPublished(binary_task.LastBinaryTaskKosherReleaseMixin, sdk2.Task):
    """
    Notify experiment's DRAFT->PUBLISHED transition

    The task is used to perform a commit when an experiment changes its state from DRAFT to PUBLISHED
    """

    class Parameters(binary_task.LastBinaryReleaseParameters):
        _lbrp = binary_task.binary_release_parameters(stable=True)

        experiment_id = sdk2.parameters.String("experiment_id", required=True)
        timestamp = sdk2.parameters.Integer("timestamp", default=0)

        base_path = sdk2.parameters.String("base_path", default_value=DEFAULT_BASE_PATH)

    class Requirements(task_env.TinyRequirements):
        pass

    def on_enqueue(self):
        self.Requirements.semaphores = ctt.Semaphores(
            acquires=[ctt.Semaphores.Acquire(
                name="{}_{}".format(
                    self.type.name,
                    self.experiment_id,
                ),
                capacity=1,
            )],
            release=(ctt.Status.Group.BREAK, ctt.Status.Group.FINISH),
        )

    @cached_property
    def now(self):
        now = time_utils.datetime_utc()

        self.set_info("Current time preserved: {}".format(time_utils.datetime_to_iso(now)))

        return now

    @property
    def now_timestamp(self):
        return time_utils.datetime_to_timestamp(self.now)

    @property
    def target_timestamp(self):
        return int(self.Parameters.timestamp) or int(self.now_timestamp)

    @property
    def experiment_id(self):
        return self.Parameters.experiment_id

    @cached_property
    def local_arcadia_root_path(self):
        return str(self.path("arcadia"))

    @cached_property
    def commit_dir_path(self):
        logging.debug("... building commit data dir path")
        return os.path.join(
            self.Parameters.base_path,
            str(self.now.year),
            "{:0>2}".format(self.now.month),  # i.e., 01, 02, etc.
        )

    @cached_property
    def commit_file_path(self):
        logging.debug("... building commit data file path")
        return os.path.join(
            self.commit_dir_path,
            "{experiment_id}_{timestamp}.json".format(
                experiment_id=self.experiment_id,
                timestamp=int(self.target_timestamp),
            ),
        )

    def _get_ssh_key(self):
        # return rm_svn.get_ssh_key(self, rm_const.COMMON_TOKEN_OWNER, rm_const.ARC_ACCESS_TOKEN_NAME)
        return rm_svn.get_ssh_key(
            self,
            key_owner=ARCADIA_KEY_OWNER,
            key_name=ARCADIA_KEY_NAME,
        )

    def _get_commit_data_dict(self):
        logging.debug("... building commit data dict")
        return {
            "experiment_id": self.experiment_id,
            "timestamp": self.target_timestamp,
        }

    def _get_commit_dir_path(self):
        logging.debug("... building commit data dir path")
        return os.path.join(
            self.Parameters.base_path,
            str(self.now.year),
            "{:0>2}".format(self.now.month),  # i.e., 01, 02, etc.
        )

    def _get_commit_file_path(self):
        logging.debug("... building commit data file path")
        return os.path.join(
            self.commit_dir_path,
            "{experiment_id}_{timestamp}.json".format(
                experiment_id=self.experiment_id,
                timestamp=int(self.target_timestamp),
            ),
        )

    def _create_dirs(self):
        logging.debug("... creating dirs")

        from library.python import fs

        local_dir_path = os.path.join(self.local_arcadia_root_path, self.commit_dir_path)

        fs.create_dirs(local_dir_path)

        svn.Arcadia.add(local_dir_path, parents=True, force=True)

    def _dump_commit_data(self, commit_data_dict, local_path):

        logging.debug("... dumping commit data")

        from library.python import fs

        with fs.open_file(local_path, "w") as f:
            json.dump(
                commit_data_dict,
                f,
            )

    def commit_experiment_info(self, commit_data_dict):

        logging.info("... checking out Arcadia to %s", self.local_arcadia_root_path)

        local_base_path = os.path.join(self.local_arcadia_root_path, self.Parameters.base_path)

        svn.Arcadia.checkout(
            "arcadia:/arc/trunk/arcadia/{}/".format(self.Parameters.base_path.strip("/")),
            local_base_path,
        )

        local_path = os.path.join(self.local_arcadia_root_path, self.commit_file_path)

        with self._get_ssh_key():

            self._create_dirs()

            self._dump_commit_data(commit_data_dict, local_path)

            svn.Arcadia.add(local_path, parents=True)

            logging.info("... committing")

            commit_result = svn.Arcadia.commit(
                local_base_path,
                "commit expid {} for testing SKIP_CHECK".format(self.experiment_id),
                user=self.author,
            )

            logging.info("... commit result: %s", commit_result)

    def on_execute(self):

        logging.info("Building...")

        commit_data_dict = self._get_commit_data_dict()

        if not commit_data_dict:
            error_handlers.check_failed("Commit data is empty")

        if not self.commit_file_path:
            error_handlers.check_failed("Commit path is empty")

        logging.info("Going to commit %s into %s", commit_data_dict, self.commit_file_path)

        self.commit_experiment_info(commit_data_dict)

        logging.info("Success!")
