_PAYMENTS = [
    'payment_id',
    'clid',
    'balance_id',
    'created_at',
    'updated_at',
    'status',
    'origin',
    'doc_id',
]

_PAYMENT_ENTRIES = [
    'payment_id',
    'contract_id',
    'bcid',
    'amount',
    'currency',
    'status_code',
    'status_message',
    'reject_code',
    'reject_message',
]

_PAYMENT_TIMERS = ['clid', 'expires_at']

_BALANCES = [
    'balance_id',
    'clid',
    'date',
    'bcid',
    'contract_id',
    'contract_type',
    'contract_alias',
    'contract_limit',
    'amount',
    'currency',
    'request_flag',
    'org_id',
    'reject_code',
    'reject_reason',
]

_MODE_CHANGES = ['clid', 'active_since', 'active_mode']


def dump_payments(pgsql):
    dump = {}

    with pgsql['fleet_payouts'].cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                {', '.join(_PAYMENTS)}
            FROM
                pay.payments
        """,
        )
        for row in cursor:
            pmt = {c: row[i] for i, c in enumerate(_PAYMENTS)}
            dump[pmt['payment_id']] = pmt

    return dump


def dump_payment_entries(pgsql):
    dump = {}

    with pgsql['fleet_payouts'].cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                {', '.join(_PAYMENT_ENTRIES)}
            FROM
                pay.payment_entries
        """,
        )
        for row in cursor:
            ent = {c: row[i] for i, c in enumerate(_PAYMENT_ENTRIES)}
            dump[(ent['payment_id'], ent['contract_id'])] = ent

    return dump


def dump_payment_timers(pgsql):
    dump = {}

    with pgsql['fleet_payouts'].cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                {', '.join(_PAYMENT_TIMERS)}
            FROM
                pay.payment_timers
        """,
        )
        for row in cursor:
            tmr = {c: row[i] for i, c in enumerate(_PAYMENT_TIMERS)}
            dump[tmr['clid']] = tmr

    return dump


def dump_balances(pgsql):
    dump = {}

    with pgsql['fleet_payouts'].cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                {', '.join(_BALANCES)}
            FROM
                pay.balances
        """,
        )
        for row in cursor:
            bal = {c: row[i] for i, c in enumerate(_BALANCES)}
            dump[(bal['balance_id'], bal['clid'], bal['contract_id'])] = bal

    return dump


def dump_partner_current_mode(pgsql, clid):
    dump = ''
    with pgsql['fleet_payouts'].cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                {','.join(_MODE_CHANGES)}
            FROM
                pay.partner_payout_mode_changes as c
            WHERE
                c.clid = '{clid}'
            ORDER BY active_since DESC
            LIMIT 1
            """,
        )
        row = next(cursor)
        dump = {key: val for (key, val) in zip(_MODE_CHANGES, row)}
    return dump
