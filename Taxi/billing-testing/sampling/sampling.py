import argparse
import asyncio
import datetime
from importlib import util
import logging
import os
import pathlib
import sys

import dateutil.parser
import yaml

from . import sampler

ENCODING = 'utf-8'

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


async def _main() -> bool:
    args = get_params()
    path = args.path
    if not os.path.isdir(path):
        usage(f'script directory "{path}" does not exists')
        exit(2)
    os.chdir(os.path.abspath(path))

    logs_dir = os.path.abspath(os.path.join('logs'))
    if not os.path.isdir(logs_dir):
        os.makedirs(logs_dir)
    log_path = os.path.abspath(os.path.join('logs', 'runtime.log'))
    setup_logging(log_path)

    date_str = args.date
    max_date = datetime.date.today() - datetime.timedelta(days=2)
    if date_str == 'last':
        date = max_date
        logger.info(f'date = {date}')
    else:
        date = dateutil.parser.parse(date_str).date()
        if date > max_date:
            logger.info(f'max date is {max_date}')
            return False

    token_path = os.path.join(pathlib.Path.home(), '.yql', 'token')
    error_count = 0
    config = get_sampler_config()
    for sample_name in config:
        output_folder = os.path.join(
            config[sample_name].get('output_path', 'data'),
        )
        sampler_class = get_sampler_class(config[sample_name]['class'])
        logger.info('*' * 29)
        logger.info('*' * 29)
        logger.info(f'sampling {sample_name} started')
        file_name = config[sample_name].get('file_name', f'{sample_name}.json')
        output_filename = os.path.abspath(
            os.path.join(output_folder, file_name),
        )
        sampler_obj = sampler_class(
            sample_name,
            output_filename,
            date,
            token_path,
            config[sample_name],
        )
        if not await sampler_obj.sample_data():
            error_count = error_count + 1
            logger.info(f'sampling {sample_name} finished with error')
        else:
            logger.info(f'sampling {sample_name} finished successfully')

    logger.info(f'finished sampling with {error_count} errors')
    return error_count == 0


def main():
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(_main())
    loop.close()
    return 0 if result else 1


def get_sampler_class(class_name: str):
    sampler_class = getattr(sampler, class_name, None)
    if sampler_class:
        return sampler_class
    sampler_class_path = os.path.join('sample.py')
    logger.info(f'checking {sampler_class_path}')
    if os.path.isfile(sampler_class_path):
        spec = util.spec_from_file_location('test_sampler', sampler_class_path)
        sampler_module = util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(sampler_module)  # type: ignore
        sampler_class = getattr(sampler_module, class_name)
    if not sampler_class:
        raise RuntimeError(f'{sampler_class} not found')
    return sampler_class


def get_sampler_config() -> dict:
    config_path = os.path.join('config.yaml')
    if os.path.isfile(config_path):
        with open(file=config_path, mode='r', encoding='utf-8') as stream:
            return yaml.load(stream, Loader=yaml.Loader).get('sample', {})
    return {}


def usage(errmsg: str) -> None:
    if errmsg:
        print(f'ERROR: {errmsg}')
    print(f'USAGE: {sys.argv[0]} test_path --date=yyyy-mm-dd ')


def get_params():
    parser = argparse.ArgumentParser(description='Sampling')
    parser.add_argument('path', metavar='path', help='Path to test')
    parser.add_argument('date', help='Date to sample (yyyy-mm-dd|last)')
    return parser.parse_args()


if __name__ == '__main__':
    try:
        main()
    except BrokenPipeError as exc:
        sys.exit(exc.errno)
