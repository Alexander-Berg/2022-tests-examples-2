import datetime
from typing import List
from typing import Optional
from typing import Tuple

import pytest
import pytz

from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools

# Audit group names
_FINANCIAL = 'financial'
_TECHNICAL = 'technical'
_ANALYTICAL = 'analytical'


class ReviewDecision:
    def __init__(
            self,
            decision: str = 'allowed',
            audit_groups: Optional[List[str]] = None,
            fields: Optional[List[Tuple[str, str, str]]] = None,
    ):
        self.decision = decision
        self.is_audit_required = bool(audit_groups)
        self.audit_groups = [
            {'name': group_name} for group_name in (audit_groups or list())
        ]
        self.fields = (
            [
                {'name': row[0], 'level': row[1], 'hint': row[2]}
                for row in fields
            ]
            if fields is not None
            else None
        )


# Placeholder [_INSERT_HERE_] is required
_TEXT_VALID = '[_INSERT_HERE_] SELECT 1;'
_TEXT_VALID_CHANGED = '[_INSERT_HERE_] SELECT 2;'
_TEXT_OUTDATED = 'SELECT 1;'
_TEXT_OUTDATED_CHANGED = 'SELECT 2;'
_PRAGMA_USER_SLOT = 'PRAGMA yT.UserSlots = "1234";\n'
_PRAGMA_POOL = 'PRAGMA YT.POOL = "my_pool";\n'
_PRAGMA_NON_REPLACED = 'PRAGMA yT.TmpFolder = "non-replaced";\n'
_PRAGMA_OPERATION_SPEC = 'PRAGMA yT.OperationSpec = "bla-bla-bla";\n'
_TEXT_PRAGMA_POOL_ONLY = _PRAGMA_POOL + _PRAGMA_NON_REPLACED + _TEXT_VALID
_TEXT_PRAGMAS = (
    _PRAGMA_USER_SLOT
    + _PRAGMA_POOL
    + _PRAGMA_NON_REPLACED
    + _PRAGMA_OPERATION_SPEC
    + _TEXT_VALID
)
_NAME_INVALID = ' bad[symbols?!] and lead-spaces '
_NAME_VALID = 'Only-.G00d symbols___'

_TASK_TICKET = 'TASKTICKET-12345'
_TASK_TICKET_CHANGED = 'TASKTICKET-12346'

# Was deprecated
_SYNTAX_OUTDATED = 'SQL'

_NOW = datetime.datetime.now(pytz.utc)
_HOUR_BEFORE = _NOW - datetime.timedelta(hours=1)
_HOUR_AFTER = _NOW + datetime.timedelta(hours=1)

_NOW_TZ = _NOW.astimezone(pytz.timezone('Europe/Moscow'))
_HOUR_BEFORE_TZ = _NOW_TZ - datetime.timedelta(hours=1)
_HOUR_AFTER_TZ = _NOW_TZ + datetime.timedelta(hours=1)
_TWO_HOURS_AFTER_TZ = _NOW_TZ + datetime.timedelta(hours=2)


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_tag_names(
            [
                tags_tools.TagName(1000, 'vip'),
                tags_tools.TagName(1001, 'frauder'),
            ],
        ),
        tags_tools.insert_topics(
            [
                tags_tools.Topic(1000, 'audited_topic', is_financial=True),
                tags_tools.Topic(1001, 'simple_topic', is_financial=False),
            ],
        ),
        tags_tools.insert_relations(
            [tags_tools.Relation(1000, 1000), tags_tools.Relation(1001, 1001)],
        ),
        tags_tools.insert_providers(
            [
                tags_tools.Provider.from_id(1000),
                tags_tools.Provider.from_id(1001),
                tags_tools.Provider.from_id(1002),
                tags_tools.Provider.from_id(1003, is_active=False),
                tags_tools.Provider(
                    provider_id=1004,
                    name='reserved',
                    desc='reserved',
                    is_active=False,
                ),
                tags_tools.Provider.from_id(1005),
            ],
        ),
        yql_tools.insert_queries(
            [
                yql_tools.Query(
                    name='enabled_valid',
                    provider_id=1000,
                    tags=['frauder'],
                    query=_TEXT_VALID,
                    enabled=True,
                    tags_limit=100,
                ),
                yql_tools.Query(
                    name='enabled_ticket_valid',
                    provider_id=1005,
                    tags=['frauder'],
                    query=_TEXT_VALID,
                    ticket=_TASK_TICKET,
                    enabled=True,
                    tags_limit=100,
                ),
                yql_tools.Query(
                    name='enabled_financial',
                    provider_id=1001,
                    tags=['vip'],
                    query=_TEXT_VALID,
                    enabled=True,
                    ticket=_TASK_TICKET,
                    tags_limit=100,
                ),
                yql_tools.Query(
                    name='enabled_outdated with bad name!',
                    provider_id=1002,
                    tags=['frauder'],
                    query=_TEXT_OUTDATED,
                    syntax=_SYNTAX_OUTDATED,
                    enabled=True,
                    ticket=_TASK_TICKET,
                    tags_limit=None,
                ),
                yql_tools.Query(
                    name='disabled_outdated_financial',
                    provider_id=1003,
                    tags=['frauder', 'vip'],
                    query=_TEXT_OUTDATED,
                    enabled=False,
                    tags_limit=None,
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'query, expected_response',
    [
        pytest.param(
            yql_tools.Query(
                name='enabled_valid',
                provider_id=1000,
                tags=['frauder'],
                query=_TEXT_VALID,
                enabled=True,
                ticket=_TASK_TICKET,
                tags_limit=100,
            ),
            ReviewDecision(decision='allowed'),
            id='no-changes',
        ),
        pytest.param(
            yql_tools.Query(
                name='enabled_valid',
                provider_id=1000,
                tags=['frauder'],
                query=_TEXT_VALID_CHANGED,
                enabled=True,
                ticket=_TASK_TICKET,
                tags_limit=100,
            ),
            ReviewDecision(decision='allowed'),
            id='allow-changes-without-audit',
        ),
        pytest.param(
            yql_tools.Query(
                name='enabled_valid',
                provider_id=1000,
                tags=['frauder', 'vip'],
                query=_TEXT_VALID,
                enabled=True,
                ticket=_TASK_TICKET,
                tags_limit=100,
            ),
            ReviewDecision(decision='allowed', audit_groups=[_FINANCIAL]),
            id='allow-changes-with-audit',
        ),
        pytest.param(
            yql_tools.Query(
                name='enabled_outdated with bad name!',
                provider_id=1001,
                tags=['frauder'],
                query=_TEXT_OUTDATED_CHANGED,
                syntax=_SYNTAX_OUTDATED,
                enabled=True,
                ticket=_TASK_TICKET,
                tags_limit=100,
            ),
            ReviewDecision(decision='denied'),
            id='deny-outdated-params-changing',
        ),
        pytest.param(
            yql_tools.Query(
                name='enabled_outdated with bad name!',
                provider_id=1001,
                tags=['frauder'],
                query=_TEXT_OUTDATED_CHANGED,
                syntax=_SYNTAX_OUTDATED,
                enabled=False,
                tags_limit=100,
            ),
            ReviewDecision(decision='denied'),
            id='deny-outdated-params-changing-while-disabling-query',
        ),
        pytest.param(
            yql_tools.Query(
                name='enabled_outdated with bad name!',
                provider_id=1001,
                tags=['frauder'],
                query=_TEXT_OUTDATED,
                syntax=_SYNTAX_OUTDATED,
                ticket=_TASK_TICKET,
                enabled=False,
                tags_limit=None,
            ),
            ReviewDecision(decision='allowed'),
            id='allow-disabling-outdated-query',
        ),
        pytest.param(
            yql_tools.Query(
                name='disabled_outdated_financial',
                provider_id=1003,
                tags=['frauder'],
                query=_TEXT_OUTDATED_CHANGED,
                syntax=_SYNTAX_OUTDATED,
                enabled=False,
                ticket=_TASK_TICKET,
                tags_limit=100,
            ),
            ReviewDecision(decision='denied', audit_groups=[_FINANCIAL]),
            id='deny-outdated-params-changing-for-disabled-query',
        ),
        pytest.param(
            yql_tools.Query(
                name='disabled_outdated_financial',
                provider_id=1003,
                tags=['frauder', 'vip'],
                query=_TEXT_VALID_CHANGED,
                enabled=True,
                ticket=_TASK_TICKET,
                tags_limit=100,
            ),
            ReviewDecision(decision='allowed', audit_groups=[_FINANCIAL]),
            id='allow-fixing-outdated-params-and-enabling-query',
        ),
        pytest.param(
            yql_tools.Query(
                name='enabled_valid',
                provider_id=1000,
                tags=['frauder'],
                query=_TEXT_VALID,
                ticket=_TASK_TICKET,
                enabled=True,
                tags_limit=100,
            ),
            ReviewDecision(decision='allowed'),
            id='allow-ticket-set',
        ),
        pytest.param(
            yql_tools.Query(
                name='enabled_ticket_valid',
                provider_id=1000,
                tags=['frauder'],
                query=_TEXT_VALID,
                ticket=_TASK_TICKET_CHANGED,
                enabled=True,
                tags_limit=100,
            ),
            ReviewDecision(decision='allowed'),
            id='allow-ticket-change',
        ),
        pytest.param(
            yql_tools.Query(
                name=_NAME_VALID,
                provider_id=1004,
                tags=['frauder'],
                query=_TEXT_VALID,
                ticket=_TASK_TICKET_CHANGED,
                enabled=True,
                tags_limit=100,
            ),
            ReviewDecision(decision='allowed'),
            id='allow new query with valid name',
        ),
        pytest.param(
            yql_tools.Query(
                name=_NAME_INVALID,
                provider_id=1004,
                tags=['frauder'],
                query=_TEXT_VALID,
                ticket=_TASK_TICKET_CHANGED,
                enabled=True,
                tags_limit=100,
            ),
            ReviewDecision(decision='denied'),
            id='deny new query with invalid name',
        ),
        pytest.param(
            yql_tools.Query(
                name='enabled_ticket_valid',
                provider_id=1005,
                tags=['frauder'],
                query=_TEXT_VALID,
                enabled=True,
                tags_limit=100,
            ),
            ReviewDecision(decision='denied'),
            id='deny-ticket-unset',
        ),
        pytest.param(
            yql_tools.Query(
                name='enabled_new_query',
                provider_id=-1,
                tags=['frauder'],
                query=_TEXT_VALID,
                enabled=True,
                tags_limit=100,
            ),
            ReviewDecision(decision='denied'),
            id='deny-no-ticket-set',
        ),
        pytest.param(
            yql_tools.Query(
                name='enabled_new_query',
                provider_id=-1,
                tags=['frauder'],
                query=_TEXT_VALID,
                ticket=_TASK_TICKET_CHANGED,
                enabled=True,
                tags_limit=None,
            ),
            ReviewDecision(decision='denied'),
            id='deny-no-tags_limit-set',
        ),
        pytest.param(
            yql_tools.Query(
                name='enabled_ticket_valid',
                provider_id=1000,
                tags=['frauder'],
                query=_TEXT_PRAGMA_POOL_ONLY,
                ticket=_TASK_TICKET,
                enabled=True,
                tags_limit=100,
            ),
            ReviewDecision(
                decision='allowed',
                fields=[
                    (
                        'query',
                        'warning',
                        (
                            'Pragma '
                            + _PRAGMA_POOL
                            + ' can be replaced by service.'
                        ),
                    ),
                ],
            ),
            id='allow-one-pragma-replace',
        ),
        pytest.param(
            yql_tools.Query(
                name='enabled_ticket_valid',
                provider_id=1000,
                tags=['frauder'],
                query=_TEXT_PRAGMAS,
                ticket=_TASK_TICKET,
                enabled=True,
                tags_limit=100,
            ),
            ReviewDecision(
                decision='allowed',
                fields=[
                    (
                        'query',
                        'warning',
                        (
                            'Some pragmas can be overwritten by the service: '
                            + _PRAGMA_USER_SLOT
                            + _PRAGMA_POOL
                            + _PRAGMA_OPERATION_SPEC
                            + '.'
                        ),
                    ),
                ],
            ),
            id='allow-some-pragmas-replace',
        ),
    ],
)
async def test_review(
        taxi_tags, query: yql_tools.Query, expected_response: ReviewDecision,
):
    await query.perform_review_request(
        taxi_tags=taxi_tags,
        login='last-modifier-login',
        expected_decision=expected_response.decision,
        expected_audit_required=expected_response.is_audit_required,
        expected_audit_groups=expected_response.audit_groups,
        expected_fields=expected_response.fields,
    )


@pytest.mark.nofilldb()
@pytest.mark.config(TAGS_YQL_MINIMAL_EXECUTION_INTERVAL={'__default__': 10})
@pytest.mark.parametrize(
    'query_diff, expected_response',
    [
        pytest.param({}, ReviewDecision(), id='no-rules'),
        pytest.param(
            {},
            ReviewDecision(audit_groups=[_TECHNICAL]),
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_if_ttl_is_more_than_days': 90,
                    },
                ),
            ],
            id='audit-for-query-without-ttl-specified',
        ),
        pytest.param(
            dict(disable_at=_HOUR_AFTER),
            ReviewDecision(),
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_if_ttl_is_more_than_days': 90,
                    },
                ),
            ],
            id='query-passed-ttl-check',
        ),
        pytest.param(
            dict(period=360, syntax='SQLv1'),
            ReviewDecision(audit_groups=[_TECHNICAL]),
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_if_period_is_less_than_seconds': {
                            '__default__': 3600,
                            'CLICKHOUSE': 180,
                        },
                    },
                ),
            ],
            id='audit-for-query-with-short-period-SQLv1',
        ),
        pytest.param(
            dict(period=360, syntax='CLICKHOUSE'),
            ReviewDecision(),
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_if_period_is_less_than_seconds': {
                            '__default__': 3600,
                            'CLICKHOUSE': 180,
                        },
                    },
                ),
            ],
            id='query-passes-period-check',
        ),
        pytest.param(
            dict(disable_at=_HOUR_AFTER),
            ReviewDecision(audit_groups=[_TECHNICAL]),
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_if_ttl_in_ranges': {
                            'ranges': [
                                {
                                    'begin': _HOUR_BEFORE_TZ.isoformat(),
                                    'end': _NOW_TZ.isoformat(),
                                    'name': 'unimportant range',
                                },
                                {
                                    'begin': _HOUR_AFTER_TZ.isoformat(),
                                    'end': _TWO_HOURS_AFTER_TZ.isoformat(),
                                    'name': 'feature freeze',
                                },
                            ],
                        },
                    },
                ),
            ],
            id='audit-for-query-with-forbidden-ttl-range',
        ),
        pytest.param(
            dict(disable_at=_NOW_TZ),
            ReviewDecision(),
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_if_ttl_in_ranges': {
                            'ranges': [
                                {
                                    'begin': _HOUR_BEFORE_TZ.isoformat(),
                                    'end': _NOW_TZ.isoformat(),
                                    'name': 'unimportant range',
                                },
                                {
                                    'begin': _NOW_TZ.isoformat(),
                                    'end': _HOUR_AFTER_TZ.isoformat(),
                                    'name': 'feature freeze',
                                },
                            ],
                        },
                    },
                ),
            ],
            id='query-passes-forbidden-ttl-check',
        ),
        pytest.param(
            dict(tags=['frauder', 'german_speaker']),
            ReviewDecision(audit_groups=['german-speaking']),
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'product_audit_rules': [
                            {
                                'name': 'german-speaking',
                                'title': 'German skeaking club',
                                'tag_names': ['frauder', 'german_speaker'],
                            },
                        ],
                    },
                ),
            ],
            id='product-audit-rule',
        ),
        pytest.param(
            dict(tags=['frauder', 'german_speaker']),
            ReviewDecision(audit_groups=['antifraud']),
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'product_audit_rules': [
                            {
                                'name': 'antifraud',
                                'title': 'Antifraud',
                                'tag_names': [
                                    'frauder',
                                    'punisher',
                                    'violence',
                                ],
                            },
                            {
                                'name': 'german-speaking',
                                'title': 'German skeaking club',
                                'tag_names': ['frauder', 'german_speaker'],
                            },
                        ],
                    },
                ),
            ],
            id='first-product-audit-rule-matched',
        ),
        pytest.param(
            dict(tags=['frauder']),
            ReviewDecision(audit_groups=[_TECHNICAL, 'antifraud']),
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'product_audit_rules': [
                            {
                                'name': 'antifraud',
                                'title': 'Antifraud',
                                'tag_names': [
                                    'frauder',
                                    'punisher',
                                    'violence',
                                ],
                            },
                        ],
                        'require_audit_if_ttl_is_more_than_days': 90,
                    },
                ),
            ],
            id='technical-and-product-audit-groups',
        ),
        pytest.param(
            dict(tags_limit=None),
            ReviewDecision(decision='denied'),
            id='removed-tags-limits',
        ),
        pytest.param(
            dict(tags_limit=100),
            ReviewDecision(audit_groups=[_TECHNICAL]),
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_if_tags_limit_is_more_than_value': 99,
                    },
                ),
            ],
            id='tags-limit-over',
        ),
        pytest.param(
            dict(tags_limit=100),
            ReviewDecision(audit_groups=[_TECHNICAL]),
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_for_topics_or_entity_types': {
                            'by_entity_types': {'dbid_uuid': 99},
                        },
                    },
                ),
            ],
            id='tags-limit-over-by-entity-type',
        ),
        pytest.param(
            dict(tags_limit=100),
            ReviewDecision(audit_groups=[_TECHNICAL]),
            marks=[
                pytest.mark.config(
                    TAGS_YQL_COUNT_LIMITS={
                        '__default__': {
                            '__default__': 10000,
                            'ordinary_name': 100,
                        },
                    },
                ),
            ],
            id='tags-limit-double-set',
        ),
        pytest.param(
            dict(tags_limit=100),
            ReviewDecision(),
            marks=[
                pytest.mark.config(
                    TAGS_YQL_COUNT_LIMITS={
                        '__default__': {'__default__': 10000},
                    },
                ),
            ],
            id='tags-limit-pass',
        ),
        pytest.param(
            dict(),
            ReviewDecision(audit_groups=[_ANALYTICAL]),
            marks=[
                pytest.mark.pgsql(
                    'tags',
                    queries=[
                        tags_tools.insert_tag_names(
                            [tags_tools.TagName(100, 'ordinary_tag')],
                        ),
                        tags_tools.insert_topics(
                            [
                                tags_tools.Topic(
                                    100, 'topic', is_financial=False,
                                ),
                            ],
                        ),
                        tags_tools.insert_relations(
                            [tags_tools.Relation(100, 100)],
                        ),
                    ],
                ),
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={'analyst_audit_enabled': True},
                ),
            ],
            id='analyst-audit-enabled',
        ),
        pytest.param(
            dict(),
            ReviewDecision(),
            marks=[
                pytest.mark.pgsql(
                    'tags',
                    queries=[
                        tags_tools.insert_tag_names(
                            [tags_tools.TagName(100, 'ordinary_tag')],
                        ),
                        tags_tools.insert_topics(
                            [
                                tags_tools.Topic(
                                    100, 'topic', is_financial=False,
                                ),
                            ],
                        ),
                        tags_tools.insert_relations(
                            [tags_tools.Relation(100, 100)],
                        ),
                    ],
                ),
            ],
            id='analyst-audit-disabled',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_audit_required(
        taxi_tags, query_diff: dict, expected_response: ReviewDecision,
):
    query = yql_tools.Query(
        name='ordinary_name',
        provider_id=-1,
        tags=['ordinary_tag'],
        period=3600,
        syntax='SQLv1',
        ticket=_TASK_TICKET,
        disable_at=None,
        tags_limit=10,
    )
    for key, value in query_diff.items():
        query.__setattr__(key, value)

    await query.perform_review_request(
        taxi_tags=taxi_tags,
        login='last-modifier-login',
        expected_decision=expected_response.decision,
        expected_audit_required=expected_response.is_audit_required,
        expected_audit_groups=expected_response.audit_groups,
    )
