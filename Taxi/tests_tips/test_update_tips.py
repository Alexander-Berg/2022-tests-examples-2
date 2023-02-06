import datetime
from typing import Any
from typing import Dict
from typing import Optional

import pytest


HANDLE_URL = '/internal/tips/v1/update-tips'

BIG_NUM = (
    '1797693134862315708145274237317043567980705675258449965989174768031572607'
    '8002853876058955863276687817154045895351438246423432132688946418276846754'
    '6703537516986049910576551282076245490090389328944075868508455133942304583'
    '2369032229481658085593321233482747978262041447231687381771809192998812504'
    '040261841248583689'
)


@pytest.fixture(name='mock_order_core')
def _mock_order_core(mockserver):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        return mockserver.make_response(
            json={
                'order_id': 'some_order_id',
                'replica': 'master',
                'version': '1',
                'fields': {
                    'order': {
                        'creditcard': {
                            'tips_perc_default': 0,
                            'tips': {'type': 'flat', 'value': 10},
                        },
                        'user_id': 'some_user_id',
                    },
                },
            },
            status=200,
        )

    @mockserver.json_handler('/order-core/v1/tc/set-order-fields')
    def _mock_set_order_fields(request):
        return mockserver.make_response(json={}, status=200)


@pytest.mark.config(MAX_TIPS_BY_CURRENCY={'USD': 100})
@pytest.mark.parametrize(
    ['tips_type', 'tips_value', 'currency', 'expected_status_code'],
    [
        ('flat', '1000', 'RUB', 200),
        ('percent', '5', 'RUB', 200),
        ('flat', '0', 'RUB', 200),
        ('percent', '0', 'RUB', 200),
        ('wrong', '100', 'RUB', 400),  # invalid type
        ('flat', 'keks', 'RUB', 400),  # invalid value
        ('flat', '-123', 'RUB', 400),  # negative tips
        ('flat', BIG_NUM, 'RUB', 400),  # double overflow
        # test max tips by currency
        ('flat', '100', 'USD', 200),
        ('percent', '5', 'USD', 200),
        ('flat', '101', 'USD', 400),  # value over tips limit by currency
        ('percent', '101', 'USD', 200),
    ],
)
async def test_validate_tips(
        taxi_tips,
        mock_order_core,
        tips_type: str,
        tips_value: str,
        currency: Optional[str],
        expected_status_code: int,
):
    body = {
        'order_id': 'existing_order_id',
        'order_is_finished': True,
        'tips_type': tips_type,
        'tips_value': tips_value,
    }
    if currency is not None:
        body['currency'] = currency
    response = await taxi_tips.post(HANDLE_URL, json=body)
    assert response.status_code == expected_status_code


@pytest.mark.pgsql(
    'tips',
    queries=[
        'INSERT INTO tips.tips (id, is_final, updated_at) '
        'VALUES (\'existing_order_id\', false, \'2020-11-24T12:00:00\')',
    ],
)
@pytest.mark.parametrize(
    [
        'order_id',
        'tips_value',
        'order_is_finished',
        'expected_in_db',
        'expected_updated',
    ],
    [
        pytest.param(
            'existing_order_id', 50, False, True, True, id='in_tips_db',
        ),
        pytest.param(
            'existing_order_id_2', 50, False, True, True, id='not_in_tips_db',
        ),
        pytest.param(
            'existing_order_id', 0, False, True, False, id='zero_in_tips_db',
        ),
        pytest.param(
            'existing_order_id_2',
            0,
            False,
            False,
            False,
            id='zero_not_in_tips_db',
        ),
        pytest.param(
            'existing_order_id',
            0,
            True,
            True,
            True,
            id='zero_in_tips_db_final',
        ),
        pytest.param(
            'existing_order_id_2',
            0,
            True,
            False,
            False,
            id='zero_not_in_tips_db_final',
        ),
    ],
)
@pytest.mark.now('2020-11-24T12:00:00Z')
async def test_tips_db(
        taxi_tips,
        mock_order_core,
        tips_postgres_db,
        order_id: str,
        tips_value: int,
        expected_in_db: bool,
        expected_updated: bool,
        order_is_finished: bool,
):
    body = {
        'order_id': order_id,
        'order_is_finished': order_is_finished,
        'tips_type': 'flat',
        'tips_value': str(tips_value),
        'currency': 'RUB',
    }
    response = await taxi_tips.post(HANDLE_URL, json=body)
    assert response.status_code == 200
    tips_postgres_db.execute(
        'SELECT id, updated_at '
        'FROM tips.tips '
        f'WHERE id = \'{order_id}\'',
    )
    orders = list(row for row in tips_postgres_db)
    if expected_in_db:
        assert len(orders) == 1
        db_order_id, db_updated_at = orders[0]
        assert db_order_id == order_id
        if expected_updated:
            # checking against old row in db
            # since mock.now doesnt work for postgres
            assert db_updated_at > datetime.datetime.fromisoformat(
                '2020-11-24T12:00:00',
            )
        else:
            assert db_updated_at == datetime.datetime.fromisoformat(
                '2020-11-24T12:00:00',
            )
    else:
        assert len(orders) == 0  # pylint: disable=len-as-condition


async def test_orders_db_missing_order(taxi_tips, mock_order_core):
    body = {
        'order_id': 'nonexistent_order_id',
        'order_is_finished': True,
        'tips_type': 'flat',
        'tips_value': '50',
        'currency': 'RUB',
    }
    response = await taxi_tips.post(HANDLE_URL, json=body)
    assert response.status_code == 404


@pytest.mark.parametrize(
    ['order_id', 'tips_type', 'tips_value'],
    [
        ('existing_order_id', 'flat', '50'),
        ('existing_order_id', 'percent', '5'),
    ],
)
async def test_orders_db(
        taxi_tips,
        mock_order_core,
        mongodb,
        order_id: str,
        tips_type: str,
        tips_value: str,
):
    body = {
        'order_id': order_id,
        'order_is_finished': True,
        'tips_type': tips_type,
        'tips_value': tips_value,
        'currency': 'RUB',
    }
    response = await taxi_tips.post(HANDLE_URL, json=body)
    assert response.status_code == 200
    order = mongodb.orders.find_one(order_id)
    assert order is not None
    if tips_type == 'percent':
        assert order['creditcard']['tips_perc_default'] == float(tips_value)
    else:
        assert order['creditcard']['tips_perc_default'] == 0
    assert order['creditcard']['tips']['type'] == tips_type
    assert order['creditcard']['tips']['value'] == float(tips_value)


def _make_get_fields_response(
        tips_perc_default: Optional[int],
        tips_type: Optional[str],
        tips_value: Optional[int],
        user_id: Optional[str] = 'some_user_id',
        allow_none: bool = False,
) -> Dict[str, Any]:
    fields: Dict[str, Any] = {}
    if tips_perc_default is not None or allow_none:
        creditcard = fields.setdefault('order', {}).setdefault(
            'creditcard', {},
        )
        creditcard['tips_perc_default'] = tips_perc_default
    if tips_type is not None or allow_none:
        creditcard = fields.setdefault('order', {}).setdefault(
            'creditcard', {},
        )
        creditcard.setdefault('tips', {})['type'] = tips_type
    if tips_value is not None or allow_none:
        creditcard = fields.setdefault('order', {}).setdefault(
            'creditcard', {},
        )
        creditcard.setdefault('tips', {})['value'] = tips_value
    if user_id is not None:
        fields.setdefault('order', {})['user_id'] = user_id
    response = {
        'order_id': 'some_order_id',
        'replica': 'master',
        'version': '1',
        'fields': fields,
    }
    return response


@pytest.mark.parametrize(
    [
        'get_fields_status_code',
        'get_fields_200_response',
        'set_fields_status_code',
        'expected_status_code',
    ],
    [
        # usual scenarios
        pytest.param(
            200,
            _make_get_fields_response(0, 'flat', 30),
            200,
            200,
            id='different_tips',
        ),
        pytest.param(
            200,
            _make_get_fields_response(0, 'flat', 50),
            None,
            200,
            id='matching_tips',
        ),
        # missing fields in order
        pytest.param(
            200,
            _make_get_fields_response(0, None, None),
            200,
            200,
            id='no_tips_set',
        ),
        pytest.param(
            200,
            _make_get_fields_response(None, None, None),
            200,
            200,
            id='no_tips_or_default_set',
        ),
        pytest.param(
            200,
            _make_get_fields_response(0, 'flat', 30, None),
            None,
            409,
            id='no_user_id_in_order',
        ),
        # explicit none instead of missing values
        pytest.param(
            200,
            _make_get_fields_response(0, None, None, allow_none=True),
            200,
            200,
            id='no_tips_set_explicit_none',
        ),
        pytest.param(
            200,
            _make_get_fields_response(None, None, None, allow_none=True),
            200,
            200,
            id='no_tips_or_default_set_explicit_none',
        ),
        # unexpected order-core responses
        pytest.param(400, None, None, 500, id='invalid_get_request'),
        pytest.param(
            200,
            _make_get_fields_response(0, 'flat', 30),
            400,
            500,
            id='invalid_update_request',
        ),
        pytest.param(404, None, None, 404, id='order_not_found_during_get'),
        pytest.param(
            200,
            _make_get_fields_response(0, 'flat', 30),
            404,
            404,
            id='order_not_found_during_update',
        ),
        pytest.param(
            200,
            _make_get_fields_response(0, 'flat', 30),
            409,
            409,
            id='order_proc_update_conflict',
        ),
    ],
)
async def test_order_core(
        taxi_tips,
        mockserver,
        get_fields_status_code: int,
        get_fields_200_response: Optional[Dict[str, Any]],
        set_fields_status_code: Optional[int],
        expected_status_code: int,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        if get_fields_status_code == 200:
            body = get_fields_200_response
        else:
            body = {'code': str(get_fields_status_code), 'message': 'msg'}
        return mockserver.make_response(
            json=body, status=get_fields_status_code,
        )

    @mockserver.json_handler('/order-core/v1/tc/set-order-fields')
    def _mock_set_order_fields(request):
        assert set_fields_status_code is not None
        if set_fields_status_code == 200:
            body = {}
        else:
            body = {'code': str(set_fields_status_code), 'message': 'msg'}
        return mockserver.make_response(
            json=body, status=set_fields_status_code,
        )

    body = {
        'order_id': 'existing_order_id',
        'order_is_finished': True,
        'tips_type': 'flat',
        'tips_value': '50',
        'currency': 'RUB',
    }
    response = await taxi_tips.post(HANDLE_URL, json=body)
    assert response.status_code == expected_status_code
    if set_fields_status_code is None:
        assert _mock_set_order_fields.times_called == 0
    elif set_fields_status_code == 409:
        assert _mock_set_order_fields.times_called == 3
    else:
        assert _mock_set_order_fields.times_called == 1
