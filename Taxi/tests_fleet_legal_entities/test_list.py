import itertools

import pymongo
import pytest

PARK_ID = 'park_id1'
PARK_ID_NOT_FOUND = 'park_id2'
PARK_ID_COUNTRY_NOT_FOUND = 'park_id3'

ENDPOINT = '/fleet/fleet-legal-entities/v1/carriers/list'

COUNTRIES = {
    'rus': {'field_ids': ['work_hours'], 'registration_number_alias': 'ogrn'},
}

RUS_PROJECTION = {'registration_number', 'name', 'work_hours', 'address'}


def _check_equal(mongo_item, service_item, additional_fields):
    assert mongo_item['name'] == service_item['fields']['name']
    assert mongo_item['address'] == service_item['fields']['address']
    assert (
        mongo_item['registration_number']
        == service_item['fields']['registration_number']
    )
    for count, alias in enumerate(additional_fields):
        field = service_item['fields']['additional_fields'][count]
        assert alias == field['alias']
        assert mongo_item[alias] == field['value']


def _build_headers(park_id):
    return {
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
        'Accept-Language': 'ru',
    }


@pytest.mark.parametrize(
    ('park_id', 'limit', 'cursor', 'filter_param', 'mongo_params'),
    [
        (PARK_ID, 2, None, None, {'park_id': PARK_ID}),
        (
            PARK_ID,
            1,
            'eyJyZWdpc3RyYXRpb25fbnVtYmVyIjoiMTExMTEzNDIzIiw'
            'ibmFtZSI6ItCg0L7Qs9CwINC4INCa0L7Qv9GL0YLQsCJ9',
            None,
            {
                'park_id': PARK_ID,
                'name': {'$gte': 'Рога и Копыта'},
                'registration_number': {'$gte': '111113423'},
            },
        ),
        (
            PARK_ID,
            5,
            None,
            'Га',
            {
                'park_id': PARK_ID,
                '$or': [
                    {'name': {'$regex': 'Га', '$options': 'i'}},
                    {'registration_number': {'$regex': 'Га', '$options': 'i'}},
                ],
            },
        ),
        (
            PARK_ID,
            5,
            None,
            '34',
            {
                'park_id': PARK_ID,
                '$or': [
                    {'name': {'$regex': '34', '$options': 'i'}},
                    {'registration_number': {'$regex': '34', '$options': 'i'}},
                ],
            },
        ),
    ],
)
@pytest.mark.config(FLEET_LEGAL_ENTITIES_FIELDS_BY_COUNTRY=COUNTRIES)
async def test_post_list_carriers(
        mongodb,
        taxi_fleet_legal_entities,
        mock_fleet_parks_list,
        park_id,
        limit,
        cursor,
        filter_param,
        mongo_params,
):
    response = await taxi_fleet_legal_entities.post(
        ENDPOINT,
        headers=_build_headers(PARK_ID),
        json={'limit': limit, 'cursor': cursor, 'filter': filter_param},
    )

    mongo_response = list(
        mongodb.dbparks_legal_entities.find(
            mongo_params, RUS_PROJECTION, limit=limit,
        ).sort(
            [
                ('name', pymongo.ASCENDING),
                ('registration_number', pymongo.ASCENDING),
            ],
        ),
    )

    assert response.status_code == 200
    assert len(mongo_response) == len(response.json()['carriers'])
    for mongo_item, service_item in itertools.zip_longest(
            mongo_response, response.json()['carriers'], fillvalue=' ',
    ):
        _check_equal(mongo_item, service_item, COUNTRIES['rus']['field_ids'])


async def test_park_not_found(
        mongodb, taxi_fleet_legal_entities, mock_fleet_parks_list,
):
    response = await taxi_fleet_legal_entities.post(
        ENDPOINT, headers=_build_headers(PARK_ID_NOT_FOUND), json={},
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'park_not_found',
        'message': 'Park not found',
    }


async def test_country_not_found(
        mongodb, taxi_fleet_legal_entities, mock_fleet_parks_list,
):
    response = await taxi_fleet_legal_entities.post(
        ENDPOINT, headers=_build_headers(PARK_ID_COUNTRY_NOT_FOUND), json={},
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'country_not_supported',
        'message': 'Country not supported',
    }
