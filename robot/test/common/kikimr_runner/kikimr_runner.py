import logging
import ydb


class KikimrRunner:
    def __init__(
            self,
            tables_yql,
            data_yql
    ):
        self._logger = logging.getLogger("kikimr_run_logger")
        self._tables_yql = tables_yql
        self._data_yql = data_yql
        self._driver = ydb.Driver(ydb.ConnectionParams(self.get_endpoint(), self.get_database()))
        self._driver.wait()

    def get_endpoint(self):
        with open('ydb_endpoint.txt') as r:
            endpoint = r.read()
        self._logger.info("get_endpoint: {}".format(endpoint))
        return endpoint

    def get_database(self):
        with open('ydb_database.txt') as r:
            database = r.read()
        self._logger.info("get_database: {}".format(database))
        return database

    def setup(self):
        self._logger.info("setting up schema")
        with open(self._tables_yql) as r:
            tables_yql_text = r.read()

        session = self._driver.table_client.session().create()
        session.execute_scheme(tables_yql_text)

        with session.transaction() as transaction:
            with open(self._data_yql) as r:
                data_yql_text = r.readlines()
            for line in data_yql_text:
                if not line.strip().startswith("--"):
                    transaction.execute(line)
            transaction.commit()

    def stop(self):
        self._logger.info("Shutting down")
        self._driver.stop()
