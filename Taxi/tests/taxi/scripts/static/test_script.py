import argparse


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', dest='optional_argument')
    parser.add_argument('-l', type=int, dest='logs_count')
    parser.add_argument('-f', action='store_true', dest='should_fail')
    return parser


def main():
    args = create_parser().parse_args()
    print(f'ARG: {args.optional_argument}')

    if args.logs_count is not None:
        for _ in range(args.logs_count // 1024):
            print('A' * 1024)

        print('A' * (args.logs_count % 1024))

    if args.should_fail:
        raise ValueError('Failed by request')


if __name__ == '__main__':
    main()
