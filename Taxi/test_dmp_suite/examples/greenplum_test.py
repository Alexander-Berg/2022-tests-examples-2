"""
Этот модуль содержит рекомендации по написанию интеграционных тестов, связанных с GP.
"""
import re

import pytest

from dmp_suite.table import OdsLayout
from dmp_suite.greenplum import (
    GPTable,
    ExternalGPTable,
    ExternalGPLayout,
    resolve_meta,
)
from test_dmp_suite.greenplum import utils

# Кстати говоря, никогда не пишите `from connection.greenplum import connection` в тестах.
# В коде connection/greenplum.py объяснено, почему.
from connection import greenplum as gp


class ExampleTestTable(GPTable):
    """При определении таблиц предпочтительно использовать TestLayout."""

    __layout__ = utils.TestLayout(name="example")


def schema_is_randomized(table):
    return re.match("throwaway_[a-z0-9]{8}", resolve_meta(table).schema)


@pytest.mark.slow("gp")
def test_example_1():
    """
    Тесты, взаимодействующие с GP, рекомендуется помечать декоратором @pytest.mark.slow("gp")

    Для таких тестов префикс будет переопределён на случайный (уникальный для каждого теста).

    По завершении теста все созданные с этим префиксом схемы будут автоматически удалены.
    Созданные таблицы нет необходимости явно затирать, они будут удалены вместе со схемой.
    """
    assert schema_is_randomized(ExampleTestTable)
    with gp.connection.transaction():
        gp.connection.create_table(ExampleTestTable)
        # Схемы для STG-таблиц тоже префиксуются и тоже очищаются после теста.
        stg_meta = gp.connection.create_stg_table(ExampleTestTable)
    assert schema_is_randomized(stg_meta)


class ExampleTaxiOdsTable(GPTable):
    __layout__ = OdsLayout(name="example", source="source", prefix_key="taxi")


@pytest.mark.slow("gp")
def test_example_2():
    """
    Таблицы, импортированные из ETL-сервисов, также можно использовать в тестах.
    """
    assert schema_is_randomized(ExampleTaxiOdsTable)
    with gp.connection.transaction():
        gp.connection.create_table(ExampleTaxiOdsTable)


class ExampleDeprecatedTestTable(ExternalGPTable):
    __layout__ = ExternalGPLayout(schema="summary", table="example_deprecated")
