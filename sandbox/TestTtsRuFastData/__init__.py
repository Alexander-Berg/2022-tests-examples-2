# coding: U8
import json
import logging
import tarfile
import tempfile
from sandbox import sdk2
from sandbox.common import errors
from sandbox.projects.common.nanny.client import NannyClient
import sandbox.common.types.task as ctt
from sandbox.projects.voicetech import resource_types


NANNY_API_URL = "http://nanny.yandex-team.ru/"


def find_resources(sandbox_files):
    ret = {}
    for item in sandbox_files:
        logging.info("Searching resource with the following meta:")
        logging.info(json.dumps(item, indent=2))
        if item["resource_type"] == "VOICETECH_TTS_RU_GPU":
            r = sdk2.Resource.find(id=item["resource_id"]).first()
            assert r is not None
            logging.info("Found ru_e2e lingware")
            ret["lingware"] = r
        elif item["resource_type"] == "VOICETECH_TTS_FASTDATA_SMOKE_TEST":
            r = sdk2.Resource.find(id=item["resource_id"]).first()
            assert r is not None
            logging.info("Found smoke test binary")
            ret["smoke_test_binary"] = r
        elif item["resource_type"] == "VOICETECH_TTS_FASTDATA_SMOKE_TEST_CASES":
            r = sdk2.Resource.find(id=item["resource_id"]).first()
            assert r is not None
            logging.info("Found smoke test cases")
            ret["smoke_test_cases"] = r
    assert len(ret) == 3
    return ret


def path_from_resource(r):
    data = sdk2.ResourceData(r)
    return data.path


def untar(src, dst):
    src = str(src)
    dst = str(dst)
    with tarfile.open(src, mode="r:*") as tar:
        logging.info("Unpacking {} to {}".format(src, dst))
        tar.extractall(dst)


class TestTtsRuFastData(sdk2.Task):
    """
    """
    class Requirements(sdk2.Requirements):
        cores = 4
        disk_space = 10 * 1024 # 10 GB
        ram = 10 * 1024 # 10 GB

    class Parameters(sdk2.Task.Parameters):
        kill_timeout = 3600 + 1200

        fast_data_bundle = sdk2.parameters.Resource(
            "Fast Data bundle to test",
            resource_type=[
                resource_types.VOICETECH_TTS_RU_FASTDATA_BUNDLE,
            ],
            required=True,
        )
        validator_nanny_service = sdk2.parameters.String(
            "TTS Fast Data Validator Nanny service name",
            required=True,
            default="fastdata-validator"
        )
        with sdk2.parameters.Group("Vault"):
            nanny_token_name = sdk2.parameters.String("Nanny token name", required=True)

        with sdk2.parameters.Output:
            smoke_test_binary = sdk2.parameters.Resource(
                "TTS fast data smoke test binary",
                resource_type = [
                    resource_types.VOICETECH_TTS_FASTDATA_SMOKE_TEST
                ],
            )
            lingware = sdk2.parameters.Resource(
                "TTS lingware",
                resource_type = [
                    resource_types.VOICETECH_TTS_RU_GPU
                ],
            )
            smoke_test_cases = sdk2.parameters.Resource(
                "TTS fast data smoke test texts",
                resource_type=[
                    resource_types.VOICETECH_TTS_FASTDATA_SMOKE_TEST_CASES
                ],
            )

    def get_resources_from_prod_yappy(self):
        nanny_client = NannyClient(
            NANNY_API_URL,
            sdk2.Vault.data(self.Parameters.nanny_token_name)
        )
        service = self.Parameters.validator_nanny_service

        logging.info("Querying sandbox resources from {}".format(service))
        resources = nanny_client.get_service_resources(
            service_id=service
        )

        sandbox_files = resources["content"]["sandbox_files"]
        logging.info("Found {} sandbox files:".format(len(sandbox_files)))
        logging.info(json.dumps(sandbox_files, indent=2))

        logging.info("Searching input resources to run tests")
        resources = find_resources(sandbox_files)

        self.Parameters.smoke_test_binary = resources["smoke_test_binary"]
        self.Parameters.lingware =  resources["lingware"]
        self.Parameters.smoke_test_cases = resources["smoke_test_cases"]

    def run_smoke_test(self):
        logging.info("Downloading resources")
        smoke_test = path_from_resource(self.Parameters.smoke_test_binary)
        lingware = path_from_resource(self.Parameters.lingware)
        fast_data_bundle = path_from_resource(self.Parameters.fast_data_bundle)
        smoke_test_cases = path_from_resource(self.Parameters.smoke_test_cases)

        logging.info("Unpacking fast data bundle")
        fastdata_dir = tempfile.mkdtemp(dir=".")
        untar(fast_data_bundle, fastdata_dir)

        logging.info("Running test binary")
        with sdk2.helpers.ProcessLog(self, logger="shell") as pl:
            sdk2.helpers.subprocess.check_call([
                str(smoke_test),
                "--lingware", str(lingware),
                "--fast_data", str(sdk2.path.Path(fastdata_dir) / "ru_fastdata"),
                "--test_cases", str(smoke_test_cases)
                ], stdout=pl.stdout, stderr=pl.stderr)

    def on_execute(self):
        with self.memoize_stage.find_resources:
            self.get_resources_from_prod_yappy()

        with self.memoize_stage.run_smoke_test:
            logging.info("Starting test subtask")
            self.run_smoke_test()
