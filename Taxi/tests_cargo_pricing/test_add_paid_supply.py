async def _call_add_paid_supply(
        v1_calc_creator,
        v2_add_paid_supply,
        conf_exp3_yt_calcs_logging_enabled,
        yt_logging_enabled,
):
    await conf_exp3_yt_calcs_logging_enabled(enabled=False)
    calc_response = await v1_calc_creator.execute()
    assert calc_response.status_code == 200

    first_calc_id = calc_response.json()['calc_id']
    v2_add_paid_supply.add_calc(calc_id=first_calc_id)

    await conf_exp3_yt_calcs_logging_enabled(enabled=yt_logging_enabled)
    response = await v2_add_paid_supply.execute()
    return response


async def test_add_paid_supply_yt_calcs_logger(
        v1_calc_creator,
        v2_add_paid_supply,
        conf_exp3_yt_calcs_logging_enabled,
        yt_calcs_logger_testpoint,
):
    response = await _call_add_paid_supply(
        v1_calc_creator,
        v2_add_paid_supply,
        conf_exp3_yt_calcs_logging_enabled,
        yt_logging_enabled=True,
    )
    assert response.status_code == 200
    resp = response.json()

    assert len(yt_calcs_logger_testpoint.messages) == 1
    msg = yt_calcs_logger_testpoint.messages[0]
    assert msg['calc_id'] == resp['calculations'][0]['calc_id']
    assert msg['log_place'] == 'v2_add_paid_supply'


async def test_add_paid_supply_yt_calcs_logger_disabled(
        v1_calc_creator,
        v2_add_paid_supply,
        conf_exp3_yt_calcs_logging_enabled,
        yt_calcs_logger_testpoint,
):
    response = await _call_add_paid_supply(
        v1_calc_creator,
        v2_add_paid_supply,
        conf_exp3_yt_calcs_logging_enabled,
        yt_logging_enabled=False,
    )
    assert response.status_code == 200

    assert yt_calcs_logger_testpoint.messages == []


async def test_add_paid_supply_yt_calcs_logger_exp_kwargs(
        v1_calc_creator,
        v2_add_paid_supply,
        conf_exp3_yt_calcs_logging_enabled,
        experiments3,
):
    exp3_recorder = experiments3.record_match_tries(
        'cargo_pricing_yt_calcs_logging',
    )

    response = await _call_add_paid_supply(
        v1_calc_creator,
        v2_add_paid_supply,
        conf_exp3_yt_calcs_logging_enabled,
        yt_logging_enabled=True,
    )
    assert response.status_code == 200

    # first time for v1/taxi/calc
    tries = await exp3_recorder.get_match_tries(ensure_ntries=2)
    kwargs = tries[1].kwargs
    assert kwargs['consumer'] == 'cargo-pricing/yt_calcs_logging'
    assert kwargs['corp_client_id'] == 'corp_client_id'
    assert kwargs['homezone'] == 'moscow'
    assert kwargs['log_place'] == 'v2_add_paid_supply'
    assert kwargs['price_for'] == 'client'
    assert kwargs['source'] == 'unknown'
    assert kwargs['tariff_class'] == 'cargocorp'
    assert kwargs['request_timestamp']
