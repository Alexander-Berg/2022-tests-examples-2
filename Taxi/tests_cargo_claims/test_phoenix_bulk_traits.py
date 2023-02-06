import pytest


@pytest.mark.usefixtures('yt_apply')
@pytest.mark.parametrize(
    'url, is_phoenix',
    [
        ('v2/admin/phoenix/bulk-traits', True),
        ('v2/admin/phoenix/bulk-traits', False),
        ('v2/claims/phoenix/bulk-traits', True),
        ('v2/claims/phoenix/bulk-traits', False),
    ],
)
async def test_positive_get_bulk_traits_with_phoenix(
        taxi_cargo_claims,
        get_default_headers,
        create_segment_with_performer,
        url,
        is_phoenix,
        enable_billing_event_feature,
        enable_using_cargo_pipelines_feature,
        enable_dry_run_in_cargo_pipelines,
):
    await enable_billing_event_feature()
    await enable_using_cargo_pipelines_feature()
    await enable_dry_run_in_cargo_pipelines()
    segment = await create_segment_with_performer(
        is_phoenix=is_phoenix, status='delivered',
    )

    headers = get_default_headers()
    response = await taxi_cargo_claims.post(
        url,
        json={
            'cargo_order_ids': [
                segment.cargo_order_id,
                '00000000-0000-0000-0000-000000000000',
            ],
        },
        headers=headers,
    )
    assert response.status_code == 200
    assert len(response.json()['orders']) == 1
    expected_response = {
        'cargo_order_id': segment.cargo_order_id,
        'claim_id': segment.claim_id,
        'is_phoenix_flow': is_phoenix,
        'is_cargo_finance_billing_event': is_phoenix,
        'is_cargo_finance_using_cargo_pipelines': is_phoenix,
        'is_cargo_finance_dry_run_for_cargo_pipelines': is_phoenix,
        'is_phoenix_corp': is_phoenix,
        'is_agent_scheme': is_phoenix,
    }
    assert response.json()['orders'][0] == expected_response
