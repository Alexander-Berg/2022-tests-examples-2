#!/usr/bin/env python

import os
import shutil
import yatest

from os.path import join as pj


def test_entry():

    env = os.environ.copy()
    env['PATH'] = env.get('PATH', '/bin:/usr/bin') + os.pathsep + yatest.common.binary_path(".")

    run_path = yatest.common.output_path("run")
    output_path = os.path.abspath(yatest.common.output_path(pj("run", "output")))
    os.makedirs(output_path)

    for script in ["run.sh", "build.mk", "run_iface.sh"]:
        shutil.copy(yatest.common.source_path("robot/jupiter/base_bundle/{}".format(script)), pj(run_path, script))

    for binary in ["robot/jupiter/tools/shardmerge_utils/shardmerge_utils", "robot/jupiter/tools/indexstats/indexstats"]:
        shutil.copy(yatest.common.binary_path(binary), pj(run_path, os.path.basename(binary)))

    open(pj(output_path, "indexcounts"), "w").close()

    with open(pj(output_path, "jupiter-doccount.txt"), "w") as doccount:
        doccount.write('100')

    shell_path = pj("run", "run.sh")
    yatest.common.execute(["bash", shell_path, "-g", "20160704-162149", "-o", output_path, "-t", "PlatinumTier0", "-s", "0-9", "-d", "true"],
                          env=env, cwd=yatest.common.output_path())

if __name__ == '__main__':
    test_entry()
