async def test_c2c_taxi_requirements(
        taxi_cargo_claims,
        create_default_cargo_c2c_order,
        create_segment_for_claim,
        get_db_segment_ids,
        mock_create_event,
):
    mock_create_event()
    claim_info = await create_default_cargo_c2c_order(cargo=True)

    created_segments = (
        await create_segment_for_claim(claim_info.claim_id)
    ).json()['created_segments']
    assert len(created_segments) == 1
    segment_id = created_segments[0]['segment_id']

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200
    segment = response.json()
    assert segment['performer_requirements'] == {
        'claim_taxi_requirements_num': 2,
        'claim_taxi_requirements_str': 'taxi_req',
        'claim_taxi_requirements_bool': True,
        'cargo_type': 'lcv_m',
        'cargo_loaders': 2,
        'door_to_door': True,
        'thermobag_covid': True,
        'taxi_classes': ['cargo'],
        'special_requirements': {
            'virtual_tariffs': [
                {
                    'class': 'express',
                    'special_requirements': [{'id': 'food_delivery'}],
                },
                {
                    'class': 'cargo',
                    'special_requirements': [{'id': 'cargo_etn'}],
                },
            ],
        },
    }
