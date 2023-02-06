#!/usr/bin/env python3

import argparse

import get_services
import teamcity_utils


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('services', metavar='SERVICE', nargs='+')
    args = parser.parse_args()

    integration_test_services = get_services.load_services()

    tested_services = set()
    for service in args.services:
        prefixed_service = get_services.get_prefixed_service_name(service)
        if prefixed_service not in integration_test_services:
            continue
        tested_services.add(service)

    teamcity_utils.set_parameter(
        'env.CHANGED_PROJECTS', ' '.join(sorted(tested_services)) or '_empty',
    )


if __name__ == '__main__':
    main()
