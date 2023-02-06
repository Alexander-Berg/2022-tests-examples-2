import pytest

START_COMMENT_TEMPLATE = (
    'start comment: {old_flavor}, {new_flavor}, {operation_id}, {folder_id}, '
    '{mdb_type}, {cluster_id}'
)

END_COMMENT_TEMPLATE = (
    'end comment: {old_flavor}, {new_flavor}, {operation_id}, {folder_id}, '
    '{mdb_type}, {cluster_id}'
)

ROLLBACK_COMMENT_TEMPLATE = 'rollback comment: {key_phrase}'

START_COMMENT_RESULT = (
    'start comment: s2.micro, s2.large, '
    'operation-id, folder-id, mongodb, cluster-id'
)

END_COMMENT_RESULT = (
    'end comment: s2.micro, s2.large, '
    'operation-id, folder-id, mongodb, cluster-id'
)

ROLLBACK_COMMENT_RESULT = 'rollback comment: Rollback reallocation'

TRANSLATIONS = {
    'tickets.mdb_force_reallocation_start_comment': {
        'ru': START_COMMENT_TEMPLATE,
    },
    'tickets.mdb_force_reallocation_end_comment': {'ru': END_COMMENT_TEMPLATE},
    'tickets.mdb_force_reallocation_rollback_comment': {
        'ru': ROLLBACK_COMMENT_TEMPLATE,
    },
}


@pytest.mark.parametrize(
    'start_comment, end_comment, rollback_comment',
    [
        pytest.param(
            'tickets.mdb_force_reallocation_start_comment',
            'tickets.mdb_force_reallocation_end_comment',
            'tickets.mdb_force_reallocation_rollback_comment',
            id='without_translations',
        ),
        pytest.param(
            START_COMMENT_RESULT,
            END_COMMENT_RESULT,
            ROLLBACK_COMMENT_RESULT,
            marks=pytest.mark.translations(clownductor=TRANSLATIONS),
            id='with_translations',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_force_reallocation_comment_text(
        call_cube_handle, start_comment, end_comment, rollback_comment,
):
    await call_cube_handle(
        'MDBForceReallocationCommentText',
        {
            'content_expected': {
                'payload': {
                    'start_comment': start_comment,
                    'end_comment': end_comment,
                    'comment_props': {'summonees': ['karachevda']},
                    'key_phrase': 'Rollback reallocation',
                    'rollback_comment': rollback_comment,
                },
                'status': 'success',
            },
            'data_request': {
                'input_data': {
                    'old_flavor': 's2.micro',
                    'new_flavor': 's2.large',
                    'operation_id': 'operation-id',
                    'folder_id': 'folder-id',
                    'cluster_id': 'cluster-id',
                    'db_type': 'mongo',
                    'user': 'karachevda',
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
