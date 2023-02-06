#!/usr/bin/env python3

import argparse
import sys

import make_utils
import rm_broken_networks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'docker_compose',
        default=['docker-compose.yml', 'docker-compose.eats.yml'],
        type=str,
        nargs='*',
        metavar='DOCKER_FILE',
        help='Path to docker-compose.yml to be processed',
    )
    args = parser.parse_args()

    proc = make_utils.run_docker_compose(
        docker_files=args.docker_compose,
        proc_args=[
            'down',
            '--remove-orphans',
            '--volumes',
            '--timeout',
            '0',
        ],
        stderr_to_stdout=True,
    )
    if proc.returncode:
        sys.stderr.write(
            'Some networks are broken. Removing using other way...\n',
        )
        rm_broken_networks.main()


if __name__ == '__main__':
    main()
