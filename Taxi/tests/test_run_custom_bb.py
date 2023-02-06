import dataclasses
from typing import Callable
from typing import Sequence

import freezegun
import git
import pytest

import git_checkout
import run_custom_bb
from taxi_buildagent.tools.vcs import git_repo
from tests.plugins import bitbucket
from tests.utils import repository
from tests.utils.examples import backend


@dataclasses.dataclass
class Params:
    init_repo: Callable
    pull_requests: Sequence[dict]
    slack_message: str
    expected_calls: Sequence[str]
    obsolete_flag: bool = False
    skip_checks_flag: bool = False
    whitelist_flag: bool = False


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                init_repo=backend.init,
                pull_requests=[
                    {
                        'login': 'rumkex',
                        'title': 'basic pr 1',
                        'branch': 'feature1',
                        'commits': (
                            repository.Commit('init', ['README.txt']),
                            repository.Commit('feature', ['feature.py']),
                        ),
                        'build_status': [
                            bitbucket.BuildStatus(
                                state='SUCCESSFUL', key='TestBuild1',
                            ),
                            bitbucket.BuildStatus(
                                state='SUCCESSFUL', key='TestBuild2',
                            ),
                        ],
                        'updated_at': 1637060572000,
                    },
                ],
                slack_message=(
                    'Custom build was created: '
                    'https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=123123\n'
                    '*Merged PRs:*\n'
                    '  <https://bb.yandex-team.ru/projects/'
                    'EDA/repos/core/pull-requests/1|basic pr 1> - rumkex'
                ),
                expected_calls=['refs/pull-requests/1/from'],
            ),
            id='basic happy path test',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                pull_requests=[
                    {
                        'login': 'rumkex',
                        'title': 'pr 1',
                        'branch': 'feature1',
                        'commits': (
                            repository.Commit('feature', ['feature.py']),
                        ),
                    },
                    {
                        'login': 'rumkex',
                        'title': 'pr 2',
                        'branch': 'feature2',
                        'commits': (
                            repository.Commit('feature2', ['feature.py']),
                        ),
                    },
                    {
                        'login': 'rumkex',
                        'title': 'pr 3',
                        'branch': 'feature3',
                        'commits': (
                            repository.Commit('feature3', ['feature3.py']),
                        ),
                    },
                ],
                slack_message=(
                    'Custom build was created: '
                    'https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=123123\n'
                    '*Conflicted PRs:*\n'
                    '  <https://bb.yandex-team.ru/projects/EDA/repos/core/'
                    'pull-requests/2|pr 2> - @rumkex\n'
                    '*Merged PRs:*\n'
                    '  <https://bb.yandex-team.ru/projects/EDA/repos/core/'
                    'pull-requests/1|pr 1> - rumkex\n'
                    '  <https://bb.yandex-team.ru/projects/EDA/repos/core/'
                    'pull-requests/3|pr 3> - rumkex'
                ),
                expected_calls=[
                    'refs/pull-requests/1/from',
                    'refs/pull-requests/2/from',
                    'refs/pull-requests/3/from',
                ],
            ),
            id='conflicting PRs test',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                pull_requests=[
                    {
                        'login': 'olegsavinov',
                        'title': 'pr 1',
                        'branch': 'feature1',
                        'commits': (
                            repository.Commit('feature', ['feature.py']),
                        ),
                        'build_status': [
                            bitbucket.BuildStatus(
                                state='SUCCESSFUL', key='TestBuild1',
                            ),
                            bitbucket.BuildStatus(
                                state='SUCCESSFUL', key='TestBuild2',
                            ),
                        ],
                    },
                    {
                        'login': 'olegsavinov',
                        'title': 'pr 2',
                        'branch': 'feature2',
                        'commits': (
                            repository.Commit('feature2', ['feature2.py']),
                        ),
                        'build_status': [
                            bitbucket.BuildStatus(
                                state='INPROGRESS', key='TestBuild1',
                            ),
                            bitbucket.BuildStatus(
                                state='SUCCESSFUL', key='TestBuild2',
                            ),
                        ],
                    },
                    {
                        'login': 'olegsavinov',
                        'title': 'pr 3',
                        'branch': 'feature3',
                        'commits': (
                            repository.Commit('feature3', ['feature3.py']),
                        ),
                        'build_status': [
                            bitbucket.BuildStatus(
                                state='SUCCESSFUL', key='TestBuild1',
                            ),
                            bitbucket.BuildStatus(
                                state='SUCCESSFUL', key='TestBuild2',
                            ),
                        ],
                    },
                ],
                slack_message=(
                    'Custom build was created: '
                    'https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=123123\n'
                    '*PRs with failed CI builds:*\n'
                    '  <https://bb.yandex-team.ru/projects/EDA/repos/core/'
                    'pull-requests/2|pr 2> - @olegsavinov\n'
                    '*Merged PRs:*\n'
                    '  <https://bb.yandex-team.ru/projects/EDA/repos/core/'
                    'pull-requests/1|pr 1> - olegsavinov\n'
                    '  <https://bb.yandex-team.ru/projects/EDA/repos/core/'
                    'pull-requests/3|pr 3> - olegsavinov'
                ),
                expected_calls=[
                    'refs/pull-requests/1/from',
                    'refs/pull-requests/3/from',
                ],
            ),
            id='failed builds PRs test',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                pull_requests=[
                    {
                        'login': 'olegsavinov',
                        'title': 'pr 1',
                        'branch': 'feature1',
                        'commits': (
                            repository.Commit('feature', ['feature.py']),
                        ),
                        'build_status': [
                            bitbucket.BuildStatus(
                                state='SUCCESSFUL', key='TestBuild1',
                            ),
                            bitbucket.BuildStatus(
                                state='SUCCESSFUL', key='TestBuild2',
                            ),
                        ],
                    },
                    {
                        'login': 'olegsavinov',
                        'title': 'pr 2',
                        'branch': 'feature2',
                        'commits': (
                            repository.Commit('feature2', ['feature2.py']),
                        ),
                        'build_status': [
                            bitbucket.BuildStatus(
                                state='FAILED', key='TestBuild1',
                            ),
                            bitbucket.BuildStatus(
                                state='SUCCESSFUL', key='TestBuild2',
                            ),
                        ],
                    },
                    {
                        'login': 'olegsavinov',
                        'title': 'pr 3',
                        'branch': 'feature3',
                        'commits': (
                            repository.Commit('feature3', ['feature3.py']),
                        ),
                        'build_status': [
                            bitbucket.BuildStatus(
                                state='SUCCESSFUL', key='TestBuild1',
                            ),
                            bitbucket.BuildStatus(
                                state='SUCCESSFUL', key='TestBuild2',
                            ),
                        ],
                    },
                ],
                slack_message=(
                    'Custom build was created: '
                    'https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=123123\n'
                    '*PRs with failed CI builds:*\n'
                    '  <https://bb.yandex-team.ru/projects/EDA/repos/core/'
                    'pull-requests/2|pr 2> - @olegsavinov\n'
                    '*Merged PRs:*\n'
                    '  <https://bb.yandex-team.ru/projects/EDA/repos/core/'
                    'pull-requests/1|pr 1> - olegsavinov\n'
                    '  <https://bb.yandex-team.ru/projects/EDA/repos/core/'
                    'pull-requests/3|pr 3> - olegsavinov'
                ),
                expected_calls=[
                    'refs/pull-requests/1/from',
                    'refs/pull-requests/3/from',
                ],
            ),
            id='in progress builds PRs test',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                pull_requests=[
                    {
                        'login': 'rumkex',
                        'title': 'pr 1',
                        'branch': 'feature1',
                        'commits': (
                            repository.Commit('init', ['README.txt']),
                            repository.Commit('feature', ['feature.py']),
                        ),
                        'build_status': [
                            bitbucket.BuildStatus(
                                state='SUCCESSFUL', key='TestBuild1',
                            ),
                            bitbucket.BuildStatus(
                                state='FAILED',
                                key=(
                                    'YandexTaxiProjects_Eda_BackendServiceCore'
                                    '_PullRequests_MigrationTests'
                                ),
                            ),
                        ],
                    },
                ],
                slack_message=(
                    'Custom build was created: '
                    'https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=123123\n'
                    '*Merged PRs:*\n'
                    '  <https://bb.yandex-team.ru/projects/'
                    'EDA/repos/core/pull-requests/1|pr 1> - rumkex'
                ),
                expected_calls=['refs/pull-requests/1/from'],
            ),
            id='failed migrations build test',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                pull_requests=[
                    {
                        'login': 'eugenyegorov',
                        'title': 'pr 1',
                        'branch': 'feature_1',
                        'commits': (
                            repository.Commit('feature_1', ['script_1.py']),
                        ),
                        'build_status': [
                            bitbucket.BuildStatus(
                                state='SUCCESSFUL', key='TestBuild1',
                            ),
                        ],
                        'created_at': 1637233372000,
                        'updated_at': 1637233372000,
                    },
                    {
                        'login': 'eugenyegorov',
                        'title': 'pr 2',
                        'branch': 'feature_2',
                        'commits': (
                            repository.Commit('feature_2', ['script_2.py']),
                        ),
                        'build_status': [
                            bitbucket.BuildStatus(
                                state='SUCCESSFUL', key='TestBuild1',
                            ),
                        ],
                        'created_at': 1637146972000,
                        'updated_at': 1637146972000,
                    },
                    {
                        'login': 'eugenyegorov',
                        'title': 'pr 3',
                        'branch': 'feature_3',
                        'commits': (
                            repository.Commit('feature_3', ['script_3.py']),
                        ),
                        'build_status': [
                            bitbucket.BuildStatus(
                                state='SUCCESSFUL', key='TestBuild1',
                            ),
                        ],
                        'created_at': 1637060572000,
                        'updated_at': 1637060572000,
                    },
                ],
                slack_message=(
                    'Custom build was created: '
                    'https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=123123'
                    f'\n*PRs are not updated more than %s days:*\n'
                    '  <https://bb.yandex-team.ru/projects/EDA/repos/core/'
                    'pull-requests/3|pr 3> - @eugenyegorov'
                    '\n*Merged PRs:*\n'
                    '  <https://bb.yandex-team.ru/projects/EDA/repos/core/'
                    'pull-requests/1|pr 1> - eugenyegorov\n'
                    '  <https://bb.yandex-team.ru/projects/EDA/repos/core/'
                    'pull-requests/2|pr 2> - eugenyegorov'
                ),
                expected_calls=[
                    'refs/pull-requests/1/from',
                    'refs/pull-requests/2/from',
                ],
                obsolete_flag=True,
            ),
            id='too old PRs test',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                pull_requests=[
                    {
                        'login': 'eugenyegorov',
                        'title': 'pr 1',
                        'branch': 'feature_1',
                        'commits': (
                            repository.Commit('feature_1', ['script_1.py']),
                        ),
                        'build_status': [
                            bitbucket.BuildStatus(
                                state='SUCCESSFUL', key='TestBuild2',
                            ),
                        ],
                    },
                    {
                        'login': 'eugenyegorov',
                        'title': 'pr 2',
                        'branch': 'feature_2',
                        'commits': (
                            repository.Commit('feature_2', ['script_2.py']),
                        ),
                        'build_status': [
                            bitbucket.BuildStatus(
                                state='FAILED', key='TestBuild3',
                            ),
                        ],
                    },
                    {
                        'login': 'eugenyegorov',
                        'title': 'pr 3',
                        'branch': 'feature_3',
                        'commits': (
                            repository.Commit('feature_3', ['script_3.py']),
                        ),
                        'build_status': [
                            bitbucket.BuildStatus(
                                state='FAILED', key='TestBuild4',
                            ),
                            bitbucket.BuildStatus(
                                state='INPROGRESS', key='TestBuild5',
                            ),
                        ],
                    },
                ],
                slack_message=(
                    'Custom build was created: '
                    'https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=123123'
                    '\n*Merged PRs:*\n'
                    '  <https://bb.yandex-team.ru/projects/EDA/repos/core/'
                    'pull-requests/1|pr 1> - eugenyegorov\n'
                    '  <https://bb.yandex-team.ru/projects/EDA/repos/core/'
                    'pull-requests/2|pr 2> - eugenyegorov\n'
                    '  <https://bb.yandex-team.ru/projects/EDA/repos/core/'
                    'pull-requests/3|pr 3> - eugenyegorov'
                ),
                expected_calls=[
                    'refs/pull-requests/1/from',
                    'refs/pull-requests/2/from',
                    'refs/pull-requests/3/from',
                ],
                skip_checks_flag=True,
            ),
            id='pass PRs with failed builds by flag',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                pull_requests=[
                    {
                        'login': 'eugenyegorov',
                        'title': 'pr 1',
                        'branch': 'feature_1',
                        'commits': (
                            repository.Commit('feature_1', ['script_1.py']),
                        ),
                        'build_status': [
                            bitbucket.BuildStatus(
                                state='SUCCESSFUL', key='TestBuild1',
                            ),
                        ],
                    },
                    {
                        'login': 'eugenyegorov',
                        'title': 'pr 2',
                        'branch': 'feature_2',
                        'commits': (
                            repository.Commit('feature_2', ['script_2.py']),
                        ),
                        'build_status': [
                            bitbucket.BuildStatus(
                                state='FAILED', key='TestBuild1',
                            ),
                        ],
                    },
                    {
                        'login': 'eugenyegorov',
                        'title': 'pr 3',
                        'branch': 'feature_3',
                        'commits': (
                            repository.Commit('feature_3', ['script_3.py']),
                        ),
                        'build_status': [
                            bitbucket.BuildStatus(
                                state='FAILED', key='TestBuild1',
                            ),
                        ],
                    },
                ],
                slack_message=(
                    'Custom build was created: '
                    'https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=123123\n'
                    '*PRs with failed CI builds:*\n'
                    '  <https://bb.yandex-team.ru/projects/EDA/repos/core/'
                    'pull-requests/3|pr 3> - @eugenyegorov\n'
                    '*Merged PRs:*\n'
                    '  <https://bb.yandex-team.ru/projects/EDA/repos/core/'
                    'pull-requests/1|pr 1> - eugenyegorov\n'
                    '  <https://bb.yandex-team.ru/projects/EDA/repos/core/'
                    'pull-requests/2|pr 2> - eugenyegorov'
                ),
                expected_calls=[
                    'refs/pull-requests/1/from',
                    'refs/pull-requests/2/from',
                ],
                whitelist_flag=True,
            ),
            id='pass PRs by whitelist',
        ),
    ],
)
@freezegun.freeze_time(time_to_freeze='2021-11-24', tz_offset=+3)
def test_custom_bb(
        bitbucket_instance,
        patch_requests,
        home_dir,
        tmpdir,
        monkeypatch,
        repos_dir,
        teamcity_report_problems,
        teamcity_set_parameters,
        params: Params,
):
    monkeypatch.setattr(run_custom_bb, 'SLACK_CHANNEL', '#testing')
    monkeypatch.setattr(run_custom_bb, 'SLACK_API_URL', 'http://slack/post')

    @patch_requests('http://slack/post')
    def slack_message_handler(method, url, **kwargs):
        return patch_requests.response(status_code=200)

    monkeypatch.setenv('BUILD_ID', '123123')
    monkeypatch.setenv('BUILD_NUMBER', '123')
    if params.obsolete_flag:
        days = '7'
        monkeypatch.setenv('LABEL_TTL_DAYS', days)
        params.slack_message = params.slack_message % days

    if params.skip_checks_flag:
        monkeypatch.setenv('CUSTOM_IGNORE_PR_STATUS_CHECK', '1')

    if params.whitelist_flag:
        monkeypatch.setenv('PR_WHITE_LIST', '2')

    merge_calls = []
    _origin_merge_branch = git_repo.Repo.merge_branch

    def merge_branch(self, source, *args):
        merge_calls.append(source)
        return _origin_merge_branch(self, source, *args)

    monkeypatch.setattr(
        'taxi_buildagent.tools.vcs.git_repo.Repo.merge_branch', merge_branch,
    )

    repo = params.init_repo(tmpdir)
    origin_url = next(repo.remotes[0].urls)

    for prq in params.pull_requests:
        bitbucket_instance.create_pr(repo, **prq)

    git_config_file = home_dir / '.gitconfig'
    git_config = git.GitConfigParser(str(git_config_file), read_only=False)
    git_config.set_value('user', 'name', 'alberist')
    git_config.set_value('user', 'email', 'alberist@yandex-team.ru')

    git_config.set_value(
        'url "%s"' % repo.working_tree_dir,
        'insteadOf',
        'git@github.yandex-team.ru:taxi/backend.git',
    )

    without_sub_path = str(tmpdir.mkdir('repo_without_submodules'))
    args = [
        '--branch=develop',
        '--commit=develop',
        '--no-submodules',
        'git@github.yandex-team.ru:taxi/backend.git',
        without_sub_path,
    ]
    git_checkout.main(args)

    repo_without_submodules = git.Repo(without_sub_path)
    repo_without_submodules.git.remote('set-url', 'origin', origin_url)

    repo_without_submodules.git.checkout('develop')
    monkeypatch.chdir(repo_without_submodules.working_tree_dir)
    run_custom_bb.main()

    json = slack_message_handler.calls[0]['kwargs']['json']
    message_text = '\n'.join(
        [line['text']['text'] for line in json['attachments'][0]['blocks']],
    )
    assert message_text == params.slack_message, message_text
    assert params.expected_calls == merge_calls
