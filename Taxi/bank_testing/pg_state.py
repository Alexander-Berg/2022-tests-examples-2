import datetime
import json
import typing


class PgState:
    class Table:
        def __init__(
                self,
                cluster_name: str,
                table_name: str,
                id_column: str,
                columns: typing.List[str],
                defaults: dict,
                converters: dict,
        ):
            assert id_column in columns
            assert set(converters.keys()) <= set(columns)
            assert set(defaults.keys()) <= set(columns)
            self.cluster_name = cluster_name
            self.table_name = table_name
            self.id_column = id_column
            self.columns = columns
            self.converters = converters
            self.defaults = defaults

        def convert_row(self, row: dict) -> dict:
            return {
                col_id: (
                    self.converters[col_id].to_representation(val)
                    if col_id in self.converters
                    else val
                )
                for col_id, val in row.items()
            }

        def unconvert_row(self, row: dict) -> dict:
            return {
                col_id: (
                    self.converters[col_id].from_representation(val)
                    if col_id in self.converters
                    else val
                )
                for col_id, val in row.items()
            }

    def __init__(self, pgsql, default_cluster):
        self._pgsql = pgsql
        self._default_cluster = default_cluster
        self._tables = {}
        self._expected_state = {}

    def add_table(
            self,
            table_name: str,
            id_column: str,
            columns: typing.List[str],
            alias: typing.Union[str, None] = None,
            defaults: typing.Union[dict, None] = None,
            converters: typing.Union[dict, None] = None,
            cluster_name: typing.Union[str, None] = None,
    ):
        if alias is None:
            alias = table_name
        if converters is None:
            converters = {}
        if cluster_name is None:
            cluster_name = self._default_cluster
        if defaults is None:
            defaults = {}

        assert alias not in self._tables
        self._tables[alias] = self.Table(
            cluster_name, table_name, id_column, columns, defaults, converters,
        )
        self._expected_state[alias] = {}

    def expect_insert(self, table_alias: str, row: dict):
        table = self._tables[table_alias]
        expected = self._expected_state[table_alias]
        row = table.defaults | row
        assert set(table.columns) == set(row.keys())

        row_id = row[table.id_column]
        assert row_id not in expected, f'Row {row_id} already expected'
        expected[row_id] = row

    def expect_update(self, table_alias: str, row_id, changes: dict):
        table = self._tables[table_alias]
        expected = self._expected_state[table_alias]
        assert row_id in expected
        assert table.id_column not in changes
        assert set(table.columns) >= set(changes.keys())
        for column_name, value in changes.items():
            if not isinstance(value, Arbitrary) and not isinstance(
                    expected[row_id][column_name], Arbitrary,
            ):
                assert expected[row_id][column_name] != value, (
                    f'Value "{value}" already expected'
                    f' in column `{column_name}`'
                    f' of row "{row_id}"'
                )
        expected[row_id].update(changes)

    def expect_delete(self, table_alias: str, row_id):
        expected = self._expected_state[table_alias]
        del expected[row_id]

    def do_insert(self, table_alias: str, row: dict):
        table = self._tables[table_alias]
        expected = self._expected_state[table_alias]
        cursor = self._pgsql[table.cluster_name].cursor()
        assert set(row.keys()) <= set(table.columns)

        row = table.unconvert_row(row)
        row_columns_quoted = ','.join([f'"{col}"' for col in row.keys()])
        all_columns_quoted = ','.join([f'"{col}"' for col in table.columns])
        values_placeholders = ','.join(['%s'] * len(row))
        cursor.execute(
            f'INSERT INTO {table.table_name}({row_columns_quoted})'
            f'VALUES ({values_placeholders}) RETURNING {all_columns_quoted}',
            tuple(row.values()),
        )
        inserted_rows = [
            table.convert_row(dict(zip(table.columns, inserted_row)))
            for inserted_row in cursor
        ]
        assert len(inserted_rows) == 1
        expected[inserted_rows[0][table.id_column]] = inserted_rows[0]

    def read_table(self, table_alias: str) -> dict:
        table = self._tables[table_alias]
        cursor = self._pgsql[table.cluster_name].cursor()
        cursor.execute(f'SELECT * FROM {table.table_name}')
        columns = [column.name for column in cursor.description]
        assert set(columns) == set(table.columns)
        # pylint: disable=consider-using-dict-comprehension
        rows = [table.convert_row(dict(zip(columns, row))) for row in cursor]
        return {row[table.id_column]: row for row in rows}

    def expected(self) -> dict:
        return self._expected_state

    def actual(self) -> dict:
        # pylint: disable=consider-iterating-dictionary
        return {
            table_name: self.read_table(table_name)
            for table_name in self._tables.keys()
        }

    def assert_valid(self):
        assert self.expected() == self.actual()


#  ======== Helpers  ========


class DateTimeAsStr:
    def __init__(
            self,
            fmt: str = '%Y-%m-%dT%H:%M:%S',
            timezone: datetime.timezone = datetime.timezone.utc,
    ):
        self.fmt = fmt
        self.timezone = timezone

    def to_representation(self, value: typing.Union[datetime.datetime, None]):
        if isinstance(value, datetime.datetime):
            return value.astimezone(self.timezone).strftime(self.fmt)

        assert value is None, 'Unexpected type: ' + str(type(value))
        return None

    def from_representation(self, value: typing.Union[str, None]):
        if isinstance(value, str):
            return datetime.datetime.strptime(value, self.fmt).replace(
                tzinfo=self.timezone,
            )

        assert value is None, 'Unexpected type: ' + str(type(value))
        return None


class JsonbAsDict:
    def __init__(self):
        pass

    def to_representation(self, value: typing.Union[dict, None]):
        return value

    def from_representation(self, value: typing.Union[dict, None]):
        if value is None:
            return None
        return json.dumps(value)


class Arbitrary:
    def __init__(self, not_null=False):
        self.not_null = not_null

    def __eq__(self, other):
        if other is None:
            return not self.not_null
        return True
