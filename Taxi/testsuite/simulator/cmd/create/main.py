import argparse

import case_generator


def main(args: argparse.Namespace):
    generator_ = case_generator.CaseGenerator()
    generator_.generate(case_name=args.case_name, template=args.template)


def build_args_parser():
    parser = argparse.ArgumentParser(description='Create simulator case')
    parser.add_argument(
        '--case-name', help='name for new case', required=True, type=str,
    )

    parser.add_argument(
        '--template',
        help='template type',
        required=False,
        type=str,
        default='default',
    )

    return parser


if __name__ == '__main__':
    main(build_args_parser().parse_args())
