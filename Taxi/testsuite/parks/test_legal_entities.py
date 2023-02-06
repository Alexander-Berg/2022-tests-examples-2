import json

import pytest

from . import error


ENDPOINT_URL = '/legal-entities'
DADATA_URL = '/dadata/suggestions/api/4_1/rs/findById/party'
DEFAULT_COUNTRY_RULES = [{'country_id': 'rus', 'rules': ['1', '11']}]


def get_legal_entity(db, park_id, ogrn):
    return db.dbparks_legal_entities.find_one(
        {'park_id': park_id, 'registration_number': ogrn},
    )


@pytest.mark.config(PARKS_LEGAL_ENTITY_INN_COUNTRY_RULES=DEFAULT_COUNTRY_RULES)
@pytest.mark.config(PARKS_LEGAL_ENTITY_SUPPORTED_COUNTRIES=['rus'])
@pytest.mark.parametrize(
    'stop_list',
    [
        ([]),
        (
            [
                {'id': '0123456789123', 'country': 'rus'},
                {'id': '2', 'country': 'ukr'},
            ]
        ),
    ],
)
@pytest.mark.parametrize(
    'legal_entity, dadata_response, dadata_code,'
    ' enable_dadata, allow_invalid, '
    'check_private_address',
    [
        (
            {
                'registration_number': '2',
                'name': 'Petrov',
                'address': 'Loukhi Sudozavodskaya 9 17',
                'work_hours': 'mon-fr 11-13',
                'type': 'carrier_permit_owner',
                'legal_type': 'private',
            },
            None,
            None,
            False,
            False,
            False,
        ),
        (
            {
                'registration_number': '50',
                'name': 'Petrov',
                'address': 'Loukhi Sudozavodskaya 9 17',
                'work_hours': 'mon-fr 11-13',
                'type': 'carrier_permit_owner',
                'legal_type': 'private',
            },
            {
                'suggestions': [
                    {
                        'value': 'Petrov',
                        'data': {
                            'type': 'INDIVIDUAL',
                            'ogrn': '50',
                            'address': {'value': 'Loukhi'},
                        },
                    },
                ],
            },
            200,
            True,
            False,
            False,
        ),
        (
            {
                'registration_number': '50',
                'name': 'Petrov',
                'address': 'Loukhi',
                'work_hours': 'mon-fr 11-13',
                'type': 'carrier_permit_owner',
                'legal_type': 'private',
            },
            {
                'suggestions': [
                    {
                        'value': 'Petrov',
                        'data': {
                            'type': 'INDIVIDUAL',
                            'ogrn': '50',
                            'address': {'value': 'Loukhi'},
                        },
                    },
                ],
            },
            200,
            True,
            False,
            True,
        ),
        (
            {
                'registration_number': '51',
                'name': 'Petrov',
                'address': 'Loukhi Sudozavodskaya 9 17',
                'work_hours': 'mon-fr 11-13',
                'type': 'carrier_permit_owner',
                'legal_type': 'private',
            },
            {
                'suggestions': [
                    {'value': 'Petrov', 'data': {'type': 'INDIVIDUAL'}},
                    {
                        'value': 'Petrov',
                        'data': {
                            'type': 'INDIVIDUAL',
                            'ogrn': '51',
                            'address': {},
                        },
                    },
                ],
            },
            200,
            True,
            False,
            False,
        ),
        (
            {
                'registration_number': '52',
                'name': 'Petrov',
                'address': 'Loukhi Sudozavodskaya 9 17',
                'work_hours': 'mon-fr 11-13',
                'type': 'carrier_permit_owner',
                'legal_type': 'legal',
            },
            {
                'suggestions': [
                    {
                        'value': 'Petrov',
                        'data': {
                            'type': 'LEGAL',
                            'ogrn': '52',
                            'address': {'value': 'Loukhi Sudozavodskaya 9 17'},
                        },
                    },
                ],
            },
            200,
            True,
            False,
            False,
        ),
        (
            {
                'registration_number': '53',
                'name': '',
                'address': '',
                'work_hours': '',
                'type': 'carrier_permit_owner',
                'legal_type': 'private',
            },
            {'suggestions': []},
            200,
            True,
            True,
            False,
        ),
        (
            {
                'registration_number': '54',
                'name': '',
                'address': '',
                'work_hours': '',
                'type': 'carrier_permit_owner',
                'legal_type': 'legal',
            },
            {'error': 'error'},
            403,
            True,
            True,
            False,
        ),
    ],
)
def test_post_ok(
        db,
        taxi_parks,
        mockserver,
        config,
        stop_list,
        legal_entity,
        dadata_response,
        dadata_code,
        enable_dadata,
        allow_invalid,
        check_private_address,
):
    config.set_values(
        dict(
            PARKS_LEGAL_ENTITY_STOP_LIST2=stop_list,
            PARKS_ENABLE_DADATA_VALIDATION=enable_dadata,
            PARKS_ALLOW_DADATA_INVALID_RESULT=allow_invalid,
            PARKS_LEGAL_ENTITY_CHECK_PRIVATE_ADDRESS=check_private_address,
        ),
    )

    @mockserver.json_handler(DADATA_URL)
    def mock_callback(request):
        request.get_data()
        return mockserver.make_response(
            json.dumps(dadata_response), dadata_code,
        )

    response = taxi_parks.post(
        ENDPOINT_URL, params={'park_id': '123'}, data=json.dumps(legal_entity),
    )

    ogrn = legal_entity['registration_number']

    assert response.status_code == 200, response.text

    if enable_dadata:
        assert mock_callback.times_called == 1
        dadata_request = mock_callback.next_call()['request']
        assert json.loads(dadata_request.get_data()) == {'query': ogrn}
    else:
        assert mock_callback.times_called == 0

    legal_entity.update({'park_id': '123'})
    assert 'id' in response.json()
    response_to_check = response.json()
    response_to_check.pop('id')
    assert response_to_check == legal_entity

    legal_entities_in_mongo = get_legal_entity(db, '123', ogrn)
    assert legal_entities_in_mongo.pop('_id') is not None
    assert legal_entities_in_mongo.pop('created_date') is not None
    assert legal_entities_in_mongo.pop('modified_date') is not None
    assert legal_entities_in_mongo == legal_entity


@pytest.mark.config(PARKS_LEGAL_ENTITY_INN_COUNTRY_RULES=DEFAULT_COUNTRY_RULES)
@pytest.mark.config(PARKS_LEGAL_ENTITY_SUPPORTED_COUNTRIES=['rus'])
@pytest.mark.config(PARKS_ENABLE_DADATA_VALIDATION=False)
@pytest.mark.config(PARKS_ALLOW_DADATA_INVALID_RESULT=False)
def test_post_already_exists(db, taxi_parks):
    legal_entity = {
        'registration_number': '1',
        'name': 'Petya',
        'address': 'Omsk',
        'work_hours': '11-13',
        'type': 'carrier_permit_owner',
        'legal_type': 'legal',
    }

    response = taxi_parks.post(
        ENDPOINT_URL, params={'park_id': '123'}, data=json.dumps(legal_entity),
    )

    assert response.status_code == 409, response.text
    assert response.json() == error.make_error_response(
        'Duplicate <park_id, registration_number>.',
    )


@pytest.mark.config(PARKS_LEGAL_ENTITY_SUPPORTED_COUNTRIES=[])
def test_post_no_such_park(db, taxi_parks):
    response = taxi_parks.post(ENDPOINT_URL, params={'park_id': '000'})

    assert response.status_code == 404, response.text
    assert response.json() == error.make_error_response(
        'park with id `000` not found',
    )


@pytest.mark.config(PARKS_LEGAL_ENTITY_SUPPORTED_COUNTRIES=['rus'])
def test_post_unsupported_country(db, taxi_parks):
    response = taxi_parks.post(ENDPOINT_URL, params={'park_id': '124'})

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(
        'unsupported country: fra', 'unsupported_country',
    )


@pytest.mark.config(PARKS_LEGAL_ENTITY_INN_COUNTRY_RULES=DEFAULT_COUNTRY_RULES)
@pytest.mark.config(PARKS_LEGAL_ENTITY_SUPPORTED_COUNTRIES=['rus'])
@pytest.mark.config(PARKS_ENABLE_DADATA_VALIDATION=True)
@pytest.mark.config(PARKS_ALLOW_DADATA_INVALID_RESULT=False)
def test_post_dadata_failed(db, mockserver, taxi_parks):
    @mockserver.json_handler(DADATA_URL)
    def mock_callback(request):
        request.get_data()
        return mockserver.make_response('some error', 429)

    response = taxi_parks.post(
        ENDPOINT_URL,
        params={'park_id': '123'},
        data=json.dumps(
            {
                'registration_number': '1',
                'name': 'Petya',
                'address': 'Omsk',
                'work_hours': '11-13',
                'type': 'carrier_permit_owner',
                'legal_type': 'legal',
            },
        ),
    )

    assert mock_callback.times_called == 1
    assert response.status_code == 503, response.text


@pytest.mark.config(PARKS_LEGAL_ENTITY_INN_COUNTRY_RULES=DEFAULT_COUNTRY_RULES)
@pytest.mark.config(PARKS_LEGAL_ENTITY_SUPPORTED_COUNTRIES=['rus'])
@pytest.mark.config(PARKS_ENABLE_DADATA_VALIDATION=True)
@pytest.mark.config(PARKS_ALLOW_DADATA_INVALID_RESULT=False)
@pytest.mark.parametrize(
    'legal_entity, dadata_response, ' 'check_private_address',
    [
        (
            {
                'registration_number': '1',
                'name': 'Petrov',
                'address': 'Loukhi Sudozavodskaya 9 17',
                'work_hours': 'mon-fr 11-13',
                'type': 'carrier_permit_owner',
                'legal_type': 'private',
            },
            {'suggestions': []},
            False,
        ),
        (
            {
                'registration_number': '1',
                'name': 'Petrov',
                'address': 'Loukhi Sudozavodskaya 9 17',
                'work_hours': 'mon-fr 11-13',
                'type': 'carrier_permit_owner',
                'legal_type': 'private',
            },
            {
                'suggestions': [
                    {
                        'data': {
                            'type': 'INDIVIDUAL',
                            'ogrn': '1',
                            'address': {'value': 'Loukhi'},
                        },
                    },
                ],
            },
            False,
        ),
        (
            {
                'registration_number': '1',
                'name': 'Petrov',
                'address': 'Loukhi Sudozavodskaya 9 17',
                'work_hours': 'mon-fr 11-13',
                'type': 'carrier_permit_owner',
                'legal_type': 'private',
            },
            {
                'suggestions': [
                    {
                        'value': 'Petrov',
                        'data': {
                            'type': 'INDIVIDUAL',
                            'ogrn': '1',
                            'address': {'value': 'Loukhi'},
                        },
                    },
                ],
            },
            True,
        ),
        (
            {
                'registration_number': '1',
                'name': 'Petrov',
                'address': 'Loukhi Sudozavodskaya 9 17',
                'work_hours': 'mon-fr 11-13',
                'type': 'carrier_permit_owner',
                'legal_type': 'legal',
            },
            {
                'suggestions': [
                    {
                        'value': 'Petrov',
                        'data': {
                            'type': 'LEGAL',
                            'ogrn': '1',
                            'address': {'value': 'Loukhi'},
                        },
                    },
                ],
            },
            False,
        ),
    ],
)
def test_post_dadata_not_equal(
        mockserver,
        taxi_parks,
        config,
        legal_entity,
        dadata_response,
        check_private_address,
):
    config.set_values(
        dict(PARKS_LEGAL_ENTITY_CHECK_PRIVATE_ADDRESS=check_private_address),
    )

    @mockserver.json_handler(DADATA_URL)
    def mock_callback(request):
        return dadata_response

    response = taxi_parks.post(
        ENDPOINT_URL, params={'park_id': '123'}, data=json.dumps(legal_entity),
    )

    assert mock_callback.times_called == 1
    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(
        'dadata check failed', 'dadata_check_failed',
    )


@pytest.mark.config(PARKS_LEGAL_ENTITY_INN_COUNTRY_RULES=DEFAULT_COUNTRY_RULES)
@pytest.mark.config(PARKS_LEGAL_ENTITY_SUPPORTED_COUNTRIES=['rus'])
@pytest.mark.config(
    PARKS_LEGAL_ENTITY_STOP_LIST2=[
        {'id': '1', 'country': 'rus'},
        {'id': 'ogrn2', 'country': 'rus'},
    ],
)
@pytest.mark.parametrize('method_str', ['post', 'put'])
def test_post_forbbiden_ogrn(taxi_parks, method_str):
    method = {'post': taxi_parks.post, 'put': taxi_parks.put}

    response = method[method_str](
        ENDPOINT_URL,
        params={'park_id': '123', 'id': 'asd'},
        data=json.dumps(
            {
                'registration_number': '1',
                'name': '',
                'address': '',
                'work_hours': '',
                'type': 'carrier_permit_owner',
                'legal_type': 'private',
            },
        ),
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(
        'forbidden registration number', 'forbidden_registration_number',
    )


@pytest.mark.config(PARKS_LEGAL_ENTITY_INN_COUNTRY_RULES=DEFAULT_COUNTRY_RULES)
@pytest.mark.config(PARKS_LEGAL_ENTITY_SUPPORTED_COUNTRIES=['rus'])
@pytest.mark.config(PARKS_LEGAL_ENTITY_CHECK_PRIVATE_ADDRESS=False)
@pytest.mark.parametrize(
    'legal_entity, dadata_response, '
    'dadata_code, enable_dadata, allow_invalid',
    [
        (
            {
                'registration_number': '3',
                'name': 'Petrov',
                'address': 'Loukhi Sudozavodskaya 9 17',
                'work_hours': 'mon-fr 11-13',
                'type': 'carrier_permit_owner',
                'legal_type': 'private',
            },
            None,
            None,
            False,
            False,
        ),
        (
            {
                'registration_number': '3',
                'name': 'Petrov',
                'address': 'Loukhi Sudozavodskaya 9 17',
                'work_hours': 'mon-fr 11-13',
                'type': 'carrier_permit_owner',
                'legal_type': 'private',
            },
            {
                'suggestions': [
                    {
                        'value': 'Petrov',
                        'data': {
                            'type': 'INDIVIDUAL',
                            'ogrn': '3',
                            'address': {'value': 'Loukhi'},
                        },
                    },
                ],
            },
            200,
            True,
            False,
        ),
        (
            {
                'registration_number': '3',
                'name': '',
                'address': '',
                'work_hours': '',
                'type': 'carrier_permit_owner',
                'legal_type': 'private',
            },
            {'suggestions': []},
            200,
            True,
            True,
        ),
    ],
)
def test_put_ok(
        db,
        mockserver,
        taxi_parks,
        config,
        legal_entity,
        dadata_response,
        dadata_code,
        enable_dadata,
        allow_invalid,
):
    config.set_values(
        dict(
            PARKS_ENABLE_DADATA_VALIDATION=enable_dadata,
            PARKS_ALLOW_DADATA_INVALID_RESULT=allow_invalid,
        ),
    )

    id = '5b5984fdfefe3d7ba0ac1234'

    @mockserver.json_handler(DADATA_URL)
    def mock_callback(request):
        request.get_data()
        return mockserver.make_response(
            json.dumps(dadata_response), dadata_code,
        )

    response = taxi_parks.put(
        ENDPOINT_URL,
        params={'park_id': '123', 'id': id},
        data=json.dumps(legal_entity),
    )

    ogrn = legal_entity['registration_number']

    assert response.status_code == 200, response.text

    if enable_dadata:
        assert mock_callback.times_called == 1
        dadata_request = mock_callback.next_call()['request']
        assert json.loads(dadata_request.get_data()) == {'query': ogrn}
    else:
        assert mock_callback.times_called == 0

    legal_entity.update({'park_id': '123'})

    legal_entities_in_mongo = get_legal_entity(db, '123', ogrn)

    assert response.status_code == 200, response.text
    assert 'id' in response.json()
    response_to_check = response.json()
    response_to_check.pop('id')
    assert response_to_check == legal_entity
    assert legal_entities_in_mongo.pop('_id') is not None
    assert legal_entities_in_mongo.pop('created_date') is not None
    assert legal_entities_in_mongo.pop('modified_date') is not None
    assert legal_entities_in_mongo == legal_entity


@pytest.mark.config(PARKS_LEGAL_ENTITY_INN_COUNTRY_RULES=DEFAULT_COUNTRY_RULES)
@pytest.mark.config(PARKS_LEGAL_ENTITY_SUPPORTED_COUNTRIES=['rus'])
@pytest.mark.config(PARKS_ENABLE_DADATA_VALIDATION=False)
@pytest.mark.config(PARKS_ALLOW_DADATA_INVALID_RESULT=False)
@pytest.mark.parametrize(
    'park_id,id,expected_code,' 'expected_response, error_code',
    [
        (
            '123',
            '5b5984fdfefe3d7ba0ac0000',
            400,
            'no such legal entity',
            'invalid_request',
        ),
        (
            '123',
            '5b5984fdfefe3d7ba0ac1234',
            409,
            'Duplicate <park_id, registration_number>.',
            None,
        ),
        (
            '000',
            '5b5984fdfefe3d7ba0ac1234',
            404,
            'park with id `000` not found',
            None,
        ),
        (
            '124',
            '5b5984fdfefe3d7ba0ac0000',
            400,
            'unsupported country: fra',
            'unsupported_country',
        ),
    ],
)
def test_put_not_ok(
        taxi_parks, park_id, id, expected_code, expected_response, error_code,
):
    legal_entity = {
        'registration_number': '10',
        'name': 'Ivanov',
        'address': 'Spb 9 17',
        'work_hours': '11-13',
        'type': 'carrier_permit_owner',
        'legal_type': 'legal',
    }

    response = taxi_parks.put(
        ENDPOINT_URL,
        params={'park_id': park_id, 'id': id},
        data=json.dumps(legal_entity),
    )

    assert response.status_code == expected_code, response.text
    assert response.json() == (
        error.make_error_response(expected_response, error_code)
    )


def test_get_ok(taxi_parks):
    id = '5b5984fdfefe3d7ba0ac1235'

    legal_entity = {
        'registration_number': '10',
        'name': 'Ivanov2',
        'address': 'Msk2',
        'work_hours': '11-14',
        'park_id': '123',
        'type': 'carrier_permit_owner',
        'legal_type': 'legal',
    }

    response = taxi_parks.get(
        ENDPOINT_URL, params={'park_id': '123', 'id': id},
    )

    assert response.status_code == 200, response.text
    assert 'id' in response.json()
    response_to_check = response.json()
    response_to_check.pop('id')
    assert response_to_check == legal_entity


def test_invalid_id(taxi_parks):
    id = 'invalid_oid'

    response = taxi_parks.get(
        ENDPOINT_URL, params={'park_id': '000', 'id': id},
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(
        'Invalid oid=' + id, 'invalid_request',
    )


@pytest.mark.config(
    PARKS_LEGAL_ENTITY_INN_COUNTRY_RULES=[
        {'country_id': 'rus', 'rules': ['11']},
    ],
)
@pytest.mark.config(PARKS_LEGAL_ENTITY_SUPPORTED_COUNTRIES=['rus'])
def test_invalid_format1(db, mockserver, taxi_parks):
    response = taxi_parks.post(
        ENDPOINT_URL,
        params={'park_id': '123'},
        data=json.dumps(
            {
                'registration_number': '1',
                'name': 'Petya',
                'address': 'Omsk',
                'work_hours': '11-13',
                'type': 'carrier_permit_owner',
                'legal_type': 'legal',
            },
        ),
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(
        'invalid registration number format',
        'invalid_registration_number_format',
    )


@pytest.mark.config(PARKS_LEGAL_ENTITY_INN_COUNTRY_RULES=[])
@pytest.mark.config(PARKS_LEGAL_ENTITY_SUPPORTED_COUNTRIES=['rus'])
def test_invalid_format_500(db, mockserver, taxi_parks):
    response = taxi_parks.post(
        ENDPOINT_URL,
        params={'park_id': '123'},
        data=json.dumps(
            {
                'registration_number': '1',
                'name': 'Petya',
                'address': 'Omsk',
                'work_hours': '11-13',
                'type': 'carrier_permit_owner',
                'legal_type': 'legal',
            },
        ),
    )

    assert response.status_code == 500, response.text


@pytest.mark.config(
    PARKS_LEGAL_ENTITY_INN_COUNTRY_RULES=[
        {'country_id': 'fra', 'rules': ['1A']},
    ],
)
@pytest.mark.config(PARKS_LEGAL_ENTITY_SUPPORTED_COUNTRIES=['fra'])
@pytest.mark.config(PARKS_ENABLE_DADATA_VALIDATION=True)
@pytest.mark.config(PARKS_ALLOW_DADATA_INVALID_RESULT=False)
def test_post_not_russia(db, mockserver, taxi_parks):
    @mockserver.json_handler(DADATA_URL)
    def mock_callback(request):
        return {}

    legal_entity = {
        'registration_number': '1a',
        'name': 'Petya',
        'address': 'Omsk',
        'work_hours': '11-13',
        'type': 'carrier_permit_owner',
        'legal_type': 'legal',
    }

    response = taxi_parks.post(
        ENDPOINT_URL, params={'park_id': '124'}, data=json.dumps(legal_entity),
    )

    assert response.status_code == 200, response.text

    assert mock_callback.times_called == 0

    legal_entity.update({'park_id': '124'})
    assert 'id' in response.json()
    response_to_check = response.json()
    response_to_check.pop('id')
    assert response_to_check == legal_entity

    legal_entities_in_mongo = get_legal_entity(db, '124', '1a')
    assert legal_entities_in_mongo.pop('_id') is not None
    assert legal_entities_in_mongo.pop('created_date') is not None
    assert legal_entities_in_mongo.pop('modified_date') is not None
    assert legal_entities_in_mongo == legal_entity


@pytest.mark.config(
    PARKS_LEGAL_ENTITY_INN_COUNTRY_RULES=[
        {'country_id': 'fra', 'rules': ['1A']},
    ],
)
@pytest.mark.config(PARKS_LEGAL_ENTITY_SUPPORTED_COUNTRIES=['fra'])
@pytest.mark.config(PARKS_ENABLE_DADATA_VALIDATION=True)
@pytest.mark.config(PARKS_ALLOW_DADATA_INVALID_RESULT=False)
def test_put_not_russia(db, mockserver, taxi_parks):
    @mockserver.json_handler(DADATA_URL)
    def mock_callback(request):
        return {}

    id = '5b5984fdfefe3d7ef0ac1238'
    legal_entity = {
        'registration_number': '1a',
        'name': 'Petya',
        'address': 'Omsk',
        'work_hours': '11-13',
        'type': 'carrier_permit_owner',
        'legal_type': 'legal',
    }

    response = taxi_parks.put(
        ENDPOINT_URL,
        params={'park_id': '124', 'id': id},
        data=json.dumps(legal_entity),
    )

    assert response.status_code == 200, response.text

    assert mock_callback.times_called == 0

    legal_entity.update({'park_id': '124'})
    legal_entity.update({'id': id})
    assert response.json() == legal_entity

    legal_entities_in_mongo = get_legal_entity(db, '124', '1a')
    assert legal_entities_in_mongo.pop('_id') is not None
    assert legal_entities_in_mongo.pop('created_date') is not None
    assert legal_entities_in_mongo.pop('modified_date') is not None
    legal_entity.pop('id')
    assert legal_entities_in_mongo == legal_entity


@pytest.mark.config(
    PARKS_LEGAL_ENTITY_INN_COUNTRY_RULES=[
        {'country_id': 'fra', 'rules': ['1A']},
    ],
)
@pytest.mark.config(PARKS_LEGAL_ENTITY_SUPPORTED_COUNTRIES=['fra'])
@pytest.mark.config(PARKS_ENABLE_DADATA_VALIDATION=True)
@pytest.mark.config(PARKS_ALLOW_DADATA_INVALID_RESULT=False)
def test_normalization(db, mockserver, taxi_parks):
    legal_entity = {
        'registration_number': ' 1a  ',
        'name': 'Petya',
        'address': 'Omsk',
        'work_hours': '11-13',
        'type': 'carrier_permit_owner',
        'legal_type': 'legal',
    }

    response = taxi_parks.post(
        ENDPOINT_URL, params={'park_id': '124'}, data=json.dumps(legal_entity),
    )

    assert response.status_code == 200, response.text
    legal_entity['park_id'] = '124'
    legal_entity['registration_number'] = '1a'
    assert 'id' in response.json()
    response_to_check = response.json()
    response_to_check.pop('id')
    assert response_to_check == legal_entity
