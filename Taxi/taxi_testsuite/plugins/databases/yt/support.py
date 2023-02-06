# pylint: disable=redefined-outer-name
import dataclasses
import pathlib
import time
import typing

_DEFAULT_TABLE_ATTRIBUTES = {'replication_factor': 1}
_MOUNT_TABLE_RETRIES_NUM = 0
_MOUNT_TABLE_RETRY_SLEEP_TIME = 0.2


@dataclasses.dataclass(frozen=True)
class TableData:
    data: list
    yt_format: typing.Optional[dict]


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
                table_exists = yt_client.exists(table.path)
                if table.dynamic and table_exists:
                    table_exists = self._flush_dyn_table(yt_client, table.path)
                if not table_exists:
                    self._create_table(yt_client, table)
            self._fill_data(yt_client, table)

    @classmethod
    def _create_table(cls, yt_client, table: Table):
        attributes = (table.attributes or {}).copy()
        for key, value in _DEFAULT_TABLE_ATTRIBUTES.items():
            attributes.setdefault(key, value)
        yt_client.create(
            'table', table.path, recursive=True, attributes=attributes,
        )
        if table.dynamic:
            cls._ensure_dyn_table_mounted(yt_client, table.path)

    @classmethod
    def _fill_data(cls, yt_client, table: Table):
        import yt.wrapper

        for initial_data_part in table.initial_data:
            initial_data = initial_data_part.data
            yt_format = None
            if initial_data_part.yt_format is not None:
                initial_data = _encode_value(initial_data)
                yt_format = yt.wrapper.YsonFormat(
                    **initial_data_part.yt_format,
                )

            if table.dynamic:
                cls._ensure_dyn_table_mounted(yt_client, table.path)
                yt_client.insert_rows(
                    table.path, initial_data, format=yt_format,
                )
            else:
                yt_client.write_table(
                    table.path, initial_data, format=yt_format,
                )

    @classmethod
    def _flush_dyn_table(cls, yt_client, path):
        cls._ensure_dyn_table_mounted(yt_client, path)
        schema = yt_client.get(path + '/@schema')
        sorted_by = [
            key['name']
            for key in schema
            if key.get('sort_order') and not key.get('expression')
        ]
        if not sorted_by:
            # https://yt.yandex-team.ru/docs/description/dynamic_tables/ordered_dynamic_tables
            yt_client.remove(path, force=True)
            return False
        yt_client.delete_rows(
            path,
            (
                {key: doc[key] for key in sorted_by}
                for doc in yt_client.select_rows(
                    f'{", ".join(sorted_by)} from [{path}]',
                )
            ),
        )
        return True

    @classmethod
    def _ensure_dyn_table_mounted(
            cls,
            yt_client,
            path,
            *,
            retries=_MOUNT_TABLE_RETRIES_NUM,
            sleep_time=_MOUNT_TABLE_RETRY_SLEEP_TIME,
    ):
        import yt.wrapper.errors

        def _mount_table():
            if yt_client.get(path + '/@tablet_state') != 'mounted':
                yt_client.mount_table(path, sync=True)

        for _ in range(retries):
            try:
                _mount_table()
                return
            except yt.wrapper.errors.YtHttpResponseError:
                time.sleep(sleep_time)
        _mount_table()


@dataclasses.dataclass
class YTServiceState:
    service_schemas: typing.List[pathlib.Path]
    initialized: bool = dataclasses.field(init=False, default=False)


def _encode_value(value):
    if isinstance(value, str):
        return value.encode()
    if isinstance(value, dict):
        return {key.encode(): _encode_value(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_encode_value(item) for item in value]
    return value
