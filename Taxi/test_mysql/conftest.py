# pylint: disable=redefined-outer-name
import mysql_connection.generated.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['mysql_connection.generated.pytest_plugins']
