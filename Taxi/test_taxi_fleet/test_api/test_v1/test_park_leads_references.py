import pytest


@pytest.mark.config(
    OPTEUM_PARK_LEADS_REJECTION_REASONS=[
        {'name': 'reject_reason_car_does_not_fit_classifier'},
        {'name': 'reject_reason_country_dl_does_not_meet_requirements'},
        {'name': 'reject_reason_insufficient_experience'},
        {'name': 'reject_reason_need_car'},
        {'name': 'reject_reason_not_get_in_touch'},
        {'name': 'reject_reason_not_satisfied_with_conditions'},
        {'name': 'reject_reason_wants_to_be_courier'},
        {'name': 'reject_reason_security_service_refusal'},
        {'name': 'reject_reason_other', 'is_comment_enabled': True},
    ],
)
@pytest.mark.translations(
    opteum_park_leads={
        'reject_reason_car_does_not_fit_classifier': {
            'ru': 'Авто не подходит по классификатору',
        },
        'reject_reason_country_dl_does_not_meet_requirements': {
            'ru': 'Страна выдачи ВУ не соответствует требованиям',
        },
        'reject_reason_insufficient_experience': {'ru': 'Недостаточный стаж'},
        'reject_reason_need_car': {'ru': 'Нужен автомобиль'},
        'reject_reason_not_get_in_touch': {'ru': 'Не выходит на связь'},
        'reject_reason_not_satisfied_with_conditions': {
            'ru': 'Не устраивают условия парка',
        },
        'reject_reason_wants_to_be_courier': {'ru': 'Хочет быть курьером'},
        'reject_reason_security_service_refusal': {
            'ru': 'Отказ Службы Безопасности',
        },
        'reject_reason_other': {'ru': 'Другое'},
    },
)
async def test_success(web_app_client, headers, load_json):
    stub = load_json('success.json')

    response = await web_app_client.get(
        '/api/v1/park-leads/references', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['response']
