import pytest

from test_toll_roads import db_helper


@pytest.fixture
def db(web_context):
    return db_helper.DbHelper(web_context)
