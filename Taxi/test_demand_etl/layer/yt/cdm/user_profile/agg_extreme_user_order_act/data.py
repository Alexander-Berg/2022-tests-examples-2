first_but_unsuccess_order = dict(
    user_phone_pd_id='some_dude',
    brand='yandex',
    order_id='aaa',
    utc_order_created_dttm='2020-10-03 12:00:00',
    success_order_flg=False,
)
first_success_order_in_yandex = dict(
    user_phone_pd_id='some_dude',
    brand='yandex',
    order_id='bbb',
    utc_order_created_dttm='2020-10-03 18:00:00',
    success_order_flg=True,
)
last_success_order_in_yandex = dict(
    user_phone_pd_id='some_dude',
    brand='yandex',
    order_id='ccc',
    utc_order_created_dttm='2020-10-05 18:00:00',
    success_order_flg=True,
)
first_success_order_in_uber = dict(
    user_phone_pd_id='some_dude',
    brand='uber',
    order_id='ddd',
    utc_order_created_dttm='2020-10-01 17:00:00',
    success_order_flg=True,
)
single_order_by_another_dude = dict(
    user_phone_pd_id='another_dude',
    brand='yandex',
    order_id='eee',
    utc_order_created_dttm='2020-10-03 11:00:00',
    success_order_flg=True,
)
ORDER = [
    first_but_unsuccess_order,
    first_success_order_in_yandex,
    last_success_order_in_yandex,
    first_success_order_in_uber,
    single_order_by_another_dude,
]

fake_order = dict(
        user_phone_pd_id='some_dude',
        brand='uber',
        order_id='xxx',
        utc_order_created_dttm='1970-00-00 00:00:00',
        success_order_flg=False,
    )
UBER_ORDER = [
    # На самом деле, этих заказов нет, но надо что-то подложить, чтобы Spark смог распарсить схему.
    fake_order
]

another_dude_all_history = dict(
    phone_pd_id='another_dude',
    brand_name='__all__',
    first_order_id='xxx',
    utc_first_order_dttm='2020-09-03 10:00:00',
    last_order_id='yyy',
    utc_last_order_dttm='2020-09-04 11:00:00'
)
another_dude_uber_history = dict(
    phone_pd_id='another_dude',
    brand_name='uber',
    first_order_id='xxx',
    utc_first_order_dttm='2020-09-03 11:00:00',
    last_order_id='xxx',
    utc_last_order_dttm='2020-09-03 11:00:00'
)
another_dude_yandex_history = dict(
    phone_pd_id='another_dude',
    brand_name='yandex',
    first_order_id='yyy',
    utc_first_order_dttm='2020-09-04 10:00:00',
    last_order_id='yyy',
    utc_last_order_dttm='2020-09-04 10:00:00'
)
CURRENT_EXTREME_USER_ORDER = [
    another_dude_all_history,
    another_dude_uber_history,
    another_dude_yandex_history,
]

EXPECTED = [
    dict(
        phone_pd_id='another_dude',
        brand_name='__all__',
        first_order_id='xxx',
        utc_first_order_dttm='2020-09-03 10:00:00',
        last_order_id='eee',
        utc_last_order_dttm='2020-10-03 11:00:00'
    ),
    dict(
        phone_pd_id='another_dude',
        brand_name='uber',
        first_order_id='xxx',
        utc_first_order_dttm='2020-09-03 11:00:00',
        last_order_id='xxx',
        utc_last_order_dttm='2020-09-03 11:00:00'
    ),
    dict(
        phone_pd_id='another_dude',
        brand_name='yandex',
        first_order_id='yyy',
        utc_first_order_dttm='2020-09-04 10:00:00',
        last_order_id='eee',
        utc_last_order_dttm='2020-10-03 11:00:00'
    ),
    dict(
        phone_pd_id='some_dude',
        brand_name='__all__',
        first_order_id='ddd',
        utc_first_order_dttm='2020-10-01 17:00:00',
        last_order_id='ccc',
        utc_last_order_dttm='2020-10-05 18:00:00'
    ),
    dict(
        phone_pd_id='some_dude',
        brand_name='uber',
        first_order_id='ddd',
        utc_first_order_dttm='2020-10-01 17:00:00',
        last_order_id='ddd',
        utc_last_order_dttm='2020-10-01 17:00:00'
    ),
    dict(
        phone_pd_id='some_dude',
        brand_name='yandex',
        first_order_id='bbb',
        utc_first_order_dttm='2020-10-03 18:00:00',
        last_order_id='ccc',
        utc_last_order_dttm='2020-10-05 18:00:00'
    ),
]
