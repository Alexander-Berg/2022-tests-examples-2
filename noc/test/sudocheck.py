import os

import yatest.common


def test_sudo():
    # vpath = yatest.common.binary_path("visudo")
    file = os.path.join(os.path.join(yatest.common.source_path(), "noc/packages/mondata/sudoers"))
    yatest.common.execute(["visudo", "-f", file, "-c"], check_exit_code=True)
