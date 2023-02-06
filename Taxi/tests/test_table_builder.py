import re

from core.table_builder import (generate_gp_table_create_statement,
                                generate_gp_grand_privilege_statement)
from core.transformation import yt_to_gp


def test_generate_gp_table_create_statement():
    yt_columns = {
        'col1': 'string',
        'col2': 'uint16',
    }

    expected_result = """
        create table test (
            col1 varchar, col2 int
        )
        distributed randomly;
    """
    expected_result = re.sub(r"\s+", " ", expected_result)

    statement = generate_gp_table_create_statement('test', yt_columns, yt_to_gp)

    assert expected_result == re.sub(r"\s+", " ", statement)


def test_generate_gp_grand_privilege_statement():
    expected_result = """
        grant SELECT, INSERT, TRUNCATE, UPDATE on table test to "robot";
    """
    expected_result = re.sub(r"\s+", " ", expected_result)
    statement = generate_gp_grand_privilege_statement('test', 'robot')
    assert expected_result == re.sub(r"\s+", " ", statement)

