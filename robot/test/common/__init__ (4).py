from robot.library.python.common_test import merge_kwargs, run_safe, yatest_binary_path

from robot.pluto.library.yuppie import LocalPluto


def launch_local_pluto(env, **kwargs):
    return run_safe(
        env.hang_test, LocalPluto,
        **merge_kwargs(
            kwargs,
            arcadia=env.arcadia,
            working_dir=env.output_path,
            ya_binaries_dir=yatest_binary_path("robot/pluto/packages/binaries"),
            ya_cm_bin_dir=env.binary_path,
            ya_data_dir=yatest_binary_path("robot/pluto/packages/data"),
            ya_dssm_dir=yatest_binary_path("robot/pluto/packages/dssm_model/dssm3")
        )
    )
