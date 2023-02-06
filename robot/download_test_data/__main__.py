from robot.jupiter.library.python.sample import download_test_data as dtd

import os
import argparse
import logging


def download_test_data(args, dir_specified):
    if not os.path.exists(args.tmp_dir):
        dtd.download(mr_server=args.mr_server, mr_prefix=args.mr_prefix,
                     sample_type=args.instance, yt_fmt=args.format, tmp_dir=args.tmp_dir, state=args.state)
    else:
        logging.warning("Found %s. Remove it manually to restart from very beginning.", args.tmp_dir)
    dtd.pack(output=args.output, tmp_dir=args.tmp_dir, keep_tmp_dir=dir_specified)


if __name__ == '__main__':
    _LOG_FORMAT = '%(asctime)s [%(name)s] [%(levelname)s]  %(message)-100s'
    logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)
    logging.getLogger("yt.packages.requests.packages.urllib3.connectionpool").setLevel(level=logging.WARNING)

    parser = argparse.ArgumentParser()
    parser.add_argument('--instance', help='Target instance', default='integration')
    parser.add_argument('--format', help='Download format', default='yson')
    parser.add_argument('--mr-prefix', help='YT prefix of Jupiter instance', default='//home/jupiter')
    parser.add_argument('--mr-server', help='YT proxy', default='arnold.yt.yandex.net')
    parser.add_argument('--output', help='Data bundle name', default='integration.tar')
    parser.add_argument('--tmp-dir', help='Path to downloaded data', default=None)
    parser.add_argument('--state', help='Sample state', default=None)

    args = parser.parse_args()

    dir_specified = args.tmp_dir is not None
    if not dir_specified:
        args.tmp_dir = dtd.get_temp_dir(args.output)

    download_test_data(args, dir_specified)
