from kikimr.public.sdk.python import client as ydb
from settings.settings import logger, YT_TOKEN


class db_ydb:
    def __init__(self):
        pass

    async def connect(self, query):
        connection_params = ydb.DriverConfig('ydb-ru.yandex.net:2135',
                                             database='/ru/suptech-taxi/prod/support-taxi',
                                             auth_token=YT_TOKEN)
        try:
            driver = ydb.Driver(connection_params)
            driver.wait(timeout=5)
            ydb_session = driver.table_client.session().create()
            result_sets = ydb_session.transaction(ydb.SerializableReadWrite()).execute(query, commit_tx=True)
            logger.info(result_sets)
            if result_sets:
                return result_sets[0].rows
            return result_sets
        except TimeoutError as e:
            logger.error(e)
