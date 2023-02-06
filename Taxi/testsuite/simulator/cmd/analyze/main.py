import argparse

import join_statistics


def main(args: argparse.Namespace):
    generator_ = join_statistics.StatisticsJoiner()
    generator_.join(
        case_name=args.case_name,
        headers_projection=args.headers_projection,
        transpose=args.transpose,
    )


def build_args_parser():
    parser = argparse.ArgumentParser(
        description='Join statistics for simulator case',
    )
    parser.add_argument(
        '--case-name',
        '-c',
        help='name for target case',
        required=True,
        type=str,
    )
    parser.add_argument(
        '--headers-projection',
        '-p',
        help='select only specific headers',
        required=False,
        nargs='+',
        type=str,
        default=[],
    )
    parser.add_argument(
        '--transpose',
        '-t',
        help='Transpose statistics table '
        '(metrics are rows, cases are columns)',
        action='store_true',
    )

    return parser


if __name__ == '__main__':
    main(build_args_parser().parse_args())
