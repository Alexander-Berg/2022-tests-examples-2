import os
import sys
import errno
import shutil
import argparse
import tempfile

import yaml
import pytest

from sandbox import common
import sandbox.taskbox.binary as cli

import library.python.sfx.extract


# Modules which are available on our clients in runtime.
# Can't refer to these listed in BUILD_SANDBOX,
# as it would cause tasks code to import and possibly alter test results.
ALLOWED_PATHS = (
    "yasandbox",
    "web", "common", "agentr", "etc", "serviceq",
    "sandboxsdk", "sdk2",
    "client", "projects",
    "__init__.py",
    "tasks", "virtualenv",
)


class CommandHandler(object):
    def __init__(self, args, unparsed_args):
        self.args = args
        self.unparsed_args = unparsed_args

    def extract(self):
        """
        Extract files included in binary to a directory and print the path to it.
        The following are deliberately skipped:
        - PY_PROGRAM and PYTEST/PY3TEST;
        - PY_LIBRARY/PY23_LIBRARY with TOP_LEVEL or NAMESPACE macros;
        - Sandbox files that may be missing on hosts executing tasks;
        """

        arcadia_dir = self.args.target
        if arcadia_dir is None:
            arcadia_dir = tempfile.mkdtemp()
            print arcadia_dir

        tmp_dir = tempfile.mkdtemp()
        library.python.sfx.extract.extract_sources(tmp_dir)
        cli.dump_resources(tmp_dir)

        source_dir = os.path.join(tmp_dir, "sandbox")
        sb_dir = os.path.join(arcadia_dir, "sandbox")

        for path in ALLOWED_PATHS:
            source = os.path.join(source_dir, path)
            destination = os.path.join(sb_dir, path)
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                try:
                    os.makedirs(os.path.dirname(destination))
                except OSError as e:
                    if e.errno == errno.EEXIST:
                        pass
                shutil.copy(source, destination)

        return arcadia_dir

    def test(self):
        """
        Run Sandbox tasks code tests on sources extracted from binary (SANDBOX-5476),
        so that it's possible to run tasks tests as "ya make -tt sandbox/tasks"
        instead of typing "~/arcadia/sandbox/sandbox test_tasks".

        For autocheck test parameters, see parent ya.make file.
        """

        arcadia_dir = self.args.target or self.extract()
        sb_dir = os.path.join(arcadia_dir, "sandbox")

        init_path = os.path.join(sb_dir, "__init__.py")
        if not os.path.exists(init_path):
            raise RuntimeError(
                "{} doesn't exist, although it's required for tests to perform correctly".format(init_path)
            )

        os.chdir(arcadia_dir)

        projects_dir = os.path.join(sb_dir, "projects")
        runtime_dir = os.path.join(os.path.dirname(sb_dir), "runtime_data")
        with tempfile.NamedTemporaryFile(delete=False) as conf:
            settings = {"client": {"dirs": {"data": runtime_dir}}}
            yaml.dump(settings, conf, default_flow_style=False)

        os.environ[common.config.Registry.CONFIG_ENV_VAR] = conf.name
        cmd = [
            "--confcutdir={}".format(projects_dir),
            "sandbox/projects",
        ]

        if self.unparsed_args:
            cmd.extend(self.unparsed_args)

        res = pytest.main(cmd)
        sys.exit(res)


def parse_args():
    parser = argparse.ArgumentParser(description="Sandbox tasks tests binary")
    subparsers = parser.add_subparsers(title="available commands", help="<description>", metavar="<command>")

    sp_extract = subparsers.add_parser(
        CommandHandler.extract.__name__, help="Extract code into a directory and output the path to it",
        formatter_class=argparse.RawTextHelpFormatter
    )
    sp_extract.set_defaults(command=CommandHandler.extract)

    sp_test = subparsers.add_parser(
        CommandHandler.test.__name__, help="Run Sandbox tests. You can pass any pytest-specific options, like -ra or -v",
        formatter_class=argparse.RawTextHelpFormatter
    )
    sp_test.set_defaults(command=CommandHandler.test)

    for p in (sp_extract, sp_test):
        p.add_argument("--target", help="Directory with Arcadia (default: temporary directory)")

    return parser.parse_known_args()


def main():
    parsed, unparsed = parse_args()
    handler = CommandHandler(parsed, unparsed)
    handler.args.command(handler)
