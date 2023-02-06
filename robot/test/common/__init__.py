from robot.jupiter.test.common import merge_kwargs, run_safe, yatest_binary_path

from robot.favicon.library.yuppie import LocalFavicon
import os

WORKING_SUBDIR_ARG_NAME = "working_subdir"


def launch_local_favicon(env, **kwargs):
    if WORKING_SUBDIR_ARG_NAME in kwargs:
        working_dir = os.path.join(env.output_path, kwargs.get(WORKING_SUBDIR_ARG_NAME))
        del kwargs[WORKING_SUBDIR_ARG_NAME]
    else:
        working_dir = env.output_path

    return run_safe(
        env.hang_test, LocalFavicon,
        **merge_kwargs(
            kwargs,
            working_dir=working_dir,
            bin_dir=yatest_binary_path("robot/favicon/packages/cm_binaries"),
        )
    )
