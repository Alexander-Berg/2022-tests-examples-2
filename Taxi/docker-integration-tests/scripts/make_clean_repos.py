#!/usr/bin/env python3

import os

import make_utils


def clean_repo(repo: str, image: str) -> None:
    if not os.path.exists(f'./{repo}/Makefile'):
        return
    print(f'Clear repo: {repo}')
    compose_path = []
    if repo != 'backend-cpp':
        compose_path = ['-f', f'../../taxi/{repo}/docker-compose.yml']

    proc = make_utils.run_process(
        proc_args=[
            'docker-compose',
            *compose_path,
            'run',
            '--rm',
            image,
            'make',
            'clean',
        ],
    )
    if proc.returncode:
        make_utils.report_error(
            f'unable to clean for project in {repo}',
        )
        exit(proc.returncode)


def main():
    clean_repo('backend-cpp', 'taxi-build-cxx')
    clean_repo('uservices', 'taxi-uservices-xenial')
    clean_repo('backend-py3', 'taxi-test-service')


if __name__ == '__main__':
    main()
