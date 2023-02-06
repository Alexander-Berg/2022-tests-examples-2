import datetime

import pytest
import pytz


TEST_PERSONAL_PHONE_ID = '123'
TEST_UPDATED = datetime.datetime(
    2022, 6, 22, 0, 28, 36, 123000, tzinfo=pytz.utc,
)
TEST_UPDATED_ISO = TEST_UPDATED.strftime('%Y-%m-%dT%H:%M:%SZ')


@pytest.mark.nofilldb
async def test_telesign_proxy_retrieve(taxi_uantifraud, mongodb):
    def check_post():
        return taxi_uantifraud.post(
            'v1/telesign/proxy_retrieve?consumer=rtxaron',
            {
                'id_in_set': [TEST_PERSONAL_PHONE_ID, '456'],
                'projection': [
                    'data.risk_recommendation',
                    'data.risk_score',
                    'data.updated',
                ],
            },
        )

    mongodb.antifraud_telesign_phone_scoring.insert_one(
        {
            'personal_phone_id': TEST_PERSONAL_PHONE_ID,
            'risk_recommendation': 'block',
            'risk_score': 209,
            'updated': TEST_UPDATED,
        },
    )

    response = await check_post()
    assert response.json() == {
        'phones': [
            {
                'personal_phone_id': TEST_PERSONAL_PHONE_ID,
                'data': {
                    'risk_recommendation': 'block',
                    'risk_score': 209,
                    'updated': TEST_UPDATED_ISO,
                },
            },
            {'personal_phone_id': '456'},
        ],
    }
