import typing

import pytest


MAX_RATE_EXPERIMENT_ANSWERS = {
    '000040': {
        'first': {
            'key': 'delightful_service',
            'tanker_key': 'eats_tips_payments.high_rating_order_service',
            'default_value': 'Душевный сервис',
        },
        'second': {
            'key': 'good_atmosphere',
            'tanker_key': 'eats_tips_payments.high_rating_order_atmosphere',
            'default_value': 'Прекрасная атмосфера',
        },
    },
    '000180': {
        'first': {
            'key': 'delightful_service',
            'tanker_key': 'eats_tips_payments.high_rating_order_service',
            'default_value': 'Душевный сервис',
        },
        'second': {
            'key': 'good_speed',
            'tanker_key': 'eats_tips_payments.high_rating_order_service_speed',
            'default_value': 'Быстрое обслуживание',
        },
    },
    '000080': {
        'first': {
            'key': 'good_atmosphere',
            'tanker_key': 'eats_tips_payments.high_rating_order_atmosphere',
            'default_value': 'Прекрасная атмосфера',
        },
        'second': {
            'key': 'good_speed',
            'tanker_key': 'eats_tips_payments.high_rating_order_service_speed',
            'default_value': 'Быстрое обслуживание',
        },
    },
    '000170': {
        'first': {
            'key': 'good_atmosphere',
            'tanker_key': 'eats_tips_payments.high_rating_order_atmosphere',
            'default_value': 'Прекрасная атмосфера',
        },
        'second': {
            'key': 'good_speed',
            'tanker_key': 'eats_tips_payments.high_rating_order_service_speed',
            'default_value': 'Быстрое обслуживание',
        },
    },
}


def make_experiment_answer(user_id: str, new_schema: bool = False) -> dict:
    answers = MAX_RATE_EXPERIMENT_ANSWERS[user_id]
    low_rating_answers: typing.List[typing.Union[dict, str]]
    high_rating_answers: typing.List[typing.Union[dict, str]]
    if new_schema:
        low_rating_answers = ['service', 'speed']
        high_rating_answers = [
            answers['first']['key'],
            answers['second']['key'],
        ]
    else:
        low_rating_answers = [
            {
                'key': 'service',
                'tanker': {
                    'key': 'eats_tips_payments.low_rating_order_service',
                },
                'default': 'Сервис',
            },
            {
                'key': 'speed',
                'tanker': {
                    'key': (
                        'eats_tips_payments.' 'low_rating_order_service_speed'
                    ),
                },
                'default': 'Скорость обслуживания',
            },
        ]
        high_rating_answers = [
            {
                'key': answers['first']['key'],
                'tanker': {'key': answers['first']['tanker_key']},
                'default': answers['first']['default_value'],
            },
            {
                'key': answers['second']['key'],
                'tanker': {'key': answers['second']['tanker_key']},
                'default': answers['second']['default_value'],
            },
        ]
    return {
        'ratings': [
            {
                'title': {
                    'tanker': {
                        'key': 'eats_tips_payments.low_rating_order_title',
                    },
                    'default': 'Над чем поработать, что бы стать лучше?',
                },
                'rating': 1,
                'answers': low_rating_answers,
            },
            {
                'title': {
                    'tanker': {
                        'key': 'eats_tips_payments.high_rating_order_title',
                    },
                    'default': 'Спасибо! Что понравилось?',
                },
                'rating': 5,
                'answers': high_rating_answers,
            },
        ],
    }


def make_expected_result(user_id):
    result_variants = {
        '000040': [
            {'text': 'Душевный сервис', 'key': 'delightful_service'},
            {'text': 'Прекрасная атмосфера', 'key': 'good_atmosphere'},
        ],
        '000180': [
            {'text': 'Душевный сервис', 'key': 'delightful_service'},
            {'text': 'Быстрое обслуживание', 'key': 'good_speed'},
        ],
        '000080': [
            {'text': 'Прекрасная атмосфера', 'key': 'good_atmosphere'},
            {'text': 'Быстрое обслуживание', 'key': 'good_speed'},
        ],
        '000170': [
            {'text': 'Прекрасная атмосфера', 'key': 'good_atmosphere'},
            {'text': 'Быстрое обслуживание', 'key': 'good_speed'},
        ],
    }
    return {
        'ratings': [
            {
                'rating_options': [
                    {'text': 'Сервис', 'key': 'service'},
                    {'text': 'Скорость обслуживания', 'key': 'speed'},
                ],
                'rating': 1,
                'title': 'Над чем поработать, что бы стать лучше?',
            },
            {
                'rating_options': result_variants[user_id],
                'rating': 5,
                'title': 'Спасибо! Что понравилось?',
            },
        ],
    }


@pytest.mark.client_experiments3(
    consumer='eats-tips-payments/rating_options',
    experiment_name='rating_options',
    args=[
        {'name': 'place_id', 'type': 'int', 'value': 3},
        {'name': 'brand_id', 'type': 'int', 'value': 12},
        {'name': 'user_id', 'type': 'string', 'value': '000040'},
    ],
    value=make_experiment_answer('000040'),
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-payments/rating_options',
    experiment_name='rating_options',
    args=[
        {'name': 'place_id', 'type': 'int', 'value': 10},
        {'name': 'brand_id', 'type': 'int', 'value': 12},
        {'name': 'user_id', 'type': 'string', 'value': '000180'},
    ],
    value=make_experiment_answer('000180'),
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-payments/rating_options',
    experiment_name='rating_options',
    args=[
        {'name': 'place_id', 'type': 'int', 'value': 9},
        {'name': 'user_id', 'type': 'string', 'value': '000080'},
    ],
    value=make_experiment_answer('000080'),
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-payments/rating_options',
    experiment_name='rating_options',
    args=[
        {'name': 'place_id', 'type': 'int', 'value': 16},
        {'name': 'brand_id', 'type': 'int', 'value': 15},
        {'name': 'user_id', 'type': 'string', 'value': '000170'},
    ],
    value=make_experiment_answer('000170', new_schema=True),
)
@pytest.mark.parametrize(
    'user_id, expected_result',
    [
        ('000040', make_expected_result('000040')),
        ('000180', make_expected_result('000180')),
        ('000080', make_expected_result('000080')),
        ('000170', make_expected_result('000170')),
    ],
)
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
async def test_get_review_options(
        taxi_eats_tips_payments_web, user_id, expected_result,
):
    response = await taxi_eats_tips_payments_web.get(
        '/v1/users/review/options', params={'user_id': user_id},
    )
    answer = await response.json()
    assert answer == expected_result
