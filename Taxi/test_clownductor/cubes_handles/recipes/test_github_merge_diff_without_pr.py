import pytest


@pytest.fixture(name='client_github_mock')
def _client_github_mock(
        patch,
        github_get_commit_mock,
        github_create_reference_mock,
        github_create_blob_mock,
        github_create_tree_mock,
        github_create_commit_object_mock,
        github_update_reference_mock,
        github_merge_branch_object_mock,
        github_delete_reference_mock,
):
    def _wrapper(
            base_commit_sha,
            base_tree_sha,
            new_tree_sha,
            new_commit_sha,
            commit_message,
            head_branch_name,
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

    return _wrapper


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_recipe(
        load_yaml,
        task_processor,
        run_job_common,
        sha1,
        diff_proposal_mock,
        client_github_mock,
):
    df_mock, df_sha = diff_proposal_mock()
    expected = {
        'diff_proposal': df_mock.serialize(),
        'st_ticket': None,
        'user': 'taxi',
        'repo': 'infra-cfg-graphs',
        'changes_title': df_mock.title,
        'base_branch_name': 'develop',
        'head_branch_name': f'update-config-{df_sha}',
        'diff_proposal_sha': df_sha,
        'base_commit_sha': sha1('basecommitsha'),
        'head_commit_sha': sha1('newcommitsha'),
        'merge_sha': 'e3443502b8fd692b789f9af514b335bce53f0667',
        'base_tree_sha': sha1('basetreesha'),
        'head_tree_sha': sha1('newtreesha'),
        'blobs_sha_by_filepaths': {
            'path/to/file.yaml': 'aee925e4cf25dc7a7187cff4e124d7fb82cf235f',
            'path/to/file2.yaml': '24e4ff850d939327d348dcaf66d819a1faa4ebe8',
        },
    }
    client_github_mock(
        base_commit_sha=expected['base_commit_sha'],
        base_tree_sha=expected['base_tree_sha'],
        new_tree_sha=expected['head_tree_sha'],
        new_commit_sha=expected['head_commit_sha'],
        commit_message=expected['changes_title'],
        head_branch_name=expected['head_branch_name'],
    )

    recipe = task_processor.load_recipe(
        load_yaml('recipes/GithubMergeDiffProposalWithoutPR.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={'diff_proposal': df_mock.serialize(), 'st_ticket': None},
        initiator='clownductor',
    )
    await run_job_common(job)

    assert job.job_vars == expected
