# -*- coding: utf-8 -*-
from __future__ import unicode_literals


import logging

import sandbox.projects.release_machine.components.components_info as rm_comp
import sandbox.projects.release_machine.core as rm_core


class ReleaseMachineTestInfo(rm_comp.ReferenceComponentMetricsed):
    @staticmethod
    def st_create_links(release_ticket, commit_ticket_keys):
        """ RMDEV-53 """
        logging.info(
            "This is test component, do not spam people. "
            "Related tickets for {} are: {}".format(release_ticket.key, list(commit_ticket_keys))
        )

    def get_last_deploy(self, token=None, only_level=None):
        return [rm_core.DeployedResource.from_released(i) for i in self.get_last_release(only_level)]

    def _cleanup_testenv_dbs_after_release(self, major_release_num):
        logging.info("Do not clean testenv databases after release")
