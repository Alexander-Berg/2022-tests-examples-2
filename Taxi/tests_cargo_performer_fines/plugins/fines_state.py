import pytest


@pytest.fixture(name='mock_fines_state')
def _mock_fines_state(
        mockserver,
        default_operation_id,
        default_taxi_order_id,
        default_taxi_alias_id,
        default_fine_unique_key,
        default_fine_code,
        default_ticket,
        performer_fines_api_key,
):
    def handler(
            taxi_order_id=default_taxi_order_id,
            driver_id=None,
            park_id=None,
            fine_code=None,
    ):
        @mockserver.json_handler(
            '/cargo-finance-via-abk/admin/cargo-finance/performer/fines/state',
        )
        def _mock(request):
            assert request.headers['Authorization'] == performer_fines_api_key
            assert request.query['taxi_order_id'] == taxi_order_id
            if driver_id:
                assert request.query['driver_uuid'] == driver_id
            if park_id:
                assert request.query['park_id'] == park_id
            decisions = [
                {
                    'created_at': '2020-02-25T06:00:00+03:00',
                    'resolved_at': '2020-02-25T06:10:00+03:00',
                    'operation_id': default_operation_id,
                    'revision': 2,
                    'decision': {
                        'park_id': park_id,
                        'driver_uuid': driver_id,
                        'taxi_alias_id': default_taxi_alias_id,
                        'fine_unique_key': default_fine_unique_key,
                    },
                    'operator': {
                        'yandex_uid': '2222',
                        'yandex_login': 'operator_login',
                    },
                    'reason': {'st_ticket': default_ticket},
                },
            ]
            if fine_code:
                decisions[0]['decision']['fine_code'] = fine_code

            return mockserver.make_response(
                json={'decisions': decisions, 'pending_decisions': []},
                status=200,
            )

    return handler


@pytest.fixture(name='exp3_driver_simple_push_settings')
async def _exp3_driver_push_settings(taxi_cargo_performer_fines, experiments3):
    experiments3.add_config(
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        name='cargo_performer_fines_driver_push_settings',
        consumers=['cargo-performer-fines/decision'],
        clauses=[],
        default_value={
            'ignore_any_push': False,
            'enable_custom_push': False,
            'delay_after_decision_resolved': 0,
        },
    )
    await taxi_cargo_performer_fines.invalidate_caches()


@pytest.fixture(name='setup_order_fines_codes')
async def _setup_order_fines_codes(
        taxi_cargo_performer_fines, taxi_config, default_fine_code,
):
    taxi_config.set(
        ORDER_FINES_CODES=[
            {
                'description': 'first fine description',
                'disabled': False,
                'fine_code': default_fine_code,
                'title': 'first fine title',
                'driver_notification_params': {
                    'tanker_keyset': 'notify',
                    'fine_assigned_tanker_key': (
                        'cargo_performer_fines.'
                        'driver_pushes.assigned_default_fine'
                    ),
                },
            },
        ],
    )
    await taxi_cargo_performer_fines.invalidate_caches()
