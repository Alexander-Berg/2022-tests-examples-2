import pytest

from infranaim import helper

import app


@pytest.fixture()
def get_suggests(flask_client):
    def do_it(field_name):
        response = flask_client.get(
            '/suggests',
            headers={'Content-Language': 'en'},
            query_string={'field_name': field_name},
        )
        assert response.status_code == 200
        return response.json
    return do_it


@pytest.mark.parametrize(
    'field_name, expected',
    [
        pytest.param('non_exists', [], id='non_exists'),
        pytest.param(
            'source',
            [
                {'id': 'source_1', 'value': 'Source 1'},
                {'id': 'source_2', 'value': 'Source 2'},
            ],
            id='source',
        ),
        pytest.param(
            'education_status',
            [{'id': 'some_field_1', 'value': 'Some field 1'}],
            id='education_status',
        ),
        pytest.param(
            'language_level',
            [{
                'id': 'field_with_translation',
                'value': 'Field with translation',
            }],
            id='with_translations',
        ),
    ],
)
def test_universal(
        log_in,
        get_suggests,
        field_name, expected,
):
    assert get_suggests(field_name) == expected


@pytest.mark.usefixtures('log_in')
@pytest.mark.parametrize(
    'params, status_code',
    [
        ({}, 400),
        ({'feild_name': 'some'}, 400),
        ({'field': 'some'}, 400),
    ],
)
def test_bad_params(
        flask_client,
        params, status_code,
):
    response = flask_client.get(
        '/suggests',
        query_string=params,
    )
    assert response.status_code == status_code


def test_translator():
    with app.app.app_context():
        translator = helper.Translator(
            db=app.app.db,
            data=[{'id': 'key', 'value': 'value to translate'}],
            language='en',
            key_mapper={
                'id_key': 'id',
                'value_key': 'value',
            },
            suggests=[{'_id': 'key', 'suggests': {'en': 'translation'}}],
        )

        assert translator.result == [{'id': 'key', 'value': 'translation'}]


@pytest.mark.usefixtures('log_in')
@pytest.mark.parametrize(
    'params, status_code, expected',
    [
        ({}, 400, 'Fail'),
        ({'city': 'you give love a bad name'}, 400, 'Fail'),
        ({'city': 'катрааси'}, 200, 'узбекистан'),
        ({'city': 'Катрааси'}, 200, 'узбекистан'),
        ({'city': 'небесный_город'}, 200, 'россия'),
    ],
)
def test_suggest_country_by_city(flask_client, params, status_code, expected):
    response = flask_client.get(
        '/suggests/country_by_city',
        query_string=params,
    )
    assert response.status_code == status_code

    if response.status_code == 200:
        country_tag = response.json['country_tag']
        assert country_tag == expected


@pytest.mark.usefixtures('log_in')
@pytest.mark.parametrize(
    'params, status_code',
    [
        ({'city': 'москва'}, 200, ),
    ],
)
def test_suggest_parks(flask_client, load_json, params, status_code, patch):
    @patch('app.suggests._get_parks_request')
    def _tvm(*args, **kwargs):
        return load_json('taxiparks_response.json')

    response = flask_client.get(
        '/suggests/parks',
        query_string=params,
    )
    assert response.status_code == status_code


@pytest.mark.usefixtures('log_in')
@pytest.mark.parametrize(
    'city, code',
    [
        ('Ташкент', '+99'),
        ('ташкент', '+99'),
        ('some', '+7'),
        ('казань', '+7'),
        ('Казань', '+7'),
    ]
)
def test_get_country_code(flask_client, city, code):
    response = flask_client.get(
        '/get_country_code',
        query_string={'city': city},
    )
    assert response.status_code == 200
    data = response.json
    assert data['country_phone_code'] == code


@pytest.mark.parametrize(
    'user_doc, field_name, expected',
    [
        pytest.param(
            {
                'login': 'scout',
                'password': 'scout_pass',
            },
            'non_exists',
            [],
            id='non_existing_field',
        ),
        pytest.param(
            {
                'login': 'scout',
                'password': 'scout_pass',
            },
            'education_status',
            [{'id': 'some_field_1', 'value': 'Some field 1'}],
            id='some_existing_field_without_additional_filters',
        ),
        pytest.param(
            {
                'login': 'agent',
                'password': 'agent_pass',
            },
            'advertisement_campaign',
            [{'id': 'adv_id_1', 'value': 'adv_value_1'}],
            id='advertisement_campaign_with_one_allowed_adv_source',
        ),
        pytest.param(
            {
                'login': 'agent_legal_entity_jp',
                'password': 'scout_pass',
            },
            'advertisement_campaign',
            [
                {'id': 'adv_id_1', 'value': 'adv_value_1'},
                {'id': 'adv_id_2', 'value': 'adv_value_2'},
            ],
            id='advertisement_campaign_with_two_allowed_adv_sources',
        ),
        pytest.param(
            {
                'login': 'agent_legal_entity',
                'password': 'agent_legal_entity_pass',
            },
            'advertisement_campaign',
            [
                {'id': 'adv_id_1', 'value': 'adv_value_1'},
                {'id': 'adv_id_2', 'value': 'adv_value_2'},
            ],
            id='advertisement_campaign_with_two_allowed_adv_sources2',
        ),
        pytest.param(
            {
                'login': 'scout',
                'password': 'scout_pass',
            },
            'advertisement_campaign',
            [
                {'id': 'adv_id_1', 'value': 'adv_value_1'},
                {'id': 'adv_id_2', 'value': 'adv_value_2'},
            ],
            id='advertisement_campaign_without_additional_filters',
        ),
    ],
)
def test_suggests_with_additional_filters(
        flask_client,
        log_user_in,
        csrf_token,
        get_suggests,
        user_doc, field_name, expected,
):
    user_doc['csrf_token'] = csrf_token
    res = log_user_in(user_doc)
    assert res.status_code == 200
    assert get_suggests(field_name) == expected


@pytest.mark.usefixtures('log_in')
@pytest.mark.parametrize(
    'route',
    [
        '/suggests/deaf_relation'
    ]
)
def test_simple_suggests(flask_client, route):
    response = flask_client.get(
        route,
        query_string={},
    )
    assert response.status_code == 200
    assert response.json
