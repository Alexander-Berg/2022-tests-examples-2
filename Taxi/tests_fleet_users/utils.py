import dateutil.parser


def pg_response_to_dict(cursor):
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]
    return res


def get_user_by_phone_id(pgsql, park_id, phone_id, is_user_expected=True):
    cursor = pgsql['fleet_users'].cursor()
    cursor.execute(
        f"""
        SELECT user_id, park_id, group_id, user_name,
        user_phone_id, created_at, is_confirmed, confirmed_at,
        is_multifactor_authentication_required, is_enabled
        FROM fleet_users.users
        WHERE park_id='{park_id}' AND user_phone_id='{phone_id}'
        """,
    )
    result = pg_response_to_dict(cursor)
    if is_user_expected:
        assert len(result) == 1
        return result[0]
    assert not result
    return None


def get_user_by_passport_uid(pgsql, park_id, passport_uid):
    cursor = pgsql['fleet_users'].cursor()
    cursor.execute(
        f"""
        SELECT user_id, park_id, group_id, user_name,
        user_phone_id, created_at, is_confirmed, confirmed_at,
        is_multifactor_authentication_required, is_enabled
        FROM fleet_users.users
        WHERE park_id='{park_id}' AND passport_uid='{passport_uid}'
        """,
    )
    result = pg_response_to_dict(cursor)
    assert len(result) == 1
    return result[0]


def get_user_by_id(pgsql, park_id, user_id):
    cursor = pgsql['fleet_users'].cursor()
    cursor.execute(
        f"""
        SELECT user_id, park_id, group_id, user_name,
        user_phone_id, created_at, is_confirmed, confirmed_at,
        is_multifactor_authentication_required, is_enabled
        FROM fleet_users.users
        WHERE park_id='{park_id}' AND user_id='{user_id}'
        """,
    )
    result = pg_response_to_dict(cursor)
    assert len(result) == 1
    return result[0]


def get_users_count(pgsql):
    cursor = pgsql['fleet_users'].cursor()
    cursor.execute(
        """
        SELECT count(*)
        FROM fleet_users.users
        """,
    )
    return cursor.fetchone()[0]


def check_created_user(
        pgsql, request, park_id, is_multifactor_authentication_require=False,
):
    created_user = get_user_by_phone_id(pgsql, park_id, 'phone_id1')

    assert created_user['user_id']
    assert created_user['park_id'] == park_id
    assert created_user['group_id'] == request['group_id']
    assert created_user['user_name'] == request['name']
    assert created_user['user_phone_id'] == 'phone_id1'
    assert created_user['created_at'] == dateutil.parser.parse(
        '2019-01-01T01:00:00Z',
    )
    assert not created_user['is_confirmed']
    assert not created_user['confirmed_at']
    assert created_user['is_enabled']
    assert (
        created_user['is_multifactor_authentication_required']
        == is_multifactor_authentication_require
    )
