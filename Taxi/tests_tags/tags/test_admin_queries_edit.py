# pylint: disable=C0302
import datetime
from typing import List
from typing import Optional

import pytest

from tests_tags.tags import acl_tools
from tests_tags.tags import constants
from tests_tags.tags import yql_tools

_NOW = datetime.datetime.now()
_HOUR_BEFORE = _NOW - datetime.timedelta(hours=1)
_HOUR_AFTER = _NOW + datetime.timedelta(hours=1)

_QUERY_WITHOUT_PLACEHOLDER = 'SELECT * FROM table;'
_QUERY_WITH_MULTI_PLACEHOLDERS = (
    '[_INSERT_HERE_] SELECT * FROM table; [_INSERT_HERE_]'
)
_QUERY = '[_INSERT_HERE_] SELECT * FROM table;'
_SQLV1 = 'SQLv1'
_CLICKHOUSE = 'CLICKHOUSE'
_SQLV0 = 'SQL'
_DBID_UUID = 'dbid_uuid'
_DRIVER_LICENSE = 'driver_license'
_CAR_NUMBER = 'car_number'
_TAGS = ['tag_name_1000', 'tag_name_1001']
_USUAL_TOPICS = ['topic_10']
_FINANCIAL_TAGS = {'tag_name_1002_financial'}
_FINANCIAL_TOPICS = {'topic_20_financial'}
_LOGIN = 'science-intensive'
_INITIAL_AUTHOR = 'author'
_TASK_TICKET = 'TASKTICKET-1234'
_AUDIT_NOT_REQUIRED = 'not_required'

_EXISTING_ID = '1000_active'
_EXISTING_FINANCIAL_ID = '1002_financial'
_EXISTING_PROVIDER_ID = '1001_disabled'
_EXISTING_DRIVER_LICENSE = 'query_with_driver_license'
_EXISTING_DYNAMIC = 'dynamic_entity_types'
_EXISTING_CLICKHOUSE_ID = 'clickhouse_query'
_EXISTING_NO_TICKET_ID = ' no_ticket_query"with]bad!name '


def _find_query(db, query_name: str):
    cursor = db.cursor()
    cursor.execute(
        f'SELECT name, enabled, tags, query, syntax, entity_type, '
        f'last_modifier, custom_execution_time, disable_at, ticket, '
        f'tags_limit '
        f'FROM service.queries WHERE name=\'{query_name}\'',
    )

    rows = list(row for row in cursor)
    assert len(rows) <= 1
    return rows[0] if rows else None


class CreateParams:
    def __init__(
            self,
            login: Optional[str] = _LOGIN,
            query_name: str = 'whatever',
            query: str = _QUERY,
            period: int = 1800,
            syntax: str = _SQLV1,
            tags: Optional[List[str]] = None,
            entity_type: Optional[str] = _DBID_UUID,
            enabled: bool = True,
            custom_execution_time: Optional[datetime.datetime] = None,
            disable_at: Optional[datetime.datetime] = None,
            ticket: Optional[str] = _TASK_TICKET,
            tags_limit: Optional[int] = 10,
    ):
        self.login = login
        self.query_name = query_name
        self.query = query
        self.period = period
        self.syntax = syntax
        self.tags = tags or []
        self.entity_type = entity_type
        self.enabled = enabled
        self.custom_execution_time = custom_execution_time
        self.disable_at = disable_at
        self.ticket = ticket
        self.tags_limit = tags_limit

    def values(self):
        return (
            self.query_name,
            self.enabled,
            self.tags,
            self.query,
            self.syntax,
            self.entity_type,
            self.login,
            self.custom_execution_time,
            self.disable_at,
            self.ticket,
            self.tags_limit,
        )


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['queries_create_initial.sql'])
@pytest.mark.parametrize('use_financial_handler', [True, False])
@pytest.mark.parametrize(
    'expected_code, params',
    [
        pytest.param(
            400,
            CreateParams(period=60),
            id='forbid creating disabled SQLv1 query without tags',
        ),
        pytest.param(
            400,
            CreateParams(period=60, syntax=_SQLV0, enabled=False),
            id='forbid creating disabled SQLv0 query',
        ),
        pytest.param(
            400,
            CreateParams(),
            id='forbid creating enabled SQLV1 query without tags',
        ),
        pytest.param(
            200,
            CreateParams(period=60, enabled=False, tags=_TAGS),
            id='create disabled SQLv1 query with tags',
        ),
        pytest.param(
            400,
            CreateParams(period=60, syntax=_SQLV0, tags=_TAGS, enabled=False),
            id='create disabled SQLv0 query with tags rejected',
        ),
        pytest.param(
            200,
            CreateParams(tags=_TAGS),
            id='create enabled SQLv1 query with tags',
        ),
        pytest.param(
            400,
            CreateParams(tags=_TAGS, tags_limit=None),
            id='forbid creating query without tags limit',
        ),
        pytest.param(
            200,
            CreateParams(tags=_TAGS, entity_type=None),
            id='create SQLv1 query with dynamic entity_types',
        ),
        pytest.param(400, CreateParams(tags=[]), id='forbid empty tags list'),
        pytest.param(
            400, CreateParams(login=None, tags=_TAGS), id='no login in header',
        ),
        pytest.param(
            400, CreateParams(period=0, tags=_TAGS), id='period is 0',
        ),
        pytest.param(
            400,
            CreateParams(period=59, tags=_TAGS),
            id='period is less than config minimum',
        ),
        pytest.param(
            400,
            CreateParams(query_name='query_name', period=1799, tags=_TAGS),
            id='period is less than config default',
        ),
        pytest.param(
            400,
            CreateParams(tags=_TAGS, entity_type='bad_type'),
            id='invalid entity type',
        ),
        pytest.param(
            400,
            CreateParams(syntax='yql', tags=_TAGS),
            id='invalid sql syntax',
        ),
        pytest.param(
            409,
            CreateParams(query_name=_EXISTING_ID, tags=_TAGS),
            id='query already exists',
        ),
        pytest.param(
            409,
            CreateParams(query_name=_EXISTING_PROVIDER_ID, tags=_TAGS),
            id='provider already exists',
        ),
        pytest.param(
            200,
            CreateParams(
                query_name='provider_id_',
                tags=_TAGS,
                custom_execution_time=_HOUR_AFTER,
            ),
            id='with custom execution time',
        ),
        pytest.param(
            400,
            CreateParams(query_name='[]', tags=_TAGS),
            id='bad query name',
        ),
        pytest.param(
            400,
            CreateParams(query_name=' abc', tags=_TAGS),
            id='bad query name',
        ),
        pytest.param(
            400,
            CreateParams(query_name='abc ', tags=_TAGS),
            id='bad query name',
        ),
        pytest.param(
            400,
            CreateParams(query_name='[]', tags=_TAGS),
            id='bad query name',
        ),
        pytest.param(
            400,
            CreateParams(query_name='abc!', tags=_TAGS),
            id='bad query name',
        ),
        pytest.param(
            200,
            CreateParams(
                query_name='_G00d. query- name__',
                tags=_TAGS,
                custom_execution_time=_HOUR_BEFORE,
            ),
            id='custom execution time is before now',
        ),
        pytest.param(
            200,
            CreateParams(
                query_name='provider_id__', tags=_TAGS, disable_at=_HOUR_AFTER,
            ),
            id='disable time is after now',
        ),
        pytest.param(
            400,
            CreateParams(query_name='provider_id__', tags=_TAGS, ticket=None),
            id='ticket is not set',
        ),
        pytest.param(
            400,
            CreateParams(period=60, tags=['a' * 256]),
            id='tag name too long',
        ),
        pytest.param(
            400, CreateParams(period=60, tags=['-?!']), id='bad tag name',
        ),
        pytest.param(
            400, CreateParams(period=60, tags=['']), id='empty tag name',
        ),
        pytest.param(
            400,
            CreateParams(
                query_name='abracadabra',
                query=_QUERY_WITHOUT_PLACEHOLDER,
                syntax=_CLICKHOUSE,
                tags=_TAGS,
            ),
            id='can\'t create clickhouse query without placeholder',
        ),
        pytest.param(
            400,
            CreateParams(
                query_name='abracadabra',
                query=_QUERY_WITH_MULTI_PLACEHOLDERS,
                syntax=_CLICKHOUSE,
                tags=_TAGS,
            ),
            id='can\'t create clickhouse query with multi placeholder',
        ),
        pytest.param(
            400,
            CreateParams(
                query_name='abracadabra',
                syntax=_CLICKHOUSE,
                tags=_TAGS,
                entity_type=None,
            ),
            id='can\'t create clickhouse query without entity_type',
        ),
        pytest.param(
            400,
            CreateParams(
                query_name='abracadabra',
                query=_QUERY_WITHOUT_PLACEHOLDER,
                tags=_TAGS,
            ),
            id='can\'t create sqlv1 query without placeholder',
        ),
        pytest.param(
            400,
            CreateParams(
                query_name='abracadabra',
                query=_QUERY_WITH_MULTI_PLACEHOLDERS,
                tags=_TAGS,
            ),
            id='can\'t create sqlv1 query with multi placeholder',
        ),
        pytest.param(
            400,
            CreateParams(query_name='', tags=_TAGS),
            id='empty query name',
        ),
        pytest.param(
            400,
            CreateParams(query_name='invalid:name', tags=_TAGS),
            id='invalid query name: colon symbol',
        ),
        pytest.param(
            400,
            CreateParams(query_name=' space_first', tags=_TAGS),
            id='invalid query name: first space symbol',
        ),
        pytest.param(
            400,
            CreateParams(tags=_TAGS, entity_type=_DRIVER_LICENSE),
            id='create enabled SQLV1 query with deprecated driver_license',
        ),
        pytest.param(
            400,
            CreateParams(tags=_TAGS, entity_type=_CAR_NUMBER),
            id='create enabled SQLV1 query with deprecated car_number',
        ),
        pytest.param(
            400,
            CreateParams(query_name='forbid_square[brackets]', tags=_TAGS),
            id='invalid query name: colon symbol',
        ),
    ],
)
@pytest.mark.config(
    TAGS_YQL_MINIMAL_EXECUTION_INTERVAL={'__default__': 1800, 'whatever': 60},
)
@pytest.mark.now(_NOW.isoformat())
async def test_create(
        taxi_tags,
        expected_code: int,
        params: CreateParams,
        use_financial_handler: bool,
        pgsql,
):
    query = yql_tools.Query(
        name=params.query_name,
        provider_id=-1,
        tags=params.tags,
        query=params.query,
        period=params.period,
        syntax=params.syntax,
        entity_type=params.entity_type,
        enabled=params.enabled,
        custom_execution_time=params.custom_execution_time,
        disable_at=params.disable_at,
        ticket=params.ticket,
        tags_limit=params.tags_limit,
    )
    await query.perform_edit_request(
        taxi_tags,
        'create',
        login=params.login,
        use_financial_handler=use_financial_handler,
        expected_code=expected_code,
    )

    if expected_code == 200:
        found = _find_query(pgsql['tags'], params.query_name)
        assert found is not None
        assert found == params.values()


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['queries_create_initial.sql'])
@pytest.mark.parametrize(
    'use_financial_handler',
    [True, False],
    ids=['using_financial_handler', 'using_common_handler'],
)
@pytest.mark.parametrize(
    'expected_code, expected_financial_code, acl_allowed, acl_enabled, '
    'login, tags, expected_topics, expected_audit_type',
    [
        pytest.param(
            200,
            200,
            True,
            True,
            constants.TEST_LOGIN,
            _TAGS,
            _USUAL_TOPICS,
            yql_tools.AuditType.Technical,
            id='allowed',
        ),
        pytest.param(
            403,
            403,
            False,
            True,
            constants.TEST_LOGIN,
            _TAGS,
            _USUAL_TOPICS,
            yql_tools.AuditType.Technical,
            id='prohibited',
        ),
        pytest.param(
            200,
            200,
            False,
            False,
            constants.TEST_LOGIN,
            _TAGS,
            _USUAL_TOPICS,
            yql_tools.AuditType.Technical,
            id='prohibited, but acl disabled',
        ),
        pytest.param(
            400,
            400,
            True,
            True,
            None,
            _TAGS + list(_FINANCIAL_TAGS),
            _USUAL_TOPICS + list(_FINANCIAL_TOPICS),
            yql_tools.AuditType.Financial,
            id='no login',
        ),
        pytest.param(
            403,
            200,
            True,
            True,
            constants.TEST_LOGIN,
            _TAGS + list(_FINANCIAL_TAGS),
            _USUAL_TOPICS + list(_FINANCIAL_TOPICS),
            yql_tools.AuditType.Financial,
            id='financial tags prohibited',
        ),
        pytest.param(
            400,
            400,
            False,
            True,
            constants.TEST_LOGIN,
            None,
            [],
            yql_tools.AuditType.Technical,
            id='denied without tags',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_create_acl(
        taxi_tags,
        expected_code: int,
        expected_financial_code: int,
        login: str,
        tags: List[str],
        expected_topics: List[str],
        expected_audit_type: yql_tools.AuditType,
        use_financial_handler: bool,
        pgsql,
        taxi_config,
        mockserver,
        acl_enabled: bool,
        acl_allowed: bool,
):
    _query_name = 'whatever'

    await acl_tools.toggle_acl(taxi_tags, taxi_config, acl_enabled)

    if acl_allowed:
        acl_tools.make_mock_acl_allowed(mockserver)
    else:
        acl_tools.make_mock_acl_prohibited(
            mockserver, constants.TEST_LOGIN, expected_topics, expected_topics,
        )

    expected_code = (
        expected_financial_code if use_financial_handler else expected_code
    )

    response = await yql_tools.edit_request(
        taxi_tags,
        'create',
        login=login,
        query_name=_query_name,
        query=_QUERY,
        period=1800,
        syntax=_SQLV1,
        tags=tags,
        ticket=_TASK_TICKET,
        entity_type=_DBID_UUID,
        enabled=True,
        use_financial_handler=use_financial_handler,
        audit_type=expected_audit_type,
        expected_code=expected_code,
        custom_execution_time=None,
        tags_limit=100,
    )

    assert response.status_code == expected_code

    if expected_code == 200:
        found = _find_query(pgsql['tags'], _query_name)
        assert found is not None


def _verify_process_in_yt_query(db, name: str):
    cursor = db.cursor()
    cursor.execute(
        'SELECT yql_processing_method FROM service.queries WHERE name=\''
        + name
        + '\';',
    )
    rows = list(row for row in cursor)
    assert len(rows) == 1
    assert rows[0][0] == 'yt_merge'


async def test_create_with_placeholder(taxi_tags, pgsql):
    response = await yql_tools.edit_request(
        taxi_tags,
        'create',
        login=_LOGIN,
        query_name='yql_with_placeholder',
        query=_QUERY,
        tags=['new_tag'],
        tags_limit=100,
        ticket=_TASK_TICKET,
    )
    assert response.status_code == 200
    _verify_process_in_yt_query(pgsql['tags'], 'yql_with_placeholder')


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['queries_create_initial.sql'])
@pytest.mark.parametrize(
    'use_financial_handler',
    [True, False],
    ids=['using_financial_handler', 'using_common_handler'],
)
@pytest.mark.parametrize(
    'tags, entity_type, audit_type, product_audit, analyst_audit,'
    'expected_code, expected_financial_code',
    [
        pytest.param(
            None,
            _DBID_UUID,
            None,
            None,
            None,
            400,
            400,
            id='not-tags-means-bad-request',
        ),
        pytest.param(
            _TAGS,
            _DBID_UUID,
            None,
            None,
            None,
            200,
            200,
            id='no-audit-required',
        ),
        pytest.param(
            list(_FINANCIAL_TAGS),
            _DBID_UUID,
            yql_tools.AuditType.Financial,
            None,
            None,
            403,
            200,
            id='financial-tags-found',
        ),
        pytest.param(
            list(_FINANCIAL_TAGS),
            _DBID_UUID,
            yql_tools.AuditType.FinancialAndTechnical,
            None,
            None,
            403,
            200,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_if_ttl_is_more_than_days': 90,
                    },
                ),
            ],
            id='financial-and-technical-review',
        ),
        pytest.param(
            list(_FINANCIAL_TAGS),
            _DBID_UUID,
            yql_tools.AuditType.Financial,
            'security',
            None,
            403,
            200,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'product_audit_rules': [
                            {
                                'name': 'security',
                                'title': 'Tests security team',
                                'topics': list(_FINANCIAL_TOPICS),
                            },
                        ],
                    },
                ),
            ],
            id='financial-and-product-reviews',
        ),
        pytest.param(
            list(_FINANCIAL_TAGS),
            _DBID_UUID,
            yql_tools.AuditType.FinancialAndTechnical,
            'security',
            None,
            403,
            200,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_if_ttl_is_more_than_days': 90,
                        'product_audit_rules': [
                            {
                                'name': 'security',
                                'title': 'Tests security team',
                                'topics': list(_FINANCIAL_TOPICS),
                            },
                        ],
                    },
                ),
            ],
            id='financial-technical-product-reviews',
        ),
        pytest.param(
            _TAGS,
            _DBID_UUID,
            yql_tools.AuditType.Technical,
            None,
            None,
            403,
            200,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_if_tags_limit_is_more_than_value': 99,
                        'require_audit_for_topics_or_entity_types': {},
                    },
                ),
            ],
            id='tags-limit-over',
        ),
        pytest.param(
            _TAGS,
            _DBID_UUID,
            yql_tools.AuditType.Technical,
            None,
            None,
            403,
            200,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_for_topics_or_entity_types': {
                            'by_entity_types': {
                                '__default__': 101,
                                'dbid_uuid': 99,
                            },
                        },
                    },
                ),
            ],
            id='tags-limit-over-by-entity-type',
        ),
        pytest.param(
            _TAGS,
            None,
            yql_tools.AuditType.Technical,
            None,
            None,
            403,
            200,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_for_topics_or_entity_types': {
                            'by_entity_types': {
                                '__default__': 99,
                                'dbid_uuid': 101,
                            },
                        },
                    },
                ),
            ],
            id='tags-limit-over-by-dynamic-entity-type',
        ),
        pytest.param(
            _TAGS,
            _DBID_UUID,
            yql_tools.AuditType.Technical,
            None,
            None,
            403,
            200,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_if_tags_limit_is_more_than_value': 101,
                        'require_audit_for_topics_or_entity_types': {
                            'by_topics': {'topic_10': 99, 'topic_1': 102},
                        },
                    },
                ),
            ],
            id='tags-limit-over-by-topic',
        ),
        pytest.param(
            _TAGS,
            _DBID_UUID,
            yql_tools.AuditType.Technical,
            None,
            None,
            403,
            200,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_COUNT_LIMITS={
                        '__default__': {'__default__': 10000, 'test': 100},
                    },
                ),
            ],
            id='tags-limit-double-set',
        ),
        pytest.param(
            _TAGS,
            _DBID_UUID,
            None,
            None,
            None,
            200,
            200,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_for_topics_or_entity_types': {
                            'by_entity_types': {'__default__': 101},
                        },
                    },
                    TAGS_YQL_COUNT_LIMITS={
                        '__default__': {'__default__': 10000},
                    },
                ),
            ],
            id='tags-limit-pass',
        ),
        pytest.param(
            _TAGS,
            _DBID_UUID,
            None,
            None,
            'default',
            403,
            200,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={'analyst_audit_enabled': True},
                ),
            ],
            id='analyst-audit-enabled',
        ),
        pytest.param(
            _TAGS,
            _DBID_UUID,
            None,
            None,
            None,
            200,
            200,
            id='analyst-audit-disabled',
        ),
    ],
)
async def test_create_security(
        taxi_tags,
        expected_code: int,
        expected_financial_code: int,
        tags: List[str],
        entity_type: Optional[str],
        audit_type: yql_tools.AuditType,
        product_audit: Optional[str],
        analyst_audit: Optional[str],
        use_financial_handler: bool,
        pgsql,
):
    expected_code = (
        expected_financial_code if use_financial_handler else expected_code
    )

    await yql_tools.edit_request(
        taxi_tags,
        'create',
        login=_LOGIN,
        query_name='test',
        tags=tags,
        audit_type=audit_type,
        product_audit=product_audit,
        analyst_audit=analyst_audit,
        enabled=True,
        use_financial_handler=use_financial_handler,
        expected_code=expected_code,
        query=_QUERY,
        entity_type=entity_type,
        ticket=_TASK_TICKET,
        tags_limit=100,
    )

    found = _find_query(pgsql['tags'], 'test')
    if expected_code == 200:
        assert found
    else:
        assert not found


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['queries_edit_initial.sql'])
@pytest.mark.parametrize(
    'financial', [True, False], ids=['financial', 'non_financial'],
)
async def test_query_not_found(taxi_tags, pgsql, financial):
    db = pgsql['tags']
    query_name = 'unknown_query_name'
    query = yql_tools.Query.find_by_name(db, query_name)
    assert query is None

    query = yql_tools.Query(
        name=query_name,
        provider_id=32167,
        tags=_TAGS,
        changed=_NOW,
        created=_NOW,
    )
    await query.perform_edit_request(
        taxi_tags,
        'edit',
        login='mordeth',
        expected_code=404,
        use_financial_handler=financial,
    )


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['queries_edit_initial.sql'])
@pytest.mark.parametrize(
    'financial', [True, False], ids=['financial', 'non_financial'],
)
@pytest.mark.parametrize(
    'expected_code, any_changes, query_name, params',
    [
        pytest.param(
            200,
            False,
            _EXISTING_ID,
            dict(
                query=_QUERY,
                period=3600,
                syntax=_SQLV1,
                tags=_TAGS,
                enabled=True,
            ),
            id='initial state, the same changes made',
        ),
        pytest.param(
            200,
            False,
            _EXISTING_ID,
            dict(),
            id='initial state, no changes made',
        ),
        pytest.param(
            400,
            False,
            _EXISTING_NO_TICKET_ID,
            dict(),
            id='initial state, no changes made (no ticket)',
        ),
        pytest.param(
            200,
            True,
            _EXISTING_NO_TICKET_ID,
            dict(ticket=_TASK_TICKET),
            id='set ticket only',
        ),
        pytest.param(
            400, False, _EXISTING_ID, dict(ticket=None), id='remove ticket',
        ),
        pytest.param(
            200,
            True,
            _EXISTING_ID,
            dict(ticket=_TASK_TICKET),
            id='change ticket',
        ),
        pytest.param(
            200,
            True,
            _EXISTING_ID,
            dict(tags_limit=123456),
            id='set tags limit',
        ),
        pytest.param(
            200,
            True,
            _EXISTING_ID,
            dict(tags_limit=12345),
            id='change tags limit',
        ),
        pytest.param(
            400,
            True,
            _EXISTING_ID,
            dict(tags_limit=None),
            id='clean tags limit',
        ),
        pytest.param(
            200,
            True,
            _EXISTING_ID,
            dict(
                query=_QUERY,
                period=3600,
                syntax=_SQLV1,
                tags=_TAGS,
                enabled=False,
            ),
            id='disabling query',
        ),
        pytest.param(
            200,
            True,
            _EXISTING_ID,
            dict(
                query=_QUERY,
                period=3600,
                syntax=_SQLV1,
                tags=['d'],
                enabled=True,
            ),
            id='changing tags list',
        ),
        pytest.param(
            400,
            True,
            _EXISTING_ID,
            dict(
                query=_QUERY,
                period=3600,
                syntax=_SQLV1,
                tags=[],
                enabled=False,
            ),
            id='changing tags list to empty one is NOT allowed',
        ),
        pytest.param(
            200,
            True,
            _EXISTING_ID,
            dict(query='use hahn; [_INSERT_HERE_]'),
            id='changing query',
        ),
        pytest.param(
            400,
            True,
            _EXISTING_ID,
            dict(syntax=_SQLV0, enabled=True),
            id='changing syntax to lower version should be forbidden',
        ),
        pytest.param(
            400,
            True,
            _EXISTING_PROVIDER_ID,
            dict(syntax=_SQLV1, enabled=True),
            id='only changing syntax to new',
        ),
        pytest.param(
            400,
            True,
            _EXISTING_PROVIDER_ID,
            dict(query='use hahn;', enabled=True),
            id='changing query but not changing old syntax',
        ),
        pytest.param(
            200,
            True,
            _EXISTING_PROVIDER_ID,
            dict(enabled=False),
            id='disabling query with old syntax',
        ),
        pytest.param(
            200,
            True,
            _EXISTING_PROVIDER_ID,
            dict(syntax=_SQLV0, enabled=False),
            id='disabling query without changing old syntax',
        ),
        pytest.param(
            400,
            True,
            _EXISTING_ID,
            dict(syntax=_SQLV0, enabled=False),
            id='disabling query with changing syntax to old',
        ),
        pytest.param(
            200, True, _EXISTING_ID, dict(enabled=False), id='only disabling',
        ),
        pytest.param(
            200,
            True,
            'beautiful_query_name',
            dict(enabled=False),
            id='only disabling query with name different from provider name',
        ),
        pytest.param(
            200,
            True,
            'beautiful_query_name',
            dict(login='l', enabled=False),
            id=(
                'disable query with different name from provider '
                'name and update modifier'
            ),
        ),
        pytest.param(
            200,
            True,
            'beautiful_query_name',
            dict(login=_INITIAL_AUTHOR, enabled=False),
            id=(
                'disable query with different name from provider name'
                'and update modifier'
            ),
        ),
        pytest.param(
            200,
            True,
            _EXISTING_ID,
            dict(custom_execution_time=_HOUR_AFTER),
            id='update custom_execution_time',
        ),
        pytest.param(
            200,
            True,
            _EXISTING_ID,
            dict(custom_execution_time=_HOUR_BEFORE),
            id='update custom_execution_time before now',
        ),
        pytest.param(
            200,
            True,
            _EXISTING_ID,
            dict(disable_at=_HOUR_AFTER),
            id='update disable_at',
        ),
        pytest.param(
            200,
            True,
            _EXISTING_ID,
            dict(ticket='TASKTICKET-1234'),
            id='update ticket',
        ),
        pytest.param(
            400,
            True,
            _EXISTING_ID,
            dict(query=_QUERY_WITHOUT_PLACEHOLDER),
            id='change query, remove placeholder from there',
        ),
        pytest.param(
            400,
            True,
            _EXISTING_ID,
            dict(query=_QUERY_WITH_MULTI_PLACEHOLDERS),
            id='change query, double placeholder',
        ),
        pytest.param(
            200,
            True,
            'query_with_custom_execution_time',
            dict(custom_execution_time=None),
            id='disable custom_execution_time',
        ),
        pytest.param(
            400,
            True,
            _EXISTING_ID,
            dict(tags=['a' * 256]),
            id='tag name too long',
        ),
        pytest.param(
            400, True, _EXISTING_ID, dict(tags=['абвгде']), id='bad tag name',
        ),
        pytest.param(
            400,
            True,
            _EXISTING_PROVIDER_ID,
            dict(period=1799),
            id='updated query period is more than default',
        ),
        pytest.param(
            200,
            True,
            _EXISTING_ID,
            dict(period=60),
            id='updated query period doesn\'t more config value',
        ),
        pytest.param(
            400,
            True,
            _EXISTING_ID,
            dict(entity_type=_DRIVER_LICENSE),
            id='updated entity type to deprecated value',
        ),
        pytest.param(
            400,
            True,
            _EXISTING_ID,
            dict(entity_type=_DRIVER_LICENSE, enabled=False),
            id='updated query to deprecated entity type and disabled',
        ),
        pytest.param(
            200,
            True,
            _EXISTING_DRIVER_LICENSE,
            dict(entity_type=_DRIVER_LICENSE, enabled=False),
            id='updated query with deprecated entity type to disabled',
        ),
        pytest.param(
            400,
            False,
            _EXISTING_DRIVER_LICENSE,
            dict(entity_type=_DRIVER_LICENSE),
            id='no changes in query with deprecated entity type',
        ),
        pytest.param(
            400,
            False,
            _EXISTING_DYNAMIC,
            dict(syntax=_CLICKHOUSE, entity_type=None),
            id='cannot change syntax to clickhouse without entity_type',
        ),
        pytest.param(
            400,
            True,
            _EXISTING_DYNAMIC,
            dict(syntax=_CLICKHOUSE),
            id='cannot change to clickhouse syntax anyway',
        ),
        pytest.param(
            200,
            True,
            _EXISTING_CLICKHOUSE_ID,
            dict(tags=['irrelevant'], tags_limit=10),
            id='set tags_limit for where was NULL',
        ),
        pytest.param(
            400,
            False,
            _EXISTING_CLICKHOUSE_ID,
            dict(tags=['irrelevant'], entity_type=None, tags_limit=10),
            id='cannot set empty entity_type for clickhouse query',
        ),
        pytest.param(
            400,
            False,
            _EXISTING_CLICKHOUSE_ID,
            dict(tags=['irrelevant'], syntax=_SQLV1, tags_limit=10),
            id='cannot change syntax from clickhouse',
        ),
        pytest.param(
            200,
            True,
            _EXISTING_DYNAMIC,
            dict(entity_type=_DBID_UUID, tags=_TAGS),
            id='make dynamic query static and setup a manifest',
        ),
        pytest.param(
            400,
            True,
            _EXISTING_DYNAMIC,
            dict(entity_type=_DBID_UUID),
            id='make dynamic query static but dont fix empty manifest',
        ),
        pytest.param(
            200,
            True,
            _EXISTING_ID,
            dict(entity_type=None),
            id='make static query dynamic',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    TAGS_YQL_MINIMAL_EXECUTION_INTERVAL={
        '__default__': 1800,
        _EXISTING_ID: 60,
    },
)
async def test_edit(
        taxi_tags,
        expected_code: int,
        any_changes: bool,
        query_name: str,
        params: dict,
        financial: bool,
        pgsql,
):
    db = pgsql['tags']
    query = yql_tools.Query.find_by_name(db, query_name)
    assert query is not None
    assert query.author == _INITIAL_AUTHOR

    login = params.pop('login', _LOGIN)
    for key, value in params.items():
        query.__setattr__(key, value)
    await query.perform_edit_request(
        taxi_tags,
        'edit',
        login=login,
        expected_code=expected_code,
        use_financial_handler=financial,
    )

    if expected_code == 200:
        modified_query = yql_tools.Query.find_by_name(db, query_name)
        assert modified_query is not None
        if any_changes:
            query.last_modifier = login
            query.changed = modified_query.changed
        assert query == modified_query


@pytest.mark.pgsql('tags', files=['queries_edit_initial.sql'])
async def test_edit_query_add_placeholder(taxi_tags, pgsql):
    response = await yql_tools.edit_request(
        taxi_tags,
        'edit',
        login=_LOGIN,
        query_name='query_without_placeholder',
        query=_QUERY,
        tags=_TAGS,
        tags_limit=100,
        ticket=_TASK_TICKET,
    )
    assert response.status_code == 200
    _verify_process_in_yt_query(pgsql['tags'], 'query_without_placeholder')


@pytest.mark.pgsql('tags', files=['queries_edit_initial.sql'])
async def test_edit_query_sql_to_chyt(taxi_tags):
    # migrate SQL -> CLICKHOUSE with placeholder
    await yql_tools.edit_request(
        taxi_tags,
        'edit',
        login=_LOGIN,
        query_name=_EXISTING_ID,
        syntax=_CLICKHOUSE,
        query=_QUERY,
        tags=_TAGS,
        tags_limit=100,
        ticket=_TASK_TICKET,
        confirmation_token='totally_unique_uuid_2',
        expected_code=400,
    )


@pytest.mark.config(TAGS_ACL_TOPICS_ENABLED=True)
@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['queries_edit_initial.sql'])
@pytest.mark.parametrize(
    'use_financial_handler',
    [True, False],
    ids=['using_financial_handler', 'using_common_handler'],
)
@pytest.mark.parametrize(
    'expected_code, expected_topics, acl_allowed, query_name, tags',
    [
        pytest.param(
            200, _USUAL_TOPICS, True, _EXISTING_ID, _TAGS, id='simple allowed',
        ),
        pytest.param(
            403,
            _USUAL_TOPICS,
            False,
            _EXISTING_ID,
            _TAGS,
            id='simple prohibited',
        ),
        pytest.param(
            400,
            _USUAL_TOPICS,
            False,
            _EXISTING_ID,
            [],
            id='update tags, set no tags',
        ),
        pytest.param(
            403,
            _USUAL_TOPICS + list(_FINANCIAL_TOPICS),
            False,
            _EXISTING_ID,
            list(_FINANCIAL_TAGS),
            id='update tags, set financial tags',
        ),
        pytest.param(
            403,
            _USUAL_TOPICS + list(_FINANCIAL_TOPICS),
            False,
            _EXISTING_FINANCIAL_ID,
            list(_FINANCIAL_TAGS),
            id='no updating financial query',
        ),
        pytest.param(
            403,
            _USUAL_TOPICS + list(_FINANCIAL_TOPICS),
            False,
            _EXISTING_FINANCIAL_ID,
            ['unknown_tag', 'usual_tag'],
            id='set non-financial tags to query',
        ),
    ],
)
async def test_edit_acl(
        taxi_tags,
        query_name: str,
        tags: List[str],
        use_financial_handler: bool,
        pgsql,
        mockserver,
        acl_allowed: bool,
        expected_code: int,
        expected_topics: List[str],
):
    existing = _find_query(pgsql['tags'], query_name)
    assert existing is not None

    if acl_allowed:
        acl_tools.make_mock_acl_allowed(mockserver)
    else:
        acl_tools.make_mock_acl_prohibited(
            mockserver, constants.TEST_LOGIN, expected_topics, expected_topics,
        )

    await yql_tools.edit_request(
        taxi_tags,
        'edit',
        login=constants.TEST_LOGIN,
        query_name=query_name,
        tags=tags,
        use_financial_handler=use_financial_handler,
        expected_code=expected_code,
        query=_QUERY,
        tags_limit=100,
        ticket=_TASK_TICKET,
    )


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['queries_edit_initial.sql'])
@pytest.mark.parametrize(
    'use_financial_handler',
    [True, False],
    ids=['using_financial_handler', 'using_common_handler'],
)
@pytest.mark.parametrize(
    'query_name, tags, expected_code, expected_financial_code,'
    'expected_audit_type, expected_product_audit, expected_analyst_audit',
    [
        pytest.param(
            _EXISTING_ID,
            _TAGS,
            200,
            200,
            None,
            None,
            None,
            id='do not update tags',
        ),
        pytest.param(
            _EXISTING_ID,
            ['unknown_tag', 'usual_tag'],
            200,
            200,
            None,
            None,
            None,
            id='update tags, set non-financial ones',
        ),
        pytest.param(
            _EXISTING_ID,
            [],
            400,
            400,
            None,
            None,
            None,
            id='update tags, set no tags',
        ),
        pytest.param(
            _EXISTING_ID,
            list(_FINANCIAL_TAGS),
            403,
            200,
            yql_tools.AuditType.Financial,
            None,
            None,
            id='update tags, set financial tags',
        ),
        pytest.param(
            _EXISTING_ID,
            list(_FINANCIAL_TAGS),
            403,
            200,
            yql_tools.AuditType.FinancialAndTechnical,
            None,
            None,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_if_ttl_is_more_than_days': 90,
                    },
                ),
            ],
            id='update tags list to financial and require technical review',
        ),
        pytest.param(
            _EXISTING_FINANCIAL_ID,
            list(_FINANCIAL_TAGS),
            403,
            200,
            yql_tools.AuditType.Financial,
            None,
            None,
            id='no updating financial query',
        ),
        pytest.param(
            _EXISTING_FINANCIAL_ID,
            ['unknown_tag', 'usual_tag'],
            403,
            200,
            yql_tools.AuditType.Financial,
            None,
            None,
            id='set non-financial tags to query',
        ),
        pytest.param(
            _EXISTING_FINANCIAL_ID,
            list(_FINANCIAL_TAGS),
            403,
            200,
            yql_tools.AuditType.Financial,
            None,
            None,
            id='update finance tags on query',
        ),
        pytest.param(
            'beautiful_query_name',
            ['unknown_tag', 'usual_tag'],
            200,
            200,
            yql_tools.AuditType.Technical,
            None,
            None,
            id=(
                'update tags, set non-financial ones on query'
                'with name different from provider\'s name'
            ),
        ),
        pytest.param(
            'beautiful_query_name',
            ['frauder'],
            403,
            200,
            yql_tools.AuditType.NotRequired,
            'antifraud',
            None,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'product_audit_rules': [
                            {
                                'name': 'antifraud',
                                'title': 'Antifraud group',
                                'tag_names': ['frauder'],
                            },
                        ],
                    },
                ),
            ],
            id='product_audit_requirement',
        ),
        pytest.param(
            _EXISTING_ID,
            _TAGS,
            403,
            200,
            yql_tools.AuditType.Technical,
            None,
            None,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_if_tags_limit_is_more_than_value': 99,
                        'require_audit_for_topics_or_entity_types': {
                            'entity_types': {
                                '__default__': 101,
                                'dbid_uuid': 102,
                            },
                        },
                    },
                ),
            ],
            id='tags-limit-over',
        ),
        pytest.param(
            _EXISTING_ID,
            _TAGS,
            403,
            200,
            yql_tools.AuditType.Technical,
            None,
            None,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_for_topics_or_entity_types': {
                            'by_entity_types': {
                                '__default__': 101,
                                'dbid_uuid': 99,
                            },
                        },
                    },
                ),
            ],
            id='tags-limit-over-by-entity-type',
        ),
        pytest.param(
            _EXISTING_ID,
            _TAGS,
            403,
            200,
            yql_tools.AuditType.Technical,
            None,
            None,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_for_topics_or_entity_types': {
                            'by_topics': {'topic_01': 101, 'topic_10': 99},
                        },
                    },
                ),
            ],
            id='tags-limit-over-by-topic',
        ),
        pytest.param(
            _EXISTING_ID,
            _TAGS,
            403,
            200,
            yql_tools.AuditType.Technical,
            None,
            None,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_COUNT_LIMITS={
                        '__default__': {
                            '__default__': 10000,
                            _EXISTING_ID: 100,
                        },
                    },
                ),
            ],
            id='tags-limit-double-set',
        ),
        pytest.param(
            _EXISTING_ID,
            _TAGS,
            200,
            200,
            None,
            None,
            None,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'require_audit_if_tags_limit_is_more_than_value': 103,
                        'require_audit_for_topics_or_entity_types': {
                            'by_topics': {'topic_10': 101},
                            'by_entity_types': {
                                '__default__': 99,
                                'dbid_uuid': 102,
                            },
                        },
                    },
                    TAGS_YQL_COUNT_LIMITS={
                        '__default__': {'__default__': 10000},
                    },
                ),
            ],
            id='tags-limit-pass',
        ),
        pytest.param(
            _EXISTING_ID,
            ['tag_name_1000'],
            403,
            200,
            None,
            None,
            'default',
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={'analyst_audit_enabled': True},
                ),
            ],
            id='analyst-audit-enabled',
        ),
        pytest.param(
            _EXISTING_ID,
            ['tag_name_1000'],
            200,
            200,
            None,
            None,
            None,
            id='analyst-audit-disabled',
        ),
    ],
)
async def test_edit_security(
        taxi_tags,
        query_name: str,
        tags: List[str],
        use_financial_handler: bool,
        expected_code: int,
        expected_financial_code: int,
        expected_audit_type: yql_tools.AuditType,
        expected_product_audit: Optional[str],
        expected_analyst_audit: Optional[str],
        pgsql,
):
    existing = _find_query(pgsql['tags'], query_name)
    assert existing is not None
    expected_code = (
        expected_financial_code if use_financial_handler else expected_code
    )
    await yql_tools.edit_request(
        taxi_tags,
        'edit',
        login=_LOGIN,
        query_name=query_name,
        tags=tags,
        use_financial_handler=use_financial_handler,
        audit_type=expected_audit_type,
        product_audit=expected_product_audit,
        analyst_audit=expected_analyst_audit,
        enabled=True,
        expected_code=expected_code,
        query=_QUERY,
        tags_limit=100,
        ticket=_TASK_TICKET,
    )


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['queries_edit_initial.sql'])
@pytest.mark.parametrize(
    'handler, query_name, tags, '
    'audit_type, expected_audit_type, '
    'product_audit, expected_product_audit, '
    'analyst_audit, expected_analyst_audit, '
    'expected_code',
    [
        pytest.param(
            'create',
            'new_query_name',
            list(_FINANCIAL_TAGS),
            yql_tools.AuditType.Financial,
            yql_tools.AuditType.Financial,
            _AUDIT_NOT_REQUIRED,
            _AUDIT_NOT_REQUIRED,
            _AUDIT_NOT_REQUIRED,
            _AUDIT_NOT_REQUIRED,
            200,
            id='create-financial-query',
        ),
        pytest.param(
            'create',
            'new_query_name',
            list(_FINANCIAL_TAGS),
            yql_tools.AuditType.Technical,
            yql_tools.AuditType.Financial,
            _AUDIT_NOT_REQUIRED,
            _AUDIT_NOT_REQUIRED,
            _AUDIT_NOT_REQUIRED,
            _AUDIT_NOT_REQUIRED,
            403,
            id='missing-financial-audit',
        ),
        pytest.param(
            'create',
            'new_query_name',
            list(_FINANCIAL_TAGS),
            yql_tools.AuditType.FinancialAndTechnical,
            yql_tools.AuditType.Financial,
            _AUDIT_NOT_REQUIRED,
            _AUDIT_NOT_REQUIRED,
            _AUDIT_NOT_REQUIRED,
            _AUDIT_NOT_REQUIRED,
            200,
            id='extra-technical-audit',
        ),
        pytest.param(
            'edit',
            _EXISTING_ID,
            ['audit_me_please'],
            None,
            None,
            'security',
            'security',
            _AUDIT_NOT_REQUIRED,
            _AUDIT_NOT_REQUIRED,
            200,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'product_audit_rules': [
                            {
                                'name': 'security',
                                'title': 'reason for product audit',
                                'tag_names': ['audit_me_please'],
                            },
                        ],
                    },
                ),
            ],
            id='edit-query-with-product-audit',
        ),
        pytest.param(
            'edit',
            _EXISTING_ID,
            ['audit_me_please'],
            yql_tools.AuditType.Technical,
            None,
            _AUDIT_NOT_REQUIRED,
            'security',
            _AUDIT_NOT_REQUIRED,
            _AUDIT_NOT_REQUIRED,
            403,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={
                        'product_audit_rules': [
                            {
                                'name': 'security',
                                'title': 'reason for product audit',
                                'tag_names': ['audit_me_please'],
                            },
                        ],
                    },
                ),
            ],
            id='missing-product-audit',
        ),
        pytest.param(
            'edit',
            _EXISTING_ID,
            ['tag_name_1000'],
            None,
            None,
            None,
            None,
            None,
            'default',
            403,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={'analyst_audit_enabled': True},
                ),
            ],
            id='analyst-audit-enabled-for-edit',
        ),
        pytest.param(
            'create',
            'new_query_name',
            ['tag_name_1000'],
            None,
            None,
            None,
            None,
            None,
            'default',
            403,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_AUDIT_RULES={'analyst_audit_enabled': True},
                ),
            ],
            id='analyst-audit-enabled-for-create',
        ),
    ],
)
async def test_audit_completion(
        taxi_tags,
        handler: str,
        query_name: str,
        tags: List[str],
        audit_type: Optional[yql_tools.AuditType],
        expected_audit_type: Optional[yql_tools.AuditType],
        product_audit: Optional[str],
        expected_product_audit: Optional[str],
        analyst_audit: Optional[str],
        expected_analyst_audit: Optional[str],
        expected_code: int,
):
    # check handler does not receive audit_completion information,
    # instead, it's a producer and should always return 200 in the cases
    expected_check_code = 200

    await yql_tools.edit_request(
        taxi_tags,
        handler,
        login=_LOGIN,
        query_name=query_name,
        tags=tags,
        use_financial_handler=True,
        audit_type=audit_type,
        expected_audit_type=expected_audit_type,
        product_audit=product_audit,
        expected_product_audit=expected_product_audit,
        analyst_audit=analyst_audit,
        expected_analyst_audit=expected_analyst_audit,
        enabled=True,
        expected_code=expected_code,
        expected_check_code=expected_check_code,
        query=_QUERY,
        tags_limit=100,
        ticket=_TASK_TICKET,
    )
