import typing

from crm_hub.generated.stq3 import stq_context
from crm_hub.generated.web import web_context
from crm_hub.repositories import process_results

AppContext = typing.Union[stq_context.Context, web_context.Context]


async def create_table_for_sending(
        context: AppContext, entities: typing.List[dict], table_name: str,
):
    columns = [
        process_results.Field('id', 'INTEGER', 'NOT NULL PRIMARY KEY'),
        *process_results.COMMON_FIELDS,
    ]

    sql_columns = []
    for column in columns:
        sql_columns.append(process_results.generate_field_string(column))

    async with context.pg.master_pool.acquire() as conn:
        query, binds = context.sqlt.drop_create_table(
            columns_data=sql_columns, table=table_name,
        )
        await conn.execute(query, *binds)

        query, binds = context.sqlt.insert_chunk(
            columns=('id',),
            lines=[entity['id'] for entity in entities],
            table=table_name,
        )
        await conn.execute(query, *binds)
