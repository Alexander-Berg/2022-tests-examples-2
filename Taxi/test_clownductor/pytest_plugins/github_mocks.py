from typing import List
from typing import Optional

import pytest

from client_github import components as github
from client_github import types as gh_client_mock_types


@pytest.fixture(name='github_resp')
def _github_resp(relative_load_json):
    return relative_load_json('github_responses.json')[0]


@pytest.fixture(name='mock_github')
def _mock_github(
        patch_aiohttp_session,
        patch_blobs_handler,
        patch_get_commit,
        patch_create_commit_object,
        response_mock,
        simple_secdist,
        relative_load_json,
        github_resp,
):
    def _do_it(github_responses=github_resp, github_api_url=None):
        simple_secdist['settings_override'].update(
            {'GITHUB_TOKEN': 'github_oauth'},
        )
        if github_api_url is None:
            github_api_url = (
                'https://github.yandex-team.ru'
                '/api/v3/repos/taxi/infra-cfg-graphs/'
            )

        if 'git_blobs' in github_responses:
            patch_blobs_handler(
                user='taxi',
                repo='infra-cfg-graphs',
                sha=None,
                responses=[
                    gh_client_mock_types.ResponseMock(
                        body=resp['json'], status=resp['status'],
                    )
                    for resp in github_responses['git_blobs']
                ],
            )

        patch_get_commit(
            user='taxi',
            repo='infra-cfg-graphs',
            ref='generated',
            responses=[
                gh_client_mock_types.ResponseMock(
                    body=resp['json'], status=resp['status'],
                )
                for resp in relative_load_json(
                    'github_get_commits_generated_responses.json',
                )
            ],
        )

        get_commit_response = relative_load_json(
            'github_get_commit_response.json',
        )
        override_commit_response = github_responses.get(
            'commits_7025192b9f3032cec800c5d1de386a5b4ccb8c4e',
        )
        if override_commit_response:
            get_commit_response['commit']['tree'] = override_commit_response[
                'content'
            ]['commit']['tree']
            get_commit_response['sha'] = override_commit_response['content'][
                'sha'
            ]
            get_commit_response['files'] = override_commit_response['content'][
                'files'
            ]
            get_commit_response['stats'] = override_commit_response['content'][
                'stats'
            ]

            patch_get_commit(
                user='taxi',
                repo='infra-cfg-graphs',
                ref='7025192b9f3032cec800c5d1de386a5b4ccb8c4e',
                responses=[
                    gh_client_mock_types.ResponseMock(
                        body=get_commit_response,
                        status=override_commit_response['status'],
                    ),
                ],
            )

        patch_create_commit_object(
            user='taxi',
            repo='infra-cfg-graphs',
            responses=[
                gh_client_mock_types.ResponseMock(
                    body=resp['json'], status=resp['status'],
                )
                for resp in relative_load_json(
                    'github_create_commit_responses.json',
                )
            ],
        )

        @patch_aiohttp_session(github_api_url)
        def handler(method, url, **kwargs):
            method_url = url.replace(github_api_url, '').replace('/', '_')
            return response_mock(
                json=github_responses[method_url]['content'],
                status=github_responses[method_url]['status'],
            )

        return handler

    return _do_it


@pytest.fixture(name='github_merge_pull')
async def _merge_pull(patch):
    @patch('client_github.components.GithubClient.merge_pull')
    async def _handler(_):
        return


@pytest.fixture(name='github_get_pull')
async def _get_pull(patch):
    @patch('client_github.components.GithubClient.get_pull')
    async def _handler(*args, **kwargs):
        return {'deletions': 'temp', 'title': 'blah', 'body': 'more blah'}

    return _handler


@pytest.fixture(name='create_file_change_proposal')
async def _create_file_change_proposal(patch):
    @patch(
        'client_github.components.GithubClient.' 'create_file_change_proposal',
    )
    async def _handler(*args, **kwargs):
        return github.CreatePullRequestResult(
            html_url='gh-test-url.yandex-team.ru', number=228,
        )


@pytest.fixture(name='create_files_and_push_to_branch')
async def _create_files_and_push_to_branch(patch):
    @patch(
        'client_github.components.GithubClient.'
        'create_files_and_push_to_branch',
    )
    async def _handler(*args, **kwargs):
        return github.CreatePullRequestResult(
            html_url='gh-test-url.yandex-team.ru', number=228,
        )


@pytest.fixture(name='github_create_service_fixture')
async def _github_create_service_fixture(patch):
    @patch('client_github.components.GithubClient.get_pull')
    async def _get_pull(*args, **kwargs):
        return {
            'deletions': 1,
            'title': 'blah',
            'body': 'more blah',
            'mergeable': 1,
            'merge': 1,
        }

    @patch('taxi.clients_wrappers.github.GithubClient.update_issue')
    async def _update_issue(*args, **kwargs):
        return


@pytest.fixture(name='github_create_reference_mock')
async def _github_create_reference_mock(patch, git_reference_mock):
    def _wrapper(
            commit_sha: Optional[str] = None,
            exc: Optional[github.BaseError] = None,
    ):
        @patch('client_github.components.GithubClient.create_reference')
        async def _create_reference(*args, **kwargs):
            if exc:
                raise exc

            assert kwargs.pop('ref').startswith('refs/heads/')
            gh_mock = git_reference_mock(commit_sha=commit_sha)
            return gh_mock

        return _create_reference

    return _wrapper


@pytest.fixture(name='github_update_reference_mock')
async def _github_update_reference_mock(patch, git_reference_mock):
    def _wrapper(commit_sha: Optional[str] = None):
        @patch('client_github.components.GithubClient.update_reference')
        async def _update_reference(*args, **kwargs):
            assert kwargs.pop('ref').startswith('heads/')
            gh_mock = git_reference_mock(commit_sha=commit_sha)
            return gh_mock

        return _update_reference

    return _wrapper


@pytest.fixture(name='github_delete_reference_mock')
async def _github_delete_reference_mock(patch, git_reference_mock):
    def _wrapper(branch_name: str):
        @patch('client_github.components.GithubClient.delete_reference')
        async def _delete_reference(*args, **kwargs):
            assert kwargs.pop('ref') == f'heads/{branch_name}'

        return _delete_reference

    return _wrapper


@pytest.fixture(name='github_create_blob_mock')
async def _github_create_blob_mock(patch, sha1, git_blob_short_mock):
    def _wrapper():
        @patch('client_github.components.GithubClient.create_blob_')
        async def _create_blob(*args, **kwargs):
            gh_mock = git_blob_short_mock()
            gh_mock.sha = sha1(kwargs.pop('content'))
            return gh_mock

        return _create_blob

    return _wrapper


@pytest.fixture(name='github_create_tree_mock')
async def _github_create_tree_mock(patch, git_tree_mock):
    def _wrapper(
            updated_node_count: int,
            deleted_node_count: int,
            new_tree_sha: Optional[str] = None,
    ):
        @patch('client_github.components.GithubClient.create_tree')
        async def _create_tree(*args, **kwargs):
            new_tree = kwargs.pop('tree')
            assert (
                sum(1 for node in new_tree if node.sha) == updated_node_count
            )
            assert (
                sum(1 for node in new_tree if not node.sha)
                == deleted_node_count
            )

            tree_mock = git_tree_mock(
                sha=new_tree_sha, tree=[node.serialize() for node in new_tree],
            )
            return tree_mock

        return _create_tree

    return _wrapper


@pytest.fixture(name='github_get_commit_mock')
async def _github_get_commit_mock(patch, github_commit_mock):
    def _wrapper(commit_sha: str, tree_sha: str):
        @patch('client_github.components.GithubClient.get_commit_')
        async def _get_commit(*args, **kwargs):
            gh_mock = github_commit_mock(commit_sha, tree_sha)
            return gh_mock

        return _get_commit

    return _wrapper


@pytest.fixture(name='github_create_commit_object_mock')
async def _github_create_commit_object_mock(patch, git_commit_object_mock):
    def _wrapper(
            parents: List[str],
            new_commit_sha: str,
            new_tree_sha: str,
            commit_message: str,
    ):
        @patch('client_github.components.GithubClient.create_commit_object')
        async def _create_commit(*args, **kwargs):
            assert parents == kwargs.pop('parents')
            assert new_tree_sha == kwargs.pop('tree_sha')
            assert commit_message == kwargs.pop('message')
            gh_mock = git_commit_object_mock(new_commit_sha, new_tree_sha)
            return gh_mock

        return _create_commit

    return _wrapper


@pytest.fixture(name='github_merge_branch_object_mock')
async def _github_merge_branch_object_mock(patch, github_commit_mock):
    def _wrapper(head_branch_name: str):
        @patch('client_github.components.GithubClient.merge_branch_')
        async def _merge_branch(*args, **kwargs):
            assert kwargs.pop('head') == head_branch_name
            gh_mock = github_commit_mock()
            return gh_mock

        return _merge_branch

    return _wrapper


@pytest.fixture(name='github_get_pull_mock')
async def _github_get_pull(patch):
    def _wrapper(
            mergeable: bool = True, merged: bool = True, state: str = 'closed',
    ):
        @patch('client_github.components.GithubClient.get_pull')
        async def _get_pull(*args, **kwargs):
            return {
                'deletions': 'temp',
                'title': 'blah',
                'body': 'more blah',
                'mergeable': mergeable,
                'merged': merged,
                'state': state,
            }

        return _get_pull

    return _wrapper


@pytest.fixture(name='github_get_pull_request_mock')
async def _github_get_pull_request_mock(patch, github_pull_request_mock):
    def _wrapper(
            number: Optional[int] = None,
            pr_url: Optional[str] = None,
            mergeable: Optional[bool] = None,
            merged: Optional[bool] = None,
            state: Optional[github.PullRequestState] = None,
    ):
        @patch('client_github.components.GithubClient.get_pull_request')
        async def _get_pulls(*args, **kwargs):
            gh_mock = github_pull_request_mock(
                number=number,
                html_url=pr_url,
                mergeable=mergeable,
                merged=merged,
                state=state,
            )
            return gh_mock

        return _get_pulls

    return _wrapper


@pytest.fixture(name='github_github_get_pull_requests_mock')
async def _github_github_get_pull_requests_mock(
        patch, github_pull_requests_mock,
):
    def _wrapper(
            repo: Optional[str] = None,
            base_branch: Optional[str] = None,
            head_branch: Optional[str] = None,
            pr_url: Optional[str] = None,
    ):
        @patch('client_github.components.GithubClient.get_pull_requests')
        async def _get_pulls(*args, **kwargs):
            gh_mock = github_pull_requests_mock(
                repo=repo,
                base_branch=base_branch,
                head_branch=head_branch,
                pr_url=pr_url,
            )
            return gh_mock

        return _get_pulls

    return _wrapper


@pytest.fixture(name='github_create_pull_request_mock')
async def _github_create_pull_request_mock(patch, github_pull_request_mock):
    def _wrapper(
            pr_number: Optional[int] = None,
            pr_url: Optional[str] = None,
            exc: Optional[github.BaseError] = None,
    ):
        @patch('client_github.components.GithubClient.create_pull_request_')
        async def _create_pull_request(*args, **kwargs):
            if exc:
                raise exc

            gh_mock = github_pull_request_mock(pr_number, pr_url)
            return gh_mock

        return _create_pull_request

    return _wrapper


@pytest.fixture(name='patch_github')
def _patch_github(patch):
    def _wrapper():
        @patch(
            'client_github.components.GithubClient.'
            'create_file_change_proposal',
        )
        async def _create_file_change_proposal(
                *args, **kwargs,
        ) -> github.CreatePullRequestResult:
            return github.CreatePullRequestResult(html_url='', number=None)

        @patch('client_github.components.GithubClient.merge_pull')
        async def _merge_pull(*args, **kwargs):
            return

        @patch('client_github.components.GithubClient.get_pull')
        async def _get_pull(*args, **kwargs):
            return

    return _wrapper


@pytest.fixture(name='patch_github_single_file')
def _patch_github_single_file(load, patch):
    def _wrapper(path, filename):
        @patch('client_github.components.GithubClient.get_single_file')
        async def get_single_file(*args, **kwargs):
            if kwargs:
                assert kwargs['path'] == path
            try:
                data = load(filename)
            except FileNotFoundError as exc:
                raise github.BaseError(f'Client error: {exc}')
            return data.encode()

        return get_single_file

    return _wrapper


@pytest.fixture(name='patch_git_read_file_with_path')
def _patch_github_single_file_with_path(load, patch):
    def _wrapper(path):
        @patch('client_github.components.GithubClient.get_single_file')
        async def get_single_file(*args, **kwargs):
            filename = path.split('/')[-1] if path else ''
            try:
                data = load(filename)
            except FileNotFoundError as exc:
                raise github.BaseError(f'Client error: {exc}')
            return data.encode()

        return get_single_file

    return _wrapper
