import pytest

START_COMMENT_TEMPLATE = (
    'start_comment: {taskgroup_id}, {nanny_name}, {reallocation_id}'
)

END_COMMENT_TEMPLATE = (
    'end comment: {taskgroup_id}, {nanny_name}, {reallocation_id}'
)

START_COMMENT_RESULT = (
    'start_comment: deploy-0000095890, ' 'test_service_stable, test_id'
)

END_COMMENT_RESULT = (
    'end comment: deploy-0000095890, ' 'test_service_stable, test_id'
)

TRANSLATIONS = {
    'tickets.nanny_force_reallocation_start_comment': {
        'ru': START_COMMENT_TEMPLATE,
    },
    'tickets.nanny_force_reallocation_end_comment': {
        'ru': END_COMMENT_TEMPLATE,
    },
}


@pytest.mark.parametrize(
    'start_comment, end_comment',
    [
        pytest.param(
            'tickets.nanny_force_reallocation_start_comment',
            'tickets.nanny_force_reallocation_end_comment',
            id='without_translations',
        ),
        pytest.param(
            START_COMMENT_RESULT,
            END_COMMENT_RESULT,
            marks=pytest.mark.translations(clownductor=TRANSLATIONS),
            id='with_translations',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_force_reallocation_comment_text(
        call_cube_handle,
        nanny_mockserver,
        original_allocation_request,
        start_comment,
        end_comment,
):
    await call_cube_handle(
        'NannyForceReallocationCommentText',
        {
            'content_expected': {
                'payload': {
                    'start_comment': start_comment,
                    'end_comment': end_comment,
                    'comment_props': {'summonees': ['karachevda']},
                    'key_phrase': 'Rollback reallocation',
                    'rollback_comment': (
                        'tickets.nanny_force_reallocation_rollback_comment'
                    ),
                },
                'status': 'success',
            },
            'data_request': {
                'input_data': {
                    'reallocation_id': 'test_id',
                    'nanny_name': 'test_service_stable',
                    'allocation_request': original_allocation_request,
                    'user': 'karachevda',
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
