# coding: utf8
import argparse
import logging
import os
import sys
from typing import Dict

import yaml

import copy_config

logger = logging.getLogger(__name__)


def setup_logging(file_name):
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    simple = logging.Formatter()
    extended = logging.Formatter(
        '%(asctime)s\t%(levelname)s\t%(name)s - %(message)s',
    )

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(simple)
    root.addHandler(console)

    blackbox = logging.FileHandler(file_name)
    blackbox.setLevel(logging.DEBUG)
    blackbox.setFormatter(extended)
    root.addHandler(blackbox)


def usage(errmsg: str):
    if errmsg:
        print(f'ERROR: {errmsg}')
    print(f'USAGE: {sys.argv[0]} test_path backend_path uservices_path')


def get_params():
    parser = argparse.ArgumentParser(description='sync')
    parser.add_argument('path', metavar='path', help='Path to test')
    parser.add_argument(
        'backend_path', metavar='path', help='Path to backend-py3',
    )
    parser.add_argument(
        'uservices_path', metavar='path', help='Path to uservices',
    )
    return parser.parse_args()


def get_config_source(path) -> Dict:
    config_path = os.path.join(path, 'config.yaml')
    logger.info(config_path)
    if os.path.isfile(config_path):
        with open(file=config_path, mode='r', encoding='utf-8') as stream:
            return (
                yaml.load(stream, Loader=yaml.Loader)
                .get('test')
                .get('config_source')
            )
    return {}


def main():
    args = get_params()
    path = args.path
    backend_path = args.backend_path
    uservices_path = args.uservices_path
    for directory in [path, backend_path, uservices_path]:
        if not os.path.isdir(directory):
            usage(f'directory "{directory}" does not exists')
            exit(2)

    log_path = os.path.abspath(os.path.join(path, 'sync.log'))
    setup_logging(log_path)

    error_count = 0
    config_source = get_config_source(path)
    if config_source:
        config_filename = config_source.get('file_name')
        if not config_filename:
            logger.info('wrong config_source in service.yaml need file_name')
            return False
        logger.info(f'config_filename: {config_filename}')
        config_filename = os.path.abspath(os.path.join(path, config_filename))
        if config_filename:
            if not copy_config.copy_prod_config(
                    config_filename,
                    config_source.get('backend_services', []),
                    backend_path,
                    config_source.get('uservices', []),
                    uservices_path,
                    config_source.get('skip_configs', []),
            ):
                logger.info(f'config copying failed')
                error_count = error_count + 1
    else:
        logger.info(f'nothing to sync')

    logger.info(f'finished sync with {error_count} errors')
    return error_count == 0


if __name__ == '__main__':
    sys.exit(main())
