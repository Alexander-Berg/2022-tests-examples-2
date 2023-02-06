import pymysql
import pytest


class MySQLConnection:
    def __init__(
            self,
            username: str = 'root',
            password: str = 'password',
            hostname: str = 'mysql.yandex.net',
            database: str = 'bigfood',
    ):
        self.connection = pymysql.connect(
            host=hostname,
            user=username,
            database=database,
            password=password,
            cursorclass=pymysql.cursors.DictCursor,
        )


@pytest.fixture
def mysql():
    instance = MySQLConnection()
    return instance.connection
