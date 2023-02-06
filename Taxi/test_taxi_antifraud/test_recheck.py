from typing import List

import pytest


async def recheck(web_app_client, data):
    return await web_app_client.post(
        '/v1/blacklist/recheck',
        json={
            'licenses': data['licenses'],
            'start_date': data['start_date'],
            'end_date': data['end_date'],
        },
    )


async def check_mongo(db, expected: List[dict]):
    statuses = await db.antifraud_subventions_check_status.find({}).to_list(
        None,
    )

    assert expected == [
        {'proc_status': item['proc_status'], 'billing_id': item['billing_id']}
        for item in statuses
    ]


async def check_default(db, web_app_client, test):
    response = await recheck(web_app_client, test['request'])
    assert response.status == 200

    await check_mongo(db, expected=test['response'])


@pytest.mark.parametrize(
    'test',
    [
        {
            'request': {
                'licenses': ['license_1', 'license_2'],
                'start_date': '2019-02-05T12:20:00.0+03:00',
                'end_date': '2019-02-05T19:20:00.0+03:00',
            },
            'response': [
                {'billing_id': '1', 'proc_status': 'force_check'},
                {'billing_id': '2', 'proc_status': 'pay'},
                {'billing_id': '3', 'proc_status': 'pay'},
                {'billing_id': '4', 'proc_status': 'pay'},
                {'billing_id': '5', 'proc_status': 'pay'},
            ],
        },
        {
            'request': {
                'licenses': ['license_2'],
                'start_date': '2019-02-05T12:20:00.0+03:00',
                'end_date': '2019-02-05T19:20:00.0+03:00',
            },
            'response': [
                {'billing_id': '1', 'proc_status': 'pay'},
                {'billing_id': '2', 'proc_status': 'pay'},
                {'billing_id': '3', 'proc_status': 'pay'},
                {'billing_id': '4', 'proc_status': 'pay'},
                {'billing_id': '5', 'proc_status': 'pay'},
            ],
        },
    ],
)
async def test_recheck(db, web_app_client, test):
    await check_default(db, web_app_client, test)


@pytest.mark.parametrize(
    'test',
    [
        {
            'request': {
                'licenses': None,
                'start_date': '2019-02-05T12:20:00.0+03:00',
                'end_date': '2019-02-05T19:20:00.0+03:00',
            },
            'response': [
                {'billing_id': '1', 'proc_status': 'force_check'},
                {'billing_id': '2', 'proc_status': 'pay'},
                {'billing_id': '3', 'proc_status': 'pay'},
                {'billing_id': '4', 'proc_status': 'pay'},
                {'billing_id': '5', 'proc_status': 'pay'},
            ],
        },
    ],
)
async def test_recheck_all_license(db, web_app_client, test):
    await check_default(db, web_app_client, test)
