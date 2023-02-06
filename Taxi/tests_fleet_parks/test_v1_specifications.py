import datetime

import pytest

from tests_fleet_parks import utils

ENDPOINT = 'v1/parks/specifications'

HEADERS = {'X-Ya-Service-Ticket': utils.SERVICE_TICKET}


def _make_params(park_id):
    return {'park_id': park_id}


def _make_request(specifications, passport_uid=None):
    return {
        **(
            {'created_by': {'passport_uid': passport_uid}}
            if passport_uid
            else {}
        ),
        'specifications': specifications,
    }


def check_updated(updated_field):
    assert isinstance(updated_field, datetime.datetime)
    delta = datetime.datetime.utcnow() - updated_field
    assert datetime.timedelta() <= delta < datetime.timedelta(minutes=1)


@pytest.mark.parametrize(
    ('park_id', 'passport_uid', 'request_specs', 'expected_specs'),
    [
        (
            'park_valid2',
            None,
            ['signalq', 'taxi', 'spec2'],
            ['spec1', 'spec2', 'signalq', 'taxi'],
        ),
        ('park_valid1', '123', ['signalq'], ['signalq']),
        ('park_valid2', None, ['spec1', 'taxi'], ['spec1', 'spec2', 'taxi']),
        ('park_valid2', '12345', ['spec2', 'spec1'], ['spec1', 'spec2']),
    ],
)
async def test_add_specifications(
        taxi_fleet_parks,
        mongodb,
        park_id,
        passport_uid,
        request_specs,
        expected_specs,
):
    response = await taxi_fleet_parks.post(
        ENDPOINT,
        headers=HEADERS,
        params=_make_params(park_id),
        json=_make_request(request_specs, passport_uid),
    )
    assert response.status_code == 200, response.text
    result = mongodb.dbparks.find_one({'_id': park_id})
    assert sorted(result['park_specifications']) == sorted(expected_specs)
    check_updated(result['modified_date'])


async def test_not_exist_park(taxi_fleet_parks):
    response = await taxi_fleet_parks.post(
        ENDPOINT,
        headers=HEADERS,
        params=_make_params('Not_exist'),
        json=_make_request(['signalq']),
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'park with id `Not_exist` was not found',
    }


@pytest.mark.parametrize('spec', ['spec3', 'spec4'])
async def test_invalid_specification(taxi_fleet_parks, spec):
    response = await taxi_fleet_parks.post(
        ENDPOINT,
        headers=HEADERS,
        params=_make_params('park_valid2'),
        json=_make_request([spec]),
    )
    assert response.json() == {
        'code': '400',
        'message': f'specification `{spec}` does not exist or disabled',
    }


async def test_empty_specification(taxi_fleet_parks):
    response = await taxi_fleet_parks.post(
        ENDPOINT,
        headers=HEADERS,
        params=_make_params('park_valid2'),
        json=_make_request([]),
    )
    assert response.status_code == 400
