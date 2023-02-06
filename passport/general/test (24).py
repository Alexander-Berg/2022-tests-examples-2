import subprocess
import sys
import yatest.common as yc


def test_run():
    test_cxx_ok_file = yc.source_path() + '/passport/infra/libs/cpp/utils/ut_py/test_ok.cpp'
    test_cxx_bad_file = yc.source_path() + '/passport/infra/libs/cpp/utils/ut_py/test_bad.cpp'

    p = subprocess.Popen(
        [
            yc.cxx_compiler_path(),
            '-std=c++17',
            '-Werror',
            test_cxx_ok_file,
            '-c',
        ],
        stdout=sys.stderr,
        stderr=sys.stderr,
    )
    assert p.wait() == 0

    p = subprocess.Popen(
        [
            yc.cxx_compiler_path(),
            '-std=c++17',
            '-Werror',
            test_cxx_bad_file,
            '-c',
        ],
        stdout=sys.stderr,
        stderr=open('./stderr', 'w'),
    )
    assert p.wait() != 0

    assert open('./stderr', 'r').read().count('switch (e) {') > 0
