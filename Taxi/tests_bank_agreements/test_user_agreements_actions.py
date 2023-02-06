import pytest

DEFAULT_YABANK_SESSION_UUID = 'session_uuid_1'
DEFAULT_YABANK_PHONE_ID = 'phone_id_1'
DEFAULT_YANDEX_BUID = 'buid_1'
DEFAULT_YANDEX_UID = 'uid_1'
DEFAULT_USER_TICKET = 'user_ticket_1'

UID = 'UID'
BUID = 'BUID'

PG_FIELDS = (
    'user_id_type, user_id, agreement_title, ' 'version, status, initiator'
)


def _default_headers():
    return {
        'X-YaBank-SessionUUID': DEFAULT_YABANK_SESSION_UUID,
        'X-YaBank-PhoneID': DEFAULT_YABANK_PHONE_ID,
        'X-Yandex-BUID': DEFAULT_YANDEX_BUID,
        'X-Yandex-UID': DEFAULT_YANDEX_UID,
        'X-Ya-User-Ticket': DEFAULT_USER_TICKET,
    }


def _default_headers_wo_buid():
    headers = _default_headers()
    headers.pop('X-Yandex-BUID')
    return headers


def _default_headers_wo_uid():
    headers = _default_headers()
    headers.pop('X-Yandex-UID')
    return headers


def is_valid_pg_record(
        record, agreement_title, version, status, is_uid_agreement=False,
):
    if is_uid_agreement:
        assert record[0] == UID
        assert record[1] == DEFAULT_YANDEX_UID
        assert record[5] == {
            'initiator_type': UID,
            'initiator_id': DEFAULT_YANDEX_UID,
        }
    else:
        assert record[0] == BUID
        assert record[1] == DEFAULT_YANDEX_BUID
        assert record[5] == {
            'initiator_type': BUID,
            'initiator_id': DEFAULT_YANDEX_BUID,
        }
    assert record[2] == agreement_title
    assert record[3] == version
    assert record[4] == status
    return True


AGREEMENTS_LIST_V2 = {
    'REGISTRATION': {
        'tanker_key': 'registration_key',
        'tanker_params': {'url1': 'some_url_1', 'url2': 'some_url_2'},
        'version': 0,
    },
    'SIMPLIFIED_IDENTIFICATION': {
        'tanker_key': 'simplified_identification_key',
        'version': 0,
    },
}


@pytest.mark.config(BANK_AGREEMENTS_AGREEMENTS_LIST_V2=AGREEMENTS_LIST_V2)
@pytest.mark.parametrize(
    'operation',
    [
        'agreements-internal/v1/accept_agreement',
        'v1/agreements/v1/reject_agreement',
        'v1/agreements/v1/accept_agreement',
    ],
)
@pytest.mark.parametrize(
    'agreement_title', ['REGISTRATION', 'SIMPLIFIED_IDENTIFICATION'],
)
@pytest.mark.parametrize('version', [0, 1])
async def test_accept_reject_agreement(
        taxi_bank_agreements, pgsql, agreement_title, operation, version,
):
    headers = (
        _default_headers_wo_buid()
        if agreement_title == 'REGISTRATION'
        else _default_headers()
    )
    response = await taxi_bank_agreements.post(
        operation,
        headers=headers,
        json={
            'title': agreement_title,
            'version': version,
            'buid': DEFAULT_YANDEX_BUID,
            'yandex_uid': DEFAULT_YANDEX_UID,
        },
    )

    if version == 0:
        assert response.status_code == 200
    if 'reject' not in operation and version == 1:
        assert response.status_code == 404
    cursor = pgsql['bank_agreements'].cursor()
    cursor.execute(f'SELECT {PG_FIELDS} FROM bank_agreements.events;')
    records = list(cursor)

    if 'reject' not in operation and version == 1:
        assert not records
        return

    operation_type = 'ACCEPT'
    if 'reject' in operation:
        operation_type = 'REJECT'

    assert is_valid_pg_record(
        records[0],
        agreement_title,
        version,
        operation_type,
        agreement_title == 'REGISTRATION',
    )


@pytest.mark.config(BANK_AGREEMENTS_AGREEMENTS_LIST_V2=AGREEMENTS_LIST_V2)
@pytest.mark.parametrize(
    'operation, status_code',
    [
        ('agreements-internal/v1/accept_agreement', 400),
        ('v1/agreements/v1/reject_agreement', 401),
        ('v1/agreements/v1/accept_agreement', 401),
    ],
)
@pytest.mark.parametrize('version', [0, 1])
async def test_accept_reject_agreement_no_buid(
        taxi_bank_agreements, pgsql, operation, status_code, version,
):
    agreement_title = 'SIMPLIFIED_IDENTIFICATION'
    response = await taxi_bank_agreements.post(
        operation,
        headers=_default_headers_wo_buid(),
        json={
            'title': agreement_title,
            'version': version,
            'yandex_uid': DEFAULT_YANDEX_UID,
        },
    )

    assert response.status_code == status_code
    cursor = pgsql['bank_agreements'].cursor()
    cursor.execute(f'SELECT {PG_FIELDS} FROM bank_agreements.events;')
    records = list(cursor)
    assert not records


@pytest.mark.config(BANK_AGREEMENTS_AGREEMENTS_LIST_V2=AGREEMENTS_LIST_V2)
@pytest.mark.parametrize('version,status_code', [(0, 200), (1, 404)])
async def test_accept_agreement_no_uid(
        taxi_bank_agreements, pgsql, version, status_code,
):
    agreement_title = 'SIMPLIFIED_IDENTIFICATION'
    response = await taxi_bank_agreements.post(
        'agreements-internal/v1/accept_agreement',
        headers=_default_headers_wo_uid(),
        json={
            'title': agreement_title,
            'version': version,
            'buid': DEFAULT_YANDEX_BUID,
        },
    )

    assert response.status_code == status_code
    cursor = pgsql['bank_agreements'].cursor()
    cursor.execute(f'SELECT {PG_FIELDS} FROM bank_agreements.events;')
    records = list(cursor)
    if status_code == 200:
        assert records
    else:
        assert not records


@pytest.mark.config(BANK_AGREEMENTS_AGREEMENTS_LIST_V2=AGREEMENTS_LIST_V2)
@pytest.mark.parametrize(
    'agreement_title,locale,expected_text',
    [
        (
            'REGISTRATION',
            'ru',
            'Нажимая на кнопку, вы принимаете <a href=\"some_url_1\">условия'
            + ' использования сервиса</a> и <a href=\"some_url_2\">тарифы</a>',
        ),
        (
            'REGISTRATION',
            'en',
            'By pressing the button, you agree with '
            + '<a href=\"some_url_1\">terms of service use</a> '
            + 'and <a href=\"some_url_2\">tariffs</a>',
        ),
        (
            'REGISTRATION',
            'smth_invalid',
            'Нажимая на кнопку, вы принимаете <a href=\"some_url_1\">условия'
            + ' использования сервиса</a> и <a href=\"some_url_2\">тарифы</a>',
        ),
        (
            'SIMPLIFIED_IDENTIFICATION',
            'ru',
            'Нажимая на кнопку, вы принимаете все условия',
        ),
        (
            'SIMPLIFIED_IDENTIFICATION',
            'en',
            'By pressing the button, you agree with all terms of service use',
        ),
        (
            'SIMPLIFIED_IDENTIFICATION',
            'smth_invalid',
            'Нажимая на кнопку, вы принимаете все условия',
        ),
    ],
)
async def test_get_agreements(
        taxi_bank_agreements, agreement_title, locale, expected_text,
):
    headers = _default_headers()
    headers['X-Request-Language'] = locale
    response = await taxi_bank_agreements.post(
        'v1/agreements/v1/get_agreement',
        headers=headers,
        json={'title': agreement_title},
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json['title'] == agreement_title
    assert response_json['agreement_text'] == expected_text
    assert (
        response_json['version']
        == AGREEMENTS_LIST_V2[agreement_title]['version']
    )
