import dataclasses
import enum
import typing

import pytest


class YtTableType(enum.Enum):
    Retail = 'retail'
    Restaurants = 'restaurants'


@dataclasses.dataclass
class YtTable:
    path: str
    promotion: str
    type: YtTableType


def adverts_cache_config(tables: typing.List[YtTable]):
    config_tables = []
    for table in tables:
        config_tables.append(
            {
                'path': table.path,
                'promotion': table.promotion,
                'schema_type': table.type.value,
            },
        )
    return pytest.mark.config(
        EATS_ADVERTS_GOODS_ADVERTS_CACHE_SETTINGS={
            'enabled': True,
            'tables': config_tables,
        },
    )
