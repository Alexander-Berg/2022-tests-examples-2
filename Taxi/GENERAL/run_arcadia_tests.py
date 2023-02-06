import argparse
import logging
import pathlib
from typing import Optional
from typing import Sequence

from taxi_buildagent import agenda
from taxi_buildagent import utils
from taxi_buildagent.tools import vcs
from taxi_buildagent.tools import ya


def main(argv: Optional[Sequence[str]] = None) -> None:
    utils.init_logger()

    args = parse_args(argv)

    with utils.catch_build_errors(exit_on_error=True):
        repo = vcs.open_repo()

        paths_to_test = []

        for service in args.services:
            project = agenda.Project(repo, service)
            service_yaml = project.get_service_yaml()
            if not service_yaml.get('ya-make', {}).get('enabled'):
                continue

            paths_to_test.append(project.relpath)

        if not paths_to_test:
            logging.warning('No services to test')
            return

        ya.run_tests(
            *paths_to_test,
            output_dir=str(args.output_dir.resolve()),
            junit_file=str(
                args.test_reports_dir.resolve() / 'tier0-tests.xml',
            ),
        )


def parse_args(argv: Optional[Sequence[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('services', nargs='+', help='Services under test')
    parser.add_argument(
        '--output-dir',
        required=True,
        type=pathlib.Path,
        help='Path to directory where output will be saved',
    )
    parser.add_argument(
        '--test-reports-dir',
        required=True,
        type=pathlib.Path,
        help='Path to directory where test reports will be saved',
    )
    return parser.parse_args(argv)


if __name__ == '__main__':
    main()
