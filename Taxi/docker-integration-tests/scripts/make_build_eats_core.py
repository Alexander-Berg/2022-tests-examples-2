#!/usr/bin/env python3

import argparse
import re
import sys
import typing

import packaging.version

import make_utils


DOCKER_VERSION_PATTERN = 'Docker version (.+), build .+'
REQUIRED_DOCKER_VERSION = '18.09'


def parse_args(
        argv: typing.Optional[typing.List[str]] = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--core-path', required=True)
    parser.add_argument('--tag', required=True)
    return parser.parse_args(argv)


def build_core_image(
        core_path: str, tag: str, version: str = 'test',
) -> typing.Tuple[int, str]:
    proc = make_utils.run_docker(
        proc_args=[
            'build',
            '--build-arg',
            'APP_ENV=production',
            '--build-arg',
            f'APP_ROOT={core_path}',
            '--build-arg',
            f'VERSION={version}',
            '--pull',
            '--no-cache',
            '-t',
            f'registry.yandex.net/eda/core/production:{tag}',
            '-f',
            f'{core_path}/Dockerfile',
            '--ssh=default',
            f'{core_path}',
        ],
        env={'DOCKER_BUILDKIT': '1'},
        pipe_stdout=True,
    )

    return proc.returncode, proc.stdout


def get_core_head_commit() -> str:
    proc = make_utils.run_process(
        proc_args=['git', 'rev-parse', 'HEAD'],
        pipe_stdout=True,
        cwd='./eats-core',
    )

    if proc.returncode:
        exit(-1)
    return proc.stdout.rstrip()


def is_proper_docker_engine_version() -> bool:
    version = packaging.version.Version

    proc = make_utils.run_docker(
        proc_args=['--version'], pipe_stdout=True,
    )
    if proc.returncode:
        return False
    _match = re.match(DOCKER_VERSION_PATTERN, proc.stdout)
    if not _match:
        print('ERROR: Output of `docker --version` does not contain '
              'version in proper format.\n'
              f'output: `{proc.stdout}`')
        return False
    docker_version: str = _match.group(1)

    if version(REQUIRED_DOCKER_VERSION) > version(docker_version):
        print(f'ERROR: Version of Docker engine ({docker_version}) '
              f'is less than {REQUIRED_DOCKER_VERSION}.xx.\n'
              'eats-core cannot be built using this version.\n'
              f'Please use {REQUIRED_DOCKER_VERSION}+ '
              f'version of Docker engine.')
        return False
    return True


def main(argv: typing.Optional[typing.List[str]] = None) -> None:
    args = parse_args(argv)

    if not is_proper_docker_engine_version():
        exit(-1)

    head_commit_hash = get_core_head_commit()
    return_code, stdout = build_core_image(
        core_path=args.core_path, tag=args.tag, version=head_commit_hash,
    )
    if return_code:
        print('Error building image.\n' + stdout, file=sys.stderr)
        exit(-1)


if __name__ == '__main__':
    main()
