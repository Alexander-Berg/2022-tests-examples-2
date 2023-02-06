from typing import List
from typing import Optional

from bson import objectid
import pytest

from tests_coupons import util


PHONE_ID = '0123456789ab0123456789cf'
PERSONAL_PHONE_ID = '123456789'


def normalize(coupon_code):
    return coupon_code.lower()


def mock_request_finish(
        order_id: str,
        code: str,
        success: bool,
        cost_usage: Optional[str] = None,
        service: Optional[str] = None,
        yandex_uid: str = 'yandex_uid',
        phone_id: str = PHONE_ID,
        personal_phone_id: str = PERSONAL_PHONE_ID,
        device_id: str = 'device_id',
        card_id: str = 'card_id',
):
    body = {
        'order_id': order_id,
        'yandex_uid': yandex_uid,
        'device_id': device_id,
        'card_id': card_id,
        'success': success,
        'coupon_id': code,
        'application_name': 'iphone',
    }
    if phone_id:
        body['phone_id'] = phone_id
    if personal_phone_id:
        body['personal_phone_id'] = personal_phone_id
    if service:
        body['service'] = service
    if cost_usage:
        body['cost_usage'] = cost_usage
    return body


@pytest.mark.parametrize(
    'body,expected_status_code',
    [
        pytest.param(
            {
                'order_id': 'r_order_id',
                'yandex_uid': 'r_yandex_uid',
                'success': True,
                'coupon_id': 'r_coupon_id',
                'phone_id': PHONE_ID,
            },
            400,
            id='missing_cost_usage',
        ),
        pytest.param(
            {
                'order_id': 'r_order_id',
                'yandex_uid': 'r_yandex_uid',
                'success': False,
                'coupon_id': 'r_coupon_id',
                'phone_id': PHONE_ID,
            },
            400,
            id='missing_application_name',
        ),
        pytest.param(
            {
                'order_id': 'r_order_id',
                'yandex_uid': 'r_yandex_uid',
                'success': True,
                'cost_usage': '13.37',
                'coupon_id': 'r_coupon_id',
                'application_name': 'iphone',
                'phone_id': PHONE_ID,
            },
            200,
            id='success_for_success_equal_true',
        ),
        pytest.param(
            {
                'order_id': 'r_order_id',
                'yandex_uid': 'r_yandex_uid',
                'success': False,
                'coupon_id': 'r_coupon_id',
                'application_name': 'iphone',
                'phone_id': PHONE_ID,
            },
            200,
            id='success_for_success_equal_false',
        ),
        pytest.param(
            {
                'order_id': 'r_order_id',
                'yandex_uid': 'r_yandex_uid',
                'success': False,
                'coupon_id': 'r_coupon_id',
                'application_name': 'iphone',
                'service': 'eats',
                'personal_phone_id': PERSONAL_PHONE_ID,
            },
            400,
            id='personal_phone_id_only_eats_service_separate_flows_off',
        ),
        pytest.param(
            {
                'order_id': 'r_order_id',
                'yandex_uid': 'r_yandex_uid',
                'success': False,
                'coupon_id': 'r_coupon_id',
                'application_name': 'iphone',
                'service': 'eats',
                'personal_phone_id': PERSONAL_PHONE_ID,
            },
            200,
            marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)],
            id='personal_phone_id_only_eats_service_separate_flows_on',
        ),
        pytest.param(
            {
                'order_id': 'r_order_id',
                'yandex_uid': 'r_yandex_uid',
                'success': False,
                'coupon_id': 'r_coupon_id',
                'application_name': 'iphone',
                'personal_phone_id': PERSONAL_PHONE_ID,
            },
            400,
            id='personal_phone_id_only_taxi_service',
        ),
        pytest.param(
            {
                'order_id': 'r_order_id',
                'yandex_uid': 'r_yandex_uid',
                'success': False,
                'coupon_id': 'r_coupon_id',
                'application_name': 'iphone',
                'service': 'eats',
                'phone_id': PHONE_ID,
            },
            200,
            id='phone_id_only_eats_service',
        ),
        pytest.param(
            {
                'order_id': 'r_order_id',
                'yandex_uid': 'r_yandex_uid',
                'success': False,
                'coupon_id': 'r_coupon_id',
                'application_name': 'iphone',
                'service': 'eats',
                'phone_id': PHONE_ID,
            },
            400,
            marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)],
            id='phone_id_only_eats_service',
        ),
        pytest.param(
            {
                'order_id': 'r_order_id',
                'yandex_uid': 'r_yandex_uid',
                'success': False,
                'coupon_id': 'r_coupon_id',
                'application_name': 'iphone',
                'phone_id': PHONE_ID,
                'personal_phone_id': PERSONAL_PHONE_ID,
            },
            200,
            id='both_phones_taxi_service',
        ),
        pytest.param(
            {
                'order_id': 'r_order_id',
                'yandex_uid': 'r_yandex_uid',
                'success': False,
                'coupon_id': 'r_coupon_id',
                'application_name': 'iphone',
                'service': 'eats',
                'phone_id': PHONE_ID,
                'personal_phone_id': PERSONAL_PHONE_ID,
            },
            200,
            id='both_phones_eats_service',
        ),
    ],
)
async def test_request_parsing(taxi_coupons, body, expected_status_code):
    """
    This test does not require any mocked data in db.
    It's intended to check that the data is parsed correctly.
    """
    response = await taxi_coupons.post('/internal/coupon_finish', body)
    assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    'code, service, order_id, reserve_key',
    [
        pytest.param(
            'CODE_1',
            None,
            'order_id_1',
            'order_id_1',
            id='taxi_without_service',
        ),
        pytest.param(
            'code_1', 'taxi', 'order_id_1', 'order_id_1', id='taxi_service',
        ),
        pytest.param(
            'lavkapromocode',
            'lavka',
            'lavka:cart:order_id',
            'lavka_lavka:cart:order_id',
            id='lavka_service',
        ),
        pytest.param(
            'eatspromocode',
            'eats',
            'cart:order',
            'eats_cart:order',
            id='eats_service',
        ),
    ],
)
@pytest.mark.parametrize(
    'separate_flows_enabled',
    [
        pytest.param(
            True, marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)],
        ),
        pytest.param(
            False, marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=False)],
        ),
    ],
)
async def test_finish_after_successful_order(
        taxi_coupons,
        mongodb,
        code,
        service,
        order_id,
        reserve_key,
        separate_flows_enabled,
):
    """
    This test checks that promocode was applied.
    """

    if service == 'eats' and not separate_flows_enabled:
        code = 'taxi_' + code  # different codes in different mongo-collections

    body = mock_request_finish(
        order_id, code, success=True, cost_usage='13.37', service=service,
    )

    expected_cost_usage = '113.37'  # 'cost_usage' in db is mocked as '100'

    response = await taxi_coupons.post('/internal/coupon_finish', json=body)
    assert response.status_code == 200

    coupon_usage = util.collection_promocode_usages2(
        mongodb, service, separate_flows_enabled,
    ).find_one({'code': normalize(code)})

    assert 'usages' in coupon_usage
    assert len(coupon_usage['usages']) == 1
    assert coupon_usage['usages'][0]['reserve'] == reserve_key
    # in those 2 assertions we got lucky with floats binary representation
    assert str(coupon_usage['usages'][0]['cost_usage']) == body['cost_usage']
    assert str(coupon_usage['cost_usage']) == expected_cost_usage


@pytest.mark.parametrize(
    'code, service, order_id',
    [
        pytest.param('CODE_2', None, 'order_id_2', id='taxi_without_service'),
        pytest.param('code_2', 'taxi', 'order_id_2', id='taxi_service'),
        pytest.param(
            'lavkapromocode2',
            'lavka',
            'lavka:cart:order_id_2',
            id='lavka_service',
        ),
        pytest.param('edapromic2', 'eats', 'cart:order2', id='eats_service'),
    ],
)
@pytest.mark.parametrize(
    'separate_flows_enabled',
    [
        pytest.param(
            True, marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)],
        ),
        pytest.param(
            False, marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=False)],
        ),
    ],
)
async def test_finish_after_unsuccessful_order(
        taxi_coupons, mongodb, code, service, order_id, separate_flows_enabled,
):
    """
    This test checks that promocode was not applied
    and given back to the user.
    """

    if service == 'eats' and not separate_flows_enabled:
        code = 'taxi_' + code  # different codes in different mongo-collections

    body = mock_request_finish(order_id, code, success=False, service=service)

    response = await taxi_coupons.post('/internal/coupon_finish', json=body)
    assert response.status_code == 200

    coupon_usage = util.collection_promocode_usages2(
        mongodb, service, separate_flows_enabled,
    ).find_one({'code': normalize(code)})

    assert 'usages' in coupon_usage
    assert coupon_usage['usages'] == []
    assert 'cost_usage' not in coupon_usage
    assert coupon_usage['rides'] == 0

    coupon_usage = util.collection_promocode_usages(
        mongodb, service, separate_flows_enabled,
    ).find_one({'code': normalize(code)})
    assert coupon_usage is None

    user_coupon = mongodb.user_coupons.find_one(
        {'yandex_uid': body['yandex_uid'], 'brand_name': 'yataxi'},
    )
    assert 'promocodes' in user_coupon
    assert len(user_coupon['promocodes']) == 1
    assert user_coupon['promocodes'][0]['code'] == normalize(code)


async def test_metrics_exist(taxi_coupons, taxi_coupons_monitor):
    body = mock_request_finish(
        'order_id_1', 'code_1', success=True, cost_usage='13.37',
    )
    response = await taxi_coupons.post('/internal/coupon_finish', json=body)
    assert response.status_code == 200

    metrics_name = 'coupon-finish-statistics'
    metrics = await taxi_coupons_monitor.get_metrics(metrics_name)

    assert metrics_name in metrics.keys()


@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.config(
    COUPONS_USAGES_EXTENDED_ANTIFRAUD_USER_IDS=['device_id', 'card_id'],
)
@pytest.mark.parametrize('token', [None, 'abcdefgh01234567'])
@pytest.mark.parametrize(
    'service, separate_flows_enabled',
    [
        pytest.param(
            'taxi',
            True,
            marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)],
        ),
        pytest.param(
            'taxi',
            False,
            marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=False)],
        ),
        pytest.param(
            'eats',
            True,
            marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)],
        ),
    ],
)
@pytest.mark.parametrize(
    'coupon_used',
    [
        pytest.param(
            True,
            id='successful_finish',
            marks=pytest.mark.filldb(
                promocode_usages2='unfinished_reserve',
                mdb_promocode_usages2='unfinished_reserve',
            ),
        ),
        pytest.param(
            False,
            id='cancel_after_reserve',
            marks=pytest.mark.filldb(
                promocode_usages2='unfinished_reserve',
                mdb_promocode_usages2='unfinished_reserve',
            ),
        ),
        pytest.param(False, id='cancel_before_reserve'),
        pytest.param(
            False,
            id='cancel_before_reserve_with_phone',
            marks=pytest.mark.filldb(
                promocode_usages2='before_reserve_phone',
                mdb_promocode_usages2='before_reserve_phone',
            ),
        ),
        pytest.param(
            False,
            id='cancel_before_reserve_with_device',
            marks=pytest.mark.filldb(
                promocode_usages2='before_reserve_device',
                mdb_promocode_usages2='before_reserve_device',
            ),
        ),
        pytest.param(
            False,
            id='cancel_before_reserve_with_card',
            marks=pytest.mark.filldb(
                promocode_usages2='before_reserve_card',
                mdb_promocode_usages2='before_reserve_card',
            ),
        ),
        pytest.param(
            False,
            id='cancel_before_reserve_with_phone_device_card',
            marks=pytest.mark.filldb(
                promocode_usages2='before_reserve_phone_device_card',
                mdb_promocode_usages2='before_reserve_phone_device_card',
            ),
        ),
    ],
)
async def test_finish_extended_antifraud(
        taxi_coupons,
        mongodb,
        service,
        token,
        coupon_used,
        separate_flows_enabled,
):
    # multiuser promocode
    code, cost_usage = 'secondpromocode', 400
    request_order_id = 'taxi_order_id'

    db_order_id = (
        request_order_id
        if service == 'taxi' or service is None
        else str(service + '_' + request_order_id)
    )

    headers = {'X-Idempotency-Token': token} if token else {}

    request = mock_request_finish(
        request_order_id,
        code,
        service=service,
        success=coupon_used,
        cost_usage=str(cost_usage),
    )
    response = await taxi_coupons.post(
        '/internal/coupon_finish', headers=headers, json=request,
    )
    assert response.status_code == 200

    if coupon_used is True:
        usage = util.collection_promocode_usages2(
            mongodb, service, separate_flows_enabled,
        ).find_one({'usages.reserve': db_order_id})
        assert usage['cost_usage'] == cost_usage
        assert usage['usages'][0]['reserve'] == db_order_id
        assert usage['usages'][0]['cost_usage'] == cost_usage
    else:
        if token:
            usages = list(
                util.collection_promocode_usages2(
                    mongodb, service, separate_flows_enabled,
                )
                .find({'code': code})
                .sort('_id'),
            )
            # In case of multiple usages docs reserve cancel will be added
            # to the first one according to the sort order by _id field.
            usage = usages[0]
            assert usage['usages'][0] == {
                'reserve': db_order_id,
                'idempotency_tokens': [token],
                'cancel_tokens': [token],
            }
        else:
            usage = util.collection_promocode_usages2(
                mongodb, service, separate_flows_enabled,
            ).find_one({'usages.reserve': db_order_id})
            assert not usage


class Usage:
    def __init__(self, order_id):
        self.reserve = order_id
        self.idempotency_tokens = set()
        self.cancel_tokens = set()

    @property
    def data(self):
        data = {'reserve': self.reserve}
        if self.idempotency_tokens:
            data['idempotency_tokens'] = self.idempotency_tokens
        if self.cancel_tokens:
            data['cancel_tokens'] = self.cancel_tokens
        return data

    def do_reserve(self, token):
        self.idempotency_tokens.add(token)

    def do_rollback(self, token):
        self.cancel_tokens.add(token)


class Usages:
    def __init__(
            self,
            value,
            code,
            series_id,
            phone_id,
            cost_usage: Optional[float] = None,
    ):
        self.value = value
        self.code = code
        self.series_id = series_id
        self.phone_id = phone_id
        self.cost_usage = cost_usage
        self.usages: List[Usage] = []
        self.rides: int = 0

    def add_usage(
            self, order_id: str, token: str, rides_diff: int, rollbacked: bool,
    ):
        usage = next(
            (x for x in self.usages if x.data['reserve'] == order_id),
            Usage(order_id),
        )
        usage.do_reserve(token)
        if rollbacked:
            usage.do_rollback(token)
        self.usages = [x for x in self.usages if x.data['reserve'] != order_id]
        self.usages.append(usage)
        self.rides += rides_diff

    def convert_to_dict(self):
        fields = self.__dict__.copy()
        fields['usages'] = [usage.data for usage in self.usages]
        return fields


async def check_usage(mongodb, code, expected: Usages):
    coupon_usage = mongodb.promocode_usages2.find_one({'code': code})
    for usage in coupon_usage['usages']:

        def convert_to_set(usage, field):
            if field in usage:
                usage[field] = set(usage[field])

        convert_to_set(usage, 'idempotency_tokens')
        convert_to_set(usage, 'cancel_tokens')

    expected_dict = expected.convert_to_dict()
    print('expect', expected_dict)
    print('got', coupon_usage)
    for key, value in expected_dict.items():
        assert coupon_usage.get(key) == value


def call_finish(order_id: str, code: str, token: str, phone_id: str):
    async def func(taxi_coupons):
        body = mock_request_finish(order_id, code, success=False)
        response = await taxi_coupons.post(
            '/internal/coupon_finish',
            json=body,
            headers={'X-Idempotency-Token': token},
        )
        assert response.status_code == 200

    return func


def call_reserve(order_id: str, code: str, token: str, phone_id: str):
    async def func(taxi_coupons):
        request = util.mock_request_reserve(
            code=code, order_id=order_id, phone_id=phone_id,
        )
        response = await taxi_coupons.post(
            'v1/couponreserve',
            json=request,
            headers={'X-Idempotency-Token': token},
        )

        assert response.status_code == 200
        assert response.json()['valid']

    return func


class UsageUpdate:
    def __init__(self, rides_diff, rollbacked):
        self.rides_diff = rides_diff
        self.rollbacked = rollbacked


def add_usage(order_id: str, token: str, usage_update=None):
    def func(usages: Usages):
        if usage_update:
            usages.add_usage(
                order_id,
                token,
                usage_update.rides_diff,
                usage_update.rollbacked,
            )

    return func


ORDER_ID = 'order_1'
CODE = 'foopromocode'
SERIES_ID = 'foo'
TOKEN = 'token1'


class Step:
    def __init__(self, caller, order_id, token, usage_update=None, code=CODE):
        self.caller = caller(
            order_id=order_id, code=code, token=token, phone_id=PHONE_ID,
        )
        self.add_usage = add_usage(order_id, token, usage_update)

    async def perform(self, taxi_coupons, usages):
        await self.caller(taxi_coupons)
        self.add_usage(usages)


@pytest.mark.parametrize(
    'steps',
    [
        pytest.param(
            [
                Step(call_reserve, ORDER_ID, TOKEN, UsageUpdate(1, False)),
                Step(call_finish, ORDER_ID, TOKEN, UsageUpdate(-1, True)),
            ],
            id='simple_rollback_after_reserve',
        ),
        pytest.param(
            [
                Step(call_reserve, ORDER_ID, TOKEN, UsageUpdate(1, False)),
                Step(
                    call_finish,
                    ORDER_ID,
                    TOKEN,
                    UsageUpdate(-1, True),
                    code=CODE.upper(),
                ),
            ],
            id='simple_rollback_after_reserve_uppercase_coupon',
        ),
        pytest.param(
            [
                Step(call_finish, ORDER_ID, TOKEN, UsageUpdate(0, True)),
                Step(call_finish, ORDER_ID, TOKEN),
            ],
            id='double_rollback',
        ),
        pytest.param(
            [
                Step(call_reserve, ORDER_ID, TOKEN, UsageUpdate(1, False)),
                Step(call_finish, ORDER_ID, TOKEN, UsageUpdate(-1, True)),
                Step(call_finish, ORDER_ID, TOKEN),
            ],
            id='double_rollback_after_reserve',
        ),
        pytest.param(
            [
                Step(call_finish, ORDER_ID, TOKEN, UsageUpdate(0, True)),
                Step(call_reserve, ORDER_ID, TOKEN),
            ],
            id='reserve_after_rollback',
        ),
        pytest.param(
            [
                Step(call_reserve, ORDER_ID, TOKEN, UsageUpdate(1, False)),
                Step(call_reserve, ORDER_ID, 'token2', UsageUpdate(1, False)),
                Step(call_finish, ORDER_ID, 'token2', UsageUpdate(-1, True)),
                Step(call_finish, ORDER_ID, TOKEN, UsageUpdate(-1, True)),
            ],
            id='different_tokens',
        ),
        pytest.param(
            [
                Step(call_finish, ORDER_ID, 'token2', UsageUpdate(0, True)),
                Step(call_reserve, ORDER_ID, TOKEN, UsageUpdate(1, False)),
                Step(call_reserve, ORDER_ID, 'token2'),
            ],
            id='block_other_token',
        ),
        pytest.param(
            [
                Step(call_finish, ORDER_ID, TOKEN, UsageUpdate(0, True)),
                Step(call_reserve, 'order_2', TOKEN, UsageUpdate(1, False)),
            ],
            id='two_orders_rollback_first',
        ),
        pytest.param(
            [
                Step(call_reserve, 'order_2', TOKEN, UsageUpdate(1, False)),
                Step(call_finish, ORDER_ID, TOKEN, UsageUpdate(0, True)),
            ],
            id='two_orders_reserve_first',
        ),
    ],
)
@pytest.mark.now('2017-03-06T11:30:00+0300')
async def test_rollback_idempotency(
        steps, taxi_coupons, mongodb, local_services,
):
    local_services.add_card()
    expected_usages = Usages(
        123.0, CODE, SERIES_ID, objectid.ObjectId(PHONE_ID),
    )

    for step in steps:
        await step.perform(taxi_coupons, expected_usages)
        await check_usage(mongodb, CODE, expected_usages)
