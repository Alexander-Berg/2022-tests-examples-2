import argparse
import asyncio
import logging


from taxi import db as taxi_db
from taxi import secdist
from taxi import settings as taxi_settings
from taxi.clients import billing_v2
from taxi.clients import configs
from taxi.clients import http_client
from taxi.clients import tvm

from taxi_corp import config
from taxi_corp import settings


logger = logging.getLogger('create-test-contract')

OPERATOR = '0'


class Context:
    def __init__(self, loop):
        self.secdist = secdist.load_secdist()
        self.secdist_ro = secdist.load_secdist_ro()
        self.db = taxi_db.create_db(
            self.secdist.get('mongo_settings', {}),
            self.secdist_ro.get('mongo_settings', {}),
        )

        self.session = http_client.HTTPClient(loop=loop)
        self.settings = taxi_settings.Settings()
        configs_client = configs.ConfigsApiClient(self.session, self.settings)
        self.config = config.Config(
            settings=self.settings,
            configs_client=configs_client,
            service_name=settings.SERVICE_NAME,
        )
        self.tvm = tvm.TVMClient(
            service_name='corp-cabinet',
            secdist=self.secdist,
            config=self.config,
            session=self.session,
        )
        self.billing = billing_v2.BalanceClient(
            settings.BALANCE_XMLRPC_API_HOST,
            loop=loop,
            session=self.session,
            tvm_client=self.tvm,
        )

    async def __aenter__(self):
        await self.config.refresh_cache()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()


async def create_person(ctx, billing_id) -> int:
    return await ctx.billing.create_person(
        OPERATOR,
        {
            'client_id': billing_id,
            'person_id': 0,
            'type': 'ph',
            'lname': 'person_last_name',
            'fname': 'person_first_name',
            'mname': 'person_patr_name',
            'phone': '+79990002233',
            'email': 'ya@ya.ru',
        },
    )


async def create_common_contract(
        ctx, billing_id, person_id, services, contract_type='postpaid',
) -> int:
    params = {
        'client_id': billing_id,
        'person_id': person_id,
        'services': services,
        'manager_uid': '389886597',
        'currency': 'RUR',
        'firm_id': 13,
        'nds': 20,
        'country': '213',
        'signed': 1,
    }

    if contract_type == 'postpaid':
        params['payment_type'] = 3
        params['payment_term'] = 15
        params['tickets'] = 'TAXIDOCS-9'
        params['partner_credit'] = 1
        params['credit_type'] = 1
    else:
        params['payment_type'] = 2
    return await ctx.billing.create_common_contract(OPERATOR, **params)


async def create_contract(ctx, args):
    client = await ctx.db.secondary.corp_clients.find_one(
        {'_id': args.client_id},
    )
    billing_id = client.get('billing_id')
    if not billing_id:
        raise Exception('Unknown billing_id')

    logger.info('billing_id: %s', billing_id)

    person_id = await create_person(ctx, billing_id)
    contract = await create_common_contract(
        ctx,
        billing_id,
        person_id,
        args.service_ids,
        contract_type=args.payment,
    )
    logger.debug('Contract: {}'.format(contract))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', type=str, default='INFO')
    parser.add_argument('--client_id', type=str, required=True)
    parser.add_argument('--service_ids', type=int, nargs='+', required=True)
    parser.add_argument(
        '--payment',
        type=str,
        choices=['prepaid', 'postpaid'],
        default='postpaid',
    )
    return parser.parse_args()


async def main(loop):
    args = parse_args()
    logging.basicConfig(level=args.log)
    logger.info('Start script: %r', args)
    if taxi_settings.ENVIRONMENT == taxi_settings.PRODUCTION:
        print('this script is only for testing env.')
        return

    async with Context(loop) as context:
        await create_contract(context, args)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
