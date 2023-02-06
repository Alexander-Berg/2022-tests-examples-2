from __future__ import annotations

import typing as tp

from test_abt import consts


class PlotDataBuilder:
    def __init__(self):
        self._columns = []

    def add_column(
            self,
            col_name: str,
            bucket: int,
            group_id: int,
            value: int,
            date: tp.Optional[str] = None,
    ) -> PlotDataBuilder:
        self._columns.append(
            {
                consts.DEFAULT_BUCKET_COLUMN: bucket,
                consts.DEFAULT_GROUP_COLUMN: group_id,
                col_name: value,
            },
        )
        if date is not None:
            self._columns[-1].update({consts.DEFAULT_DATE_COLUMN: date})
        return self

    def remove_column(
            self, col_name: str, date: str, bucket: int, group_id: int,
    ) -> PlotDataBuilder:
        new_columns = []
        for column in self._columns:
            if all(
                    [
                        col_name in column,
                        column[consts.DEFAULT_DATE_COLUMN] == date,
                        column[consts.DEFAULT_BUCKET_COLUMN] == bucket,
                        column[consts.DEFAULT_GROUP_COLUMN] == group_id,
                    ],
            ):
                continue
            new_columns.append(column)
        self._columns = new_columns
        return self

    def build(self) -> tp.List[dict]:
        return self._columns
