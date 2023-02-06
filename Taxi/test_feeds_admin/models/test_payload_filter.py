import re

from feeds_admin.models import json_filter as models


async def test_payload_filter():
    complex_filter = models.Filters(
        filters=[
            models.Filter(
                db_field=models.DbField.PAYLOAD,
                path='text',
                values=['one'],
                operator=models.Operator.EQUALS,
            ),
            models.Filter(
                db_field=models.DbField.PAYLOAD,
                path='',
                values=['global_search'],
                operator=models.Operator.CONTAINS,
            ),
            models.Filter(
                db_field=models.DbField.PAYLOAD,
                path='context.pages.0.text',
                values=['one', 'two'],
                operator=models.Operator.CONTAINS,
            ),
            models.Filter(
                db_field=models.DbField.PAYLOAD,
                path='array',
                values=['one'],
                operator=models.Operator.IN_ARRAY,
            ),
            models.Filter(
                db_field=models.DbField.PAYLOAD,
                path='nothing',
                operator=models.Operator.NULL,
            ),
            models.Filter(
                db_field=models.DbField.PAYLOAD,
                path='float_field',
                operator=models.Operator.BETWEEN,
                values=[0, '100'],
                settings={models.CAST_TO: 'float'},
            ),
            models.Filter(
                db_field=models.DbField.RECIPIENTS_SETTINGS,
                path='int_field',
                operator=models.Operator.BETWEEN,
                values=[0, None],
                settings={models.CAST_TO: 'int'},
            ),
        ],
    )

    assert complex_filter.sql == re.sub(
        '\\s\\s+',
        ' ',
        """AND (payload->>'text' = 'one'
                AND payload::text ILIKE
                 ('%global_search%' COLLATE "ru_RU.utf8")
                AND payload->'context'->'pages'->0->>'text'
                 ILIKE ('%one%' COLLATE "ru_RU.utf8")
                AND payload->'context'->'pages'->0->>'text'
                 ILIKE ('%two%' COLLATE "ru_RU.utf8")
                AND payload->'array' ? 'one'
                AND payload->'nothing' IS NULL
                AND (payload->>'float_field')::float <= 100::float
                AND (payload->>'float_field')::float >= 0::float
                """
        'AND (feeds_admin.recipient_group.group_settings->>\'int_field\''
        ')::int >= 0::int)',
    )
