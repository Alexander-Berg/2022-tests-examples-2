import dataclasses
from typing import Any
from typing import Callable
from typing import List
from typing import Optional

import git
import pytest

import run_hotfix
import run_release
from taxi_buildagent.clients import vcs_base
from tests.utils import repository
from tests.utils.examples import backend


def test_hotfix_after_release(harness, teamcity_report_problems, startrek):
    harness.init_repo(backend.init)
    harness.checkout('master')
    pr_url = harness.create_pr(
        branch='hotfix/my-hotfix',
        target_branch='develop',
        state='merged',
        merge=True,
        merge_message='hotfix: do stuff (#1)\n\nRelates: TAXITOOLS-1',
        login='rumkex',
        commits=[
            repository.Commit('hotfix: do stuff', ['taxi/data'], 'has hotfix'),
        ],
        reviews=[vcs_base.Review('rumkex', 'approved')],
    )

    run_release.main([])

    assert (
        startrek.create_ticket.calls[0]['json']['description']
        == 'TAXITOOLS-1\nalberist | commit'
    )

    run_hotfix.main([pr_url])

    assert teamcity_report_problems.calls[0]['description'] == (
        'https://github.yandex-team.ru/taxi/backend/pull/1'
        ' has been already merged into master'
    )
    assert not list(startrek.update_ticket.calls)


@dataclasses.dataclass
class Params:
    target_branch: str
    hotfix_changelog: str
    release_changelog: str


# FIXME: releases must not include messages for commits cherry-picked from
#  develop, and the release ticket must be exactly the same for all types of
#  hotfixes, see: TAXITOOLS-2980
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                target_branch='master',
                hotfix_changelog='some\ntext\n\n3.0.224hotfix1:\n'
                'User rumkex | hotfix: do stuff',
                release_changelog='alberist | commit',
            ),
            id='release-after-merge',
        ),
        pytest.param(
            Params(
                target_branch='develop',
                hotfix_changelog='some\ntext\n\n3.0.224hotfix1:\n'
                'User rumkex | Merge pull request (#1)',
                release_changelog='User rumkex | Merge pull request (#1)\n'
                'alberist | commit',
            ),
            id='release-after-cherrypick',
        ),
    ],
)
def test_release_after_hotfix(
        harness, teamcity_report_problems, startrek, params: Params,
):
    """
    Test if merged and cherry-picked hotfixes do not break the next release
    and do not get logged in the release changelog
    """
    harness.init_repo(backend.init)
    harness.checkout('master')
    should_merge = params.target_branch == 'develop'
    pr_url = harness.create_pr(
        branch='hotfix/my-hotfix',
        target_branch=params.target_branch,
        merge=should_merge,
        state='closed' if params.target_branch == 'develop' else 'open',
        login='rumkex',
        commits=[
            repository.Commit('hotfix: do stuff', ['taxi/data'], 'has hotfix'),
        ],
        reviews=[vcs_base.Review('rumkex', 'approved')],
    )

    run_hotfix.main([pr_url])

    assert (
        startrek.update_ticket.calls[0]['json']['description']
        == params.hotfix_changelog
    )

    run_release.main([])

    assert (
        startrek.create_ticket.calls[0]['json']['description']
        == params.release_changelog
    )


def test_hotfix_with_deploy_resources(harness, startrek):
    """
    Test that hotfix is possible with deploying resources
    """
    harness.init_repo(
        backend.init,
        [
            repository.Commit(
                'commit0',
                ['service.yaml'],
                'clownductor: {sandbox-resources: '
                '[{source-path: bla, destination-path: bla1, '
                'owner: gilfanovii}]}',
            ),
        ],
    )
    pr_url = harness.create_pr(
        branch='hotfix/my-hotfix',
        target_branch='develop',
        merge=True,
        state='closed',
        login='rumkex',
        commits=[repository.Commit('hotfix', ['taxi/data'])],
        reviews=[vcs_base.Review('rumkex', 'approved')],
    )

    run_hotfix.main([pr_url])

    check_st(
        startrek,
        'some\ntext\n\n3.0.224hotfix1:\nUser rumkex | Merge pull request (#1)',
    )

    harness.commit(['commit1'])
    run_release.main(['--deploy-type', 'sandbox-resources'])
    check_st(
        startrek,
        'User rumkex | Merge pull request (#1)\n'
        'alberist | commit\nalberist | commit0\nalberist | commit1',
        summary='SUMMARY 3.0.224resources1',
    )

    startrek.ticket_components = [{'name': 'sandbox-resources', 'id': 41}]
    pr_url = harness.create_pr(
        branch='hotfix/my-hotfix2',
        target_branch='develop',
        merge=True,
        state='closed',
        login='rumkex1',
        commits=[repository.Commit('hotfix', ['taxi/data1'])],
        reviews=[vcs_base.Review('rumkex', 'approved')],
    )
    run_hotfix.main([pr_url])
    check_st(
        startrek,
        'some\ntext\n\n3.0.224resources1hotfix1:\n'
        'User rumkex1 | Merge pull request (#2)',
    )

    harness.commit(['commit2'])
    run_release.main(['--deploy-type', 'sandbox-resources'])
    check_st(
        startrek, 'User rumkex1 | Merge pull request (#2)\nalberist | commit2',
    )


def check_st(startrek, msg, *, summary=None):
    calls = startrek.update_ticket.calls or startrek.create_ticket.calls
    assert calls[0]['json']['description'] == msg
    if summary:
        assert calls[0]['json']['summary'] == summary


class Harness:
    def __init__(self, tmpdir, chdir, github):
        self._tmpdir = tmpdir
        self._chdir = chdir
        self._repo = None
        self._github = github
        self._github_repo = None

    def init_repo(
            self,
            repo_factory: Callable[[Any], git.Repo],
            develop_commits: Optional[List[repository.Commit]] = None,
    ) -> None:
        assert not self._repo
        self._repo = repo_factory(self._tmpdir)
        self._repo.create_tag('3.0.224')
        self._repo.git.push('origin', '3.0.224')
        repository.apply_commits(
            self._repo,
            [
                repository.Commit('commit', ['file'], 'very important'),
                *(develop_commits or []),
            ],
        )
        self._repo.git.push('origin', 'develop')
        self._chdir(self._repo.working_tree_dir)
        self._github_repo = self._github.init_repo(
            'taxi', 'backend', next(self._repo.remotes[0].urls),
        )
        self._repo.git.config('user.email', 'buildfarm@yandex-team.ru')

    def checkout(self, branch):
        self._repo.git.checkout(branch)

    def create_pr(self, **kwargs):
        return self._github_repo.create_pr(self._repo, **kwargs)

    def commit(self, commits: List[str]) -> None:
        self.checkout('develop')
        self._repo.git.config('user.email', 'alberist@yandex-team.ru')
        repository.apply_commits(
            self._repo,
            [repository.Commit(commit, [commit]) for commit in commits],
        )
        self._repo.git.push('origin', 'develop')
        self._repo.git.config('user.email', 'buildfarm@yandex-team.ru')
        self.checkout('master')


@pytest.fixture(name='harness')
def _harness(monkeypatch, tmpdir, chdir, github, startrek):
    monkeypatch.setenv('TELEGRAM_BOT_CHAT_ID', 'tchatid')
    monkeypatch.setenv('ADD_FOLLOWERS', '')
    monkeypatch.setenv('TELEGRAM_DISABLED', '1')
    monkeypatch.setenv('SLACK_DISABLED', '1')
    monkeypatch.setenv('RELEASE_TICKET_SUMMARY', 'SUMMARY')

    startrek.ticket_status = 'testing'

    return Harness(tmpdir, chdir, github)
