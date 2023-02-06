from testsuite.utils import matching


async def test_save_special_requirements(
        create_claim_for_segment,
        create_segment_for_claim,
        mock_virtual_tariffs,
        get_db_segment_ids,
        get_segment,
        get_default_corp_client_id,
):
    claim_info = await create_claim_for_segment()
    response = (await create_segment_for_claim(claim_info.claim_id)).json()

    segment = await get_segment(response['created_segments'][0]['segment_id'])
    assert segment['performer_requirements']['special_requirements'] == {
        'virtual_tariffs': [
            {
                'class': 'express',
                'special_requirements': [{'id': 'food_delivery'}],
            },
            {'class': 'cargo', 'special_requirements': [{'id': 'cargo_etn'}]},
        ],
    }

    assert (await mock_virtual_tariffs.wait_call())['request'].json == {
        'corp_client_id': get_default_corp_client_id,
        'zone_id': 'moscow',
        'classes': [{'id': 'cargo'}, {'id': 'courier'}, {'id': 'express'}],
        'cargo_ref_id': matching.AnyString(),
    }
