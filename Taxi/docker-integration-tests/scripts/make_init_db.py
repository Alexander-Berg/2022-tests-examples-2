#!/usr/bin/env python3

import re
import sys
import time

import make_utils


ERROR_REGEX = re.compile('.*Error: (.*)')


def main():
    start_time = time.time()
    proc = make_utils.run_process(
        proc_args=['docker-compose', 'run', '-T', '--rm', 'taxi-bootstrap'],
        pipe_stdout=True,
        stderr_to_stdout=True,
    )

    end_time = time.time()
    init_db_time = (end_time - start_time) * 1000
    key_stat_name = 'Init DB Time For Integration Tests'
    make_utils.report_statistic(key_stat_name, init_db_time)

    if proc.returncode:
        match = ERROR_REGEX.match(proc.stdout)
        if match:
            make_utils.report_error('Init db error: ' + match.group(1))
        else:
            print(proc.stdout, file=sys.stderr)
            make_utils.report_error('Init db error')
        exit(1)


if __name__ == '__main__':
    main()
