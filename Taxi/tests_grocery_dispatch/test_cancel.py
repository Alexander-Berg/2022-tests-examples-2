# pylint: disable=import-only-modules
import pytest

from tests_grocery_dispatch import configs
from tests_grocery_dispatch.constants import CLAIM_ID
DISPATCH_TYPE = 'cargo_sync'

NOW = '2020-10-05T16:28:00.000Z'
DELIVERY_ETA_TS = '2020-10-05T16:38:00.000Z'


@pytest.mark.now(NOW)
async def test_basic_cancel_200(
        taxi_grocery_dispatch,
        mockserver,
        mocked_time,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_dispatch_pg,
        cargo_pg,
):

    cargo.add_performer(
        claim_id=CLAIM_ID,
        eats_profile_id='123_123',
        driver_id='123',
        park_id='123',
    )

    dispatch_info = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE, status='scheduled',
    )
    cargo_model = cargo_pg.create_claim(
        dispatch_id=dispatch_info.dispatch_id,
        claim_id=CLAIM_ID,
        claim_version=123,
        auth_token_key='b2b-taxi-auth-grocery-fra',
    )
    cargo.set_data(
        items=cargo.convert_items(dispatch_info.order.items),
        delivered_eta_ts=DELIVERY_ETA_TS,
        version=123,
    )

    cargo.check_authorization(authorization='Bearer CCC123')

    json = {'dispatch_id': dispatch_info.dispatch_id, 'cancel_type': 'paid'}

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/cancel',
    )
    def _mock_cancel(request):
        version = request.json['version']
        assert version == 123

        auth_token_key = request.headers['Authorization']
        assert auth_token_key == 'Bearer CCC123'

        return {
            'id': request.args['claim_id'],
            'status': 'cancelled',
            'version': version,
        }

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/cancel', json,
    )
    assert response.status_code == 200
    assert _mock_cancel.times_called == 1

    assert cargo_model.claim_version == 123


@pytest.mark.now(NOW)
@pytest.mark.experiments3(
    name='grocery_dispatch_cargo_general',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'use_cancel_info': True, 'optional_return': False},
        },
    ],
    is_config=True,
)
async def test_cancel_check_cancel_state(
        taxi_grocery_dispatch,
        mockserver,
        mocked_time,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_dispatch_pg,
        cargo_pg,
):

    cargo.add_performer(
        claim_id=CLAIM_ID,
        eats_profile_id='123_123',
        driver_id='123',
        park_id='123',
    )

    dispatch_info = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE, status='scheduled',
    )
    cargo_model = cargo_pg.create_claim(
        dispatch_id=dispatch_info.dispatch_id,
        claim_id=CLAIM_ID,
        status_updated=NOW,
        claim_version=123,
    )
    cargo.set_data(
        items=cargo.convert_items(dispatch_info.order.items),
        delivered_eta_ts=DELIVERY_ETA_TS,
        version=123,
    )

    json = {'dispatch_id': dispatch_info.dispatch_id, 'cancel_type': 'paid'}

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v2/claims/cancel-info',
    )
    def _mock_cancel_info(request):
        claim_id = request.args['claim_id']
        assert claim_id == CLAIM_ID
        return {'cancel_state': 'free'}

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/cancel',
    )
    def _mock_cancel(request):
        version = request.json['version']
        assert version == 123

        return {
            'id': request.args['claim_id'],
            'status': 'cancelled',
            'version': version,
        }

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/cancel', json,
    )
    assert response.status_code == 200
    assert _mock_cancel_info.times_called == 1
    assert _mock_cancel.times_called == 1

    assert cargo_model.claim_version == 123


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    ['cargo_status'],
    [
        ['failed'],
        ['cancelled_by_taxi'],
        ['returning'],
        ['performer_not_found'],
        ['return_arrived'],
        ['ready_for_return_confirmation'],
        ['returned'],
        ['returned_finish'],
    ],
)
async def test_cancel_returns_correct_failure_reason_type(
        taxi_grocery_dispatch,
        mockserver,
        cargo,
        cargo_status,
        grocery_dispatch_pg,
        cargo_pg,
):
    cargo.add_performer(  # TODO default values
        claim_id=CLAIM_ID,
        eats_profile_id='123_123',
        driver_id='123',
        park_id='123',
    )

    dispatch_info = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE, status='scheduled',
    )
    cargo_model = cargo_pg.create_claim(  # TODO default values
        dispatch_id=dispatch_info.dispatch_id,
        claim_id=CLAIM_ID,
        claim_version=123,
    )
    cargo.set_data(
        items=cargo.convert_items(dispatch_info.order.items),
        delivered_eta_ts=DELIVERY_ETA_TS,
        version=123,
        status=cargo_status,
    )

    json = {'dispatch_id': dispatch_info.dispatch_id, 'cancel_type': 'paid'}

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/cancel',
    )
    def _mock_cancel(request):
        pass

    await taxi_grocery_dispatch.post('/internal/dispatch/v1/cancel', json)
    # Если cargo отвечает что-то отличное от cancelled, cancelled_with_payment,
    # cancelled_with_items_on_hands (DispatchStatus::Canceled,
    # DispatchStatus::Canceling),
    # вернется 409
    # [fmatantsev] уже так не работает LAVKALOGDEV-309
    # assert response.status_code == 409
    #
    assert _mock_cancel.times_called == 0
    assert cargo_model.claim_version == 123

    # Дальше проверяем, что в таблице в failure_reason_type
    # записалось то, что нужно
    assert dispatch_info.failure_reason_type == cargo_status


@configs.DISPATCH_GENERAL_CONFIG
@pytest.mark.parametrize('need_return_items', [False, True])
@pytest.mark.now(NOW)
async def test_cancel_with_return(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        mocked_time,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_dispatch_pg,
        cargo_pg,
        need_return_items,
):
    cargo.add_performer(
        claim_id=CLAIM_ID,
        eats_profile_id='123_123',
        driver_id='123',
        park_id='123',
    )

    dispatch_info = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE, status='scheduled',
    )
    cargo_pg.create_claim(
        dispatch_id=dispatch_info.dispatch_id,
        claim_id=CLAIM_ID,
        claim_version=123,
        claim_status='pickuped',
    )
    cargo.set_data(
        items=cargo.convert_items(dispatch_info.order.items),
        delivered_eta_ts=DELIVERY_ETA_TS,
        version=123,
        status='pickuped',
    )

    if not need_return_items:
        experiments3.add_config(
            name='grocery_dispatch_cargo_return',
            consumers=['grocery_dispatch/dispatch'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'need_return_items': False},
                },
            ],
        )

    json = {'dispatch_id': dispatch_info.dispatch_id, 'cancel_type': 'paid'}

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/return',
    )
    def _mock_return(request):
        assert request.json['point_id'] == cargo.route_points[0].point_id
        assert request.args['claim_id'] == CLAIM_ID
        assert need_return_items == request.json['need_return_items']

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/cancel', json,
    )
    assert response.status_code == 200
    assert _mock_return.times_called == 1


@configs.DISPATCH_GENERAL_CONFIG
@pytest.mark.now(NOW)
async def test_cancel_twice(
        taxi_grocery_dispatch,
        mockserver,
        cargo,
        grocery_dispatch_pg,
        cargo_pg,
):
    cargo.add_performer(
        claim_id=CLAIM_ID,
        eats_profile_id='123_123',
        driver_id='123',
        park_id='123',
    )

    dispatch_info = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE, status='scheduled',
    )
    cargo_pg.create_claim(
        dispatch_id=dispatch_info.dispatch_id,
        claim_id=CLAIM_ID,
        claim_version=123,
        claim_status='pickuped',
    )
    cargo.set_data(
        items=cargo.convert_items(dispatch_info.order.items),
        delivered_eta_ts=DELIVERY_ETA_TS,
        version=123,
        status='pickuped',
    )

    json = {'dispatch_id': dispatch_info.dispatch_id, 'cancel_type': 'paid'}

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/return',
    )
    def _mock_return(request):
        assert request.json['point_id'] == cargo.route_points[0].point_id
        assert request.args['claim_id'] == CLAIM_ID

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/cancel', json,
    )
    assert response.status_code == 200
    assert _mock_return.times_called == 1

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/cancel', json,
    )

    assert response.status_code == 200
    assert _mock_return.times_called == 1


@configs.DISPATCH_GENERAL_CONFIG
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    ['status', 'resp_code'],
    [('delivered', 409), ('canceled', 200), ('revoked', 200)],
)
async def test_cancel_after_finish_state(
        taxi_grocery_dispatch, cargo, grocery_dispatch_pg, status, resp_code,
):

    dispatch_info = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE, status=status,
    )

    json = {'dispatch_id': dispatch_info.dispatch_id, 'cancel_type': 'paid'}

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/cancel', json,
    )
    assert cargo.times_cancel_called() == 0
    assert cargo.times_return_called() == 0
    assert response.status_code == resp_code


@pytest.mark.now(NOW)
async def test_cancel_cargo_409(
        taxi_grocery_dispatch,
        mockserver,
        cargo,
        grocery_dispatch_pg,
        cargo_pg,
):

    cargo.add_performer(
        claim_id=CLAIM_ID,
        eats_profile_id='123_123',
        driver_id='123',
        park_id='123',
    )

    dispatch_info = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE, status='scheduled',
    )
    cargo_pg.create_claim(
        dispatch_id=dispatch_info.dispatch_id,
        claim_id=CLAIM_ID,
        claim_version=123,
    )
    cargo.set_data(
        items=cargo.convert_items(dispatch_info.order.items),
        delivered_eta_ts=DELIVERY_ETA_TS,
        version=123,
    )

    json = {'dispatch_id': dispatch_info.dispatch_id, 'cancel_type': 'paid'}

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/cancel',
    )
    def _mock_cancel(request):
        return mockserver.make_response(
            status=409, json={'code': 'cancel_error', 'message': 'test'},
        )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/cancel', json,
    )
    assert response.status_code == 409
    assert _mock_cancel.times_called == 1
