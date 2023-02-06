import copy
import hashlib

import pytest

from arc_api import types as arc_types
from arcanum_api import components as arcanum_api
from arcanum_api import types as arcanum_types
from yandex.arc.api.public import repo_pb2
from yandex.arc.api.public import shared_pb2

from clownductor.internal.utils.links import startrack


@pytest.fixture(name='arc_client_mock')
def _arc_client_mock(
        patch,
        arc_mockserver,
        patch_commit_service,
        patch_branch_service,
        patch_arc_get_commit,
        patch_arc_create_commit,
        patch_arc_set_reference,
        patch_arc_delete_reference,
):
    def _wrapper(
            base: str,
            base_commit: shared_pb2.Commit,
            new_commit: shared_pb2.Commit,
    ):
        create_commit_mock = patch_arc_create_commit(
            responses=[
                arc_types.ResponseMock(
                    message=repo_pb2.CommitFileResponse(Commit=new_commit),
                ),
            ],
            init_mockserver=False,
        )

        get_commit_mock = patch_arc_get_commit(
            revision=base, commit=base_commit, init_mockserver=False,
        )
        set_reference_mock = patch_arc_set_reference(
            responses=[
                arc_types.ResponseMock(message=repo_pb2.SetRefResponse()),
            ],
            init_mockserver=False,
        )
        delete_ref_mock = patch_arc_delete_reference(
            responses=[
                arc_types.ResponseMock(message=repo_pb2.DeleteRefResponse()),
            ],
            init_mockserver=False,
        )

        commit_service_mock = patch_commit_service(
            commit_file=create_commit_mock, get_commit=get_commit_mock,
        )
        branch_service_mock = patch_branch_service(
            set_ref=set_reference_mock, delete_ref=delete_ref_mock,
        )
        arc_mockserver(commit_service_mock, branch_service_mock)

    return _wrapper


@pytest.fixture(name='arcanum_client_mock')
def _arcanum_client_mock(
        arcanum_pull_request_mock,
        patch_arcanum_pr_handler,
        arcanum_get_review_request_mock,
):
    def _wrapper(pr_number: int, pr_url: str):
        pr_open_mock = arcanum_pull_request_mock(
            pr_number=pr_number,
            pr_url=pr_url,
            status=arcanum_api.PullRequestStatus.OPEN,
        )
        pr_merged_mock = arcanum_pull_request_mock(
            pr_number=pr_number,
            pr_url=pr_url,
            status=arcanum_api.PullRequestStatus.MERGED,
        )

        create_pull_request_mock = patch_arcanum_pr_handler(
            number=None,
            responses=[
                arcanum_types.ResponseMock(
                    body={'data': pr_open_mock.serialize()}, status=200,
                ),
            ],
        )
        get_pull_request_mock = patch_arcanum_pr_handler(
            number=pr_number,
            responses=[
                arcanum_types.ResponseMock(
                    body={'data': pr_merged_mock.serialize()}, status=200,
                ),
            ],
        )
        get_review_request_mock = arcanum_get_review_request_mock(
            pr_number=pr_number,
            pr_url=pr_url,
            full_status=arcanum_api.PullRequestStatus.OPEN,
        )

        return (
            create_pull_request_mock,
            get_pull_request_mock,
            get_review_request_mock,
        )

    return _wrapper


@pytest.fixture(name='startrack_client_mock')
def _startrack_client_mock(st_get_myself, st_get_comments, st_create_comment):
    pass


@pytest.mark.usefixtures('startrack_client_mock')
async def test_recipe(
        arc_commit_mock,
        arc_client_mock,
        arcanum_client_mock,
        diff_proposal_mock,
        load_yaml,
        task_processor,
        run_job_common,
):
    st_ticket = 'TAXIREL-123'
    base = 'trunk'
    repo_owner = 'arcadia'
    repo = 'backend-py3'
    filepath = 'path/to/service.yaml'
    file = {
        'filepath': filepath,
        'state': 'created_or_updated',
        'data': 'Content1',
    }
    df_mock, df_sha = diff_proposal_mock(
        user=repo_owner, repo=repo, base=base, changes=[file],
    )

    expected_pr_number = 123
    expected_pr_url = 'test-pr-url'
    expected_user = 'robot-taxi-clown'
    expected_message = 'test commit'
    expected_branch = f'{st_ticket}-update-config-{df_sha}'
    expected_base_commit = copy.deepcopy(arc_commit_mock)
    expected_new_commit = copy.deepcopy(arc_commit_mock)
    expected_new_commit.Oid = hashlib.sha1(
        filepath.encode('utf-8'),
    ).hexdigest()
    expected_new_commit.Message = expected_message
    expected_new_commit.Author = expected_user
    expected_filepath = f'{df_mock.repo}/{filepath}'

    expected = {
        'st_ticket': st_ticket,
        'automerge': True,
        'reviewers': ['spolischouck'],
        'approve_required': False,
        'robot_for_ship': None,
        'check_files_comment_props': {},
        'check_files_comment_skip': True,
        'check_files_comment_text': '',
        'diff_proposal': df_mock.serialize(),
        'diff_proposal_sha': df_sha,
        'user': expected_user,
        'repo': repo,
        'changes_title': df_mock.title,
        'base_branch_name': base,
        'head_branch_name': expected_branch,
        'base_commit_oid': expected_base_commit.Oid,
        'head_commit_oid': expected_new_commit.Oid,
        'commits_oid_by_filepaths': {
            expected_filepath: expected_new_commit.Oid,
        },
        'pull_request_id': expected_pr_number,
        'pull_request_url': expected_pr_url,
        'pull_request_title': df_mock.title,
        'pull_request_body': (
            'Update configs during job#1\n\n'
            'Tests: сгенерировано автоматикой\n'
            f'Relates: [{st_ticket}]({startrack.ST_HOST}/{st_ticket})\n'
        ),
        'pull_request_state': arcanum_api.PullRequestStatus.MERGED.value,
        'pull_request_st_comment_props': {'summonees': ['spolischouck']},
        'comment_pr_is_merged': (
            f'(({expected_pr_url} PR #{expected_pr_number})) is merged.'
        ),
        'comment_pr_is_ready_to_review': (
            'PR is ready to review.\n'
            f'Approve and merge (({expected_pr_url} PR #{expected_pr_number}))'
        ),
    }

    arc_client_mock(
        base=base,
        base_commit=expected_base_commit,
        new_commit=expected_new_commit,
    )
    arcanum_client_mock(pr_number=expected_pr_number, pr_url=expected_pr_url)

    recipe = task_processor.load_recipe(
        load_yaml('recipes/ArcadiaMergeDiffProposalWithPR.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={
            'diff_proposal': df_mock.serialize(),
            'st_ticket': st_ticket,
            'automerge': True,
            'reviewers': ['spolischouck'],
            'approve_required': False,
            'robot_for_ship': None,
        },
        initiator='clownductor',
    )
    await run_job_common(job)

    assert job.job_vars == expected
