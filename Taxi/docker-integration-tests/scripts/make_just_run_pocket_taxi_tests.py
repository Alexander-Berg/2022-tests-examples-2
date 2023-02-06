#!/usr/bin/env python3

import os.path
import sys

import make_utils

TESTS_DIR = os.path.join('pocket-taxi-tests', 'tests')


def main() -> None:
    proc = make_utils.run_process(
        proc_args=[sys.executable, '-m', 'pytest', '-vv', TESTS_DIR],
    )

    if proc.returncode:
        make_utils.run_process(proc_args=['docker', 'ps', '-a'])

        bad_docker_info = make_utils.get_bad_docker_info()
        if bad_docker_info:
            make_utils.report_error(
                'Tests run failed. Containers in bad state. '
                + str(bad_docker_info),
            )
        exit(proc.returncode)


if __name__ == '__main__':
    main()
