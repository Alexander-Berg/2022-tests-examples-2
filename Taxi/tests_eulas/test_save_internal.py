import datetime

import pytest
import pytz

URL = 'eulas/v1/save'

YANDEX_UID = 0
EULA_TYPE = 1
STATUS = 2
VALID_TILL = 3
UPDATED_AT = 4


def sort_key(tup):
    return (tup[YANDEX_UID], tup[EULA_TYPE])


def to_utc(stamp):
    if stamp.tzinfo is not None:
        stamp = stamp.astimezone(pytz.utc).replace(tzinfo=None)
    return stamp


async def test_get_not_allowed(taxi_eulas):
    json = {'type': 'gdpr', 'status': 'accepted', 'yandex_uid': '1234'}

    response = await taxi_eulas.get(URL, json=json)
    assert response.status_code == 405, response.text


@pytest.mark.config(EULAS_SERVICE_ENABLED=False)
async def test_service_disabled(taxi_eulas):
    json = {'type': 'gdpr', 'status': 'accepted', 'yandex_uid': '1234'}
    response = await taxi_eulas.post(URL, json=json)
    assert response.status_code == 403, response.text
    assert response.json() == {'code': '403', 'message': 'Eulas: forbidden'}


@pytest.mark.config(EULAS={})
async def test_eula_not_found(taxi_eulas):
    """
    No saved eula in config EULAS
    """
    eula_type = 'some_eula'
    json = {'type': eula_type, 'status': 'accepted', 'yandex_uid': '1234'}

    response = await taxi_eulas.post(URL, json=json)
    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': '404',
        'message': 'Eula not found: {}'.format(eula_type),
    }


@pytest.mark.now('2018-1-01T00:00:00Z')
async def test_simple(taxi_eulas, pgsql, now):
    yandex_uid = '1234'
    type_ = 'gdpr'

    def get_signed_at():
        cursor = pgsql['eulas'].cursor()
        cursor.execute('SELECT * FROM eulas.users')
        result = list((row[UPDATED_AT]) for row in cursor)
        cursor.close()
        return result

    def get_expected_till(days):
        # TODO try fix formula (here hack, offset moscow 3 hours)
        return (
            now + datetime.timedelta(days=days) - datetime.timedelta(hours=3)
        )

    def get_users():
        cursor = pgsql['eulas'].cursor()
        cursor.execute('SELECT * FROM eulas.users')
        result = list(
            (
                row[YANDEX_UID],
                row[EULA_TYPE],
                row[STATUS],
                to_utc(row[VALID_TILL]),
            )
            for row in cursor
        )
        cursor.close()
        return result

    # init
    assert get_users() == []

    # create
    response = await taxi_eulas.post(
        URL,
        json={'type': type_, 'status': 'accepted', 'yandex_uid': yandex_uid},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == {}

    # check db
    curr_db = get_users()
    curr_db.sort(key=sort_key)
    expected_db = [(yandex_uid, type_, 'accepted', get_expected_till(365))]
    expected_db.sort(key=sort_key)
    assert curr_db == expected_db

    date_db_create = get_signed_at()

    # update record
    response = await taxi_eulas.post(
        URL,
        json={'type': type_, 'status': 'rejected', 'yandex_uid': yandex_uid},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == {}

    # check db
    curr_db = get_users()
    curr_db.sort(key=sort_key)
    expected_db = [(yandex_uid, type_, 'rejected', get_expected_till(180))]
    expected_db.sort(key=sort_key)
    assert curr_db == expected_db

    date_db_update = get_signed_at()

    # update field has changed
    assert date_db_create[0] < date_db_update[0]


@pytest.mark.parametrize(
    'request_body, expected_code, expected_response',
    [
        (
            {'type': 'gdpr', 'status': 'accepted', 'yandex_uid': '1234'},
            200,
            {},
        ),
        (  # empty yandex_uid
            {'type': 'gdpr', 'status': 'accepted', 'yandex_uid': ''},
            400,
            {
                'code': '400',
                'message': (
                    'Value of \'yandex_uid\': incorrect size, must be '
                    '1 (limit) <= 0 (value)'
                ),
            },
        ),
        (  # no yandex_uid
            {'type': 'gdpr', 'status': 'accepted'},
            400,
            {'code': '400', 'message': 'Field \'yandex_uid\' is missing'},
        ),
        (  # empty type
            {'type': '', 'status': 'accepted', 'yandex_uid': '1234'},
            400,
            {
                'code': '400',
                'message': (
                    'Value of \'type\': incorrect size, must be '
                    '1 (limit) <= 0 (value)'
                ),
            },
        ),
        (  # no type
            {'status': 'accepted', 'yandex_uid': '1234'},
            400,
            {'code': '400', 'message': 'Field \'type\' is missing'},
        ),
        (  # empty status
            {'type': 'gdpr', 'status': '', 'yandex_uid': '1234'},
            400,
            {
                'code': '400',
                'message': 'Value of \'status\' () is not parseable into enum',
            },
        ),
        (  # no status
            {'type': 'gdpr', 'yandex_uid': '1234'},
            400,
            {'code': '400', 'message': 'Field \'status\' is missing'},
        ),
    ],
)
async def test_request(
        taxi_eulas, request_body, expected_code, expected_response,
):
    response = await taxi_eulas.post(URL, json=request_body)

    assert response.status_code == expected_code, response.text

    data = response.json()
    if expected_code == 400:
        assert data['code'] == '400'
    else:
        assert data == expected_response
