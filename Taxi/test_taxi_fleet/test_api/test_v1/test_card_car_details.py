import aiohttp.web
import pytest

FLEET_API_CAR_CATEGORIES = {
    'internal_categories': ['econom', 'comfort'],
    'external_categories': [],
}


@pytest.mark.config(
    FLEET_API_CAR_CATEGORIES=FLEET_API_CAR_CATEGORIES,
    OPTEUM_CARD_TC_REQUIRED_FIELDS={
        'enable': True,
        'fields': ['brand', 'model'],
        'enable_backend': True,
    },
    OPTEUM_CARD_TC_FIELDS_EDIT={
        'enable': True,
        'fields': ['color'],
        'duration': 3,
        'enable_backend': True,
    },
    OPTEUM_CARD_CAR_REQUIRED_CATEGORIES=[
        {
            'enable': True,
            'kind': 'required',
            'categories': ['express'],
            'categories_related': {'kind': 'include', 'set': ['cargo']},
        },
    ],
)
@pytest.mark.now('2019-01-05T01:00:00+03:00')
async def test_success(
        web_app_client, mock_parks, headers, mockserver, load_json,
):
    stub = load_json('success.json')

    @mockserver.json_handler('/parks/cars/retrieve')
    async def _car_retrieve(request):
        assert request.json == stub['parks_car_retrieve']['request']
        return aiohttp.web.json_response(
            stub['parks_car_retrieve']['response'],
        )

    response = await web_app_client.post(
        '/api/v1/cards/car/details',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']


@pytest.mark.config(
    FLEET_API_CAR_CATEGORIES=FLEET_API_CAR_CATEGORIES,
    OPTEUM_CARD_TC_REQUIRED_FIELDS={
        'enable': True,
        'fields': ['brand', 'model'],
        'enable_backend': True,
    },
    OPTEUM_CARD_TC_FIELDS_EDIT={
        'enable': True,
        'fields': ['color'],
        'duration': 3,
        'enable_backend': True,
    },
    OPTEUM_CARD_CAR_REQUIRED_CATEGORIES=[
        {
            'enable': True,
            'kind': 'required',
            'categories': ['express'],
            'categories_related': {'kind': 'include', 'set': ['cargo']},
        },
    ],
)
@pytest.mark.now('2019-01-05T01:00:00+03:00')
@pytest.mark.parametrize(
    'json_name', ['success_deu.json', 'success_deu_phv.json'],
)
async def test_success_deu(
        web_app_client,
        mock_parks_deu,
        headers,
        mockserver,
        load_json,
        json_name,
):
    stub = load_json(json_name)

    @mockserver.json_handler('/parks/cars/retrieve')
    async def _car_retrieve(request):
        assert request.json == stub['parks_car_retrieve']['request']
        return aiohttp.web.json_response(
            stub['parks_car_retrieve']['response'],
        )

    response = await web_app_client.post(
        '/api/v1/cards/car/details',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']


@pytest.mark.config(
    FLEET_API_CAR_CATEGORIES=FLEET_API_CAR_CATEGORIES,
    OPTEUM_CARD_TC_REQUIRED_FIELDS={
        'enable': True,
        'fields': ['brand', 'model'],
        'enable_backend': True,
    },
    OPTEUM_CARD_TC_FIELDS_EDIT={
        'enable': True,
        'fields': ['color'],
        'duration': 3,
        'enable_backend': True,
    },
    OPTEUM_CARD_CAR_REQUIRED_CATEGORIES=[
        {
            'enable': True,
            'kind': 'required',
            'categories': ['express'],
            'categories_related': {'kind': 'include', 'set': ['cargo']},
        },
    ],
)
@pytest.mark.now('2019-01-04T02:00:00+03:00')
async def test_success_disabled_fields(
        web_app_client, mock_parks, headers, mockserver, load_json,
):

    stub = load_json('success_disabled_fields.json')

    @mockserver.json_handler('/parks/cars/retrieve')
    async def _car_retrieve(request):
        assert request.json == stub['parks_car_retrieve']['request']
        return aiohttp.web.json_response(
            stub['parks_car_retrieve']['response'],
        )

    response = await web_app_client.post(
        '/api/v1/cards/car/details',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']
