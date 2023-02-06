import pytest


@pytest.fixture(name='mock_dispath_performer_assigning')
def _mock_dispath_performer_assigning(mockserver):
    @mockserver.json_handler(
        '/cargo-dispatch/v1/waybill/mark/performer-assigning',
    )
    def mock(request):
        context.last_request = request.json
        return mockserver.make_response(
            status=context.status_code, json=context.response_body,
        )

    class Context:
        def __init__(self):
            self.last_request = None
            self.status_code = 200
            self.response_body = {}
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='mock_claims_performer_assigned')
def _mock_claims_performer_assigned(mockserver):
    @mockserver.json_handler(
        '/cargo-claims/v1/claims/mark/taxi-order-performer-assigned',
    )
    def mock(request):
        context.last_request = request.json
        return mockserver.make_response(
            status=context.status_code, json=context.response_body,
        )

    class Context:
        def __init__(self):
            self.last_request = None
            self.status_code = 200
            self.response_body = {}
            self.handler = mock

    context = Context()

    return context


def build_kwargs(
        order_id, lookup_version: int = 1, is_manual_dispatch: bool = None,
):
    kwargs = {
        'cargo_ref_id': f'order/{order_id}',
        'taxi_order_id': 'taxi-order',
        'driver_id': 'park1_driver1',
        'park_id': 'park1',
        'lookup_version': lookup_version,
    }
    if is_manual_dispatch is not None:
        kwargs['is_manual_dispatch'] = is_manual_dispatch
    return kwargs.copy()


@pytest.mark.config(
    CARGO_ORDERS_PERFORMER_ASSIGNING_STQ={
        'notify_ld': True,
        'max-reschedules': 5,
        'reschedule-sleep-ms': 5000,
    },
)
@pytest.mark.parametrize('is_manual_dispatch', [None, False, True])
async def test_cargo_taxi_order_performer_assigning(
        taxi_cargo_orders,
        stq_runner,
        my_waybill_info,
        default_order_id,
        mock_dispath_performer_assigning,
        mock_claims_performer_assigned,
        is_manual_dispatch: bool,
):
    notify_expected = is_manual_dispatch is True

    await stq_runner.cargo_taxi_order_performer_assigning.call(
        task_id='test_stq',
        kwargs=build_kwargs(
            default_order_id, is_manual_dispatch=is_manual_dispatch,
        ),
    )

    assert (
        mock_dispath_performer_assigning.handler.has_calls == notify_expected
    )
    if notify_expected:
        assert mock_dispath_performer_assigning.last_request == {
            'waybill_ref': 'waybill-ref',
            'order_id': default_order_id,
            'taxi_order_id': 'taxi-order',
            'lookup_version': 1,
            'manual_dispatch': True,
            'performer': {'park_id': 'park1', 'driver_id': 'driver1'},
        }

    assert mock_claims_performer_assigned.handler.has_calls
    assert mock_claims_performer_assigned.last_request == {
        'driver_profile_id': 'driver1',
        'park_id': 'park1',
        'lookup_version': 1,
        'claims_ids': ['some_claim_id'],
    }


@pytest.mark.parametrize('is_manual_dispatch', [None, False, True])
async def test_do_not_notify_ld(
        taxi_cargo_orders,
        stq_runner,
        my_waybill_info,
        default_order_id,
        mock_dispath_performer_assigning,
        mock_claims_performer_assigned,
        is_manual_dispatch: bool,
):
    await stq_runner.cargo_taxi_order_performer_assigning.call(
        task_id='test_stq',
        kwargs=build_kwargs(
            default_order_id, is_manual_dispatch=is_manual_dispatch,
        ),
    )
    assert not mock_dispath_performer_assigning.handler.has_calls


@pytest.fixture
def __change_order_commit_state(pgsql):
    def inner(order_id, state):
        pgsql['cargo_orders'].cursor().execute(
            'UPDATE cargo_orders.orders SET commit_state = '
            + f'\'{state}\' WHERE order_id = \'{order_id}\'',
        )

    return inner


@pytest.mark.parametrize('state', ['draft', 'failed'])
async def test_retrieve_order_error(
        taxi_cargo_orders,
        stq,
        stq_runner,
        my_waybill_info,
        default_order_id,
        __change_order_commit_state,
        state: str,
):
    __change_order_commit_state(default_order_id, state)
    await stq_runner.cargo_taxi_order_performer_assigning.call(
        task_id='test_stq',
        kwargs=build_kwargs(default_order_id),
        expect_fail=False,
    )

    assert not stq.cargo_taxi_order_performer_assigning.has_calls
