#!/usr/bin/env python3

import argparse
import pathlib
import sys

sys.path.extend([str(pathlib.Path(__file__).parent.parent / 'util')])

import runtests_utils as utils  # noqa: E402 pylint: disable=E0401,C0413


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '--output',
        default='/tmp/uservices-build/runtests',
        type=pathlib.Path,
        help='Path to store test results and intermediates in',
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_file = args.output / 'test_config.json'
    recipe_context_file = args.output / 'recipe_context_file.json'
    if not config_file.exists() or not recipe_context_file.exists():
        print('All recipes are already down!')
        return

    test_config = utils.TestConfig.load(config_file)
    recipe_context = utils.TestContext(recipe_context_file)
    utils.run_recipes(recipe_context, test_config.recipes, action='stop')
    recipe_context_file.unlink()


if __name__ == '__main__':
    main()
