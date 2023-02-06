import datetime as dt
import json
import pathlib
import re
import uuid

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from billing_commissions_plugins import *  # noqa: F403 F401
import pytest

BILLING_COMMISSIONS_DB_NAME = 'billing_commissions'


@pytest.fixture
def billing_commissions_postgres_db(pgsql):
    return pgsql[BILLING_COMMISSIONS_DB_NAME].cursor()


@pytest.fixture(name='a_base_rule')
def _base_rule_builder():
    def _builder(
            rule_id=None,
            tariff_zone='moscow',
            tariff='econom',
            tag=None,
            payment_type=None,
            starts_at='2022-01-01T00:00:00+03:00',
            ends_at=None,
            rule_type='fixed_percent',
            fee=None,
            acquiring=0,
            agent=0,
            call_center=0,
            hiring=0,
            hiring_rent=0,
            hiring_age=0,
            taximeter=0,
            cancellation_percent=None,
            min_cost=0,
            max_cost=150000000,
            expired_cost=0,
            expired_percent=0,
            vat=12000,
            billing_values=None,
            branding_discounts=None,
            updated_at=None,
    ):
        fee = fee or {'percent': 1200}
        billing_values = billing_values or {
            'bcd': 300,
            'p_max': 300,
            'p_min': 60,
            'u_max': 30,
            'u_min': 420,
        }
        branding_discounts = branding_discounts or [
            {'marketing_level': ['sticker'], 'value': 3},
        ]
        return {
            'rule_id': rule_id or str(uuid.uuid4()),
            'tariff_zone': tariff_zone,
            'tariff': tariff,
            'tag': tag,
            'payment_type': payment_type,
            'starts_at': starts_at,
            'ends_at': ends_at,
            'time_zone': 'Europe/Moscow',
            'rule_type': rule_type,
            'fee': json.dumps(fee),
            'min_order_cost': min_cost,
            'max_order_cost': max_cost,
            'cancellation_percent': cancellation_percent,
            'vat': vat,
            'rates': json.dumps(
                {
                    'acp': acquiring,
                    'agp': agent,
                    'callcenter_commission_percent': call_center,
                    'hiring': {
                        'extra_percent': hiring,
                        'extra_percent_with_rent': hiring_rent,
                        'max_age_in_seconds': hiring_age,
                    },
                    'taximeter_payment': taximeter,
                },
            ),
            'billing_values': json.dumps(billing_values),
            'branding_discounts': json.dumps(branding_discounts),
            'expiration': json.dumps(
                {'cost': expired_cost, 'percent': expired_percent},
            ),
            'updated_at': updated_at,
        }

    return _builder


@pytest.fixture(name='base_create_drafts')
def _base_rules_drafts_inserter(billing_commissions_postgres_db):
    # pylint: disable=redefined-outer-name
    def _insert_drafts(*rules, change_doc_id=None, initiator=None):
        draft_id = _draft_spec_insert(
            billing_commissions_postgres_db,
            change_doc_id=change_doc_id,
            initiator=initiator,
        )
        _base_rule_drafts_insert(
            billing_commissions_postgres_db, draft_id, rules,
        )
        return draft_id

    return _insert_drafts


@pytest.fixture(name='base_create_rules')
def _base_rules_inserter(billing_commissions_postgres_db, base_create_drafts):
    # pylint: disable=redefined-outer-name
    def _create_rules(*rules):
        draft_id = base_create_drafts(*rules)
        _draft_spec_update(billing_commissions_postgres_db, draft_id)
        _base_rule_drafts_approve(billing_commissions_postgres_db, draft_id)
        _base_rule_set_updated_at(billing_commissions_postgres_db, rules)

    return _create_rules


def _draft_spec_insert(db, change_doc_id=None, initiator=None):
    sql = _load_sql('insert_draft_id.sql')
    db.execute(
        sql, (change_doc_id or 'auto_change_doc_id', initiator or '<auto>'),
    )
    return db.fetchone()[0]


def _draft_spec_update(db, draft_id):
    sql = _load_sql('draft_spec_update.sql')
    db.execute(
        sql,
        (
            '<TICKET>',
            '<approvers>',
            '<DRAFT>',
            '2000-01-01T00:00:00+03:00',
            draft_id,
        ),
    )


def _base_rule_drafts_insert(db, draft_id, rules):
    if not rules:
        return
    fields = [
        'rule_id',
        'tariff_zone',
        'tariff',
        'tag',
        'payment_type',
        'starts_at',
        'ends_at',
        'time_zone',
        'rule_type',
        'min_order_cost',
        'max_order_cost',
        'cancellation_percent',
        'vat',
        'fee',
        'rates',
        'billing_values',
        'branding_discounts',
        'expiration',
    ]
    values = [[r.get(f) for r in rules] for f in fields]
    sql = _load_sql('base_rule_draft_create.sql')
    db.execute(sql, [draft_id] + values)


def _base_rule_drafts_approve(db, draft_id):
    sql = _load_sql('base_rule_draft_approve.sql')
    db.execute(sql, (draft_id,))


def _base_rule_set_updated_at(db, rules):
    sql = 'UPDATE fees.base_rule SET updated_at = %s WHERE rule_id = %s'
    updated_at = [
        (r['rule_id'], r['updated_at'])
        for r in rules
        if r['updated_at'] is not None
    ]
    for rule_id, value in updated_at:
        db.execute(sql, [value, rule_id])


@pytest.fixture(name='a_rule')
def _rule_builder():
    def _builder(
            *,
            kind,
            fees,
            rule_id=None,
            starts_at='2022-01-01T00:00:00+03:00',
            ends_at=None,
            tariff_zone='moscow',
            tariff='econom',
            withdraw_from_driver_account=None,
            cost_min=None,
            cost_max=None,
            tag=None,
            payment_type=None,
            hiring_type=None,
            hiring_age=None,
            fine_code=None,
    ):
        return {
            'rule_id': rule_id or str(uuid.uuid4()),
            'kind': kind,
            'starts_at': dt.datetime.fromisoformat(starts_at),
            'ends_at': dt.datetime.fromisoformat(ends_at) if ends_at else None,
            'fees': json.dumps(fees),
            'tariff_zone': tariff_zone,
            'tariff': tariff,
            'withdraw_from_driver_account': withdraw_from_driver_account,
            'cost_min': cost_min,
            'cost_max': cost_max,
            'tag': tag,
            'payment_type': payment_type,
            'hiring_type': hiring_type,
            'hiring_age': hiring_age,
            'fine_code': fine_code,
        }

    return _builder


@pytest.fixture(name='create_drafts')
def _rules_drafts_inserter(billing_commissions_postgres_db):
    # pylint: disable=redefined-outer-name
    def _insert_drafts(*rules, change_doc_id=None, initiator=None):
        draft_id = _draft_spec_insert(
            billing_commissions_postgres_db,
            change_doc_id=change_doc_id,
            initiator=initiator,
        )
        _rule_drafts_insert(billing_commissions_postgres_db, draft_id, rules)
        return draft_id

    return _insert_drafts


def _rule_drafts_insert(db, draft_id, rules):
    if not rules:
        return
    sql = _load_sql('insert_draft_rule.sql')
    for rule in rules:
        values = [
            rule['rule_id'],
            rule['kind'],
            rule['starts_at'],
            rule['ends_at'],
            rule['starts_at'],  # for COALESCE
            draft_id,
            rule['fees'],
            rule['tariff_zone'],
            rule['tariff'],
            rule['withdraw_from_driver_account'],
            rule['cost_min'],
            rule['cost_max'],
            rule['tag'],
            rule['payment_type'],
            rule['hiring_type'],
            rule['hiring_age'],
            rule['fine_code'],
        ]
        db.execute(sql, values)


@pytest.fixture(name='create_rules')
def _rules_inserter(billing_commissions_postgres_db, create_drafts):
    # pylint: disable=redefined-outer-name
    def _create_rules(*rules):
        draft_id = create_drafts(*rules)
        _rule_drafts_approve(billing_commissions_postgres_db, draft_id)

    return _create_rules


def _rule_drafts_approve(db, draft_id):
    values = [
        ('draft_id', draft_id),
        ('iniitiator', 'pytest'),
        ('ticket', '<TICKET>'),
        ('close_desc', []),
        ('create_desc', ''),
        ('rules_to_close', []),
        ('approvers', '<approvers>'),
        ('external_draft_id', 11111),
    ]
    sql = _load_sql('apply_draft_for_rules.sql', params=[v[0] for v in values])
    db.execute(sql, dict(values))


def _load_sql(fname, params=None):
    name = pathlib.Path(__file__).parent.absolute() / f'../../src/sql/{fname}'
    with open(name) as script:
        sql = re.sub(r'/\*.*\*/', '', script.read(), flags=re.DOTALL)
        sql = re.sub(r'--.*', '', sql)
        if params is None:
            sql = re.sub(r'\$\d+', '%s', sql)
        else:
            for i, param in enumerate(params or [], 1):
                sql = re.sub(rf'\${i}\b', f'%({param})s', sql)
    return sql.strip()
