import datetime

import bson.timestamp
import pytest

from tests_fleet_parks import utils


ENDPOINT = 'v1/parks/contacts'

HEADERS = {
    'X-Ya-User-Ticket': '_!fake!_ya-11',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Ya-Service-Ticket': utils.SERVICE_TICKET,
}


@pytest.fixture(autouse=True)
def personal_data_request(mockserver):
    @mockserver.json_handler('/personal/v1/emails/store')
    def _emails_store(request):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }

    @mockserver.json_handler('/personal/v1/phones/store')
    def _phones_store(request):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _phones_retrieve(request):
        phone_id = request.json['id']
        return {
            'id': phone_id,
            'value': phone_id[:-3] if phone_id.endswith('_id') else '',
        }

    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _emails_retrieve(request):
        email_id = request.json['id']
        return {
            'id': email_id,
            'value': email_id[:-3] if email_id.endswith('_id') else '',
        }


def check_updated(updated_field):
    assert isinstance(updated_field, datetime.datetime)
    delta = datetime.datetime.utcnow() - updated_field
    assert datetime.timedelta() <= delta < datetime.timedelta(minutes=1)


def check_updated_ts(updated_field):
    assert isinstance(updated_field, bson.timestamp.Timestamp)
    check_updated(datetime.datetime.utcfromtimestamp(updated_field.time))
    assert updated_field.inc > 0


TEST_GET_PARAMS = [
    (
        {'park_id': 'park_valid1'},
        {
            'drivers': {
                'email': 'driver@',
                'phone': '+322',
                'address': 'drivers_address',
                'address_coordinates': {
                    'lon': '37.123123',
                    'lat': '69.321321',
                },
                'schedule': 'drivers_schedule',
                'money_withdrawal': {'description': 'description'},
            },
            'passengers': {'phone': '+1337'},
            'description': 'top park, wow',
        },
    ),
    (
        {'park_id': 'park_valid2'},
        {'drivers': {'email': 'driver@', 'phone': '+322'}},
    ),
    ({'park_id': 'park_valid4'}, {}),
]


@pytest.mark.parametrize('params, expected_response', TEST_GET_PARAMS)
async def test_get_ok(taxi_fleet_parks, params, expected_response):

    headers = {'X-Ya-Service-Ticket': utils.SERVICE_TICKET}
    response = await taxi_fleet_parks.get(
        ENDPOINT, params=params, headers=headers,
    )
    assert response.status_code == 200, response.text
    assert response.json() == expected_response


async def test_get_park_not_found(taxi_fleet_parks):

    headers = {'X-Ya-Service-Ticket': utils.SERVICE_TICKET}
    params = {'park_id': 'unknown park id'}

    response = await taxi_fleet_parks.get(
        ENDPOINT, params=params, headers=headers,
    )
    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'park_not_found',
        'message': 'park not found',
    }


TEST_PUT_OK_PARAMS = [
    (
        {'park_id': 'park_valid1'},
        {
            'drivers': {
                'schedule': 'sch',
                'address': 'addr',
                'address_coordinates': {
                    'lon': '37.123123',
                    'lat': '69.321312',
                },
                'email': 'email@mail.com',
                'phone': '+123',
                'money_withdrawal': {'description': 'description'},
            },
            'passengers': {'phone': '+1337'},
            'description': 'new park description',
        },
        {
            'drivers': {
                'schedule': 'sch',
                'address': 'addr',
                'address_coordinates': {
                    'lon': '37.123123',
                    'lat': '69.321312',
                },
                'email': 'email@mail.com_id',
                'phone': '+123_id',
                'money_withdrawal': {'description': 'description'},
            },
            'passengers': {'phone': '+1337_id'},
            'description': 'new park description',
        },
    ),
    (
        {'park_id': 'park_valid2'},
        {'description': 'park2 desc'},
        {'description': 'park2 desc'},
    ),
    (
        {'park_id': 'park_valid2'},
        {'drivers': {'email': 'driver@mail.com', 'phone': '+3238382'}},
        {'drivers': {'email': 'driver@mail.com_id', 'phone': '+3238382_id'}},
    ),
    (
        {'park_id': 'park_valid5'},
        {'passengers': {'phone': '32'}},
        {'passengers': {'phone': '32_id'}},
    ),
    ({'park_id': 'park_valid4'}, {}, {}),
]


@pytest.mark.config(
    PARKS_CONTACTS_FIELDS_LENGTH={
        'description': 1000,
        'money_withdrawal_description': 1000,
        'address': 1000,
        'schedule': 1000,
        'email': 50,
    },
)
@pytest.mark.parametrize('params, request_body, mongo_doc', TEST_PUT_OK_PARAMS)
async def test_put_ok(
        taxi_fleet_parks, params, request_body, mongo_doc, mongodb,
):

    response = await taxi_fleet_parks.put(
        ENDPOINT, params=params, headers=HEADERS, json=request_body,
    )
    expected_response = request_body.copy()

    assert response.status_code == 200, response.text
    assert response.json() == expected_response

    park_doc = mongodb.dbparks.find_one({'_id': params['park_id']})

    assert park_doc.pop('description', '') == mongo_doc.pop('description', '')
    assert park_doc['park_contacts'] == mongo_doc
    check_updated_ts(park_doc.pop('updated_ts'))
    check_updated(park_doc.pop('modified_date'))


@pytest.mark.config(
    PARKS_CONTACTS_FIELDS_LENGTH={
        'description': 1000,
        'money_withdrawal_description': 1000,
        'address': 1000,
        'schedule': 1000,
        'email': 50,
    },
)
async def test_put_park_not_found(taxi_fleet_parks):

    params = {'park_id': 'unknown park id'}

    response = await taxi_fleet_parks.get(
        ENDPOINT, params=params, headers=HEADERS, json={},
    )
    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'park_not_found',
        'message': 'park not found',
    }


TEST_PUT_BAD_PARAMS = [
    (
        {'drivers': {'email': 'oh shit'}},
        {
            'code': 'invalid_drivers_email',
            'message': 'email must be in correct format',
        },
    ),
    (
        {'drivers': {'phone': '023210983210938201983091280398'}},
        {
            'code': 'invalid_drivers_phone',
            'message': 'phone must be in correct format',
        },
    ),
    (
        {'drivers': {'email': 'ti@.mail'}},
        {
            'code': 'invalid_drivers_email',
            'message': 'email must be in correct format',
        },
    ),
    (
        {'drivers': {'email': 'привет@mail.ru'}},
        {
            'code': 'invalid_drivers_email',
            'message': 'email must be in correct format',
        },
    ),
    (
        {'passengers': {'phone': 'badphone'}},
        {
            'code': 'invalid_passengers_phone',
            'message': 'phone must be in correct format',
        },
    ),
    (
        {'description': 'a' * 1001},
        {'code': 'long_description', 'message': 'description must be shorter'},
    ),
    (
        {'description': '1234 5469 et 7000-1349-3448 sber'},
        {
            'code': 'payment_card_number_in_description',
            'message': 'field must not contain payment card numbers',
        },
    ),
    (
        {'drivers': {'schedule': '1234 5469 et 7000-1349-3448 sber'}},
        {
            'code': 'payment_card_number_in_drivers_schedule',
            'message': 'field must not contain payment card numbers',
        },
    ),
    (
        {'drivers': {'address': '1234 5469 et 7000-1349-3448 sber'}},
        {
            'code': 'payment_card_number_in_drivers_address',
            'message': 'field must not contain payment card numbers',
        },
    ),
    (
        {
            'drivers': {
                'money_withdrawal': {
                    'description': '1234 5469 et 7000-1349-3448 sber',
                },
            },
        },
        {
            'code': (
                'payment_card_number_in_drivers_money_withdrawal_description'
            ),
            'message': 'field must not contain payment card numbers',
        },
    ),
    (
        {'drivers': {'money_withdrawal': {'description': 'a' * 1001}}},
        {
            'code': 'long_money_withdrawal_description',
            'message': 'money withdrawal description must be shorter',
        },
    ),
    (
        {'drivers': {'email': 'ti@mail.ru' + 'a' * 100}},
        {'code': 'long_drivers_email', 'message': 'email must be shorter'},
    ),
    (
        {'drivers': {'schedule': 'a' * 1001}},
        {'code': 'long_schedule', 'message': 'schedule must be shorter'},
    ),
    (
        {'drivers': {'address': 'э' * 1001}},
        {'code': 'long_address', 'message': 'address must be shorter'},
    ),
]


@pytest.mark.config(
    PARKS_CONTACTS_FIELDS_LENGTH={
        'description': 1000,
        'money_withdrawal_description': 1000,
        'address': 1000,
        'schedule': 1000,
        'email': 50,
    },
)
@pytest.mark.parametrize('request_body, error_obj', TEST_PUT_BAD_PARAMS)
async def test_put_bad_request(
        taxi_fleet_parks, error_obj, request_body, mongodb,
):

    response = await taxi_fleet_parks.put(
        ENDPOINT,
        params={'park_id': 'park_valid1'},
        headers=HEADERS,
        json=request_body,
    )

    assert response.status_code == 400, response.text
    assert response.json() == error_obj
