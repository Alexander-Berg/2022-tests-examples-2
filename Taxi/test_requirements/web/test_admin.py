import pytest

PAYMENT_TYPES_REQS = ['coupon', 'creditcard', 'corp', 'applepay', 'googlepay']


async def test_list(web_app_client, mongo):
    response = await web_app_client.get('/v1/requirements/')
    assert response.status == 200
    content = await response.json()
    assert content == ['childchair_v2', 'yellowcarnumber']


async def test_list_suggest(web_app_client, mongo):
    response = await web_app_client.get('/v1/requirements_suggest/')
    assert response.status == 200
    content = await response.json()
    assert (
        content
        == ['childchair_v2', 'childchair_v2.booster', 'yellowcarnumber']
        + PAYMENT_TYPES_REQS
    )


async def test_list_suggest_cache(web_app_client, mongo, mongodb):
    for _ in range(2):
        response = await web_app_client.get('/v1/requirements_suggest/')
        assert response.status == 200
        content = await response.json()
        assert len(content) == 8
        # second iteration will either use cache or will fail
        mongodb.requirements.remove({'name': 'childchair_v2'})


async def test_list_v2(web_app_client, mongo):
    response = await web_app_client.get('/v2/requirements_suggest/')
    assert response.status == 200
    content = await response.json()
    assert content == [
        {
            'name': 'childchair_v2',
            'tariff_specific': True,
            'flavors': ['1_1', '1_1_1', '2_1_1', 'to_fix'],
            'supports_flavors': True,
        },
        {'name': 'yellowcarnumber', 'tariff_specific': False},
    ]


@pytest.mark.parametrize(
    'name, expected_content, code',
    [
        pytest.param(
            'yellowcarnumber', 'api_yellowcarnumber.json', 200, id='boolean',
        ),
        pytest.param(
            'childchair_v2', 'api_childchair_v2.json', 200, id='multiselect',
        ),
        pytest.param(
            'unknown',
            {
                'status': 'error',
                'message': 'Requirement unknown not found',
                'code': 'unknown_requirement',
            },
            404,
            id='not_found',
        ),
        pytest.param(
            'bad_format',
            {
                'status': 'error',
                'message': (
                    'Requirement bad_format has bad format:'
                    ' position is required property'
                ),
                'code': 'bad_format',
            },
            400,
            id='bad_format',
        ),
    ],
)
async def test_get(
        web_app_client,
        mongo,
        mongodb,
        load_json,
        name,
        expected_content,
        code,
):
    if isinstance(expected_content, str):
        expected_content = load_json(expected_content)
    if name == 'bad_format':
        mongodb.requirements.insert_one({'name': 'bad_format', 'type': 'smth'})

    response = await web_app_client.get(f'/v2/requirements/{name}/')
    assert response.status == code
    content = await response.json()
    assert content == expected_content


@pytest.mark.translations(
    tariff={
        'service_name.yellowcarnumber': {
            'ru': 'Желтые номера',
            'en': 'Yellow plates',
        },
        'service_name.childchair_v2': {
            'ru': 'Детское кресло',
            'en': 'Child seat',
        },
        'service_name.need_empty_trunk': {
            'ru': 'Нужен пустой багажник',
            'en': 'Need empty trunk',
        },
    },
    client_messages={
        'requirement.yellowcarnumber': {
            'ru': 'Желтые номера',
            'en': 'Yellow plates',
        },
        'requirement.childchair_v2': {
            'ru': 'Детское кресло',
            'en': 'Child seat',
        },
        'requirement.childchair_v2.infant': {
            'ru': 'Кресло от 1 до 3 лет',
            'en': 'Chair (from 1 to 3)',
        },
        'requirement.childchair_v2.chair': {
            'ru': 'Кресло от 4 до 7 лет',
            'en': 'Chair (from 4 to 7)',
        },
        'requirement.childchair_v2.booster': {
            'ru': 'Бустер от 7 лет',
            'en': 'Booster (7 and older)',
        },
        'requirement.need_empty_trunk': {
            'ru': 'Нужен пустой багажник',
            'en': 'Need empty trunk',
        },
    },
)
@pytest.mark.parametrize(
    'name, api_request, expected_content, code, is_created',
    [
        pytest.param(
            'yellowcarnumber',
            'api_yellowcarnumber.json',
            {
                'status': 'ok',
                'message': (
                    'requirement `yellowcarnumber` was successfully modified.'
                ),
            },
            200,
            False,
            id='modified',
        ),
        pytest.param(
            'yellowcarnumber',
            'api_yellowcarnumber.json',
            {
                'status': 'ok',
                'message': (
                    'requirement `yellowcarnumber` was successfully created.'
                ),
            },
            200,
            True,
            id='created',
        ),
        pytest.param(
            'childchair_v2',
            'api_childchair_v2.json',
            {
                'status': 'ok',
                'message': (
                    'requirement `childchair_v2` was successfully modified.'
                ),
            },
            200,
            False,
            id='multiselect',
        ),
        pytest.param(
            'need_empty_trunk',
            'api_special.json',
            {
                'status': 'ok',
                'message': (
                    'requirement `need_empty_trunk` was successfully created.'
                ),
            },
            200,
            True,
            id='special',
        ),
    ],
)
async def test_set(
        web_app_client,
        mongo,
        mongodb,
        load_json,
        name,
        api_request,
        expected_content,
        code,
        is_created,
):
    if is_created:
        mongodb.requirements.delete_one({'name': name})

    response = await web_app_client.put(
        f'/v2/requirements/{name}/', json=load_json(api_request),
    )
    assert response.status == code
    content = await response.json()
    assert content == expected_content
