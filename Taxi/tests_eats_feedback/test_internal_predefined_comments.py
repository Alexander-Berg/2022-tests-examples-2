import pytest


@pytest.mark.parametrize(
    ['params', 'result_json'],
    [
        [
            {'predefined_comment_id': 1, 'user_locale': 'ru'},
            'predefined_comment_1.json',
        ],
        [
            {
                'predefined_comment_id': 1,
                'version': 'short',
                'user_locale': 'ru',
            },
            'predefined_comment_1.json',
        ],
        [
            {
                'predefined_comment_id': 20,
                'show_deleted': False,
                'user_locale': 'ru',
            },
            'predefined_comment_20.json',
        ],
        [{'user_locale': 'ru'}, 'predefined_comments.json'],
        [
            {'show_deleted': False, 'user_locale': 'ru'},
            'predefined_comments.json',
        ],
        [
            {'show_deleted': True, 'user_locale': 'ru'},
            'predefined_comments_with_deleted.json',
        ],
        [
            {'version': 'short', 'user_locale': 'ru'},
            'predefined_comments_short_version.json',
        ],
        [
            {'show_deleted': True, 'version': 'default', 'user_locale': 'ru'},
            'predefined_comments_default_version_with_deleted.json',
        ],
    ],
    ids=[
        'predefined_comment_id=1',
        'predefined_comment_id=1, ignored version=short',
        'predefined_comment_id=20, ignored show_deleted=False',
        'default',
        'show_deleted=False',
        'show_deleted=True',
        'version=short',
        'show_deleted=True&version=default',
    ],
)
@pytest.mark.pgsql(
    'eats_feedback', files=['predefined_comments.sql', 'test_comments.sql'],
)
async def test_get_predefined_comments(
        load_json, taxi_eats_feedback, params, result_json,
):
    response = await taxi_eats_feedback.get(
        '/internal/eats-feedback/v1/predefined-comments', params=params,
    )
    assert response.status_code == 200
    assert response.json() == load_json(result_json)
