import os
import subprocess
import sys
import yatest.common as yc


BIN_PATH = yc.build_path() + '/passport/infra/daemons/blackbox/tools/reporter/access_log/bin/blackbox_access_log_parser'
DATA_PATH = yc.source_path() + '/passport/infra/daemons/blackbox/tools/reporter/access_log/ut_py/in_data/'
TMP_DIR = './tmp_dir/'
ENV = os.environ.copy()


def test_parser():
    if os.path.isdir(TMP_DIR):
        os.removedirs(TMP_DIR)
    os.mkdir(TMP_DIR)

    p = subprocess.Popen(
        [
            # fmt: off
            BIN_PATH,
            '--storage', DATA_PATH,
            '--outdir', TMP_DIR,
            '--date', '20190101',
            # fmt: on
        ],
        env=ENV,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )
    assert p.wait() == 0

    return [
        yc.canonical_file(TMP_DIR + f, local=True)
        for f in [
            'raw.mimino',
            'raw.prod',
            'raw.yateam',
            'result.mimino.txt',
            'result.prod.txt',
            'result.yateam.txt',
        ]
    ]
