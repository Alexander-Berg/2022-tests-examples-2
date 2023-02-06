#!/usr/bin/env python3

import argparse
import os
import pathlib
import re
import shutil
from typing import Generator
from typing import Tuple

import get_services

ROOT_DIR = pathlib.Path(os.path.realpath(__file__).split('scripts')[0])


def services_bypass(compose_file: str) -> Generator[str, None, None]:
    services = get_services.load_services(docker_compose_files=(compose_file,))
    for name in services:
        yield name


def find_sql_files(
        services: Generator[str, None, None],
        arcadia_dir: pathlib.Path,
) -> Generator[Tuple[str, pathlib.Path], None, None]:
    services_dir = arcadia_dir / 'taxi/uservices/services'
    for service in services:
        source_dir = services_dir.joinpath(service.replace('_', '-'))
        if source_dir.is_dir():
            for file in source_dir.glob('**/*.sql'):
                if file.is_file():
                    yield service, file


def find_migrations(
        service_file_pair: Generator[Tuple[str, pathlib.Path], None, None],
) -> Generator[Tuple[str, pathlib.Path], None, None]:
    for service, sql_file in service_file_pair:
        if not re.search(
                r'(src|grants|rollbacks)', str(sql_file.absolute()),
        ) and re.search('postgresql', str(sql_file.absolute())):
            yield service, sql_file


def copy_cycle(
        migrations: Generator[Tuple[str, pathlib.Path], None, None],
) -> Generator[Tuple[str, str], None, None]:
    for service, sql in migrations:
        target_dir = (
            pathlib.Path(ROOT_DIR)
            / 'volumes/bootstrap_db/postgres/schemas'
            / service.replace('-', '_')
        )
        yield shutil.copy(sql, target_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--arcadia',
        type=str,
        required=True,
        help='path to the arcadia folder',
    )
    parser.add_argument(
        '--docker-compose',
        type=str,
        default=f'{ROOT_DIR}/eats/docker-compose.yml',
        help='path to docker-compose.yml file',
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    arcadia_path = pathlib.Path(args.arcadia)
    dc_file = args.docker_compose

    if not os.listdir(arcadia_path):
        raise RuntimeError(f'Arcadia is not mounted')

    services = services_bypass(dc_file)
    files = find_sql_files(services, arcadia_path)
    migrations = find_migrations(files)
    nums = len([dst for dst in copy_cycle(migrations)])
    print(f'{nums} files have been copied')


if __name__ == '__main__':
    main()
