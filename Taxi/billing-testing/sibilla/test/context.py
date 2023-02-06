# coding: utf8
# pylint: disable=too-many-instance-attributes

import asyncio

import aiohttp

from sibilla import processing
from sibilla.test import event
from taxi import config
from taxi import db as taxi_db
from taxi import secdist
from taxi import settings as taxi_settings
from taxi.clients import configs
from taxi.clients import tvm
from taxi.stq import client


class ContextData:
    @classmethod
    async def create(
            cls,
            loop: asyncio.AbstractEventLoop,
            logger: event.EventCollector,
            suite_path: str,
    ):
        self = ContextData(loop, suite_path, logger)
        await self.init()
        return self

    def __init__(
            self,
            loop: asyncio.AbstractEventLoop,
            suite_path: str,
            logger: event.EventCollector,
    ):
        self.suite_path = suite_path
        self.loop = loop
        self.logger = logger
        self._secdist_object = secdist.load_secdist()
        self._secdist_ro_object = secdist.load_secdist_ro()
        self._db = taxi_db.create_db(
            self._secdist_object['mongo_settings'],
            self._secdist_ro_object['mongo_settings'],
            loop=self.loop,
        )
        self._settings = taxi_settings.Settings()
        self.session = aiohttp.ClientSession()
        configs_client = configs.ConfigsApiClient(self.session, self._settings)
        self.config = config.Config(
            self._db, settings=self._settings, configs_client=configs_client,
        )
        self.tvm_client = tvm.TVMClient(
            service_name='sibilla',
            secdist=self._secdist_object,
            config=self.config,
            session=self.session,
        )
        self.container = processing.Storage()

    async def init(self) -> None:
        await self.config.init_cache()

    def init_stq3_queue(self, clients):
        client.init(
            self._secdist_object,
            clients=clients,
            session=self.session,
            app_config=self.config,
            app_settings=self._settings,
            tvm_client=self.tvm_client,
        )

    async def stq3_put(self, queue, task_id, eta):
        await client.put(
            queue=queue,
            task_id=task_id,
            eta=eta,
            kwargs={'log_extra': None},
            loop=self.loop,
        )

    def pgaas_connections(self, name: str, shard: int) -> str:
        pg_section = self._secdist_object['postgresql_settings']['databases']
        if name in pg_section:
            for conn in pg_section[name]:
                if conn['shard_number'] == shard:
                    return conn['hosts'][0]
        raise RuntimeError('No viable host for {}:{}'.format(name, shard))

    def mongo_conn(self, name):
        return self._secdist_object['mongo_settings'][name]

    async def close(self):
        """
        Call before shutdown
        :return:
        """
        await self.session.close()
