import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = 'internal-admin/signal-device-api-admin/v1/filters'


@pytest.mark.parametrize(
    'filter_id, expected_db_ids, expected_code, expected_response',
    [
        ('id-1', ['id-2', 'id-3'], 200, None),
        (
            'id-3',
            ['id-1', 'id-2', 'id-3'],
            404,
            {
                'code': 'No_filter',
                'message': 'No filter with id = id-3 for that user',
            },
        ),
    ],
)
@pytest.mark.pgsql('signal_device_api_meta_db', files=['test_data.sql'])
async def test_ok(
        taxi_signal_device_api_admin,
        pgsql,
        filter_id,
        expected_db_ids,
        expected_code,
        expected_response,
):
    response = await taxi_signal_device_api_admin.delete(
        ENDPOINT,
        headers={**web_common.PARTNER_HEADERS_1},
        params={'id': filter_id},
    )
    assert response.status_code == expected_code, response.text
    if expected_response:
        assert response.json() == expected_response

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute('select id from signal_device_api.internal_filters')
    db_ids = []
    for row in list(db):
        db_ids.append(row[0])
    assert db_ids == expected_db_ids
