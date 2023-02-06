#!/usr/bin/env python
# coding: utf8

import argparse
import asyncio
from importlib import util
import json
import logging
import os
import shutil
import sys

import yaml

from sibilla import reporter
from sibilla import storage
from sibilla import test
from sibilla.test import context as ctx
from sibilla.test import event


logger = logging.getLogger(__name__)

RESULTS_DATABASE_NAME = 'results.sqlite3'


def usage(errmsg: str):
    if errmsg:
        print(f'ERROR: {errmsg}')
    print(
        f'USAGE: {sys.argv[0]} test_suite_path '
        '[--warmup-stq] [--warmup-db] [--tests] [--bootstrap] [-v|--verbose]',
    )


def setup_logging(output, verbose):
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    simple = logging.Formatter()
    extended = logging.Formatter(
        '%(asctime)s\t%(levelname)s\t%(name)s - %(message)s',
    )

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO if verbose else logging.WARN)
    console.setFormatter(simple)
    root.addHandler(console)

    fname = os.path.join(output, 'runtime.log')
    blackbox = logging.handlers.RotatingFileHandler(
        fname, maxBytes=1e6, backupCount=1,
    )
    blackbox.setLevel(logging.DEBUG)
    blackbox.setFormatter(extended)
    root.addHandler(blackbox)


async def _main(loop: asyncio.AbstractEventLoop):
    args = _get_params()
    path = args.path
    output = os.path.abspath(os.path.join(path, 'output'))
    if not os.path.isdir(path):
        usage(f'script directory "{path}" does not exists')
        exit(2)
    if not os.path.isdir(output):
        os.makedirs(output)
    db_storage = os.path.join(output, RESULTS_DATABASE_NAME)
    setup_logging(output, args.verbose)
    os.chdir(path)
    logger.info('Run test suite from %s', path)
    suite_class = get_suite_class(path)
    suite_config = get_suite_config(path)
    events_collector = event.EventCollector()
    context = await ctx.ContextData.create(
        loop=loop, logger=events_collector, suite_path=path,
    )
    logger.info('using storage %s', db_storage)
    stg = storage.Storage(db_storage, keep_old=True, store_all=False)
    events_collector.add(event.EventToScreen())
    events_collector.add(event.EventToStorage(stg))
    if args.bootstrap:
        test_path = os.path.join(path, 'tests')
        output_path = os.path.join(path, 'generated')
        if os.path.exists(output_path):
            shutil.rmtree(output_path, ignore_errors=True)
        os.mkdir(output_path)
        events_collector.add(
            event.EventToFile(output_path, suite_class.processors()),
        )
    else:
        test_path = os.path.join(path, 'generated')
    if not os.path.isdir(test_path):
        logger.error('Directory %s not exists (try to bootstrap)', test_path)
        return False
    test_data_iterator = iter(tests_source(test_path))
    suite = suite_class(
        test_data_iterator, context=context, options=suite_config,
    )
    if args.warmup_db:
        print('Prepare database and configs-api')
        status = await suite.fill_db()
    if args.warmup_stq:
        print('Prepare stq queues')
        status = await suite.fill_services()
    if args.tests:
        status = await suite.exec()
        reporter.generate_report(
            outdir=output, stg=stg, session_uuid=stg.current_session_uuid(),
        )
    await context.close()
    return status


def main():
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(_main(loop=loop))
    loop.close()
    return 0 if result else 1


def _get_params():
    parser = argparse.ArgumentParser(description='Sibilla tests.')
    parser.add_argument(
        'path', metavar='path', help='Test suite path', default='/taxi/tests',
    )
    parser.add_argument(
        '--bootstrap', action='store_true', help='bootstrap tests',
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true', help='verbose mode',
    )
    parser.add_argument(
        '--warmup-db', action='store_true', help='warmup database',
    )
    parser.add_argument('--tests', action='store_true', help='Run suite')
    parser.add_argument('--warmup-stq', action='store_true', help='warmup stq')
    return parser.parse_args()


def get_suite_class(path):
    suite_class_path = os.path.join(path, 'suite.py')
    suite_class = test.Suite
    if os.path.isfile(suite_class_path):
        spec = util.spec_from_file_location('test_suite', suite_class_path)
        suite_module = util.module_from_spec(spec)
        spec.loader.exec_module(suite_module)
        suite_class = suite_module.TestSuite
    return suite_class


def get_suite_config(path):
    config_path = os.path.join(path, 'config.yaml')
    if os.path.isfile(config_path):
        with open(file=config_path, mode='r', encoding='utf-8') as stream:
            result = yaml.load(stream, Loader=yaml.FullLoader).get('test', {})
            config_source = result.get('config_source')
            if config_source:
                file_name = config_source.get('file_name')
                try:
                    configs_file_name = os.path.join(path, file_name)
                    if os.path.isfile(configs_file_name):
                        with open(
                                file=configs_file_name,
                                mode='r',
                                encoding='utf-8',
                        ) as stream:
                            configs: dict = yaml.load(
                                stream, Loader=yaml.FullLoader,
                            ).get('configs', {})
                            configs.update(
                                result.get('prerequests', {}).get(
                                    'configs', {},
                                ),
                            )
                            if not result.get('prerequests'):
                                result['prerequests'] = {}
                            result['prerequests']['configs'] = configs
                            logger.info('Added %d configs', len(configs))
                except Exception as error:  # pylint: disable=broad-except
                    print(
                        (
                            f'Could not load configs from file {file_name}: '
                            f'{str(error)}'
                        ),
                        sys.stderr,
                    )
            return result
    return {}


def tests_source(path):
    for file_path in sorted(os.listdir(path)):
        if file_path[-5:] != '.json':
            continue
        full_path = os.path.join(path, file_path)
        if os.path.isfile(full_path):
            try:
                fdesc = open(file=full_path, mode='r', encoding='utf-8')
                data = json.load(fdesc)
                if 'name' not in data:
                    data['name'] = file_path
                yield data
            except json.JSONDecodeError:
                print(f'Could not parse file {full_path}', sys.stderr)


if __name__ == '__main__':
    sys.exit(main())
