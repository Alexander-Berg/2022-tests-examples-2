import robot.jupiter.test.common as jupiter_integration
import robot.jupiter.test.sample.common as sample_test
from robot.library.yuppie.modules.environment import Environment


def test_jupiter_sample():
    env = Environment(diff_test=True)
    cm_env = {
        "DeletionMode": "aggressive",
        "SpreadRTHub.DeleteExport": "",
        "HostdatAsync.DeleteExport": "",
    }
    with jupiter_integration.launch_local_jupiter(
        env,
        cm_env=cm_env,
        jupiter_instance="beta",
        test_data="integration.tar",
    ) as local_jupiter:
        return jupiter_integration.call_jupiter(
            env.hang_test, sample_test.process,
            local_jupiter, env)
