import argparse
import sys


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', dest='optional_argument')
    parser.add_argument('-f', action='store_true', dest='should_fail')
    return parser


def main():
    args = create_parser().parse_args()
    print(f'PATH: {sys.path}, ARG: {args.optional_argument}')

    if args.should_fail:
        raise ValueError('Failed by request')


if __name__ == '__main__':
    main()
