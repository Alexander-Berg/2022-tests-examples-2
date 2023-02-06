from __future__ import annotations

import typing as tp

from test_abt import consts
from . import base


class MeasuresBuilder(base.BaseBuilder):
    revision_col_name: str = consts.DEFAULT_REVISION_COLUMN
    _revision_id: int

    group_col_name: str = consts.DEFAULT_GROUP_COLUMN
    _group_id: int

    buckets_col_name: str = consts.DEFAULT_BUCKET_COLUMN
    _buckets_count: int

    columns: tp.Dict[str, tp.List[float]]

    def __init__(self, revision_id: int, group_id: int, buckets_count: int):
        self.revision_id = revision_id
        self.group_id = group_id
        self._buckets_count = buckets_count
        self.columns = {}

    def add_column(self, col_name, values) -> MeasuresBuilder:
        values = list(values)
        assert col_name not in self.columns, 'Column already added'
        assert self._buckets_count == len(values), (
            f'Number of buckets doesn\'t match with previous columns. '
            f'{len(values)} != {self._buckets_count}'
        )
        self.columns[col_name] = [float(val) for val in values]
        return self

    def build(self) -> tp.List[dict]:
        ret = []
        for i in range(self._buckets_count):
            row: tp.Dict[str, tp.Any] = {
                self.revision_col_name: self.revision_id,
                self.group_col_name: self.group_id,
                self.buckets_col_name: i,
            }
            for col, values in self.columns.items():
                row[col] = values[i]

            ret.append(row)
        return ret
