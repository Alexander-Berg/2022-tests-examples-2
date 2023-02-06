import pathlib

import pytest


@pytest.fixture(name='static_path')
def _static_path():
    return pathlib.Path(__file__).parent.joinpath('static/test_sql')


def test_default(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository[
        'services/test-service/src/some_query.sql'
    ] = """
SELECT
    id
FROM
    "table"
"""

    generate_services_and_libraries(
        default_repository, 'test_sql/base', default_base,
    )


def test_duplicates(
        generate_services_and_libraries,
        default_repository,
        default_base,
        capsys,
):
    default_repository.update(
        {
            'services/test-service/src/some_query.sql': (
                'SELECT name FROM people'
            ),
            'services/test-service/src/view/some_query.yql': (
                'SELECT name FROM yql_people'
            ),
        },
    )

    with pytest.raises(SystemExit):
        generate_services_and_libraries(
            default_repository, 'test_sql/base', default_base,
        )
