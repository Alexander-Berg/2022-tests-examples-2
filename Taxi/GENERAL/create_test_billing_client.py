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
from taxi.logs import auto_log_extra

from taxi_corp import config
from taxi_corp import settings


logger = logging.getLogger('create-test-billing-client')

OPERATOR = '0'


class Context:
    def __init__(self, loop, log_extra):
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
        self.log_extra = log_extra

    async def __aenter__(self):
        await self.config.refresh_cache()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()


async def create_client(ctx) -> int:
    return await ctx.billing.create_client(
        OPERATOR,
        {
            'NAME': 'клиент корпоративного такси в балансе',
            'EMAIL': 'ya@ya.ru',
            'PHONE': '+79990002233',
            'CITY': 'Москва',
            'REGION_ID': '225',
            'CURRENCY': 'RUB',
        },
    )


async def create_person(ctx, client_id) -> int:
    return await ctx.billing.create_person(
        OPERATOR,
        {
            'client_id': client_id,
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
        ctx, client_id, person_id, services, payment='postpaid',
) -> int:
    params = {
        'client_id': client_id,
        'person_id': person_id,
        'services': services,
        'manager_uid': '389886597',
        'currency': 'RUR',
        'firm_id': 13,
        'nds': 20,
        'country': '213',
        'signed': 1,
    }

    if payment == 'prepaid':
        params['payment_type'] = 2
    elif payment == 'postpaid':
        params['payment_type'] = 3
        params['payment_term'] = 15
        params['tickets'] = 'TAXIDOCS-9'
        params['partner_credit'] = 1
        params['credit_type'] = 1
    else:
        raise ValueError('Unknown payment type: {}'.format(payment))

    return await ctx.billing.create_common_contract(OPERATOR, **params)


async def create_offer(
        ctx, client_id, person_id, services, payment='postpaid',
) -> int:
    params = {
        'client_id': client_id,
        'person_id': person_id,
        'operator_uid': OPERATOR,
        'currency': 'RUB',
        'firm_id': 13,
        'manager_uid': '389886597',
        'services': services,
        'country': '225',
        'region': '213',
        'offer_confirmation_type': 'no',
    }

    if payment == 'prepaid':
        params['payment_type'] = 2
    elif payment == 'postpaid':
        params['payment_type'] = 3
        params['payment_term'] = 180
    else:
        raise ValueError('Unknown payment type: {}'.format(payment))
    return await ctx.billing.create_offer(**params)


async def create_test_billing_client(ctx, args):
    client_id = await create_client(ctx)
    logger.debug('Billing client id: {}'.format(client_id))

    info = await ctx.billing.get_passport_by_login(OPERATOR, args.login)
    customer_uid = info['Uid']

    try:
        association = await ctx.billing.create_user_client_association(
            OPERATOR, client_id, customer_uid,
        )
        logger.debug('Association: {}'.format(association))
    except billing_v2.UserClientAssociationError as err:
        logger.warning(err)

    person_id = await create_person(ctx, client_id)
    logger.debug('Person: {}'.format(person_id))

    if args.is_offer:
        contract = await create_offer(
            ctx, client_id, person_id, args.service_ids, args.payment,
        )
    else:
        contract = await create_common_contract(
            ctx, client_id, person_id, args.service_ids, args.payment,
        )
    logger.debug('Contract: {}'.format(contract))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', type=str, default='INFO')
    parser.add_argument(
        '--login', type=str, help='Yandex login for client', required=True,
    )
    parser.add_argument('--is_offer', action='store_true')
    parser.add_argument(
        '--payment',
        type=str,
        choices=['prepaid', 'postpaid'],
        default='postpaid',
    )
    parser.add_argument('--service_ids', type=int, nargs='+', required=True)
    return parser.parse_args()


async def main(loop):
    args = parse_args()
    logging.basicConfig(level=args.log)
    log_extra = auto_log_extra.get_log_extra()
    logger.info('Start script: %r', args, extra=log_extra)
    if taxi_settings.ENVIRONMENT == taxi_settings.PRODUCTION:
        print('this script is only for testing env.')
        return

    async with Context(loop, log_extra) as context:
        await create_test_billing_client(context, args)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
