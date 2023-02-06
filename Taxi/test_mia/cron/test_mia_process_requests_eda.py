# pylint: disable=redefined-outer-name

import pytest

from mia.crontasks import personal_wrapper
from mia.generated.cron import run_cron
from test_mia.cron import personal_dummy
from test_mia.cron import yt_dummy


@pytest.fixture()
def personal_mock(patch):
    @patch('mia.crontasks.dependencies._create_personal_api')
    def _create_personal_api(_):
        return personal_wrapper.PersonalWrapper(personal_dummy.PersonalDummy())


@pytest.mark.parametrize(
    'query_name,expected_matches',
    [
        (
            'mia_eda_request_query_1',
            [
                {
                    'order_id': 102,
                    'order_nr': 'test_order_nr',
                    'user_phone': 'test_phone_number',
                    'order_type': 'native',
                    'cost_for_customer': 123,
                    'cost_for_place': 12,
                    'finished_at': '04.02.2020 18:54:13+0300',
                    'address_office': 'test_address_office',
                    'address_entrance': 'test_address_entrance',
                    'address_comment': 'test_comment',
                    'address_city': 'test_city',
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
                    'order_items': ['item_2 x2', 'item_3 x3'],
                    'order_status': 'Доставлен',
                    'payment_method': 'Безналичный расчёт',
                    'place_address': 'test_address_full_2',
                    'place_name': 'test_name_2',
                    'user_email': 'test_email_4',
                    'user_first_name': 'test_first_name_4',
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                    'courier_phone': 'courier_phone_number_1',
                },
            ],
        ),
        (
            'mia_eda_request_query_2',
            [
                {
                    'order_id': 102,
                    'order_nr': 'test_order_nr',
                    'user_phone': 'test_phone_number',
                    'order_type': 'native',
                    'cost_for_customer': 123,
                    'cost_for_place': 12,
                    'finished_at': '04.02.2020 18:54:13+0300',
                    'address_office': 'test_address_office',
                    'address_entrance': 'test_address_entrance',
                    'address_comment': 'test_comment',
                    'address_city': 'test_city',
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
                    'order_items': ['item_2 x2', 'item_3 x3'],
                    'order_status': 'Доставлен',
                    'payment_method': 'Безналичный расчёт',
                    'place_address': 'test_address_full_2',
                    'place_name': 'test_name_2',
                    'user_email': 'test_email_4',
                    'user_first_name': 'test_first_name_4',
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                    'courier_phone': 'courier_phone_number_1',
                },
            ],
        ),
        (
            'mia_eda_request_query_3',
            [
                {
                    'order_id': 103,
                    'order_nr': 'test_order_nr',
                    'user_phone': 'test_phone_number',
                    'order_type': 'native',
                    'cost_for_customer': 123,
                    'cost_for_place': 12,
                    'finished_at': '04.02.2020 18:54:13+0300',
                    'address_office': 'test_address_office',
                    'address_entrance': 'test_address_entrance',
                    'address_comment': 'test_comment',
                    'address_city': 'test_city',
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
                    'order_refunds': [],
                    'order_items': ['item_2 x2', 'item_3 x3'],
                    'order_status': 'Доставлен',
                    'payment_method': 'Безналичный расчёт',
                    'place_address': 'test_address_full_2',
                    'place_name': 'test_name_2',
                    'user_email': 'test_email_4',
                    'user_first_name': 'test_first_name_4',
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                    'courier_phone': 'courier_phone_number_1',
                },
                {
                    'order_id': 104,
                    'order_nr': 'test_order_nr',
                    'user_phone': 'test_phone_number',
                    'order_type': 'native',
                    'cost_for_customer': 123,
                    'cost_for_place': 12,
                    'finished_at': '04.02.2020 18:54:13+0300',
                    'address_office': 'test_address_office',
                    'address_entrance': 'test_address_entrance',
                    'address_comment': 'test_comment',
                    'address_city': 'test_city',
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
                    'order_refunds': [],
                    'order_items': ['item_2 x2', 'item_3 x3'],
                    'order_status': 'Доставлен',
                    'payment_method': 'Безналичный расчёт',
                    'place_address': 'test_address_full_2',
                    'place_name': 'test_name_2',
                    'user_email': 'test_email_4',
                    'user_first_name': 'test_first_name_4',
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                    'courier_phone': 'courier_phone_number_1',
                },
                {
                    'order_id': 105,
                    'order_nr': 'test_order_nr',
                    'user_phone': 'test_phone_number',
                    'order_type': 'native',
                    'cost_for_customer': 123,
                    'cost_for_place': 12,
                    'finished_at': '04.02.2020 18:54:13+0300',
                    'address_office': 'test_address_office',
                    'address_entrance': 'test_address_entrance',
                    'address_comment': 'test_comment',
                    'address_city': 'test_city',
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
                    'order_refunds': [],
                    'order_items': ['item_2 x2', 'item_3 x3'],
                    'order_status': 'Доставлен',
                    'payment_method': 'Безналичный расчёт',
                    'place_address': 'test_address_full_2',
                    'place_name': 'test_name_2',
                    'user_email': 'test_email_4',
                    'user_first_name': 'test_first_name_4',
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                    'courier_phone': 'courier_phone_number_1',
                },
            ],
        ),
    ],
)
@pytest.mark.now('2020-02-04T12:20:00.0')
async def test_mia_process_requests_eda(
        patch,
        load_json,
        taxi_mia_web,
        personal_mock,
        query_name,
        expected_matches,
):
    yt_tables = load_json('yt_tables.json')
    request = load_json(query_name + '.json')

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(yt_tables)

    response = await taxi_mia_web.post('/v1/eda/query', request)
    content = await response.json()

    await run_cron.main(['mia.crontasks.mia_process_requests', '-t', '0'])

    response = await taxi_mia_web.get('/v1/eda/query/' + content['id'], {})
    content = await response.json()

    assert response.status == 200
    assert content['state']['status'] == 'succeeded'
    assert sorted(
        content['result']['matched'], key=lambda x: x['order_id'],
    ) == sorted(expected_matches, key=lambda x: x['order_id'])


@pytest.mark.pgsql('mia', files=['pg_mia_process_requests_eda.sql'])
@pytest.mark.parametrize(
    'test',
    [
        {
            'expected': [
                {
                    'order_id': 102,
                    'order_nr': 'test_order_nr',
                    'user_phone': 'test_phone_number',
                    'order_type': 'native',
                    'finished_at': '04.02.2020 18:54:13+0300',
                    'cost_for_customer': 123,
                    'cost_for_place': 12,
                    'address_entrance': 'test_address_entrance',
                    'address_office': 'test_address_office',
                    'address_comment': 'test_comment',
                    'address_city': 'test_city',
                    'address_house': 'test_house',
                    'address_street': 'test_street',
                    'deliverer_address': '-',
                    'deliverer_name': '-',
                    'deliverer_inn': '-',
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
                    'order_items': ['item_2 x2', 'item_3 x3'],
                    'order_status': 'Доставлен',
                    'payment_method': 'Безналичный расчёт',
                    'place_address': 'test_address_full_2',
                    'place_name': 'test_name_2',
                    'user_email': 'test_email_4',
                    'user_first_name': 'test_first_name_4',
                    'masked_pan': '-',
                    'rrn': '-',
                    'approval_code': '-',
                    'payment_time': '-',
                    'courier_phone': 'courier_phone_number_1',
                },
            ],
        },
    ],
)
@pytest.mark.now('2020-02-04T12:20:00.0')
async def test_mia_process_requests_fetch_in_progress_eda(
        patch, load_json, taxi_mia_web, personal_mock, test,
):
    expected = test['expected']
    yt_tables = load_json('yt_tables.json')

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(
            yt_tables,
            {
                'some_operation_id': yt_dummy.OperationDummy(
                    'some_operation_id',
                    {'spec': {'output_table_paths': ['mia_fetch_map_table']}},
                ),
            },
        )

    await run_cron.main(['mia.crontasks.mia_process_requests', '-t', '0'])

    response = await taxi_mia_web.get('/v1/eda/query/123', {})
    content = await response.json()

    assert response.status == 200
    assert content['state']['status'] == 'succeeded'
    assert content['result']['matched'] == expected


@pytest.mark.config(MIA_QUERIES_BATCH_SIZE=1)
@pytest.mark.parametrize(
    'test', [{'request': {'query_name': 'mia_eda_request_query_1'}}],
)
@pytest.mark.now('2020-02-04T12:20:00.0')
async def test_mia_priority_order_eda(
        patch, load_json, taxi_mia_web, personal_mock, test,
):
    request = test['request']

    query_name = request['query_name']

    yt_tables = load_json('yt_tables.json')
    request_body = load_json(query_name + '.json')

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(yt_tables)

    order_num_to_priority = {0: '4', 1: '1', 2: '3', 3: '2'}
    order_num_to_id = {}
    order_num_to_status = {}

    for order_num, priority in order_num_to_priority.items():
        response = await taxi_mia_web.post(
            f'/v1/eda/query/?priority={priority}', request_body,
        )
        content = await response.json()
        order_num_to_id[order_num] = content['id']

    async def run_cron_and_update_statuses():
        await run_cron.main(['mia.crontasks.mia_process_requests', '-t', '0'])
        for order_num, query_id in order_num_to_id.items():
            response = await taxi_mia_web.get('/v1/eda/query/' + query_id, {})
            content = await response.json()
            order_num_to_status[order_num] = content['state']['status']

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'pending'
    assert order_num_to_status[2] == 'pending'
    assert order_num_to_status[3] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'pending'
    assert order_num_to_status[2] == 'succeeded'
    assert order_num_to_status[3] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'pending'
    assert order_num_to_status[2] == 'succeeded'
    assert order_num_to_status[3] == 'succeeded'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'succeeded'
    assert order_num_to_status[3] == 'succeeded'


@pytest.mark.config(MIA_QUERIES_BATCH_SIZE=1)
@pytest.mark.parametrize(
    'test', [{'request': {'query_name': 'mia_eda_request_query_1'}}],
)
@pytest.mark.now('2020-02-04T12:20:00.0')
async def test_mia_priority_equal_order_eda(
        patch, load_json, taxi_mia_web, personal_mock, test,
):
    request = test['request']

    query_name = request['query_name']

    yt_tables = load_json('yt_tables.json')
    request_body = load_json(query_name + '.json')

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(yt_tables)

    order_num_to_priority = {0: '3', 1: '4', 2: '3', 3: '3'}
    order_num_to_id = {}
    order_num_to_status = {}

    for order_num, priority in order_num_to_priority.items():
        response = await taxi_mia_web.post(
            f'/v1/eda/query/?priority={priority}', request_body,
        )
        content = await response.json()
        order_num_to_id[order_num] = content['id']

    async def run_cron_and_update_statuses():
        await run_cron.main(['mia.crontasks.mia_process_requests', '-t', '0'])
        for order_num, query_id in order_num_to_id.items():
            response = await taxi_mia_web.get('/v1/eda/query/' + query_id, {})
            content = await response.json()
            order_num_to_status[order_num] = content['state']['status']

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'pending'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'pending'
    assert order_num_to_status[3] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'pending'
    assert order_num_to_status[3] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'succeeded'
    assert order_num_to_status[3] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'succeeded'
    assert order_num_to_status[3] == 'succeeded'


@pytest.mark.config(MIA_QUERIES_BATCH_SIZE=1)
@pytest.mark.parametrize(
    'test', [{'request': {'query_name': 'mia_eda_request_query_1'}}],
)
@pytest.mark.now('2020-02-04T12:20:00.0')
async def test_mia_process_in_order_eda(
        patch, load_json, taxi_mia_web, personal_mock, test,
):
    request = test['request']

    query_name = request['query_name']

    yt_tables = load_json('yt_tables.json')
    request_body = load_json(query_name + '.json')

    @patch('mia.crontasks.dependencies._create_yt_client')
    def _create_yt_client(_):
        return yt_dummy.YtWrapperDummy(yt_tables)

    order_num_to_id = {}
    order_num_to_status = {}

    for i in range(4):
        response = await taxi_mia_web.post(f'/v1/eda/query/', request_body)
        content = await response.json()
        order_num_to_id[i] = content['id']

    async def run_cron_and_update_statuses():
        await run_cron.main(['mia.crontasks.mia_process_requests', '-t', '0'])
        for order_num, query_id in order_num_to_id.items():
            response = await taxi_mia_web.get('/v1/eda/query/' + query_id, {})
            content = await response.json()
            order_num_to_status[order_num] = content['state']['status']

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'pending'
    assert order_num_to_status[2] == 'pending'
    assert order_num_to_status[3] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'pending'
    assert order_num_to_status[3] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'succeeded'
    assert order_num_to_status[3] == 'pending'

    await run_cron_and_update_statuses()
    assert order_num_to_status[0] == 'succeeded'
    assert order_num_to_status[1] == 'succeeded'
    assert order_num_to_status[2] == 'succeeded'
    assert order_num_to_status[3] == 'succeeded'
