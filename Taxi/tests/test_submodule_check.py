import os
import pathlib
from typing import Callable
from typing import NamedTuple
from typing import Optional
from typing import Sequence
from typing import Tuple

import freezegun
import git
import pytest

import git_checkout
import submodule_check
from tests.utils import repository
from tests.utils.examples import backend
from tests.utils.examples import backend_cpp
from tests.utils.examples import uservices


class Params(NamedTuple):
    init_repo: Callable[[str], git.Repo]
    origin_develop_commits: Sequence[repository.Commit] = ()
    submodule_add_branches: Sequence[Tuple[str, str]] = ()
    submodule_commits: Sequence[
        Tuple[str, str, Sequence[repository.Commit]]
    ] = ()
    submodule_checkouts: Sequence[Tuple[str, str]] = ()
    pr_commits: Sequence[repository.Commit] = ()
    fail_messages: Optional[Sequence[dict]] = None


@freezegun.freeze_time('2018-04-23 14:22:56', tz_offset=3)
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                origin_develop_commits=[
                    repository.Commit(
                        'new_sub',
                        [],
                        submodules=[
                            (
                                'submodules/testsuite',
                                [
                                    repository.Commit(
                                        'testsuite commit', ['test3'],
                                    ),
                                ],
                            ),
                            (
                                'new_sub',
                                [repository.Commit('init sub', ['f1'])],
                            ),
                        ],
                    ),
                ],
                pr_commits=[repository.Commit('new_commit', ['f1'])],
            ),
            id='backend_cpp develop submodules update',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                pr_commits=[
                    repository.Commit(
                        'new_sub',
                        [],
                        submodules=[
                            (
                                'submodules/testsuite',
                                [
                                    repository.Commit(
                                        'testsuite commit', ['test3'],
                                    ),
                                ],
                            ),
                            (
                                'new_sub',
                                [repository.Commit('init sub', ['f1'])],
                            ),
                        ],
                    ),
                ],
            ),
            id='backend_cpp submodules update',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                submodule_checkouts=[('submodules/testsuite', 'HEAD~1')],
                fail_messages=[
                    {
                        'description': (
                            'submodule submodules/testsuite downgraded'
                        ),
                        'identity': 'submodules/testsuite',
                    },
                ],
            ),
            id='backend_cpp submodules rollback',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                submodule_checkouts=[('submodules/testsuite', 'HEAD~1')],
                origin_develop_commits=[
                    repository.Commit(
                        'update_sub',
                        [],
                        submodules=[
                            (
                                'submodules/testsuite',
                                [
                                    repository.Commit(
                                        'testsuite commit', ['test3'],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
                fail_messages=[
                    {
                        'description': (
                            'submodule submodules/testsuite downgraded'
                        ),
                        'identity': 'submodules/testsuite',
                    },
                ],
            ),
            id='backend_cpp submodules rollback with develop changes',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                submodule_checkouts=[('submodules/testsuite', 'HEAD~1')],
                pr_commits=[
                    repository.Commit(
                        'update_sub',
                        [],
                        submodules=[
                            (
                                'submodules/testsuite',
                                [
                                    repository.Commit(
                                        'testsuite commit', ['test3'],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
                fail_messages=[
                    {
                        'description': (
                            'submodule submodules/testsuite downgraded'
                        ),
                        'identity': 'submodules/testsuite',
                    },
                ],
            ),
            id='backend_cpp submodules rollback with updates',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                submodule_add_branches=[
                    ('submodules/testsuite', 'sub_pull_request'),
                ],
                submodule_commits=[
                    (
                        'submodules/testsuite',
                        'sub_pull_request',
                        [
                            repository.Commit(
                                'testsuite commit for sub pr', ['test42'],
                            ),
                        ],
                    ),
                ],
                pr_commits=[
                    repository.Commit(
                        'new_sub',
                        [],
                        submodules=[
                            (
                                'submodules/testsuite',
                                [
                                    repository.Commit(
                                        'testsuite commit', ['test43'],
                                    ),
                                ],
                            ),
                            (
                                'new_sub',
                                [repository.Commit('init sub', ['f1'])],
                            ),
                        ],
                    ),
                ],
                fail_messages=[
                    {
                        'identity': 'submodules/testsuite',
                        'description': (
                            'submodule submodules/testsuite must be '
                            'in \'develop\' branch'
                        ),
                    },
                ],
            ),
            id='backend_cpp change submodule hash to submodule pr hash',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                submodule_add_branches=[
                    ('submodules/testsuite', 'sub_pull_request'),
                    ('submodules/random_submodule', 'sub2_pull_request'),
                ],
                submodule_commits=[
                    (
                        'submodules/testsuite',
                        'sub_pull_request',
                        [
                            repository.Commit(
                                'testsuite commit for sub pr', ['test42'],
                            ),
                        ],
                    ),
                    (
                        'submodules/random_submodule',
                        'sub2_pull_request',
                        [
                            repository.Commit(
                                'random commit for sub pr', ['test42'],
                            ),
                        ],
                    ),
                ],
                pr_commits=[
                    repository.Commit(
                        'new_sub',
                        [],
                        submodules=[
                            (
                                'submodules/testsuite',
                                [
                                    repository.Commit(
                                        'testsuite commit', ['test43'],
                                    ),
                                ],
                            ),
                            (
                                'submodules/random_submodule',
                                [
                                    repository.Commit(
                                        'random_submodule commit', ['test44'],
                                    ),
                                ],
                            ),
                            (
                                'new_sub',
                                [repository.Commit('init sub', ['f1'])],
                            ),
                        ],
                    ),
                ],
                fail_messages=[
                    {
                        'identity': 'submodules/random_submodule',
                        'description': (
                            'submodule submodules/random_submodule must '
                            'be in \'develop\' branch'
                        ),
                    },
                    {
                        'identity': 'submodules/testsuite',
                        'description': (
                            'submodule submodules/testsuite must be '
                            'in \'develop\' branch'
                        ),
                    },
                ],
            ),
            id=(
                'backend_cpp change submodule hash to submodule pr '
                'hash in 2 submodules'
            ),
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                submodule_add_branches=[
                    ('submodules/testsuite', 'sub_pull_request'),
                ],
                submodule_commits=[
                    (
                        'submodules/testsuite',
                        'sub_pull_request',
                        [
                            repository.Commit(
                                'testsuite commit for sub pr', ['test42'],
                            ),
                        ],
                    ),
                ],
                submodule_checkouts=[('submodules/testsuite', 'develop')],
            ),
            id='backend_cpp make pr in submodule but checkout back on develop',
        ),
        pytest.param(Params(init_repo=backend.init), id='empty backend'),
        pytest.param(
            Params(init_repo=backend_cpp.init), id='empty backend_cpp',
        ),
        pytest.param(Params(init_repo=backend.init), id='empty backend_py3'),
        pytest.param(Params(init_repo=uservices.init), id='empty uservices'),
    ],
)
def test_submodule_check(
        tmpdir,
        chdir,
        monkeypatch,
        teamcity_report_problems,
        github,
        staff_persons_mock,
        telegram,
        params: Params,
):
    repo = params.init_repo(tmpdir)
    repo.git.checkout('-b', 'pr')
    # send origin_develop_commits to origin repo
    repository.add_commits_only_to_origin(repo, params.origin_develop_commits)
    repo.git.checkout('pr')
    repo.git.submodule('update', '--init', '--recursive')

    # make submodule changes in submodule pull request
    for submodule, branch_name in params.submodule_add_branches:
        sub_repo = git.Repo(os.path.join(repo.working_tree_dir, submodule))
        sub_repo.git.branch(branch_name)

    for submodule, branch, commits in params.submodule_commits:
        sub_repo = git.Repo(os.path.join(repo.working_tree_dir, submodule))
        sub_repo.git.checkout(branch)
        repository.apply_commits(sub_repo, commits)

    for submodule, commit in params.submodule_checkouts:
        sub_repo = git.Repo(os.path.join(repo.working_tree_dir, submodule))
        sub_repo.git.checkout(commit)

    # commit submodules changes into main repo pr
    if params.submodule_checkouts or params.submodule_commits:
        repo.git.add('-A')
        repo.index.commit('update submodules')

    repository.apply_commits(repo, params.pr_commits)
    chdir(repo.working_tree_dir)
    pr_commit = repo.head.object
    repo.git.checkout(pr_commit)

    submodule_check.main()

    assert repo.head.object == pr_commit

    if params.fail_messages is not None:
        assert teamcity_report_problems.calls == params.fail_messages
    else:
        assert teamcity_report_problems.calls == []


class AnotherParams(NamedTuple):
    submodule_branches: Sequence[str] = ()
    fail_message: Optional[dict] = None


@freezegun.freeze_time('2018-04-23 14:22:56', tz_offset=3)
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            AnotherParams(submodule_branches=['develop', 'random_one']),
            id='backend_cpp have other branch and develop',
        ),
        pytest.param(
            AnotherParams(
                submodule_branches=['random_one'],
                fail_message={
                    'identity': 'submodules/test_module',
                    'description': (
                        'submodule submodules/test_module must have '
                        '\'develop\' branch'
                    ),
                },
            ),
            id='backend_cpp dont have develop branch',
        ),
    ],
)
def test_submodule_check_has_develop(
        tmpdir,
        chdir,
        monkeypatch,
        teamcity_report_problems,
        staff_persons_mock,
        params: AnotherParams,
):
    username = 'testuser'
    email = 'testuser@yandex-team.ru'

    # make repo with origin
    path = str(tmpdir.mkdir('repo'))
    origin_path = str(tmpdir.mkdir('origin'))

    repo = git.Repo.init(path)
    repository.set_current_user(repo, username, email)
    repo.git.checkout('-b', 'develop')
    repository.apply_commits(
        repo, [repository.Commit('init repo', files=['test_file'])],
    )
    repo.clone(origin_path, bare=True)
    repo.git.remote('add', 'origin', origin_path)

    # add submodule with origin
    submodule_name = 'test_module'
    submodule_path = os.path.join('submodules', submodule_name)
    origin_submodule_path = repo.working_tree_dir + '_' + submodule_name

    origin_sub_repo = git.Repo.init(origin_submodule_path)
    repository.set_current_user(origin_sub_repo, username, email)
    repository.apply_commits(
        origin_sub_repo,
        [repository.Commit('init sub repo', files=['test_sub_file'])],
    )

    repo.git.submodule('add', origin_submodule_path, submodule_path)

    repo.git.add('-A')
    repo.index.commit('add submodule')
    sub_repo = git.Repo(os.path.join(path, submodule_path))

    # add branches
    for branch_name in params.submodule_branches:
        sub_repo.git.branch(branch_name)
    sub_repo.git.push('--all', 'origin')

    chdir(repo.working_tree_dir)
    head_commit = repo.head.object
    repo.git.checkout(head_commit)

    submodule_check.main()

    assert repo.head.object == head_commit

    if params.fail_message is not None:
        assert teamcity_report_problems.calls == [params.fail_message]
    else:
        assert teamcity_report_problems.calls == []


def test_check_correct_submodules_update(
        tmpdir, monkeypatch, chdir, teamcity_report_problems, repos_dir,
):
    checkout_dir = str(tmpdir.mkdir('checkout_dir'))
    repo = uservices.init(tmpdir)
    origin_sub_repo = git.Repo(os.path.join(tmpdir, 'repo_userver'))

    uservices_url = 'git@github.yandex-team.ru:taxi/uservices.git'
    userver_url = 'git@github.yandex-team.ru:taxi/userver.git'
    home_dir = pathlib.Path(tmpdir.mkdir('home'))
    git_config_file = home_dir / '.gitconfig'
    monkeypatch.setenv('HOME', home_dir)
    git_config = git.GitConfigParser(str(git_config_file), read_only=False)
    git_config.set_value('user', 'name', 'alberist')
    git_config.set_value('user', 'email', 'alberist@yandex-team.ru')
    git_config.set_value(
        'url "%s"' % repo.working_tree_dir, 'insteadOf', uservices_url,
    )
    git_config.set_value(
        'url "%s"' % origin_sub_repo.working_tree_dir,
        'insteadOf',
        userver_url,
    )
    repo.git.config(
        '--file', '.gitmodules', 'submodule.userver.url', userver_url,
    )
    repo.git.add('-A')
    repo.index.commit('change submodule url')

    git_checkout.main([uservices_url, checkout_dir])
    chdir(checkout_dir)
    submodule_check.main()

    assert teamcity_report_problems.calls == []

    repo.git.checkout('develop')
    repository.apply_commits(
        origin_sub_repo,
        [repository.Commit('new_commit', files=['test_file'])],
    )
    sub_repo = git.Repo(os.path.join(repo.working_tree_dir, 'userver'))
    sub_repo.git.pull()

    repo.git.add('-A')
    repo.index.commit('update userver submodule')

    repo.git.checkout('-b', 'pr')
    sub_repo.git.checkout('HEAD~1')
    repo.git.add('-A')
    repo.index.commit('downgrade submodule')
    repo.git.checkout(repo.head.object)

    git_checkout.main(
        [
            '--branch',
            'refs/pull/123/head',
            '--commit',
            str(repo.head.object),
            '--clean',
            uservices_url,
            checkout_dir,
        ],
    )
    submodule_check.main()

    assert teamcity_report_problems.calls == [
        {'description': 'submodule userver downgraded', 'identity': 'userver'},
    ]
