import os
import pathlib
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional

import git
import pytest

import git_checkout
from taxi_buildagent import utils


class Params(NamedTuple):
    url: str
    expected_branch: Optional[str]
    expected_files: List[str]
    branch: Optional[str] = None
    commit: Optional[str] = None
    commit_not_found: bool = False
    merge_with_develop: bool = False
    no_submodules: bool = False
    break_mirror: bool = False
    non_empty_checkout_dir: bool = False
    teamcity_build_fail: Optional[Dict[str, Any]] = None
    fail_type: Optional[Exception] = None
    second: Optional['Params'] = None  # type: ignore


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                url='git@github.yandex-team.ru:taxi/uservices.git',
                expected_branch='develop',
                expected_files=['c', 'userver/b', 'userver/codegen/a'],
            ),
            id='no params',
        ),
        pytest.param(
            Params(
                url='git@github.yandex-team.ru:taxi/uservices.git',
                branch='refs/pulls/3333/head',
                commit='uservices_b',
                expected_branch=None,
                expected_files=['b', 'userver/a'],
            ),
            id='pr branch',
        ),
        pytest.param(
            Params(
                url='git@github.yandex-team.ru:taxi/uservices.git',
                branch='refs/pulls/3333/head',
                commit='lost',
                commit_not_found=True,
                expected_branch=None,
                expected_files=['b', 'userver/a'],
                teamcity_build_fail={
                    'description': '(\'Commit `lost` not found\', None)',
                    'identity': None,
                },
            ),
            id='pr commit not found',
        ),
        pytest.param(
            Params(
                url='git@github.yandex-team.ru:taxi/uservices.git',
                branch='refs/pulls/3333/head',
                commit='uservices_b',
                merge_with_develop=True,
                expected_branch=None,
                expected_files=['c', 'userver/b', 'userver/codegen/a'],
            ),
            id='pr branch merge',
        ),
        pytest.param(
            Params(
                url='git@github.yandex-team.ru:taxi/uservices.git',
                branch='refs/pulls/3333/head',
                commit='uservices_b',
                merge_with_develop=True,
                no_submodules=True,
                expected_branch=None,
                expected_files=['c', 'userver/'],
            ),
            id='pr branch merge no submodules',
        ),
        pytest.param(
            Params(
                url='git@github.yandex-team.ru:taxi/uservices.git',
                branch='refs/heads/master',
                expected_branch='master',
                expected_files=['a'],
            ),
            id='master',
        ),
        pytest.param(
            Params(
                url='git@github.yandex-team.ru:taxi/uservices.git',
                branch='refs/heads/develop',
                commit='uservices_a',
                expected_branch='develop',
                expected_files=['a'],
            ),
            id='develop-a',
        ),
        pytest.param(
            Params(
                url='git@github.yandex-team.ru:taxi/uservices.git',
                branch='refs/heads/develop',
                commit='uservices_b',
                expected_branch='develop',
                expected_files=['b', 'userver/a'],
            ),
            id='develop-b',
        ),
        pytest.param(
            Params(
                url='git@github.yandex-team.ru:taxi/uservices.git',
                branch='refs/heads/develop',
                commit='uservices_c',
                expected_branch='develop',
                expected_files=['c', 'userver/b', 'userver/codegen/a'],
            ),
            id='develop-c',
        ),
        pytest.param(
            Params(
                url='git@github.yandex-team.ru:taxi/userver.git',
                branch='refs/heads/develop',
                commit='userver_b',
                expected_branch='develop',
                expected_files=['b', 'codegen/a'],
            ),
            id='userver develop-b',
        ),
        pytest.param(
            Params(
                url='git@github.yandex-team.ru:taxi/uservices.git',
                branch='refs/heads/develop',
                commit='uservices_b',
                merge_with_develop=True,
                expected_branch='develop',
                expected_files=['c', 'userver/b', 'userver/codegen/a'],
            ),
            id='develop-b merge',
        ),
        pytest.param(
            Params(
                url='git@github.yandex-team.ru:taxi/uservices.git',
                expected_branch='develop',
                expected_files=['c', 'userver/b', 'userver/codegen/a'],
                second=Params(
                    url='git@github.yandex-team.ru:taxi/uservices.git',
                    expected_branch='develop',
                    expected_files=[
                        'd',
                        'userver/c',
                        'userver/codegen/b',
                        'userver/codegen/dashboards/a',
                    ],
                ),
            ),
            id='second no params',
        ),
        pytest.param(
            Params(
                url='git@github.yandex-team.ru:taxi/uservices.git',
                expected_branch='develop',
                expected_files=['c', 'userver/b', 'userver/codegen/a'],
                second=Params(
                    url='git@github.yandex-team.ru:taxi/uservices.git',
                    branch='refs/heads/develop',
                    expected_branch='develop',
                    expected_files=[
                        'd',
                        'userver/c',
                        'userver/codegen/b',
                        'userver/codegen/dashboards/a',
                    ],
                ),
            ),
            id='second develop',
        ),
        pytest.param(
            Params(
                url='git@github.yandex-team.ru:taxi/uservices.git',
                expected_branch='develop',
                expected_files=['c', 'userver/b', 'userver/codegen/a'],
                second=Params(
                    url='git@github.yandex-team.ru:taxi/uservices.git',
                    branch='refs/heads/develop',
                    expected_branch='develop',
                    break_mirror=True,
                    expected_files=[
                        'd',
                        'userver/c',
                        'userver/codegen/b',
                        'userver/codegen/dashboards/a',
                    ],
                ),
            ),
            id='break mirror',
        ),
        pytest.param(
            Params(
                url='git@github.yandex-team.ru:taxi/uservices.git',
                expected_branch='develop',
                expected_files=['c', 'userver/b', 'userver/codegen/a'],
                second=Params(
                    url='git@github.yandex-team.ru:taxi/uservices.git',
                    commit='uservices_pr',
                    branch='refs/heads/develop',
                    expected_branch='develop',
                    expected_files=[
                        'c',
                        'pr',
                        'ext/e',
                        'ext/ext/a',
                        'dashboards/a',
                        'usrv_pr/b',
                        'usrv_pr/codegen/a',
                    ],
                ),
            ),
            id='second develop pr',
        ),
        pytest.param(
            Params(
                url='git@github.yandex-team.ru:taxi/uservices.git',
                expected_branch='develop',
                expected_files=['c', 'userver/b', 'userver/codegen/a'],
                second=Params(
                    url='git@github.yandex-team.ru:taxi/uservices.git',
                    commit='uservices_pr',
                    branch='refs/pulls/111/head',
                    expected_branch=None,
                    expected_files=[
                        'c',
                        'ext/e',
                        'ext/ext/a',
                        'pr',
                        'dashboards/a',
                        'usrv_pr/b',
                        'usrv_pr/codegen/a',
                    ],
                ),
            ),
            id='second pr',
        ),
        pytest.param(
            Params(
                url='git@github.yandex-team.ru:taxi/uservices.git',
                expected_branch='develop',
                expected_files=['c', 'userver/b', 'userver/codegen/a'],
                second=Params(
                    url='git@github.yandex-team.ru:taxi/uservices.git',
                    commit='uservices_pr',
                    branch='refs/pulls/111/head',
                    expected_branch=None,
                    merge_with_develop=True,
                    expected_files=[
                        'd',
                        'ext/e',
                        'ext/ext/a',
                        'pr',
                        'dashboards/a',
                        'usrv_pr/c',
                        'usrv_pr/codegen/b',
                        'usrv_pr/codegen/dashboards/a',
                    ],
                ),
            ),
            id='second pr merge',
        ),
        pytest.param(
            Params(
                url='',
                expected_branch=None,
                expected_files=[],
                teamcity_build_fail={
                    'description': (
                        'Failed to perform checkout on agent: '
                        '(\'Failed to perform cleanup %s '
                        'with following exception: FileNotFoundError, '
                        'fail\', None)'
                    ),
                    'identity': None,
                },
                fail_type=FileNotFoundError('fail'),
                non_empty_checkout_dir=True,
            ),
            id='fail on non-empty checkout dir',
        ),
        pytest.param(
            Params(
                url='git@github.yandex-team.ru:taxi/uservices.git',
                expected_branch='develop',
                expected_files=['c', 'userver/b', 'userver/codegen/a'],
                fail_type=PermissionError('Permission denied: ...'),
                non_empty_checkout_dir=True,
            ),
            id='sudo clean checkout dir',
        ),
        pytest.param(
            Params(
                url='git@github.yandex-team.ru:taxi/eda.git',
                expected_branch='develop',
                expected_files=['a'],
                second=Params(
                    url='git@bb.yandex-team.ru:taxi/eda.git',
                    expected_branch='develop',
                    expected_files=['a', 'new_file'],
                ),
            ),
            id='bb repo migration',
        ),
    ],
)
def test_git_checkout(
        params: Params,
        commands_mock,
        home_dir,
        monkeypatch,
        tmpdir,
        patch,
        repos_dir,
        teamcity_report_problems,
):
    dest_dir = pathlib.Path(tmpdir.mkdir('dest'))
    git_config_file = home_dir / '.gitconfig'
    if params.non_empty_checkout_dir:

        monkeypatch.setattr('taxi_buildagent.utils.BUILD_DIR', dest_dir)

        @patch('taxi_buildagent.utils._clean_dir_impl')
        def clean_dir_mock(path):
            raise params.fail_type

        @commands_mock('sudo')
        def sudo(args, **kwargs):
            return ''

    else:
        clean_dir_mock = None
        sudo = None
    git_config = git.GitConfigParser(str(git_config_file), read_only=False)
    git_config.set_value('user', 'name', 'alberist')
    git_config.set_value('user', 'email', 'alberist@yandex-team.ru')
    commit_by_name = {}

    def create_repo(name, web_service='github', *, dirname=None):
        repo_dir = pathlib.Path(tmpdir.mkdir(dirname or name))
        git_repo = git.Repo.init(repo_dir)
        (repo_dir / 'a').touch()
        git_repo.index.add(['a'])
        commit_by_name['%s_a' % name] = git_repo.index.commit('a')
        git_repo.create_head('develop').checkout()
        git_config.set_value(
            'url "%s"' % repo_dir,
            'insteadOf',
            'git@%s.yandex-team.ru:taxi/%s.git' % (web_service, name),
        )
        return repo_dir, git_repo

    def run(params, clean=True):
        args = []
        if params.branch is not None:
            args.append('--branch=' + params.branch)
        if params.commit is not None:
            commit = params.commit
            if commit in commit_by_name:
                commit = commit_by_name[commit].hexsha
            args.append('--commit=' + commit)
        if params.merge_with_develop:
            args.append('--merge-with-develop')
        if clean:
            args.append('--clean')
        if params.no_submodules:
            args.append('--no-submodules')
        git_checkout.main([*args, params.url, str(dest_dir)])

        dest_files = set()

        for root, dirs, files in os.walk(dest_dir):
            if not dirs and not files:
                dest_files.add(
                    pathlib.Path(root).relative_to(dest_dir).as_posix()
                    + os.sep,
                )
                continue
            try:
                dirs.remove('.git')
            except ValueError:
                files.remove('.git')
            repo = git.Repo(root)
            assert not repo.untracked_files
            assert not repo.index.diff(None)
            assert not repo.index.diff(repo.head.commit)
            dest_files.update(
                pathlib.Path(root, file).relative_to(dest_dir).as_posix()
                for file in files
                if file != '.gitmodules'
            )

        repo = git.Repo(str(dest_dir))
        if params.expected_branch is None:
            with pytest.raises(TypeError):
                assert not repo.active_branch
        else:
            assert repo.active_branch.name == params.expected_branch
        assert set(params.expected_files) == dest_files

    uservices_dir, uservices_repo = create_repo('uservices')
    userver_dir, userver_repo = create_repo('userver')
    codegen_dir, codegen_repo = create_repo('codegen')
    create_repo('eda', dirname='eda_original')
    migrated_eda_dir, migrated_eda_repo = create_repo('eda', 'bb')
    (migrated_eda_dir / 'new_file').touch()
    migrated_eda_repo.index.add(['new_file'])
    migrated_eda_repo.index.commit('b')

    (uservices_dir / 'b').touch()
    uservices_repo.index.add(['b'])
    uservices_repo.index.remove('a', working_tree=True)
    userver_submodule = uservices_repo.create_submodule(
        'userver', 'userver', 'git@github.yandex-team.ru:taxi/userver.git',
    )
    commit_by_name['uservices_b'] = uservices_repo.index.commit('b')

    (userver_dir / 'b').touch()
    userver_repo.index.remove('a', working_tree=True)
    userver_repo.index.add(['b'])
    codegen_submodule = userver_repo.create_submodule(
        'codegen', 'codegen', 'git@github.yandex-team.ru:taxi/codegen.git',
    )
    commit_by_name['userver_b'] = userver_repo.index.commit('b')

    (uservices_dir / 'c').touch()
    uservices_repo.index.add(['c'])
    uservices_repo.index.remove('b', working_tree=True)
    userver_submodule.update(to_latest_revision=True, recursive=True)
    uservices_repo.git.add(userver_submodule.path)
    commit_by_name['uservices_c'] = uservices_repo.index.commit('c')

    if params.commit_not_found:
        with pytest.raises(SystemExit):
            run(params)
        assert teamcity_report_problems.calls == [params.teamcity_build_fail]
    elif params.teamcity_build_fail:
        with pytest.raises(SystemExit) as wrapped_exc:
            run(params)
        assert wrapped_exc.value.code == 2
        params.teamcity_build_fail['description'] %= dest_dir.absolute()
        assert teamcity_report_problems.calls == [params.teamcity_build_fail]
    else:
        run(params)

    if params.non_empty_checkout_dir:
        assert clean_dir_mock is not None
        assert clean_dir_mock.calls == [dict(path=dest_dir)]
        if params.fail_type.__class__.__name__ == 'PermissionError':
            calls = sudo.calls
            assert len(calls) == 1
            assert calls[0]['args'] == [
                'sudo',
                '/usr/bin/find',
                str(utils.BUILD_DIR),
                '-mindepth',
                '1',
                '-delete',
            ]

    if not params.second:
        return

    create_repo('taxi-ext')
    ext_dir = pathlib.Path(tmpdir.mkdir('ext'))
    ext_repo = git.Repo.init(ext_dir)
    (ext_dir / 'e').touch()
    ext_repo.index.add(['e'])
    ext_repo.create_submodule(
        'ext', 'ext', 'git@github.yandex-team.ru:taxi/taxi-ext.git',
    )
    commit_by_name['taxi-ext_a'] = ext_repo.index.commit('a')
    ext_repo.create_head('develop').checkout()
    git_config.set_value(
        'url "%s"' % ext_dir, 'insteadOf', 'git@github.ru:ext/repo.git',
    )

    create_repo('dashboards')

    uservices_repo.git.checkout(uservices_repo.commit().hexsha)
    (uservices_dir / 'pr').touch()
    uservices_repo.index.add(['pr'])
    uservices_repo.create_submodule('ext', 'ext', 'git@github.ru:ext/repo.git')
    uservices_repo.create_submodule(
        'dashboards',
        'dashboards',
        'git@github.yandex-team.ru:taxi/dashboards.git',
    )
    uservices_repo.git.status()  # do not work without this line
    uservices_repo.git.mv('userver', 'usrv_pr')
    commit_by_name['uservices_pr'] = uservices_repo.index.commit('pr')
    uservices_repo.git.update_ref(
        'refs/pulls/111/head', commit_by_name['uservices_pr'].hexsha,
    )
    uservices_repo.git.checkout('develop')
    uservices_repo.git.submodule('update', '--init', '--recursive')

    (codegen_dir / 'b').touch()
    codegen_repo.index.add(['b'])
    codegen_repo.index.remove('a', working_tree=True)
    codegen_repo.create_submodule(
        'dashboards',
        'dashboards',
        'git@github.yandex-team.ru:taxi/dashboards.git',
    )
    commit_by_name['codegen_b'] = codegen_repo.index.commit('b')

    (userver_dir / 'c').touch()
    userver_repo.index.add(['c'])
    userver_repo.index.remove('b', working_tree=True)
    codegen_submodule.module().remote().fetch()
    codegen_submodule.module().git.checkout(commit_by_name['codegen_b'].hexsha)
    userver_repo.git.add('codegen')
    commit_by_name['userver_c'] = userver_repo.index.commit('c')

    (uservices_dir / 'd').touch()
    uservices_repo.index.add(['d'])
    uservices_repo.index.remove('c', working_tree=True)
    userver_submodule.module().remote().fetch()
    userver_submodule.module().git.checkout(commit_by_name['userver_c'].hexsha)
    uservices_repo.git.add('userver')
    commit_by_name['uservices_d'] = uservices_repo.index.commit('d')

    if params.second.break_mirror:
        (repos_dir / 'taxi' / 'userver.git' / 'HEAD').unlink()

    run(params.second)
