import logging

logger = logging.getLogger("test_logger")

from sandbox.projects.mobile_apps.teamcity_sandbox_runner.runner_stage import TeamcitySandboxRunnerStage


def test_parse_secret_file_parameter():
    # dummytask = Task(parent=None)
    # tsrStage = TeamcitySandboxRunnerStage()
    # tsrStage.work_dir = "/tmp"
    store_secret_path, secret_name, secret_key, secret_env = TeamcitySandboxRunnerStage._parse_secret_file_parameter(
        "sec-abc1:file_key", "newfile.txt:MY_SPECIAL_VAR")
    assert store_secret_path == '/tmp/newfile.txt'
    assert secret_name == 'sec-abc1'
    assert secret_key == 'file_key'
    assert secret_env == 'MY_SPECIAL_VAR'

    store_secret_path, secret_name, secret_key, secret_env = TeamcitySandboxRunnerStage._parse_secret_file_parameter(
        "sec-abc1:file_key", "newfile.txt")
    assert store_secret_path == '/tmp/newfile.txt'
    assert secret_name == 'sec-abc1'
    assert secret_key == 'file_key'
    assert secret_env == None
