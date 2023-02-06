import typing

import pytest

from replication.drafts import exceptions
from replication.drafts.models import source_validation


class EqualMagic:
    def __init__(self, comparator, desc: str):
        self._comparator = comparator
        self._desc = desc

    def __repr__(self):
        return f'EqualMagic({self._desc})'

    def __eq__(self, other):
        return self._comparator(other)


_JUST_TABLE_SCHEMA = EqualMagic(
    lambda other: ('created_at' in other and 'modified_at' in other),
    'pg just_table schema has created_at and modified_at fields',
)
_JUST_TABLE_INDEXES = EqualMagic(
    lambda other: (
        '[shard0] indexes:' in other
        and 'created_at' in other
        and 'modified_at' in other
    ),
    'pg just_table has created_at and modified_at indexes',
)


class DraftContextDummy:
    def __init__(self):
        self.comments: typing.List[str] = []

    async def add_comment(self, comment: str, *, log_datetime: bool = True):
        self.comments.append(comment)

    async def add_raw_comment(self, comment: str):
        return await self.add_comment(comment)


@pytest.mark.parametrize(
    ['request_payload', 'expected_comments', 'expected_errors'],
    [
        (
            {
                'secret_type': 'yav',
                'secret_id': 'sec-example_pg',
                'source_type': 'postgres',
            },
            ['[shard0] connection: SUCCESS', '[shard1] connection: SUCCESS'],
            None,
        ),
        (
            {
                'secret_type': 'yav',
                'secret_id': 'sec-conditioned',
                'source_type': 'postgres',
                'source_table': 'just_table',
            },
            [
                '[shard0] connection: SUCCESS',
                'Table just_table exists.',
                'User in secret has access to table',
                '[shard0] primary keys:\n[\n    "id"\n]',
                _JUST_TABLE_SCHEMA,
                _JUST_TABLE_INDEXES,
                '[shard0] '
                'Query:\nSELECT * from just_table limit 1\nDuration: 0.0',
                'WARN: Table just_table shard0 is accessible but EMPTY',
                EqualMagic(
                    lambda other: 'pg_total_relation_size' in other,
                    'pg_total_relation_size query',
                ),
                EqualMagic(
                    lambda other: 'so it and can be loaded as snapshot'
                    in other,
                    'pg comment: table size',
                ),
            ],
            ['Table just_table shard0 is accessible but EMPTY'],
        ),
        (
            {
                'secret_type': 'yav',
                'secret_id': 'sec-conditioned',
                'source_type': 'postgres',
                'source_table': 'just_table',
                'replicate_by': 'modified_at',
            },
            [
                '[shard0] connection: SUCCESS',
                'Table just_table exists.',
                'User in secret has access to table',
                '[shard0] primary keys:\n[\n    "id"\n]',
                _JUST_TABLE_SCHEMA,
                _JUST_TABLE_INDEXES,
                '[shard0 just_table] has index field by '
                'replicate_by="modified_at"',
                '[shard0] '
                'Query:\nSELECT * from just_table limit 1\nDuration: 0.0',
                'WARN: Table just_table shard0 is accessible but EMPTY',
                '[shard0] Query:\n'
                'EXPLAIN ANALYZE select * from just_table '
                'WHERE modified_at < now()'
                ' AND modified_at > now() - interval \'5 minutes\' '
                'ORDER BY modified_at LIMIT 10000\n'
                'Duration: 0.0',
                EqualMagic(
                    lambda other: other.startswith('QUERY PLAN'),
                    'QUERY PLAN query',
                ),
                EqualMagic(
                    lambda other: 'pg_total_relation_size' in other,
                    'pg_total_relation_size query',
                ),
                EqualMagic(
                    lambda other: 'so it and can be loaded as snapshot'
                    in other,
                    'pg comment: table size',
                ),
            ],
            ['Table just_table shard0 is accessible but EMPTY'],
        ),
        (
            {
                'secret_type': 'yav',
                'secret_id': 'sec-conditioned',
                'source_type': 'postgres',
                'source_table': 'just_table',
                'replicate_by': 'updated_at',
            },
            [
                '[shard0] connection: SUCCESS',
                'Table just_table exists.',
                'User in secret has access to table',
                '[shard0] primary keys:\n[\n    "id"\n]',
                _JUST_TABLE_SCHEMA,
                _JUST_TABLE_INDEXES,
                EqualMagic(
                    lambda other: other.startswith(
                        'WARN: [shard0 just_table] '
                        'has not any index which contains '
                        'replicate_by="updated_at". '
                        'Suitable fields, which can be used as replicate_by: ',
                    ),
                    'Bad updated_at index field',
                ),
                EqualMagic(
                    lambda other: 'SELECT * from just_table limit 1' in other,
                    'Doc example query',
                ),
                'WARN: Table just_table shard0 is accessible but EMPTY',
                EqualMagic(
                    lambda other: (
                        'Got UndefinedColumnError error: '
                        'column "updated_at" does not exist'
                    )
                    in other,
                    (
                        'Got UndefinedColumnError error: '
                        'column "updated_at" does not exist'
                    ),
                ),
            ],
            [
                'has not any index which contains replicate_by="updated_at"',
                'Table just_table shard0 is accessible but EMPTY',
            ],
        ),
    ],
)
async def test_source_validation(
        replication_ctx, request_payload, expected_comments, expected_errors,
):
    draft_context = DraftContextDummy()
    payload = source_validation.SourceValidationPayload(**request_payload)
    # pylint: disable=protected-access
    secret_id = source_validation._make_secret_id(payload)
    if expected_errors:
        with pytest.raises(exceptions.DraftApplyingError) as error:
            await replication_ctx.source_schemas_keeper.source_validation(
                draft_context=draft_context,
                secret_id=secret_id,
                payload=payload,
            )
        for expected_error in expected_errors:
            assert expected_error in str(error.value)
    else:
        await replication_ctx.source_schemas_keeper.source_validation(
            draft_context=draft_context, secret_id=secret_id, payload=payload,
        )
    assert draft_context.comments == expected_comments
