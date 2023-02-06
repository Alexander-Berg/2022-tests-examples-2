import os

import yatest.common


def test_sudo():
    file = os.path.join(os.path.join(yatest.common.source_path(), "noc/packages/monitor-sudoers/sudoers"))
    yatest.common.execute(["visudo", "-f", file, "-c"], check_exit_code=True)
