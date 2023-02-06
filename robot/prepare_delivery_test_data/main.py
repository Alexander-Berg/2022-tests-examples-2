# -*- coding: utf-8 -*-

import argparse
import json
import logging
import os
import tarfile
from os.path import join as pj

from robot.jupiter.tools.prepare_delivery_test_data import test_preparer
from robot.library.yuppie.prepare_yt_testdata import recursive_read


def collect_args():
    _LOG_FORMAT = '%(asctime)s [%(name)s] [%(levelname)s]  %(message)-100s'
    logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)
    logging.getLogger('yt.packages.requests.packages.urllib3.connectionpool').setLevel(level=logging.ERROR)

    parser = argparse.ArgumentParser()
    parser.add_argument('--delivery-config', type=argparse.FileType())
    parser.add_argument('--yt-output-dir')
    parser.add_argument('--local-output-dir')
    parser.add_argument('--delivery', nargs='*', dest='deliveries', help='Create sample only for specified deliveries.')
    parser.add_argument('--source-cluster', help='Use this cluster and do not try to guess one using config.')
    parser.add_argument('--source-table', help='Use this table and do not try to guess one using config.')
    parser.add_argument('--delivery-prefix', help='Delivery prefix', default='//home/jupiter')
    parser.add_argument('--delivery-type', choices=['tables', 'files'], default='tables')
    parser.add_argument('--extfiles', help='Path to extfiles.py')
    parser.add_argument('--sbclient', help='Path to sbclient.py')

    parser.add_argument('--output-dir', default='', help='Where to store results.')

    parser.add_argument(
        '--no-user-meta',
        action='store_false',
        help='I won\'t blame you, if you don\'t want to save user defined metaattributes in test data.',
        dest='save_meta'
    )

    parser.add_argument(
        '--save-attribute',
        action='append',
        help='What you ask is what you get. Can be used multiple times. Overrides --no-user-meta option.',
        dest='attributes_to_save',
        default=[]
    )

    parser.add_argument(
        '--mock',
        action='store_true',
        help='Take only 10 first records from tables and create empty files.'
    )

    parser.add_argument(
        '--check-sorting',
        action='store_true',
        help='Require every table being read to be sorted.'
    )

    parser.add_argument('--force', action='store_true', help='Replace existing files')

    parser.add_argument('--skip-sample', action='store_true', help='Skip sample generation')
    parser.add_argument('--skip-download', action='store_true', help='Skip loading files to local machine')
    parser.add_argument('--skip-archive', action='store_true', help='Skip archiving')
    parser.add_argument('--skip-upload-to-sandbox', action='store_true', help='Skip uploading to sandbox')

    parser.add_argument('--archname', default='delivery_tables.tar', help='Name of output archive')
    parser.add_argument('--data-spec-name', default='data_spec.json', help='Name of json file with description of downloaded data')

    yt_output_proxy = os.environ.get('YT_PROXY', '')
    parser.add_argument('--yt-output-proxy', default=yt_output_proxy)

    args = parser.parse_args()

    return args, parser


def sample(args, parser, uploader):

    if args.delivery_config is None:
        raise parser.error('sampling requires --delivery-config')

    delivery_config_parsed = json.load(args.delivery_config)
    delivery_config_parsed = {k: v for k, v in delivery_config_parsed.items() if v.get("delivery_test", True)}

    if not args.delivery_config:
        raise parser.error('--delivery-config is necessary for sampling')

    if not args.yt_output_dir and not args.local_output_dir:
        raise parser.error('Cannot do sampling without any of --local-output-dir or --yt-output-dir')

    if args.delivery_type == 'tables':
        if args.yt_output_proxy == '':
            raise parser.error('delivery_type=tables requires --yt-output-proxy'
                               '(You can just set YT_PROXY)')

        if args.yt_output_dir is None:
            raise parser.error('delivery_type=tables requires --yt-output-dir')
        if not args.source_table:
            logging.info('Start naive sampling')
            failed = uploader.try_to_prepare_test_data(delivery_config_parsed, args.yt_output_dir, args.deliveries)
            logging.info('Start handmade sampling')
            uploader.hand_written_sampling(
                failed,
                delivery_config_parsed,
                args.yt_output_dir,
                args.deliveries,
                args.delivery_prefix)
        else:
            if len(args.deliveries) != 1:
                raise parser.error('Only one delivery can be sampled if --source-table option is specified.')

            uploader.create_sample(args.deliveries[0], args.source_cluster, args.source_table, args.yt_output_dir)

    if args.delivery_type == 'files':
        uploader.prepare_test_files(
            delivery_config_parsed,
            args.local_output_dir,
            args.deliveries,
            args.extfiles,
            args.sbclient
        )


def download(args, parser, uploader):
    if not args.yt_output_proxy or not args.yt_output_dir:
        raise parser.error('--yt-output-proxy and --yt-output-dir is necessary for downloading')

    output_dir_abspath = os.path.abspath(args.output_dir)
    if not os.path.exists(output_dir_abspath):
        os.makedirs(output_dir_abspath)

    data_spec_dict = {}
    recursive_read(
        path=args.yt_output_dir,
        proxy=uploader.default_proxy,
        strip_prefix=args.yt_output_dir,
        data_spec=data_spec_dict,
        user_meta_attrs_to_save=args.attributes_to_save,
        check_sorting=args.check_sorting,
        mock=args.mock,
        output_dir=output_dir_abspath,
        save_meta=args.save_meta
    )

    with open(pj(output_dir_abspath, args.data_spec_name), 'w') as data_spec_file:
        json.dump(data_spec_dict, data_spec_file, indent=4, separators=(',', ': '), sort_keys=True)


def ask(question):
    decision = None
    question_message = '{} (y/n): '.format(question)
    while decision not in {'y', 'n'}:
        answer = raw_input(question_message)
        decision = answer[0].lower()
    return decision == 'y'


def archive(args):
    archname = args.archname
    if os.path.exists(pj(args.output_dir, archname)):
        error_message = 'File {} already exists.'.format(archname)
        if args.force or ask(error_message + '\nDo you want to replace it?'):
            os.remove(pj(args.output_dir, archname))
        else:
            raise RuntimeError("delivery_tables.tar already exists")

    with tarfile.open(pj(args.output_dir, archname), "w:gz") as tar:
        for filename in os.listdir(args.output_dir):
            if filename != archname:
                tar.add(pj(args.output_dir, filename), arcname=filename)


def upload_to_sandbox(args, parser):
    print("Uploading to sandbox is not supported")


def main():
    args, parser = collect_args()
    uploader = test_preparer.TestPreparer(args.yt_output_proxy)

    if not args.skip_sample:
        try:
            sample(args, parser, uploader)
        except:
            logging.exception('')
            logging.error("Exception in sampling")
            exit(1)

    if not args.skip_download:
        try:
            download(args, parser, uploader)
        except:
            logging.exception('')
            logging.error("Exception in downloading")
            logging.error("Use --skip-sample if you want to restart from this step")
            exit(1)

    if not args.skip_archive:
        try:
            archive(args)
        except:
            logging.exception('')
            logging.error("Exception in archiving")
            logging.error("Use --skip-sample --skip-download if you want to restart from this step")
            exit(1)

    if not args.skip_upload_to_sandbox:
        try:
            upload_to_sandbox(args, parser)
        except:
            logging.exception('')
            logging.error("Exception in uploading to sandbox")
            logging.error("Use --skip-sample --skip-download --skip-archive if you want to restart from this step")
            exit(1)
