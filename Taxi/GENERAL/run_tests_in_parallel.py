import argparse
import asyncio
import logging
import os
import pathlib
import signal
from typing import List
from typing import Optional

from taxi_buildagent import dockertest
from taxi_buildagent import utils
from taxi_buildagent.clients import mds_s3

DEFAULT_DC_ENV = 'taxi-test-env'
DEFAULT_DC_SERVICE = 'taxi-test-service'
DEFAULT_IMAGE = 'registry.yandex.net/taxi/taxi-integration-xenial-base'
FLAP_TESTS_FILENAME = pathlib.Path('flap_tests_list')

logger = logging.getLogger(__name__)


def main(argv: Optional[List[str]] = None) -> None:
    utils.init_logger()
    with utils.catch_build_errors(exit_on_error=True):
        signal.signal(signal.SIGTERM, terminate)
        args = parse_args(argv)
        os.chdir(args.path_to_repo)
        download_flap_tests_list()
        exit_code = asyncio.run(
            run_tests(
                dc_service=args.dc_service,
                dc_env=args.dc_env,
                base_image=args.base_image,
                services=args.services,
                test_reports_dir=args.test_reports_dir,
                service_output_dir=args.service_output_dir,
            ),
        )
        if exit_code != 0:
            exit(exit_code)


def download_flap_tests_list() -> None:
    try:
        mds_s3.download_flap_tests_list(FLAP_TESTS_FILENAME)
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning(
            'Load flap tests list from mds failed with exception %s: %s',
            type(exc),
            exc,
        )


def parse_args(argv: Optional[List[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--docker-compose-service',
        dest='dc_service',
        default=DEFAULT_DC_SERVICE,
        help='Name of service from docker-compose.yaml',
    )
    parser.add_argument(
        '--docker-compose-env',
        dest='dc_env',
        default=DEFAULT_DC_ENV,
        help='Name of environment service from docker-compose.yaml',
    )
    parser.add_argument(
        '--path-to-repo',
        type=pathlib.Path,
        default=pathlib.Path.cwd(),
        help='Path to tested repository',
    )
    parser.add_argument(
        '--base-image',
        default=DEFAULT_IMAGE,
        help=(
            'Docker image on which containers with tests will be based. '
            '(set DOCKER_IMAGE environment variable)'
        ),
    )
    parser.add_argument(
        '--test-reports-dir',
        type=pathlib.Path,
        default=pathlib.Path('test-results'),
        help=(
            'Path to directory where test reports will be saved '
            '(relative to \'--path-to-repo\')'
        ),
    )
    parser.add_argument(
        '--service-output-dir',
        type=pathlib.Path,
        default=None,
        help='Path to directory where services output will be saved',
    )
    parser.add_argument(
        'services', nargs='*', help='Services names which should be tested',
    )
    return parser.parse_args(argv)


async def run_tests(
        dc_service: str,
        dc_env: str,
        base_image: str,
        services: List[str],
        test_reports_dir: pathlib.Path,
        service_output_dir: pathlib.Path,
) -> int:
    max_workers = int(os.getenv('MAX_TEST_CONTAINERS', '4'))
    logger.info(
        'Running `%s` in parallel (%s workers)', dc_service, max_workers,
    )
    async with dockertest.Pool(
            dc_service, dc_env, base_image, max_workers,
    ) as pool:
        exit_code = await pool.run_tests(
            services, test_reports_dir, service_output_dir,
        )
    return exit_code


def terminate(*args, **kwargs) -> None:
    logger.error('Terminate tests running with SIGTERM')
    raise KeyboardInterrupt


if __name__ == '__main__':
    main()
