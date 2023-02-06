import copy

from tests_cargo_pricing import utils


async def test_calc_yt_calcs_logger(
        v1_calc_creator,
        conf_exp3_yt_calcs_logging_enabled,
        yt_calcs_logger_testpoint,
):
    await conf_exp3_yt_calcs_logging_enabled(enabled=True)
    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    resp = response.json()

    assert len(yt_calcs_logger_testpoint.messages) == 1
    msg = yt_calcs_logger_testpoint.messages[0]
    assert msg['calc_id'] == resp['calc_id']
    assert msg['details'] == resp['details']
    assert msg['log_place'] == 'v1_taxi_calc'
    assert msg['price'] == 3000000
    expected_recalc_resp = copy.deepcopy(
        v1_calc_creator.mock_recalc.response['price'],
    )
    expected_recalc_resp['driver']['additional_payloads'].pop('route_parts')
    expected_recalc_resp['user']['additional_payloads'].pop('route_parts')
    assert msg['recalc_response'] == expected_recalc_resp
    assert msg['request'] == v1_calc_creator.payload
    assert (
        msg['prepared_category']
        == v1_calc_creator.mock_prepare.categories['cargocorp']
    )


async def test_calc_yt_calcs_logger_disabled(
        v1_calc_creator,
        conf_exp3_yt_calcs_logging_enabled,
        yt_calcs_logger_testpoint,
):
    await conf_exp3_yt_calcs_logging_enabled(enabled=False)
    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    assert yt_calcs_logger_testpoint.messages == []


async def test_calc_yt_calcs_logger_exp_kwargs(
        v1_calc_creator, conf_exp3_yt_calcs_logging_enabled, experiments3,
):
    exp3_recorder = experiments3.record_match_tries(
        'cargo_pricing_yt_calcs_logging',
    )

    await conf_exp3_yt_calcs_logging_enabled(enabled=True)
    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    kwargs = tries[0].kwargs
    assert kwargs['consumer'] == 'cargo-pricing/yt_calcs_logging'
    assert kwargs['corp_client_id'] == 'corp_client_id'
    assert kwargs['homezone'] == 'moscow'
    assert kwargs['log_place'] == 'v1_taxi_calc'
    assert kwargs['price_for'] == 'client'
    assert kwargs['source'] == 'unknown'
    assert kwargs['tariff_class'] == 'cargocorp'
    assert kwargs['request_timestamp']


async def test_calc_yt_calcs_logger_no_log_on_retry(
        v1_calc_creator,
        conf_exp3_yt_calcs_logging_enabled,
        yt_calcs_logger_testpoint,
):
    await conf_exp3_yt_calcs_logging_enabled(enabled=True)

    v1_calc_creator.payload = utils.get_default_calc_request()
    v1_calc_creator.payload['idempotency_token'] = 'idempotency_token_1'
    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert len(yt_calcs_logger_testpoint.messages) == 1

    v1_calc_creator.payload = utils.get_default_calc_request()
    v1_calc_creator.payload['idempotency_token'] = 'idempotency_token_1'
    second_response = await v1_calc_creator.execute()
    assert second_response.status_code == 200
    assert len(yt_calcs_logger_testpoint.messages) == 1
