import os
import logging
import shutil
import tarfile
from sandbox import sdk2
from sandbox.projects.common import error_handlers as eh
from sandbox.projects.common.search.components import component as components_common
from sandbox.projects.yabs.qa.sut.utils import reserve_port


LOGGER = logging.getLogger(__name__)


WAIT_TIMEOUT_DEFAULT = 2400


class YabsHitModels(
        components_common.ProcessComponentMixinWithShutdownSDK2,
        components_common.WaitPortComponentMixin,
        components_common.Component,
):
    """
    Interface for yabs hit model service.

    https://a.yandex-team.ru/arc/trunk/arcadia/search/daemons/begemot/yabs_hit_models
    """

    name = "yabs-hit-models"

    def __init__(self, task, binary_path, layer_path, archive_path, wait_timeout=WAIT_TIMEOUT_DEFAULT, work_dir=os.curdir):
        self.task = task
        self._port, self._socket = reserve_port()
        self._grpc_port, self._grpc_socket = reserve_port()
        self._binary_path = binary_path

        self._archive_path = os.path.abspath(archive_path)
        self._unpacked_archive_path = os.path.abspath(os.path.join(work_dir, "realtime_data"))
        self.extract_archive(self._archive_path, self._unpacked_archive_path)

        self._layer_path = os.path.abspath(layer_path)
        self._unpacked_layer_path = os.path.abspath(os.path.join(work_dir, "configs"))
        self.extract_archive(self._layer_path, self._unpacked_layer_path)

        self._service_config_path = os.path.join(self._unpacked_layer_path, "workloads/yabs_hit_models")

        # TODO(@aleosi) change resource archive to common
        src = os.path.join(self._service_config_path, "data/TsarModels/config.heavy.nanny.common.cfgproto.txt")
        dst = os.path.join(self._service_config_path, "data/TsarModels/config.cfgproto.txt")
        os.symlink(src, dst)

        components_common.WaitPortComponentMixin.__init__(self, endpoints=[("localhost", self._port)], wait_timeout=wait_timeout)
        components_common.ProcessComponentMixinWithShutdownSDK2.__init__(
            self,
            args=map(str, (
                self._binary_path,
                "--data", os.path.join(self._service_config_path, "data"),
                "--config", os.path.join(self._service_config_path, "conf/begemot.heavy.nanny.common.cfg"),
                "--realtime", self._unpacked_archive_path,
                "-p", self._port,
                "-g", self._grpc_port
                )),
            shutdown_url="http://localhost:{}/admin?action=shutdown".format(self._port),
            log_prefix=self.name,
        )
        LOGGER.info("Component '%s' initialized successfully with port '%s'", self.name, self._port)

    def __enter__(self):
        self.process_log = sdk2.helpers.ProcessLog(self.task, logger=self._log_prefix)
        super(YabsHitModels, self).__enter__()

    def flush_state(self):
        shutil.rmtree(self._unpacked_data_path)

    def get_port(self):
        return self._port

    def verify_stderr(self, custom_stderr_path=None):
        """Check stderr output stored in file for errors/warnings existence."""
        stderr_path = custom_stderr_path or self.process.stderr_path
        if not os.path.exists(stderr_path):
            return

        LOGGER.info("Verifying stderr path %s ...", stderr_path)
        with open(stderr_path) as stderr:
            for line in stderr:
                if "[ERROR]" in line:
                    eh.check_failed("Unexpected stderr log line: '{}'".format(line))

    def extract_archive(self, archive_path, extract_path):
        if os.path.isdir(extract_path):
            logging.debug("Reuse existing models_archive data %s", extract_path)
        else:
            logging.debug("Extract %s to %s", archive_path, extract_path)
            with tarfile.open(archive_path) as tar:
                tar.extractall(path=extract_path)
