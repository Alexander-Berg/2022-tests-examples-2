import pytest

OPTEUM_SHOWCASE = [
    {
        'id': '1',
        'category': 'Ремонт',
        'url': '/park-init?id={park_id}&name={park_name}',
        'img_url': 'https://yastatic.net/s3/fleet/showcase/gbo-taxi.jpg',
        'title': 'Газовые моторы',
        'description': 'Газовые моторы экономят 60% расходов на топливо',
        'full_description': 'Газовые моторы экономят 60 % расходов на топливо',
        'author': 'ivitech-finance.ru',
        'address': 'г.Москва, ЮВАО  на Ленинском проспекте',
        'phone': '+7 495 235 12 32',
        'discount': {
            'title': 'Скидка 15%',
            'description': 'На газовый мотор новой модели',
        },
        'cities': ['Москва'],
        'countries': [],
    },
    {
        'id': '2',
        'category': 'Страхование',
        'url': '#',
        'img_url': 'https://yastatic.net/s3/fleet/showcase/gbo-taxi.jpg',
        'title': 'Газовые моторы',
        'description': 'Газовые моторы экономят 60% расходов на топливо',
        'full_description': 'Газовые моторы экономят 60 % расходов на топливо',
        'author': 'ivitech-finance.ru',
        'address': 'г.Москва, ЮВАО  на Ленинском проспекте',
        'phone': '+7 495 235 12 32',
        'discount': {
            'title': 'Скидка 15%',
            'description': 'На газовый мотор новой модели',
        },
        'cities': [],
        'countries': ['rus'],
    },
    {
        'id': '3',
        'category': 'Ремонт',
        'url': '#',
        'img_url': 'https://yastatic.net/s3/fleet/showcase/gbo-taxi.jpg',
        'title': 'Газовые моторы',
        'description': 'Газовые моторы экономят 60% расходов на топливо',
        'full_description': 'Газовые моторы экономят 60 % расходов на топливо',
        'author': 'ivitech-finance.ru',
        'address': 'г.Москва, ЮВАО  на Ленинском проспекте',
        'phone': '+7 495 235 12 32',
        'discount': {
            'title': 'Скидка 15%',
            'description': 'На газовый мотор новой модели',
        },
        'cities': ['Казань'],
        'countries': [],
    },
    {
        'id': '4',
        'category': 'Ремонт',
        'url': '#',
        'img_url': 'https://yastatic.net/s3/fleet/showcase/gbo-taxi.jpg',
        'title': 'Газовые моторы',
        'description': 'Газовые моторы экономят 60% расходов на топливо',
        'full_description': 'Газовые моторы экономят 60 % расходов на топливо',
        'author': 'ivitech-finance.ru',
        'address': 'г.Москва, ЮВАО  на Ленинском проспекте',
        'phone': '+7 495 235 12 32',
        'discount': {
            'title': 'Скидка 15%',
            'description': 'На газовый мотор новой модели',
        },
        'cities': [],
        'countries': [],
    },
]


@pytest.mark.config(OPTEUM_SHOWCASE=OPTEUM_SHOWCASE)
async def test_success(
        web_app_client, mock_parks, headers, mock_hiring_api, load_json,
):
    stub = load_json('success.json')

    response = await web_app_client.get(
        '/api/v1/showcase/list', headers=headers,
    )

    assert response.status == 200
    data = await response.json()
    assert data == stub['response']
