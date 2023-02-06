import logging

import pytest

from mia.crontasks import personal_wrapper
from mia.crontasks import pg_wrapper
from mia.stq import mia_process_fast_request
from test_mia.cron import personal_dummy


@pytest.mark.config(MIA_FAST_QUERIES_ENABLED=True)
@pytest.mark.yt(
    dyn_table_data=[
        'yt_lavka_driver_id_index.yaml',
        'yt_lavka_orders_monthly.yaml',
        'yt_lavka_order_log_monthly.yaml',
    ],
)
@pytest.mark.now('2022-06-17T00:00:00.0')
async def test_mia_process_fast_requests_search_by_courier_phone(
        taxi_mia_web, stq3_context, mock_driver_profiles, yt_apply, patch,
):
    @mock_driver_profiles('/v1/driver/profiles/retrieve_by_phone')
    async def _driver_profiles(request):
        assert request.json == {
            'driver_phone_in_set': ['+79008001111_id'],
            'projection': ['park_driver_profile_id'],
        }
        return {
            'profiles_by_phone': [
                {
                    'driver_phone': '+79008001111_id',
                    'profiles': [
                        {'park_driver_profile_id': 'parkid1_driver_id'},
                        {'park_driver_profile_id': 'parkid2_driver_id'},
                    ],
                },
            ],
        }

    @patch('mia.crontasks.dependencies._create_personal_api')
    def _create_personal_api(_):
        return personal_wrapper.PersonalWrapper(personal_dummy.PersonalDummy())

    request = {
        'exact': {'courier_phone': '+79008001111'},
        'completed_only': False,
    }
    response = await taxi_mia_web.post('/v1/lavka/query', request)
    content = await response.json()
    logging.info(f'content: {content}')
    await mia_process_fast_request.task(
        stq3_context,
        mia_query_id=int(content['id']),
        service_name=pg_wrapper.ServiceName.LAVKA.name,
    )
    response = await taxi_mia_web.get('/v1/lavka/query/' + content['id'], {})
    logging.info(f'response: {response}')
    assert response.status == 200
    content = await response.json()
    logging.info(f' response json: {content}')
    assert content['state']['status'] == 'succeeded'

    expected_result = [
        {
            'address_city': 'Москва',
            'address_comment': 'test',
            'address_entrance': '-',
            'address_floor': 'None,',
            'address_house': '3',
            'address_office': 'None,',
            'address_street': 'улица Доватора',
            'cost_for_customer': 378.0,
            'courier_name': 'Иван',
            'courier_phone': None,
            'created_at': '15.06.2022 20:18:53+0300',
            'deliverer_address': '-',
            'deliverer_inn': '-',
            'deliverer_name': '-',
            'deliverer_phone_number': '-',
            'delivery_cost': 90.0,
            'finished_at': '15.06.2022 20:25:33+0300',
            'order_id': '01c19ea37eda4894b1cd94749fc007fb-grocery',
            'order_items': [
                'Лимон x3',
                'Авокадо x3',
                'Банан x2',
                'Пюре «Агуша» банан с 6 месяцев x1',
            ],
            'order_nr': '211028-735-3568',
            'order_refunds': None,
            'order_status': 'Отменён',
            'payment_method': 'Безналичный расчёт',
            'place_address': '125195, Москва г, Смольная ул, дом № 47',
            'place_name': 'Яндекс.Лавка',
            'user_email': 'test',
            'user_first_name': '-',
            'user_phone': 'test',
        },
    ]
    assert content['result']['matched'] == expected_result
