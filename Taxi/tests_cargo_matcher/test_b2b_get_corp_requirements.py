import pytest

CORP_CLIENT_ID = 'corp_client_id_12312312312312312'

HEADERS = {
    'Accept-Language': 'ru',
    'X-B2B-Client-Id': CORP_CLIENT_ID,
    'X-Cargo-Api-Prefix': '/b2b/cargo/integration/',
}


@pytest.fixture(name='request_internal_v1_tariff_requirements')
def _request_internal_v1_tariff_requirements(taxi_cargo_matcher):
    async def wrapper(tariff_class='express'):
        response = await taxi_cargo_matcher.post(
            '/internal/v1/tariff_requirements',
            headers=HEADERS,
            json={
                'homezone': 'moscow',
                'corp_client_id': CORP_CLIENT_ID,
                'tariff_class': tariff_class,
            },
        )
        return response

    return wrapper


@pytest.mark.config(
    CARGO_MATCHER_TARIFF_DESCRIPTIONS_BY_COUNTRY={
        'cargo': {
            'title_key': {'__default__': 'tariff.cargo.title'},
            'text_key': {'__default__': 'tariff.cargo.text'},
        },
    },
    CARGO_MATCHER_TARIFF_REQUIREMENTS={
        'cargo_type': {
            'title_key': 'requirement.cargo_type.title',
            'text_key': 'requirement.cargo_type.text',
            'type': 'select',
            'variants': [
                {
                    'name': 'cargo_type.lcv_m',
                    'title_key': 'cargo_type.lcv_m.title',
                    'text_key': 'cargo_type.lcv_m.text',
                    'value': 'lcv_m',
                },
            ],
        },
    },
)
async def test_cargo_type_change(
        request_internal_v1_tariff_requirements,
        cargo_corp_client_info,
        mocker_tariff_current,
):
    response = await request_internal_v1_tariff_requirements(
        tariff_class='cargo',
    )

    assert response.status_code == 200
    assert response.json()['requirements'][0]['name'] == 'cargo_type_int'
    assert response.json()['requirements'][0]['options'][0]['value'] == 1


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_matcher_additional_tariff_requirements',
    consumers=['cargo-matcher/additional_tariff_requirements'],
    clauses=[],
    is_config=True,
    default_value={
        'requirements': [
            {
                'type': 'bool',
                'name': 'add_req1',
                'title_tanker_key': 'requirement.add_req1.title',
                'text_tanker_key': 'requirement.add_req1.text',
                'default': False,
                'required': True,
            },
            {
                'type': 'bool',
                'name': 'add_req2',
                'title_tanker_key': 'requirement.add_req2.title',
                'text_tanker_key': 'requirement.add_req2.text',
                'default': True,
                'required': False,
            },
        ],
    },
)
async def test_requirements_for_b2b_tariff(
        request_internal_v1_tariff_requirements,
        cargo_corp_client_info,
        mocker_tariff_current,
):
    mocker_tariff_current()
    response = await request_internal_v1_tariff_requirements()

    assert response.status_code == 200
    assert response.json() == {
        'requirements': [
            {
                'default': True,
                'name': 'door_to_door',
                'required': False,
                'text': 'От двери до двери',
                'title': 'От двери до двери',
                'type': 'bool',
            },
            {
                'default': False,
                'name': 'add_req1',
                'required': True,
                'text': 'requirement.add_req1.text',
                'title': 'requirement.add_req1.title',
                'type': 'bool',
            },
            {
                'default': True,
                'name': 'add_req2',
                'required': False,
                'text': 'requirement.add_req2.text',
                'title': 'requirement.add_req2.title',
                'type': 'bool',
            },
        ],
    }


@pytest.mark.config(
    CARGO_MATCHER_TARIFF_OPTIONS={
        'auto_courier': {
            'title_key': 'requirement.cargo_options.auto_courier.title',
            'text_key': 'requirement.cargo_options.auto_courier.text',
        },
    },
    CARGO_TARIFF_OPTIONS_EXPERIMENTS={'express': 'cargo_tariff_cargo_options'},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_tariff_cargo_options',
    consumers=['cargo-matcher/tariff-options'],
    clauses=[],
    is_config=True,
    default_value={'options': ['auto_courier']},
)
async def test_b2b_get_tariff_requirements_cargo_options(
        request_internal_v1_tariff_requirements,
        conf_exp3_requirements_from_options,
        cargo_corp_client_info,
        mocker_tariff_current,
):
    mocker_tariff_current()
    await conf_exp3_requirements_from_options(requirement='auto_courier')
    response = await request_internal_v1_tariff_requirements()

    assert response.status_code == 200
    assert response.json() == {
        'requirements': [
            {
                'default': False,
                'name': 'auto_courier',
                'required': False,
                'text': 'requirement.cargo_options.auto_courier.text',
                'title': 'requirement.cargo_options.auto_courier.title',
                'type': 'bool',
            },
            {
                'default': True,
                'name': 'door_to_door',
                'required': False,
                'text': 'От двери до двери',
                'title': 'От двери до двери',
                'type': 'bool',
            },
        ],
    }
