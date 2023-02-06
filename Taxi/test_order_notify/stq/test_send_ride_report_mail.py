import typing

from aiohttp import web
import bson
import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.order_info import OrderData
from order_notify.stq import send_ride_report_mail
from test_order_notify.conftest import TRANSLATIONS_COLOR
from test_order_notify.conftest import TRANSLATIONS_NOTIFY_EXTRA
from test_order_notify.conftest import TRANSLATIONS_TARIFF
from test_order_notify.conftest import TRANSLATIONS_UBER_RIDE_REPORT
from test_order_notify.util import get_bson_order_data

EXP3_CONSUMER = 'order-notify/stq/call_old_ride_report'
CALL_STQ_EXP3_NAME = 'call_send_report'
PERSONAL_EMAIL_ID = '343c'

EXP3_ARGS = [
    {
        'name': 'phone_id',
        'type': 'string',
        'value': '5db9a7d77984b5db6237105d',
    },
    {'name': 'country', 'type': 'string', 'value': 'rus'},
    {
        'name': 'order_id',
        'type': 'string',
        'value': '71a910a1bb274456bfe4946bd2bb8351',
    },
    {
        'name': 'personal_email_id',
        'type': 'string',
        'value': PERSONAL_EMAIL_ID,
    },
    {'name': 'locale', 'type': 'string', 'value': 'ru'},
]

UBER_ORDER_ID = 'c7970f55c96cd62fae010a752f1a270b'

TO_EMAIL = 'fedor-miron@yandex-team.ru'


@pytest.fixture(name='mock_functions')
def mock_functions_fixture(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.send_user_report_mail = Counter()
            self.send_corp_report_mail = Counter()
            self.get_order_info = Counter()
            self.is_completed = Counter()
            self.update_ride_report_sent_value = Counter()

    counters = Counters()

    @patch(
        'order_notify.repositories.ride_report_sent.'
        'update_ride_report_sent_value',
    )
    async def _update_ride_report_sent_value(
            context: stq_context.Context, order_id: str, value: bool,
    ):
        assert value is False
        counters.update_ride_report_sent_value.call()

    @patch('order_notify.repositories.order_info.get_order_info')
    async def _get_order_info(
            context: stq_context.Context, order_id: str,
    ) -> typing.Optional[OrderData]:
        counters.get_order_info.call()

        order: typing.Optional[typing.Dict[str, typing.Any]] = None
        order_proc: typing.Optional[typing.Dict[str, typing.Any]] = None

        if order_id in ('2', 'c091882b77c'):
            order = {}
            order_proc = {}
        if order_id == '71a910a1bb274456bfe4946bd2bb8351':
            order = {
                'nz': 'moscow',
                'status': 'finished',
                'taxi_status': 'complete',
            }
            order_proc = {
                'order': {
                    'request': {},
                    'user_phone_id': bson.ObjectId('5db9a7d77984b5db6237105d'),
                },
                'order_info': {'statistics': {'corp_ride_report_sent': True}},
            }
        if order_id == 'c091882b77c74cd7a8be754fa2360413':
            order = {'status': 'finished', 'taxi_status': 'complete'}
            order_proc = {'order': {'request': {'cargo_ref_id': 'bruh'}}}
        if order_id in (
                '71a910a1bb274456bfe4946bd2bb8334',
                '71a910a1bb274456bfe49ja3klk3md1a',
        ):
            order = {'status': 'finished', 'taxi_status': 'complete'}
            order_proc = {
                'order_info': {'statistics': {'corp_ride_report_sent': True}},
            }
        if order_id in (
                '71a910a1bb274456bfe4946bd2bb8338',
                '71a910a1bb274456bfe4946bd2bb8330',
        ):
            order = {'status': 'finished', 'taxi_status': 'complete'}
            order_proc = {
                'order_info': {'statistics': {'corp_ride_report_sent': False}},
            }

        if order is not None and order_proc is not None:
            order_proc['_id'] = order_id
            if order_proc.get('order') is None:
                order_proc['order'] = {}
            if order_proc['order'].get('request') is None:
                order_proc['order']['request'] = {}
            return OrderData(
                brand='', country='', order=order, order_proc=order_proc,
            )
        return None

    @patch(
        'order_notify.repositories.send_report_functions.'
        'send_user_report_mail',
    )
    async def _send_user_report_mail(
            context: stq_context.Context,
            order_data: OrderData,
            locale: typing.Optional[str] = None,
            personal_email_id: str = None,
    ):
        counters.send_user_report_mail.call()

    @patch(
        'order_notify.repositories.send_report_functions.'
        'send_corp_report_mail',
    )
    async def _send_corp_report_mail(
            context: stq_context.Context,
            order_data: OrderData,
            locale: typing.Optional[str] = None,
    ):
        counters.send_corp_report_mail.call()

    return counters


@pytest.mark.filldb()
@pytest.mark.client_experiments3(
    file_with_default_response='default_experiment.json',
)
@pytest.mark.parametrize(
    'force_send, order_id, expected_times_called',
    [
        pytest.param(True, '1', [1, 1, 0, 0, 0], id='no_order_data'),
        pytest.param(True, '2', [1, 1, 0, 0, 0], id='not_completed'),
        pytest.param(
            True,
            'c091882b77c74cd7a8be754fa2360413',
            [1, 1, 0, 0, 0],
            id='cargo_order',
        ),
        pytest.param(
            True,
            '71a910a1bb274456bfe4946bd2bb8351',
            [1, 1, 1, 1, 0],
            id='force_send',
        ),
        pytest.param(
            False,
            '71a910a1bb274456bfe4946bd2bb8334',
            [0, 1, 0, 1, 0],
            id='user_order_exist_ride_report_sent',
        ),
        pytest.param(
            False,
            '71a910a1bb274456bfe49ja3klk3md1a',
            [0, 1, 0, 1, 0],
            id='user_order_not_exist_ride_report_sent',
        ),
        pytest.param(
            False,
            '71a910a1bb274456bfe4946bd2bb8338',
            [0, 1, 1, 0, 0],
            id='corp_order',
        ),
        pytest.param(
            False,
            '71a910a1bb274456bfe4946bd2bb8330',
            [0, 1, 1, 1, 0],
            id='corp_and_user_order',
        ),
        pytest.param(
            False,
            '71a910a1bb274456bfe4946bd2bb8351',
            [0, 1, 0, 0, 0],
            id='no_one_order',
        ),
    ],
)
async def test_send_ride_report_mail(
        stq3_context: stq_context.Context,
        mock_get_cashed_zones,
        stq,
        mock_functions,
        force_send,
        order_id,
        expected_times_called,
):
    await send_ride_report_mail.task(
        context=stq3_context,
        personal_email_id='343c',
        force_send=force_send,
        order_id=order_id,
        locale='ru',
    )
    times_called = [
        mock_functions.update_ride_report_sent_value.times_called,
        mock_functions.get_order_info.times_called,
        mock_functions.send_corp_report_mail.times_called,
        mock_functions.send_user_report_mail.times_called,
        stq.send_ride_report_mail.times_called,
    ]
    assert times_called == expected_times_called


@pytest.mark.filldb()
@pytest.mark.parametrize(
    'personal_email_id, expected_times_called',
    [
        pytest.param(
            PERSONAL_EMAIL_ID,
            [0, 0, 1],
            marks=[
                pytest.mark.client_experiments3(
                    consumer=EXP3_CONSUMER,
                    experiment_name=CALL_STQ_EXP3_NAME,
                    args=EXP3_ARGS,
                    value={},
                ),
            ],
            id='no enabled',
        ),
        pytest.param(PERSONAL_EMAIL_ID, [0, 0, 1], id='no exp3'),
        pytest.param(
            PERSONAL_EMAIL_ID,
            [0, 0, 1],
            marks=[
                pytest.mark.client_experiments3(
                    consumer=EXP3_CONSUMER,
                    experiment_name=CALL_STQ_EXP3_NAME,
                    args=EXP3_ARGS,
                    value={'enabled': True},
                ),
            ],
            id='call_send_report',
        ),
        pytest.param(
            PERSONAL_EMAIL_ID,
            [1, 1, 0],
            marks=[
                pytest.mark.client_experiments3(
                    consumer=EXP3_CONSUMER,
                    experiment_name=CALL_STQ_EXP3_NAME,
                    args=EXP3_ARGS,
                    value={'enabled': False},
                ),
            ],
            id='not_call_send_report',
        ),
        pytest.param(
            None,
            [0, 0, 1],
            marks=[
                pytest.mark.client_experiments3(
                    consumer=EXP3_CONSUMER,
                    experiment_name=CALL_STQ_EXP3_NAME,
                    args=[
                        {
                            'name': 'phone_id',
                            'type': 'string',
                            'value': '5db9a7d77984b5db6237105d',
                        },
                        {'name': 'country', 'type': 'string', 'value': 'rus'},
                        {
                            'name': 'order_id',
                            'type': 'string',
                            'value': '71a910a1bb274456bfe4946bd2bb8351',
                        },
                    ],
                    value={'enabled': True},
                ),
            ],
            id='call_send_report_without_personal_email_id',
        ),
    ],
)
async def test_call_stq(
        stq3_context: stq_context.Context,
        mock_functions,
        mock_get_cashed_zones,
        stq,
        personal_email_id,
        expected_times_called,
):
    await send_ride_report_mail.task(
        context=stq3_context,
        personal_email_id=personal_email_id,
        force_send=True,
        order_id='71a910a1bb274456bfe4946bd2bb8351',
        locale='ru',
    )
    times_called = [
        mock_functions.send_corp_report_mail.times_called,
        mock_functions.send_user_report_mail.times_called,
        stq.send_report.times_called,
    ]
    assert times_called == expected_times_called


@pytest.fixture(name='send_ride_report_fixture')
def _send_ride_report_fixture(mockserver, load_json):
    orders_proc = load_json('order_proc.json')
    orders = load_json('order.json')

    @mockserver.json_handler('/order-archive/v1/order_proc/retrieve')
    async def _order_archive_handler(request):
        bson_order_proc = get_bson_order_data(db=orders_proc, request=request)
        if bson_order_proc:
            return mockserver.make_response(
                response=bson_order_proc,
                content_type='application/x-bson-binary',
            )
        return mockserver.make_response('Not Found', status=404)

    @mockserver.json_handler('/archive-api/archive/order')
    def _archive_api_handler(request):
        bson_order = get_bson_order_data(db=orders, request=request)
        if bson_order:
            return web.Response(
                body=bson_order, headers={'Content-Type': 'application/bson'},
            )
        return web.json_response({}, status=404)

    @mockserver.json_handler('/user-api/users/get')
    async def _users_handler(request):
        assert request.json['id']
        return {
            'id': request.json['id'],
            'phone_id': '614ac98273872fb3b5e4ebf2',
            'yandex_uid': '"4096095415',
        }

    @mockserver.json_handler('/user-api/user_emails/get')
    async def _user_emails_handler(request):
        assert request.json.get('yandex_uids', []) or request.json.get(
            'phone_ids', [],
        )
        return load_json('user_emails_response.json')

    @mockserver.json_handler('personal/v1/emails/retrieve')
    async def _personal_handler(request):
        assert request.json['id']
        return {'id': request.json['id'], 'value': TO_EMAIL}

    @mockserver.json_handler('taxi-tariffs/v1/tariff_settings/bulk_retrieve')
    def _tariff_settings_handler(request):
        json = load_json('tariff_settings_response.json')
        return {
            'zones': [
                zone
                for zone in json['zones']
                if zone['zone'] in request.query['zone_names']
            ],
        }

    @mockserver.json_handler('/driver-trackstory/legacy/gps-storage/get')
    def _mock_driver_trackstory(request):
        if (
                request.query['driver_id']
                == 'fa53651ff34b43f88ed7caf2626270e6'
                and request.query['db_id']
                == '7f74df331eb04ad78bc2ff25ff88a8f2'
        ):
            return {
                'track': [
                    {
                        'point': [37.606797, 55.760301],
                        'timestamp': 1653569318,
                        'bearing': 0.0,
                        'speed': 0.0,
                    },
                    {
                        'point': [37.584379, 55.687061],
                        'timestamp': 1653569510,
                        'bearing': 0.0,
                        'speed': 0.0,
                    },
                ],
            }
        return {'track': []}

    @mockserver.json_handler('/protocol/3.0/localizeaddress')
    def _mock_localizeaddress(request):
        if request.json['locale'] == 'ru':
            return load_json('localizeaddress_response.json')
        return {}

    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def _mock_parks_retrieve(_):
        return load_json('parks_replica_response.json')

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock_personal_phones(request):
        return {'value': '+79123456789', 'id': request.json['id']}


def add_exp3_records(
        client_experiments3, load_json, brand: str, country: str, locale: str,
):
    client_experiments3.add_record(
        consumer='order-notify/stq/send_ride_report_mail_locale_template',
        config_name='order-notify_send_ride_report_locale_template',
        args=[
            {'name': 'brand', 'type': 'string', 'value': brand},
            {'name': 'locale', 'type': 'string', 'value': locale},
        ],
        value=load_json(f'{brand}_{locale}_exp_args.json'),
    )
    client_experiments3.add_record(
        consumer='order-notify/stq/send_ride_report_mail',
        config_name='order-notify_send_ride_report_brand_template',
        args=[{'name': 'brand', 'type': 'string', 'value': brand}],
        value=load_json(f'{brand}_exp_args.json'),
    )
    client_experiments3.add_record(
        consumer='order-notify/stq/send_ride_report_mail_country_template',
        config_name='order-notify_send_ride_report_country_template',
        args=[
            {'name': 'brand', 'type': 'string', 'value': brand},
            {'name': 'country', 'type': 'string', 'value': country},
        ],
        value=load_json(f'{brand}_{country}_exp_args.json'),
    )
    client_experiments3.add_record(
        consumer='order-notify/stq/send_ride_report_mail',
        config_name='order-notify_send_ride_report_tanker_keys',
        args=[
            {'name': 'brand', 'type': 'string', 'value': brand},
            {'name': 'country', 'type': 'string', 'value': country},
        ],
        value=load_json(f'{brand}_{country}_tanker_keys.json'),
    )


@pytest.mark.client_experiments3(
    file_with_default_response='default_experiment.json',
)
@pytest.mark.filldb()
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'order-notify'}])
@pytest.mark.translations(
    notify=dict(**TRANSLATIONS_UBER_RIDE_REPORT, **TRANSLATIONS_NOTIFY_EXTRA),
    tariff=TRANSLATIONS_TARIFF,
    color=TRANSLATIONS_COLOR,
)
@pytest.mark.parametrize(
    'order_id,brand,locale,country,expected_from_email,expected_from_name',
    [
        pytest.param(
            UBER_ORDER_ID,  # order_id
            'yauber',  # brand
            'ru',  # locale
            'rus',  # country
            'no-reply@support-uber.com',  # expected_from_email
            'Uber',  # expected_from_name
            id='ru-rus-uber',
        ),
    ],
)
async def test_send_ride_report_key_values(
        order_id: str,
        brand: str,
        locale: str,
        country: str,
        expected_from_email: str,
        expected_from_name: str,
        stq3_context: stq_context.Context,
        send_ride_report_fixture,
        mock_tariff_zones,
        client_experiments3,
        load_json,
        patch,
):
    add_exp3_records(client_experiments3, load_json, brand, country, locale)

    @patch('taxi.clients.sender.SenderClient.send_transactional_email')
    async def _handle_sender(
            campaign_slug: str,
            from_name: str,
            from_email: str,
            to_email: str,
            template_vars: dict,
            is_async: bool,
    ):
        assert from_name == expected_from_name
        assert from_email == expected_from_email
        assert to_email == TO_EMAIL

        expected_template_vars = load_json(
            f'{brand}_{locale}_{country}_expected_kwargs.json',
        )

        # ignore extra keys in template_vars as they are ignored by sender
        assert {
            k: v
            for k, v in template_vars.items()
            if k in expected_template_vars.keys()
        } == expected_template_vars

        return {'status': 'OK'}

    await send_ride_report_mail.task(
        context=stq3_context, force_send=True, order_id=order_id,
    )
