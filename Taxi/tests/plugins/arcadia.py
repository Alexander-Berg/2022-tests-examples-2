# Correct imports will be ensured by Arcadia CI
# pylint: disable=import-error,no-name-in-module,no-member
import argparse
import configparser
import logging
import os
import pathlib
import shutil
from typing import Any
from typing import List
from typing import Optional
from typing import Union

import arc.ci.tests.arcd
import arc.ci.tests.svn2arc
import arc.ci.tests.ydb_util
import pytest
import yatest.common
import yatest.common.process

from taxi_buildagent import utils
from taxi_buildagent.tools.vcs import arc_repo

BINARY_MAP = {
    'arc': 'arc/local/bin/arc',
    'svn': 'contrib/libs/subversion/subversion/svn/svn',
    'svnadmin': 'contrib/libs/subversion/subversion/svnadmin/svnadmin',
    'svn2arc': 'arc/robots/svn/bin/svn2arc',
}

logger = logging.getLogger(__name__)


@pytest.fixture(name='save_arc_traces', autouse=True)
def _save_arc_traces(monkeypatch, home_dir):
    yield

    traces_path = pathlib.Path(home_dir, 'arc/store/.arc/traces')

    if traces_path.exists():
        shutil.copytree(
            str(traces_path), yatest.common.test_output_path('arc_traces'),
        )


@pytest.fixture(name='arcd', scope='session')
def _arcd():
    arcd = arc.ci.tests.arcd.Arcd()
    arcd.init_database()
    return arcd


@pytest.fixture(name='arcadia_builder')
def _arcadia_builder(
        request, monkeypatch, home_dir, commands_mock, tmp_path_factory, arcd,
):
    mounted_dirs: List[pathlib.Path] = []

    name = request.node.callspec.id

    config = configparser.ConfigParser()
    config['user'] = {}
    config['user']['name'] = 'buildfarm'
    config['alias'] = {}
    config['alias']['mount'] = (
        f'mount --ssl 0 --vfs-version 2 --repository {name}'
        f' --server localhost --port {arcd.port}'
    )

    arc_config_dir = pathlib.Path(home_dir, '.config/arc')
    arc_config_dir.mkdir(parents=True, exist_ok=True)
    with (arc_config_dir / 'config').open('w') as config_file:
        config.write(config_file, space_around_delimiters=False)

    monkeypatch.setenv(
        'PATH',
        # /bin is required here because arc uses fusermount under the hood
        os.pathsep.join((yatest.common.binary_path('arc/local/bin'), '/bin')),
        prepend=os.pathsep,
    )
    monkeypatch.setenv('ARC_TOKEN', 'user-robot-taxi-teamcity')
    monkeypatch.setenv('YAV_TOKEN', 'user-robot-taxi-teamcity')
    monkeypatch.setattr(arc_repo.Repo, 'REMOTE_PREFIX', f'{name}/')

    @commands_mock('arc')
    def _arc_mock(args, **kwargs):
        if args[1] == 'mount':
            arc_parser = argparse.ArgumentParser()
            arc_parser.add_argument(
                '--mount', dest='mount_path', type=pathlib.Path,
            )
            parsed, _ = arc_parser.parse_known_args(args)
            mounted_dirs.append(parsed.mount_path)
            args = [arg for arg in args if arg != '--allow-other']
            args.extend(('--override-lazy-checkout', '0'))

        return tuple(args)

    logger.info('Starting Arcd')
    _prepare_db(arcd.ydb, name)
    arcd.run()

    repo_dir = tmp_path_factory.mktemp('arcadia_builder')
    yield ArcadiaBuilder(repo_dir, arcd, name)

    monkeypatch.undo()  # needed for arc unmount to succeed
    for path in mounted_dirs:
        if not path.is_mount():
            continue
        _sh('arc', 'unmount', str(path), cwd=path.parent)

    arcd.stop()


class ArcadiaBuilder:
    def __init__(
            self,
            data_dir: pathlib.Path,
            arcd: arc.ci.tests.arcd.Arcd,
            repo_name: str = 'arcadia_fake',
    ) -> None:
        self._arcd: arc.ci.tests.arcd.Arcd = arcd
        self._repo_name: str = repo_name
        self._data_dir: pathlib.Path = data_dir

        self._svn_dir: pathlib.Path = data_dir / 'repo'
        self._svn_local_dir: pathlib.Path = data_dir / 'working_copy'
        self.root = self._svn_local_dir / 'trunk'

        self.root.mkdir(parents=True)
        self._svn_dir.mkdir(parents=True)
        _sh('svnadmin', 'create', str(self._svn_dir))
        self._svn('checkout', f'file://{self._svn_dir}', '.')

    def add(self, *paths: Union[str, pathlib.Path]) -> None:
        for path in paths:
            full_path = self.root.joinpath(path).resolve()
            assert self._svn_local_dir in full_path.parents
            self._svn(
                'add',
                '--force',
                '--parents',
                str(full_path.relative_to(self._svn_local_dir)),
            )

    def commit(self, message: str, author: str = 'tester') -> None:
        self._svn('commit', '-m', message, '--username', author)

    def __enter__(self) -> 'ArcadiaBuilder':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        svn2arc_store: pathlib.Path = self._data_dir.joinpath('svn2arc_store')
        svn2arc = arc.ci.tests.svn2arc.Svn2Arc(
            endpoint=self._arcd.endpoint, store=svn2arc_store,
        )
        svn2arc.convert_migration(
            path='/trunk',
            branch='trunk',
            svn=str(self._svn_dir),
            repo=self._repo_name,
            monitor_port=0,
        )
        self._arcd.ydb.session.transaction().execute(
            f'UPSERT INTO `repos/arc/{self._repo_name}/refs` (name, default)'
            ' VALUES (\'trunk\', true);',
            commit_tx=True,
        )

    def _svn(self, *args: str, **kwargs) -> Optional[str]:
        return _sh('svn', *args, cwd=self._svn_local_dir, **kwargs)


def _prepare_db(
        ydb: arc.ci.tests.ydb_util.TestYdbSession, repo_name: str,
) -> None:
    # Borrowed from here to support dynamically creating new repos:
    # https://a.yandex-team.ru/arc_vcs/arc/ci/tests/arcd.py?
    # rev=9bdf917c0f8ac851683f6447b07858f95571f895#L46
    database_prefix = f'/{ydb.database}/'
    for table in arc.ci.tests.arcd.PER_REPO_TABLES:
        ydb.create_table(
            table.sql,
            database_prefix
            + table.prefix.format(domain='arc', repo=repo_name),
        )

    ydb.execute_query(
        f"""
        UPSERT INTO repositories (created_timestamp, domain, format, name)
        VALUES (CAST(Yql::Now() AS Uint64), "arc", "vcs", "{repo_name}");
        """,
        ydb.prefix,
    )
    ydb.execute_query(
        """
        UPSERT INTO outstaff_users (login, external, robot)
        VALUES
        ('buildfarm', False, False),
        ('tester', False, False),
        ('svn2arc_test', False, True),
        ('robot-taxi-teamcity', False, True);
        """,
        '/'.join((ydb.prefix, 'arc', repo_name)),
    )

    ydb.execute_query(
        """
        UPSERT INTO acl (login, prefix, access_flags)
        VALUES
        ('svn2arc_test', 'migrations/', 0b11111),
        ('svn2arc_test', 'trunk', 0b11111),
        ('robot-taxi-teamcity', 'releases/', 0b11111),
        ('robot-taxi-teamcity', 'users/', 0b11111),
        ('robot-taxi-teamcity', 'tags/users/robot-taxi-teamcity/', 0b11111);
        """,
        '/'.join((ydb.prefix, 'arc', repo_name)),
    )


def _sh(binary: str, *args: str, **kwargs) -> Any:
    try:
        mapped_binary = yatest.common.binary_path(BINARY_MAP[binary])
    except KeyError:
        raise ValueError(f'Command {binary} is not mapped to Arcadia path')

    return utils.sh([mapped_binary, *args], **kwargs)
