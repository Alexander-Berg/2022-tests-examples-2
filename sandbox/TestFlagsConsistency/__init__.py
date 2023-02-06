import logging

import sandbox.common.errors as c_err
from sandbox.projects.common.binary_task import deprecated as binary_task
import sandbox.projects.common.dynamic_models.check as models_check
import sandbox.projects.common.dynamic_models.const as models_const
import sandbox.sdk2 as sdk2


class TestFlagsConsistency(binary_task.LastBinaryTaskRelease, sdk2.Task):
    """
        * Checks that every model in flags.json has its file in experiments folder
    """
    class Requirements(sdk2.Task.Requirements):
        disk_space = 512  # 512 Mb

    class Parameters(binary_task.LastBinaryReleaseParameters):
        kill_timeout = 15 * 60  # 15 min
        prod_models_flags_revision = sdk2.parameters.Integer("Revision of prod flags")

    def on_execute(self):
        binary_task.LastBinaryTaskRelease.on_execute(self)
        for formula_type in ["base", "mmeta"]:
            local_file_name = "test_base" if formula_type == "base" else "test_middle"
            self.check_all_formulas_in_exp(local_file_name, models_const.MODELS_EXPERIMENT_URL)

    def check_all_formulas_in_exp(self, local_file_name, exp_url):
        not_existent_files = list(self.check_file(local_file_name, exp_url))
        if not_existent_files:
            raise c_err.TaskFailure(
                "There are files, which are not exist in experiments folder: {}".format(not_existent_files)
            )

    def check_file(self, local_file_name, exp_url):
        exp_files = set(sdk2.svn.Arcadia.list(exp_url, as_list=True))
        logging.info("There are %s files in %s", len(exp_files), exp_url)
        file_name = models_const.MODELS_PROD_URL + local_file_name
        sdk2.svn.Arcadia.export(file_name, local_file_name, revision=self.Parameters.prod_models_flags_revision)
        return models_check.check_one_mapping(local_file_name, exp_files)
