#!/usr/bin/python3.7

import argparse
import json
import os
import pathlib

ROOT_PATH = pathlib.Path(__file__).parent.parent
SECDIST_JSON_PATH = pathlib.Path('testsuite') / 'configs' / 'secdist.json'
BUILD_DIR_HELP = 'build directory. If absent, try tier0 build dir'


def parse_args():
    parser = argparse.ArgumentParser(
        description='Connects to testsuite postgresql',
    )
    parser.add_argument('--service', help='service name', required=True)
    parser.add_argument('--build-dir', help=BUILD_DIR_HELP, type=pathlib.Path)
    parser.add_argument(
        '--cluster', help='cluster name (will be guessed if not set)',
    )
    return parser.parse_args()


def read_testsuite_secdist(service: str, build_dir: pathlib.Path) -> dict:
    test_dir = 'tests_' + service.replace('-', '_')
    service_py3test_path = (
        pathlib.Path('services')
        / service
        / 'testsuite'
        / test_dir
        / 'test-results'
        / 'py3test'
    )
    if build_dir:
        path = build_dir / 'services' / service / SECDIST_JSON_PATH
    else:
        print(f'No build_dir arg. Try to find from test.context')
        context_file_path = ROOT_PATH / service_py3test_path / 'test.context'
        if not context_file_path.exists():
            raise Exception(f'Failed to locate {context_file_path} file')
        context_file_data = json.loads(context_file_path.read_text())
        build_root = pathlib.Path(context_file_data['runtime']['build_root'])
        path = (
            build_root
            / 'taxi'
            / 'uservices'
            / service_py3test_path
            / SECDIST_JSON_PATH
        )

    if not os.path.exists(path):
        raise Exception(f'Failed to locate testsuite secdist file: "{path}"')

    print(f'Reading secdist file "{path}"...')
    with open(path) as inp:
        return json.load(inp)


def guess_pg_clustername(secdist: dict) -> str:
    dbs = secdist.get('postgresql_settings', {}).get('databases', {})
    if not dbs:
        raise Exception('No postgresql clusters found in secdist')

    if len(dbs) != 1:
        raise Exception(
            'Multiple postgresql clusters found in secdist, '
            'I don\'t know which one to use',
        )

    return list(dbs.keys())[0]


def read_psql_connstring(secdist: dict, clustername: str) -> str:
    cluster = secdist['postgresql_settings']['databases'][clustername]
    assert len(cluster) == 1
    hosts = cluster[0]['hosts']

    for host in hosts:
        if 'read_only' not in host:
            return host

    raise Exception('Failed to find non-readonly connstring in secdist')


def execve_psql(connstr: str) -> None:
    os.execvp('psql', ['psql', connstr])


def main() -> None:
    args = parse_args()

    secdist = read_testsuite_secdist(args.service, args.build_dir)
    if args.cluster:
        clustername = args.cluster
    else:
        clustername = guess_pg_clustername(secdist)
    connstr = read_psql_connstring(secdist, clustername)

    execve_psql(connstr)


if __name__ == '__main__':
    main()
