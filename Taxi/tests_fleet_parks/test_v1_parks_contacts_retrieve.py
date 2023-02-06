import datetime

import bson.timestamp
import pytest

from tests_fleet_parks import utils


ENDPOINT = 'v1/parks/contacts/retrieve'


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
async def test_retrieve_ok(taxi_fleet_parks, params, expected_response):

    headers = {'X-Ya-Service-Ticket': utils.SERVICE_TICKET}
    response = await taxi_fleet_parks.get(
        ENDPOINT, params=params, headers=headers,
    )
    assert response.status_code == 200, response.text
    assert response.json() == expected_response


async def test_park_not_found(taxi_fleet_parks):

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
