import tarfile
import os
import re
import logging

from sandbox.projects.common import utils

import sandbox.common.types.misc as ctm

from sandbox import sdk2
from sandbox.sdk2.vcs.svn import Arcadia as Arcadia


class RazladkiWowResource(sdk2.Resource):
    """ Razladki wow resource """


class RazladkiWowVirtualEnv(sdk2.Resource):
    """ Razladki-wow virtual env """


class BuildRazladkiWow(sdk2.Task):
    """
        Build Razladki wow.
        Checkouts razladki wow from SVN and packs it with ready virtualenv package.
    """

    URL_RAZLADKI_WOW_SVN = 'razladki/razladki_wow'

    PATH_PACKET = 'razladki_wow'
    PATH_TGZ = 'razladki_wow.tar.gz'

    class Requirements(sdk2.Requirements):
        dns = ctm.DnsType.DNS64

    class Parameters(sdk2.Task.Parameters):
        ArcadiaUrlParameter = sdk2.parameters.ArcadiaUrl('Arcadia url', default_value='arcadia:/arc/trunk/arcadia')

        VirtualEnvPackageParameter = sdk2.parameters.LastReleasedResource(
            'Virtualenv like package ready for razladki wow',
            resource_type=RazladkiWowVirtualEnv,
            required=True
        )

    def arcadia_info(self):
        return self.Context.revision, "Razladki_wow venv {} r{}".format(self.Context.branch, self.Context.revision), self.Context.branch

    def on_execute(self):
        url_arcadia = self.Parameters.ArcadiaUrlParameter

        revision = Arcadia.get_revision(url_arcadia)
        branch = utils.get_short_branch_name(url_arcadia)
        if not branch:
            try:
                branch_match = re.search(r'(branch.+)$', url_arcadia).group(0)
                branch = branch_match
            except IndexError:
                pass

        logging.info('ARCADIA {} {}'.format(branch, revision))
        assert revision, 'Trying to fetch project from SVN, but no revision specified'

        self.Context.revision = revision
        self.Context.branch = branch

        path_packet = self.path(self.PATH_PACKET).as_posix()
        path_virtualenv = os.path.join(path_packet, 'env')
        path_checkout = path_packet

        os.mkdir(path_packet)
        self._export_arcadia(self.URL_RAZLADKI_WOW_SVN, path_checkout)

        self._create_virtualenv(path_packet)
        self._validate_virtualenv(path_virtualenv, path_checkout)

        python_path = os.path.join(path_packet, 'env', 'bin', 'python')
        if not os.path.exists(python_path):
            raise ValueError('Seems no "python" in %s after installing dependencies package' % python_path)

        logging.info('creating tgz file')
        with tarfile.open(self.path(self.PATH_TGZ).as_posix(), 'w:gz') as tar:
            for entry in os.listdir(path_packet):
                tar.add(os.path.join(path_packet, entry), entry)

        logging.info('creating resource')
        sdk2.ResourceData(
            RazladkiWowResource(
                self,
                'razladki wow resource r{0}'.format(self.Context.revision),
                self.path(self.PATH_TGZ).as_posix(),
                arch='linux'
            )
        )

    def _create_virtualenv(self, path_packet):
        logging.info('extracting virtualenv')

        virtualenv_package = sdk2.ResourceData(self.Parameters.VirtualEnvPackageParameter).path.as_posix()
        logging.info('Extracting virtualenv package %s to %s' % (virtualenv_package, path_packet))
        tarfile.open(virtualenv_package).extractall(path_packet)

    def _validate_virtualenv(self, path_virtualenv, path_checkout):
        logging.info('validating virtualenv')

        with open(os.path.join(path_virtualenv, "pip-requirements.txt"), "r") as f:
            reqs_virtualenv = f.read()
        with open(os.path.join(path_checkout, "pip-requirements.txt"), "r") as f:
            reqs_checkout = f.read()

        if not reqs_virtualenv == reqs_checkout:
            logging.error("OUTDATED virtualenv")
            raise Exception("Virtualenv is outdated, please build new using BUILD_EXPERIMENTS_ADMINKA_ENV task")

    def _get_arcadia_url(self, arcadia_path):
        url_arcadia = self.Parameters.ArcadiaUrlParameter

        url_parsed = Arcadia.parse_url(url_arcadia)
        path_new = re.sub(r'/arcadia.*', '/arcadia/' + arcadia_path, url_parsed.path, count=1)

        return Arcadia.replace(url_arcadia, path=path_new)

    def _export_arcadia(self, arcadia_path, path):
        url = self._get_arcadia_url(arcadia_path)
        logging.info("EXPORT '{}' TO '{}'".format(url, path))

        Arcadia.export(url, path)
