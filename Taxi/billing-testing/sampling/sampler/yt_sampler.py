# coding: utf8

import asyncio
import datetime
import json
import logging
import os
from typing import Optional

import yql.api.v1.client as yql_api
import yt.yson as yson

logger = logging.getLogger(__name__)


class YtSampler:
    def __init__(
            self,
            sample_name: str,
            file_name: str,
            date: datetime.date,
            token_path: str,
            options: Optional[dict] = None,
    ):
        self.__sample_name = sample_name
        self.__options = options or {}
        self.__data_type = self.__options.get('type')
        options_file_name = self.__options.get('file_name')
        if options_file_name:
            self.__file_name = os.path.abspath(os.path.join(options_file_name))
        else:
            self.__file_name = file_name
        self.__date = date
        file = open(token_path, 'r')
        yql_token = file.read().strip()
        self.__yql_client = yql_api.YqlClient(token=yql_token, db='hahn')

    def process_row(self, row: dict):
        pass

    def __parse_row(self, column_names: list, values: list) -> dict:
        row = {}
        for idx, column_name in enumerate(column_names):
            data = values[idx]
            if isinstance(data, bytes):
                data = data.decode()
            if isinstance(data, str):
                try:
                    data = yson.loads(data.encode())
                except yson.YsonError:
                    pass
            row[column_name] = yson.yson_to_json(data)
            row[column_name] = yson.yson_to_json(data)
        if self.__data_type == 'doc':
            row = parse_doc_row(row)
        elif self.__data_type == 'park':
            row = parse_park_row(row)
        self.process_row(row)
        return row

    def __build_query(self) -> str:
        if self.__data_type == 'doc':
            return self.__build_doc_query()
        if self.__data_type == 'park':
            return self.__build_park_query()
        raise Exception(f'Query for {self.__data_type} is not implemented')

    def __build_park_query(self) -> str:
        ids_path = self.__options.get('ids')
        assert ids_path
        ids_path = os.path.join(ids_path)
        if os.path.isfile(ids_path):
            with open(ids_path) as file:
                ids = json.load(file)

        park_ids = ','.join(
            ['\'' + driver_id.split('_')[0] + '\'' for driver_id in ids],
        )
        where = f'WHERE `id` in ({park_ids})'
        logger.info(f'Params ({ids_path}): where: {where}')

        return f"""PRAGMA AnsiInForEmptyOrNullableItemsCollections;
            SELECT
                `id` as `_id`,
                `city`,
                `corp_vats`,
                `account_offer_contracts`,
                `account_offer_confirmed`,
                `account_cash_contract_currency`,
                `account_card_contract_currency`,
                `pay_donations_without_offer`,
                `automate_marketing_payments`
            FROM
                hahn.`//home/taxi/production/replica/mongo/struct/parks_private/parks`
            {where}"""

    def __build_doc_query(self) -> str:
        kind = self.__options.get('kind')
        count = self.__options.get('count', 100)
        zones = self.__options.get('zones')
        if zones:
            zones_str = '\',\''.join(zones)
            zones_condition = (
                'AND DictLookup(Yson::ConvertTo(`data`, '
                'ParseType(@@Dict<String,String?>@@)), \'zone\')'
                f' in (\'{zones_str}\')'
            )
        date = self.__date
        logger.info(
            f'Params: doc.kind = {kind}, date: {date}'
            f', zones: {zones}, count: {count}',
        )

        from_time = datetime.datetime.combine(date, datetime.time(0, 0))
        to_time = from_time + datetime.timedelta(days=1)

        return f"""PRAGMA AnsiInForEmptyOrNullableItemsCollections;
            SELECT *
            FROM
                hahn.`//home/taxi/production/replica/api/billing_docs/doc_monthly/{from_time.strftime('%Y-%m')}`
            WHERE
                `kind` = '{kind}'{zones_condition}
            AND event_at > {get_microseconds(from_time)}
            AND event_at < {get_microseconds(to_time)}
            LIMIT {count}"""

    async def sample_data(self) -> bool:
        try:
            query = self.__build_query()
            logger.debug(f'select_rows: {query}')
            title = f'YQL: sample {self.__sample_name}'
            request = self.__yql_client.query(
                query, syntax_version=1, title=title,
            )

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, request.run)
            query_results = await loop.run_in_executor(
                None, request.get_results,
            )

            logger.info('query completed')
            if query_results.errors or not query_results.is_success:
                logger.error(f'yql_query "{title}" failed!')
                for error in query_results.errors or []:
                    logger.error(str(error))
                return False

            results = []
            for table in query_results:
                table.fetch_full_data()
                column_names = table.column_names
                for row in table.rows:
                    parsed_row = self.__parse_row(column_names, row)
                    results.extend(
                        [
                            {'json': parsed_row}
                            if self.__data_type == 'doc'
                            else parsed_row,
                        ],
                    )
            if os.path.exists(self.__file_name):
                os.rename(self.__file_name, self.__file_name + '.bak')
            with open(self.__file_name, 'w') as file:
                ext = os.path.splitext(self.__file_name)[1]
                if ext == '.json':
                    json.dump(
                        results,
                        file,
                        indent=4,
                        sort_keys=True,
                        ensure_ascii=False,
                    )
                elif ext == '.jsonl':
                    for row in results:
                        file.write(json.dumps(row) + '\n')
                else:
                    logger.error(f'unknown result extension {ext}')
                    return False
            logger.info(f'{len(results)} rows saved')
            return True
        except Exception as error:  # pylint: disable=broad-except
            logger.error(f'Error: {str(error)}')
        return False


def convert_to_datetime_str(data: Optional[int]) -> str:
    if data:
        return datetime.datetime.fromtimestamp(data / 1_000_000).strftime(
            '%Y-%m-%dT%H:%M:%SZ',
        )
    return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')


def get_microseconds(time: datetime.datetime) -> int:
    return int(
        (time - datetime.datetime.fromtimestamp(0)).total_seconds()
        * 1_000_000,
    )


def parse_park_row(row: dict) -> dict:
    row['_id'] = str(row['_id'])
    return row


def parse_doc_row(row: dict) -> dict:
    return {
        'status': 'new',
        'kind': row.get('kind'),
        'service': row.get('service'),
        'external_obj_id': row.get('external_obj_id'),
        'external_event_ref': row.get('external_event_ref'),
        'event_at': convert_to_datetime_str(row.get('event_at')),
        'process_at': convert_to_datetime_str(row.get('process_at')),
        'journal_entries': [],
        'data': yson.yson_to_json(row.get('data')),
    }
