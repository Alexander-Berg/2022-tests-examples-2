import pytest

URL = '/communications-audience/v1/unpublish'


@pytest.mark.ydb(files=['fill_for_unpublish.sql'])
async def test_unpublish(
        taxi_communications_audience, ydb, mock_promotions_unpublish,
):
    mock_promotions_unpublish()

    json_body = {
        'campaign_label': 'test_campaign',
        'communication_id': 'test_id',
        'users': [
            {'id_type': 'yandex_uid', 'id': 'test_uid_1'},
            {'id_type': 'yandex_uid', 'id': 'test_uid_2'},
            {'id_type': 'yandex_uid', 'id': 'unknown_id'},
            {'id_type': 'phone_id', 'id': 'test_phone_id_1'},
            {'id_type': 'phone_id', 'id': 'test_phone_id_3'},
            {'id_type': 'personal_phone_id', 'id': 'test_personal_phone_id_1'},
            {'id_type': 'personal_phone_id', 'id': 'test_personal_phone_id_2'},
            {'id_type': 'device_id', 'id': 'test_device_id_2'},
            {'id_type': 'device_id', 'id': 'test_device_id_3'},
        ],
    }
    response = await taxi_communications_audience.post(URL, json=json_body)
    assert response.status_code == 200

    cursor = ydb.execute(
        'SELECT * FROM audience_by_yandex_uid ORDER by yandex_uid,campaign_id',
    )
    assert len(cursor) == 1
    assert len(cursor[0].rows) == 1

    assert cursor[0].rows[0]['yandex_uid'] == b'test_uid_3'
    assert cursor[0].rows[0]['campaign_id'] == b'test_campaign_4'

    cursor1 = ydb.execute(
        'SELECT * FROM audience_by_phone_id ORDER by phone_id, campaign_id',
    )

    assert len(cursor1) == 1
    assert len(cursor1[0].rows) == 2

    assert cursor1[0].rows[0]['phone_id'] == b'test_phone_id_1'
    assert cursor1[0].rows[0]['campaign_id'] == b'test_campaign_1'
    assert cursor1[0].rows[1]['phone_id'] == b'test_phone_id_2'
    assert cursor1[0].rows[1]['campaign_id'] == b'test_campaign_2'

    cursor2 = ydb.execute('SELECT * FROM audience_by_personal_phone_id')
    assert len(cursor2) == 1
    assert len(cursor2[0].rows) == 1

    assert cursor2[0].rows[0]['personal_phone_id'] == b'test_personal_phone_id'
    assert cursor2[0].rows[0]['campaign_id'] == b'test_campaign_1'

    cursor3 = ydb.execute('SELECT * FROM audience_by_device_id')
    assert len(cursor3) == 1
    assert len(cursor3[0].rows) == 1

    assert cursor3[0].rows[0]['device_id'] == b'test_device_id_1'
    assert cursor3[0].rows[0]['campaign_id'] == b'test_campaign_1'


@pytest.mark.ydb(files=['fill_for_unpublish.sql'])
async def test_unpublish_by_campaign_label_only(
        taxi_communications_audience, ydb, mock_promotions_unpublish,
):
    mock_promotions_unpublish()

    json_body = {
        'campaign_label': 'test_campaign',
        'communication_id': 'test_id',
    }
    response = await taxi_communications_audience.post(URL, json=json_body)
    assert response.status_code == 200

    cursor = ydb.execute('SELECT * FROM audience_by_yandex_uid')
    assert len(cursor) == 1
    assert len(cursor[0].rows) == 1

    cursor1 = ydb.execute('SELECT * FROM audience_by_phone_id')
    assert len(cursor1) == 1
    assert len(cursor1[0].rows) == 2

    cursor2 = ydb.execute('SELECT * FROM audience_by_personal_phone_id')
    assert len(cursor2) == 1
    assert len(cursor2[0].rows) == 1

    cursor3 = ydb.execute('SELECT * FROM audience_by_device_id')
    assert len(cursor3) == 1
    assert len(cursor3[0].rows) == 1


@pytest.mark.ydb(files=['fill_for_unpublish.sql'])
@pytest.mark.parametrize(
    'promotions_error_code, response_code',
    [pytest.param(400, 500), pytest.param(409, 200), pytest.param(502, 500)],
)
async def test_unpublish_promotions_errors(
        taxi_communications_audience,
        mock_promotions_unpublish,
        promotions_error_code,
        response_code,
):
    mock_promotions_unpublish(status_code=promotions_error_code)

    json_body = {
        'campaign_label': 'test_campaign',
        'communication_id': 'test_id',
    }
    response = await taxi_communications_audience.post(URL, json=json_body)
    assert response.status_code == response_code
