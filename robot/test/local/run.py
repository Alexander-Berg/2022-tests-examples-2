#!/usr/bin/env python

from argparse import ArgumentParser
from distutils.spawn import find_executable
from subprocess import check_call
import os


def build_test_params(args, extra_args):
    result_args = []
    if args.blrt_config:
        result_args.append("blrt_config={}".format(os.path.realpath(args.blrt_config)))
    if args.dev:
        result_args.append("dev={}".format(args.dev))
    result_args.append("datacamp={}".format(str(args.datacamp).lower()))
    if args.input:
        result_args.append("input={}".format(",".join(args.input)))
    result_args += args.extra + extra_args
    return [it for arg in result_args for it in ("--test-param", arg)]


def exec_ya_make_cmd(args, extra_args):
    ya_make_cmd = [
        str(find_executable("ya")),
        "make",
        "--checkout",
        "--target", os.path.abspath(os.path.dirname(__file__)),
        "--threads", "16",
        "--run-all-tests",
        "--test-stderr",
        "--test-debug",
    ] + build_test_params(args, extra_args)
    print(" ".join(ya_make_cmd))
    check_call(ya_make_cmd)


def main():
    parser = ArgumentParser()
    parser.add_argument("-b", "--blrt-config")
    parser.add_argument("-d", "--dev", choices=["local", "vanilla", "none"], default="local")
    parser.add_argument("--datacamp", action="store_true", default=False)
    parser.add_argument("-i", "--input", nargs="*", default=[])
    parser.add_argument("-e", "--extra", nargs="*", default=[])
    args, extra_args = parser.parse_known_args()
    exec_ya_make_cmd(args, extra_args)


if __name__ == '__main__':
    main()
