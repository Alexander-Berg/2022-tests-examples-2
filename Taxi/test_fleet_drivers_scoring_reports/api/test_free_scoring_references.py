import pytest


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_REPORTS_QUESTIONNAIRE={
        'free': {
            'enable': True,
            'link': 'http://example.com/free',
            'link_key': 'free_url_text_key',
            'question_key': 'free_question_key',
        },
        'paid': {
            'enable': True,
            'link': 'http://example.com/paid',
            'link_key': 'paid_url_text_key',
            'question_key': 'paid_question_key',
        },
    },
)
@pytest.mark.translations(
    opteum_scoring={
        'free_url_text_key': {'ru': 'Пройти опрос'},
        'free_question_key': {'ru': 'Вопрос 1'},
        'paid_url_text_key': {'ru': 'Пройти опрос'},
        'paid_question_key': {'ru': 'Вопрос 2'},
    },
)
async def test_success(web_app_client, headers, load_json):
    stub = load_json('success.json')

    response = await web_app_client.get(
        '/drivers-scoring-api/v1/scoring/references', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
