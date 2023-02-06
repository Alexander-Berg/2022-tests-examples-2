import argparse
import os
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional

import packaging.version

import get_services
import make_utils

DEBUG = os.getenv('TOOL_DEBUG')


class ServiceInfo(NamedTuple):
    name: str
    image: str
    packages: List[str]


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    all_services = filter_services()
    required_services = args.services
    if required_services == ['all']:
        required_services = list(all_services)
    wrong_services = set(required_services) - all_services.keys()
    if wrong_services:
        make_utils.report_error(
            'Wrong services: %s' % ', '.join(wrong_services),
        )
        exit(1)
    services = [all_services[service] for service in required_services]
    if args.action == 'build':
        build(services, args.tag)
    elif args.action == 'push':
        push(services, args.tag)
    else:
        raise NotImplementedError


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', required=True, choices=['build', 'push'])
    parser.add_argument('--tag', required=True)
    parser.add_argument('services', nargs='+')
    return parser.parse_args(argv)


def filter_services() -> Dict[str, ServiceInfo]:
    all_services = get_services.load_services()
    services: Dict[str, ServiceInfo] = {}
    for name, data in all_services.items():
        if 'build' not in data:
            continue
        if not data['image'].endswith(':${IMAGE_VERSION:-test}'):
            continue
        services[name] = ServiceInfo(
            name=name,
            image=get_services.prepare_image(data['image']).split(':', 1)[0],
            packages=[
                package.split('=', 1)[0].strip()
                for package in data['build']['args']['packages'].split()
            ],
        )
    return services


def build(services: List[ServiceInfo], tag: str) -> None:
    versions = get_versions(services, pull=True)
    for service in services:
        proc = make_utils.run_process(
            proc_args=['docker-compose', 'build', '--no-cache', service.name],
            env={'IMAGE_VERSION': tag},
        )
        if proc.returncode:
            make_utils.report_error('Failed build service %s' % service.name)
            exit(1)
    result_versions = get_versions(services, tag=tag)
    validate_versions(services, versions, result_versions)
    tag_latest(services, tag)


def push(services: List[ServiceInfo], tag: str) -> None:
    services_names = [service.name for service in services]
    if DEBUG:
        print('Debug mode is enabled. Skip push tag images')
    else:
        proc = make_utils.run_process(
            proc_args=['docker-compose', 'push', *services_names],
            env={'IMAGE_VERSION': tag},
        )
        if proc.returncode:
            make_utils.report_error('Failed push services')
            exit(1)
    old_versions = get_versions(services, pull=True)
    new_versions = get_versions(services, tag=tag)
    validate_versions(services, old_versions, new_versions)
    tag_latest(services, tag)
    if DEBUG:
        print('Debug mode is enabled. Skip push latest images')
    else:
        proc = make_utils.run_process(
            proc_args=['docker-compose', 'push', *services_names],
            env={'IMAGE_VERSION': 'latest'},
        )
        if proc.returncode:
            make_utils.report_error('Failed push services')
            exit(1)


def get_versions(
        services: List[ServiceInfo], *, pull=False, tag='latest',
) -> List[List[str]]:
    if pull:
        services_names = [service.name for service in services]
        proc = make_utils.run_process(
            proc_args=['docker-compose', 'pull', *services_names],
            env={'IMAGE_VERSION': tag},
        )
        if proc.returncode:
            make_utils.report_error('Failed pull services')
            exit(1)
    versions = []
    for service in services:
        proc = make_utils.run_process(
            proc_args=[
                'docker-compose',
                'run',
                '--rm',
                '--no-deps',
                service.name,
                'dpkg-query',
                '--showformat=${Version} ',
                '--show',
                *service.packages,
            ],
            env={'IMAGE_VERSION': tag},
            pipe_stdout=True,
        )
        if proc.returncode:
            make_utils.report_error('Failed build service %s' % service.name)
            exit(1)
        versions.append(proc.stdout.split())
    return versions


def tag_latest(services: List[ServiceInfo], tag: str) -> None:
    for service in services:
        tag_image = service.image + ':' + tag
        latest_image = service.image + ':latest'
        proc = make_utils.run_process(
            proc_args=['docker', 'tag', tag_image, latest_image],
            env={'IMAGE_VERSION': tag},
        )
        if proc.returncode:
            make_utils.report_error('Failed push services')
            exit(1)


def validate_versions(
        services: List[ServiceInfo],
        old_versions: List[List[str]],
        new_versions: List[List[str]],
) -> None:
    downgraded: List[str] = []
    for service, old_vers, new_vers in zip(
            services, old_versions, new_versions,
    ):
        for old_version, new_version in zip(old_vers, new_vers):
            if packaging.version.parse(old_version) > packaging.version.parse(
                    new_version,
            ):
                downgraded.append(service.name)
                break

    if downgraded:
        make_utils.report_error(
            'Downgrade services: %s' % ', '.join(downgraded),
        )
        exit(1)


if __name__ == '__main__':
    main()
