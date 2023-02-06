import typing

import pytest

from testsuite.utils import matching


DEFAULT_VERSIONS: typing.Dict[str, int] = {
    'additional_info_version': 0,
    'cargo_finance_claim_estimating_results_version': 0,
    'claim_audit_version': 0,
    'claim_changes_version': 0,
    'claim_custom_context_version': 0,
    'claim_estimating_results_version': 0,
    'claim_features_version': 0,
    'claim_point_time_intervals_version': 0,
    'claim_points_version': 0,
    'claim_segment_points_version': 0,
    'claim_segment_points_change_log_version': 0,
    'claim_segments_version': 0,
    'claim_warnings_version': 0,
    'claims_version': 0,
    'claims_c2c_version': 0,
    'courier_manual_dispatch_version': 0,
    'documents_version': 0,
    'items_version': 0,
    'items_exchange_version': 0,
    'items_fiscalization_version': 0,
    'matched_cars_version': 0,
    'matched_items_version': 0,
    'payment_on_delivery_version': 0,
    'points_version': 0,
    'points_ready_for_interact_notifications_version': 0,
    'taxi_order_changes_version': 0,
    'taxi_performer_info_version': 0,
}


async def test_claims_version_v2_create(
        taxi_cargo_claims,
        get_default_request,
        get_default_headers,
        get_default_idempotency_token,
        pgsql,
):
    response = await taxi_cargo_claims.post(
        '/api/integration/v1/claims/create',
        params={'request_id': get_default_idempotency_token},
        json=get_default_request(),
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    claim_uuid = response.json()['id']

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
            SELECT to_json(claims_version_v2)
            FROM cargo_claims.claims_version_v2
            WHERE claim_uuid ='{claim_uuid}'
        """,
    )
    versions = list(cursor)[0][0]
    expected_versions = {
        **DEFAULT_VERSIONS,
        'claim_uuid': claim_uuid,
        'additional_info_version': 1,
        'claim_audit_version': 1,
        'claim_custom_context_version': 1,
        'claim_points_version': 3,
        'claims_version': 1,
        'items_version': 2,
        'points_version': 3,
        'updated_ts': matching.datetime_string,
    }

    assert versions == expected_versions


@pytest.mark.pgsql('cargo_claims', files=['pg_raw_denorm.sql'])
@pytest.mark.parametrize(
    'table_name',
    (
        'additional_info',
        'cargo_finance_claim_estimating_results',
        'claim_audit',
        'claim_changes',
        'claim_custom_context',
        'claim_estimating_results',
        'claim_features',
        'claim_point_time_intervals',
        'claim_points',
        'claim_segment_points',
        'claim_segment_points_change_log',
        'claim_segments',
        'claim_warnings',
        'claims_c2c',
        'courier_manual_dispatch',
        'documents',
        'items',
        'items_exchange',
        'items_fiscalization',
        'matched_cars',
        'matched_items',
        'payment_on_delivery',
        'points',
        'points_ready_for_interact_notifications',
        'taxi_order_changes',
        'taxi_performer_info',
    ),
)
async def test_claims_version_v2_table_update(pgsql, table_name: str):
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
            INSERT INTO cargo_claims.claims_version_v2(claim_uuid)
            VALUES('{'9756ae927d7b42dc9bbdcbb832924343'}');
        """,
    )
    cursor.execute(
        f"""
            UPDATE cargo_claims.{table_name}
                SET claim_uuid = claim_uuid
            WHERE claim_uuid = '9756ae927d7b42dc9bbdcbb832924343';
        """,
    )
    cursor.execute(
        f"""
            SELECT to_json(claims_version_v2)
            FROM cargo_claims.claims_version_v2
            WHERE claim_uuid ='{'9756ae927d7b42dc9bbdcbb832924343'}'
        """,
    )
    versions = list(cursor)[0][0]
    expected_versions = {
        **DEFAULT_VERSIONS,
        'claim_uuid': '9756ae927d7b42dc9bbdcbb832924343',
        'updated_ts': matching.datetime_string,
        f'{table_name}_version': 1,
    }
    assert versions == expected_versions
