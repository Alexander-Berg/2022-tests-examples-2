import logging

import yatest.common
from robot.library.yuppie.modules.sys_mod import Sys


def run_safe(need_hang, function, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except BaseException as err:
        if need_hang:
            logging.info("Got error: %s", err)
            Sys.hang()
        else:
            raise


def merge_kwargs(original, **patch):
    # add new params and keep original values
    patch.update(original)
    return patch


def yatest_binary_path(path):
    try:
        return yatest.common.binary_path(path)
    except BaseException:
        return None
