import copy

import pytest

from .. import utils_v2


# TODO(umed): fix as part of https://st.yandex-team.ru/CARGODEV-10906
@pytest.mark.parametrize(
    'claim_status, is_phoenix_claim',
    (
        # ('cancelled_with_items_on_hands', True),
        ('cancelled_by_taxi', True),
        # ('cancelled_with_payment', True),
        ('cancelled', True),
        ('returned_finish', True),
        ('delivered_finish', True),
        ('performer_not_found', True),
        ('pickup_arrived', True),
        ('failed', True),
        # ('cancelled_with_items_on_hands', False),
        ('cancelled_by_taxi', False),
        # ('cancelled_with_payment', False),
        ('cancelled', False),
        ('returned_finish', False),
        ('delivered_finish', False),
        ('performer_not_found', False),
        ('failed', False),
    ),
)
@pytest.mark.config(
    CARGO_CLAIMS_CORP_CLIENTS_FEATURES={'__default__': ['phoenix_claim']},
)
async def test_phoenix_events(
        state_controller,
        pgsql,
        get_create_request_v2,
        procaas_send_settings,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        claim_status,
        is_phoenix_claim,
        mock_cargo_corp_up,
):
    await procaas_send_settings()
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()

    if claim_status == 'cancelled_with_items_on_hands':
        state_controller.use_create_version('v2')
        state_controller.handlers().create.request = (
            utils_v2.get_create_request()
        )
        state_controller.handlers().create.request['optional_return'] = True
        if is_phoenix_claim:
            state_controller.handlers().create.request['features'] = [
                {'id': 'phoenix_claim'},
            ]
        await state_controller.apply(
            target_status=claim_status, next_point_order=2,
        )

    else:
        create_request = copy.deepcopy(get_create_request_v2())
        if is_phoenix_claim:
            create_request['features'] = [{'id': 'phoenix_claim'}]
        state_controller.use_create_version('v2')
        state_controller.handlers().create.request = create_request
        claim_info = await state_controller.apply(target_status=claim_status)
        if is_phoenix_claim:
            assert claim_info.claim_full_response['features'] == [
                {'id': 'phoenix_claim'},
            ]
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        'SELECT payload FROM cargo_claims.processing_events '
        'WHERE payload->>\'status\' = \'{}\';'.format(claim_status),
    )
    result = cursor.fetchall()[0][0]
    assert result['data']['phoenix_claim'] == is_phoenix_claim


@pytest.mark.config(
    CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
        'enabled': True,
        'sleep_ms': 50,
        'new_event_chunk_size': 2,
    },
)
@pytest.mark.parametrize(
    'claim_status, is_corp_present',
    (
        ('cancelled_by_taxi', True),
        ('returned_finish', True),
        ('delivered_finish', True),
        ('performer_not_found', True),
        ('pickup_arrived', False),
        ('failed', True),
    ),
)
async def test_c2c_phoenix_events(
        state_controller,
        pgsql,
        get_default_corp_client_id,
        procaas_send_settings,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        mock_cargo_corp_up,
        claim_status,
        is_corp_present,
):
    await procaas_send_settings()
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()

    state_controller.use_create_version('v2_cargo_c2c')
    state_controller.set_options(is_phoenix=True)
    claim_info = await state_controller.apply(target_status=claim_status)
    claim_features = set(
        feature['id'] for feature in claim_info.claim_full_response['features']
    )
    assert 'phoenix_claim' in claim_features

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        'SELECT payload FROM cargo_claims.processing_events '
        'WHERE payload->>\'status\' = \'{}\';'.format(claim_status),
    )
    result = cursor.fetchall()[0][0]
    assert result['data']['phoenix_claim'] is True
    if is_corp_present:
        assert result['data']['corp_client_id'] == get_default_corp_client_id
    assert result['data']['claim_origin'] == 'yandexgo'
    assert result['data']['skip_client_notify'] is False
