#!/usr/bin/env python3

import argparse
import json
import pathlib
from typing import List
from typing import Optional

import jinja2


CUR_DIR = pathlib.Path(__file__).parent
ROOT_DIR = CUR_DIR.parent.parent
LOCALIZATIONS_SCHEMAS_PATH = ROOT_DIR / 'schemas' / 'mongo'
TEMPLATE_DIR = CUR_DIR / 'templates'
MONGO_DB_CONFIG_PATH = (
    ROOT_DIR / 'volumes' / 'bootstrap_db' / 'db_data' / 'db_config.json'
)

LOZALIZATIONS_SCHEMAS_ENTRY_TEMPLATE = (
    TEMPLATE_DIR / 'localizations-schemas-entry.jinja'
)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('keyset', help='Keyset name')
    parser.add_argument('keyset_id', help='Tanker keyset id')
    parser.add_argument('project_id', help='Tanker project id')
    return parser.parse_args(argv)


def add_keyset(args: argparse.Namespace) -> None:
    add_keyset_to_schemas(args)
    add_keyset_to_db_config(args)


def add_keyset_to_schemas(args: argparse.Namespace) -> None:
    keyset = args.keyset
    entry = form_schemas_entry(
        LOZALIZATIONS_SCHEMAS_ENTRY_TEMPLATE, 'grocery', keyset,
    )

    schemas_file_name = f'localization_{keyset}'
    schemas_entry_path = LOCALIZATIONS_SCHEMAS_PATH / (
        schemas_file_name + '.yaml'
    )
    schemas_entry_path.write_text(entry)


def add_keyset_to_db_config(args: argparse.Namespace) -> None:
    keyset = args.keyset

    mongo_collection_name = f'localization.grocery.{keyset}'
    tanker_keyset_id = args.keyset_id
    tanker_project_id = args.project_id
    entry = {
        'mongo_collection_name': mongo_collection_name,
        'tanker_keyset_id': tanker_keyset_id,
        'tanker_project_id': tanker_project_id,
    }

    db_config_text = MONGO_DB_CONFIG_PATH.read_text()
    db_config_json = json.loads(db_config_text)
    for config_entry in db_config_json:
        if config_entry['_id'] == 'LOCALIZATIONS_KEYSETS':
            config_entry['v']['keysets'][keyset] = entry

    db_config_text = json.dumps(db_config_json)
    MONGO_DB_CONFIG_PATH.write_text(db_config_text)


def form_schemas_entry(
        template_path: pathlib.Path, scope: str, keyset: str,
) -> str:
    template = jinja2.Template(template_path.read_text())

    schemas_entry = template.render(scope=scope, keyset=keyset)
    return schemas_entry


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    add_keyset(args)


if __name__ == '__main__':
    main()
