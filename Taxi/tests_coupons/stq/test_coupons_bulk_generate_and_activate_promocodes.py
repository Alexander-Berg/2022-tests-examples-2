import pytest

from tests_coupons import util

USERS_LIST = [
    {'yandex_uid': 'yandex_uid_0', 'application_name': 'iphone'},
    {
        'yandex_uid': 'yandex_uid_1',
        'application_name': 'iphone',
        'brand_name': 'yataxi',
    },
    {'yandex_uid': 'yandex_uid_2', 'brand_name': 'yataxi'},
]

TOKEN = 'idempotency_key_1'
SERIES_ID = 'series_id_1'


def check_promocodes(
        mongodb,
        generate_token,
        series_id,
        yandex_uid,
        expected_count,
        expected_user_count,
        value=None,
        value_numeric=None,
        expire_at=None,
):
    promocodes = list(
        mongodb.promocodes.find({'generate_token': generate_token}),
    )
    user_coupons = list(
        mongodb.user_coupons.find(
            {'yandex_uid': yandex_uid, 'brand_name': 'yataxi'},
        ),
    )
    assert len(promocodes) == expected_count

    if promocodes:
        promocode = promocodes[0]
        assert promocode['series_id'] == series_id

        if value:
            assert promocode['value'] == value
        if value_numeric:
            assert promocode['value'] == float(value_numeric)
        if expire_at:
            assert promocode['expire_at'] == util.utc_datetime_from_str(
                expire_at,
            )

    assert len(user_coupons) == expected_user_count
    if user_coupons:
        user_coupon = user_coupons[0]
        assert len(user_coupon['promocodes']) == expected_user_count

    if user_coupons and promocodes:
        assert (
            promocodes[0]['code'] == user_coupons[0]['promocodes'][0]['code']
        )


@pytest.mark.now('2019-06-24T20:00:00+0300')
async def test_success_bulk_generate_and_activate(stq_runner, mongodb):
    kwargs = {'token': TOKEN, 'users_list': USERS_LIST, 'series_id': SERIES_ID}
    await stq_runner.coupons_bulk_generate_and_activate_promocodes.call(
        task_id='test_task_id', kwargs=kwargs,
    )

    for user in USERS_LIST:
        yandex_uid = user['yandex_uid']
        generate_token = f'{TOKEN}_{yandex_uid}'

        check_promocodes(
            mongodb=mongodb,
            generate_token=generate_token,
            yandex_uid=yandex_uid,
            series_id=SERIES_ID,
            expected_count=1,
            expected_user_count=1,
        )


@pytest.mark.parametrize(
    'value, value_numeric,is_valid',
    [
        pytest.param(None, None, False, id='without value'),
        pytest.param(100, None, True, id='int value'),
        pytest.param(None, '123.4', True, id='float str value'),
        pytest.param(
            200, None, False, id='invalid int value (greater than series has)',
        ),
        pytest.param(
            None,
            '432.1',
            False,
            id='invalid float str value (greater than series has)',
        ),
    ],
)
@pytest.mark.now('2019-06-24T20:00:00+0300')
async def test_success_bulk_generate_and_activate_with_value(
        stq_runner, mongodb, value, value_numeric, is_valid,
):
    kwargs = {
        'token': TOKEN,
        'users_list': USERS_LIST,
        'series_id': 'series_id_4',
        'value': value,
        'value_numeric': value_numeric,
    }
    await stq_runner.coupons_bulk_generate_and_activate_promocodes.call(
        task_id='test_task_id', kwargs=kwargs, expect_fail=not is_valid,
    )

    for user in USERS_LIST:
        yandex_uid = user['yandex_uid']
        generate_token = f'{TOKEN}_{yandex_uid}'

        if is_valid:
            check_promocodes(
                mongodb=mongodb,
                generate_token=generate_token,
                yandex_uid=yandex_uid,
                series_id='series_id_4',
                expected_count=1,
                expected_user_count=1,
                value=value,
                value_numeric=value_numeric,
            )
        else:
            check_promocodes(
                mongodb=mongodb,
                generate_token=generate_token,
                yandex_uid=yandex_uid,
                series_id='series_id_4',
                expected_count=0,
                expected_user_count=0,
            )


@pytest.mark.now('2019-03-01T12:00:00+0300')
@pytest.mark.parametrize(
    'expire_at, is_valid',
    [
        pytest.param(
            '2019-03-01T11:00:00+03:00', False, id='expire_at less than now',
        ),
        pytest.param(
            '2019-03-01T12:00:00+03:00', False, id='expire_at equals to now',
        ),
        pytest.param(
            '2019-06-25T13:00:00+03:00', True, id='expire_at more than now',
        ),
    ],
)
@pytest.mark.now('2019-06-24T20:00:00+0300')
async def test_success_bulk_generate_and_activate_with_expire_at(
        stq_runner, mongodb, expire_at, is_valid,
):
    kwargs = {
        'token': TOKEN,
        'users_list': USERS_LIST,
        'series_id': SERIES_ID,
        'expire_at': expire_at,
    }
    await stq_runner.coupons_bulk_generate_and_activate_promocodes.call(
        task_id='test_task_id', kwargs=kwargs, expect_fail=not is_valid,
    )

    for user in USERS_LIST:
        yandex_uid = user['yandex_uid']
        generate_token = f'{TOKEN}_{yandex_uid}'

        if is_valid:
            check_promocodes(
                mongodb=mongodb,
                generate_token=generate_token,
                yandex_uid=yandex_uid,
                series_id=SERIES_ID,
                expected_count=1,
                expected_user_count=1,
                expire_at=expire_at,
            )
        else:
            check_promocodes(
                mongodb=mongodb,
                generate_token=generate_token,
                yandex_uid=yandex_uid,
                series_id=SERIES_ID,
                expected_count=0,
                expected_user_count=0,
            )


@pytest.mark.now('2019-06-24T20:00:00+0300')
async def test_bulk_generate_and_activate_try_two_times(
        stq_runner, mongodb, stq,
):
    kwargs = {'token': TOKEN, 'users_list': USERS_LIST, 'series_id': SERIES_ID}
    await stq_runner.coupons_bulk_generate_and_activate_promocodes.call(
        task_id='test_task_id1', kwargs=kwargs,
    )

    await stq_runner.coupons_bulk_generate_and_activate_promocodes.call(
        task_id='test_task_id2', kwargs=kwargs,
    )

    assert stq.is_empty

    for user in USERS_LIST:
        yandex_uid = user['yandex_uid']
        generate_token = f'{TOKEN}_{yandex_uid}'

        check_promocodes(
            mongodb=mongodb,
            generate_token=generate_token,
            yandex_uid=yandex_uid,
            series_id=SERIES_ID,
            expected_count=1,
            expected_user_count=1,
        )


@pytest.mark.now('2019-06-24T20:00:00+0300')
async def test_bulk_generate_and_activate_non_unique(stq_runner, mongodb):
    series_id = 'non_unique'

    kwargs = {'token': TOKEN, 'users_list': USERS_LIST, 'series_id': series_id}
    await stq_runner.coupons_bulk_generate_and_activate_promocodes.call(
        task_id='test_task_id', kwargs=kwargs,
    )

    for user in USERS_LIST:
        yandex_uid = user['yandex_uid']
        generate_token = f'{TOKEN}_{yandex_uid}'

        check_promocodes(
            mongodb=mongodb,
            generate_token=generate_token,
            yandex_uid=yandex_uid,
            series_id=series_id,
            expected_count=0,
            expected_user_count=1,
        )


@pytest.mark.config(
    COUPONS_BULK_GENERATE_AND_ACTIVATE_SETTINGS={'max_bulk_size': 1},
)
@pytest.mark.now('2019-06-24T20:00:00+0300')
async def test_bulk_generate_and_activate_split_to_tasks(
        stq_runner, mongodb, stq,
):
    series_id = 'non_unique'

    kwargs = {'token': TOKEN, 'users_list': USERS_LIST, 'series_id': series_id}
    await stq_runner.coupons_bulk_generate_and_activate_promocodes.call(
        task_id='test_task_id', kwargs=kwargs,
    )

    assert (
        stq.coupons_bulk_generate_and_activate_promocodes.times_called
        == len(USERS_LIST)
    )
