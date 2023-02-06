from __future__ import annotations

import typing as tp

from test_abt import consts
from . import base


class FacetsBuilder(base.BaseBuilder):
    sys_facets: dict
    custom_facets: tp.List[dict]

    def __init__(self):
        self.sys_facets = consts.DEFAULT_SYS_FACETS
        self.custom_facets = []

    def set_sys_facet(self, name: str, column: str) -> FacetsBuilder:
        self.sys_facets[name] = {'column': column}
        return self

    def add_custom_facet(
            self,
            facet: str,
            columns: tp.List[str],
            agg: tp.Optional[str] = None,
    ) -> FacetsBuilder:
        self.custom_facets.append({'facet': facet, 'columns': columns})

        if agg:
            self.custom_facets[-1]['agg'] = agg

        return self

    def build(self) -> dict:
        result: dict = {'sys': self.sys_facets}
        if self.custom_facets:
            result['custom'] = self.custom_facets

        return result
