import pytest

PUSHES_CONFIG = {
    'app_texts': {
        'test_brand_1': [
            {
                'algo_names': ['test_algo_1', 'test_algo_2'],
                'texts': [
                    {
                        'text': (
                            'text_1: algo_1, algo_2 '
                            '{max_discount_percent}% {prep_case_city} '
                            '{tariffs}'
                        ),
                        'title': 'brand_1 title_1',
                    },
                    {
                        'text': 'text_2: algo_1, algo_2 {tariffs}',
                        'title': 'brand_1 title_2',
                    },
                ],
                'locale': 'ru',
                'country': 'rus',
            },
            {
                'algo_names': ['test_algo_2', 'test_algo_3'],
                'texts': [
                    {
                        'text': 'text_3: algo_2, algo_3 ' '{prep_case_city}',
                        'title': 'brand_1 title_3',
                    },
                ],
                'locale': 'ru',
                'country': 'aze',
            },
        ],
        'test_brand_2': [
            {
                'algo_names': ['test_algo_1'],
                'texts': [
                    {
                        'text': 'text_1: algo_1 {tariffs}',
                        'title': 'brand_2 title_1',
                    },
                ],
                'locale': 'ru',
                'country': 'aze',
            },
            {
                'algo_names': ['test_algo_2'],
                'texts': [
                    {
                        'text': (
                            'text_2: algo_2 '
                            '{max_discount_percent}% '
                            '{max_price_with_discount} '
                            '{prep_case_city} '
                            '{tariffs}'
                        ),
                        'title': 'brand_2 title_2',
                    },
                ],
                'locale': 'en',
                'country': 'aze',
            },
            {
                'algo_names': ['test_algo_1'],
                'texts': [
                    {
                        'text': 'text_2: algo_2 {prep_case_city}',
                        'title': 'brand_2 title_2',
                    },
                ],
                'locale': 'en',
                'country': 'rus',
            },
            {
                'algo_names': ['test_algo_1'],
                'texts': [
                    {
                        'text': 'text_2: algo_2 {prep_case_city} {tariffs}',
                        'title': 'brand_2 title_2',
                    },
                ],
                'locale': 'ru',
                'country': 'rus',
            },
            {
                'algo_names': ['test_algo_1'],
                'texts': [
                    {
                        'text': '{prep_case_city}',
                        'title': 'non existent locale',
                    },
                ],
                'locale': 'en',
                'country': 'tst',
            },
        ],
    },
    'city_variables': {
        'Абиджан': {
            'en': {'prep_case_city': 'in Abidjan'},
            'ru': {'prep_case_city': 'в Абиджане'},
            '__country__': 'aze',
        },
        'Саратов': {
            'ru': {'prep_case_city': 'в Саратове'},
            '__country__': 'rus',
        },
        'Тест город': {'__country__': 'tst'},
    },
    'brands_tariffs_mapping': {
        'test_brand_1': ['econom', 'uberx'],
        'test_brand_2': ['econom', 'business'],
    },
    'tariffs_localization': {
        'econom': {'ru': 'Эконом'},
        'business': {'ru': 'Комфорт'},
        'uberx': {'ru': 'uberX'},
    },
}

EXPECTED_SINGLE_APP = {
    'ru': {
        'test_brand_1': [
            {
                'text': 'text_3: algo_2, algo_3 в Абиджане',
                'title': 'brand_1 title_3',
            },
        ],
    },
}

EXPECTED_MULTIPLE_APP = {
    'ru': {
        'test_brand_1': [
            {
                'text': 'text_3: algo_2, algo_3 в Абиджане',
                'title': 'brand_1 title_3',
            },
        ],
    },
}

EXPECTED_MULTIPLE_TARIFFS = {
    'ru': {
        'test_brand_1': [
            {
                'text': 'text_1: algo_1, algo_2 21% в Саратове Эконом и uberX',
                'title': 'brand_1 title_1',
            },
            {
                'text': 'text_2: algo_1, algo_2 Эконом и uberX',
                'title': 'brand_1 title_2',
            },
        ],
        'test_brand_2': [
            {
                'text': 'text_2: algo_2 в Саратове Эконом и Комфорт',
                'title': 'brand_2 title_2',
            },
        ],
    },
}


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_suggests_to_pushes_texts.sql'],
)
@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_PUSHES_CONFIG=PUSHES_CONFIG,
)
async def test_get_pushes_texts_single_app(web_app_client):
    response = await web_app_client.get(
        '/v1/pushes_texts',
        params={'suggest_id': 1, 'algorithm_name': 'test_algo_3'},
    )

    assert response.status == 200
    content = await response.json()

    assert content == EXPECTED_SINGLE_APP


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_suggests_to_pushes_texts.sql'],
)
@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_PUSHES_CONFIG=PUSHES_CONFIG,
)
async def test_get_pushes_texts_multiple_app(web_app_client):
    response = await web_app_client.get(
        '/v1/pushes_texts',
        params={'suggest_id': 2, 'algorithm_name': 'test_algo_2'},
    )
    assert response.status == 200
    content = await response.json()

    assert content == EXPECTED_MULTIPLE_APP


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_suggests_to_pushes_texts.sql'],
)
@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_PUSHES_CONFIG=PUSHES_CONFIG,
)
async def test_get_pushes_texts_non_existent_city(web_app_client):
    response = await web_app_client.get(
        '/v1/pushes_texts',
        params={'suggest_id': 3, 'algorithm_name': 'test_algo_3'},
    )

    assert response.status == 400
    content = await response.json()

    assert content == {
        'code': 'BadRequest::CityNotFound',
        'message': 'City "Тестовый город" not found',
    }


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_suggests_to_pushes_texts.sql'],
)
@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_PUSHES_CONFIG=PUSHES_CONFIG,
)
async def test_get_pushes_texts_non_existent_algo(web_app_client):
    response = await web_app_client.get(
        '/v1/pushes_texts',
        params={'suggest_id': 1, 'algorithm_name': 'non_existent_algo'},
    )

    assert response.status == 200
    content = await response.json()

    assert content == {}


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_suggests_to_pushes_texts.sql'],
)
@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_PUSHES_CONFIG=PUSHES_CONFIG,
)
async def test_get_pushes_texts_non_existent_locale(web_app_client):
    response = await web_app_client.get(
        '/v1/pushes_texts',
        params={'suggest_id': 5, 'algorithm_name': 'test_algo_1'},
    )

    assert response.status == 200
    content = await response.json()

    assert content == {}


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_suggests_to_pushes_texts.sql'],
)
@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_PUSHES_CONFIG=PUSHES_CONFIG,
)
async def test_get_pushes_texts_multiple_tariffs(web_app_client):
    response = await web_app_client.get(
        '/v1/pushes_texts',
        params={'suggest_id': 4, 'algorithm_name': 'test_algo_1'},
    )

    assert response.status == 200
    content = await response.json()

    assert content == EXPECTED_MULTIPLE_TARIFFS
