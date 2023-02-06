import typing as tp


def get_bank_communications_records(pgsql):
    cursor = pgsql['bank_communications'].cursor()

    cursor.execute(f'SELECT * FROM bank_communications.communications;')
    columns = [column.name for column in cursor.description]
    records_communications = [dict(zip(columns, row)) for row in cursor]

    cursor.execute(f'SELECT * FROM bank_communications.yasms;')
    columns = [column.name for column in cursor.description]
    records_yasms = [dict(zip(columns, row)) for row in cursor]
    return records_communications, records_yasms


def check_pg_records(
        pgsql,
        buid,
        phone,
        headers: tp.Dict[str, str],
        status: str,
        error_code: tp.Optional[str] = None,
        message_sent_id: tp.Optional[str] = None,
        locale: tp.Optional[str] = 'ru',
        tanker_key: tp.Optional[str] = 'text',
):
    records_communications, records_yasms = get_bank_communications_records(
        pgsql,
    )
    record_communications, record_yasms = (
        records_communications[0],
        records_yasms[0],
    )

    assert record_communications['bank_uid'] == buid
    assert (
        record_communications['idempotency_token']
        == headers['X-Idempotency-Token']
    )

    assert (
        record_yasms['communication_id']
        == record_communications['communication_id']
    )

    assert record_yasms['status'] == status
    assert record_yasms['locale'] == locale
    assert record_yasms['tanker_key'] == tanker_key
    assert record_yasms['error_code'] == error_code
    assert record_yasms['message_sent_id'] == message_sent_id
    assert record_yasms['phone_number'] == phone


def get_yasms_id(pgsql):
    _, records_yasms = get_bank_communications_records(pgsql)

    return records_yasms[0]['yasms_id']


def get_last_subscriptions(pgsql, uuid):
    cursor = pgsql['bank_communications'].cursor()

    fields = [
        'subscription_id',
        'bank_uid',
        'xiva_subscription_id',
        'uuid',
        'device_id',
        'status',
        'locale',
    ]
    cursor.execute(
        f'SELECT {",".join(fields)} FROM'
        f' bank_communications.push_subscriptions '
        f'where uuid=\'{uuid}\''
        f'order by created_at desc;',
    )

    res = cursor.fetchall()
    for i, _ in enumerate(res):
        res[i] = dict(zip(fields, res[i]))
    return res


def insert_push_subscription(
        pgsql, uuid, bank_uid, status='ACTIVE', locale='ru',
):
    cursor = pgsql['bank_communications'].cursor()

    cursor.execute(
        f'INSERT INTO bank_communications.push_subscriptions '
        f'(bank_uid, xiva_subscription_id, uuid, device_id, status, locale) '
        f'values (\'{bank_uid}\', \'xiva_subscription_id\', \'{uuid}\','
        f'\'device_id\', \'{status}\', \'{locale}\') '
        f'returning subscription_id ',
    )

    return cursor.fetchone()[0]


def insert_push_notification(
        pgsql,
        communication_id,
        status,
        subscription_id,
        uuid='uuid',
        notification_text='notification_text',
        bank_uid='7948e3a9-623c-4524-a390-9e4264d27a11',
        title='title',
):
    cursor = pgsql['bank_communications'].cursor()

    cursor.execute(
        f'INSERT INTO bank_communications.push_notifications '
        f'(communication_id, status, subscription_id, '
        f'bank_uid, uuid, notification_text, title) '
        f'values (\'{communication_id}\', \'{status}\', \'{subscription_id}\','
        f'\'{bank_uid}\','
        f'\'uuid\', \'notification_text\', \'title\')',
    )


def get_push_by_communication_id(pgsql, communication_id):
    cursor = pgsql['bank_communications'].cursor()

    fields = [
        'status',
        'notification_text',
        'uuid',
        'notification_id',
        'title',
    ]
    cursor.execute(
        f'SELECT {",".join(fields)} from '
        f'bank_communications.push_notifications '
        f'where communication_id = \'{communication_id}\' ',
    )

    return dict(zip(fields, cursor.fetchone()))
