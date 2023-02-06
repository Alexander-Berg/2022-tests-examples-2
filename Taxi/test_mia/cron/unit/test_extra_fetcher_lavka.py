# pylint: disable=protected-access

import pytest

from mia.crontasks import personal_wrapper
from mia.crontasks.extra_fetcher import extra_fetcher_lavka
from mia.crontasks.request_parser import request_parser_lavka
from test_mia.cron import personal_dummy
from test_mia.cron import yt_dummy


@pytest.mark.parametrize(
    'rows, expected',
    [
        (
            [
                {
                    'order_id': '01c19ea37eda4894b1cd94749fc007fb-grocery',
                    'created_at': 1635497371.1,
                    'created_idx': 1635497371,
                    'finished_at': 1635497371.1,
                    'order_nr': '211028-735-3568',
                    'client_price': '378',
                    'currency': 'RUB',
                    'address_country': 'Россия',
                    'address_city': 'Москва',
                    'address_street': 'улица Доватора',
                    'address_house': '3',
                    'address_flat': None,
                    'address_floor': None,
                    'dispatch_courier_name': 'Иван',
                    'address_comment': 'test',
                    'status': 'canceled',
                    'eats_user_id': 1,
                    'personal_phone_id': 'test_id',
                    'personal_email_id': 'test_id',
                    'payment_method': {
                        'id': 'card-x4a3e73e89b85f804e357f79e',
                        'type': 'card',
                    },
                },
            ],
            [
                extra_fetcher_lavka.RowWithExtraLavka(
                    row={
                        'order_id': '01c19ea37eda4894b1cd94749fc007fb-grocery',
                        'created_at': 1635497371.1,
                        'created_idx': 1635497371,
                        'finished_at': 1635497371.1,
                        'order_nr': '211028-735-3568',
                        'client_price': '378',
                        'currency': 'RUB',
                        'address_country': 'Россия',
                        'address_city': 'Москва',
                        'address_street': 'улица Доватора',
                        'address_house': '3',
                        'address_flat': None,
                        'address_floor': None,
                        'dispatch_courier_name': 'Иван',
                        'address_comment': 'test',
                        'status': 'canceled',
                        'eats_user_id': 1,
                        'personal_phone_id': 'test_id',
                        'personal_email_id': 'test_id',
                        'payment_method': {
                            'id': 'card-x4a3e73e89b85f804e357f79e',
                            'type': 'card',
                        },
                    },
                    order_log={
                        'order_id': '01c19ea37eda4894b1cd94749fc007fb-grocery',
                        'created_idx': 1635497371,
                        'cart_items': '[{"id": "7942f683c37f49e7a177881de23f209d000300010000", "price": "37", "quantity": "3", "item_name": "Лимон", "gross_weight": "100", "cashback_charge": "0"}, {"id": "766abf20be8e454fbad3fec10ba5b5e1000200010001", "price": "147", "quantity": "3", "item_name": "Авокадо", "gross_weight": "450", "cashback_charge": "0"}, {"id": "515bcd5bc4b14c1c8998e2f0db2a08f3000100010001", "price": "13", "quantity": "2", "item_name": "Банан", "gross_weight": "110", "cashback_charge": "0"}, {"id": "8c3d828e89004fa7bd24a98997b27125000100010001", "price": "57", "quantity": "1", "item_name": "Пюре «Агуша» банан с 6 месяцев", "gross_weight": "900"}]',  # noqa: E501
                        'refund': None,
                        'delivery_cost': 90.0,
                        'courier_id': 2,
                        'place_address': (
                            '125195, Москва г, Смольная ул, дом № 47'
                        ),
                    },
                    personal={'phone': 'test', 'email': 'test'},
                    courier_personal_data={
                        'id': 2,
                        'inn': 'test_inn_2',
                        'address': 'test_address_2',
                        'phone_number': 'test_phone_number_2',
                    },
                    courier_service={
                        'id': 2,
                        'inn': 'test_inn_2',
                        'address': 'test_address_2',
                        'phone_number': 'test_phone_number_2',
                        'name': 'test_name_2',
                    },
                    user={
                        'id': 1,
                        'first_name': 'test_first_name_1',
                        'email': 'test_email_1',
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.yt(
    dyn_table_data=[
        'yt_lavka_order_log_monthly_2021_10.yaml',
        'yt_lavka_order_log_monthly_2021_09.yaml',
        'yt_eda_couriers.yaml',
        'yt_eda_courier_billing_data_history.yaml',
        'yt_eda_courier_personal_data.yaml',
        'yt_eda_courier_services.yaml',
        'yt_eda_users.yaml',
    ],
)
@pytest.mark.now('2021-10-10T09:20:41')
async def test_fetch_extra(rows, expected, yt_apply, yt_client):
    fetcher = extra_fetcher_lavka.ExtraFetcherLavka(
        yt_dummy.YtLocalDummy(yt_client),
        personal_wrapper.PersonalWrapper(personal_dummy.PersonalDummy()),
    )
    assert (
        await fetcher.fetch_extra(
            rows, request_parser_lavka.ProcessorsConfigLavka(),
        )
        == expected
    )
