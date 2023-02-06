import pytest


@pytest.mark.geo_nodes(filename='geonodes.json')
async def test_courier_data_updater(
        stq_runner,
        taxi_eats_performer_subventions,
        db_select_orders,
        mockserver,
        make_order,
):
    order_nr = 'order-nr'
    order_status = 'created'
    claim_id = 'claim-id'
    corp_client_alias = 'default'
    attempt = 1

    make_order(
        eats_id=order_nr,
        order_status=order_status,
        claim_id=claim_id,
        claim_attempt=attempt,
        corp_client_type=corp_client_alias,
    )

    eats_profile_id = 'eats-profile-id'
    park_id = 'park-id'
    driver_id = 'driver-id'
    zone_id = 'moscow'
    oebs_mvp_id = 'oebs-mvp-id'
    taxi_alias_id = 'taxi-alias-id'

    @mockserver.json_handler('/cargo-claims/internal/external-performer')
    def _mock_cargo_claims(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            json={
                'eats_profile_id': eats_profile_id,
                'name': 'Winston Churchill',
                'first_name': 'Winston',
                'legal_name': 'Sir Winston Leonard Spencer Churchill',
                'transport_type': 'Car',
                'driver_id': driver_id,
                'park_id': park_id,
                'taxi_alias_id': taxi_alias_id,
                'zone_id': zone_id,
            },
            status=200,
        )

    @mockserver.json_handler(
        '/taxi-agglomerations/v1/geo_nodes/get_mvp_oebs_id',
    )
    def _mock_agglomerations(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            json={'oebs_mvp_id': oebs_mvp_id}, status=200,
        )

    await taxi_eats_performer_subventions.run_task('update-courier-data-task')

    assert _mock_cargo_claims.times_called == 1
    assert _mock_agglomerations.times_called == 1

    order = db_select_orders()[0]
    assert order['eats_id'] == order_nr
    assert order['claim_id'] == claim_id
    assert order['eats_profile_id'] == eats_profile_id
    assert order['driver_id'] == driver_id
    assert order['park_id'] == park_id
    assert order['zone_name'] == zone_id
    assert order['geo_hierarchy'] == 'br_root/br_moscow_adm/' + zone_id
    assert order['oebs_mvp_id'] == oebs_mvp_id
    assert order['taxi_alias_id'] == taxi_alias_id
