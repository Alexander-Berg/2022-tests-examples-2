# -*- coding: utf-8 -*-
import os
import re
import logging
import tarfile
from sandbox import sdk2

from sandbox.projects.ab_testing import SESSION_MANAGER_FRONTEND
from sandbox.projects.common.nanny import nanny
from sandbox.projects.common import utils


class BuildSessionManagerFrontend(nanny.ReleaseToNannyTask2, sdk2.Task):
    '''
        Build session manager frontend tar
    '''
    class Parameters(sdk2.Task.Parameters):
        arcadia_url = sdk2.parameters.ArcadiaUrl(
                "Arcadia Url", default_value="arcadia:/arc/trunk/arcadia", required=True)

    PATH_PACKET = 'sema'
    URL_SEMA_SVN = 'quality/ab_testing/scripts/sema'
    PATH_TGZ = 'sema.tar.gz'

    def arcadia_info(self):
        return self.revision, "Session manager {} r{}".format(
                self.branch, self.revision), self.branch

    def _get_arcadia_url(self, arcadia_path):
        url_parsed = sdk2.svn.Arcadia.parse_url(self.url_arcadia)
        path_new = re.sub(r'/arcadia.*', '/arcadia/' + arcadia_path, url_parsed.path, count=1)
        return sdk2.svn.Arcadia.replace(self.url_arcadia, path=path_new)

    def _export_arcadia(self, arcadia_path, path):
        url = self._get_arcadia_url(arcadia_path)
        logging.info("EXPORT '{}' TO '{}'".format(url, path))
        sdk2.svn.Arcadia.export(url, path)

    def _make_resource(self, path_packet):
        logging.info('create tgz file')
        with tarfile.open(str(self.path(self.PATH_TGZ)), 'w:gz') as tar:
            tar.dereference = True
            for entry in os.listdir(path_packet):
                tar.add(os.path.join(path_packet, entry), entry)
        sdk2.ResourceData(SESSION_MANAGER_FRONTEND(self, self.PATH_TGZ, self.PATH_TGZ))

    def on_execute(self):
        url_arcadia = self.Parameters.arcadia_url
        revision = sdk2.svn.Arcadia.get_revision(url_arcadia)
        branch = utils.get_short_branch_name(url_arcadia)
        branch = branch or "UNKNOWN_BRANCH"

        self.url_arcadia = url_arcadia
        self.revision = revision
        self.branch = branch

        path_packet = str(self.path(self.PATH_PACKET))
        path_checkout = os.path.join(path_packet, "sema")

        os.mkdir(path_packet)

        self._export_arcadia(self.URL_SEMA_SVN, path_checkout)

        self._make_resource(path_packet)
