import pytest

DB = 'hiring_data_markup'


@pytest.mark.pgsql(
    'hiring_data_markup',
    queries=[
        """
        INSERT INTO hiring_data_markup.endpoints
            ("name", "description", "markup", "section", "limit")
        VALUES
            ('endpoint', 'description', \'{\"data_D\" : 1}\'::jsonb,
            'section', 20);
        INSERT INTO hiring_data_markup.sections
            ("name", "description", "markup")
        VALUES
            ('section', 'description', \'{\"section_data\" : 1}\'::jsonb)
        """,
    ],
)
async def test_new_bd(pgsql, web_context):
    query = 'SELECT * FROM hiring_data_markup.endpoints '
    async with web_context.postgresql() as connection:
        assert await connection.fetch(query)
    query = 'SELECT * FROM hiring_data_markup.sections '
    async with web_context.postgresql() as connection:
        assert await connection.fetch(query)
