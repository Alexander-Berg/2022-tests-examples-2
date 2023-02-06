import pytest


async def test_confirm_usage(confirm_usage, v1_calc_creator, pgsql):
    external_ref = 'taxi_order_id/' + 'x' * 32

    create_resp = await v1_calc_creator.execute()
    assert create_resp.status_code == 200
    calc_id = create_resp.json()['calc_id']

    await confirm_usage(calc_id=calc_id, external_ref=external_ref)

    cursor = pgsql['cargo_pricing'].conn.cursor()
    cursor.execute(
        """
        SELECT details_external_ref, is_confirmed
        FROM cargo_pricing.calculations
        """,
    )
    details_external_ref, is_confirmed = list(cursor)[0]
    assert is_confirmed
    assert external_ref == details_external_ref


@pytest.mark.yt(
    schemas=['yt/yt_calculations_raw_schema.yaml'],
    dyn_table_data=['yt/yt_calculations_raw.yaml'],
)
async def test_confirm_usage_calc_in_yt(confirm_usage, yt_apply):
    calc_id = 'cargo-pricing/v1/731d5f77-8c8b-4ac9-b556-9d38357b92b2'
    external_ref = 'taxi_order_id/' + 'x' * 32
    await confirm_usage(calc_id=calc_id, external_ref=external_ref)
