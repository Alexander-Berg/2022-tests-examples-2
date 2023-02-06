#!/usr/bin/env python3

import argparse
import time

import make_utils


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--wait-script',
        type=str,
        required=False,
        default='/taxi/tools/wait_services.sh',
        help='Path to wait_services script',
    )
    parser.add_argument(
        'docker_compose',
        default=None,
        type=str,
        nargs='*',
        metavar='DOCKER_FILE',
        help='Path to docker-compose.yml to be processed',
    )
    args = parser.parse_args()

    start_time = time.time()
    proc = make_utils.run_docker_compose(
        docker_files=args.docker_compose,
        proc_args=[
            'run',
            '-T',
            '--rm',
            'taxi-tests',
            args.wait_script,
        ],
        stderr_to_stdout=True,
    )

    end_time = time.time()
    wait_services_time = (end_time - start_time) * 1000
    key_stat_name = 'Wait Services Time For Integration Tests'
    make_utils.report_statistic(key_stat_name, wait_services_time)

    if proc.returncode:
        make_utils.run_process(proc_args=['docker', 'ps', '-a'])

        msg = 'Error waiting for services.'

        bad_docker_info = make_utils.get_bad_docker_info()
        if bad_docker_info:
            make_utils.report_error(
                'Containers in bad state. ' + str(bad_docker_info),
            )

        make_utils.report_error(msg)
        exit(1)


if __name__ == '__main__':
    main()
