import pytest


@pytest.mark.pgsql('crm_admin', files=['update_group_state.sql'])
async def test_group_trigger(pgsql):
    cursor = pgsql['crm_admin'].cursor()

    query = """
    SELECT state_from, state_to
    FROM crm_admin.group_state_log
    ORDER BY updated_at
    """

    cursor.execute(query)

    expected = (('', 'NEW'), ('NEW', 'SENT'), ('SENT', ''))

    for value in expected:
        assert cursor.fetchone() == value
