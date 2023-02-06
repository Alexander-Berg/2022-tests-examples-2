import tarfile
import logging
import subprocess

from sandbox import sdk2
import sandbox.common.types.misc as ctm
import sandbox.common.types.client as ctc
from sandbox.projects import resource_types


class TestExperimentsAdminkaUnitTests(sdk2.Task):
    """
        Run experiments adminka unit tests using earlier built resource
    """

    class Requirements(sdk2.Requirements):
        dns = ctm.DnsType.DNS64
        client_tags = ctc.Tag.LINUX_PRECISE

    class Parameters(sdk2.Task.Parameters):
        AdminkaBuildParameter = sdk2.parameters.Resource(
            'Expadm build resource',
            resource_type=resource_types.EXPERIMENTS_ADMINKA,
            required=True,
        )

    def on_execute(self):
        """ Unpack built resource and run unit tests """
        path_build_tgz = sdk2.ResourceData(self.Parameters.AdminkaBuildParameter).path.as_posix()
        logging.info("Input tgz path: %s", path_build_tgz)

        with tarfile.open(path_build_tgz, mode="r:gz") as f:
            f.extractall(path=".")

        cmd = 'env/bin/python ./adminka/manage.py test --settings adminka.settings_krodo adminka.tests'
        logging.info("Running tests: %s", cmd)

        try:
            test_output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            logging.error(str(e))
            logging.error("Called process error output %s", e.output)
            raise

        logging.info(test_output)
