import json
import os
import subprocess
import sys
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Sequence

import teamcity_utils


DEFAULT_COMPOSE_FILE = 'docker-compose.yml'


class BadDockerInfo(NamedTuple):
    unhealthy_containers: List[str]
    non_running_containers: List[str]

    def __str__(self):
        msg_parts = []
        if self.unhealthy_containers:
            msg_parts.append('Unhealthy:')
            msg_parts.extend(self.unhealthy_containers)
        if self.non_running_containers:
            msg_parts.append('Non-running:')
            msg_parts.extend(self.non_running_containers)
        return ' '.join(msg_parts)


def run_process(
        *,
        proc_args: Sequence[str],
        pipe_stdout: bool = False,
        pipe_stderr: bool = False,
        env: Dict[str, str] = None,
        stderr_to_stdout: bool = False,
        **kwargs,
) -> subprocess.CompletedProcess:
    if env is not None:
        env = {**os.environ, **env}
    if pipe_stderr and stderr_to_stdout:
        raise ValueError(
            'pipe_stderr and stderr_to_stdout arguments are '
            'mutually exclusive.',
        )
    pipe = None
    if pipe_stderr:
        pipe = subprocess.PIPE
    if stderr_to_stdout:
        pipe = subprocess.STDOUT
    proc = subprocess.run(
        args=proc_args,
        stdout=subprocess.PIPE if pipe_stdout else None,
        stderr=pipe,
        encoding='utf-8',
        env=env,
        **kwargs,
    )

    if proc.returncode:
        print('Error running process: ' + ' '.join(proc.args), file=sys.stderr)
    return proc


def run_docker_compose(
        docker_files: Sequence[str], proc_args: Sequence[str], **kwargs,
) -> subprocess.CompletedProcess:
    return run_process(
        proc_args=[
            'docker-compose',
            '--project-directory',
            os.getcwd(),
            *[arg for x in docker_files for arg in ('-f', x)],
            *proc_args,
        ],
        **kwargs,
    )


def run_docker(
        proc_args: Sequence[str], **kwargs,
) -> subprocess.CompletedProcess:
    return run_process(proc_args=['docker', *proc_args], **kwargs)


def report_error(message):
    if os.environ.get('TEAMCITY_VERSION'):
        teamcity_utils.report_build_problem(message)
    else:
        print(message, file=sys.stderr)


def report_statistic(key, value):
    if os.environ.get('TEAMCITY_VERSION'):
        teamcity_utils.report_build_statistic(key, value)


def get_docker_container_ids(docker_files: Sequence[str]):
    proc = run_docker_compose(
        docker_files=docker_files,
        proc_args=['ps', '--quiet'],
        pipe_stdout=True,
    )

    if proc.returncode:
        print('Error getting docker service ids.', file=sys.stderr)
        return None

    ids = []
    for output_string in proc.stdout.split('\n'):
        container_id = output_string.strip()
        if container_id:
            ids.append(container_id)
    return ids


def get_docker_container_info(container_id):
    proc = run_docker(proc_args=['inspect', container_id], pipe_stdout=True)

    if proc.returncode:
        print('Error getting docker container info.', file=sys.stderr)
        return None

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exception:
        print(
            'Error parsing docker container info:', exception, file=sys.stderr,
        )
    return None


def is_docker_container_running(container_info):
    state_info = container_info[0]['State']
    return state_info['Status'] == 'running'


def is_docker_container_unhealthy(container_info):
    state_info = container_info[0]['State']
    return state_info.get('Health', {}).get('Status') == 'unhealthy'


def get_docker_container_name(container_info):
    return container_info[0]['Name']


def get_bad_docker_info():
    """
    Returns BadDockerInfo object with info on non-running and
    unhealthy containers. Returns None if no such containers found.
    """
    cont_ids = get_docker_container_ids([DEFAULT_COMPOSE_FILE])
    if cont_ids is None:
        return None

    result = BadDockerInfo(non_running_containers=[], unhealthy_containers=[])

    for cont_id in cont_ids:
        cont_info = get_docker_container_info(cont_id)
        if cont_info is None:
            return None

        cont_name = get_docker_container_name(cont_info)

        # Check if unhealthy first
        if is_docker_container_unhealthy(cont_info):
            result.unhealthy_containers.append(cont_name)
        elif not is_docker_container_running(cont_info):
            result.non_running_containers.append(cont_name)

    if result.non_running_containers or result.unhealthy_containers:
        return result

    return None
