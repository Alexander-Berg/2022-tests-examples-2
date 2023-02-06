#!/usr/bin/env python3

import argparse
import pathlib
import re
import stat
from typing import List
from typing import Optional

import jinja2
import yaml


CUR_DIR = pathlib.Path(__file__).parent
ROOT_DIR = CUR_DIR.parent
COMPOSE_PATH = ROOT_DIR / 'docker-compose.yml'
TEMPLATE_DIR = CUR_DIR / 'templates'

COMPOSE_SERVICE_ENTRY_TEMPLATE = TEMPLATE_DIR / 'compose-service-entry.jinja'
COMPOSE_DEPENDS_ENTRY_TEMPLATE = TEMPLATE_DIR / 'compose-depends-entry.jinja'
USERVICES_RUN_SCRIPT_TEMPLATE = TEMPLATE_DIR / 'uservices-run-script.jinja'
PY3_RUN_SCRIPT_TEMPLATE = TEMPLATE_DIR / 'backend-py3-run-script.jinja'

RUN_SCRIPT_DIR = ROOT_DIR / 'volumes' / 'run'
WAIT_SERVICES_PATH = ROOT_DIR / 'volumes' / 'tools' / 'wait_services.sh'

TAXI_TEST_PATTERN = re.compile(
    r'^(\s*)taxi-tests:\n((.+\n)+?)((\s*)depends_on:\n)', flags=re.MULTILINE,
)
WAIT_SERVICE_STARTED = re.compile(r'^(\s*)--run echo .*$', flags=re.MULTILINE)

USERVICES = 'uservices'
BACKEND_PY3 = 'backend-py3'


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('service', help='Service name')
    parser.add_argument(
        'repo', help='Repository name', choices=(USERVICES, BACKEND_PY3),
    )
    parser.add_argument('--rtc', action='store_true', help='Is rtc service')
    # TODO add compose file
    return parser.parse_args(argv)


def add_service_to_int_tests(args: argparse.Namespace) -> None:
    validate_service_absence(args.service)

    add_entries_to_compose_yaml(args.service, args.repo, args.rtc)
    add_run_script(args.service, args.repo)
    add_wait_service(args.service)


def validate_service_absence(service: str) -> None:
    taxi_service = form_taxi_service(service)
    with COMPOSE_PATH.open() as f_in:
        docker_compose_yaml = yaml.load(f_in, Loader=yaml.SafeLoader)
        assert taxi_service not in docker_compose_yaml['services'], (
            '%s service is already in docker-compose.yaml!' % service
        )


def add_entries_to_compose_yaml(service: str, repo: str, rtc: bool) -> None:
    service_entry = form_compose_entry(
        COMPOSE_SERVICE_ENTRY_TEMPLATE, service, repo, rtc,
    )
    depends_entry = form_compose_entry(
        COMPOSE_DEPENDS_ENTRY_TEMPLATE, service, repo, rtc,
    )
    insert_entry_to_compose_yaml(service_entry, depends_entry)


def form_compose_entry(
        template_path: pathlib.Path, service: str, repo: str, rtc: bool,
) -> str:
    template = jinja2.Template(template_path.read_text())
    pure_service = form_pure_service(service)
    taxi_service = form_taxi_service(service)
    underscored_taxi_service = taxi_service.replace('-', '_')
    taxi_web_service = form_web_service(taxi_service, repo)

    service_entry = template.render(
        taxi_service=taxi_service,
        pure_service=pure_service,
        taxi_web_service=taxi_web_service,
        repo=repo,
        rtc=rtc,
        underscored_taxi_service=underscored_taxi_service,
    )
    return service_entry


def insert_entry_to_compose_yaml(
        service_entry: str, depends_entry: str,
) -> None:
    compose_content = COMPOSE_PATH.read_text()

    updated_compose_content = re.sub(
        TAXI_TEST_PATTERN,
        lambda matchobj: service_entry + matchobj.group(0) + depends_entry,
        compose_content,
    )
    COMPOSE_PATH.write_text(updated_compose_content)


def add_run_script(service: str, repo: str) -> None:
    underscored_service = service.replace('-', '_')
    underscored_upper_service = underscored_service.upper()
    taxi_service = form_taxi_service(service)
    taxi_web_service = form_web_service(taxi_service, repo)

    if repo == USERVICES:
        template_filename = USERVICES_RUN_SCRIPT_TEMPLATE
    elif repo == BACKEND_PY3:
        template_filename = PY3_RUN_SCRIPT_TEMPLATE
    else:
        assert False, 'Repository %s is not supported for this script!' % repo
    underscored_taxi_service = taxi_service.replace('-', '_')
    underscored_taxi_web_service = taxi_web_service.replace('-', '_')

    run_script_content = template_filename.read_text()
    template = jinja2.Template(run_script_content)
    filled_run_script_content = template.render(
        service=service,
        underscored_service=underscored_service,
        underscored_upper_service=underscored_upper_service,
        taxi_service=taxi_service,
        underscored_taxi_service=underscored_taxi_service,
        underscored_taxi_web_service=underscored_taxi_web_service,
        taxi_web_service=taxi_web_service,
    )

    pure_service = form_pure_service(service)
    run_script_path = RUN_SCRIPT_DIR / (pure_service + '.sh')
    run_script_path.write_text(filled_run_script_content)

    mode = run_script_path.stat()
    new_permissions = mode.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
    run_script_path.chmod(new_permissions)


def form_pure_service(service: str) -> str:
    return service.split('taxi-')[-1]


def form_taxi_service(service: str) -> str:
    if service.startswith('taxi'):
        return service
    return 'taxi-' + service


def form_web_service(service: str, repo: str) -> str:
    if repo == BACKEND_PY3:
        return service + '-web'
    return service


def add_wait_service(service: str) -> None:
    pure_service = form_pure_service(service)
    hostname_entry = (
        '        http://' + pure_service + '.taxi.yandex.net/ping \\\n'
    )
    wait_content = WAIT_SERVICES_PATH.read_text()
    updated_wait_content = re.sub(
        WAIT_SERVICE_STARTED,
        lambda matchobj: hostname_entry + matchobj.group(0),
        wait_content,
    )
    WAIT_SERVICES_PATH.write_text(updated_wait_content)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    add_service_to_int_tests(args)


if __name__ == '__main__':
    main()
