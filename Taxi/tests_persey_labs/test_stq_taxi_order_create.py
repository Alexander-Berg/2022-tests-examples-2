import pytest


PERSEY_USER_AGENT = 'persey'

PERSONAL_PHONE_ID = 'bcbd359dd939443b8880d1f9f62876d6'
USER_ID = '9c264f0d5dda41b382586872b10f2033'
ORDER_ID = '4d0aa64de77628c49613c7d21a04738d'

ORDERSEARCH_POLLING_TIMES = 3


@pytest.fixture(name='mock_personal')
def _mock_personal(mockserver):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_store(request, *args, **kwargs):
        return {'id': PERSONAL_PHONE_ID, 'value': request.json['value']}

    return _mock_store


class IntApiContext:
    def __init__(self):
        self.search_status = 'unknown'
        self.handlers = {}


@pytest.fixture(name='mock_int_api')
def _mock_int_api(mockserver):
    context = IntApiContext()

    @mockserver.json_handler('/int-authproxy/v1/profile')
    def _mock_profile(request, *args, **kwargs):
        assert request.headers.get('User-Agent') == PERSEY_USER_AGENT
        return {
            'dont_ask_name': False,
            'experiments': [],
            'name': '',
            'personal_phone_id': PERSONAL_PHONE_ID,
            'user_id': USER_ID,
        }

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _mock_orderestimate(request, *args, **kwargs):
        assert request.headers.get('User-Agent') == PERSEY_USER_AGENT
        assert len(request.json.get('route', [])) == 1
        assert request.json['route'][0] == [35.5, 55.5]
        return {
            'offer': 'c9e8879792bc595eecc7b5ddb4f4b8a6',
            'is_fixed_price': True,
            'service_levels': [],
            'currency_rules': {
                'code': 'RUB',
                'sign': '₽',
                'template': '$VALUE$ $SIGN$$CURRENCY$',
                'text': 'руб.',
            },
        }

    @mockserver.json_handler('/int-authproxy/v1/orders/draft')
    def _mock_orderdraft(request, *args, **kwargs):
        assert request.headers.get('User-Agent') == PERSEY_USER_AGENT
        assert len(request.json.get('route', [])) == 1
        assert request.json['route'][0] == {
            'fullname': 'Somewhere',
            'geopoint': [35.5, 55.5],
        }
        return {'orderid': ORDER_ID}

    @mockserver.json_handler('/int-authproxy/v1/orders/commit')
    def _mock_ordercommit(request, *args, **kwargs):
        assert request.headers.get('User-Agent') == PERSEY_USER_AGENT
        return {'orderid': ORDER_ID, 'status': 'search'}

    polling_counter = {'value': 0}

    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_ordersearch(request, *args, **kwargs):
        assert request.headers.get('User-Agent') == PERSEY_USER_AGENT

        polling_counter['value'] += 1

        if polling_counter['value'] < ORDERSEARCH_POLLING_TIMES:
            status = 'search'
        else:
            status = context.search_status

        return {'orders': [{'orderid': ORDER_ID, 'status': status}]}

    context.handlers = {
        'profile': _mock_profile,
        'orderestimate': _mock_orderestimate,
        'orderdraft': _mock_orderdraft,
        'ordercommit': _mock_ordercommit,
        'ordersearch': _mock_ordersearch,
    }

    return context


def get_order_info_for_shift(shift_id, db_cursor):
    query = f"""
        SELECT
            taxi_order_id, taxi_order_state
        FROM persey_labs.lab_employee_shifts
        WHERE
            id = {shift_id}
    """
    db_cursor.execute(query)
    rows = list(db_cursor)
    return rows[0] if rows else None


@pytest.mark.now('2020-11-10T08:40:00+0300')
@pytest.mark.config(
    PERSEY_TAXI_ORDER_CREATE_SETTINGS={
        'draft_commit_enabled': True,
        'search_polling_delay': 10,
        'tariff_name': 'persey-tariff',
    },
)
@pytest.mark.parametrize(
    [
        'shift_id',
        'ordersearch_status',
        'expected_state',
        'new_order_created',
        'order_searched',
    ],
    [
        (1, 'driving', 'committed', True, True),
        (1, 'waiting', 'committed', True, True),
        (1, 'transporting', 'committed', True, True),
        (1, 'expired', 'incomplete', True, True),
        (2, 'driving', 'committed', False, True),
        (3, 'driving', 'committed', False, False),
        (4, 'driving', 'committed', True, True),
        (5, 'driving', 'planned', False, False),
    ],
)
async def test_stq_taxi_order_create(
        stq_runner,
        pgsql,
        load_json,
        mock_personal,
        mock_int_api,
        fill_labs,
        taxi_persey_labs,
        shift_id,
        ordersearch_status,
        expected_state,
        new_order_created,
        order_searched,
):
    fill_labs.load_lab_entities(load_json('labs.json'))
    fill_labs.load_employees('my_lab_id_1', load_json('employees.json'))
    mock_int_api.search_status = ordersearch_status

    await stq_runner.persey_taxi_order_create.call(
        task_id=str(shift_id), kwargs={'shift_id': shift_id},
    )

    assert mock_personal.times_called == 1
    for handler, mock in mock_int_api.handlers.items():
        if handler == 'profile':
            assert mock.times_called == 1
        elif handler == 'ordersearch':
            assert mock.times_called == ORDERSEARCH_POLLING_TIMES * int(
                order_searched,
            )
        else:
            assert mock.times_called == int(new_order_created)
            if handler in ['estimate', 'orderdraft'] and mock.times_called:
                request = mock.next_call()['request']
                body = request.json
                assert body['payment'] == {
                    'type': 'corp',
                    'payment_method_id': 'corp-123456',
                }

    db_cursor = pgsql['persey_labs'].cursor()
    assert get_order_info_for_shift(shift_id, db_cursor) == (
        ORDER_ID if expected_state != 'planned' else None,
        expected_state,
    )
