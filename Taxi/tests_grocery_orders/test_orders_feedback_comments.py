import pytest

from . import configs
from . import headers
from . import models

COMMENTS = [
    (1, '1_star_feedback', ['bad_feedback']),
    (2, '2_star_feedback', ['bad_feedback']),
    (3, '3_star_feedback', ['bad_feedback']),
    (4, '4_star_feedback', ['bad_feedback']),
    (5, '5_star_feedback', ['bad_feedback']),
]

LOCALIZED_TEXT = {
    'ru': {
        '1_star_feedback': 'Почему так плохо',
        '2_star_feedback': 'неочень',
        '3_star_feedback': 'норм',
        '4_star_feedback': 'Хорошо',
        '5_star_feedback': 'Очень хорошо',
        'bad_feedback': 'Ты не очень',
    },
    'en': {
        '1_star_feedback': 'Why so bad',
        '2_star_feedback': 'Not good',
        '3_star_feedback': 'Ok',
        '4_star_feedback': 'Good',
        '5_star_feedback': 'very good',
        'bad_feedback': 'You suck',
    },
}


def _add_comments_to_experiment(experiments3):
    configs.add_feedback_comments_config(
        experiments3,
        {
            evaluation: {'title': title, 'comments': comments}
            for evaluation, title, comments in COMMENTS
        },
    )


@pytest.mark.parametrize('locale', ['ru', 'en'])
@pytest.mark.parametrize('evaluation,title,comments', COMMENTS)
async def test_basic(
        taxi_grocery_orders, experiments3, evaluation, title, comments, locale,
):
    _add_comments_to_experiment(experiments3)

    feedback_comments_response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/feedback/comments',
        headers={**headers.DEFAULT_HEADERS, 'X-Request-Language': locale},
        json={'evaluation': evaluation},
    )

    assert feedback_comments_response.status_code == 200
    body = feedback_comments_response.json()
    assert body['title'] == LOCALIZED_TEXT[locale][title]
    assert body['comments'] == [
        LOCALIZED_TEXT[locale][comment] for comment in comments
    ]


@pytest.mark.parametrize('evaluation', [0, 6])
async def test_invalid_evaluation(
        taxi_grocery_orders, experiments3, evaluation,
):
    _add_comments_to_experiment(experiments3)

    feedback_comments_response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/feedback/comments',
        headers=headers.DEFAULT_HEADERS,
        json={'evaluation': evaluation},
    )

    assert feedback_comments_response.status_code == 400
    body = feedback_comments_response.json()
    assert body['error_code'] == 'invalid_evaluation'


COMMENT_TRANSLATIONS = {
    'bad_feedback': {'ru': 'Ты не очень', 'en': 'You suck'},
    'comment_key_1': {'ru': 'Ключ номер 1', 'en': 'Key 1'},
    'comment_key_2': {'ru': 'Ключ номер 2', 'en': 'Key 2'},
}


GROCERY_FEEDBACK_PREDEFINED_COMMENTS = pytest.mark.experiments3(
    name='grocery_feedback_predefined_comments',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'options': [
                    {
                        'evaluation': 1,
                        'title': 'bad_feedback',
                        'predefined_comments': [
                            {
                                'comment_id': 'comment_id_1',
                                'eats_id': 1,
                                'tanker_key': 'comment_key_1',
                            },
                        ],
                    },
                    {
                        'evaluation': 2,
                        'title': 'bad_feedback',
                        'predefined_comments': [
                            {
                                'comment_id': 'comment_id_2',
                                'eats_id': 1,
                                'tanker_key': 'comment_key_2',
                            },
                        ],
                    },
                ],
            },
        },
    ],
    is_config=True,
)


@pytest.mark.translations(grocery_orders=COMMENT_TRANSLATIONS)
@GROCERY_FEEDBACK_PREDEFINED_COMMENTS
@pytest.mark.parametrize('locale', ['ru', 'en'])
async def test_basic_v2(taxi_grocery_orders, pgsql, locale):
    order = models.Order(
        pgsql=pgsql,
        state=models.OrderState(close_money_status='success'),
        status='closed',
        locale=locale,
    )
    feedback_comments_response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v2/feedback/comments',
        headers={**headers.DEFAULT_HEADERS, 'X-Request-Language': locale},
        json={'order_id': order.order_id},
    )

    assert feedback_comments_response.status_code == 200
    comments = feedback_comments_response.json()['comments']
    assert comments == [
        {
            'evaluation': 1,
            'title': LOCALIZED_TEXT[locale]['bad_feedback'],
            'predefined_comments': [
                {
                    'comment_id': 'comment_id_1',
                    'text': COMMENT_TRANSLATIONS['comment_key_1'][locale],
                },
            ],
        },
        {
            'evaluation': 2,
            'title': LOCALIZED_TEXT[locale]['bad_feedback'],
            'predefined_comments': [
                {
                    'comment_id': 'comment_id_2',
                    'text': COMMENT_TRANSLATIONS['comment_key_2'][locale],
                },
            ],
        },
    ]


async def test_order_not_found(taxi_grocery_orders):
    feedback_comments_response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v2/feedback/comments',
        headers=headers.DEFAULT_HEADERS,
        json={'order_id': 'this-id-does-not-exist'},
    )

    assert feedback_comments_response.status_code == 404
