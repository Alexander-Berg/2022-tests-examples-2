#!/usr/bin/env python3
import argparse
import pathlib
import shutil
from typing import List
from typing import Optional


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    new_schema_dir = (
        pathlib.Path(args.schemas_path) / 'schemas' / 'services' / args.service
    )
    from_path = pathlib.Path('services') / args.service / 'docs' / 'yaml'
    shutil.copytree(from_path, new_schema_dir)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('service')
    parser.add_argument('schemas_path')
    return parser.parse_args(argv)


if __name__ == '__main__':
    main()
