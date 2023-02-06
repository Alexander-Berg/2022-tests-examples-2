from robot.blrt.library.local_blrt import start_local_blrt
from robot.library.yuppie.modules.environment import Environment


def _build_cmcheck_local_blrt_config(cm_configuration):
    return {
        "yt": {
            "enable": False
        },
        "perl_env": {
            "enable": False
        },
        "setup_yt_env": {
            "enable": False
        },
        "cm": {
            "configuration": cm_configuration
        }
    }


def run_cmcheck(cm_configuration):
    Environment.setup_logging()
    with start_local_blrt(_build_cmcheck_local_blrt_config(cm_configuration), for_tests=True) as local_blrt:
        assert local_blrt.cm


def test_blrt_cmcheck():
    return run_cmcheck("blrt")


def test_blrt_prestable_cmcheck():
    return run_cmcheck("blrt_prestable")


def test_blrt_acceptance_cmcheck():
    return run_cmcheck("blrt_acceptance")


def test_blrt_multidc_cmcheck():
    return run_cmcheck("blrt_multidc")


def test_blrt_multidc_prestable_cmcheck():
    return run_cmcheck("blrt_multidc_prestable")


def test_blrt_offer_acceptance():
    return run_cmcheck("blrt_offer_acceptance")
