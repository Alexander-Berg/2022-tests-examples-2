import hashlib
import json

from dateutil import parser
import pytest

from testsuite.utils import ordered_object

from tests_billing_commissions import blueprints


@pytest.mark.parametrize('use_mongo', (True, False))
@pytest.mark.parametrize(
    'query_json, expected_db, expected_drafts',
    [
        ('request.json', blueprints.mongo.mongo_after_create(), 'drafts.json'),
        (
            'request_unusual_types.json',
            blueprints.mongo.mongo_after_create_unusual(),
            'drafts_unusual_types.json',
        ),
    ],
)
@pytest.mark.now('2000-04-01T14:00:00Z')
async def test_create_check(
        taxi_billing_commissions,
        billing_commissions_postgres_db,
        mongodb,
        load_json,
        query_json,
        expected_db,
        expected_drafts,
        taxi_config,
        use_mongo,
):
    taxi_config.set_values(
        {'BILLING_COMMISSIONS_MIRRORING_TO_MONGO_ENABLED': use_mongo},
    )
    contracts_count = mongodb.commission_contracts.count()
    query = load_json(query_json)
    response = await taxi_billing_commissions.post(
        'v1/rules/create', json=query, headers={'X-YaTaxi-Draft-Author': 'me'},
    )
    assert response.status_code == 200, response.json()
    data = response.json()
    change_doc_id = data['change_doc_id'].split(':')[-1]
    assert data['data']['commissions'] == query['commissions']
    _assert_change_doc_id(query['commissions'], data['change_doc_id'])
    if use_mongo:
        _assert_contracts(mongodb, expected_db)
        expected_count = contracts_count + len(expected_db)
        assert mongodb.commission_contracts.count() == expected_count
    else:
        assert mongodb.commission_contracts.count() == contracts_count
    # postgres
    draft_spec_id = data['data']['draft_spec_id']
    spec = _get_draft_spec(billing_commissions_postgres_db, draft_spec_id)
    assert spec == {
        'change_doc_id': change_doc_id,
        'initiator': 'me',
        'approvers': '',
        'ticket': '',
        'external_draft_id': '',
        'approved_at': None,
    }
    drafts = _get_drafts(billing_commissions_postgres_db, draft_spec_id)
    for draft in drafts:
        draft.pop('rule_id')
    ordered_object.assert_eq(drafts, load_json(expected_drafts), ['rule_type'])


def _get_draft_spec(cursor, draft_spec_id):
    sql = """
    SELECT change_doc_id, initiator, ticket, approvers, external_draft_id,
           approved_at
    FROM fees.draft_spec WHERE id = %s;
    """
    cursor.execute(sql, (draft_spec_id,))
    fields = [column.name for column in cursor.description]
    return dict(zip(fields, cursor.fetchone() or ()))


def _get_drafts(cursor, draft_spec_id):
    sql = """
    SELECT
        rule_id,
        tariff_zone,
        tariff,
        tag,
        payment_type,
        TO_CHAR(timezone('UTC', starts_at),
                'YYYY-MM-DD"T"HH24:MI:SS"Z"') as starts_at,
        CASE
            WHEN ends_at IS NULL
            THEN NULL
            ELSE TO_CHAR(timezone('UTC', ends_at),
                         'YYYY-MM-DD"T"HH24:MI:SS"Z"')
        END as ends_at,
        time_zone,
        rule_type,
        fee,
        min_order_cost,
        max_order_cost,
        billing_values,
        rates,
        cancellation_percent,
        expiration,
        branding_discounts,
        vat
    FROM fees.base_rule_draft
    WHERE draft_spec_id = %s;
    """
    cursor.execute(sql, (draft_spec_id,))
    fields = [column.name for column in cursor.description]
    return [dict(zip(fields, row)) for row in cursor.fetchall()]


@pytest.mark.parametrize('use_mongo', (True, False))
@pytest.mark.parametrize(
    'query_json,existed_rules,expected_message',
    [
        (
            'request_duplicate_id.json',
            [],
            {
                'code': 'INCORRECT_PARAMETERS',
                'message': 'Duplicate keys found',
            },
        ),
        (
            'request_not_valid_begin.json',
            [],
            {
                'code': 'INCORRECT_PARAMETERS',
                'message': 'Object starts in the past',
            },
        ),
        (
            'request_spb_intersect.json',
            [
                dict(
                    tariff_zone='spb',
                    tariff='econom',
                    tag=None,
                    payment_type='cash',
                    starts_at='2001-12-12T09:00:00+00:00',
                ),
                dict(
                    tariff_zone='spb',
                    tariff='econom',
                    tag=None,
                    payment_type='cash',
                    starts_at='2001-12-12T09:00:00+00:00',
                ),
            ],
            {
                'code': 'INCORRECT_PARAMETERS',
                'message': (
                    'Too many active contracts for contract (zone: spb, '
                    'tag: -, tariff: econom, payment_type: cash, '
                    'begin_at: 2001-12-12T09:00:00Z)'
                ),
            },
        ),
    ],
)
@pytest.mark.now('2000-04-01T14:00:00Z')
async def test_create_check_validation_failures(
        taxi_billing_commissions,
        mongodb,
        load_json,
        query_json,
        existed_rules,
        expected_message,
        taxi_config,
        use_mongo,
        base_create_rules,
        a_base_rule,
):
    taxi_config.set_values(
        {'BILLING_COMMISSIONS_MIRRORING_TO_MONGO_ENABLED': use_mongo},
    )
    if existed_rules:
        base_create_rules(*[a_base_rule(**attrs) for attrs in existed_rules])

    contracts_count = mongodb.commission_contracts.count()
    response = await taxi_billing_commissions.post(
        'v1/rules/create',
        json=load_json(query_json),
        headers={'X-YaTaxi-Draft-Author': 'me'},
    )
    assert response.status_code == 400, response.json()
    assert response.json() == expected_message
    assert mongodb.commission_contracts.count() == contracts_count


@pytest.mark.parametrize('use_mongo', (True, False))
@pytest.mark.now('1999-04-01T14:00:00Z')
async def test_create_check_approve(
        taxi_billing_commissions,
        mongodb,
        billing_commissions_postgres_db,
        load_json,
        mockserver,
        base_create_drafts,
        base_create_rules,
        a_base_rule,
        taxi_config,
        use_mongo,
):
    taxi_config.set_values(
        {'BILLING_COMMISSIONS_MIRRORING_TO_MONGO_ENABLED': use_mongo},
    )
    # existsing data
    base_create_rules(
        a_base_rule(
            rule_id='5e4281104602ddca140a628d',
            payment_type='cash',
            starts_at='2000-12-12T09:00:00Z',
            updated_at='1999-01-01T00:00:00Z',
        ),
        a_base_rule(
            rule_id='ends_at_not_changed',
            tag='xyz',
            payment_type='cash',
            starts_at='2000-12-12T09:00:00Z',
            updated_at='1999-01-01T00:00:00Z',
        ),
    )
    contracts_count = mongodb.commission_contracts.count()
    query = load_json('request.json')
    audit_requests = []
    draft_id = base_create_drafts(
        a_base_rule(
            rule_id='5e4282104602ddca140a628d',
            payment_type='cash',
            starts_at='2001-12-12T09:00:00Z',
            rule_type='asymptotic_formula',
            fee={
                'asymp': 420000,
                'cost_norm': 420000,
                'max_commission_percent': 420000,
                'numerator': 420000,
            },
            acquiring=420000,
            agent=420000,
            call_center=420000,
            cancellation_percent=420000,
            hiring=420000,
            hiring_rent=420000,
            hiring_age=3628800,
            taximeter=420000,
            min_cost=420000,
            max_cost=120000,
            branding_discounts=[
                {'marketing_level': ['sfsfdsfsdfs'], 'value': 123122130000},
            ],
            billing_values={
                'bcd': 42,
                'p_max': 2,
                'p_min': 1,
                'u_max': 2,
                'u_min': 1,
            },
            expired_cost=320000,
            expired_percent=420000,
            vat=120000,
        ),
        change_doc_id='test_approve_draft_id',
        initiator='author',
    )
    query['draft_spec_id'] = draft_id

    # setup mock for audit
    @mockserver.json_handler('/audit/v1/robot/logs/')
    def mock_create_log(request):
        audit_requests.append(json.loads(request.get_data()))
        return {'id': '123456'}

    async with taxi_billing_commissions.capture_logs() as logs:
        response = await taxi_billing_commissions.post(
            'v1/rules/create/approve',
            json=query,
            headers={
                'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
                'X-YaTaxi-Draft-Author': 'author',
                'X-YaTaxi-Draft-Approvals': 'approver',
                'X-YaTaxi-Draft-Id': 'draft_id',
            },
        )
    assert response.status_code == 200, response.json()
    if use_mongo:
        assert mongodb.commission_contracts.count() == contracts_count
        _assert_contracts(
            mongodb, blueprints.mongo.mongo_after_create_approve(),
        )
    assert mock_create_log.times_called == 1
    assert audit_requests == load_json(
        'valid_audit_arguments.json', object_hook=None,
    )
    # postgres
    draft_spec_id = query['draft_spec_id']
    spec = _get_draft_spec(billing_commissions_postgres_db, draft_spec_id)
    assert spec == {
        'change_doc_id': 'test_approve_draft_id',
        'initiator': 'author',
        'approvers': 'approver',
        'ticket': 'RUPRICE-55',
        'external_draft_id': 'draft_id',
        'approved_at': parser.parse('1999-04-01T14:00:00Z'),
    }
    expected = load_json('base_rules.json')
    rules = _get_rules(billing_commissions_postgres_db, draft_spec_id)
    assert rules == expected['added']
    closed_rules = _get_closed_rules(
        billing_commissions_postgres_db,
        [r['rule_id'] for r in expected['closed']],
    )
    ordered_object.assert_eq(closed_rules, expected['closed'], ['', 'rule_id'])
    assert logs.select(level='WARNING') == []


def _get_rules(cursor, draft_spec_id):
    sql = """
    SELECT
        rule_id,
        tariff_zone,
        tariff,
        tag,
        payment_type,
        TO_CHAR(timezone('UTC', starts_at),
                'YYYY-MM-DD"T"HH24:MI:SS"Z"') as starts_at,
        CASE
            WHEN ends_at IS NULL
            THEN NULL
            ELSE TO_CHAR(timezone('UTC', ends_at),
                         'YYYY-MM-DD"T"HH24:MI:SS"Z"')
        END as ends_at,
        time_zone,
        rule_type,
        fee,
        min_order_cost,
        max_order_cost,
        billing_values,
        rates,
        cancellation_percent,
        expiration,
        branding_discounts,
        vat,
        changelog
    FROM fees.base_rule
    WHERE draft_spec_id = %s;
    """
    cursor.execute(sql, (draft_spec_id,))
    fields = [column.name for column in cursor.description]
    return [dict(zip(fields, row)) for row in cursor.fetchall()]


def _get_closed_rules(cursor, rule_ids):
    sql = """
    SELECT
        rule_id,
        TO_CHAR(timezone('UTC', ends_at),
                'YYYY-MM-DD"T"HH24:MI:SS"Z"') as ends_at,
        changelog,
        TO_CHAR(timezone('UTC', updated_at),
                'YYYY-MM-DD"T"HH24:MI:SS"Z"') as updated_at
    FROM fees.base_rule
    WHERE rule_id = ANY(%s::varchar[]);
    """
    cursor.execute(sql, (rule_ids,))
    fields = [column.name for column in cursor.description]
    return [dict(zip(fields, row)) for row in cursor.fetchall()]


@pytest.mark.now('1999-04-01T14:00:00Z')
async def test_create_check_approve_invalid(
        taxi_billing_commissions,
        mongodb,
        load_json,
        base_create_drafts,
        base_create_rules,
        a_base_rule,
):
    # existsing data
    base_create_rules(
        a_base_rule(
            rule_id='5e4281104602ddca140a628d',
            tag='xyz',
            payment_type='cash',
            starts_at='2000-12-12T09:00:00Z',
        ),
    )
    expected_count = mongodb.commission_contracts.count()

    draft_id = base_create_drafts(
        a_base_rule(
            rule_id='42.1',
            tag='xyz',
            payment_type='cash',
            starts_at='1999-12-12T12:00:00Z',
        ),
    )
    query = load_json('request_early_begin.json')
    query['draft_spec_id'] = draft_id

    response = await taxi_billing_commissions.post(
        'v1/rules/create/approve',
        json=query,
        headers={
            'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
            'X-YaTaxi-Draft-Author': 'author',
            'X-YaTaxi-Draft-Approvals': 'approver',
            'X-YaTaxi-Draft-Id': 'draft_id',
        },
    )
    assert response.status_code == 400, response.json()
    assert mongodb.commission_contracts.count() == expected_count
    assert response.json() == {
        'code': 'VALIDATION_ERROR',
        'message': '42.1 intersects with 5e4281104602ddca140a628d',
    }


def _assert_change_doc_id(commissions, actual):
    ids = [commission['id'] for commission in commissions]
    zones = [commission['matcher']['zone'] for commission in commissions]
    expected = '{}:{}'.format(
        ':'.join(sorted(set(zones))),
        hashlib.sha1(':'.join(sorted(set(ids))).encode()).hexdigest(),
    )
    assert actual == expected


def _assert_contracts(mongodb, expected):
    actual = blueprints.helpers.clean_mongo_data_before_compare(
        mongodb.commission_contracts.find({'external_id': {'$exists': True}}),
    )
    ordered_object.assert_eq(actual, expected, ['external_id'])


@pytest.mark.now('2000-04-01T14:00:00Z')
@pytest.mark.parametrize('kind', ('asymptotic', 'call_center'))
async def test_v1_rules_create_demands_presense_of_required_values(
        taxi_billing_commissions, load_json, kind,
):
    query = load_json('request.json')
    query['commissions'] = _drop_agreement_by_kind(query['commissions'], kind)
    response = await taxi_billing_commissions.post(
        'v1/rules/create', json=query, headers={'X-YaTaxi-Draft-Author': 'me'},
    )
    assert response.status_code == 400, response.json()
    assert response.json() == {
        'code': 'INCORRECT_PARAMETERS',
        'message': 'The list of agreements is incomplete',
    }


@pytest.mark.now('2000-04-01T14:00:00Z')
@pytest.mark.parametrize(
    'kind', ('taximeter', 'hiring', 'hiring_commercial', 'acquiring', 'agent'),
)
async def test_v1_rules_create_ignores_absense_of_optional_values(
        taxi_billing_commissions, load_json, kind,
):
    query = load_json('request.json')
    query['commissions'] = _drop_agreement_by_kind(query['commissions'], kind)
    response = await taxi_billing_commissions.post(
        'v1/rules/create', json=query, headers={'X-YaTaxi-Draft-Author': 'me'},
    )
    assert response.status_code == 200, response.json()


def _drop_agreement_by_kind(drafts, kind):
    for draft in drafts:
        draft['agreements'] = [
            agreement
            for agreement in draft['agreements']
            if agreement['kind'] != kind
        ]
    return drafts


@pytest.mark.now('2022-05-24T18:30:00+03:00')
@pytest.mark.parametrize('use_mongo', (True, False))
async def test_create_rule_with_unrealized_rate(
        taxi_billing_commissions,
        billing_commissions_postgres_db,
        mockserver,
        load_json,
        taxi_config,
        use_mongo,
):
    taxi_config.set_values(
        {'BILLING_COMMISSIONS_MIRRORING_TO_MONGO_ENABLED': use_mongo},
    )
    query = load_json('draft_with_unrealized_rate.json')
    response = await taxi_billing_commissions.post(
        'v1/rules/create', json=query, headers={'X-YaTaxi-Draft-Author': 'me'},
    )
    assert response.status_code == 200, response.json()
    draft_data = response.json()
    draft_spec_id = draft_data['data']['draft_spec_id']
    drafts = _get_drafts(billing_commissions_postgres_db, draft_spec_id)
    assert len(drafts) == 1
    rates = drafts[0]['rates']
    assert rates['unrealized_rate'] == 105000, rates

    # setup mock for audit
    @mockserver.json_handler('/audit/v1/robot/logs/')
    def mock_create_log(_):  # pylint: disable=unused-variable
        return {'id': '123456'}

    response = await taxi_billing_commissions.post(
        'v1/rules/create/approve',
        json=draft_data['data'],
        headers={
            'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
            'X-YaTaxi-Draft-Author': 'me',
            'X-YaTaxi-Draft-Approvals': 'approver',
            'X-YaTaxi-Draft-Id': 'draft_id',
        },
    )
    assert response.status_code == 200, response.json()
    rules = _get_rules(billing_commissions_postgres_db, draft_spec_id)
    assert len(rules) == 1
    rates = rules[0]['rates']
    assert rates['unrealized_rate'] == 105000, rates
