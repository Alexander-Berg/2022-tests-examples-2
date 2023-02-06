#!/usr/bin/env python3

import os
from typing import Dict
from typing import List
from typing import Optional

import make_utils


IS_TEAMCITY = 'IS_TEAMCITY'

ARCADIA_ROOT = '../..'
DEFAULT_ENV = {
    'BUILD_DIR': '/arcadia/taxi/uservices/build-integration',
    'HOST_BUILD_VOLUME': f'{ARCADIA_ROOT}/../../../../build-integration/',
    'DOCKER_BUILD_VOLUME': '/arcadia/taxi/uservices/build-integration/',
}


def _get_env() -> Dict[str, str]:
    env = dict(os.environ)
    if os.getenv(IS_TEAMCITY):
        return env

    for key, value in DEFAULT_ENV.items():
        env[key] = value
    print('CMAKE_OPTS =', env['CMAKE_OPTS'])
    return env


def build_grocery_services() -> None:
    if os.path.exists('./uservices/Makefile'):
        proc = make_utils.run_process(
            proc_args=[
                'docker-compose',
                '-f',
                f'{ARCADIA_ROOT}/taxi/uservices/docker-compose.yml',
                'run',
                '--rm',
                'taxi-uservices-bionic',
                'make',
                'build',
            ],
            env=_get_env(),
        )
        if proc.returncode:
            make_utils.report_error('Build error')
            exit(proc.returncode)


def main(argv: Optional[List[str]] = None) -> None:
    build_grocery_services()


if __name__ == '__main__':
    main()
