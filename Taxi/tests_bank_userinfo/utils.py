class Session:
    def __init__(self):
        self.session_uuid = None
        self.yandex_uid = None
        self.phone_id = None
        self.bank_uid = None
        self.status = None
        self.old_session_uuid = None
        self.created_at = None
        self.updated_at = None
        self.authorization_track_id = None
        self.app_vars = None
        self.locale = None
        self.pin_token_id = None


def select_session(pgsql, session_uuid):
    cursor = pgsql['bank_userinfo'].cursor()
    cursor.execute(
        """
        SELECT id, yandex_uid, phone_id, bank_uid, status,
        old_session_id, created_at, updated_at, authorization_track_id,
        app_vars, locale, pin_token_id
        FROM bank_userinfo.sessions
        WHERE id = %s::UUID
        """,
        [session_uuid],
    )
    sessions = cursor.fetchall()
    assert len(sessions) == 1
    session = sessions[0]

    res = Session()

    res.session_uuid = session[0]
    res.yandex_uid = session[1]
    res.phone_id = session[2]
    res.bank_uid = session[3]
    res.status = session[4]
    res.old_session_uuid = session[5]
    res.created_at = session[6]
    res.updated_at = session[7]
    res.authorization_track_id = session[8]
    res.app_vars = session[9]
    res.locale = session[10]
    res.pin_token_id = session[11]

    return res


def select_buid_sessions(pgsql, bank_uid, deleted=False):
    cursor = pgsql['bank_userinfo'].cursor()
    fields = [
        'id',
        'yandex_uid',
        'bank_uid',
        'old_session_id',
        'created_at',
        'updated_at',
        'phone_id',
        'antifraud_info',
        'authorization_track_id',
        'app_vars',
        'locale',
    ]
    cursor.execute(
        f"""
        SELECT {", ".join(fields)} FROM bank_userinfo.sessions
        WHERE bank_uid = %s
        AND (deleted_at IS NOT NULL) = %s
        order by id
        """,
        [bank_uid, deleted],
    )

    rows = cursor.fetchall()
    return list(map(lambda row: dict(zip(['id'] + fields[1:], row)), rows))


def select_buid_status(pgsql, bank_uid):
    cursor = pgsql['bank_userinfo'].cursor()
    cursor.execute(
        'SELECT status FROM bank_userinfo.buids WHERE bank_uid = %s',
        [bank_uid],
    )

    return cursor.fetchone()[0]


def update_buid_status(pgsql, bank_uid, status):
    cursor = pgsql['bank_userinfo'].cursor()
    cursor.execute(
        'UPDATE bank_userinfo.buids SET status = %s WHERE bank_uid = %s',
        [status, bank_uid],
    )

    assert cursor.rowcount == 1


def select_buid_history(pgsql, bank_uid):

    cursor = pgsql['bank_userinfo'].cursor()
    fields = [
        'bank_uid',
        'status',
        'operation_type',
        'operation_at',
        'phone_id',
        'reason',
    ]
    cursor.execute(
        f"""
        SELECT {", ".join(fields)}
        FROM bank_userinfo.buids_history
        WHERE bank_uid = %s::UUID
        ORDER BY id DESC
        """,
        [bank_uid],
    )

    return list(map(lambda row: dict(zip(fields, row)), cursor.fetchall()))
