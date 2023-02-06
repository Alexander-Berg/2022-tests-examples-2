#!/usr/bin/env python3

import os

import make_utils


def main():
    if os.path.exists('backend-cpp/Makefile'):
        proc = make_utils.run_process(
            proc_args=['docker-compose', 'run', '--rm', 'taxi-build-cxx'],
        )
        if proc.returncode:
            make_utils.report_error('Build error')
            exit(1)


if __name__ == '__main__':
    main()
