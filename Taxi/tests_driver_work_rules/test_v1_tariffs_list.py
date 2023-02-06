import json

import pytest

from tests_driver_work_rules import defaults


ENDPOINT = '/v1/tariffs/list'
FLEET_ENDPOINT = '/fleet/dwr/v1/tariffs/list'

HEADERS = {
    'X-Ya-Service-Ticket': defaults.X_YA_SERVICE_TICKET,
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
}


@pytest.mark.parametrize(
    'request_body', [({}), ({'query': {'park': {'id': ''}}},)],
)
async def test_bad_request(taxi_driver_work_rules, request_body):
    response = await taxi_driver_work_rules.post(
        ENDPOINT, headers=HEADERS, json=request_body,
    )

    assert response.status_code == 400
    assert response.json()['code'] == '400'


@pytest.mark.redis_store(
    [
        'hmset',
        'Tariffs:Tariff:my_park_id',
        {
            'tariff_id_1': json.dumps(
                {
                    'Name': 'ЭкоУфа',
                    'UniqId': 'Свои/ЭкоУфа',
                    'FolderId': '123a',
                    'Category': 1,
                    'WorkType': 'Всегда',
                    'WorkTypeParsed': 1,
                    'Days': [],
                    'MinimumAmount': 200.0,
                    'LimitTime': 10.0,
                    'WaitingFree': 10.0,
                    'WaitingPay': 5.0,
                },
            ),
            'tariff_id_2': json.dumps(
                {
                    'Name': 'abc',
                    'UniqId': '/abc',
                    'FolderId': '123b',
                    'Category': 2,
                },
            ),
            'tariff_id_3': json.dumps(
                {
                    'Name': 'qwe',
                    'UniqId': 'qwe/qwe',
                    'FolderId': 'qwe1',
                    'Category': 2,
                },
            ),
            'tariff_id_4': json.dumps(
                {
                    'Name': '',  # empty required field
                    'UniqId': 'Свои/ЭкоУфа',
                    'FolderId': '123a',
                    'Category': 1,
                    'WorkType': 'Всегда',
                    'WorkTypeParsed': 1,
                    'Days': [],
                    'MinimumAmount': 200.0,
                    'LimitTime': 10.0,
                    'WaitingFree': 10.0,
                    'WaitingPay': 5.0,
                },
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            {'query': {'park': {'id': 'my_park_id'}}},
            {
                'tariffs': [
                    {
                        'name': 'abc',
                        'id': 'tariff_id_2',
                        'folder_name': '',
                        'folder_id': '123b',
                    },
                    {
                        'name': 'qwe',
                        'id': 'tariff_id_3',
                        'folder_name': 'qwe',
                        'folder_id': 'qwe1',
                    },
                    {
                        'name': 'ЭкоУфа',
                        'id': 'tariff_id_1',
                        'folder_name': 'Свои',
                        'folder_id': '123a',
                    },
                ],
            },
        ),
    ],
)
async def tests_ok(taxi_driver_work_rules, request_body, expected_response):
    response = await taxi_driver_work_rules.post(
        ENDPOINT, headers=HEADERS, json=request_body,
    )

    assert response.json() == expected_response


@pytest.mark.redis_store(
    [
        'hmset',
        'Tariffs:Tariff:my_park_id',
        {
            'tariff_id_1': json.dumps(
                {
                    'Name': 'ЭкоУфа',
                    'UniqId': 'Свои/ЭкоУфа',
                    'FolderId': '123a',
                    'Category': 1,
                    'WorkType': 'Всегда',
                    'WorkTypeParsed': 1,
                    'Days': [],
                    'MinimumAmount': 200.0,
                    'LimitTime': 10.0,
                    'WaitingFree': 10.0,
                    'WaitingPay': 5.0,
                },
            ),
            'tariff_id_2': json.dumps(
                {
                    'Name': 'abc',
                    'UniqId': '/abc',
                    'FolderId': '123b',
                    'Category': 2,
                },
            ),
            'tariff_id_3': json.dumps(
                {
                    'Name': 'qwe',
                    'UniqId': 'qwe/qwe',
                    'FolderId': 'qwe1',
                    'Category': 2,
                },
            ),
            'tariff_id_4': json.dumps(
                {
                    'Name': '',  # empty required field
                    'UniqId': 'Свои/ЭкоУфа',
                    'FolderId': '123a',
                    'Category': 1,
                    'WorkType': 'Всегда',
                    'WorkTypeParsed': 1,
                    'Days': [],
                    'MinimumAmount': 200.0,
                    'LimitTime': 10.0,
                    'WaitingFree': 10.0,
                    'WaitingPay': 5.0,
                },
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'park_id, expected_response',
    [
        (
            'my_park_id',
            {
                'tariffs': [
                    {
                        'name': 'abc',
                        'id': 'tariff_id_2',
                        'folder_name': '',
                        'folder_id': '123b',
                    },
                    {
                        'name': 'qwe',
                        'id': 'tariff_id_3',
                        'folder_name': 'qwe',
                        'folder_id': 'qwe1',
                    },
                    {
                        'name': 'ЭкоУфа',
                        'id': 'tariff_id_1',
                        'folder_name': 'Свои',
                        'folder_id': '123a',
                    },
                ],
            },
        ),
    ],
)
async def test_fleet_dwr_ok(
        taxi_driver_work_rules, park_id, expected_response,
):
    headers = HEADERS
    headers['X-Park-ID'] = park_id

    response = await taxi_driver_work_rules.get(
        FLEET_ENDPOINT, headers=headers,
    )

    assert response.json() == expected_response
