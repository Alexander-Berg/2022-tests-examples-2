import aiohttp.web
import pytest


CONFIG_PASSENGER_TAGS = {
    'i18n_keyset': 'opteum_scoring',
    'i18n_keys': [
        {'id': 'driver_impolite', 'i18n_key': 'tag_negative_driver_impolite'},
        {'id': 'smelly_vehicle', 'i18n_key': 'tag_negative_smelly_vehicle'},
        {'id': 'no_change', 'i18n_key': 'tag_negative_no_change'},
        {'id': 'tag_mood', 'i18n_key': 'tag_positive_good_mood'},
        {'id': 'clean', 'i18n_key': 'tag_positive_clean'},
    ],
}


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_REPORTS_PASSENGER_TAGS=CONFIG_PASSENGER_TAGS,
)
@pytest.mark.translations(
    opteum_scoring={
        'tag_negative_driver_impolite': {'ru': 'Водитель был невежлив'},
        'tag_negative_smelly_vehicle': {'ru': 'Запах в машине'},
        'tag_positive_good_mood': {'ru': 'Хорошее настроение'},
    },
)
async def test_success(
        web_app_client, headers, mock_fleet_drivers_scoring, load_json,
):
    stub = load_json('success.json')

    @mock_fleet_drivers_scoring(
        '/v1/paid/drivers/scoring/passenger-tags/retrieve',
    )
    async def _passenger_tags_retrieve(request):
        assert request.json == stub['scoring_request']
        return aiohttp.web.json_response(stub['scoring_response'])

    response = await web_app_client.post(
        '/drivers-scoring-api/v1/paid/scoring/passenger-tags/retrieve',
        headers=headers,
        json={'request_id': 'request_id'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
