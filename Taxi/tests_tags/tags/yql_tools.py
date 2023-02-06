import copy
import datetime
import enum
import random
import re
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from tests_tags.tags import constants
from tests_tags.tags import tags_select
from tests_tags.tags import tags_tools

_DBID_UUID = 'dbid_uuid'
_SQLV1 = 'SQLv1'

_PRODUCT_AUDIT_NOT_REQUIRED = 'not_required'


class AuditType(enum.Enum):
    Financial = 'financial'
    Technical = 'technical'
    FinancialAndTechnical = 'financial_and_technical'
    NotRequired = 'not_required'


def _to_str(time: Optional[Union[str, datetime.datetime]]) -> Optional[str]:
    if not time:
        return None
    if isinstance(time, str):
        return time
    return time.isoformat()


class Query:
    def __init__(
            self,
            name: str,
            provider_id: int,
            tags: List[str],
            changed: Union[str, datetime.datetime] = '2018-08-30T12:34:56.0',
            created: Union[str, datetime.datetime] = '2018-08-30T12:34:56.0',
            query: str = '[_INSERT_HERE_] USE hahn via SQL;',
            period: Union[int, datetime.timedelta] = 1800,
            entity_type: Optional[str] = 'dbid_uuid',
            enabled: bool = True,
            author: str = 'vasya',
            last_modifier: str = 'petya',
            syntax: str = _SQLV1,
            custom_execution_time=None,
            yql_processing_method='yt_merge',
            last_operation_id: Optional[str] = None,
            disable_at: Optional[datetime.datetime] = None,
            ticket: Optional[str] = None,
            tags_limit: Optional[int] = None,
    ):
        self.name = name
        self.provider_id = provider_id
        self.entity_type = entity_type
        self.tags = tags
        self.author = author
        self.last_modifier = last_modifier
        self.enabled = enabled
        self.changed = _to_str(changed)
        self.created = _to_str(created)
        if isinstance(period, datetime.timedelta):
            self.period = int(period.total_seconds())
        else:
            assert isinstance(period, int)
            self.period = int(period)
        self.query = query
        self.syntax = syntax
        self.custom_execution_time = custom_execution_time
        self.yql_processing_method = yql_processing_method
        self.last_operation_id = last_operation_id
        self.disable_at = disable_at
        self.ticket = ticket
        self.tags_limit = tags_limit

    def __eq__(self, other):
        return vars(self) == vars(other)

    def __repr__(self):
        return vars(self).__repr__()

    def values(self):
        if (
                self.custom_execution_time is not None
                and self.custom_execution_time != 'NULL'
        ):
            custom_execution_time = '\'' + self.custom_execution_time + '\''
        else:
            custom_execution_time = 'NULL'
        tags = '{' + ','.join('\"' + tag + '\"' for tag in self.tags) + '}'
        return (
            (
                '(\'{name}\', {provider_id}, {entity_type}, '
                '\'{tags}\', \'{author}\', \'{last_modifier}\', {enabled}, '
                '\'{changed}\', \'{created}\', '
                'interval \'{period} seconds\', \'{query}\', '
                '\'{syntax}\', {custom_execution_time}, '
                '\'{yql_processing_method}\', \'{last_operation_id}\', '
                '{disable_at}, {ticket}, {tags_limit})'
            ).format(
                name=self.name,
                provider_id=self.provider_id,
                entity_type='\'' + self.entity_type + '\''
                if self.entity_type
                else 'NULL',
                tags=tags,
                author=self.author,
                last_modifier=self.last_modifier,
                enabled=self.enabled,
                changed=self.changed,
                created=self.created,
                period=self.period,
                query=self.query,
                syntax=self.syntax,
                custom_execution_time=custom_execution_time,
                yql_processing_method=self.yql_processing_method,
                last_operation_id=self.last_operation_id or 'NULL',
                disable_at=f'\'{self.disable_at.isoformat()}\''
                if self.disable_at
                else 'NULL',
                ticket=f'\'{self.ticket}\'' if self.ticket else 'NULL',
                tags_limit=self.tags_limit or 'NULL',
            )
        )

    @classmethod
    def from_row(cls, row):
        return Query(
            name=row[0],
            provider_id=row[1],
            entity_type=row[2],
            tags=row[3],
            author=row[4],
            last_modifier=row[5],
            enabled=row[6],
            changed=row[7],
            created=row[8],
            period=row[9],
            query=row[10],
            syntax=row[11],
            custom_execution_time=row[12],
            yql_processing_method=row[13],
            last_operation_id=row[14],
            disable_at=row[15],
            ticket=row[17],
            tags_limit=row[18],
        )

    @classmethod
    def find_by_name(cls, db, name: str) -> Optional['Query']:
        cursor = db.cursor()
        cursor.execute(f'SELECT * FROM service.queries WHERE name=\'{name}\'')
        rows = list(row for row in cursor)
        if not rows:
            return None
        return cls.from_row(rows[0])

    @staticmethod
    def prepare_request_headers(login: Optional[str] = 'vasya') -> dict:
        headers = dict()
        if login:
            headers['X-Yandex-Login'] = login
        return headers

    def prepare_edit_body(
            self, confirmation_token: str = 'whatever',
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            'name': self.name,
            'query': self.query,
            'syntax': self.syntax,
            'confirmation_token': confirmation_token,
            'period': self.period,
            'tags': self.tags,
            'enabled': self.enabled,
        }
        if self.entity_type:
            body['entity_type'] = self.entity_type
        if self.custom_execution_time is not None:
            execution_time = tags_tools.time_to_str(self.custom_execution_time)
            body['custom_execution_time'] = execution_time
        if self.disable_at is not None:
            body['disable_at'] = tags_tools.time_to_str(self.disable_at)
        if self.ticket is not None:
            body['ticket'] = self.ticket
        if self.tags_limit is not None:
            body['tags_limit'] = self.tags_limit
        return body

    async def perform_review_request(
            self,
            taxi_tags,
            login: Optional[str],
            expected_decision: Optional[str],
            expected_audit_required: Optional[bool] = None,
            expected_audit_groups: Optional[List[Dict[str, str]]] = None,
            expected_fields: Optional[List[Dict[str, str]]] = None,
            body: Optional[Dict[str, Any]] = None,
    ):
        headers = self.prepare_request_headers(login)
        if not body:
            body = self.prepare_edit_body()

        response = await taxi_tags.post(
            'v1/admin/queries/review', body, headers=headers,
        )
        assert response.status_code == 200
        response = response.json()
        if expected_decision is not None:
            assert response.get('decision') == expected_decision
        if expected_audit_required is not None:
            assert response.get('is_audit_required') == expected_audit_required
        if expected_audit_groups is not None:
            assert response.get('audit_groups') == expected_audit_groups
        if expected_fields is not None:
            assert response.get('fields') == expected_fields

    async def perform_edit_request(
            self,
            taxi_tags,
            handler_name: str,
            login: Optional[str],
            expected_code: int = 200,
            expected_check_code: Optional[int] = None,
            use_financial_handler: bool = False,
            audit_type: Optional[AuditType] = None,
            expected_audit_type: Optional[AuditType] = None,
            product_audit: Optional[str] = None,
            expected_product_audit: Optional[str] = None,
            analyst_audit: Optional[str] = None,
            expected_analyst_audit: Optional[str] = None,
            confirmation_token: str = 'totally_unique_uuid',
    ):
        body = self.prepare_edit_body(confirmation_token)
        headers = self.prepare_request_headers(login)

        if (
                expected_product_audit
                or expected_analyst_audit
                or expected_audit_type
        ):
            await check_finance_request(
                taxi_tags=taxi_tags,
                url=f'v1/admin/finance/queries/check_{handler_name}',
                expected_code=expected_check_code or expected_code,
                body=body,
                headers=headers,
                locks=[self.name],
                audit_type=expected_audit_type,
                product_audit=expected_product_audit,
                analyst_audit=expected_analyst_audit,
            )

        # No need to perform review request for an expected 400,
        # it's being tested in a separate tests
        if expected_code != 400:
            expected_decision: Optional[
                str
            ] = 'allowed' if expected_code == 200 else 'denied'
            if expected_code in {404, 403, 409}:
                # We can only image what caused the error codes
                expected_decision = None

            # TODO: Expand the tests data
            # For now, this is an optional check for when we know what
            # to expect from a /review handler based on expected code
            # from a non-audited edit request
            is_audit_required_opt = (
                False
                if (not use_financial_handler and expected_code == 200)
                else None
            )

            if use_financial_handler:
                # Parameter became required and should be used for all
                # requests into /finance handlers therefore we select it
                # if it's unknown (TODO: update the test cases)
                audit_type = audit_type or AuditType.Technical
                body['audit_type'] = audit_type.value
                body['product_audit'] = product_audit
                body['analyst_audit'] = analyst_audit

            await self.perform_review_request(
                taxi_tags=taxi_tags,
                login=login,
                expected_decision=expected_decision,
                expected_audit_required=is_audit_required_opt,
                body=body,
            )

        url_part = '/finance' if use_financial_handler else ''
        response = await taxi_tags.post(
            f'v1/admin{url_part}/queries/{handler_name}',
            body,
            headers=headers,
        )
        assert response.status_code == expected_code
        return response


def validate_operation(
        operation_id: str,
        provider_id: int,
        entity_type: str,
        status: str,
        failure_type: str,
        failure_description: str,
        db,
):
    cursor = db.cursor()
    cursor.execute(
        f'SELECT operation_id, provider_id, entity_type, status, '
        f'failure_type, failure_description FROM '
        f'service.yql_operations WHERE operation_id=\'{operation_id}\';',
    )

    rows = list(row for row in cursor)
    assert len(rows) == 1
    assert rows[0] == (
        operation_id,
        provider_id,
        entity_type,
        status,
        failure_type,
        failure_description,
    )


def remove_uuid(string: Optional[str]) -> Optional[str]:
    if string is None:
        return None
    return re.sub(r'_?[A-Za-z0-9]{32}', '', string)


def insert_operation(
        operation_id: str,
        provider_id: int,
        entity_type: Optional[str],
        status,
        started,
        failure_type: Optional[str] = None,
        failure_description='NULL',
        total_count='NULL',
        added_count='NULL',
        removed_count='NULL',
        malformed_count='NULL',
        scheduled_at: Optional[datetime.datetime] = None,
        retry_number: Optional[int] = 0,
):
    entity_type_value = f'\'{entity_type}\'' if entity_type else 'NULL'
    scheduled_at_value = f'\'{scheduled_at}\'' if scheduled_at else 'NULL'
    failure_type_value = f'\'{failure_type}\'' if failure_type else 'NULL'
    return (
        f'INSERT INTO service.yql_operations VALUES (\'{operation_id}\', '
        f'{provider_id}, {entity_type_value}, \'{status}\', \'{started}\', '
        f'{failure_description}, {failure_type_value}, '
        f'{total_count}, {added_count}, {removed_count}, {malformed_count}, '
        f'{scheduled_at_value}, {retry_number});'
    )


def insert_queries(queries: List[Query]):
    query = (
        'INSERT INTO service.queries '
        '(name, provider_id, entity_type, tags, author, last_modifier,'
        ' enabled, changed, created, period, query, syntax,'
        ' custom_execution_time, yql_processing_method, last_operation_id,'
        ' disable_at, ticket, tags_limit) VALUES '
    )
    return query + ','.join(map(lambda q: q.values(), queries))


_SNAPSHOTS_PATH = 'home/taxi/testsuite/features/tags/snapshots'

_COMMENT_SECTION = '--------------------------------------------------------'
_COMMENT_GENERATED = '-- THIS CODE WAS GENERATED BY TAGS SERVICE'

_QUERY_HEADER = (
    'PRAGMA yt.OperationSpec = "{\\"annotations\\" = '
    '{\\"taxidmp_task\\" = \\"tags_testsuite_query0\\"; '
    '\\"taxidmp_run_id\\" = \\"\\"; \\"backend_type\\" = \\"yql\\"}}";'
)

_EMPTY_TABLE_WITH_SCHEMA = (
    '(SELECT * from range("dummy", "", "") WITH SCHEMA '
    'Struct<tag:string,ttl:string,entity_value:string,entity_type:string>)'
)


def gen_snapshot_path(provider: str):
    return f'{_SNAPSHOTS_PATH}/{provider}_snapshot'


def gen_tmp_path(provider: str):
    return f'{_SNAPSHOTS_PATH}/{provider}_tmp'


def gen_tag_names_path(provider: str):
    return f'{_SNAPSHOTS_PATH}/{provider}_tag_names'


def gen_entity_types_path(provider: str):
    return f'{_SNAPSHOTS_PATH}/{provider}_entity_types'


def gen_append_path(provider: str):
    return f'{_SNAPSHOTS_PATH}/{provider}_append'


def gen_remove_path(provider: str):
    return f'{_SNAPSHOTS_PATH}/{provider}_remove'


def gen_transformed_yql_query(
        user_query: str,
        provider: str,
        entity_type: Optional[str],
        last_snapshot_path: Optional[str],
) -> str:
    prev_snapshot_path = (
        f'`{last_snapshot_path}`'
        if last_snapshot_path
        else _EMPTY_TABLE_WITH_SCHEMA
    )
    snapshot_path = gen_snapshot_path(provider)
    tmp_path = gen_tmp_path(provider)
    tag_names_path = gen_tag_names_path(provider)
    entity_types_path = gen_entity_types_path(provider)

    prefix = f'{_COMMENT_GENERATED}\n{_QUERY_HEADER}\n{_COMMENT_SECTION}\n\n\n'

    insert = (
        f'\n\n{_COMMENT_SECTION}\n{_COMMENT_GENERATED}\n'
        f'INSERT INTO `{tmp_path if entity_type else snapshot_path}`'
        f' WITH TRUNCATE\n'
        f'{_COMMENT_SECTION}\n\n\n'
    )

    postfix = (
        (
            f'\n\n\n{_COMMENT_SECTION}\n{_COMMENT_GENERATED}\n;\nCOMMIT;\n'
            f'INSERT INTO `{snapshot_path}` WITH TRUNCATE'
            f' SELECT a.tag, a.{entity_type} AS entity_value,'
            f' \'{entity_type}\' AS entity_type,'
            f' WeakField(a.ttl, string) ?? \'infinity\' AS ttl'
            f' FROM `{tmp_path}` AS a;\n'
            f'COMMIT;\n'
            f'INSERT INTO `{tag_names_path}` WITH TRUNCATE'
            f' SELECT DISTINCT tag FROM `{snapshot_path}`;\n'
            f'INSERT INTO `{entity_types_path}` WITH TRUNCATE'
            f' SELECT DISTINCT entity_type FROM `{snapshot_path}`;\n'
            f'DROP TABLE `{tmp_path}`;\n'
        )
        if entity_type is not None
        else (
            f'\n\n\n{_COMMENT_SECTION}\n{_COMMENT_GENERATED}\n;\nCOMMIT;\n'
            f'INSERT INTO `{tag_names_path}` WITH TRUNCATE'
            f' SELECT DISTINCT tag FROM `{snapshot_path}`;\n'
            f'INSERT INTO `{entity_types_path}` WITH TRUNCATE'
            f' SELECT DISTINCT entity_type FROM `{snapshot_path}`;\n'
        )
    )

    query = user_query.replace(
        '[_LAST_RUN_RESULT_]', prev_snapshot_path,
    ).replace('[_INSERT_HERE_]', insert)

    return prefix + query + postfix


def gen_yql_merge_query(provider: str, last_snapshot_path: str) -> str:
    snapshot_path = gen_snapshot_path(provider)
    append_path = gen_append_path(provider)
    remove_path = gen_remove_path(provider)

    return (
        f'INSERT INTO `{append_path}` WITH TRUNCATE'
        f' SELECT a.tag AS tag, a.entity_value AS entity_value,'
        f' a.entity_type AS entity_type,'
        f' (WeakField(a.ttl, string) ?? \'infinity\') AS ttl'
        f' FROM `{snapshot_path}` AS a'
        f' LEFT ONLY JOIN `{last_snapshot_path}` AS b'
        f' ON a.tag = b.tag AND a.entity_value = b.entity_value'
        f' AND a.entity_type = b.entity_type AND'
        f' (WeakField(a.ttl, string) ?? \'infinity\') ='
        f' (WeakField(b.ttl, string) ?? \'infinity\');\n'
        f'INSERT INTO `{remove_path}` WITH TRUNCATE'
        f' SELECT a.tag AS tag, a.entity_value AS entity_value,'
        f' a.entity_type AS entity_type FROM `{last_snapshot_path}` AS a'
        f' LEFT ONLY JOIN `{snapshot_path}` AS b ON a.tag = b.tag AND'
        f' a.entity_value = b.entity_value AND'
        f' a.entity_type = b.entity_type;\n'
    )


async def check_finance_request(
        taxi_tags,
        url: str,
        expected_code: int,
        body: Dict,
        headers: Dict,
        locks: List[str],
        audit_type: Optional[AuditType],
        product_audit: Optional[str],
        analyst_audit: Optional[str],
):
    response = await taxi_tags.post(url, body, headers=headers)
    assert response.status_code == expected_code
    if expected_code != 200:
        return

    response = response.json()

    expected_body = copy.deepcopy(body)

    # /check handler receives raw model and enriches it with
    # audit fields (at least one audit would be required in return)
    expected_body['product_audit'] = product_audit or 'not_required'
    expected_body['analyst_audit'] = analyst_audit or 'not_required'
    expected_body['audit_type'] = (
        audit_type.value if audit_type else 'not_required'
    )

    assert response['data'] == expected_body
    assert response['lock_ids'] == [
        {'custom': False, 'id': f'/yql/{lock}'} for lock in locks
    ]
    # check change_doc_id like 'yql_{name}_{uuid}'
    regexp = f'^yql_{body["name"]}_[A-Za-z0-9]{{32}}$'
    assert re.match(regexp, response['change_doc_id']) is not None

    diff = response['diff']
    assert diff['current'] != diff['new']
    if url.find('check_edit') > 0:
        assert diff['current']['name'] == diff['new']['name']
        assert diff['new'] == body


_QUERY = 'SELECT * FROM table;'
_TAGS = ['tag_name_1000', 'tag_name_1001']


async def edit_request(
        taxi_tags,
        name: str,
        login: Optional[str],
        query_name: str,
        query: str,
        period: int = 3600,
        syntax: str = _SQLV1,
        tags: Optional[List[str]] = None,
        entity_type: Optional[str] = _DBID_UUID,
        enabled: bool = False,
        use_financial_handler: bool = False,
        audit_type: Optional[AuditType] = None,
        expected_audit_type: Optional[AuditType] = None,
        product_audit: Optional[str] = None,
        expected_product_audit: Optional[str] = None,
        analyst_audit: Optional[str] = None,
        expected_analyst_audit: Optional[str] = None,
        expected_code: int = 200,
        expected_check_code: Optional[int] = None,
        custom_execution_time: Optional[datetime.datetime] = None,
        disable_at: Optional[datetime.datetime] = None,
        ticket: Optional[str] = None,
        tags_limit: Optional[int] = None,
        confirmation_token: str = 'totally_unique_uuid',
):
    yql = Query(
        name=query_name,
        provider_id=-1,
        tags=tags or [],
        query=query,
        period=period,
        entity_type=entity_type,
        enabled=enabled,
        syntax=syntax,
        custom_execution_time=custom_execution_time,
        disable_at=disable_at,
        ticket=ticket,
        tags_limit=tags_limit,
    )
    return await yql.perform_edit_request(
        taxi_tags=taxi_tags,
        handler_name=name,
        login=login,
        expected_code=expected_code,
        expected_check_code=expected_check_code,
        use_financial_handler=use_financial_handler,
        confirmation_token=confirmation_token,
        audit_type=audit_type,
        expected_audit_type=expected_audit_type,
        product_audit=product_audit,
        expected_product_audit=expected_product_audit,
        analyst_audit=analyst_audit,
        expected_analyst_audit=expected_analyst_audit,
    )


async def change_query_active_state(
        taxi_tags, query: Query, login: str, enable: bool,
):
    response = await edit_request(
        taxi_tags=taxi_tags,
        name='edit',
        login=login,
        query_name=query.name,
        query=query.query,
        period=query.period,
        tags=query.tags,
        enabled=enable,
        ticket=query.ticket,
        tags_limit=query.tags_limit,
        confirmation_token=str(random.randint(0, 100000)),
    )
    assert response.status_code == 200


class YtDownloadTask:
    def __init__(
            self,
            provider_id: int,
            snapshot_path: str,
            append_path: Optional[str],
            remove_info: Optional[Tuple[str, str]],
            current_row: int = 0,
            status: str = 'description',
            tag_names_path: str = 'tag_names',
            entity_types_path: Optional[str] = None,
            malformed_rows_count: Optional[int] = None,
    ):
        self.provider_id = provider_id
        self.snapshot_path = snapshot_path
        self.append_path = append_path
        self.remove_info = remove_info
        self.current_row = current_row
        self.status = status
        self.tag_names_path = tag_names_path
        self.entity_types_path = entity_types_path
        self.malformed_rows_count = malformed_rows_count

    def values(self):
        def _value_or(value, default_value):
            return value if value is not None else default_value

        if not self.append_path:
            append_path = 'NULL'
        else:
            append_path = '\'{}\''.format(self.append_path)
        if not self.remove_info:
            remove_path = 'NULL'
            remove_entity_type = 'NULL'
        else:
            remove_path = '\'{}\''.format(self.remove_info[0])
            remove_entity_type = f'\'{self.remove_info[1]}\''

        tag_names_path = f'\'{self.tag_names_path}\''
        if not self.entity_types_path:
            entity_types_path = 'NULL'
        else:
            entity_types_path = f'\'{self.entity_types_path}\''

        malformed_rows_count = _value_or(self.malformed_rows_count, 'NULL')

        return (
            '({provider_id}, \'{snapshot_path}\', '
            '{append_path},{remove_path}, {remove_entity_type}, '
            '{current_row}, \'{status}\', {tag_names_path},'
            '{entity_types_path}, {malformed_rows_count})'.format(
                provider_id=self.provider_id,
                snapshot_path=self.snapshot_path,
                append_path=append_path,
                remove_path=remove_path,
                remove_entity_type=remove_entity_type,
                current_row=self.current_row,
                status=self.status,
                tag_names_path=tag_names_path,
                entity_types_path=entity_types_path,
                malformed_rows_count=malformed_rows_count,
            )
        )


class YtSnapshot:
    def __init__(
            self,
            provider_id: int,
            snapshot_path: str,
            created: datetime.datetime,
            status: str,
            entity_type: Optional[str] = _DBID_UUID,
            query_syntax: str = _SQLV1,
    ):
        self.provider_id = provider_id
        self.snapshot_path = snapshot_path
        self.created = created
        self.status = status
        self.entity_type = entity_type
        self.query_syntax = query_syntax

    def __eq__(self, other):
        return (
            self.provider_id == other.provider_id
            and self.snapshot_path == other.snapshot_path
            and self.created == other.created
            and self.status == other.status
            and self.entity_type == other.entity_type
            and self.query_syntax == other.query_syntax
        )

    def values(self):
        entity_type = f'\'{self.entity_type}\'' if self.entity_type else 'NULL'
        return (
            f'({self.provider_id}, \'{self.snapshot_path}\', '
            f'\'{self.created}\', \'{self.status}\','
            f'{entity_type}, \'{self.query_syntax}\')'
        )


def insert_yt_download_tasks(tasks: List[YtDownloadTask]):
    query = (
        'INSERT INTO service.yt_download_tasks '
        '(provider_id, snapshot_path, '
        'append_path, remove_path, remove_entity_type, '
        'current_row, status, tag_names_path, entity_types_path, '
        'malformed_rows_count) VALUES '
    )
    return query + ','.join(map(lambda task: task.values(), tasks))


def verify_snapshot_status(db, status: str):
    rows = tags_select.select_table_named(
        'service.yt_snapshots', 'provider_id', db,
    )

    assert len(rows) == 1
    assert rows[0]['status'] == status


def verify_snapshot(
        db,
        snapshot_path: str,
        status: str,
        entity_type: str = _DBID_UUID,
        query_syntax: str = _SQLV1,
):
    rows = tags_select.select_table_named(
        'service.yt_snapshots', 'provider_id', db,
    )

    assert len(rows) == 1
    assert rows[0]['status'] == status
    assert rows[0]['snapshot_path'] == snapshot_path
    assert rows[0]['entity_type'] == entity_type
    assert rows[0]['query_syntax'] == query_syntax


def _gen_entity_type(entity_type: Optional[str], index: int):
    return (
        entity_type
        or constants.SUPPORTED_ENTITY_TYPES[
            index % len(constants.SUPPORTED_ENTITY_TYPES)
        ]
    )


def generate_and_insert_tags(
        db,
        local_yql_services,
        tags_count: int,
        tags_to_insert: int,
        entity_type: Optional[str] = None,
        query_syntax: str = _SQLV1,
        ttl_frequency: Optional[int] = None,
        ttl: Optional[str] = None,
):
    assert not (query_syntax == 'CLICKHOUSE' and entity_type is None)

    cursor = db.cursor()
    data = local_yql_services.gen_results_data_response(
        tags_count,
        chunk=tags_count,
        entity_type=entity_type,
        query_syntax=query_syntax,
        ttl_frequency=ttl_frequency,
        ttl=ttl,
    )
    cursor.execute(
        tags_tools.insert_tag_names([tags_tools.TagName(0, data[0]['tag'])]),
    )

    cursor.execute(
        tags_tools.insert_entities(
            map(
                lambda entry_with_id: tags_tools.Entity(
                    entry_with_id[0],
                    entry_with_id[1]['entity_value'],
                    entity_type=entry_with_id[1]['entity_type'],
                )
                if query_syntax == _SQLV1
                else tags_tools.Entity(
                    entry_with_id[0],
                    entry_with_id[1][entity_type],
                    entity_type=entity_type,
                ),
                enumerate(data[:tags_count]),
            ),
        ),
    )

    tags = [
        tags_tools.Tag(
            0,
            0,
            i,
            entity_type=_gen_entity_type(entity_type, i),
            ttl=ttl
            if ttl_frequency and not (i % ttl_frequency)
            else 'infinity',
        )
        for i in range(tags_to_insert)
    ]

    if tags_to_insert > 0:
        cursor.execute(tags_tools.insert_tags(tags))

    return data


def insert_snapshot(yt_snapshot: YtSnapshot):
    return insert_snapshots([yt_snapshot])


def insert_snapshots(yt_snapshots: List[YtSnapshot]):
    query = (
        'INSERT INTO service.yt_snapshots (provider_id, snapshot_path, '
        'created, status, entity_type, query_syntax) VALUES '
    )
    return query + ','.join(map(YtSnapshot.values, yt_snapshots))


def insert_yt_table(yt_table_path: str, operation_id: Optional[str] = None):
    operation_id = 'NULL' if operation_id is None else f'\'{operation_id}\''
    return (
        'INSERT INTO service.yt_tables_delete_queue'
        ' (yt_table_path, operation_id)'
        ' VALUES (\'' + yt_table_path + '\',' + operation_id + ')'
    )


def verify_yt_download_task(
        db,
        provider_id: int,
        status: str,
        current_row: Optional[int] = None,
        append_path: Optional[str] = None,
        remove_path: Optional[str] = None,
        malformed_rows_count: Optional[int] = None,
        check_status_only: bool = False,
):
    rows = tags_select.select_table_named(
        'service.yt_download_tasks', 'provider_id', db,
    )
    assert len(rows) == 1
    assert rows[0]['provider_id'] == provider_id
    assert rows[0]['status'] == status

    if not check_status_only:
        assert rows[0]['current_row'] == current_row
        assert rows[0]['append_path'] == append_path
        assert rows[0]['remove_path'] == remove_path
        assert rows[0]['malformed_rows_count'] == malformed_rows_count


def gen_tags(
        provider_id: int,
        tag_name_id: int,
        entities_range,
        entity_type: Optional[str] = None,
        ttl_frequency: Optional[int] = None,
        ttl: Optional[str] = None,
):
    return map(
        lambda i: tags_tools.Tag(
            tag_name_id,
            provider_id,
            i,
            entity_type=_gen_entity_type(entity_type, i),
            ttl=ttl
            if ttl_frequency and not (i % ttl_frequency)
            else 'infinity',
        ),
        entities_range,
    )


class SubscriptionType:
    def __init__(self, event: str, transport: str):
        self.event = event
        self.transport = transport


SUBSCRIPTION_TYPES = [SubscriptionType('failure', 'email')]


class Subscription:
    def __init__(
            self,
            provider_id: int,
            subscriber_login: str,
            notifications: List[SubscriptionType],
    ):
        self.provider_id = provider_id
        self.subscriber_login = subscriber_login
        self.notifications = notifications

    def notifications_to_str(self):
        return (
            '{'
            + ','.join(
                [
                    '"({},{})"'.format(
                        subscription_type.event, subscription_type.transport,
                    )
                    for subscription_type in self.notifications
                ],
            )
            + '}'
        )

    def values(self):
        return (
            f'({self.provider_id},\'{self.subscriber_login}\','
            + f'\'{self.notifications_to_str()}\')'
        )


def insert_subscriptions(subscriptions: List[Subscription]):
    return (
        'INSERT INTO service.yql_subscriptions (provider_id, subscriber_login,'
        ' notifications) VALUES '
        + ', '.join(subscription.values() for subscription in subscriptions)
        + ';'
    )
