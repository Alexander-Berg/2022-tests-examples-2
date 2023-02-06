import pytest


@pytest.mark.experiments3(filename='exp3_eats_place_rating.json')
async def test_place_feedback(
        taxi_eats_place_rating,
        mockserver,
        mock_authorizer_allowed,
        mock_eats_place_subscription,
):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-ids')
    def _mock_eaters(request):
        assert request.json == {'ids': ['111', '112']}
        return {
            'eaters': [
                {
                    'id': '111',
                    'uuid': 'uuid111',
                    'name': 'Name',
                    'created_at': '2019-12-31T10:59:59+03:00',
                    'updated_at': '2019-12-31T10:59:59+03:00',
                },
                {
                    'id': '112',
                    'uuid': 'uuid112',
                    'name': 'Name2',
                    'created_at': '2019-12-31T10:59:59+03:00',
                    'updated_at': '2019-12-31T10:59:59+03:00',
                },
            ],
            'pagination': {'limit': 2, 'has_more': False},
        }

    @mockserver.json_handler(
        '/eats-feedback/internal/eats-feedback/v1/feedbacks',
    )
    def _mock_feedback(request):
        return {
            'count': 1,
            'feedbacks': [
                {
                    'actual': True,
                    'comment_status': 'raw',
                    'feedback_filled_at': '2021-02-10T09:23:00+00:00',
                    'id': 1,
                    'order_nr': 'ORDER_1',
                    'predefined_comments': [
                        {'id': 15, 'title': 'Горячая еда!'},
                    ],
                    'rating': 4,
                    'eater_id': '111',
                    'feedback_answers': [
                        {
                            'answer': 'comment',
                            'answer_moderation_status': 'approved',
                            'coupon': {
                                'coupon': 'COUPON',
                                'currency_code': 'RUB',
                                'expire_at': '2022-03-08T20:59:00+00:00',
                                'limit': '1999.99',
                                'percent': 10,
                            },
                        },
                    ],
                    'order_delivered_at': '2021-02-10T09:23:00+00:00',
                },
                {
                    'actual': True,
                    'comment_status': 'raw',
                    'feedback_filled_at': '2021-02-10T09:27:00+00:00',
                    'id': 1,
                    'order_nr': 'ORDER_3',
                    'predefined_comments': [
                        {'id': 20, 'title': 'Еда была холодной'},
                    ],
                    'rating': 3,
                    'eater_id': '112',
                    'feedback_answers': [
                        {
                            'answer': 'comment2',
                            'answer_moderation_status': 'approved',
                        },
                    ],
                    'order_delivered_at': '2021-02-10T09:23:00+00:00',
                },
            ],
        }

    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/place-feedbacks',
        params={'place_id': 1},
        headers={'X-YaEda-PartnerId': '1'},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'feedback_answer_on': True,
        'count': 1,
        'feedbacks': [
            {
                'actual': True,
                'comment_status': 'raw',
                'feedback_filled_at': '2021-02-10T09:23:00+00:00',
                'id': 1,
                'order_nr': 'ORDER_1',
                'predefined_comments': [{'id': 15, 'title': 'Горячая еда!'}],
                'rating': 4,
                'feedback_weight': 200,
                'eater_name': 'Name',
                'feedback_answers': [
                    {
                        'answer_to_feedback': 'comment',
                        'answer_moderation_status': 'approved',
                        'coupon': {
                            'currency_code': 'RUB',
                            'expire_at': '2022-03-08T20:59:00+00:00',
                            'limit': '1999.99',
                            'percent': True,
                            'value': 10,
                        },
                    },
                ],
                'delivered_at': '2021-02-10T09:23:00+00:00',
            },
            {
                'actual': True,
                'comment_status': 'raw',
                'feedback_filled_at': '2021-02-10T09:27:00+00:00',
                'id': 1,
                'order_nr': 'ORDER_3',
                'predefined_comments': [
                    {'id': 20, 'title': 'Еда была холодной'},
                ],
                'rating': 3,
                'eater_name': 'Name2',
                'feedback_answers': [
                    {
                        'answer_to_feedback': 'comment2',
                        'answer_moderation_status': 'approved',
                    },
                ],
                'delivered_at': '2021-02-10T09:23:00+00:00',
            },
        ],
    }


@pytest.mark.experiments3(filename='exp3_eats_place_rating.json')
async def test_place_feedback_conf(
        taxi_eats_place_rating,
        mockserver,
        mock_authorizer_allowed,
        mock_eats_place_subscription_no,
):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-ids')
    def _mock_eaters(request):
        assert request.json == {'ids': ['111', '112']}
        return {
            'eaters': [
                {
                    'id': '111',
                    'uuid': 'uuid111',
                    'name': 'Name',
                    'created_at': '2019-12-31T10:59:59+03:00',
                    'updated_at': '2019-12-31T10:59:59+03:00',
                },
                {
                    'id': '112',
                    'uuid': 'uuid112',
                    'name': 'Name2',
                    'created_at': '2019-12-31T10:59:59+03:00',
                    'updated_at': '2019-12-31T10:59:59+03:00',
                },
            ],
            'pagination': {'limit': 2, 'has_more': False},
        }

    @mockserver.json_handler(
        '/eats-feedback/internal/eats-feedback/v1/feedbacks',
    )
    def _mock_feedback(request):
        return {
            'count': 1,
            'feedbacks': [
                {
                    'actual': True,
                    'comment_status': 'raw',
                    'feedback_filled_at': '2021-02-10T09:23:00+00:00',
                    'id': 1,
                    'order_nr': 'ORDER_1',
                    'predefined_comments': [
                        {'id': 15, 'title': 'Горячая еда!'},
                    ],
                    'rating': 4,
                    'eater_id': '111',
                    'feedback_answers': [
                        {
                            'answer': 'comment',
                            'answer_moderation_status': 'approved',
                            'coupon': {
                                'coupon': 'COUPON',
                                'currency_code': 'RUB',
                                'expire_at': '2022-03-08T20:59:00+00:00',
                                'limit': '1999.99',
                                'percent': 10,
                            },
                        },
                    ],
                    'order_delivered_at': '2021-02-10T09:23:00+00:00',
                },
                {
                    'actual': True,
                    'comment_status': 'raw',
                    'feedback_filled_at': '2021-02-10T09:27:00+00:00',
                    'id': 1,
                    'order_nr': 'ORDER_3',
                    'predefined_comments': [
                        {'id': 20, 'title': 'Еда была холодной'},
                    ],
                    'rating': 3,
                    'eater_id': '112',
                    'feedback_answers': [
                        {
                            'answer': 'comment2',
                            'answer_moderation_status': 'approved',
                        },
                    ],
                    'order_delivered_at': '2021-02-10T09:23:00+00:00',
                },
            ],
        }

    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/place-feedbacks',
        params={'place_id': 3},
        headers={'X-YaEda-PartnerId': '1'},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'count': 1,
        'feedback_answer_on': True,
        'feedbacks': [
            {
                'actual': True,
                'comment_status': 'raw',
                'feedback_filled_at': '2021-02-10T09:23:00+00:00',
                'id': 1,
                'order_nr': 'ORDER_1',
                'predefined_comments': [{'id': 15, 'title': 'Горячая еда!'}],
                'rating': 4,
                'feedback_answers': [
                    {
                        'answer_to_feedback': 'comment',
                        'answer_moderation_status': 'approved',
                        'coupon': {
                            'currency_code': 'RUB',
                            'expire_at': '2022-03-08T20:59:00+00:00',
                            'limit': '1999.99',
                            'percent': True,
                            'value': 10,
                        },
                    },
                ],
                'delivered_at': '2021-02-10T09:23:00+00:00',
            },
            {
                'actual': True,
                'comment_status': 'raw',
                'feedback_filled_at': '2021-02-10T09:27:00+00:00',
                'id': 1,
                'order_nr': 'ORDER_3',
                'predefined_comments': [
                    {'id': 20, 'title': 'Еда была холодной'},
                ],
                'rating': 3,
                'feedback_answers': [
                    {
                        'answer_to_feedback': 'comment2',
                        'answer_moderation_status': 'approved',
                    },
                ],
                'delivered_at': '2021-02-10T09:23:00+00:00',
            },
        ],
    }


@pytest.mark.experiments3(filename='exp3_eats_place_rating.json')
async def test_place_feedback_no_show_user(
        taxi_eats_place_rating,
        mockserver,
        mock_authorizer_allowed,
        mock_eats_place_subscription,
):
    @mockserver.json_handler(
        '/eats-feedback/internal/eats-feedback/v1/feedbacks',
    )
    def _mock_feedback(request):
        return {
            'count': 1,
            'feedbacks': [
                {
                    'actual': True,
                    'comment_status': 'raw',
                    'feedback_filled_at': '2021-02-10T09:23:00+00:00',
                    'id': 1,
                    'order_nr': 'ORDER_2',
                    'predefined_comments': [
                        {'id': 15, 'title': 'Горячая еда!'},
                    ],
                    'rating': 4,
                    'eater_id': '111',
                    'feedback_answers': [
                        {
                            'answer': 'comment',
                            'answer_moderation_status': 'approved',
                            'coupon': {
                                'coupon': 'COUPON',
                                'currency_code': 'RUB',
                                'expire_at': '2022-03-08T20:59:00+00:00',
                                'limit': '1999.99',
                                'percent': 10,
                            },
                        },
                    ],
                    'order_delivered_at': '2021-02-10T09:23:00+00:00',
                },
                {
                    'actual': True,
                    'comment_status': 'raw',
                    'feedback_filled_at': '2021-02-10T09:27:00+00:00',
                    'id': 1,
                    'order_nr': 'ORDER_3',
                    'predefined_comments': [
                        {'id': 20, 'title': 'Еда была холодной'},
                    ],
                    'rating': 3,
                    'eater_id': '112',
                    'feedback_answers': [
                        {
                            'answer': 'comment2',
                            'answer_moderation_status': 'approved',
                        },
                    ],
                    'order_delivered_at': '2021-02-10T09:23:00+00:00',
                },
            ],
        }

    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/place-feedbacks',
        params={'place_id': 2},
        headers={'X-YaEda-PartnerId': '1'},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'feedback_answer_on': True,
        'count': 1,
        'feedbacks': [
            {
                'actual': True,
                'comment_status': 'raw',
                'feedback_filled_at': '2021-02-10T09:23:00+00:00',
                'id': 1,
                'order_nr': 'ORDER_2',
                'predefined_comments': [{'id': 15, 'title': 'Горячая еда!'}],
                'rating': 4,
                'feedback_weight': 200,
                'feedback_answers': [
                    {
                        'answer_to_feedback': 'comment',
                        'answer_moderation_status': 'approved',
                        'coupon': {
                            'currency_code': 'RUB',
                            'expire_at': '2022-03-08T20:59:00+00:00',
                            'limit': '1999.99',
                            'percent': True,
                            'value': 10,
                        },
                    },
                ],
                'delivered_at': '2021-02-10T09:23:00+00:00',
            },
            {
                'actual': True,
                'comment_status': 'raw',
                'feedback_filled_at': '2021-02-10T09:27:00+00:00',
                'id': 1,
                'order_nr': 'ORDER_3',
                'predefined_comments': [
                    {'id': 20, 'title': 'Еда была холодной'},
                ],
                'rating': 3,
                'feedback_answers': [
                    {
                        'answer_to_feedback': 'comment2',
                        'answer_moderation_status': 'approved',
                    },
                ],
                'delivered_at': '2021-02-10T09:23:00+00:00',
            },
        ],
    }


@pytest.mark.experiments3(filename='exp3_eats_place_rating_false.json')
async def test_place_feedback_answer_off(
        taxi_eats_place_rating,
        mockserver,
        mock_authorizer_allowed,
        mock_eats_place_subscription_no,
):
    @mockserver.json_handler(
        '/eats-feedback/internal/eats-feedback/v1/feedbacks',
    )
    def _mock_predefined_comments(request):
        return {
            'count': 1,
            'feedbacks': [
                {
                    'actual': True,
                    'comment_status': 'raw',
                    'feedback_filled_at': '2021-02-10T09:23:00+00:00',
                    'id': 1,
                    'order_nr': 'ORDER_1',
                    'predefined_comments': [
                        {'id': 15, 'title': 'Горячая еда!'},
                    ],
                    'rating': 4,
                    'eater_id': '111',
                    'feedback_answers': [
                        {
                            'answer': 'comment',
                            'answer_moderation_status': 'approved',
                            'coupon': {
                                'coupon': 'COUPON',
                                'currency_code': 'RUB',
                                'expire_at': '2022-03-08T20:59:00+00:00',
                                'limit': '1999.99',
                                'percent': 10,
                            },
                        },
                    ],
                    'order_delivered_at': '2021-02-10T09:23:00+00:00',
                },
                {
                    'actual': True,
                    'comment_status': 'raw',
                    'feedback_filled_at': '2021-02-10T09:27:00+00:00',
                    'id': 1,
                    'order_nr': 'ORDER_3',
                    'predefined_comments': [
                        {'id': 20, 'title': 'Еда была холодной'},
                    ],
                    'rating': 3,
                    'eater_id': '111',
                    'feedback_answers': [
                        {
                            'answer': 'comment2',
                            'answer_moderation_status': 'approved',
                        },
                    ],
                    'order_delivered_at': '2021-02-10T09:23:00+00:00',
                },
            ],
        }

    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/place-feedbacks',
        params={'place_id': 1},
        headers={'X-YaEda-PartnerId': '1'},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'feedback_answer_on': False,
        'count': 1,
        'feedbacks': [
            {
                'actual': True,
                'comment_status': 'raw',
                'feedback_filled_at': '2021-02-10T09:23:00+00:00',
                'id': 1,
                'order_nr': 'ORDER_1',
                'predefined_comments': [{'id': 15, 'title': 'Горячая еда!'}],
                'rating': 4,
                'feedback_weight': 200,
            },
            {
                'actual': True,
                'comment_status': 'raw',
                'feedback_filled_at': '2021-02-10T09:27:00+00:00',
                'id': 1,
                'order_nr': 'ORDER_3',
                'predefined_comments': [
                    {'id': 20, 'title': 'Еда была холодной'},
                ],
                'rating': 3,
            },
        ],
    }


async def test_place_feedback_authorizer_403(
        taxi_eats_place_rating, mockserver, mock_authorizer_403,
):

    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/place-feedbacks',
        params={'place_id': 1},
        headers={'X-YaEda-PartnerId': '1'},
    )

    assert response.status_code == 403
    response = response.json()
    assert response == {
        'code': '403',
        'message': 'For user 1 access to places is denied',
    }


async def test_place_feedback_authorizer_forbidden_400(
        taxi_eats_place_rating, mockserver, mock_authorizer_400,
):

    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/place-feedbacks',
        params={'place_id': 1},
        headers={'X-YaEda-PartnerId': '1'},
    )

    assert response.status_code == 403
    response = response.json()
    assert response == {
        'code': '403',
        'message': 'For user 1 access to places is denied',
    }


@pytest.mark.experiments3(filename='exp3_eats_place_rating.json')
async def test_place_feedback_pass_params_to_eats_feedback(
        taxi_eats_place_rating,
        mockserver,
        mock_authorizer_allowed,
        mock_eats_place_subscription,
):
    @mockserver.json_handler(
        '/eats-feedback/internal/eats-feedback/v1/feedbacks',
    )
    def _mock_feedback(request):
        assert request.query == {
            'hide_unmoderated': 'true',
            'place_id': '1',
            'predefined_comment_ids': '11,12,13',
            'cursor': 'from-this',
            'ratings': '1,2,5',
            'user_locale': 'ru-RU',
            'from': '2022-01-01T09:00:00+00:00',
            'to': '2022-05-01T00:00:00+00:00',
        }
        return {'count': 0, 'feedbacks': []}

    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/place-feedbacks',
        params={
            'place_id': 1,
            'predefined_comment_ids': '11,12,13',
            'cursor': 'from-this',
            'ratings': '1,2,5',
            'user_locale': 'ru-RU',
            'from': '2022-01-01T12:00:00+03:00',
            'to': '2022-05-01T00:00:00+00:00',
        },
        headers={'X-YaEda-PartnerId': '1'},
    )

    assert response.status_code == 200


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
@pytest.mark.experiments3(filename='exp3_eats_place_rating.json')
async def test_place_feedback_grouped_comments(
        taxi_eats_place_rating,
        mockserver,
        mock_authorizer_allowed,
        mock_eats_place_subscription,
):
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
                    'id': 11,
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
                    'id': 12,
                    'show_position': 600,
                    'title': 'Испорчена упаковка',
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
                    'id': 14,
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
                    'id': 15,
                    'show_position': 600,
                    'title': 'Не устроил курьер',
                    'type': 'like',
                    'version': 'default',
                },
            ],
        }

    @mockserver.json_handler(
        '/eats-feedback/internal/eats-feedback/v1/feedbacks',
    )
    def _mock_feedback(request):
        assert request.query == {
            'hide_unmoderated': 'true',
            'place_id': '1',
            'predefined_comment_ids': '11,12,14',
            'user_locale': 'ru-RU',
        }
        return {'count': 0, 'feedbacks': []}

    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/place-feedbacks',
        params={
            'place_id': 1,
            'predefined_comment_ids': '10,11,12',
            'user_locale': 'ru-RU',
        },
        headers={'X-YaEda-PartnerId': '1'},
    )

    assert response.status_code == 200
