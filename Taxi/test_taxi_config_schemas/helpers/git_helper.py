import asyncio
import json
import logging
import os
import typing
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import mypy_extensions

from taxi_config_schemas import config_models
from taxi_config_schemas.repo_manager import definitions as const


logger = logging.getLogger(__name__)


async def git(path: str, command: str, *args) -> Tuple[str, str]:
    exec_args = [const.GIT_COMMAND]
    exec_args.extend(['-C', path])
    exec_args.append(command)
    exec_args.extend(args)
    try:
        process = await asyncio.create_subprocess_exec(
            *exec_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
    except Exception as exc:
        logger.exception('subprocess crashes for %s: exception: %s', args, exc)
        raise exc
    return stdout.decode('utf-8'), stderr.decode('utf-8')


async def init_git(repo_root: str):
    await git(repo_root, 'init')
    await git(repo_root, 'config', 'user.email', 'ya@ya.ru')
    await git(repo_root, 'checkout', '-b', 'develop')


async def _get_last_commit_hash(repo_root: str) -> str:
    raw_commit_hash = await git(repo_root, 'rev-parse', 'HEAD')
    commit_hash, _ = raw_commit_hash
    commit_hash = commit_hash.strip()
    return commit_hash


class CommonDefinition(mypy_extensions.TypedDict):
    directory: str
    name: str
    schema: Dict


class GitArg(typing.NamedTuple):
    commit_message: Tuple[str, str]
    config: Optional[config_models.BaseConfig] = None
    common_definition: Optional[CommonDefinition] = None


async def create_git_repos(
        repo_root: str,
        remote_repo: str,
        skip_commits: int,
        args: List[GitArg],
) -> Tuple[str, str]:
    await init_git(remote_repo)

    await git(remote_repo, 'config', 'user.name', 'default_user')
    configs_root = os.path.join(
        remote_repo, 'schemas', 'configs', 'declarations', 'default',
    )
    if not os.path.exists(configs_root):
        os.makedirs(configs_root)
    full_file_name = os.path.join(configs_root, 'default.yaml')
    with open(full_file_name, 'w') as fp:
        json.dump({}, fp)
    await git(remote_repo, 'add', full_file_name)
    await git(remote_repo, 'commit', '-m', 'init commit')

    need_run = True
    for index, arg in enumerate(args):
        full_file_name = ''
        body: Dict = {}
        if arg.common_definition:
            full_file_name, body = _prepare_definition_file(remote_repo, arg)
        else:
            full_file_name, body = _prepare_config_file(remote_repo, arg)
        with open(full_file_name, 'w') as fp:
            json.dump(body, fp, sort_keys=True)

        user_name, message = arg.commit_message
        await git(remote_repo, 'config', 'user.name', user_name)
        await git(remote_repo, 'add', full_file_name)
        await git(remote_repo, 'commit', '-m', message)
        if (index + 1 < skip_commits) or not need_run:
            continue
        need_run = False
        first_hash = await _get_last_commit_hash(remote_repo)

    last_hash = await _get_last_commit_hash(remote_repo)

    repo_root = os.path.join(repo_root, 'schemas')
    os.makedirs(repo_root)
    await init_git(repo_root)
    await git(repo_root, 'remote', 'add', 'origin', f'file://{remote_repo}')

    return first_hash, last_hash


def _prepare_definition_file(remote_repo, arg: GitArg) -> Tuple[str, Dict]:
    assert (
        arg.common_definition
    ), 'Bad test setup: no required common definitions'
    directory = arg.common_definition['directory']
    def_root = os.path.join(
        remote_repo, 'schemas', 'configs', 'definitions', directory,
    )
    if not os.path.exists(def_root):
        os.makedirs(def_root)
    def_name = arg.common_definition['name']
    full_file_name = os.path.join(def_root, def_name + '.yaml')
    body = arg.common_definition['schema']
    return full_file_name, body


def _prepare_config_file(remote_repo, arg: GitArg) -> Tuple[str, Dict]:
    assert arg.config, 'Bad test setup: no required config'
    config = arg.config
    configs_root = os.path.join(
        remote_repo, 'schemas', 'configs', 'declarations', config.group,
    )
    if not os.path.exists(configs_root):
        os.makedirs(configs_root)
    full_file_name = os.path.join(configs_root, config.name + '.yaml')
    body = config.serialize_for_schema()
    return full_file_name, body
