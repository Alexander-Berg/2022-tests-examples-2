async def test_fetch_latest_commit(
        call_cube_handle, sha1, github_get_commit_mock, diff_proposal_mock,
):
    expected_commit_sha = sha1('commitsha')
    expected_tree_sha = sha1('treesha')

    get_commit_mock = github_get_commit_mock(
        commit_sha=expected_commit_sha, tree_sha=expected_tree_sha,
    )
    df_mock, _ = diff_proposal_mock()
    input_data = {
        'user': df_mock.user,
        'repo': df_mock.repo,
        'branch_name': df_mock.base,
    }

    await call_cube_handle(
        'GithubFetchLatestCommit',
        {
            'data_request': {
                'input_data': input_data,
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
            'content_expected': {
                'payload': {
                    'commit_sha': expected_commit_sha,
                    'tree_sha': expected_tree_sha,
                },
                'status': 'success',
            },
        },
    )
    assert len(get_commit_mock.calls) == 1


async def test_create_commit(
        call_cube_handle,
        sha1,
        github_create_commit_object_mock,
        diff_proposal_mock,
):
    expected_commit_sha = sha1('newcommitsha')
    expected_parent_commit_sha = sha1('parentcommitsha')
    expected_tree_sha = sha1('treesha')
    expected_message = 'test_test'

    create_commit_object_mock = github_create_commit_object_mock(
        parents=[expected_parent_commit_sha],
        new_commit_sha=expected_commit_sha,
        new_tree_sha=expected_tree_sha,
        commit_message=expected_message,
    )
    df_mock, _ = diff_proposal_mock()
    input_data = {
        'user': df_mock.user,
        'repo': df_mock.repo,
        'tree_sha': expected_tree_sha,
        'message': expected_message,
        'parent_commit_sha': expected_parent_commit_sha,
    }

    await call_cube_handle(
        'GithubCreateCommit',
        {
            'data_request': {
                'input_data': input_data,
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
            'content_expected': {
                'payload': {'commit_sha': expected_commit_sha},
                'status': 'success',
            },
        },
    )
    assert len(create_commit_object_mock.calls) == 1
