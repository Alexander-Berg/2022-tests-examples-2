from robot.cmpy.library.cmapi import CmApi
from robot.cmpy.library.target import cm_target, start, finish  # noqa
from robot.cmpy.library.utils import read_token_from_file
from robot.library.python.sandbox.client import SandboxClient


class CallistoParams:
    arcadia_path = "svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/robot/jupiter/test/common"
    file_name = "callisto_integration_yt_data.make"
    instance = "Callisto"
    sample_type = "callisto_integration"


class JupiterParams:
    arcadia_path = "svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/robot/jupiter/test/common"
    file_name = "integration_yt_data.make"
    instance = "Jupiter"
    sample_type = "integration"


def create_new_test_data_impl(config, params):
    sandbox = SandboxClient(token=read_token_from_file(config.SandboxTokenPath))
    task_id = sandbox.run_task(
        name="JUPITER_CREATE_INTEGRATION_DATA",
        params={
            "mr_prefix": config.MrPrefix,
            "mr_server": config.MrServer,
            "sample_type": params.sample_type,
        },
        description="Create test data for {}'s integration test".format(params.instance),
        wait_success=True,
        disk_space=20 * 2 ** 30,  # disk space in bytes
        owner="JUPITER",
    )

    CmApi().setvar("Sample.NewTestDataSandboxTaskId", task_id)


def commit_resource_id_impl(config, params):
    sandbox = SandboxClient(token=read_token_from_file(config.SandboxTokenPath))
    creation_task_id = config.Sample.NewTestDataSandboxTaskId
    resource_info = sandbox.find_resource("JUPITER_INTEGRATION_DATA", task_id=creation_task_id)

    sandbox.run_task(
        name="JUPITER_COMMIT_INTEGRATION_DATA",
        params={
            "resource_id": resource_info["id"],
            "sample_type": params.sample_type,
            "yt_data_make_file_location": params.arcadia_path,
            "yt_data_make_file_name": params.file_name,
        },
        description="Commit to Arcadia resource id for {}'s integration test".format(params.instance),
        wait_success=True,
        disk_space=2 ** 30,  # disk space in bytes
        owner="JUPITER",
    )

    CmApi().unsetvar("Sample.NewTestDataSandboxTaskId")


def dispatch_by_instance(config, function):
    if config.Configuration.is_callisto():
        function(config, CallistoParams)
    else:
        function(config, JupiterParams)


@cm_target
def create_new_test_data(config):
    dispatch_by_instance(config, create_new_test_data_impl)


@cm_target
def commit_resource_id(config):
    dispatch_by_instance(config, commit_resource_id_impl)
