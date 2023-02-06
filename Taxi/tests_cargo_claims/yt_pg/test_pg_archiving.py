import pytest


@pytest.mark.pgsql(
    'cargo_claims', files=['pg_raw_denorm.sql', 'alter_sequence.sql'],
)
async def test_delete_trigger_test(pgsql, state_controller):
    await state_controller.apply(target_status='new')

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute('SELECT * FROM cargo_claims.points;')
    assert len(list(cursor)) == 4

    cursor.execute(
        f"""
            DELETE FROM ONLY cargo_claims.claims
            WHERE uuid_id = '9756ae927d7b42dc9bbdcbb832924343';
        """,
    )

    cursor.execute('SELECT * FROM cargo_claims.points;')
    assert len(list(cursor)) == 3
