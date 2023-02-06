# coding: utf8
# pylint: disable=too-many-instance-attributes

import asyncio
import logging
import time

import aiohttp

from sibilla.test import context as ctx
from sibilla.test import event
from sibilla.test import test
from sibilla.utils import shell

logger = logging.getLogger(__name__)

SERVICE_WAIT_TIMEOUT = 360
SERVICE_WAIT_TIMEOUT_BEFORE_RETRY = 30
HOST_CONFIG_API = 'http://configs.taxi.yandex.net'
HOST_STQ_AGENT = 'http://stq-agent.taxi.yandex.net'
HOST_TERRITORIES_API = 'http://territories.taxi.yandex.net'


class Suite:
    @staticmethod
    def processors():
        return {}

    def __init__(self, tests, context: ctx.ContextData, options: dict = None):
        options = options or {}
        self.__tests = tests
        self.__context = context
        self.__prerequests = options.get('prerequests', {})
        self.__name = options.get('name', '')
        self.__description = options.get('description', '')

    async def _init_stq3(self, config):
        clients = [params['queue'] for name, params in config.items()]
        if not clients:
            return True
        logger.info('Init STQ: start')
        self.__context.init_stq3_queue(clients)
        future = [
            self.__context.stq3_put(
                queue=params['queue'],
                task_id=params['task_id'],
                eta=params['eta'],
            )
            for name, params in config.items()
        ]
        await asyncio.wait(future)
        logger.info('Init STQ: done')

    async def _init_configs(self, config: dict):
        logger.info('Update configs: start')
        try:
            clear_url = HOST_CONFIG_API + '/configs/clear'
            update_url = HOST_CONFIG_API + '/configs/update'
            async with self.__context.session.post(clear_url) as response:
                if response.status != 200:
                    return False
            async with self.__context.session.post(update_url, json=config):
                if response.status != 200:
                    return False
        except aiohttp.ClientError as error_info:
            msg = 'Could not update configs. Got error: %s' % str(error_info)
            raise RuntimeError(msg) from error_info
        logger.info('Update configs: done')

    async def _init_mongodb(self, config: dict):
        logger.info('Load mongodb dump: start')
        for dbname in config:
            await shell.restore_mongo(self.__context, dbname, config[dbname])
            await shell.restore_mongocollections(
                self.__context, dbname, config[dbname],
            )
        logger.info('Load mongodb dump: done')

    async def _init_postgres(self, config: dict):
        logger.info('Load postgres dump: start')
        for dbname in config:
            await shell.restore_psql(self.__context, config[dbname])
            await shell.restore_psql_tables(
                self.__context, dbname, config[dbname],
            )
        logger.info('Load postgres dump: done')

    async def query_service(self, url: str):
        msg = f'Try to connect to {url}: %s'
        try:
            async with self.__context.session.get(url) as resp:
                logger.debug(msg, f'OK, {resp.status}')
                return resp.status == 200, url
        except aiohttp.ClientError as error_info:
            logger.debug(msg, str(error_info))
            return False, url

    async def _init_services(self, services: list):
        """
        Ожидание доступности сервисов.
        Конфигурация каждого задается как
        {
            'url': 'Адрес, который должен вернуть 200 при get-запросе'
        }
        :param services:
        :return:
        """
        urls = {item['url'] for item in services}
        if not urls:
            return
        logger.info('Check service availability: start')
        startup_time = int(time.time())
        end_time = startup_time + SERVICE_WAIT_TIMEOUT
        unfinished_urls: set = set(urls)
        while int(time.time()) < end_time:
            futures = [self.query_service(url) for url in unfinished_urls]
            done, _ = await asyncio.wait(futures)
            for future in done:
                res, url = future.result()
                if res:
                    logger.info(' ... online: %s', url)
                    unfinished_urls.remove(url)
            if not unfinished_urls:
                logger.info('Check service availability: done')
                return
            await asyncio.sleep(SERVICE_WAIT_TIMEOUT_BEFORE_RETRY)
        for url in sorted(list(unfinished_urls)):
            logger.info(' [!] offline: %s', url)
        raise RuntimeError('Expected services not available')

    async def before_suite(self):
        """
        Главными операциями по подготовке тестов являются:
        - ожидание достуности сервисов
        :return:
        """
        services = self.__prerequests.get('services', [])
        if services:
            await self._init_services(services)
        postgres = self.__prerequests.get('postgres', {})
        if postgres:
            logger.info('Fill runtime database content')
            await self._init_postgres(postgres)

    async def after_suite(self):
        pass

    async def fill_db(self) -> bool:
        try:
            mongo = self.__prerequests.get('mongo', {})
            if mongo:
                await self._init_mongodb(mongo)
            configs = self.__prerequests.get('configs', {})
            if configs:
                await self._init_configs(configs)
            return True
        except RuntimeError as error_info:
            msg = 'Could not fill database: %s' % str(error_info)
            logger.error(msg)
            return False

    async def fill_services(self):
        try:
            services = [
                {'url': HOST_STQ_AGENT + '/ping'},
                {'url': HOST_TERRITORIES_API + '/ping'},
            ]
            await self._init_services(services)
            stq3 = self.__prerequests.get('stq3', {})
            if stq3:
                await self._init_stq3(stq3)
            return True
        except RuntimeError as error_info:
            msg = 'Could not fill stq: %s' % str(error_info)
            logger.error(msg)
            return False

    async def exec(self):
        """
        Порядок исполнения тестов задается в генераторе,
        который передается в конструкторе класса
        :return:
        """
        await self.__context.logger.log(
            event.EVENT_SUITE_START,
            name=self.__name,
            description=self.__description,
        )
        try:
            await self.before_suite()
        except RuntimeError as error_info:
            msg = 'Could not initialize suite: %s' % str(error_info)
            logger.error(msg)
            await self.__context.logger.log(event.EVENT_SUITE_RESULT_FAIL, msg)
            return 0
        success = 0
        total = 0
        for raw_test_data in self.__tests:
            total += 1
            test_obj = test.Test(ctx=self.__context, **raw_test_data)
            # success test counter (bool to int)
            success += int(await test_obj.exec())
        await self.after_suite()
        if success == total:
            await self.__context.logger.log(
                event.EVENT_SUITE_RESULT_SUCCESS,
                'Test suite complete with success',
            )
        else:
            await self.__context.logger.log(
                event.EVENT_SUITE_RESULT_FAIL, 'Test suite failed',
            )
        await self.__context.logger.log(
            event.EVENT_SUITE_FINISH, 'Test suite finish',
        )
        return success == total
