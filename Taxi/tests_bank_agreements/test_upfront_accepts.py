import pytest, copy, uuid

from bank_testing.pg_state import PgState, Arbitrary, DateTimeAsStr

IDMPT = '844ef9dd-ca12-4941-b403-54f34aaa71f1'
BUID = 'ade83796-03bb-4326-927c-9314157f1b5c'
BUID_OTHER = '350b02f4-84f4-41aa-ba30-ea3a1a8a28d7'
SUPPORT_LOGIN = 'support_login'

PERMISSION_GRANTED = 'GRANTED'
PERMISSION_DENIED = 'DENIED'

ENTITY_EDA = 'eda'
ENTITY_MARKET = 'market'


@pytest.fixture
def mock_apply_policies(mockserver):
    @mockserver.json_handler(
        '/bank-access-control/access-control-internal/v1/apply-policies',
    )
    def _apply_policies(request):
        assert request.method == 'POST'
        assert 'handler_path' in request.json['resource_attributes']
        assert 'jwt' in request.json['subject_attributes']
        return {'decision': 'PERMIT', 'user_login': SUPPORT_LOGIN}


@pytest.fixture
def db(pgsql):
    db = PgState(pgsql, 'bank_agreements')
    db.add_table(
        'bank_agreements.upfront_accepts',
        'id',
        [
            'id',
            'idempotency_token',
            'buid',
            'entity',
            'permission',
            'source',
            'support_login',
            'support_ticket',
            'created_at',
        ],
        alias='upfront_accepts',
        defaults={'created_at': Arbitrary()},
        converters={'created_at': DateTimeAsStr()},
    )
    return db


SAMPLE_ENTITIES_CONFIG = {
    'market': {'title': 'Яндекс.Маркет'},
    'eda': {'title': 'Яндекс.Еда'},
}


def version_template(id):
    return {
        'idempotency_token': str(uuid.UUID(int=id)),
        'buid': BUID,
        'created_at': f'2020-01-01T12:{id:02}:00',
    }


SAMPLE_HISTORY = {
    1: version_template(1) | {
        'entity': ENTITY_EDA,
        'permission': PERMISSION_GRANTED,
        'source': 'PRO_REGISTRATION',
    },
    2: version_template(1) | {
        'entity': ENTITY_MARKET,
        'permission': PERMISSION_GRANTED,
        'source': 'PRO_REGISTRATION',
    },
    3: version_template(2) | {
        'entity': ENTITY_EDA,
        'permission': PERMISSION_DENIED,
        'source': 'SUPPORT',
        'support_login': 'support_login_1',
        'support_ticket': 'SUPPORT_0001',
    },
    4: version_template(3) | {
        'entity': ENTITY_MARKET,
        'permission': PERMISSION_DENIED,
        'source': 'SUPPORT',
        'support_login': 'support_login_2',
        'support_ticket': 'SUPPORT_0002',
    },
}
AVAILABLE_DB_VERSIONS = [0, 1, 2, 3, 4]

DATETIME_BEFORE_1 = '2020-01-01T12:00:30Z'
# no DATETIME_BETWEEN_1_2 because both inserted by one "operation" with same timestamp
DATETIME_BETWEEN_2_3 = '2020-01-01T12:01:30Z'
DATETIME_BETWEEN_3_4 = '2020-01-01T12:02:30Z'
DATETIME_AFTER_4 = '2020-01-01T12:03:30Z'


def dict_extract(dict, keys):
    return {key: dict[key] for key in keys if key in dict}


def init_sample_db(db, last_version):
    for version in range(1, 1 + last_version):
        db.do_insert('upfront_accepts', SAMPLE_HISTORY[version])


@pytest.mark.parametrize('init_version', AVAILABLE_DB_VERSIONS)
@pytest.mark.parametrize(
    'selected_entities',
    [[], [ENTITY_EDA], [ENTITY_MARKET], [ENTITY_EDA, ENTITY_MARKET]],
)
async def test_internal_init_success(
        taxi_bank_agreements, db, init_version, selected_entities,
):
    init_sample_db(db, init_version)

    # repeated requests succeeds but only first modifies db
    for iter in range(3):
        response = await taxi_bank_agreements.post(
            '/agreements-internal/v1/init_upfront_accepts',
            headers={'X-Idempotency-Token': IDMPT},
            json={
                'buid': BUID,
                'source': 'PRO_REGISTRATION',
                'entities': selected_entities,
            },
        )
        assert response.text == ''
        assert response.status_code == 200
        if iter == 0:
            next_id = init_version + 1
            for entity in selected_entities:
                db.expect_insert(
                    'upfront_accepts',
                    {
                        'id': next_id,
                        'buid': BUID,
                        'idempotency_token': IDMPT,
                        'entity': entity,
                        'permission': PERMISSION_GRANTED,
                        'source': 'PRO_REGISTRATION',
                        'support_login': None,
                        'support_ticket': None,
                    },
                )
                next_id = next_id + 1
        db.assert_valid()


@pytest.mark.config(
    BANK_AGREEMENTS_UPFRONT_ACCEPT_ENTITIES=SAMPLE_ENTITIES_CONFIG,
)
@pytest.mark.parametrize(
    'init_version, selected_entities',
    [
        (0, []),
        (1, [ENTITY_EDA]),
        (2, [ENTITY_EDA, ENTITY_MARKET]),
        (3, [ENTITY_MARKET]),
        (4, []),
    ],
)
async def test_support_get_upfront_accepts(
        taxi_bank_agreements,
        db,
        mock_apply_policies,
        init_version,
        selected_entities,
):
    init_sample_db(db, init_version)

    response = await taxi_bank_agreements.post(
        '/agreements-support/v1/get_upfront_accepts',
        headers={'X-Bank-Token': ''},
        json={'buid': BUID},
    )
    assert response.json() == {
        'selected_entities': selected_entities,
        'available_entities': SAMPLE_ENTITIES_CONFIG,
    }
    assert response.status_code == 200
    db.assert_valid()


@pytest.mark.config(
    BANK_AGREEMENTS_UPFRONT_ACCEPT_ENTITIES=SAMPLE_ENTITIES_CONFIG,
)
@pytest.mark.parametrize('init_version', AVAILABLE_DB_VERSIONS)
@pytest.mark.parametrize('limit', [1, 2, 3, 4])
async def test_support_get_upfront_accepts_history(
        taxi_bank_agreements, db, mock_apply_policies, init_version, limit,
):
    init_sample_db(db, init_version)
    request = {'buid': BUID, 'limit': limit}
    offset = 0

    while True:
        response = await taxi_bank_agreements.post(
            '/agreements-support/v1/get_upfront_accepts_history',
            headers={'X-Bank-Token': ''},
            json=request,
        )
        expect_last = offset + limit >= init_version
        page_versions = [
            SAMPLE_HISTORY[version]
            for version in range(
                init_version - offset,
                max(0, init_version - offset - limit),
                -1,
            )
        ]
        expected_json = {
            'available_entities': SAMPLE_ENTITIES_CONFIG,
            'history': [
                {
                    'entity': version['entity'],
                    'permission': version['permission'],
                    'upfront_accepts_meta': dict_extract(
                        version, ['source', 'support_login', 'support_ticket'],
                    ) | {'created_at': version['created_at'] + '+00:00'},
                }
                for version in page_versions
            ],
        }

        json = response.json()
        if not expect_last:
            expected_json['cursor'] = json['cursor']
        assert json == expected_json
        assert response.status_code == 200

        if expect_last:
            break

        offset += limit
        request['cursor'] = json['cursor']

    db.assert_valid()


@pytest.mark.config(
    BANK_AGREEMENTS_UPFRONT_ACCEPT_ENTITIES=SAMPLE_ENTITIES_CONFIG,
)
@pytest.mark.parametrize('init_version', AVAILABLE_DB_VERSIONS)
@pytest.mark.parametrize(
    'selected_entities',
    [[], [ENTITY_EDA], [ENTITY_MARKET], [ENTITY_EDA, ENTITY_MARKET]],
)
async def test_support_set_upfront_accepts(
        taxi_bank_agreements,
        db,
        mock_apply_policies,
        init_version,
        selected_entities,
):
    init_sample_db(db, init_version)

    headers = {'X-Bank-Token': '', 'X-Idempotency-Token': IDMPT}
    request = {
        'buid': BUID,
        'support_ticket': 'SUPPORT-9999',
        'selected_entities': selected_entities,
    }

    for iter in range(3):
        response = await taxi_bank_agreements.post(
            '/agreements-support/v1/set_upfront_accepts',
            headers=headers,
            json=request,
        )
        assert response.text == ''
        assert response.status_code == 200
        if iter == 0:
            db.expect_insert(
                'upfront_accepts',
                {
                    'id': init_version + 1,
                    'idempotency_token': IDMPT,
                    'buid': BUID,
                    'source': 'SUPPORT',
                    'support_login': SUPPORT_LOGIN,
                    'support_ticket': 'SUPPORT-9999',
                    'entity': ENTITY_EDA,
                    'permission': (
                        PERMISSION_GRANTED
                        if ENTITY_EDA in selected_entities
                        else PERMISSION_DENIED
                    ),
                },
            )
            db.expect_insert(
                'upfront_accepts',
                {
                    'id': init_version + 2,
                    'idempotency_token': IDMPT,
                    'buid': BUID,
                    'source': 'SUPPORT',
                    'support_login': SUPPORT_LOGIN,
                    'support_ticket': 'SUPPORT-9999',
                    'entity': ENTITY_MARKET,
                    'permission': (
                        PERMISSION_GRANTED
                        if ENTITY_MARKET in selected_entities
                        else PERMISSION_DENIED
                    ),
                },
            )
        db.assert_valid()


@pytest.mark.config(
    BANK_AGREEMENTS_UPFRONT_ACCEPT_ENTITIES=SAMPLE_ENTITIES_CONFIG,
)
@pytest.mark.parametrize('init_version', AVAILABLE_DB_VERSIONS)
@pytest.mark.parametrize('entity', ['market', 'eda'])
@pytest.mark.parametrize(
    'datetime',
    [
        DATETIME_BEFORE_1,
        DATETIME_BETWEEN_2_3,
        DATETIME_BETWEEN_3_4,
        DATETIME_AFTER_4,
    ],
)
async def test_check_upfront_accepts_no_records_for_buid(
        taxi_bank_agreements, db, init_version, entity, datetime,
):
    init_sample_db(db, init_version)

    response = await taxi_bank_agreements.post(
        '/agreements-internal/v1/check_upfront_accept',
        json={'buid': BUID_OTHER, 'entity': entity, 'datetime': datetime},
    )
    assert response.json() == {'upfront_accept_permission': PERMISSION_DENIED}
    assert response.status_code == 200
    db.assert_valid()


@pytest.mark.parametrize(
    'datetime, entity, permission',
    [
        (DATETIME_BEFORE_1, ENTITY_MARKET, PERMISSION_DENIED),
        (DATETIME_BEFORE_1, ENTITY_EDA, PERMISSION_DENIED),
        (DATETIME_BETWEEN_2_3, ENTITY_MARKET, PERMISSION_GRANTED),
        (DATETIME_BETWEEN_2_3, ENTITY_EDA, PERMISSION_GRANTED),
        (DATETIME_BETWEEN_3_4, ENTITY_MARKET, PERMISSION_GRANTED),
        (DATETIME_BETWEEN_3_4, ENTITY_EDA, PERMISSION_DENIED),
        (DATETIME_AFTER_4, ENTITY_MARKET, PERMISSION_DENIED),
        (DATETIME_AFTER_4, ENTITY_EDA, PERMISSION_DENIED),
    ],
)
async def test_check_upfront_accepts_datetime(
        taxi_bank_agreements, db, datetime, entity, permission,
):
    init_sample_db(db, 4)

    response = await taxi_bank_agreements.post(
        '/agreements-internal/v1/check_upfront_accept',
        json={'buid': BUID, 'entity': entity, 'datetime': datetime},
    )
    assert response.json() == {'upfront_accept_permission': permission}
    assert response.status_code == 200
    db.assert_valid()
