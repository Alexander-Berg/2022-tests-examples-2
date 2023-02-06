# pylint: disable=redefined-outer-name
import dataclasses
import pathlib
import typing


_DEFAULT_TABLE_ATTRIBUTES = {'replication_factor': 1}


@dataclasses.dataclass(frozen=True)
class Table:
    path: str
    attributes: dict
    initial_data: list = dataclasses.field(default_factory=list)

    @property
    def dynamic(self):
        return self.attributes.get('dynamic')


@dataclasses.dataclass(frozen=True)
class Schema:
    tables: typing.List[Table]


class YtState:
    def __init__(self, schema: Schema):
        self._initialized = False
        self._schema: Schema = schema

    def initialize(self, yt_client, force=False):
        if force and yt_client.exists('//home'):
            yt_client.remove('//home/*')
        if not self._initialized or force:
            self._populate_schema(yt_client, force=force)
            self._initialized = True

    def _populate_schema(self, yt_client, force=False):
        for table in self._schema.tables:
            if force:
                yt_client.remove(table.path, force=True)
                self._create_table(yt_client, table)
            else:
                if not yt_client.exists(table.path):
                    self._create_table(yt_client, table)
                elif table.dynamic:
                    self._flush_dyn_table(yt_client, table.path)
            self._fill_data(yt_client, table)

    @staticmethod
    def _create_table(yt_client, table: Table):
        attributes = (table.attributes or {}).copy()
        for key, value in _DEFAULT_TABLE_ATTRIBUTES.items():
            attributes.setdefault(key, value)
        yt_client.create(
            'table', table.path, recursive=True, attributes=attributes,
        )
        if table.dynamic:
            yt_client.mount_table(table.path, sync=True)

    @classmethod
    def _fill_data(cls, yt_client, table: Table):
        if table.dynamic:
            cls._ensure_dyn_table_mounted(yt_client, table.path)
            yt_client.insert_rows(table.path, table.initial_data)
        else:
            yt_client.write_table(table.path, table.initial_data)

    @classmethod
    def _flush_dyn_table(cls, yt_client, path):
        cls._ensure_dyn_table_mounted(yt_client, path)
        yt_client.delete_rows(
            path,
            (
                {key: doc[key] for key in yt_client.get(path + '/@sorted_by')}
                for doc in yt_client.select_rows(f'* from [{path}]')
            ),
        )

    @staticmethod
    def _ensure_dyn_table_mounted(yt_client, path):
        if yt_client.get(path + '/@tablet_state') != 'mounted':
            yt_client.mount_table(path, sync=True)


@dataclasses.dataclass
class YTServiceState:
    service_schemas: typing.List[pathlib.Path]
    initialized: bool = dataclasses.field(init=False, default=False)
