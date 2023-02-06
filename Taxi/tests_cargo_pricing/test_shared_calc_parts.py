import copy

from tests_cargo_pricing import utils


async def test_v1_calc_v1_retrieve_with_shared_calc_parts(
        v1_calc_creator, v1_retrieve_calc, config_shared_calc_parts,
):
    calc_response = await v1_calc_creator.execute()
    assert calc_response.status_code == 200
    calc_resp = calc_response.json()

    retrieve_response = await v1_retrieve_calc(calc_resp['calc_id'])
    assert retrieve_response.status_code == 200
    retrieve_resp = retrieve_response.json()

    assert (
        calc_resp['taxi_pricing_response']
        == retrieve_resp['taxi_pricing_response']
        == v1_calc_creator.mock_prepare.categories['cargocorp']
    )


async def test_recalc_with_shared_calc_parts_retrieve_response(
        v1_calc_creator, v1_retrieve_calc, config_shared_calc_parts,
):
    calc1_response = await v1_calc_creator.execute()
    assert calc1_response.status_code == 200

    calc2_response = await utils.calc_with_previous_calc_id(
        v1_calc_creator, prev_calc_id=calc1_response.json()['calc_id'],
    )
    assert calc2_response.status_code == 200
    calc2_resp = calc2_response.json()

    retrieve_response = await v1_retrieve_calc(calc2_resp['calc_id'])
    assert retrieve_response.status_code == 200
    retrieve_resp = retrieve_response.json()

    assert (
        calc2_resp['taxi_pricing_response']
        == retrieve_resp['taxi_pricing_response']
        == v1_calc_creator.mock_prepare.categories['cargocorp']
    )


async def test_recalc_with_shared_calc_parts_v2_recalc_request(
        v1_calc_creator, config_shared_calc_parts,
):
    first_response = await v1_calc_creator.execute()
    assert first_response.status_code == 200
    recalc_request_1 = copy.deepcopy(v1_calc_creator.mock_recalc.request)

    second_response = await utils.calc_with_previous_calc_id(
        v1_calc_creator, prev_calc_id=first_response.json()['calc_id'],
    )
    assert second_response.status_code == 200

    assert recalc_request_1 == v1_calc_creator.mock_recalc.request


async def test_calc_with_shared_calc_parts_same_field_twice_1(
        v1_calc_creator, v1_retrieve_calc, lazy_config_shared_calc_parts,
):
    await lazy_config_shared_calc_parts(
        shared_fields=[
            {
                'field': 'prepared_category',
                'sub_fields': [
                    'driver.modifications',
                    'user.data.tariff.requirement_prices',
                ],
            },
            {
                'field': 'prepared_category',
                'sub_fields': [
                    'driver.modifications',
                    'user.data.tariff.requirement_prices.door_to_door',
                ],
            },
        ],
    )

    calc_response = await v1_calc_creator.execute()
    assert calc_response.status_code == 200
    calc_resp = calc_response.json()

    retrieve_response = await v1_retrieve_calc(calc_resp['calc_id'])
    assert retrieve_response.status_code == 200
    retrieve_resp = retrieve_response.json()

    assert (
        calc_resp['taxi_pricing_response']
        == retrieve_resp['taxi_pricing_response']
        == v1_calc_creator.mock_prepare.categories['cargocorp']
    )


async def test_recalc_with_shared_calc_parts_same_field_twice_2(
        v1_calc_creator, v1_retrieve_calc, lazy_config_shared_calc_parts,
):
    await lazy_config_shared_calc_parts(
        shared_fields=[
            {
                'field': 'prepared_category',
                'sub_fields': [
                    'driver.modifications',
                    'user.data.tariff.requirement_prices.door_to_door',
                ],
            },
            {
                'field': 'prepared_category',
                'sub_fields': [
                    'driver.modifications',
                    'user.data.tariff.requirement_prices',
                ],
            },
        ],
    )

    calc_response = await v1_calc_creator.execute()
    assert calc_response.status_code == 200
    calc_resp = calc_response.json()

    retrieve_response = await v1_retrieve_calc(calc_resp['calc_id'])
    assert retrieve_response.status_code == 200
    retrieve_resp = retrieve_response.json()

    assert (
        calc_resp['taxi_pricing_response']
        == retrieve_resp['taxi_pricing_response']
        == v1_calc_creator.mock_prepare.categories['cargocorp']
    )


async def test_bulk_retrieve_calc_with_shared_calc_parts(
        v1_calc_creator, v2_retrieve_calc, config_shared_calc_parts,
):
    calc_response = await v1_calc_creator.execute()
    assert calc_response.status_code == 200
    calc = calc_response.json()

    retrieve_response = await v2_retrieve_calc([calc['calc_id']])
    assert retrieve_response.status_code == 200

    retrieve_calc = retrieve_response.json()['calculations'][0]['result']
    assert (
        retrieve_calc['diagnostics']['taxi_pricing_response']
        == calc['taxi_pricing_response']
        == v1_calc_creator.mock_prepare.categories['cargocorp']
    )


def _sorted_by_id_calcs(repsonse):
    return sorted(
        repsonse.json()['calculations'], key=lambda calc: calc['calc_id'],
    )


async def test_two_calcs_with_differ_shared_calc_parts(
        v2_calc_creator, v2_retrieve_calc, config_shared_calc_parts,
):
    utils.add_category_to_request(v2_calc_creator)
    calc_response = await v2_calc_creator.execute()
    assert calc_response.status_code == 200
    resp_calcs = _sorted_by_id_calcs(calc_response)
    calc_count = 2
    assert len(resp_calcs) == calc_count

    retrieve_response = await v2_retrieve_calc(
        [resp_calcs[0]['calc_id'], resp_calcs[1]['calc_id']],
    )
    assert retrieve_response.status_code == 200
    retrieve_calcs = _sorted_by_id_calcs(retrieve_response)
    assert len(retrieve_calcs) == calc_count
    for i in range(calc_count):
        assert (
            retrieve_calcs[i]['result']['diagnostics']['taxi_pricing_response']
            == resp_calcs[i]['result']['diagnostics']['taxi_pricing_response']
        )


async def test_two_calcs_with_same_shared_calc_parts(
        v2_calc_creator, v2_retrieve_calc, lazy_config_shared_calc_parts,
):
    await lazy_config_shared_calc_parts(
        shared_fields=[
            {
                'field': 'prepared_category',
                'sub_fields': ['driver.additional_prices'],
            },
        ],
    )
    utils.add_category_to_request(v2_calc_creator)
    calc_response = await v2_calc_creator.execute()
    assert calc_response.status_code == 200
    resp_calcs = _sorted_by_id_calcs(calc_response)
    calc_count = 2
    assert len(resp_calcs) == calc_count

    retrieve_response = await v2_retrieve_calc(
        [resp_calcs[0]['calc_id'], resp_calcs[1]['calc_id']],
    )
    assert retrieve_response.status_code == 200
    retrieve_calcs = _sorted_by_id_calcs(retrieve_response)
    assert len(retrieve_calcs) == calc_count
    for i in range(2):
        assert (
            retrieve_calcs[i]['result']['diagnostics']['taxi_pricing_response']
            == resp_calcs[i]['result']['diagnostics']['taxi_pricing_response']
        )


async def test_add_paid_supply_with_shared_calc_parts(
        v1_calc_creator,
        v2_add_paid_supply,
        v1_retrieve_calc,
        config_shared_calc_parts,
):
    calc_response = await v1_calc_creator.execute()
    assert calc_response.status_code == 200

    calc_id = calc_response.json()['calc_id']
    v2_add_paid_supply.add_calc(calc_id=calc_id)
    add_paid_supply_response = await v2_add_paid_supply.execute()
    assert add_paid_supply_response.status_code == 200
    add_paid_supply_resp = add_paid_supply_response.json()

    retrieve_response = await v1_retrieve_calc(calc_id)
    assert retrieve_response.status_code == 200
    retrieve_resp = retrieve_response.json()

    assert (
        add_paid_supply_resp['calculations'][0]['result']['diagnostics'][
            'taxi_pricing_response'
        ]
        == retrieve_resp['taxi_pricing_response']
    )
