import argparse
import datetime as dt
import getpass
import itertools
import sys
import time
import traceback

from cargo_newflow import consts
from cargo_newflow import library
from cargo_newflow import utils
from cargo_newflow import reporter as reporter_lib
from cargo_newflow.clients import (
    cargo_claims,
    cargo_orders_driver,
    cargo_waybill,
    cargo_orders_internal,
    ordercore,
    taximeter_x_service,
    telegram,
)

import cargo_newflow.clients.base


class HttpError(Exception):
    pass


class HttpNotFoundError(HttpError):
    pass


class HttpConflictError(HttpError):
    pass


class NoPointsLeft(Exception):
    pass


HTTP_CODES = {404: HttpNotFoundError, 409: HttpConflictError}


NEWFLOW_CONFIG_PATH = utils.get_project_root() / consts.NEWFLOW_CONFIG


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--phone', help='Your (dev) phone.', required=True,
    )
    parser.add_argument(
        '--case',
        help='Case to test.',
        default='default',
        choices=('default', 'return', 'create-only'),
    )
    parser.add_argument(
        '--corp-client-id',
        help='Corp client id (default: %(default)s).',
        default=consts.DEFAULT_CORP_CLIENT_ID,
    )
    parser.add_argument(
        '--yandex-uid',
        help='Yandex uid (set actual yandex uid for corps from cargo-corp, default: %(default)s).',
        default=consts.DEFAULT_YANDEX_UID,
    )
    parser.add_argument(
        '--batch-client',
        action='store_const',
        dest='corp_client_id',
        const=consts.BATCH_ENABLED_CORP_CLIENT_ID,
        help='Use batch enabled cargo client',
    )
    parser.add_argument(
        '--eats-client',
        action='store_const',
        dest='corp_client_id',
        const=consts.EATS_CORP_CLIENT_ID,
        help='Use eats cargo client',
    )
    parser.add_argument(
        '--lavka-client',
        action='store_const',
        dest='corp_client_id',
        const=consts.LAVKA_CORP_CLIENT_ID,
        help='Use lavka cargo client',
    )
    parser.add_argument(
        '--postpayment-client',
        action='store_const',
        dest='corp_client_id',
        const=consts.POSTPAYMENT_CLIENT_ID,
        help='Use postpayment cargo client',
    )
    parser.add_argument(
        '--claims',
        help='Number of claims to create (default: %(default)s).',
        default=1,
        type=int,
    )
    parser.add_argument(
        '--taxi-class',
        help='Taxi class.',
        default=None,
        choices=('express', 'courier', 'cargo', 'eda', 'lavka'),
    )
    parser.add_argument(
        '-s',
        '--dont-skip-confirmation',
        action='store_true',
        help='Skip confirmation via sms on each point.',
    )
    parser.add_argument(
        '--post-payment',
        action='store_true',
        help='Create claim with payment on delivery.',
    )
    parser.add_argument(
        '--request',
        default=None,
        help='Path to request body for v2/claims/create.',
    )
    parser.add_argument('--comment', default='', help='Claim comment')

    parser.add_argument(
        '--randomize-pickup-coordinates',
        action='store_true',
        help='Randomize pickup coordinates in small area',
    )

    parser.add_argument(
        '--randomize-dropoff-coordinates',
        action='store_true',
        help='Randomize dropoff coordinates in small area',
    )

    group = parser.add_argument_group(
        'Comment based crutches',
        'See https://nda.ya.ru/t/U055RdTd4CaSZ6 for details',
    )
    group.add_argument(
        '--wait',
        default=0,
        type=int,
        help='Courier wait time (default: %(default)s)',
    )
    group.add_argument(
        '--speed',
        default=100,
        type=int,
        help='Courier speed, kmph (default: %(default)s)',
    )
    group.add_argument(
        '--reject',
        default=None,
        type=int,
        help='Reject after n seconds (default: %(default)s)',
    )
    group.add_argument(
        '--cargo-noexchange',
        action='store_true',
        help='Disable emulator cargo-exchange logic',
    )
    group.add_argument(
        '--contractor-id',
        default=None,
        help='LD specific cargo contractor option, in format: dbid_uuid',
    )
    group.add_argument(
        '--alerts', action='store_true', help='Autotests option.',
    )
    group.add_argument(
        '--config',
        default=NEWFLOW_CONFIG_PATH,
        help='Path to autotests config file.',
    )
    group.add_argument(
        '--due',
        default=None,
        type=int,
        help='Delay(in seconds) before courier will be found.',
    )
    group.add_argument(
        '--pickup_code', action='store_true', help='PVZ pickup code 123456.',
    )
    group.add_argument(
        '--force-crutches',
        action='store_true',
        help='Forces crutches proposition builder (united-dispatch)',
    )
    group.add_argument(
        '--live-batch-with',
        default=None,
        help='Forces live batch proposition with given segment id (united-dispatch)',
    )
    group.add_argument(
        '--batch-with',
        default=None,
        help='Forces dead batch with given segment id (united-dispatch).',
    )
    group.add_argument(
        '--wait-for-batch',
        action='store_true',
        help='Forces segment to wait for batch, no p2p assignment (united-dispatch).',
    )
    group.add_argument(
        '--not-emulator-performer',
        action='store_true',
        help='Hides emulator performers from candidates search.',
    )
    group.add_argument(
        '--reject-live-batch',
        action='store_true',
        help='Reject live batch',
    )

    return parser.parse_args()


def run_script(args, reporter):

    username = getpass.getuser()

    net_address = utils.guess_address()

    cargo_client = cargo_claims.CargoClaimsClient(
        corp_client_id=args.corp_client_id,
        yandex_uid=args.yandex_uid,
        user=username,
        net_address=net_address,
    )
    waybill_client = cargo_waybill.CargoWaybillClient(
        user=username, net_address=net_address,
    )
    journals = library.Journals(claims_client=cargo_client)
    order_core_client = ordercore.OrderCoreClient(net_address=net_address)
    taximeter_xservice_client = taximeter_x_service.TaximeterXServiceClient(
        net_address=net_address,
    )
    cargo_order_client = cargo_orders_internal.CargoOrdersInternalClient(
        net_address=net_address,
    )

    for _ in range(args.claims):
        comment = library.build_comment(
            cargo_noexchange=args.cargo_noexchange,
            speed=args.speed,
            wait=args.wait,
            reject=args.reject,
            contractor_id=args.contractor_id,
            comment=args.comment,
            force_crutches=args.force_crutches,
            live_batch_with=args.live_batch_with,
            batch_with=args.batch_with,
            wait_for_batch=args.wait_for_batch,
            reject_live_batch=args.reject_live_batch,
        )

        claim = cargo_client.create_claim(
            json=library.build_request(
                username=username,
                phone=args.phone,
                comment=comment,
                request=args.request,
                corp_client_id=args.corp_client_id,
                taxi_class=args.taxi_class,
                dont_skip_confirmation=args.dont_skip_confirmation,
                post_payment=args.post_payment,
                due=args.due,
                pickup_code=args.pickup_code,
                randomize_pickup_coordinates=args.randomize_pickup_coordinates,
                randomize_dropoff_coordinates=args.randomize_dropoff_coordinates,
                not_emulator_performer=args.not_emulator_performer,
            ),
        )
        reporter.to_report('Start periodical testing...')
        reporter.section('Creating claim', claim)
        reporter.everywhere(f'Claim {claim["id"]} created')
        reporter.section(f'Waiting for claim {claim["id"]} to be ready')
        claim_link = library.get_claim_link(claim['id'])
        reporter.everywhere(f'Claim page: {claim_link}')

        timer = dt.datetime.now() + dt.timedelta(seconds=20)
        while True:
            claim_status = cargo_client.get_claim_status(claim['id'])
            print('claim_status = ', end='')
            reporter.dump_json(claim_status)
            if claim_status['status'] not in ('new', 'estimating'):
                break
            if dt.datetime.now() > timer:
                msg = 'Claim not changed status to ready_for_aproval in 20s.'
                raise TimeoutError(msg)
            time.sleep(1)
        if claim_status['status'] == 'ready_for_approval':
            reporter.section(f'Accepting claim {claim["id"]}')
            status = cargo_client.accept_claim(claim['id'])
            reporter.dump_json(status)

            reporter.section(f'Fetching segment_id for claim {claim["id"]}')

            timer = dt.datetime.now() + dt.timedelta(seconds=30)
            while True:
                segment_id = journals.get_segment_id(claim['id'])
                if segment_id:
                    reporter.section(f'Segment id: {segment_id}')
                    break
                if dt.datetime.now() > timer:
                    msg = 'Segment not created in 30s.'
                    raise TimeoutError(msg)
                print('Not found in journal, sleep...')
                time.sleep(1)
        else:
            reporter.to_report(
                f'Claim should be in ready_for_aproval, but has status: '
                f'{claim_status["status"]}.',
            )
            raise RuntimeError(
                f'Do not know what to do with claim '
                f'status {claim_status["status"]}',
            )

    reporter.section(f'Waiting for waybill to appear for segment {segment_id}')

    timer = dt.datetime.now() + dt.timedelta(seconds=300)
    while True:
        try:
            segment = waybill_client.segment_info(segment_id)
        except cargo_newflow.clients.base.HttpNotFoundError:
            print(f'segment {segment_id} not found...')
            time.sleep(1)
            continue

        if 'chosen_waybill' in segment['dispatch']:
            break
        status = segment['dispatch']['status']
        revision = segment['dispatch']['revision']

        print(
            f'waiting for waybill, segment status: {status}, '
            f'revision: {revision}',
        )
        if dt.datetime.now() > timer:
            msg = 'Waybill was not created in 300s.'
            raise TimeoutError(msg)
        time.sleep(1)

    print('dispatch_segment = ', end='')
    reporter.dump_json(segment)
    waybill_id = segment['dispatch']['chosen_waybill']['external_ref']
    reporter.section(
        f'Got waybill {waybill_id} for segment {segment_id}', segment,
    )

    reporter.section(f'Waiting for taxi order for waybill {waybill_id}')

    timer = dt.datetime.now() + dt.timedelta(seconds=20)
    while True:
        waybill = waybill_client.waybill_info(waybill_id)
        if 'taxi_order_info' in waybill['execution']:
            break
        status = waybill['dispatch']['status']
        resolution = waybill['dispatch'].get('resolution')
        revision = waybill['dispatch']['revision']
        print(
            f'waiting for taxi order, waybill status: {status}, '
            f'resolution: {resolution}, revision: {revision}',
        )

        if status in ('resolved',):
            break

        if dt.datetime.now() > timer:
            msg = 'Taxi order not created in 20s.'
            raise TimeoutError(msg)

        time.sleep(1)

    print('waybill = ', end='')
    reporter.dump_json(waybill)

    if status == 'resolved':
        reporter.section(
            f'Waybill is already resolved, giving up: '
            f'status: {status}, resolution: {resolution}',
        )
        reporter.send_report()
        return

    taxi_order_id = waybill['execution']['taxi_order_info']['order_id']
    cargo_order_id = waybill['diagnostics']['order_id']
    reporter.section(f'Cargo_order_id {cargo_order_id}')
    reporter.section(f'Got taxi order {taxi_order_id}')
    print('Order page:', library.get_order_link(taxi_order_id))
    print('Order logs:', library.get_order_logs_link(taxi_order_id))

    reporter.section(f'Waiting for performer_found for segment {segment_id}')

    timer = dt.datetime.now() + dt.timedelta(seconds=300)
    while True:
        segment = cargo_client.get_segment_info(segment_id)
        if segment['status'] not in ['performer_draft', 'performer_lookup']:
            if segment['status'] == 'performer_found':
                print(f'===> Performer found!')
                reporter.everywhere(f'Performer found!')
            else:
                print(f'===> Performer not found.')
                reporter.everywhere(f'Performer not found.')
                reporter.send_report()
                return
            break
        print('Performer not found yet, sleep...')
        if dt.datetime.now() > timer:
            msg = 'Performer not found in 300s.'
        time.sleep(5)

    dispatch_segment = waybill_client.segment_info(segment_id)
    waybill_ref = dispatch_segment['dispatch']['chosen_waybill'][
        'external_ref'
    ]
    reporter.section(f'Waybill_ref {waybill_ref}')
    waybill = waybill_client.waybill_info(waybill_ref)
    cargo_order_id = waybill['diagnostics']['order_id']
    reporter.section(f'Cargo_order_id {cargo_order_id}')

    performer = cargo_order_client.get_performer_info(cargo_order_id)
    reporter.section(f'Got performer', performer)

    orders_client = cargo_orders_driver.CargoOrdersDriverClient(
        corp_client_id=args.corp_client_id,
        user=username,
        performer=performer,
        dispatch_client=waybill_client,
        waybill_ref=waybill_id,
        cargo_order_id=cargo_order_id,
        net_address=net_address,
    )

    def iteration(do_return=False):
        time.sleep(1)
        reporter.section(f'Arrive at point for order {cargo_order_id}')
        while True:
            try:
                status = orders_client.arrive_at_point()
            # arrive_at_point returns 409, when driver is far away from point
            except cargo_newflow.clients.base.HttpConflictError:
                print('Not yet arrived at point')
                time.sleep(5)
                continue
            else:
                break

        reporter.dump_json(status)

        time.sleep(1)
        reporter.section(f'Exchange init for order {cargo_order_id}')
        status = orders_client.exchange_init()
        reporter.dump_json(status)

        time.sleep(1)
        if do_return:
            reporter.section(f'Return at point order {cargo_order_id}')
            status = orders_client.return_point()
        else:
            reporter.section(f'Exchange confirm for order {cargo_order_id}')

            timer = dt.datetime.now() + dt.timedelta(seconds=300)
            while True:
                try:
                    status = orders_client.exchange_confirm()
                except cargo_newflow.clients.base.HttpNotFoundError:
                    print('Phoenix payment is not yet complete, sleep...')
                    if dt.datetime.now() > timer:
                        print('Payment is not complete in 300s.')
                        break
                    time.sleep(5)
                    continue
                break

        reporter.dump_json(status)

        if status['new_status'] == 'complete':
            reporter.everywhere(
                f'Order {cargo_order_id} complete' f'(segment = {segment_id})',
            )
            return True
        return False

    if args.case == 'default':
        case = itertools.cycle([{}])
    elif args.case == 'return':
        case = itertools.chain(
            [{}, {'do_return': True}], itertools.cycle([{}]),
        )
    elif args.case == 'create-only':
        return
    else:
        raise RuntimeError(f'Unknown case {case}')

    for kwargs in case:
        try:
            if iteration(**kwargs):
                break
        except NoPointsLeft:
            break
        time.sleep(2)  # deal with esignature 429

    reporter.section(
        'Going to complete order in 10 seconds, '
        'press C-c to stop or C-z to suspend...',
    )
    status = cargo_client.get_claim_status(claim['id'])['status']
    reporter.everywhere(
        f'Claim {claim["id"]} completed. Claim status: {status}',
    )
    taxi_order_info = waybill['execution']['taxi_order_info']
    taxi_order_id = taxi_order_info['order_id']

    for _ in range(10):
        order_proc = order_core_client.get_order_fields(
            taxi_order_id, ['order.status', 'order.taxi_status'],
        )['fields']
        reporter.section(f'Taxi order status {taxi_order_id}', order_proc)
        time.sleep(1)

    order_proc = order_core_client.get_order_fields(
        taxi_order_id, ['performer.alias_id'],
    )['fields']
    reporter.section('Got response from order-core', order_proc)

    # response = taximeter_xservice_client.change_status(
    #     alias_id=order_proc['performer']['alias_id'],
    #     park_id=performer['park_id'],
    #     driver_id=performer['driver_id'],
    #     reason='newflow client finished',
    #     status='complete',
    # )
    # reporter.section('Got response from taximeter-xservice', response)

    reporter.send_report()


def main():
    args = parse_args()

    if args.alerts:
        conf = utils.load_config(args.config)

        telegram_client = telegram.TelegramClient(
            bot_token=conf.get('default', 'bot-token'),
            chat_id=conf.get('default', 'chat-id'),
        )
        telegram_reporter = reporter_lib.TelegramReporter(
            client=telegram_client,
            enable_alerts=args.alerts,
            report_file_path=conf.get('default', 'report-file'),
        )
    else:
        telegram_reporter = None

    console_reporter = reporter_lib.ConsoleReporter()

    reporter = reporter_lib.ProxyReporter(console_reporter, telegram_reporter)
    try:
        run_script(args, reporter)
    except (
        TimeoutError,
        RuntimeError,
        cargo_newflow.clients.base.HttpError,
    ) as exc:
        reporter.everywhere(str(exc))
        reporter.call_on_duty()
        reporter.send_report()
        sys.exit(1)

    except Exception:
        reporter.everywhere('Unexpected error occurred.')
        reporter.everywhere(traceback.format_exc())
        reporter.call_on_duty()
        reporter.send_report()
        sys.exit(1)


if __name__ == '__main__':
    main()
