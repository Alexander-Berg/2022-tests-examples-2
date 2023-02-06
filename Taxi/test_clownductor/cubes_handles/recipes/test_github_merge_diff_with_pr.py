import pytest

from client_github import components as client_github

from clownductor.internal.utils.links import startrack


@pytest.fixture(name='client_github_mock')
def _client_github_mock(
        patch,
        github_get_commit_mock,
        github_create_reference_mock,
        github_update_reference_mock,
        github_delete_reference_mock,
        github_create_blob_mock,
        github_create_tree_mock,
        github_create_commit_object_mock,
        github_merge_branch_object_mock,
        github_get_pull_request_mock,
        github_create_pull_request_mock,
):
    def _wrapper(
            base_commit_sha,
            base_tree_sha,
            new_tree_sha,
            new_commit_sha,
            commit_message,
            head_branch_name,
            pr_number,
            pr_url,
    ):
        github_get_commit_mock(
            commit_sha=base_commit_sha, tree_sha=base_tree_sha,
        )
        github_create_reference_mock(commit_sha=base_commit_sha)
        github_create_blob_mock()
        github_create_tree_mock(
            updated_node_count=2,
            deleted_node_count=1,
            new_tree_sha=new_tree_sha,
        )
        github_create_commit_object_mock(
            parents=[base_commit_sha],
            new_commit_sha=new_commit_sha,
            new_tree_sha=new_tree_sha,
            commit_message=commit_message,
        )
        github_update_reference_mock(commit_sha=new_commit_sha)
        github_merge_branch_object_mock(head_branch_name=head_branch_name)
        github_delete_reference_mock(branch_name=head_branch_name)
        github_create_pull_request_mock(pr_number=pr_number, pr_url=pr_url)
        github_get_pull_request_mock(
            number=pr_number,
            pr_url=pr_url,
            mergeable=True,
            merged=True,
            state=client_github.PullRequestState('closed'),
        )

    return _wrapper


@pytest.fixture(name='startrack_client_mock')
def _startrack_client_mock(st_get_myself, st_get_comments, st_create_comment):
    pass


@pytest.mark.usefixtures('startrack_client_mock')
async def test_recipe(
        load_yaml,
        task_processor,
        run_job_common,
        sha1,
        diff_proposal_mock,
        client_github_mock,
):
    df_mock, df_sha = diff_proposal_mock()
    st_ticket = 'TAXIREL-123'
    reviewers = ['spolischouck']
    expected_pr_number = 123
    expected_pr_url = 'test-pr-url'

    expected = {
        'diff_proposal': df_mock.serialize(),
        'st_ticket': st_ticket,
        'automerge': False,
        'reviewers': reviewers,
        'user': 'taxi',
        'repo': 'infra-cfg-graphs',
        'changes_title': df_mock.title,
        'base_branch_name': 'develop',
        'head_branch_name': f'{st_ticket}-update-config-{df_sha}',
        'diff_proposal_sha': df_sha,
        'base_commit_sha': sha1('basecommitsha'),
        'head_commit_sha': sha1('newcommitsha'),
        'base_tree_sha': sha1('basetreesha'),
        'head_tree_sha': sha1('newtreesha'),
        'blobs_sha_by_filepaths': {
            'path/to/file.yaml': 'aee925e4cf25dc7a7187cff4e124d7fb82cf235f',
            'path/to/file2.yaml': '24e4ff850d939327d348dcaf66d819a1faa4ebe8',
        },
        'pull_request_id': expected_pr_number,
        'pull_request_url': expected_pr_url,
        'pull_request_title': df_mock.title,
        'pull_request_body': (
            'Update configs during job#1\n\n'
            'Tests: сгенерировано автоматикой\n'
            f'Relates: [{st_ticket}]({startrack.ST_HOST}/{st_ticket})\n'
        ),
        'pull_request_labels': [],
        'pull_request_state': 'closed',
        'pull_request_st_comment_props': {'summonees': reviewers},
        'comment_pr_is_merged': (
            f'(({expected_pr_url} PR #{expected_pr_number})) is merged.'
        ),
        'comment_pr_is_ready_to_review': (
            'PR is ready to review.\n'
            f'Approve and merge (({expected_pr_url} PR #{expected_pr_number}))'
        ),
    }
    client_github_mock(
        base_commit_sha=expected['base_commit_sha'],
        base_tree_sha=expected['base_tree_sha'],
        new_tree_sha=expected['head_tree_sha'],
        new_commit_sha=expected['head_commit_sha'],
        commit_message=expected['changes_title'],
        head_branch_name=expected['head_branch_name'],
        pr_number=expected_pr_number,
        pr_url=expected_pr_url,
    )

    recipe = task_processor.load_recipe(
        load_yaml('recipes/GithubMergeDiffProposalWithPR.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={
            'diff_proposal': df_mock.serialize(),
            'st_ticket': st_ticket,
            'automerge': False,
            'reviewers': reviewers,
        },
        initiator='clownductor',
    )
    await run_job_common(job)

    assert job.job_vars == expected
