import pytest

from . import test_order_start
from . import utils


EATS_ID = '123'
PICKER_ID = '1'
CLAIM_ID = 'CLAIM_ID_20'


@pytest.fixture(name='order_start_environment')
def _order_start_environment(mockserver):
    class Environment:
        def __init__(self):
            self.orders = set()
            self.claims = {}
            self._build_mocks()

        def add_order(self, eats_id: str):
            self.orders.add(eats_id)

        def add_claim(self, claim_id: str, status: str):
            self.claims[claim_id] = {'status': status}

        def _build_mocks(self):
            @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
            def _mock_eats_picker_payment(request):
                assert request.query.get('card_type') == 'TinkoffBank'
                assert request.query.get('card_value') == 'cid_1'
                eats_id = request.json.get('order_id')
                if eats_id in self.orders:
                    return mockserver.make_response(
                        json={'order_id': eats_id}, status=200,
                    )
                return mockserver.make_response(status=404)

            @mockserver.json_handler(
                '/b2b-taxi/b2b/cargo/integration/v2/claims/info',
            )
            def _mock_b2b(request):
                claim_id = request.query.get('claim_id')
                assert (
                    request.headers['Authorization']
                    == 'Bearer testsuite-api-cargo-token'
                )
                if claim_id in self.claims:
                    claim = self.claims[claim_id]
                    return mockserver.make_response(
                        status=200,
                        json=dict(
                            test_order_start.CARGO_INFO_MOCK_RESPONSE,
                            id=claim_id,
                            status=claim['status'],
                        ),
                    )
                return mockserver.make_response(
                    status=404,
                    json=test_order_start.CARGO_INFO_MOCK_404_RESPONSE,
                )

            @mockserver.json_handler(
                '/eats-products/api/v2/place/assortment/details',
            )
            def _mock_eats_products(request):
                return {
                    'products': [
                        {
                            'origin_id': 'weight_item_id',
                            'name': '',
                            'description': '',
                            'is_available': True,
                            'price': 7.5,
                            'adult': False,
                            'shipping_type': '',
                            'images': [],
                            'measure': {
                                'unit': 'GRM',
                                'value': 1000,
                                'quantum': 0.75,
                            },
                        },
                        {
                            'origin_id': 'not_weight_item_id',
                            'name': '',
                            'description': '',
                            'is_available': True,
                            'price': 20,
                            'adult': False,
                            'shipping_type': '',
                            'images': [],
                        },
                    ],
                    'categories': [],
                }

            self.mock_eats_picker_payment = _mock_eats_picker_payment
            self.mock_b2b = _mock_b2b
            self.mock_eats_products = _mock_eats_products

    return Environment()


@pytest.mark.parametrize(
    ['eats_id', 'picker_id', 'is_found'],
    [
        ('12345', PICKER_ID, False),
        (EATS_ID, '11', False),
        (EATS_ID, PICKER_ID, True),
    ],
)
@pytest.mark.parametrize(
    ['state', 'do_autostart_by_state'],
    [
        ('new', False),
        ('assigned', True),
        ('picking', False),
        ('picked_up', False),
        ('paid', False),
        ('cancelled', False),
        ('complete', False),
    ],
)
@pytest.mark.parametrize(
    ['flow_type', 'claim_id', 'claim_status', 'do_autostart_by_claim'],
    [
        ('picking_packing', CLAIM_ID, 'pickup_arrived', True),
        ('picking_only', CLAIM_ID, 'pickup_arrived', True),
        ('picking_only', None, 'pickup_arrived', True),
        ('picking_only', CLAIM_ID, 'accepted', False),
        ('picking_only', 'unknown_claim_id', 'pickup_arrived', False),
        ('picking_only', CLAIM_ID, 'ololo', False),
    ],
)
@pytest.mark.parametrize('payment_error', [False, True])
@utils.send_order_events_config()
async def test_stq_autostart_order(
        order_start_environment,
        stq_runner,
        create_order,
        get_order,
        get_last_order_status,
        eats_id,
        picker_id,
        is_found,
        state,
        do_autostart_by_state,
        flow_type,
        claim_id,
        claim_status,
        do_autostart_by_claim,
        payment_error,
        mock_processing,
        mockserver,
):
    timer_id = 12345

    @mockserver.json_handler('/eats-picker-timers/api/v1/timer/finish')
    def mock_eats_picker_timers(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            status=200, json={'timer_id': timer_id},
        )

    order_id = create_order(
        eats_id=EATS_ID,
        picker_id=PICKER_ID,
        state=state,
        flow_type=flow_type,
        claim_id=claim_id,
    )
    order_start_environment.add_claim(CLAIM_ID, claim_status)
    if not payment_error:
        order_start_environment.add_order(EATS_ID)

    await stq_runner.eats_picker_orders_autostart_picking.call(
        task_id=eats_id,
        kwargs={
            'eats_id': eats_id,
            'picker_id': picker_id,
            'timeout': 10,
            'retries': 3,
            'timer_id': timer_id,
            'timestamp': '2021-06-08T10:00:00+05:00',
        },
    )

    order = get_order(order_id)
    last_status = get_last_order_status(order_id)
    if (
            state != 'picking'
            and is_found
            and do_autostart_by_state
            and do_autostart_by_claim
            and not payment_error
    ):
        assert order['state'] == 'picking'
        assert last_status['state'] == 'picking'
        assert last_status['author_id'] is None
        assert last_status['author_type'] == 'system'
        assert last_status['comment'] == 'autostart'

        assert mock_processing.times_called == 1
        assert mock_eats_picker_timers.times_called == 1
    else:
        assert order['state'] == state
        assert last_status['state'] == state
        assert mock_eats_picker_timers.times_called == 0


@pytest.mark.parametrize(
    'retries, exec_tries, reschedule_counter, do_execute, do_reschedule',
    [
        (1, 0, 0, True, True),
        (1, 1, 0, False, False),
        (3, 0, 0, True, True),
        (3, 1, 1, True, True),
        (3, 0, 3, False, False),
    ],
)
async def test_stq_autostart_order_retries(
        order_start_environment,
        mockserver,
        stq_runner,
        testpoint,
        mocked_time,
        create_order,
        get_order,
        get_last_order_status,
        retries,
        exec_tries,
        reschedule_counter,
        do_execute,
        do_reschedule,
):
    order_id = create_order(
        eats_id=EATS_ID,
        picker_id=PICKER_ID,
        state='assigned',
        flow_type='picking_only',
        claim_id=CLAIM_ID,
    )
    order_start_environment.add_claim(CLAIM_ID, 'pickup_arrived')
    order_start_environment.add_order(EATS_ID)

    @testpoint('start_order_exception')
    def start_order_exception_tp(data):
        mocked_time.sleep(10)
        return {'inject_std_exception': True}

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    await stq_runner.eats_picker_orders_autostart_picking.call(
        task_id=EATS_ID,
        kwargs={
            'eats_id': EATS_ID,
            'picker_id': PICKER_ID,
            'timeout': 0,
            'retries': retries,
            'timer_id': 12345,
            'timestamp': '2021-06-08T10:00:00+05:00',
        },
        exec_tries=exec_tries,
        reschedule_counter=reschedule_counter,
    )

    order = get_order(order_id)
    last_status = get_last_order_status(order_id)
    assert order['state'] == 'assigned'
    assert last_status['state'] == 'assigned'

    assert start_order_exception_tp.times_called == int(do_execute)
    assert mock_stq_reschedule.times_called == int(do_reschedule)
