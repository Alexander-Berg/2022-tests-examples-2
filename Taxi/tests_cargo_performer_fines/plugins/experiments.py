import pytest


@pytest.fixture(name='exp3_performer_cancel_determine_guilty')
async def _exp3_performer_cancel_determine_guilty(
        experiments3, taxi_cargo_performer_fines,
):
    async def call(guilty=True):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_performer_fines_performer_'
            'cancellations_determine_guilty',
            consumers=['cargo-performer-fines/performer-cancellations'],
            clauses=[],
            default_value={
                'alert_title_tanker_key': 'performer_cancel_title',
                'alert_message_tanker_key': 'performer_cancel_message',
                'alert_message_tanker_args': {
                    'key1': 'value1',
                    'key2': 'value2',
                },
                'guilty': guilty,
            },
        )
        await taxi_cargo_performer_fines.invalidate_caches()

    return call


@pytest.fixture(name='exp3_performer_cancel_limits')
async def _exp3_performer_cancel_limits(
        experiments3, taxi_cargo_performer_fines,
):
    async def call(required_completed_orders=30):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_performer_fines_performer_cancellations_limits',
            consumers=['cargo-performer-fines/performer-cancellations-lite'],
            clauses=[],
            default_value={
                'free_cancellation_limit': 1,
                'required_completed_orders_to_reset_cancellation_limit': (
                    required_completed_orders
                ),
                'title_tanker_key': 'performer_cancel_limit_title',
                'subtitle_tanker_key': 'performer_cancel_limit_subtitle',
                'detail_tanker_key': 'performer_cancel_limit_detail',
                'right_icon_payload': {
                    'text_tanker_key': 'performer_cancel_limit_right_icon',
                },
            },
        )
        await taxi_cargo_performer_fines.invalidate_caches()

    return call
