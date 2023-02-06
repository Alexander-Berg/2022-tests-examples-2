#!/usr/bin/env python3

import os

import make_utils

PY3_PATH = f'../../taxi/backend-py3'


def main():
    if os.path.exists(f'{PY3_PATH}/Makefile'):
        if not (
                os.environ.get('IS_TEAMCITY')
                or os.path.exists(f'{PY3_PATH}/generated')
        ):
            proc = make_utils.run_process(
                proc_args=[
                    'docker-compose',
                    '-f',
                    f'{PY3_PATH}/docker-compose.yml',
                    'run',
                    '--rm',
                    'taxi-test-service',
                    '/taxi/dockertest/gen-backend-py3.sh',
                    '--generate-debian',
                ],
            )
            if proc.returncode:
                make_utils.report_error(
                    'Backend Py3 code generation step failed.',
                )
                exit(1)


if __name__ == '__main__':
    main()
