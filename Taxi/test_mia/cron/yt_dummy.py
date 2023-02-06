# pylint: disable=invalid-name

import logging


logger = logging.getLogger(__name__)


class OperationDummy:
    def __init__(self, id_, attributes):
        self.id = id_
        self.attributes = attributes


class OperationTrackerDummy:
    def add_by_id(self, operation_id, client):
        pass

    def wait_all(self):
        if YtWrapperDummy.ruin_await_count > 0:
            YtWrapperDummy.ruin_await_count -= 1
            raise Exception(
                'Fake await operations exception, ruins remain: ',
                YtWrapperDummy.ruin_await_count,
            )

    def get_operation_count(self):
        return 0


class YtWrapperDummy:
    ruin_await_count = 0

    def __init__(
            self,
            tables,
            operations=None,
            fail_requests=None,
            ruin_await_count=0,
    ):
        self.yt_tables = tables
        self.operations = operations if operations else {}
        self.sync_yt = None

        self.fail_requests = fail_requests if fail_requests else set()
        YtWrapperDummy.ruin_await_count = ruin_await_count

    async def create_out_table(self, table_name):
        name = table_name + str(len(self.yt_tables))
        self.yt_tables[name] = []
        return name

    async def run_map(self, func, tables, out_table):
        for query_id in func.id_to_filter:
            if query_id in self.fail_requests:
                raise Exception('Fake run_map exception')

        for table in tables:
            for row in self.yt_tables[table]:
                for found in func(row):
                    self.yt_tables[out_table].append(found)
        self.operations['test_id'] = OperationDummy(
            id_='test_id',
            attributes={'spec': {'output_table_paths': [out_table]}},
        )
        return self.operations['test_id']

    async def read_table(self, table):
        return self.yt_tables[table]

    async def row_count(self, table):
        return len(self.yt_tables[table])

    async def lookup_rows(
            self, path, conditions, column_names, interval_conditions=None,
    ):
        result = []
        for row in self.yt_tables.get(path, []):
            for condition in conditions:
                if await self._check_row(row, condition, interval_conditions):
                    if column_names:
                        result.append({k: row.get(k) for k in column_names})
                    else:
                        result.append(row)
                    break
        return result

    async def select_rows(
            self,
            columns,
            table_path,
            conditions,
            interval_conditions=None,
            cluster_group='-',
            log_request=False,
    ):
        formatted_indexes = []
        for key, values in conditions.items():
            for value in values:
                if isinstance(value, str):
                    value = value.strip('"')
                formatted_indexes.append({key: value})
        return await self.lookup_rows(
            table_path, formatted_indexes, columns, interval_conditions,
        )

    async def _check_row(self, row, condition, interval_conditions=None):
        for key, value in condition.items():
            if row[key] != value:
                return False
        for interval_condition in interval_conditions or []:
            value = row[interval_condition.field_name]
            value_from = int(interval_condition.value_from)
            value_to = int(interval_condition.value_to)
            if value > value_to or value < value_from:
                return False
        return True

    async def get_operation(self, operation_id, attributes):
        return self.operations[operation_id].attributes

    async def get_operations_tracker(self):
        return OperationTrackerDummy()


class YtLocalDummy:
    def __init__(self, yt_client) -> None:
        self.yt_client = yt_client

    async def lookup_rows(self, path, conditions, column_names):
        return list(
            self.yt_client.lookup_rows(
                path, conditions, column_names=column_names,
            ),
        )

    async def select_rows(self, columns, table_path, conditions, **kwargs):
        sql_columns = ', '.join(columns)

        sql_path = f'[{table_path}]'

        sql_conditions = []
        for key, values in conditions.items():
            filtered_values = []
            for value in values:
                if value:
                    filtered_values.append(str(value))
            filtered_values = list(set(filtered_values))
            if not filtered_values:
                continue
            sql_conditions.append(f'{key} IN ({", ".join(filtered_values)})')
        if not sql_conditions:
            return []
        sql_condition = ' AND '.join(sql_conditions)
        sql_query = f'{sql_columns} FROM {sql_path} WHERE {sql_condition}'
        return list(self.yt_client.select_rows(sql_query))
