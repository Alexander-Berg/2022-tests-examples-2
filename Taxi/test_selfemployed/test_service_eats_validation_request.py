import pytest


@pytest.mark.parametrize(
    'value,expected_response',
    [
        (
            'invalid name',
            {
                'status': 'ERROR',
                'errors': {'telegram_name': ['Введён некорректный юзернейм']},
            },
        ),
        ('valid_name35', {'status': 'OK'}),
        (
            '',
            {
                'status': 'ERROR',
                'errors': {'telegram_name': ['Введён некорректный юзернейм']},
            },
        ),
    ],
)
async def test_telegram_username_validation(
        se_client, value, expected_response,
):
    data = {
        'id': 443,
        'slug': 'test-survey',
        'questions': [
            {
                'answer_type': {
                    'slug': 'answer_short_text',
                    'name': 'Короткий ответ',
                },
                'id': 30373,
                'label': 'Юзернейм в телеграм',
                'slug': 'telegram_name',
                'value': value,
            },
        ],
    }

    response = await se_client.post(
        '/service/eats-registration-request/validate', json=data,
    )

    assert response.status == 200
    content = await response.json()
    assert content == expected_response
