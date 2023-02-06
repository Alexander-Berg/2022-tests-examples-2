from __future__ import annotations

import copy
import typing as tp

from test_abt import consts
from . import base


class PrecomputesTableSchemaBuilder(base.BaseBuilder):
    fields: tp.List[dict]

    def __init__(self):
        self.fields = copy.deepcopy(consts.DEFAULT_PRECOMPUTES_TABLE_SCHEMA)

    def add_column(
            self,
            col_name: str,
            col_type: str = consts.DEFAULT_MEASURES_COL_TYPE,
            sort_order: tp.Optional[str] = None,
    ) -> PrecomputesTableSchemaBuilder:
        field = {'name': col_name, 'type': col_type}

        if sort_order is not None:
            field['sort_order'] = sort_order

        self.fields.append(field)

        return self

    def build(self) -> tp.List[dict]:
        return self.fields


class PrecomputesTableAttributesBuilder(base.BaseBuilder):
    is_sorted: bool = consts.DEFAULT_IS_SORTED
    is_dynamic: bool = consts.DEFAULT_IS_DYNAMIC
    sorted_by: tp.List[str]

    def __init__(self):
        self.sorted_by = consts.DEFAULT_SORTED_BY

    def set_is_sorted(
            self, is_sorted: bool,
    ) -> PrecomputesTableAttributesBuilder:
        self.is_sorted = is_sorted
        return self

    def set_is_dynamic(
            self, is_dynamic: bool,
    ) -> PrecomputesTableAttributesBuilder:
        self.is_dynamic = is_dynamic
        return self

    def set_sorted_by(
            self, sorted_by: tp.List[str],
    ) -> PrecomputesTableAttributesBuilder:
        self.sorted_by = sorted_by
        return self

    def build(self) -> dict:
        return {
            'is_sorted': self.is_sorted,
            'is_dynamic': self.is_dynamic,
            'sorted_by': self.sorted_by,
        }
