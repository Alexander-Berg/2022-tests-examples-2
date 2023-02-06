import os
import random
import string
from argparse import ArgumentParser

import yt.wrapper as yt_wrapper
import yt.wrapper.format as yt_formats
from six.moves import range


def get_parser():
    parser = ArgumentParser(prog='python -m tests.cli_tools.generate_data')
    parser.add_argument('--yt-path', help='Path to YT table', required=True)
    parser.add_argument('--yt-proxy', help='YT Proxy', default='hahn')
    parser.add_argument('--yt-token', help='YT Token')
    parser.add_argument('--rows',
                        help='Number of rows to Generate',
                        default=1000, type=int)
    parser.add_argument('--chunk-table', action='store_true', default=False)
    return parser


def random_str(length=64):
    return ''.join([
        random.choice(string.ascii_lowercase) for _ in range(length)])


def generate_data(rows, chunk_table):
    for _ in range(rows):
        random_number = random.randint(0, 2 ** 32)
        random_string = random_str()
        if chunk_table:
            yield {'chunk': '{}\t{}'.format(random_number, random_string)}
        else:
            yield {'col1': random_number, 'col2': random_string}


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    data = generate_data(args.rows, args.chunk_table)

    yt_client = yt_wrapper.YtClient(
        proxy=args.yt_proxy,
        token=args.yt_token or os.environ['YT_TOKEN'],
        config={'backend': 'rpc'},
    )

    if not args.chunk_table:
        yt_client.create_table(
            path=args.yt_path,
            attributes={
                'schema': [
                    {
                        'name': 'col1',
                        'type': 'int64'
                    },
                    {
                        'name': 'col2',
                        'type': 'string'
                    }
                ]
            }
        )

    yt_client.write_table(
        table=args.yt_path,
        input_stream=data,
        format=yt_formats.YsonFormat()
    )
