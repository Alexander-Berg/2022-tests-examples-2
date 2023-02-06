import json

from yatest import common as yc

from sandbox.projects.common.metrics_launch_manager import mlm_analysis as mlma


def _read_file(file_name):
    with open(file_name) as f:
        return f.read()


def test_mlm_analysis():
    mlm_file_name = yc.test_source_path("data/mlm_launch_info.json")
    mlm_launch_info = json.loads(_read_file(mlm_file_name))
    assert mlm_launch_info

    first_failed_launch_id = mlma.get_first_failed_launch_id(mlm_launch_info)
    assert first_failed_launch_id == "aa8286388004a96401801e10a13b2908"

    launch_fails = mlma.get_launch_fails(mlm_launch_info)
    assert len(launch_fails) == 1

    final_status = mlma.get_final_status(mlm_launch_info)

    # case 1: empty ignore list
    metrics_ignore_list = {}
    adjusted_final_status = mlma.calculate_adjusted_final_status(
        final_status, launch_fails, metrics_ignore_list,
        current_date="2022-02-24",
    )
    # case 1: status should remain unchanged
    assert adjusted_final_status == final_status

    # case 2: wildcarded with failed deadline
    metrics_ignore_list = {
        ('BAOBAB_PATHS', 'coverage-main-FEA-realty_gallery'): "2022-02-23",
    }
    adjusted_final_status = mlma.calculate_adjusted_final_status(
        final_status, launch_fails, metrics_ignore_list,
        current_date="2022-02-24",
    )
    # case 2: status should remain unchanged as deadline failed
    assert adjusted_final_status == final_status

    # case 3: wildcarded within deadline
    metrics_ignore_list = {
        ('BAOBAB_PATHS', 'coverage-main-FEA-realty_gallery'): "2022-02-25",
        ('BAOBAB_PATHS', 'coverage-main-WIZ-maps-country'): "2022-02-25",
    }
    mlma.verify_ignore_list(metrics_ignore_list)
    adjusted_final_status = mlma.calculate_adjusted_final_status(
        final_status, launch_fails, metrics_ignore_list,
        current_date="2022-02-24",
    )
    # case 3: status should turn to "WARN" from "CRITICAL"
    assert adjusted_final_status == mlma.LaunchFinalStatus.WARN

    # case 4: ignore list misses some critical metrics
    metrics_ignore_list = {
        ('BAOBAB_PATHS', 'coverage-main-FEA-realty_gallery'): "2022-02-25",
    }
    mlma.verify_ignore_list(metrics_ignore_list)
    adjusted_final_status = mlma.calculate_adjusted_final_status(
        final_status, launch_fails, metrics_ignore_list,
        current_date="2022-02-24",
    )
    # case 4: status should remain "CRITICAL"
    assert adjusted_final_status == mlma.LaunchFinalStatus.CRITICAL

    # case 5: exact test names within deadline
    test_name = 'blender-priemka-basket-validate-20220404 [(All)]'
    metrics_ignore_list = {
        ('BAOBAB_PATHS', test_name, 'coverage-main-FEA-realty_gallery'): "2022-02-25",
        ('BAOBAB_PATHS', test_name, 'coverage-main-WIZ-maps-country'): "2022-02-25",
    }
    mlma.verify_ignore_list(metrics_ignore_list)
    adjusted_final_status = mlma.calculate_adjusted_final_status(
        final_status, launch_fails, metrics_ignore_list,
        current_date="2022-02-24",
    )
    # case 5: status should turn to "WARN" from "CRITICAL"
    assert adjusted_final_status == mlma.LaunchFinalStatus.WARN
