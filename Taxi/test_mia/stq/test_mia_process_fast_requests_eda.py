# pylint: disable=redefined-outer-name
import pytest

from mia.crontasks import personal_wrapper
from mia.crontasks import pg_wrapper
from mia.stq import mia_process_fast_request
from test_mia.cron import personal_dummy
from test_mia.cron import scrooge_wrapper_dummy
from test_mia.cron import timezone_dummy
from test_mia.cron import user_phone_dummy
from test_mia.cron import yt_dummy


@pytest.mark.config(
    TVM_RULES=[{'src': 'mia', 'dst': 'stq-agent'}],
    MIA_SCROOGE_EDA_SERVICE_IDS=[84783],
    MIA_FAST_QUERIES_ENABLED=True,
    MIA_FILTER_BY_COUNTRIES_ENABLED=False,
)
@pytest.mark.now('2020-04-04T12:20:00.0')
@pytest.mark.parametrize(
    'case',
    [
        {
            'test_input': {
                'request': {
                    'completed_only': False,
                    'exact': {
                        'masked_pan': '123456****1234',
                        'rrn': 'test_rrn_2',
                        'approval_code': 'test_approval_code_2',
                        'order_cost': 234,
                    },
                    'period': {
                        'payment': {
                            'from': '2019-04-05T11:00:00.0',
                            'to': '2019-04-08T12:00:00.0',
                        },
                    },
                },
            },
            'expected_result': [
                {
                    'order_id': 102,
                    'order_nr': 'test-order-nr',
                    'user_phone': 'test_phone_number',
                    'order_type': 'native',
                    'cost_for_customer': 123,
                    'cost_for_place': 12,
                    'address_office': 'test_address_office',
                    'address_entrance': 'test_address_entrance',
                    'address_comment': 'test_comment',
                    'address_city': 'test_city',
                    'finished_at': '04.02.2020 00:27:33+0300',
                    'address_house': 'test_house',
                    'address_street': 'test_street',
                    'deliverer_address': '-',
                    'deliverer_inn': '-',
                    'deliverer_name': '-',
                    'deliverer_phone_number': '-',
                    'deliverer_type': 'Курьерская служба',
                    'is_virtual': False,
                    'place_phone_numbers': ['test_phone_number_1'],
                    'courier_name': 'test_courier_username',
                    'created_at': '03.02.2020 18:54:13+0300',
                    'delivery_cost': 1,
                    'items_cost': 43,
                    'order_refunds': [
                        {'amount': 123, 'id': 20, 'order_id': 102},
                        {'amount': 124, 'id': 22, 'order_id': 102},
                    ],
                    'order_items': [],
                    'order_status': 'Доставлен',
                    'payment_method': 'Безналичный расчёт',
                    'place_address': 'test_address_full_2',
                    'place_name': 'test_name_2',
                    'user_email': 'test_email_4',
                    'user_first_name': 'test_first_name_4',
                    'payment_time': '07.04.2019 21:07:00+0300',
                    'masked_pan': '123456****1234',
                    'rrn': 'test_rrn_2',
                    'approval_code': 'test_approval_code_2',
                    'courier_phone': None,
                },
            ],
        },
    ],
)
async def test_mia_process_fast_requests_eda_cards(
        patch, load_json, taxi_mia_web, stq, stq3_context, case,
):
    yt_tables = load_json('yt_tables.json')
    scrooge_tables = load_json('scrooge_tables.json')

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(yt_tables)

    @patch('mia.crontasks.dependencies._create_phone_api')
    def _create_phone_wrapper(_):
        return user_phone_dummy.UserPhoneWrapperDummy(
            {'+79990001234': ['id_of_79990001234']},
        )

    @patch('mia.crontasks.dependencies._create_timezone_wrapper')
    def _create_timezone_wrapper(_1, _2):
        return timezone_dummy.TimezoneWrapperDummy(
            {'test_zone': 'Europe/Moscow'},
        )

    @patch('mia.crontasks.dependencies._create_scrooge_wrapper')
    def _create_scrooge_wrapper(_):
        return scrooge_wrapper_dummy.ScroogeWrapperDummy(scrooge_tables)

    @patch('mia.crontasks.dependencies._create_personal_api')
    def _create_personal_api(_):
        return personal_wrapper.PersonalWrapper(personal_dummy.PersonalDummy())

    request = case['test_input']['request']
    response = await taxi_mia_web.post('/v1/eda/query', request)
    content = await response.json()

    await mia_process_fast_request.task(
        stq3_context,
        mia_query_id=int(content['id']),
        service_name=pg_wrapper.ServiceName.EDA.name,
    )

    response = await taxi_mia_web.get('/v1/eda/query/' + content['id'], {})
    content = await response.json()

    assert response.status == 200
    assert content['state']['status'] == 'succeeded'
    assert content['result']['matched'] == case['expected_result']


@pytest.mark.config(
    TVM_RULES=[{'src': 'mia', 'dst': 'stq-agent'}],
    MIA_SCROOGE_EDA_SERVICE_IDS=[84783],
    MIA_FAST_QUERIES_ENABLED=True,
    MIA_FILTER_BY_COUNTRIES_ENABLED=False,
    MIA_FAST_QUERIES_INDEXES_LIMIT=0,
)
@pytest.mark.now('2020-04-04T12:20:00.0')
@pytest.mark.parametrize(
    'case',
    [
        {
            'test_input': {
                'request': {
                    'completed_only': False,
                    'exact': {
                        'masked_pan': '123456****1234',
                        'order_cost': 234,
                    },
                    'period': {
                        'payment': {
                            'from': '2019-04-05T11:00:00.0',
                            'to': '2019-04-08T12:00:00.0',
                        },
                    },
                },
            },
            'expected_result': [],
        },
    ],
)
async def test_mia_process_fast_requests_stq_only(
        patch, load_json, taxi_mia_web, stq, stq3_context, case,
):
    yt_tables = load_json('yt_tables.json')
    scrooge_tables = load_json('scrooge_tables.json')

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(yt_tables)

    @patch('mia.crontasks.dependencies._create_phone_api')
    def _create_phone_wrapper(_):
        return user_phone_dummy.UserPhoneWrapperDummy(
            {'+79990001234': ['id_of_79990001234']},
        )

    @patch('mia.crontasks.dependencies._create_timezone_wrapper')
    def _create_timezone_wrapper(_1, _2):
        return timezone_dummy.TimezoneWrapperDummy(
            {'test_zone': 'Europe/Moscow'},
        )

    @patch('mia.crontasks.dependencies._create_scrooge_wrapper')
    def _create_scrooge_wrapper(_):
        return scrooge_wrapper_dummy.ScroogeWrapperDummy(scrooge_tables)

    request = case['test_input']['request']
    response = await taxi_mia_web.post('/v1/eda/query', request)
    content = await response.json()

    await mia_process_fast_request.task(
        stq3_context,
        mia_query_id=int(content['id']),
        service_name=pg_wrapper.ServiceName.EDA.name,
    )

    response = await taxi_mia_web.get('/v1/eda/query/' + content['id'], {})
    content = await response.json()

    assert response.status == 200
    assert content['state']['status'] == 'failed'
    assert (
        content['result']['error']
        == 'Found too much indexes (Only stq processing allowed)'
    )


@pytest.mark.config(MIA_FAST_QUERIES_ENABLED=True)
@pytest.mark.parametrize(
    'case',
    [
        {
            'test_input': {
                'request': {
                    'completed_only': False,
                    'exact': {'courier_phone': '+79990001111'},
                },
            },
            'expected_result': [
                {
                    'address_city': 'test_city',
                    'address_comment': 'test_comment',
                    'address_entrance': 'test_address_entrance',
                    'address_house': 'test_house',
                    'address_office': 'test_address_office',
                    'address_street': 'test_street',
                    'approval_code': '-',
                    'cost_for_customer': 123,
                    'cost_for_place': 12,
                    'courier_name': None,
                    'courier_phone': None,
                    'created_at': '03.02.2020 18:54:13+0300',
                    'deliverer_address': '-',
                    'deliverer_inn': '-',
                    'deliverer_name': '-',
                    'deliverer_phone_number': '-',
                    'deliverer_type': 'Курьер такси',
                    'delivery_cost': 1,
                    'finished_at': '04.02.2020 00:27:33+0300',
                    'is_virtual': True,
                    'items_cost': 43,
                    'masked_pan': '-',
                    'order_id': 103,
                    'order_items': [],
                    'order_nr': 'test-order-nr-2',
                    'order_refunds': [
                        {'amount': 125, 'id': 21, 'order_id': 103},
                    ],
                    'order_status': 'Доставлен',
                    'order_type': 'native',
                    'payment_method': 'Безналичный расчёт',
                    'payment_time': '-',
                    'place_address': 'test_address_full_2',
                    'place_name': 'test_name_2',
                    'place_phone_numbers': ['test_phone_number_1'],
                    'rrn': '-',
                    'user_email': 'test_email_4',
                    'user_first_name': 'test_first_name_4',
                    'user_phone': 'test_phone_number',
                },
            ],
        },
    ],
)
@pytest.mark.now('2020-04-04T12:20:00.0')
async def test_find_by_courier_phone(
        case, patch, load_json, stq3_context, taxi_mia_web,
):
    yt_tables = load_json('yt_tables.json')
    scrooge_tables = load_json('scrooge_tables.json')

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(yt_tables)

    @patch('mia.crontasks.dependencies._create_timezone_wrapper')
    def _create_timezone_wrapper(_1, _2):
        return timezone_dummy.TimezoneWrapperDummy(
            {'test_zone': 'Europe/Moscow'},
        )

    @patch('mia.crontasks.dependencies._create_scrooge_wrapper')
    def _create_scrooge_wrapper(_):
        return scrooge_wrapper_dummy.ScroogeWrapperDummy(scrooge_tables)

    @patch('mia.crontasks.dependencies._create_personal_api')
    def _create_personal_api(_):
        return personal_wrapper.PersonalWrapper(personal_dummy.PersonalDummy())

    request = case['test_input']['request']
    response = await taxi_mia_web.post('/v1/eda/query', request)
    content = await response.json()

    await mia_process_fast_request.task(
        stq3_context,
        mia_query_id=int(content['id']),
        service_name=pg_wrapper.ServiceName.EDA.name,
    )

    response = await taxi_mia_web.get('/v1/eda/query/' + content['id'], {})
    content = await response.json()

    assert response.status == 200
    assert content['state']['status'] == 'succeeded'
    assert content['result']['matched'] == case['expected_result']
