#!/bin/env python3

import argparse
import fcntl
import os
import subprocess
import sys
from typing import List
from typing import NamedTuple
from typing import Optional

import get_services


MESSAGE_TYPE_STDERR = 'stderr'
MESSAGE_TYPE_STDOUT = 'stdout'


class MessageInfo(NamedTuple):
    type: str
    text: str


class CustomProcessRunner:
    def __init__(self) -> None:
        self._current_proc: Optional[subprocess.Popen] = None
        self.return_code: Optional[int] = None
        self.is_finished: bool = False
        self.is_started: bool = False

    def start(self, args: List[str]) -> None:
        self._current_proc = subprocess.Popen(args=args)
        self.is_started = True

    def handle(self) -> None:
        if self.is_finished:
            return
        if not self._current_proc:
            self.is_finished = False
            return
        poll = self._current_proc.poll()
        if poll is None:
            # Custom process is still running,
            # keep buffering integration tests messages...
            self.is_finished = False
            return
        if poll:
            # Custom process has failed.
            self.return_code = self._current_proc.returncode
            self.is_finished = True
            return
        # Custom process has completed.
        self.return_code = self._current_proc.returncode
        self.is_finished = True

    def wait(self) -> None:
        if not self._current_proc:
            return
        self._current_proc.wait()
        self.return_code = self._current_proc.returncode


class IntegrationTestsRunner:
    def __init__(self, args: List[str]) -> None:
        self.messages: List[MessageInfo] = []
        self._current_proc: Optional[subprocess.Popen] = None
        self._args: List[str] = args
        self.return_code: Optional[int] = None
        self.is_finished: bool = False
        self.is_started: bool = False

    @staticmethod
    def enable_nonblock(stream):
        flags = fcntl.fcntl(stream, fcntl.F_GETFL)
        fcntl.fcntl(stream, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    def start(self) -> None:
        self._current_proc = subprocess.Popen(
            args=self._args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
        )
        self.enable_nonblock(self._current_proc.stdout)
        self.enable_nonblock(self._current_proc.stderr)
        self.is_started = True
        self.append_message(text=f'Run process with args: \'{self._args}\'\n')

    def append_message(
            self, text: str, type_: str = MESSAGE_TYPE_STDOUT,
    ) -> None:
        self.messages.append(MessageInfo(type=type_, text=text))

    def kill(self) -> None:
        if self._current_proc:
            self._current_proc.kill()
            self._current_proc.wait()
            self.return_code = self._current_proc.returncode

    def handle(self) -> None:
        if self.is_finished:
            return
        if not self._current_proc:
            self.is_finished = False
            return
        assert self._current_proc.stdout is not None
        assert self._current_proc.stderr is not None

        for out_line in self._current_proc.stdout:
            self.append_message(out_line, MESSAGE_TYPE_STDOUT)

        for err_line in self._current_proc.stderr:
            self.append_message(err_line, MESSAGE_TYPE_STDERR)

        if self._current_proc.poll() is not None:
            # process was terminated
            self.return_code = self._current_proc.returncode
            self.is_finished = True
            return

        self.is_finished = False


class OutputBuffer:
    def __init__(self):
        self.messages: List[MessageInfo] = []

    def append_chunk(self, chunk: List[MessageInfo]) -> None:
        self.messages += chunk

    def print_new_messages(self) -> None:
        os.makedirs('_logs', exist_ok=True)
        with open('_logs/tests.log', 'a') as logs_file:
            for message in self.messages:
                if message.type == MESSAGE_TYPE_STDOUT:
                    sys.stdout.write(message.text)
                    sys.stdout.flush()
                elif message.type == MESSAGE_TYPE_STDERR:
                    sys.stderr.write(message.text)
                    sys.stderr.flush()
                logs_file.write(message.text)
        self.messages.clear()


def _get_taxi_projects_set(input_projects):
    return set(
        get_services.get_prefixed_service_name(project)
        for project in input_projects
    )


def is_excluded_project(run_args: List[str]) -> bool:
    print('run_args: ', run_args)
    # exclude backend-cpp
    if 'taxi-tests-cxx' in run_args or 'taxi-build-cxx' in run_args:
        return True
    # exclude backend-py3
    if (
            '--path-to-repo=backend-py3' in run_args
            or '--test-reports-dir=/taxi/pytest-build/test-results' in run_args
    ):
        return True
    # exclude backend-py2
    if (
            'yandex-taxi-build/backend' in run_args
            or 'yandex-taxi-build/arcadia/taxi/docker-integration-tests/'
            'backend' in run_args
    ):
        return True
    return False


def get_integration_tests_command(run_args: List[str]) -> List[str]:
    changed_projects = os.getenv('CHANGED_PROJECTS', '')
    teamcity_build_type = os.getenv('TEAMCITY_BUILD_TYPE', '')

    if not changed_projects and teamcity_build_type != 'release':
        print('CHANGED_PROJECTS is empty. Run all tests.')
        if is_excluded_project(run_args):
            print('Crutch for backend-cpp/py3/py2. Run taxi-tests only.')
            return ['scripts/kill_after_run.sh', 'make', 'run-no-stop']
        return ['make', 'run-all-tests']

    input_projects: List[str] = changed_projects.split()
    if input_projects == ['_empty']:
        return ['echo', 'Run tests without integration tests']

    input_projects_set = _get_taxi_projects_set(input_projects)

    taxi_services = get_services.load_services(
        docker_compose_files=('docker-compose.yml',),
    )
    taxi_integration_test_projects = taxi_services.keys()

    eats_services = get_services.load_services(
        docker_compose_files=('eats/docker-compose.yml',),
    )
    eats_integration_test_projects = eats_services.keys()

    eats_services_affected = bool(
        eats_integration_test_projects & input_projects_set,
    )
    taxi_services_affected = bool(
        taxi_integration_test_projects & input_projects_set,
    )

    if teamcity_build_type == 'release':
        service = os.getenv('BUILD_BRANCH', '')
        if service.startswith('eats-'):
            print('Release tests for eats service')
            return [
                'scripts/run_release_tests.sh',
                'scripts/kill_after_run.sh',
                'make',
                'run-no-stop-eats',
            ]
        print('Release tests for taxi service')
        return [
            'scripts/run_release_tests.sh',
            'scripts/kill_after_run.sh',
            'make',
            'run-no-stop',
        ]

    if eats_services_affected and not taxi_services_affected:
        print('Only eats services were affected')
        return ['scripts/kill_after_run.sh', 'make', 'run-no-stop-eats']

    if not eats_services_affected and taxi_services_affected:
        print('Only taxi services were affected')
        return ['scripts/kill_after_run.sh', 'make', 'run-no-stop']

    if eats_services_affected and taxi_services_affected:
        print('Taxi&Eats services were affected')
        if is_excluded_project(run_args):
            print('Crutch for backend-cpp/py3/py2. Run taxi-tests only.')
            return ['scripts/kill_after_run.sh', 'make', 'run-no-stop']
        return ['make', 'run-all-tests']

    print('No services were affected')
    return ['echo', 'Run tests without integration tests']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'command',
        nargs=argparse.REMAINDER,
        help='Command to run in parallel with integration tests',
    )
    args = parser.parse_args()
    if not args.command:
        parser.error('Custom command not specified')

    # start custom process and integration tests
    custom_proc = CustomProcessRunner()
    custom_proc.start(args=args.command)

    int_tests_args = get_integration_tests_command(args.command)

    # Run integration tests
    output = OutputBuffer()
    tests_run = IntegrationTestsRunner(int_tests_args)
    tests_run.start()

    while True:
        tests_run.handle()
        if tests_run.is_finished:
            output.append_chunk(tests_run.messages)
            tests_run.messages.clear()
            break

        custom_proc.handle()
        if custom_proc.is_finished:
            output.append_chunk(tests_run.messages)
            tests_run.messages.clear()
            output.print_new_messages()

            if custom_proc.return_code != 0:
                tests_run.kill()
                print(
                    'Integration tests aborted due '
                    'to custom command failure.',
                    file=sys.stderr,
                )
                exit(custom_proc.return_code)

    custom_proc.wait()
    output.append_chunk(tests_run.messages)
    tests_run.messages.clear()
    output.print_new_messages()
    exit(custom_proc.return_code or tests_run.return_code)


if __name__ == '__main__':
    main()
