import copy

import pytest

HEADERS = {'X-Idempotency-Token': '123456'}

TEST_UID_1 = 'test_uid_1'
BTEST_UID_1 = b'test_uid_1'
TEST_UID_2 = 'test_uid_2'
BTEST_UID_2 = b'test_uid_2'
TEST_UID_3 = 'test_uid_3'
BTEST_UID_3 = b'test_uid_3'
TEST_UID_4 = 'test_uid_4'
BTEST_UID_4 = b'test_uid_4'

TEST_PHONE_ID_1 = 'test_phone_id_1'
BTEST_PHONE_ID_1 = b'test_phone_id_1'
TEST_PHONE_ID_2 = 'test_phone_id_2'
BTEST_PHONE_ID_2 = b'test_phone_id_2'
TEST_PHONE_ID_3 = 'test_phone_id_3'
BTEST_PHONE_ID_3 = b'test_phone_id_3'
TEST_PHONE_ID_4 = 'test_phone_id_4'
BTEST_PHONE_ID_4 = b'test_phone_id_4'
TEST_PHONE_ID_5 = 'test_phone_id_5'
TEST_PHONE_ID_6 = 'test_phone_id_6'

TEST_PERSONAL_PHONE_ID_1 = 'test_personal_phone_id_1'
TEST_PERSONAL_PHONE_ID_2 = 'test_personal_phone_id_2'
TEST_PERSONAL_PHONE_ID_3 = 'test_personal_phone_id_3'
TEST_PERSONAL_PHONE_ID_4 = 'test_personal_phone_id_4'

TEST_DEVICE_ID_1 = 'test_device_id_1'
TEST_DEVICE_ID_2 = 'test_device_id_2'
TEST_DEVICE_ID_3 = 'test_device_id_3'
TEST_DEVICE_ID_4 = 'test_device_id_4'

TEST_CAMPAIGN = 'test_campaign'
BTEST_CAMPAIGN = b'test_campaign'
TEST_CAMPAIGN_1 = 'test_campaign_1'
BTEST_CAMPAIGN_1 = b'test_campaign_1'
TEST_CAMPAIGN_2 = 'test_campaign_2'
BTEST_CAMPAIGN_2 = b'test_campaign_2'
TEST_CAMPAIGN_3 = 'test_campaign_3'
BTEST_CAMPAIGN_3 = b'test_campaign_3'
TEST_CAMPAIGN_4 = 'test_campaign_4'
BTEST_CAMPAIGN_4 = b'test_campaign_4'

JSON_BODY = {
    'campaign_label': TEST_CAMPAIGN,
    'personal_communications': [
        {
            'users': [
                {'id_type': 'yandex_uid', 'id': TEST_UID_1},
                {'id_type': 'yandex_uid', 'id': TEST_UID_1},
                {'id_type': 'yandex_uid', 'id': TEST_UID_2},
                {'id_type': 'phone_id', 'id': TEST_PHONE_ID_3},
                {'id_type': 'phone_id', 'id': TEST_PHONE_ID_1},
                {
                    'id_type': 'personal_phone_id',
                    'id': TEST_PERSONAL_PHONE_ID_2,
                },
                {
                    'id_type': 'personal_phone_id',
                    'id': TEST_PERSONAL_PHONE_ID_3,
                },
                {'id_type': 'device_id', 'id': TEST_DEVICE_ID_3},
                {'id_type': 'device_id', 'id': TEST_DEVICE_ID_1},
            ],
            'communication_id': 'test_id',
            'start_date': '2022-01-01T00:00:00+00:00',
            'end_date': '2023-01-01T00:00:00+00:00',
        },
    ],
}


@pytest.mark.ydb(files=['fill_for_publish.sql'])
async def test_publish_promotions_error(
        taxi_communications_audience, ydb, mock_promotions,
):
    mock_promotions(400)

    response = await taxi_communications_audience.post(
        'communications-audience/v1/publish', json=JSON_BODY, headers=HEADERS,
    )
    assert response.status_code == 200

    assert response.json() == {
        'audience_info': [
            {
                'communication_id': 'test_id',
                'error_message': (
                    'Could not publish for communication_id : test_id.'
                ),
                'markup_status': 'success',
                'publishing_status': 'error',
            },
        ],
    }

    cursor = ydb.execute(
        'SELECT * FROM audience_by_yandex_uid ORDER by yandex_uid,campaign_id',
    )
    assert len(cursor) == 1
    assert len(cursor[0].rows) == 3

    assert cursor[0].rows[0]['yandex_uid'] == BTEST_UID_1
    assert cursor[0].rows[0]['campaign_id'] == BTEST_CAMPAIGN
    assert cursor[0].rows[1]['yandex_uid'] == BTEST_UID_2
    assert cursor[0].rows[1]['campaign_id'] == BTEST_CAMPAIGN
    assert cursor[0].rows[2]['yandex_uid'] == BTEST_UID_3
    assert cursor[0].rows[2]['campaign_id'] == BTEST_CAMPAIGN_4

    cursor1 = ydb.execute(
        'SELECT * FROM audience_by_phone_id ORDER by phone_id, campaign_id',
    )

    assert len(cursor1) == 1
    assert len(cursor1[0].rows) == 5

    assert cursor1[0].rows[0]['phone_id'] == BTEST_PHONE_ID_1
    assert cursor1[0].rows[0]['campaign_id'] == BTEST_CAMPAIGN
    assert cursor1[0].rows[1]['phone_id'] == BTEST_PHONE_ID_1
    assert cursor1[0].rows[1]['campaign_id'] == BTEST_CAMPAIGN_1
    assert cursor1[0].rows[2]['phone_id'] == BTEST_PHONE_ID_1
    assert cursor1[0].rows[2]['campaign_id'] == BTEST_CAMPAIGN_2
    assert cursor1[0].rows[3]['phone_id'] == BTEST_PHONE_ID_2
    assert cursor1[0].rows[3]['campaign_id'] == BTEST_CAMPAIGN_2
    assert cursor1[0].rows[4]['phone_id'] == BTEST_PHONE_ID_3
    assert cursor1[0].rows[4]['campaign_id'] == BTEST_CAMPAIGN

    cursor2 = ydb.execute('SELECT * FROM audience_by_personal_phone_id')
    assert len(cursor2) == 1
    assert len(cursor2[0].rows) == 5

    cursor3 = ydb.execute('SELECT * FROM audience_by_device_id')
    assert len(cursor3) == 1
    assert len(cursor3[0].rows) == 4


@pytest.mark.ydb(files=['fill_for_publish.sql'])
async def test_publish_promotions_success(
        taxi_communications_audience, ydb, mock_promotions,
):
    mock_promotions(200)

    response = await taxi_communications_audience.post(
        'communications-audience/v1/publish', json=JSON_BODY, headers=HEADERS,
    )
    assert response.status_code == 200

    assert response.json() == {
        'audience_info': [
            {
                'communication_id': 'test_id',
                'markup_status': 'success',
                'publishing_status': 'success',
            },
        ],
    }


@pytest.mark.parametrize(
    'users,user_api_answer',
    [
        pytest.param(
            [
                {'id_type': 'phone_id', 'id': TEST_PHONE_ID_3},
                {'id_type': 'phone_id', 'id': TEST_PHONE_ID_1},
            ],
            False,
            id='allowed_for_users_from_config',
        ),
        pytest.param(
            [
                {'id_type': 'phone_id', 'id': TEST_PHONE_ID_2},
                {'id_type': 'phone_id', 'id': TEST_PHONE_ID_4},
                {'id_type': 'phone_id', 'id': TEST_PHONE_ID_5},
            ],
            True,
            id='allowed_for_staff_users',
        ),
    ],
)
@pytest.mark.ydb(files=['fill_for_publish.sql'])
@pytest.mark.config(
    COMMUNICATIONS_AUDIENCE_TEST_CAMPAIGN_PHONES_ALLOWED=[
        TEST_PHONE_ID_1,
        TEST_PHONE_ID_3,
    ],
)
async def test_publish_test_campaign_success(
        taxi_communications_audience,
        ydb,
        mock_promotions,
        mock_userapi,
        users,
        user_api_answer,
):
    mock_promotions(200)
    mock_userapi(user_api_answer)
    request_json = {
        'campaign_label': TEST_CAMPAIGN,
        'is_test_publication': True,
        'personal_communications': [
            {
                'users': users,
                'communication_id': 'test_id',
                'start_date': '2022-01-01T00:00:00+00:00',
                'end_date': '2023-01-01T00:00:00+00:00',
            },
        ],
    }
    response = await taxi_communications_audience.post(
        'communications-audience/v1/publish',
        json=request_json,
        headers=HEADERS,
    )
    assert response.status_code == 200

    assert response.json() == {
        'audience_info': [
            {
                'communication_id': 'test_id',
                'markup_status': 'success',
                'publishing_status': 'success',
            },
        ],
    }


@pytest.mark.parametrize(
    'users,user_api_answer,expected_message',
    [
        pytest.param(
            [
                {'id_type': 'yandex_uid', 'id': TEST_UID_1},
                {'id_type': 'phone_id', 'id': TEST_PHONE_ID_3},
                {'id_type': 'phone_id', 'id': TEST_PHONE_ID_1},
                {'id_type': 'device_id', 'id': TEST_DEVICE_ID_1},
            ],
            True,
            'Can\'t check users with device_id and '
            'personal_phone_id and yandex_uid type for test',
            id='forbidden_id_types',
        ),
        pytest.param(
            [
                {'id_type': 'phone_id', 'id': TEST_PHONE_ID_1},
                {'id_type': 'phone_id', 'id': TEST_PHONE_ID_2},
                {'id_type': 'phone_id', 'id': TEST_PHONE_ID_3},
                {'id_type': 'phone_id', 'id': TEST_PHONE_ID_4},
                {'id_type': 'phone_id', 'id': TEST_PHONE_ID_5},
                {'id_type': 'phone_id', 'id': TEST_PHONE_ID_6},
            ],
            True,
            'Too big audience for test, max size is 5',
            id='too_big_audience',
        ),
        pytest.param(
            [
                {'id_type': 'phone_id', 'id': TEST_PHONE_ID_1},
                {'id_type': 'phone_id', 'id': TEST_PHONE_ID_2},
            ],
            False,
            'Found not staff user test_phone_id_1, test label is blocked',
            id='not_staff_user',
        ),
    ],
)
@pytest.mark.ydb(files=['fill_for_publish.sql'])
async def test_publish_test_campaign_fail(
        taxi_communications_audience,
        ydb,
        mock_promotions,
        mock_userapi,
        users,
        user_api_answer,
        expected_message,
):
    mock_promotions(200)
    mock_userapi(user_api_answer)
    request_json = copy.deepcopy(JSON_BODY)
    request_json['is_test_publication'] = True
    request_json['personal_communications'][0]['users'] = users

    response = await taxi_communications_audience.post(
        'communications-audience/v1/publish',
        json=request_json,
        headers=HEADERS,
    )
    assert response.status_code == 403

    assert response.json() == {'error_message': expected_message}
