import pytest

from taxi.util import dates

from taxi_antifraud.admin.blacklist import names


async def add(web_app_client, data):
    return await web_app_client.post(
        '/v1/blacklist/add',
        json={
            'licenses': data['licenses'],
            'start_date': data['start_date'],
            'end_date': data['end_date'],
        },
    )


async def remove(web_app_client, data):
    return await web_app_client.post(
        '/v1/blacklist/remove_license', json={'license': data['license']},
    )


async def check_mongo(db, expected: dict):
    entity_map = await db.antifraud_entity_map.find_one(
        {'name': names.BLACKLIST_ENTITY_NAME},
    )

    assert expected == entity_map[names.VALUE_FIELD][names.LICENSES_FIELD]


async def check_default(db, web_app_client, test):
    for request in test['prefill']:
        response = await add(web_app_client, request)
        assert response.status == 200

    for request in test['requests']:
        response = await remove(web_app_client, request)
        assert response.status == 200

    await check_mongo(db, expected=test['response'])


def time(date: str):
    return dates.parse_timestring(date, timezone='UTC')


@pytest.mark.parametrize(
    'test',
    [
        {
            'prefill': [
                {
                    'licenses': ['license_1', 'license_2'],
                    'start_date': '2019-02-05T12:20:00.0+03:00',
                    'end_date': '2019-02-05T19:20:00.0+03:00',
                },
                {
                    'licenses': ['license_1', 'license_2'],
                    'start_date': '2019-03-05T12:20:00.0+03:00',
                    'end_date': '2019-03-05T19:20:00.0+03:00',
                },
            ],
            'requests': [{'license': 'license_1'}],
            'response': {
                'license_2': {
                    'dates': [
                        {
                            'start_date': time('2019-02-05T12:20:00+03:00'),
                            'end_date': time('2019-02-05T19:20:00+03:00'),
                        },
                        {
                            'start_date': time('2019-03-05T12:20:00+03:00'),
                            'end_date': time('2019-03-05T19:20:00+03:00'),
                        },
                    ],
                    'last_end_date': time('2019-03-05T19:20:00+03:00'),
                },
            },
        },
    ],
)
async def test_remove(db, web_app_client, test):
    await check_default(db, web_app_client, test)
