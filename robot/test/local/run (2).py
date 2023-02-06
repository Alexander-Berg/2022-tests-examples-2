#!/usr/bin/python2

from argparse import ArgumentParser
from distutils.spawn import find_executable
from subprocess import check_call
import logging
import os


def logged_call(cmd_list):
    logging.info(" ".join(cmd_list))
    check_call(cmd_list)


def get_build_command(args, extra_ya_args):
    executed_script_dir = os.path.abspath(os.path.dirname(__file__))
    if os.path.exists("ya"):
        ya = "./ya"
    else:
        ya = find_executable("ya")
        if not ya:
            ya = os.path.abspath(os.path.join(executed_script_dir, "../../../../ya"))

    build_cmd_list = [
        str(ya),
        "make",
        "-r",
        "--target", os.path.relpath(executed_script_dir),
        "-DDEBUGINFO_LINES_ONLY",
        "-DNO_SVN_DEPENDS",
    ]

    if not args.no_checkout:
        build_cmd_list.append("--checkout")
    if args.no_binaries:
        build_cmd_list.append("-DNO_BINARIES")

    return build_cmd_list + extra_ya_args


def dist_build(build_cmd_list):
    dist_build_cmd_list = ["--dist", "--download-artifacts", "--force-build-depends", "--add-result", "''"]
    logged_call(build_cmd_list + dist_build_cmd_list)
    logging.info("Jupiter successfully built on cluster.")


def run(build_cmd_list, args):
    test_cmd_params = [
        "--run-all-tests",
        "--test-filter=jupiter",
        "--test-stderr",
        "--test-disable-timeout",
        "--test-param", "jupiter_config={config}".format(config=os.path.abspath(args.config)),
    ]

    test_cmd_list = build_cmd_list + test_cmd_params
    logged_call(test_cmd_list)


def build_and_run(args, extra_ya_args):
    build_cmd_list = get_build_command(args, extra_ya_args)
    if args.dist:
        dist_build(build_cmd_list)
    run(build_cmd_list, args)


def main():
    _LOG_FORMAT = '%(asctime)s [%(name)s] [%(levelname)s]  %(message)-100s'
    logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)

    parser = ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--no-checkout', action='store_true')
    parser.add_argument('--no-binaries', action='store_true')
    parser.add_argument('--dist', action='store_true')
    parser.add_argument('--binaries-branch', default=None)
    parser.add_argument('--binaries-task-id', default=None)
    args, extra_ya_args = parser.parse_known_args()

    if args.binaries_task_id or args.binaries_branch:
        # TODO (@paxakor)
        raise NotImplementedError("Downloading from SB is not yet implemented")

    build_and_run(args, extra_ya_args)


if __name__ == '__main__':
    main()
