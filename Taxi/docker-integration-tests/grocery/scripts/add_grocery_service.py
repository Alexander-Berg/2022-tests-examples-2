#!/usr/bin/env python3

import argparse
import json
import pathlib
import re
import stat
from typing import List
from typing import Optional

import jinja2
import yaml


CUR_DIR = pathlib.Path(__file__).parent
ROOT_DIR = CUR_DIR.parent.parent
COMPOSE_PATH = ROOT_DIR / 'grocery' / 'grocery.yml'
TEMPLATE_DIR = CUR_DIR / 'templates'
RUN_TEMPLATE_DIR = ROOT_DIR / 'scripts' / 'templates'

COMPOSE_SERVICE_ENTRY_TEMPLATE = (
    TEMPLATE_DIR / 'compose-grocery-service-entry.jinja'
)
COMPOSE_DEPENDS_ENTRY_TEMPLATE = (
    TEMPLATE_DIR / 'compose-grocery-depends-entry.jinja'
)
USERVICES_RUN_SCRIPT_TEMPLATE = RUN_TEMPLATE_DIR / 'uservices-run-script.jinja'

RUN_SCRIPT_DIR = ROOT_DIR / 'volumes' / 'run'
WAIT_SERVICES_PATH = ROOT_DIR / 'volumes' / 'tools' / 'wait_services.sh'
SECDIST_CONFIG_PATH = ROOT_DIR / 'volumes' / 'taxi-secdist' / 'taxi.json'
DB_CONFIG_PATH = (
    ROOT_DIR / 'volumes' / 'bootstrap_db' / 'db_data' / 'db_config.json'
)

GROCERY_PROXY_PATTERN = re.compile(
    r'^(\s*)all-grocery-services: &grocery-base\n'
    r'((.+\n)+?)((\s*)depends_on:\n)',
    flags=re.MULTILINE,
)
WAIT_SERVICE_STARTED = re.compile(r'^(\s*)--run echo .*$', flags=re.MULTILINE)

USERVICES = 'uservices'


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('service', help='Service name')
    parser.add_argument('tvm_id', help='Service TVM id')
    parser.add_argument(
        '--with-pg', action='store_true', help='Does service have postgres db',
    )
    # TODO add compose file
    return parser.parse_args(argv)


def add_service_to_int_tests(args: argparse.Namespace) -> None:
    validate_service_absence(args.service)

    add_entries_to_compose_yaml(args.service)
    add_run_script(args.service)
    # add_wait_service(args.service)
    add_entry_to_tvm_config(args.service, args.tvm_id)
    add_entry_to_db_config(args.service, args.tvm_id)
    add_entry_to_pg_config(args.service, args.with_pg)


def validate_service_absence(service: str) -> None:
    with COMPOSE_PATH.open() as f_in:
        docker_compose_yaml = yaml.load(f_in, Loader=yaml.SafeLoader)
        assert service not in docker_compose_yaml['services'], (
            '%s service is already in docker-compose.yaml!' % service
        )


def add_entry_to_pg_config(service: str, with_pg: bool) -> None:
    if not with_pg:
        return

    pg_service_name = service.replace('-', '_')
    entry = [
        {
            'hosts': [
                'host=pgaas.mail.yandex.net port=5432 '
                + f'user=user password=password dbname={pg_service_name}',
            ],
            'shard_number': 0,
        },
    ]

    secdist_text = SECDIST_CONFIG_PATH.read_text()
    secdist_json = json.loads(secdist_text)

    secdist_json['postgresql_settings']['databases'][pg_service_name] = entry
    secdist_text = json.dumps(secdist_json)

    SECDIST_CONFIG_PATH.write_text(secdist_text)


def add_entry_to_tvm_config(service: str, tvm_id: str) -> None:
    entry = {'id': int(tvm_id), 'secret': 'secret'}

    secdist_text = SECDIST_CONFIG_PATH.read_text()
    secdist_json = json.loads(secdist_text)

    secdist_json['settings_override']['TVM_SERVICES'][service] = entry
    secdist_text = json.dumps(secdist_json)

    SECDIST_CONFIG_PATH.write_text(secdist_text)


def add_entry_to_db_config(service: str, tvm_id: str) -> None:
    db_config_text = DB_CONFIG_PATH.read_text()
    db_config_json = json.loads(db_config_text)

    for entry in db_config_json:
        if entry['_id'] == 'TVM_SERVICES':
            entry['v'][service] = int(tvm_id)
    db_config_text = json.dumps(db_config_json)

    DB_CONFIG_PATH.write_text(db_config_text)


def add_entries_to_compose_yaml(service: str) -> None:
    service_entry = form_compose_entry(COMPOSE_SERVICE_ENTRY_TEMPLATE, service)
    depends_entry = form_compose_entry(COMPOSE_DEPENDS_ENTRY_TEMPLATE, service)
    insert_entry_to_compose_yaml(service_entry, depends_entry)


def form_compose_entry(template_path: pathlib.Path, service: str) -> str:
    template = jinja2.Template(template_path.read_text())
    pure_service = form_pure_service(service)
    taxi_service = form_taxi_service(service)
    underscored_taxi_service = taxi_service.replace('-', '_')
    taxi_web_service = form_web_service(taxi_service)

    service_entry = template.render(
        taxi_service=taxi_service,
        pure_service=pure_service,
        taxi_web_service=taxi_web_service,
        repo=USERVICES,
        rtc=True,
        underscored_taxi_service=underscored_taxi_service,
    )
    return service_entry


def insert_entry_to_compose_yaml(
        service_entry: str, depends_entry: str,
) -> None:
    compose_content = COMPOSE_PATH.read_text()

    updated_compose_content = re.sub(
        GROCERY_PROXY_PATTERN,
        lambda matchobj: service_entry + matchobj.group(0) + depends_entry,
        compose_content,
    )
    COMPOSE_PATH.write_text(updated_compose_content)


def add_run_script(service: str) -> None:
    underscored_service = service.replace('-', '_')
    underscored_upper_service = underscored_service.upper()
    taxi_service = form_taxi_service(service)
    taxi_web_service = form_web_service(taxi_service)
    underscored_taxi_service = taxi_service.replace('-', '_')
    underscored_taxi_web_service = taxi_web_service.replace('-', '_')

    template_filename = USERVICES_RUN_SCRIPT_TEMPLATE

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


def form_web_service(service: str) -> str:
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
