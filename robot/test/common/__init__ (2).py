import re
from os.path import join as pj

from robot.jupiter.library.python.local_jupiter import LocalJupiter
from robot.jupiter.library.python.jupiter_util.bundle import JupiterBundles
from robot.library.python.common_test import merge_kwargs, run_safe, yatest_binary_path


def yandex_meta_graph_re():
    return re.compile(r"^yandex\.")


def call_jupiter_impl(process, lj, *args, **kwargs):
    cm = lj.get_cm()
    cm.set_var("SkipDeploy", "true")
    test_result = process(lj, *args, **kwargs)
    bad_targets = list(cm.find_targets_in_states([cm.State.FAILED]))
    if len(bad_targets) > 0:
        info = cm.generate_report()
        raise RuntimeError("Some targets failed. See report in Report file " + info)
    return test_result


def call_jupiter(need_hang, process, lj, *args, **kwargs):
    try:
        run_safe(need_hang, call_jupiter_impl, process, lj, *args, **kwargs)
    except BaseException:
        lj.get_cm().dump_failed_targets()
        raise


def launch_local_jupiter(env, **kwargs):
    return run_safe(
        env.hang_test, LocalJupiter,
        **merge_kwargs(
            kwargs,
            arcadia=env.arcadia,
            bin_dir=env.binary_path,
            cm_bin_dir=env.get_cm_bin_dir(),
            cluster=env.cluster,
            prefix=env.mr_prefix,
            working_dir=env.output_path,
            jupiter_bundle_dirs={name: yatest_binary_path(pj("robot", "jupiter", "packages", name)) for name in JupiterBundles()},
            jupiter_cmpy_dir=yatest_binary_path("robot/jupiter/packages/cmpy"),
            printers_dir=yatest_binary_path("robot/jupiter/packages/printers"),
            shard_deploy_bundle_dir=yatest_binary_path("robot/jupiter/packages/shard_deploy_bundle"),
            ram_drive_path=env.ram_drive_path,  # This is very-very-very IMPORTANT!!!!1!1!
        )
    )
