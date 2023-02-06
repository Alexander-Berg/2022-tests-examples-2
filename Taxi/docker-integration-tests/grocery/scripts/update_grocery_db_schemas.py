import argparse
import pathlib
import shutil
from typing import List
from typing import Optional


CUR_DIR = pathlib.Path(__file__).parent
ROOT_DIR = CUR_DIR.parent.parent

POSTGRES_MIGRATIONS_PATH = (
    ROOT_DIR / 'volumes' / 'bootstrap_db' / 'postgres' / 'schemas'
)
POSTGRES_MIGRATIONS_PATH_IN_SCHEMAS = pathlib.Path('schemas') / 'postgresql'

SERVICES_TO_UPDATE = [
    'overlord-catalog',
    'tristero-parcels',
    'grocery-marketing',
    'grocery-orders',
    'grocery-takeout',
    'grocery-depots',
    'grocery-products',
    'grocery-payments',
    'grocery-cashback',
    'grocery-discounts',
    'grocery-cart',
]

CURIOUS_DB_NAME = {'grocery-surge': 'grocery-surge'}


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('schemas_path', help='path to schemas repository')

    return parser.parse_args(argv)


def get_db_name(service_name: str):
    if service_name in CURIOUS_DB_NAME:
        return CURIOUS_DB_NAME[service_name]

    return service_name.replace('-', '_')


def copy_service_pg_schemas(
        copy_from_dir: pathlib.Path, copy_to_dir: pathlib.Path,
) -> None:
    copy_to_dir.mkdir(parents=True, exist_ok=True)

    migrations = [x for x in copy_from_dir.glob('*.sql') if x.is_file()]

    for sql in migrations:
        copy_to = copy_to_dir / sql.name
        shutil.copy(sql, copy_to)


def copy_services_pg_schemas(schemas_root_path: str) -> None:
    copy_from_dir = schemas_root_path / POSTGRES_MIGRATIONS_PATH_IN_SCHEMAS

    for service in SERVICES_TO_UPDATE:
        db_name = get_db_name(service)
        copy_service_pg_schemas(
            copy_from_dir / db_name / db_name,
            POSTGRES_MIGRATIONS_PATH / db_name,
        )


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    copy_services_pg_schemas(args.schemas_path)


if __name__ == '__main__':
    main()
