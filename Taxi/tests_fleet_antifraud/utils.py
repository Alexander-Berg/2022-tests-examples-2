# tvmknife unittest service -s 111 -d 2345
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIbxCpEg:'
    'G4hKvC1tY887M0UUAjj13gJEnzikFS9z9so'
    'b0laeFmJ4JVL0XDyNZtWBu4ZjKf9O_juLZg'
    'hRptbnyiQRqoiBsX1eXLdABRLpdJpAxLY4d'
    'fVOD0o8GEQ7q94GH0uLQOV_POubrySzzMgN'
    'gRFhn_CwXjrfZRziFuk-RV0I-zzTsE4'
)

SERVICE_HEADERS = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}


def build_headers(park_id, idempotency_token=None):
    headers = {
        **SERVICE_HEADERS,
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
    }
    if idempotency_token is not None:
        headers['X-Idempotency-Token'] = idempotency_token
    return headers


def pg_dump_operation(cursor):
    cursor.execute(
        """
        SELECT
            uid,
            started_at,
            created_at,
            name,
            initiator,
            service_id,
            service_name,
            user_id,
            user_provider
        FROM
            fleet_antifraud.operation
    """,
    )
    return {row[0]: row[1:] for row in cursor.fetchall()}


def pg_dump_park_check_settings(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            fleet_antifraud.park_check_settings
        """,
    )
    return {row[0]: row[1:] for row in cursor.fetchall()}


def pg_dump_park_check_suspicious(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            fleet_antifraud.park_check_suspicious
        """,
    )
    return {
        (row[1], row[2], row[8], row[9]): row[3:8] + row[10:]
        for row in cursor.fetchall()
    }


def pg_dump_all(cursor):
    return {
        'operation': pg_dump_operation(cursor),
        'park_check_settings': pg_dump_park_check_settings(cursor),
        'park_check_suspicious': pg_dump_park_check_suspicious(cursor),
    }
