#!/usr/bin/env python3

import argparse
import os

import make_utils


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--builder-service', default='taxi-uservices-xenial')
    args = parser.parse_args()

    if os.path.exists('./uservices/Makefile'):
        proc = make_utils.run_process(
            proc_args=[
                'docker-compose',
                '-f',
                f'../../taxi/uservices/docker-compose.yml',
                'run',
                '--rm',
                args.builder_service,
                '/taxi/dockertest/build-uservices.sh',
            ],
        )
        if proc.returncode:
            make_utils.report_error('Build error')
            exit(proc.returncode)


if __name__ == '__main__':
    main()
