import dataclasses
import pathlib
from typing import Dict
from typing import List
from typing import Optional

import git

import checkout_arcadia_submodules
from tests.utils import pytest_wraps
from tests.utils import repository


REPOS = {
    'taxi/ml': [
        repository.Commit(
            'commit0',
            ['Makefile', 'file1', 'a/b/c/file2'],
            files_content='data-ml0',
            submodules=[
                repository.SubmoduleCommits(
                    path='submodules/codegen',
                    commits=[repository.Commit('init', ['tst'])],
                ),
            ],
        ),
        repository.Commit(
            'commit1', ['file1', 'a/b/c/file3'], files_content='data-ml1',
        ),
    ],
    'taxi-external/gtest': [
        repository.Commit(
            'commit0', ['file1', 'a/b/file2'], files_content='data-gtest0',
        ),
    ],
}


@dataclasses.dataclass
class Params(pytest_wraps.Params):
    tree: Dict[str, str]
    updated: Dict[str, str] = dataclasses.field(default_factory=dict)
    removed: List[str] = dataclasses.field(default_factory=list)
    fail_message: Optional[str] = None


PARAMS = [
    Params(
        pytest_id='no-submodules-success',
        tree={'file1': 'test', 'a/b/c/file2': 'test'},
    ),
    Params(
        pytest_id='ml0-success',
        tree={
            'file1': 'test',
            'ml/actual-git-commit': '{taxi_ml0}',
            'ml/git-repo': 'git@github.yandex-team.ru:taxi/ml.git',
            'ml/Makefile': 'data-ml0',
            'ml/file1': 'data-ml0',
            'ml/a/b/c/file2': 'data-ml0',
        },
    ),
    Params(
        pytest_id='ml0-renamed-success',
        tree={
            'file1': 'test',
            'ml2/actual-git-commit': '{taxi_ml0}',
            'ml2/git-repo': 'git@github.yandex-team.ru:taxi/ml.git',
            'ml2/Makefile': 'data-ml0',
            'ml2/file1': 'data-ml0',
            'ml2/a/b/c/file2': 'data-ml0',
        },
    ),
    Params(
        pytest_id='ml0-renamed-newline-success',
        tree={
            'file1': 'test',
            'ml2/actual-git-commit': '{taxi_ml0}\n',
            'ml2/git-repo': 'git@github.yandex-team.ru:taxi/ml.git\n',
            'ml2/Makefile': 'data-ml0',
            'ml2/file1': 'data-ml0',
            'ml2/a/b/c/file2': 'data-ml0',
        },
    ),
    Params(
        pytest_id='ml0-changes',
        tree={
            'file1': 'test',
            'ml/actual-git-commit': '{taxi_ml0}',
            'ml/git-repo': 'git@github.yandex-team.ru:taxi/ml.git',
            'ml/Makefile': 'wrong',
            'ml/file3': 'data-ml0',
            'ml/a/b/c/file2': 'data-ml0',
        },
        updated={'ml/Makefile': 'data-ml0', 'ml/file1': 'data-ml0'},
        removed=['ml/file3'],
    ),
    Params(
        pytest_id='ml0-changes-no-git-repo',
        tree={
            'file1': 'test',
            'ml/actual-git-commit': '{taxi_ml0}',
            'ml/Makefile': 'wrong',
            'ml/file3': 'data-ml0',
            'ml/a/b/c/file2': 'data-ml0',
        },
        fail_message='submodules are missing repo URL files: [\'ml\']',
    ),
    Params(
        pytest_id='ml0-renamed-changes',
        tree={
            'file1': 'test',
            'ml2/actual-git-commit': '{taxi_ml0}',
            'ml2/git-repo': 'git@github.yandex-team.ru:taxi/ml.git',
            'ml2/mkfile': 'data-ml0',
            'ml2/file1': 'wrong',
            'ml2/a/b/c/file2': 'data-ml0',
        },
        updated={'ml2/Makefile': 'data-ml0', 'ml2/file1': 'data-ml0'},
        removed=['ml2/mkfile'],
    ),
    Params(
        pytest_id='ml1-success',
        tree={
            'file1': 'test',
            'ml/actual-git-commit': '{taxi_ml1}',
            'ml/git-repo': 'git@github.yandex-team.ru:taxi/ml.git',
            'ml/Makefile': 'data-ml0',
            'ml/file1': 'data-ml1',
            'ml/a/b/c/file2': 'data-ml0',
            'ml/a/b/c/file3': 'data-ml1',
        },
    ),
    Params(
        pytest_id='ml1-changes',
        tree={
            'file1': 'test',
            'ml/actual-git-commit': '{taxi_ml1}',
            'ml/git-repo': 'git@github.yandex-team.ru:taxi/ml.git',
            'ml/Makefile': 'data-ml0',
            'ml/file1': 'wrong',
            'ml/a/b/c/file1': 'data-ml0',
            'ml/a/b/c/file3': 'data-ml1',
        },
        updated={'ml/file1': 'data-ml1', 'ml/a/b/c/file2': 'data-ml0'},
        removed=['ml/a/b/c/file1'],
    ),
    Params(
        pytest_id='ml1-changes-ignored-files',
        tree={
            'file1': 'test',
            'ml/actual-git-commit': '{taxi_ml1}',
            'ml/git-repo': 'git@github.yandex-team.ru:taxi/ml.git',
            'ml/a.yaml': 'a\nyaml\ndata',
            'ml/ya.make': 'top-level ya.make',
            'ml/new-dir/ya.make': 'ya.make in new directory',
            'ml/a/b/ya.make': 'nested ya.make',
            'ml/Makefile': 'data-ml0',
            'ml/file1': 'wrong',
            'ml/a/b/c/file1': 'data-ml0',
            'ml/a/b/c/file3': 'data-ml1',
        },
        updated={'ml/file1': 'data-ml1', 'ml/a/b/c/file2': 'data-ml0'},
        removed=['ml/a/b/c/file1'],
    ),
    Params(
        pytest_id='ml1-success-ignored-files',
        tree={
            'file1': 'test',
            'ml/actual-git-commit': '{taxi_ml1}',
            'ml/git-repo': 'git@github.yandex-team.ru:taxi/ml.git',
            'ml/a.yaml': 'a\nyaml\ndata',
            'ml/ya.make': 'top-level ya.make',
            'ml/new-dir/ya.make': 'ya.make in new directory',
            'ml/a/b/ya.make': 'nested ya.make',
            'ml/Makefile': 'data-ml0',
            'ml/file1': 'data-ml1',
            'ml/a/b/c/file2': 'data-ml0',
            'ml/a/b/c/file3': 'data-ml1',
        },
    ),
    Params(
        pytest_id='ml0-gtest0-success',
        tree={
            'file1': 'test',
            'ml/actual-git-commit': '{taxi_ml0}',
            'ml/git-repo': 'git@github.yandex-team.ru:taxi/ml.git',
            'ml/Makefile': 'data-ml0',
            'ml/file1': 'data-ml0',
            'ml/a/b/c/file2': 'data-ml0',
            'sub/gtest/actual-git-commit': '{taxi_external_gtest0}',
            'sub/gtest/git-repo': (
                'git@github.yandex-team.ru:taxi-external/gtest.git'
            ),
            'sub/gtest/file1': 'data-gtest0',
            'sub/gtest/a/b/file2': 'data-gtest0',
        },
    ),
    Params(
        pytest_id='ml0-gtest0-inside-success',
        tree={
            'file1': 'test',
            'ml/actual-git-commit': '{taxi_ml0}',
            'ml/git-repo': 'git@github.yandex-team.ru:taxi/ml.git',
            'ml/Makefile': 'data-ml0',
            'ml/file1': 'data-ml0',
            'ml/a/b/c/file2': 'data-ml0',
            'ml/sub/gtest/actual-git-commit': '{taxi_external_gtest0}',
            'ml/sub/gtest/git-repo': (
                'git@github.yandex-team.ru:taxi-external/gtest.git'
            ),
            'ml/sub/gtest/file1': 'data-gtest0',
            'ml/sub/gtest/a/b/file2': 'data-gtest0',
        },
    ),
    Params(
        pytest_id='ml0-gtest0-inside-changes',
        tree={
            'file1': 'test',
            'ml/actual-git-commit': '{taxi_ml0}',
            'ml/git-repo': 'git@github.yandex-team.ru:taxi/ml.git',
            'ml/Makefile': 'data-ml0',
            'ml/file1': 'wrong1',
            'ml/a/b/c/file3': 'data-ml0',
            'ml/sub/gtest/actual-git-commit': '{taxi_external_gtest0}',
            'ml/sub/gtest/git-repo': (
                'git@github.yandex-team.ru:taxi-external/gtest.git'
            ),
            'ml/sub/gtest/file1': 'wrong2',
            'ml/sub/gtest/a/b/file2': 'data-gtest0',
        },
        updated={
            'ml/file1': 'data-ml0',
            'ml/a/b/c/file2': 'data-ml0',
            'ml/sub/gtest/file1': 'data-gtest0',
        },
        removed=['ml/a/b/c/file3'],
    ),
    Params(
        pytest_id='ml1-wrong-commit',
        tree={
            'file1': 'test',
            'ml/actual-git-commit': '76f43281e3ef98b1cc7bde3ffb485682963ec73c',
            'ml/git-repo': 'git@github.yandex-team.ru:taxi/ml.git',
            'ml/Makefile': 'data-ml0',
            'ml/file1': 'data-ml1',
            'ml/a/b/c/file2': 'data-ml0',
            'ml/a/b/c/file3': 'data-ml1',
        },
        fail_message=(
            'Commit `76f43281e3ef98b1cc7bde3ffb485682963ec73c` not found'
        ),
    ),
    Params(
        pytest_id='ml1-wrong-git-repo',
        tree={
            'file1': 'test',
            'ml/actual-git-commit': '{taxi_ml1}',
            'ml/git-repo': 'git@github.yandex-team.ru:taxi/ml2.git',
            'ml/Makefile': 'data-ml0',
            'ml/file1': 'data-ml1',
            'ml/a/b/c/file2': 'data-ml0',
            'ml/a/b/c/file3': 'data-ml1',
        },
        fail_message=(
            'failed to checkout git@github.yandex-team.ru:taxi/ml2.git'
        ),
    ),
    Params(
        pytest_id='ml1-invalid-git-repo',
        tree={
            'file1': 'test',
            'ml/actual-git-commit': '{taxi_ml1}',
            'ml/git-repo': 'git+github.yandex-team.ru/taxi/ml.git',
            'ml/Makefile': 'data-ml0',
            'ml/file1': 'data-ml1',
            'ml/a/b/c/file2': 'data-ml0',
            'ml/a/b/c/file3': 'data-ml1',
        },
        fail_message=(
            'failed to checkout git+github.yandex-team.ru/taxi/ml.git'
        ),
    ),
]


@pytest_wraps.parametrize(PARAMS)
def test_git_checkout(
        params: Params,
        home_dir,
        monkeypatch,
        tmpdir,
        repos_dir,
        teamcity_report_problems,
):
    work_dir = pathlib.Path(tmpdir.mkdir('work_dir'))
    monkeypatch.chdir(work_dir)

    git_config_file = home_dir / '.gitconfig'
    git_config = git.GitConfigParser(str(git_config_file), read_only=False)
    git_config.set_value('user', 'name', 'alberist')
    git_config.set_value('user', 'email', 'alberist@yandex-team.ru')

    repos_subst = {}
    github_dir = pathlib.Path(tmpdir.mkdir('github'))
    for repo, commits in REPOS.items():
        repo_dir = github_dir / repo
        repo_dir.mkdir(parents=True)
        git_repo = git.Repo.init(repo_dir)
        for num, commit in enumerate(commits):
            repository.apply_commits(git_repo, [commit])
            repos_subst[
                repo.replace('/', '_').replace('-', '_') + str(num)
            ] = str(git_repo.head.commit)

        git_config.set_value(
            'url "%s"' % repo_dir,
            'insteadOf',
            'git@github.yandex-team.ru:%s.git' % repo,
        )

    git_config.write()

    tree = {
        key: value.format(**repos_subst) for key, value in params.tree.items()
    }
    for filename, content in tree.items():
        path = work_dir / filename
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text(content)

    git.Repo.init(work_dir)

    checkout_arcadia_submodules.main()

    if params.fail_message is not None:
        assert teamcity_report_problems.calls == [
            {'description': params.fail_message, 'identity': None},
        ]
        return
    assert not teamcity_report_problems.calls

    tree.update(params.updated)
    for rm_path in params.removed:
        del tree[rm_path]

    real_tree = {}
    for path in work_dir.rglob('*'):
        rel_path = str(path.relative_to(work_dir))
        if path.is_file() and '.git' not in rel_path:
            real_tree[rel_path] = path.read_text()

    assert real_tree == tree
