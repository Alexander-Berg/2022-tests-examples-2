import pytest

DEFAULT_YANDEX_BUID = 'buid_1'
DEFAULT_YANDEX_UID = 'uid_1'
DEFAULT_YABANK_PHONE_ID = 'phone_id_1'
DEFAULT_YABANK_SUPPORT_ID = 'support_id_1'

UID = 'UID'
BUID = 'BUID'

PG_FIELDS = (
    'user_id_type, user_id, agreement_title, ' 'version, status, initiator'
)


def _default_headers():
    return {'X-YaBank-SupportID': DEFAULT_YABANK_SUPPORT_ID}


def is_valid_pg_record(
        record, agreement_title, version, status, is_uid_agreement=False,
):
    if is_uid_agreement:
        assert record[0] == UID
        assert record[1] == DEFAULT_YANDEX_UID
    else:
        assert record[0] == BUID
        assert record[1] == DEFAULT_YANDEX_BUID
    assert record[2] == agreement_title
    assert record[3] == version
    assert record[4] == status
    assert record[5] == {
        'initiator_type': 'SUPPORT',
        'initiator_id': DEFAULT_YABANK_SUPPORT_ID,
    }
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
    'EXPIRING_TITLE': {
        'tanker_key': 'expiring_title_key',
        'version': 0,
        'expiration_duration': 0,
    },
}


@pytest.mark.config(BANK_AGREEMENTS_AGREEMENTS_LIST_V2=AGREEMENTS_LIST_V2)
@pytest.mark.parametrize('operation', ['accept', 'reject'])
@pytest.mark.parametrize(
    'agreement_title', ['REGISTRATION', 'SIMPLIFIED_IDENTIFICATION'],
)
@pytest.mark.parametrize('version', [0, 1])
async def test_support_accept_reject_agreement(
        taxi_bank_agreements,
        pgsql,
        agreement_title,
        operation,
        version,
        mockserver,
        userinfo_mock,
):
    response = await taxi_bank_agreements.post(
        'v1/agreements_support/v1/' + operation + '_agreement',
        headers=_default_headers(),
        json={
            'title': agreement_title,
            'version': version,
            'uid': DEFAULT_YANDEX_UID,
        },
    )

    if version == 0:
        assert response.status_code == 200
    if operation != 'reject' and version == 1:
        assert response.status_code == 404
    cursor = pgsql['bank_agreements'].cursor()
    cursor.execute(f'SELECT {PG_FIELDS} FROM bank_agreements.events;')
    records = list(cursor)

    if operation != 'reject' and version == 1:
        assert not records
        return

    print(records)
    assert is_valid_pg_record(
        records[0],
        agreement_title,
        version,
        operation.upper(),
        agreement_title == 'REGISTRATION',
    )


@pytest.mark.config(BANK_AGREEMENTS_AGREEMENTS_LIST_V2=AGREEMENTS_LIST_V2)
@pytest.mark.parametrize('operation', ['accept', 'reject'])
async def test_support_neg_buid_check_accept_reject_agreement(
        taxi_bank_agreements, pgsql, operation, mockserver, userinfo_mock,
):
    userinfo_mock.response_code = 404

    response = await taxi_bank_agreements.post(
        'v1/agreements_support/v1/' + operation + '_agreement',
        headers=_default_headers(),
        json={'title': 'anon', 'version': 0, 'uid': DEFAULT_YANDEX_UID},
    )

    assert response.status_code == 404


@pytest.mark.config(BANK_AGREEMENTS_AGREEMENTS_LIST_V2=AGREEMENTS_LIST_V2)
@pytest.mark.parametrize(
    'agreement_title,locale,expected_text',
    [
        (
            'REGISTRATION',
            'ru',
            'Нажимая на кнопку, вы принимаете <a href=\"some_url_1\">условия '
            + 'использования сервиса</a> и <a href=\"some_url_2\">тарифы</a>',
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
            'Нажимая на кнопку, вы принимаете <a href=\"some_url_1\">условия '
            + 'использования сервиса</a> и <a href=\"some_url_2\">тарифы</a>',
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
async def test_support_get_agreements(
        taxi_bank_agreements, agreement_title, locale, expected_text,
):
    headers = _default_headers()
    headers['X-Request-Language'] = locale
    response = await taxi_bank_agreements.post(
        'v1/agreements_support/v1/get_agreement',
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


@pytest.mark.config(BANK_AGREEMENTS_AGREEMENTS_LIST_V2=AGREEMENTS_LIST_V2)
@pytest.mark.parametrize(
    'agreement_title', ['REGISTRATION', 'SIMPLIFIED_IDENTIFICATION'],
)
async def test_support_revoke_by_title_agreement(
        taxi_bank_agreements,
        pgsql,
        agreement_title,
        mockserver,
        userinfo_mock,
):
    response = await taxi_bank_agreements.post(
        'v1/agreements_support/v1/accept_agreement',
        headers=_default_headers(),
        json={
            'title': agreement_title,
            'version': 0,
            'uid': DEFAULT_YANDEX_UID,
        },
    )
    assert response.status_code == 200

    response = await taxi_bank_agreements.post(
        'v1/agreements_support/v1/revoke_agreement',
        headers=_default_headers(),
        json={'title': agreement_title, 'uid': DEFAULT_YANDEX_UID},
    )

    assert response.status_code == 200

    cursor = pgsql['bank_agreements'].cursor()
    cursor.execute(
        f'SELECT {PG_FIELDS} FROM bank_agreements.events '
        'WHERE status=\'REVOKE\';',
    )
    records = list(cursor)

    assert len(records) == 1

    assert is_valid_pg_record(
        records[0],
        agreement_title,
        0,
        'REVOKE',
        agreement_title == 'REGISTRATION',
    )


@pytest.mark.config(BANK_AGREEMENTS_AGREEMENTS_LIST_V2=AGREEMENTS_LIST_V2)
async def test_neg_support_revoke_agreement(taxi_bank_agreements, pgsql):
    response = await taxi_bank_agreements.post(
        'v1/agreements_support/v1/revoke_agreement',
        headers=_default_headers(),
        json={'title': 'REGISTRATION', 'all': True, 'uid': DEFAULT_YANDEX_UID},
    )
    assert response.status_code == 400


@pytest.mark.config(BANK_AGREEMENTS_AGREEMENTS_LIST_V2=AGREEMENTS_LIST_V2)
async def test_support_revoke_all_agreement(
        taxi_bank_agreements, pgsql, mockserver, userinfo_mock,
):
    response = await taxi_bank_agreements.post(
        'v1/agreements_support/v1/accept_agreement',
        headers=_default_headers(),
        json={
            'title': 'REGISTRATION',
            'version': 0,
            'uid': DEFAULT_YANDEX_UID,
        },
    )
    assert response.status_code == 200
    response = await taxi_bank_agreements.post(
        'v1/agreements_support/v1/accept_agreement',
        headers=_default_headers(),
        json={
            'title': 'SIMPLIFIED_IDENTIFICATION',
            'version': 0,
            'uid': DEFAULT_YANDEX_UID,
        },
    )
    assert response.status_code == 200

    response = await taxi_bank_agreements.post(
        'v1/agreements_support/v1/revoke_agreement',
        headers=_default_headers(),
        json={'all': True, 'uid': DEFAULT_YANDEX_UID},
    )

    assert response.status_code == 200

    cursor = pgsql['bank_agreements'].cursor()
    cursor.execute(
        f'SELECT {PG_FIELDS} FROM bank_agreements.events '
        'WHERE status=\'REVOKE\';',
    )
    records = list(cursor)

    print(records)

    assert len(records) == 3

    for record in records:
        assert is_valid_pg_record(
            record, record[2], 0, 'REVOKE', record[2] == 'REGISTRATION',
        )


@pytest.mark.config(BANK_AGREEMENTS_AGREEMENTS_LIST_V2=AGREEMENTS_LIST_V2)
async def test_support_get_all_agreement_status(
        taxi_bank_agreements, mockserver, userinfo_mock,
):
    response = await taxi_bank_agreements.post(
        'v1/agreements_support/v1/accept_agreement',
        headers=_default_headers(),
        json={
            'title': 'REGISTRATION',
            'version': 0,
            'uid': DEFAULT_YANDEX_UID,
        },
    )
    assert response.status_code == 200

    response = await taxi_bank_agreements.post(
        'v1/agreements_support/v1/get_agreements_status',
        headers=_default_headers(),
        json={'uid': DEFAULT_YANDEX_UID},
    )

    assert response.status_code == 200

    response_json = response.json()

    expected_states = [
        {
            'title': 'REGISTRATION',
            'version': 0,
            'status': 'ACCEPT',
            'initiator_type': 'SUPPORT',
            'initiator_id': DEFAULT_YABANK_SUPPORT_ID,
        },
        {'title': 'SIMPLIFIED_IDENTIFICATION', 'status': 'NONE'},
        {'title': 'EXPIRING_TITLE', 'status': 'NONE'},
    ]

    for status_json in response_json['statuses']:
        if status_json['title'] == 'REGISTRATION':
            assert status_json['version'] == 0
            assert status_json['status'] == 'ACCEPT'
            assert status_json['initiator_type'] == 'SUPPORT'
            assert status_json['initiator_id'] == DEFAULT_YABANK_SUPPORT_ID
        else:
            assert status_json in expected_states


@pytest.mark.config(BANK_AGREEMENTS_AGREEMENTS_LIST_V2=AGREEMENTS_LIST_V2)
@pytest.mark.parametrize(
    'agreement_title', ['REGISTRATION', 'SIMPLIFIED_IDENTIFICATION'],
)
async def test_support_get_one_agreement_status(
        taxi_bank_agreements, mockserver, agreement_title, userinfo_mock,
):
    response = await taxi_bank_agreements.post(
        'v1/agreements_support/v1/accept_agreement',
        headers=_default_headers(),
        json={
            'title': agreement_title,
            'version': 0,
            'uid': DEFAULT_YANDEX_UID,
        },
    )
    assert response.status_code == 200

    response = await taxi_bank_agreements.post(
        'v1/agreements_support/v1/get_agreements_status',
        headers=_default_headers(),
        json={'uid': DEFAULT_YANDEX_UID, 'title': agreement_title},
    )

    assert response.status_code == 200

    response_json = response.json()

    assert response_json['statuses'][0]['title'] == agreement_title
    assert response_json['statuses'][0]['version'] == 0
    assert response_json['statuses'][0]['status'] == 'ACCEPT'
    assert response_json['statuses'][0]['initiator_type'] == 'SUPPORT'
    assert (
        response_json['statuses'][0]['initiator_id']
        == DEFAULT_YABANK_SUPPORT_ID
    )


@pytest.mark.config(BANK_AGREEMENTS_AGREEMENTS_LIST_V2=AGREEMENTS_LIST_V2)
async def test_support_get_expired_agreement_status(
        taxi_bank_agreements, pgsql, mockserver, userinfo_mock,
):
    title = 'EXPIRING_TITLE'

    response = await taxi_bank_agreements.post(
        'v1/agreements_support/v1/accept_agreement',
        headers=_default_headers(),
        json={'title': title, 'version': 0, 'uid': DEFAULT_YANDEX_UID},
    )
    assert response.status_code == 200

    response = await taxi_bank_agreements.post(
        'v1/agreements_support/v1/get_agreements_status',
        headers=_default_headers(),
        json={'uid': DEFAULT_YANDEX_UID, 'title': title},
    )

    assert response.status_code == 200

    response_json = response.json()

    assert response_json['statuses'][0]['title'] == title
    assert response_json['statuses'][0]['version'] == 0
    assert response_json['statuses'][0]['status'] == 'EXPIRED'
    assert response_json['statuses'][0]['initiator_type'] == 'EXPIRATION'
