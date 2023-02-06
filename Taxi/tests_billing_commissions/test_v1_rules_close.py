# pylint: disable=too-many-lines
import copy

from dateutil import parser
import pytest
import pytz

MOCK_NOW = '2017-01-01T00:00:00+03:00'


@pytest.mark.parametrize('use_mongo', (True, False))
@pytest.mark.parametrize(
    'query, status, expected_response',
    [
        (  # normal close
            {
                '_id': 'some_asymptotic_formula_commission_contract_id',
                'close_at': '2017-01-01T18:48:00.000000+03:00',
            },
            200,
            {},
        ),
        (  # close in future
            {
                '_id': 'some_asymptotic_formula_commission_contract_id',
                'close_at': '2018-01-01T18:48:00.000000+03:00',
            },
            400,
            {
                'code': 'INCORRECT_PARAMETERS',
                'message': 'Rule not exist or already closed',
            },
        ),
        (  # close without end field
            {
                '_id': (
                    'some_fixed_percent_commission_contract_id'
                    '_with_unlimited_end'
                ),
                'close_at': '2018-01-01T18:48:00.000000+03:00',
            },
            200,
            {},
        ),
        (  # nonexistent
            {'_id': 'badc0de', 'close_at': '2018-01-01T18:48:00.000000+03:00'},
            400,
            {
                'code': 'INCORRECT_PARAMETERS',
                'message': 'Rule not exist or already closed',
            },
        ),
    ],
)
@pytest.mark.now(MOCK_NOW)
async def test_rules_close_approve(
        taxi_billing_commissions,
        billing_commissions_postgres_db,
        query,
        status,
        expected_response,
        mongodb,
        taxi_config,
        use_mongo,
        base_create_drafts,
):
    taxi_config.set_values(
        {'BILLING_COMMISSIONS_MIRRORING_TO_MONGO_ENABLED': use_mongo},
    )
    query['draft_id'] = base_create_drafts(
        change_doc_id='Close rule draft', initiator='author',
    )

    headers = {
        'X-YaTaxi-Draft-Tickets': 'RUPRICE-55',
        'X-YaTaxi-Draft-Author': 'author',
        'X-YaTaxi-Draft-Approvals': 'approver',
        'X-YaTaxi-Draft-Id': 'draft_id',
    }

    response = await taxi_billing_commissions.post(
        'v1/rules/close/approve', json=query, headers=headers,
    )
    assert response.status_code == status, response.json()
    assert response.json() == expected_response
    if status != 200:
        return
    if use_mongo:
        mongo_query = {
            '_id': query['_id'],
            'e': parser.parse(query['close_at']).astimezone(pytz.utc),
        }
        result = list(
            mongodb.commission_contracts.find(copy.deepcopy(mongo_query)),
        )
        assert result
        for part in result:
            assert part['log'] == [
                {
                    'ticket': headers['X-YaTaxi-Draft-Tickets'],
                    'login': headers['X-YaTaxi-Draft-Author'],
                    'e': mongo_query['e'].replace(tzinfo=None),
                },
            ]
            assert part['e'] == mongo_query['e'].replace(tzinfo=None)
    expected_close_at = parser.parse(query['close_at'])
    rule = _get_closed_rule(billing_commissions_postgres_db, query['_id'])
    assert parser.parse(rule['ends_at']) == expected_close_at
    log = {
        'ticket': headers['X-YaTaxi-Draft-Tickets'],
        'login': headers['X-YaTaxi-Draft-Author'],
        'end': expected_close_at.replace(tzinfo=None).isoformat(),
    }
    assert log in rule['changelog']
    spec = _get_draft_spec(billing_commissions_postgres_db, query['draft_id'])
    assert spec == {
        'change_doc_id': 'Close rule draft',
        'initiator': headers['X-YaTaxi-Draft-Author'],
        'approvers': headers['X-YaTaxi-Draft-Approvals'],
        'ticket': headers['X-YaTaxi-Draft-Tickets'],
        'external_draft_id': headers['X-YaTaxi-Draft-Id'],
        'approved_at': parser.parse(MOCK_NOW),
    }


def _get_closed_rule(cursor, rule_id):
    sql = """
    SELECT
        rule_id,
        TO_CHAR(timezone('UTC', ends_at),
            'YYYY-MM-DD"T"HH24:MI:SSOF":00"') as ends_at,
        changelog
    FROM fees.base_rule
    WHERE rule_id = %s;
    """
    cursor.execute(sql, (rule_id,))
    fields = [column.name for column in cursor.description]
    return dict(zip(fields, cursor.fetchone()))


@pytest.mark.parametrize(
    'query, status, expected_response',
    [
        (  # normal close
            {
                '_id': 'some_asymptotic_formula_commission_contract_id',
                'close_at': '2017-01-01T18:48:00.000000+03:00',
            },
            200,
            {
                'change_doc_id': (
                    'moscow:9a5d686550ba995093e667e50d3e6c4e6260a1d5'
                ),
                'data': {
                    '_id': 'some_asymptotic_formula_commission_contract_id',
                    'close_at': '2017-01-01T15:48:00+00:00',
                    'draft_id': 2,
                },
            },
        ),
        (  # close in future
            {
                '_id': 'some_asymptotic_formula_commission_contract_id',
                'close_at': '2018-01-01T18:48:00.000000+03:00',
            },
            400,
            {
                'code': 'INCORRECT_PARAMETERS',
                'message': 'Rule not exist or already closed',
            },
        ),
        (  # close without end field
            {
                '_id': (
                    'some_fixed_percent_commission_contract_id_'
                    'with_unlimited_end'
                ),
                'close_at': '2018-01-01T18:48:00.000000+03:00',
            },
            200,
            {
                'change_doc_id': (
                    'moscow:25da3eb4249041b8a6ebeeb6c83892acd2439eb2'
                ),
                'data': {
                    '_id': (
                        'some_fixed_percent_commission_contract_id_with_'
                        'unlimited_end'
                    ),
                    'close_at': '2018-01-01T15:48:00+00:00',
                    'draft_id': 2,
                },
            },
        ),
        (  # nonexistent
            {'_id': 'badc0de', 'close_at': '2018-01-01T18:48:00.000000+03:00'},
            400,
            {
                'code': 'INCORRECT_PARAMETERS',
                'message': 'Rule not exist or already closed',
            },
        ),
    ],
)
@pytest.mark.now(MOCK_NOW)
async def test_rules_close(
        taxi_billing_commissions,
        billing_commissions_postgres_db,
        query,
        status,
        expected_response,
):
    headers = {'X-YaTaxi-Draft-Author': 'author'}
    async with taxi_billing_commissions.capture_logs() as logs:
        response = await taxi_billing_commissions.post(
            'v1/rules/close', json=query, headers=headers,
        )
    assert response.status_code == status
    data = response.json()
    assert data == expected_response
    if status == 200:
        assert logs.select(level='WARNING') == []
        spec = _get_draft_spec(
            billing_commissions_postgres_db, data['data']['draft_id'],
        )
        assert spec == {
            'change_doc_id': data['change_doc_id'].split(':')[-1],
            'initiator': headers['X-YaTaxi-Draft-Author'],
            'approvers': '',
            'ticket': '',
            'external_draft_id': '',
            'approved_at': None,
        }


def _get_draft_spec(cursor, draft_spec_id):
    sql = """
    SELECT change_doc_id, initiator, ticket, approvers, external_draft_id,
            approved_at
    FROM fees.draft_spec WHERE id = %s;
    """
    cursor.execute(sql, (draft_spec_id,))
    fields = [column.name for column in cursor.description]
    return dict(zip(fields, cursor.fetchone() or ()))


@pytest.fixture(autouse=True)
def _fill_db(base_create_rules, a_base_rule):
    base_create_rules(
        a_base_rule(
            rule_id='some_asymptotic_formula_commission_contract_id',
            payment_type='cash',
            starts_at='2016-12-30T21:00:00Z',
            ends_at='2017-12-30T21:00:00Z',
        ),
        a_base_rule(
            rule_id=(
                'some_fixed_percent_commission_contract_id_with_unlimited_end'
            ),
            tariff='uberblack',
            tag='a_tag',
            starts_at='2016-12-31T20:00:00.0+03:00',
        ),
    )
