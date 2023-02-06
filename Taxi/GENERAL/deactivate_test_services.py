import abc
import asyncio
import collections
import datetime
import logging
import typing

import pymongo
import pymongo.errors

from taxi.maintenance import run

from corp_clients import crontasks
from corp_clients.generated.cron import cron_context as context_module

JOBS_LIMIT = 10
BULK_LIMIT = 100

logger = logging.getLogger(__name__)


class DeactivateServicesBulker(crontasks.Bulker):
    async def handle_bulk(self, bulk: list) -> None:
        mongo_bulk = []
        for client in bulk:
            service = client.pop('service_to_update')
            mongo_bulk.append(
                pymongo.UpdateOne(
                    {'_id': client['_id']},
                    {
                        '$set': {
                            f'services.{service}.is_active': False,
                            f'services.{service}.is_visible': False,
                        },
                        '$currentDate': {
                            'updated': True,
                            'updated_at': {'$type': 'timestamp'},
                        },
                    },
                ),
            )

        if mongo_bulk:
            await self.context.mongo.corp_clients.bulk_write(
                mongo_bulk, ordered=False,
            )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.flush()


class DeactivateServicesBroker(crontasks.Broker):
    SERVICE_NAME = ''

    def __init__(
            self,
            context: context_module.Context,
            bulker: crontasks.Bulker,
            stats: collections.Counter,
            jobs_limit: int,
    ) -> None:
        super().__init__(context, jobs_limit)
        self.bulker = bulker
        self.stats = stats

    async def process(self, value) -> None:

        client = value
        now = datetime.datetime.utcnow()

        self.stats[f'{self.SERVICE_NAME}_active_test_clients'] += 1

        service = client['services'].get(self.SERVICE_NAME, {})

        deactivate_date = service.get('deactivate_threshold_date')
        deactivate_ride = service.get('deactivate_threshold_ride')

        if deactivate_date and deactivate_date <= now:
            logger.info(
                'Service %s for client %s will be deactivated by date, '
                'threshold %s',
                self.SERVICE_NAME,
                client['_id'],
                deactivate_date,
            )
            self.stats[f'{self.SERVICE_NAME}_deactivated_by_date'] += 1
            client['service_to_update'] = self.SERVICE_NAME
            await self.bulker.add(client)

        elif deactivate_ride:
            total_rides = await self.get_rides_count(client['_id'])
            if total_rides >= deactivate_ride:
                logger.info(
                    'Service %s for client %s will be deactivated by rides, '
                    'threshold %s',
                    self.SERVICE_NAME,
                    client['_id'],
                    deactivate_ride,
                )
                self.stats[f'{self.SERVICE_NAME}_deactivated_by_ride'] += 1
                client['service_to_update'] = self.SERVICE_NAME
                await self.bulker.add(client)

    @abc.abstractmethod
    async def get_rides_count(self, client_id: str) -> int:
        pass


class DeactivateTaxiServicesBroker(DeactivateServicesBroker):
    SERVICE_NAME = 'taxi'

    async def get_rides_count(self, client_id: str) -> int:
        corp_orders_query = {
            'client_id': client_id,
            '$or': [
                {'status': 'finished', 'taxi_status': 'complete'},
                {'status': 'finished', 'taxi_status': 'cancelled'},
                {'status': 'cancelled', 'user_to_pay.ride': {'$gt': 0}},
            ],
        }

        taxi_rides = await self.context.mongo.secondary.corp_orders.count(
            corp_orders_query,
        )
        logger.info('Client %s has taxi %s rides', client_id, taxi_rides)

        return taxi_rides


class DeactivateCargoServicesBroker(DeactivateServicesBroker):
    SERVICE_NAME = 'cargo'

    async def get_rides_count(self, client_id: str) -> int:

        cargo_stats = await self.context.client_cargo_claims.corp_stats(
            client_id,
        )
        cargo_rides = cargo_stats['completed']
        logger.info('Client %s has %s cargo rides', client_id, cargo_rides)

        return cargo_rides


async def do_stuff(
        task_context: run.StuffContext,
        loop: asyncio.AbstractEventLoop,
        *,
        log_extra: typing.Optional[dict] = None,
):
    ctx = typing.cast(context_module.Context, task_context.data)
    logger.info('%s: starting task %s', ctx.unit_name, task_context.id)

    stats: typing.Counter[str] = collections.Counter()

    services = {
        'taxi': DeactivateTaxiServicesBroker,
        'cargo': DeactivateCargoServicesBroker,
    }

    for service, broker_class in services.items():
        cursor = ctx.mongo.secondary.corp_clients.find(
            {
                f'services.{service}.is_active': True,
                f'services.{service}.is_test': True,
            },
            projection=['yandex_login', f'services.{service}'],
            no_cursor_timeout=True,
        )

        async with DeactivateServicesBulker(ctx, BULK_LIMIT) as bulker:
            async with broker_class(ctx, bulker, stats, JOBS_LIMIT) as broker:
                async for client in cursor:
                    await broker.spawn(client)

    logger.info('Stats: %r', stats)
