import pytest


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='eats_place_rating_predefined_comments_filter',
    consumers=['eats-place-rating/predefined_comments_filter'],
    clauses=[],
    default_value={
        'enabled_comments': [
            {'code': 'BAD_PACKAGE', 'type': 'dislike'},
            {'code': 'BAD_COURIER', 'type': 'dislike'},
        ],
    },
)
async def test_predefined_comments(taxi_eats_place_rating, mockserver):
    @mockserver.json_handler(
        '/eats-feedback/internal/eats-feedback/v1/predefined-comments',
    )
    def _mock_predefined_comments(request):
        return {
            'predefined_comments': [
                {
                    'access_mask_for_order_flow': 1,
                    'calculate_average_rating_place': False,
                    'code': 'BAD_COURIER',
                    'created_at': '2020-03-19T13:04:31+00:00',
                    'deleted_at': '2020-03-30T12:32:01+00:00',
                    'generate_sorrycode': False,
                    'id': 1,
                    'show_position': 600,
                    'title': 'Не устроил курьер',
                    'type': 'dislike',
                    'version': 'default',
                },
                {
                    'access_mask_for_order_flow': 1,
                    'calculate_average_rating_place': False,
                    'code': 'BAD_PACKAGE',
                    'created_at': '2020-03-19T13:04:31+00:00',
                    'deleted_at': '2020-03-30T12:32:01+00:00',
                    'generate_sorrycode': False,
                    'id': 2,
                    'show_position': 600,
                    'title': 'Испорчена упаковка',
                    'type': 'dislike',
                    'version': 'default',
                },
                {
                    'access_mask_for_order_flow': 1,
                    'calculate_average_rating_place': False,
                    'code': 'UNNECESSARY_COMMENT',
                    'created_at': '2020-03-19T13:04:31+00:00',
                    'deleted_at': '2020-03-30T12:32:01+00:00',
                    'generate_sorrycode': False,
                    'id': 3,
                    'show_position': 600,
                    'title': 'Это мы хотим скрыть',
                    'type': 'dislike',
                    'version': 'default',
                },
                {
                    'access_mask_for_order_flow': 2,
                    'calculate_average_rating_place': False,
                    'code': 'BAD_COURIER',
                    'created_at': '2020-03-19T13:04:31+00:00',
                    'deleted_at': '2020-03-30T12:32:01+00:00',
                    'generate_sorrycode': False,
                    'id': 4,
                    'show_position': 600,
                    'title': 'Не устроил курьер',
                    'type': 'dislike',
                    'version': 'default',
                },
                {
                    'access_mask_for_order_flow': 1,
                    'calculate_average_rating_place': False,
                    'code': 'BAD_COURIER',
                    'created_at': '2020-03-19T13:04:31+00:00',
                    'deleted_at': '2020-03-30T12:32:01+00:00',
                    'generate_sorrycode': False,
                    'id': 5,
                    'show_position': 600,
                    'title': 'Это мы тоже хотим скрыть',
                    'type': 'like',
                    'version': 'default',
                },
            ],
        }

    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/'
        'v1/place-feedbacks/predefined-comments',
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'predefined_comments': [
            {'id': 2, 'title': 'Испорчена упаковка'},
            {'id': 4, 'title': 'Не устроил курьер'},
        ],
    }
