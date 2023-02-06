import http
import os

import psycopg2.extras
import pytest


AUTHOR = 'username'
MESSAGE = 'message 💸\n\nnew line'
RESPONSE = {
    'errors': [
        'following places not found or disabled: '
        '[\'999999\', \'not_found_place_id\']',
    ],
}
EXPECTED_IDS = {1, 2, 3, 4}


@pytest.fixture(name='load_src_file')
def _load_src_file():
    def _load(file_name):
        test_path = os.path.abspath(__file__)
        test_name = os.path.splitext(os.path.basename(test_path))[0]
        tests_dir = os.path.dirname(test_path)
        static_dir = os.path.join(tests_dir, 'static', test_name)
        file_path = os.path.join(static_dir, file_name)
        with open(file_path, 'rb') as stream:
            return stream.read()

    return _load


@pytest.mark.parametrize(
    ('src_file', 'expected_code', 'expected_response'),
    (
        pytest.param('push.csv', http.HTTPStatus.OK, RESPONSE, id='OK-csv'),
        pytest.param('push.xlsx', http.HTTPStatus.OK, RESPONSE, id='OK-xlsx'),
        pytest.param('push.xls', http.HTTPStatus.OK, RESPONSE, id='OK-xls'),
        pytest.param(
            'push.txt',
            http.HTTPStatus.BAD_REQUEST,
            {
                'message': (
                    'bad format for message 1, place_id=custom not csv text'
                ),
                'code': 'bad_request',
            },
            id='not-csv',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql'],
)
async def test_admin_messages_excel_send(
        taxi_eats_integration_offline_orders_web,
        pgsql,
        load_src_file,
        src_file,
        expected_code,
        expected_response,
):
    data = load_src_file(src_file)
    response = await taxi_eats_integration_offline_orders_web.post(
        '/admin/v1/messages/excel',
        data=data,
        headers={'X-Yandex-Login': AUTHOR},
    )
    assert response.status == expected_code
    body = await response.json()
    assert body == expected_response
    if expected_response is not http.HTTPStatus.OK:
        return
    cursor = pgsql['eats_integration_offline_orders'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute(
        """
SELECT *
FROM telegram_messages;
        """,
    )
    rows = cursor.fetchall()
    ids = {row['restaurant_id'] for row in rows}
    assert ids == EXPECTED_IDS
    for row in rows:
        assert row['message'] == MESSAGE
        assert row['author'] == AUTHOR
