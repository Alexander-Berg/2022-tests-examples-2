import dataclasses
import datetime
import functools
import re
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple

import git
import pytest

from taxi_buildagent.clients import bitbucket
from taxi_buildagent.clients import vcs_base
from tests.utils import repository

BASE_URL = 'https://bb.yandex-team.ru/rest/'
BASE_URL_PULL_REQUESTS = (
    BASE_URL + 'api/1.0/projects/EDA/repos/core/pull-requests'
)
BASE_URL_COMMIT_DETAILED_STATUS = BASE_URL + 'build-status/1.0/commits'
HTML_BASE_URL = 'https://bb.yandex-team.ru/projects/EDA/repos/core'
RE_LIST_PRS = re.compile(r'/pull-requests$')
RE_GET_PR = re.compile(r'/pull-requests/(?P<id>[0-9]+)$')
RE_GET_PR_REVIEWS = re.compile(r'/pull-requests/(?P<id>[0-9]+)/participants$')
RE_GET_PR_ACTIVITIES = re.compile(r'/pull-requests/(?P<id>[0-9]+)/activities$')


PR_STATE_MAP = {
    vcs_base.PullRequestState.OPEN: 'OPEN',
    vcs_base.PullRequestState.CLOSED: 'DECLINED',
    vcs_base.PullRequestState.MERGED: 'MERGED',
}

REVIEW_STATE_MAP = {
    vcs_base.ReviewState.REJECTED: 'UNAPPROVED',
    vcs_base.ReviewState.APPROVED: 'APPROVED',
    vcs_base.ReviewState.COMMENTED: 'NEEDS_WORK',
}


@dataclasses.dataclass
class BuildStatus:
    state: str
    key: str
    url: str = 'http://test-url'
    description: str = 'test description'
    dateAdded: int = 1


@dataclasses.dataclass
class PullRequest:
    pull_id: int
    repo_path: str
    branch: str
    target_branch: str
    author: str
    self_url: str
    title: Optional[str] = None
    merge_commit: Optional[str] = None
    latest_commit: Optional[str] = None
    reviews: List[vcs_base.Review] = dataclasses.field(default_factory=list)
    build_status: Optional[List[BuildStatus]] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None

    def __post_init__(self):
        now = int(datetime.datetime.now().timestamp())
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
        if self.title is None:
            self.title = 'feat all: do stuff'


class BitbucketMock:
    def __init__(self, response_cls, tmpdir) -> None:
        self._response_cls = response_cls
        self._tmpdir = tmpdir
        self._prs: Dict[int, PullRequest] = {}
        self._handlers: Dict[Tuple[str, str], Callable] = {
            ('GET', f'{BASE_URL_PULL_REQUESTS}'): self._list_prs,
            (
                'GET',
                f'{BASE_URL_COMMIT_DETAILED_STATUS}',
            ): self._detailed_build_status_for_commit,
        }

    def create_pr(
            self,
            repo: git.Repo,
            commits: Iterable[repository.Commit],
            branch: str = 'feature',
            title: Optional[str] = None,
            login: str = 'alberist',
            target_branch: str = 'develop',
            state: str = 'open',
            merge: bool = False,
            merge_message: str = '',
            reviews: Iterable[vcs_base.Review] = (),
            build_status: Optional[List[BuildStatus]] = None,
            created_at: Optional[int] = None,
            updated_at: Optional[int] = None,
    ) -> PullRequest:
        pull_id = len(self._prs) + 1

        old_active_branch = repo.active_branch
        repo.git.config('user.name', f'User {login}')
        repo.git.config('user.email', f'{login}@yandex-team.ru')

        if target_branch not in repo.branches:
            repo.git.branch(target_branch, 'develop')
        repo.git.checkout(target_branch)
        repo.git.checkout('-b', branch)
        repository.apply_commits(repo, commits)

        repo.git.push('origin', f'{branch}:refs/pull-requests/{pull_id}/from')

        if merge:
            repo.git.checkout(target_branch)
            repo.git.merge('--squash', branch)
            repo.git.commit('-m', merge_message.format(number=pull_id))
            merge_commit = repo.git.rev_parse('HEAD')
            repo.git.push('origin', target_branch)
        else:
            merge_commit = None

        latest_commit = repo.git.rev_parse('HEAD') + f'_{pull_id}'

        repo.git.checkout(old_active_branch)

        self._handlers[
            'GET', f'{BASE_URL_PULL_REQUESTS}/{pull_id}',
        ] = functools.partial(self._get_pr, pull_id)
        self._handlers[
            'GET', f'{BASE_URL_PULL_REQUESTS}/{pull_id}/activities',
        ] = functools.partial(self._get_pr_activities, pull_id)
        self._handlers[
            'GET', f'{BASE_URL_PULL_REQUESTS}/{pull_id}/participants',
        ] = functools.partial(self._get_pr_participants, pull_id)
        self._handlers[
            'GET', f'{BASE_URL_COMMIT_DETAILED_STATUS}/{latest_commit}',
        ] = (
            functools.partial(
                self._detailed_build_status_for_commit, latest_commit,
            )
        )

        self._prs[pull_id] = PullRequest(
            pull_id=pull_id,
            repo_path=repo.working_dir,
            title=title,
            author=login,
            branch=branch,
            target_branch=target_branch,
            reviews=list(reviews),
            self_url=f'{HTML_BASE_URL}/pull-requests/{pull_id}',
            merge_commit=merge_commit,
            latest_commit=latest_commit,
            build_status=build_status,
            created_at=created_at,
            updated_at=updated_at,
        )
        return self._prs[pull_id]

    def handle_request(self, method: str, url: str, **kwargs) -> dict:
        handler = self._handlers.get((method, url))
        if not handler:
            raise NotImplementedError(f'No handler for {method} {url}')

        return self._response_cls(json=handler(method, url, **kwargs))

    def _format_pr(self, pull_request: PullRequest) -> dict:
        return {
            'id': pull_request.pull_id,
            'description': 'Relates: WHATEVER-1\ndeploy:testing',
            'author': {
                'user': {
                    'name': pull_request.author,
                    'emailAddress': f'{pull_request.author}@yandex-team.ru',
                },
            },
            'state': 'OPEN' if not pull_request.merge_commit else 'MERGED',
            'toRef': {'displayId': pull_request.target_branch},
            'fromRef': {
                'displayId': pull_request.branch,
                'latestCommit': pull_request.latest_commit,
            },
            'properties': {'mergeResult': {'outcome': 'CLEAN'}},
            'version': 'whatever',
            'title': pull_request.title,
            'locked': False,
            'createdDate': pull_request.created_at,
            'updatedDate': pull_request.updated_at,
            'links': {'self': [{'href': pull_request.self_url}]},
        }

    def _get_pr(self, pr_id, *args, **kwargs) -> dict:
        pull_request = self._prs[pr_id]
        return self._format_pr(pull_request)

    def _get_pr_activities(self, pr_id, *args, **kwargs) -> dict:
        pull_request = self._prs[pr_id]

        activities = [
            {'action': 'COMMENT'},
            {'action': 'MERGED', 'commit': {'id': pull_request.merge_commit}}
            if pull_request.merge_commit
            else {'action': 'COMMENT'},
            {'action': 'COMMENT'},
        ]

        return {
            'isLastPage': True,
            'count': len(pull_request.reviews),
            'values': activities,
        }

    def _get_pr_participants(self, pr_id, *args, **kwargs) -> dict:
        pull_req = self._prs[pr_id]

        participants = [{'user': {'name': pull_req.author}, 'role': 'AUTHOR'}]
        participants.extend(
            {
                'user': {'name': review.author},
                'role': 'REVIEWER',
                'status': REVIEW_STATE_MAP[review.state],
            }
            for review in pull_req.reviews
        )

        return {
            'isLastPage': True,
            'count': len(participants),
            'values': participants,
        }

    def _list_prs(self, *args, **kwargs) -> dict:
        return {
            'isLastPage': True,
            'count': len(self._prs),
            'values': [
                self._format_pr(pr)
                for pr in sorted(self._prs.values(), key=lambda pr: pr.pull_id)
            ],
        }

    def _detailed_build_status_for_commit(self, *args, **kwargs) -> dict:
        commit_id: str = args[0]
        target_pr = None

        # pylint: disable=invalid-name
        for pr in self._prs.values():
            if pr.latest_commit == commit_id:
                target_pr = pr
                break

        if not target_pr:
            return {
                'size': 0,
                'limit': 25,
                'isLastPage': True,
                'values': [],
                'start': 0,
            }

        builds = []
        if target_pr.build_status:
            builds = target_pr.build_status
        return {
            'size': len(builds),
            'limit': 25,
            'isLastPage': True,
            'values': [dataclasses.asdict(build) for build in builds],
            'start': 0,
        }


@pytest.fixture(name='bitbucket_instance')
def _bitbucket_instance(monkeypatch, patch_requests, tmpdir):
    monkeypatch.setattr(bitbucket, 'API_TOKEN', 'foobar')
    monkeypatch.setattr(bitbucket, 'ORG', 'EDA')
    monkeypatch.setattr(bitbucket, 'REPO', 'core')

    mock = BitbucketMock(patch_requests.response, tmpdir)
    patch_requests(BASE_URL_PULL_REQUESTS)(mock.handle_request)
    patch_requests(BASE_URL_COMMIT_DETAILED_STATUS)(mock.handle_request)
    return mock
