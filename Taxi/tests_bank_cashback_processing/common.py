def get_payment_status(pgsql, idempotency_token):
    cursor = pgsql['bank_cashback_processing'].cursor()
    cursor.execute(
        'select status '
        'from bank_cashback_processing.cashbacks '
        'where idempotency_token = %s',
        (idempotency_token,),
    )
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert len(rows[0]) == 1
    return rows[0][0]


def set_payment_status(pgsql, idempotency_token, status='CREATED'):
    cursor = pgsql['bank_cashback_processing'].cursor()
    cursor.execute(
        'update bank_cashback_processing.cashbacks '
        'set status = %s '
        'where idempotency_token = %s',
        (status, idempotency_token),
    )
