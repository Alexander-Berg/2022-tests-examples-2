import datetime
import logging
import os
import re
from typing import Iterable
from typing import Optional

import pytest

from taxi_buildagent.clients import vcs_base
from tests.utils import repository

BASE_URL = 'https://github.yandex-team.ru/api/v3/'
DELETE_LABEL_RE = re.compile('^issues/([0-9]+)/labels/(.*)$')
HTML_URL = 'https://github.yandex-team.ru/%s/%s/pull/%d'


logger = logging.getLogger(__name__)


class GithubError(NotImplementedError):
    pass


REVIEW_STATE_MAP = {
    vcs_base.ReviewState.REJECTED: 'REQUEST_CHANGES',
    vcs_base.ReviewState.APPROVED: 'APPROVED',
    vcs_base.ReviewState.COMMENTED: 'COMMENTED',
}


# pylint: disable=too-many-instance-attributes, too-many-arguments
class PullRequest:
    def __init__(
            self,
            path,
            number,
            url,
            state,
            commit,
            statuses_url,
            target_branch,
            labels,
            login,
            title,
            branch,
            mergeable,
            updated,
            files,
            statuses,
            html_url,
            reviews: Iterable[vcs_base.Review],
            fetchable,
            merge_commit_sha: Optional[str] = None,
            merged: bool = False,
    ):
        self.path = path
        self.number = number
        self.url = url
        self.html_url = html_url
        self.state = state
        self.commit = commit
        self.statuses_url = statuses_url
        self.target_branch = target_branch
        self.labels = labels
        self.login = login
        self.title = title
        self.branch = branch
        self.mergeable = mergeable
        self.updated = updated
        self.files = files
        self.statuses = statuses
        self.reviews = [
            {
                'user': {'login': review.author},
                'state': REVIEW_STATE_MAP[review.state],
            }
            for review in reviews
        ]
        self.fetchable = fetchable
        self.merge_commit_sha = merge_commit_sha
        self.merged = merged

    @property
    def data(self):
        return {
            'base': {'ref': self.target_branch},
            'state': self.state,
            'number': self.number,
            'head': {
                'repo': {'owner': {'login': self.login}, 'ssh_url': self.path},
                'ref': self.branch,
            },
            'mergeable': self.mergeable,
            'statuses_url': self.statuses_url,
            'html_url': self.html_url,
            'updated_at': self.updated,
            'merged': self.merged,
            'merge_commit_sha': self.merge_commit_sha,
        }


class Repository:
    def __init__(self, org, repo, path):
        self.org = org
        self.repo = repo
        self.path = path
        self.pull_requests = []
        self.pr_repos = {}

    def issues(self, method, path, params):
        if path == 'issues':
            response = []
            has_label = params and 'labels' in params
            for prq in self.pull_requests:
                data = {
                    'pull_request': {'url': prq.url},
                    'number': prq.number,
                    'title': prq.title,
                    'html_url': prq.html_url,
                    'user': {'login': prq.login},
                    'updated_at': prq.updated,
                }
                if has_label:
                    if params['labels'] in prq.labels:
                        response.append(data)
                else:
                    response.append(data)
            return response

        match = DELETE_LABEL_RE.match(path)
        if method.upper() == 'DELETE' and match:
            number = int(match.group(1))
            label = match.group(2)
            for prq in self.pull_requests:
                if prq.number == number:
                    prq.labels.remove(label)
                    break
            else:
                raise GithubError('bad request path: %s' % path)
            return ''

        raise GithubError('bad request path: %s' % path)

    def pulls(self, url):
        for prq in self.pull_requests:
            if prq.url == url:
                return prq.data
            if prq.url + '/files' == url:
                return [{'filename': filename} for filename in prq.files]
            if prq.url + '/reviews' == url:
                return prq.reviews
        raise GithubError('bad url')

    def statuses(self, url):
        for prq in self.pull_requests:
            if prq.statuses_url == url:
                return prq.statuses
        raise GithubError('bad url')

    # pylint: disable=too-many-arguments, too-many-locals
    def create_pr(
            self,
            repo,
            branch,
            title=None,
            labels=(),
            login='alberist',
            state='open',
            target_branch='develop',
            mergeable=None,
            updated=None,
            statuses=(),
            commits=(),
            reviews=(),
            number=None,
            fetchable=True,
            merge=False,
            merge_message='Merge pull request (#{number})',
    ):
        number = number or len(self.pull_requests) + 1
        url = '%srepos/%s/%s/pulls/%d' % (
            BASE_URL,
            self.org,
            self.repo,
            number,
        )

        if login in self.pr_repos:
            pr_repo = self.pr_repos[login]
        else:
            path = os.path.join(
                os.path.dirname(repo.working_tree_dir),
                'pr_%s_%s_%s' % (self.org, self.repo, login),
            )
            self.pr_repos[login] = pr_repo = repo.clone(path)
            pr_repo.git.remote('add', 'upstream', self.path)
        pr_repo.git.config('user.name', 'User ' + login)
        pr_repo.git.config('user.email', login + '@yandex-team.ru')
        pr_repo.git.checkout(target_branch)
        pr_repo.git.checkout('-b', branch)
        files = set()
        for commit in commits:
            files.update(commit.files)
            for submodule_commit in commit.submodules:
                if isinstance(submodule_commit, repository.SubmoduleCommits):
                    submodule = submodule_commit.path
                else:
                    submodule = submodule_commit[0]
                files.add(submodule)
        repository.apply_commits(pr_repo, commits)
        commit_sha = pr_repo.commit().hexsha
        if fetchable:
            pr_repo.git.push(
                'upstream', '%s:refs/pull/%d/head' % (branch, number),
            )
        statuses_url = '%srepos/%s/%s/statuses/%s' % (
            BASE_URL,
            self.org,
            self.repo,
            commit_sha,
        )

        if merge:
            # Simulate merging PRs through GitHub
            pr_repo.git.checkout(target_branch)
            pr_repo.git.merge('--squash', branch)
            pr_repo.git.commit('-m', merge_message.format(number=number))
            pr_repo.git.push('upstream', target_branch)
        else:
            # Even if not merged, merge_commit_sha has to be populated
            # because a temporary merge head is always there.
            # Makes tests fail if one uses merge_commit_sha for checking
            # whether a PR was merged or not (use `merged` property instead)
            pr_repo.git.checkout(target_branch)
            pr_repo.git.checkout('-b', f'merge/{number}')
            pr_repo.git.merge('--no-edit', '--no-ff', branch)
        merge_commit_sha = pr_repo.git.rev_parse('HEAD')
        logger.info(f'Merged PR #{number} as {merge_commit_sha}')
        pr_repo.git.checkout(branch)

        if updated is None:
            updated = datetime.datetime.utcnow()
        if isinstance(updated, datetime.datetime):
            updated = updated.strftime('%Y-%m-%dT%H:%M:%SZ')
        html_url = HTML_URL % (self.org, self.repo, number)
        if title is None:
            title = 'feat all: make good'
        self.pull_requests.append(
            PullRequest(
                path=pr_repo.working_tree_dir if fetchable else 'dummy',
                number=number,
                url=url,
                labels=labels,
                state=state,
                commit=commit_sha,
                statuses_url=statuses_url,
                target_branch=target_branch,
                login=login,
                title=title,
                branch=branch,
                mergeable=mergeable,
                updated=updated,
                files=files,
                statuses=statuses,
                html_url=html_url,
                reviews=reviews,
                fetchable=fetchable,
                merge_commit_sha=merge_commit_sha,
                merged=merge,
            ),
        )
        return html_url


class Github:
    def __init__(self, patch_requests):
        self._response = patch_requests.response
        self._request = patch_requests(BASE_URL)(self._request_to_patch)
        self._repos = {}

    def init_repo(self, org, repo, path):
        assert (org, repo) not in self._repos
        self._repos[(org, repo)] = result = Repository(org, repo, path)
        return result

    def _request_to_patch(self, method, url, **kwargs):
        headers = kwargs.get('headers', {})
        params = kwargs.get('params', '')
        assert headers['Authorization'] == 'token gtoken'
        path = url[len(BASE_URL) :]
        if not path.startswith('repos/'):
            raise GithubError('Bad url: %s' % url)
        _, org, repo, path = path.split('/', 3)
        if (org, repo) not in self._repos:
            raise GithubError('Unknown project %s/%s' % (org, repo))
        repo = self._repos[(org, repo)]
        if path.startswith('issues'):
            return self._response(
                json=repo.issues(method, path, params=params),
            )
        if path.startswith('pulls'):
            if method.upper() != 'GET':
                raise GithubError('Bad method %s for url: %s' % (method, url))
            return self._response(json=repo.pulls(url))
        if path.startswith('statuses'):
            if method.upper() != 'GET':
                raise GithubError('Bad method %s for url: %s' % (method, url))
            return self._response(json=repo.statuses(url))
        raise GithubError('Bad url: %s' % url)


@pytest.fixture
def github(monkeypatch, patch_requests):
    monkeypatch.setattr('taxi_buildagent.clients.github.API_TOKEN', 'gtoken')
    monkeypatch.setattr('taxi_buildagent.clients.github.ORG', 'taxi')
    monkeypatch.setattr('taxi_buildagent.clients.github.REPO', 'backend')
    result = Github(patch_requests)
    return result
