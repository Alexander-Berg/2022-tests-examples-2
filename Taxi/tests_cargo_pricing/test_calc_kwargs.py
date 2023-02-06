async def test_calc_origin_uri_kwargs(
        v1_calc_creator, setup_pricing_class_substitution, experiments3,
):
    v1_calc_creator.payload[
        'origin_uri'
    ] = 'cargo-orders/driver/v1/cargo-claims/v1/cargo/calc-cash'
    exp3_recorder = experiments3.record_match_tries(
        'cargo_pricing_class_substitution',
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    kwargs = tries[0].kwargs
    assert (
        kwargs['request_origin_uri']
        == 'cargo-orders/driver/v1/cargo-claims/v1/cargo/calc-cash'
    )


async def test_calc_driver_tags_kwargs(
        v1_calc_creator,
        setup_pricing_class_substitution,
        experiments3,
        v1_drivers_match_profile,
):
    v1_calc_creator.payload['performer'] = {
        'driver_id': 'uuid0',
        'park_db_id': 'dbid0',
    }

    exp3_recorder = experiments3.record_match_tries(
        'cargo_pricing_class_substitution',
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    kwargs = tries[0].kwargs
    assert kwargs['consumer'] == 'cargo-pricing/v1/taxi/calc'
    assert kwargs['driver_tags'] == ['driver_fix_bad_guy']


async def test_calc_special_requirements_kwargs(
        v1_calc_creator, setup_pricing_class_substitution, experiments3,
):
    v1_calc_creator.payload['special_requirements'] = [
        'spec_req1',
        'spec_req2',
    ]
    exp3_recorder = experiments3.record_match_tries(
        'cargo_pricing_class_substitution',
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    kwargs = tries[0].kwargs
    assert sorted(kwargs['special_requirements']) == ['spec_req1', 'spec_req2']


async def test_calc_country_kwargs(
        v1_calc_creator, setup_pricing_class_substitution, experiments3,
):
    exp3_recorder = experiments3.record_match_tries(
        'cargo_pricing_class_substitution',
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    kwargs = tries[0].kwargs
    assert kwargs['country'] == 'rus'
