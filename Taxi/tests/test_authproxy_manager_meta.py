# pylint: disable=broad-except
import os
import sys
from typing import Iterator

import yatest.common  # pylint: disable=import-error


ROOT_DIR = os.path.join('taxi', 'uservices')
SERVICES_DIR = os.path.join(ROOT_DIR, 'services')
AM_COLLECTED_DIR = os.path.join(
    SERVICES_DIR,
    'authproxy-manager',
    'testsuite',
    'tests_authproxy_manager',
    'static',
    'test_collected_rules',
    'files',
)


def collect_authproxy_names() -> Iterator[str]:
    services_dir = yatest.common.source_path(SERVICES_DIR)
    for service in os.listdir(services_dir):
        try:
            deps_filepath = os.path.join(
                services_dir, service, 'local-files-dependencies.txt',
            )

            deps = read_file_contents(deps_filepath).split('\n')
            if 'libraries/base-proxy-rules' in deps:
                yield service
        except Exception:
            continue


def read_file_contents(filepath: str) -> str:
    try:
        with open(filepath) as ifile:
            return ifile.read()
    except Exception as exc:
        assert False, f'Failed to read file "{filepath}": {exc}'


def write_file(filepath: str, contents: str):
    realpath = os.path.realpath(filepath)
    print(f'Updating file {realpath}...', file=sys.stderr)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as ofile:
        ofile.write(contents)


def validate_files(service: str) -> None:
    files = collect_files(service)
    for filepath in files:
        am_filepath = yatest.common.source_path(
            os.path.join(AM_COLLECTED_DIR, filepath),
        )
        if os.path.exists(am_filepath):
            am_contents = read_file_contents(am_filepath)
        else:
            am_contents = ''

        service_filepath = yatest.common.source_path(
            os.path.join(ROOT_DIR, filepath),
        )
        if os.path.exists(service_filepath):
            service_contents = read_file_contents(service_filepath)
        else:
            service_contents = ''

        is_collected_rules = filepath.endswith('collected-rules.json')

        # If set, the test does copying instead of validation
        copy_mode = yatest.common.get_param('am_copy_mode')
        if copy_mode == 'collected-rules':
            if is_collected_rules:
                write_file(am_filepath, service_contents)
        elif copy_mode == 'meta-headers':
            if not is_collected_rules:
                write_file(service_filepath, am_contents)
        elif not copy_mode:
            assert am_contents == service_contents, (
                f'Files differ ({filepath}). '
                '\nRun the following command for update:'
                '\n  "cd services/authproxy-manager && make update-proxy-meta"'
            )
        else:
            assert False, f'Unknown value of "am_copy_mode": {copy_mode}'


CHECKED_FILENAMES = ['meta_headers_cache.json', 'collected-rules.json']


def collect_files(service: str):
    service_dir = yatest.common.source_path(
        os.path.join(SERVICES_DIR, service),
    )
    for root, _, files in os.walk(service_dir):
        for filename in files:
            if filename in CHECKED_FILENAMES:
                path = os.path.join(root, filename)
                path = os.path.relpath(path, service_dir)
                yield os.path.join('services', service, path)


def test_uptodate() -> None:
    services = collect_authproxy_names()
    print('')
    for service in services:
        validate_files(service)
