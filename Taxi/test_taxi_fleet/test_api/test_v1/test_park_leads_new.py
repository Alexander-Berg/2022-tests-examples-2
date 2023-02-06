import aiohttp.web
import pytest


OPTEUM_PARK_LEADS_TRANSLATIONS = {
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
}

OPTEUM_PARK_LEADS_REJECTION_REASONS = [
    {'name': 'reject_reason_car_does_not_fit_classifier'},
    {'name': 'reject_reason_country_dl_does_not_meet_requirements'},
    {'name': 'reject_reason_insufficient_experience'},
    {'name': 'reject_reason_need_car'},
    {'name': 'reject_reason_not_get_in_touch'},
    {'name': 'reject_reason_not_satisfied_with_conditions'},
    {'name': 'reject_reason_wants_to_be_courier'},
    {'name': 'reject_reason_security_service_refusal'},
    {'name': 'reject_reason_other', 'is_comment_enabled': True},
]


@pytest.mark.now('2020-10-06T12:11:00+00:00')
@pytest.mark.config(
    OPTEUM_PARK_LEADS_REJECTION_REASONS=OPTEUM_PARK_LEADS_REJECTION_REASONS,
)
@pytest.mark.translations(opteum_park_leads=OPTEUM_PARK_LEADS_TRANSLATIONS)
async def test_success(
        web_app_client, mock_parks, headers, mock_hiring_api, load_json,
):
    stub = load_json('success.json')

    @mock_hiring_api('/v1/tickets/create')
    async def _create(request):
        assert request.json == stub['hiring_api_request']
        return aiohttp.web.json_response(stub['hiring_api_response'])

    response = await web_app_client.post(
        '/api/v1/park-leads/new',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={
            'phone': '+79112223344',
            'name': 'Vasya',
            'rejection_reason': 'reject_reason_not_satisfied_with_conditions',
        },
    )

    assert response.status == 200


@pytest.mark.now('2020-10-06T12:11:00+00:00')
@pytest.mark.config(
    OPTEUM_PARK_LEADS_REJECTION_REASONS=OPTEUM_PARK_LEADS_REJECTION_REASONS,
)
@pytest.mark.translations(opteum_park_leads=OPTEUM_PARK_LEADS_TRANSLATIONS)
async def test_success_with_comment(
        web_app_client, mock_parks, headers, mock_hiring_api, load_json,
):

    stub = load_json('success_with_comment.json')

    @mock_hiring_api('/v1/tickets/create')
    async def _create(request):
        assert request.json == stub['hiring_api_request']
        return aiohttp.web.json_response(stub['hiring_api_response'])

    response = await web_app_client.post(
        '/api/v1/park-leads/new',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={
            'phone': '+79112223344',
            'name': 'Vasya',
            'rejection_reason': 'reject_reason_other',
            'comment': 'свой комментарий',
        },
    )

    assert response.status == 200


@pytest.mark.now('2020-10-06T12:11:00+00:00')
@pytest.mark.config(
    OPTEUM_PARK_LEADS_REJECTION_REASONS=OPTEUM_PARK_LEADS_REJECTION_REASONS,
)
@pytest.mark.translations(opteum_park_leads=OPTEUM_PARK_LEADS_TRANSLATIONS)
async def test_wrong_reason(web_app_client, mock_parks, headers, load_json):

    response = await web_app_client.post(
        '/api/v1/park-leads/new',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={
            'phone': '+79112223344',
            'name': 'Vasya',
            'rejection_reason': 'wrong_reject_reason',
        },
    )

    assert response.status == 400
